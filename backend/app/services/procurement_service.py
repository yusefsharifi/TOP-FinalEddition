"""
Procurement Module — Core Service
TOP WorX ERP System

Handles the full purchase-to-pay lifecycle:
  1. Purchase Request → approval workflow
  2. PO creation from PR or direct
  3. Goods Receipt → inventory inbound + AP entry
  4. Vendor Invoice → 3-way match verification
  5. Payment → AP settlement

Costing method: Weighted Average (update item.standard_cost on every inbound).
DECISION POINT ⚙️: Switch to FIFO by replacing update_weighted_avg_cost()
with a fifo_layers table approach (see sales module FIFO notes).
"""
from __future__ import annotations

import random
import string
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.procurement import (
    ApprovalRule, GoodsReceipt, GoodsReceiptLine, MatchResult,
    POLineStatus, POStatus, PRLineStatus, PRPriority, PRStatus,
    PurchaseOrder, PurchaseOrderLine, PurchaseRequest, PurchaseRequestLine,
    Vendor, VendorInvoice, VendorInvoiceStatus, VendorPaymentStatus,
    PaymentToVendor,
)
from app.schemas.procurement import (
    POCreate, PRCreate, ReceiptCreate, VendorCreate, VendorInvoiceCreate,
    VendorPaymentCreate, ThreeWayMatchResult,
)


class ProcurementError(Exception):
    """Business rule violation in procurement."""


def _rand(n: int = 5) -> str:
    return "".join(random.choices(string.digits, k=n))


JALALI_YEAR = 1403  # TODO: compute dynamically


# ===========================================================================
# Vendor CRUD helpers
# ===========================================================================
async def get_vendor(db: AsyncSession, vendor_id: int) -> Optional[Vendor]:
    r = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    return r.scalar_one_or_none()


async def update_vendor_ap_balance(db: AsyncSession, vendor_id: int) -> None:
    """Recompute denormalised AP totals."""
    inv_r = await db.execute(
        select(
            func.coalesce(func.sum(VendorInvoice.total_amount), Decimal("0")).label("purchased"),
            func.coalesce(func.sum(VendorInvoice.amount_paid), Decimal("0")).label("paid"),
        ).where(
            VendorInvoice.vendor_id == vendor_id,
            VendorInvoice.status != VendorInvoiceStatus.PENDING_VERIFICATION,
        )
    )
    row = inv_r.one()
    vendor = await get_vendor(db, vendor_id)
    if vendor:
        vendor.total_purchased = Decimal(str(row.purchased))
        vendor.total_paid = Decimal(str(row.paid))
        vendor.balance_due = vendor.total_purchased - vendor.total_paid
        await db.flush()


# ===========================================================================
# Approval Workflow
# ===========================================================================
class ApprovalService:

    async def find_rule(
        self, db: AsyncSession, department: str, amount: Decimal
    ) -> Optional[ApprovalRule]:
        """Find lowest matching approval rule for department + amount."""
        r = await db.execute(
            select(ApprovalRule)
            .where(
                ApprovalRule.is_active.is_(True),
                ApprovalRule.min_amount <= amount,
                (ApprovalRule.max_amount.is_(None)) | (ApprovalRule.max_amount >= amount),
                (ApprovalRule.department.is_(None)) | (ApprovalRule.department == department),
            )
            .order_by(ApprovalRule.sort_order.asc())
            .limit(1)
        )
        return r.scalar_one_or_none()

    async def submit_pr(
        self, db: AsyncSession, pr: PurchaseRequest, user_id: int
    ) -> PurchaseRequest:
        if pr.status != PRStatus.DRAFT:
            raise ProcurementError(f"Only DRAFT requests can be submitted. Status: {pr.status}")
        rule = await self.find_rule(db, pr.department, pr.total_estimated)
        if not rule:
            # No rule = auto-approve for small amounts
            pr.status = PRStatus.APPROVED
            pr.approver_id = user_id
            pr.approved_at = datetime.utcnow()
            pr.approval_notes = "Auto-approved: no matching approval rule"
        else:
            pr.status = PRStatus.PENDING_APPROVAL
            pr.approver_id = rule.approver_user_id
            # TODO: send notification to rule.approver_role
        pr.updated_by_id = user_id
        await db.flush()
        return pr

    async def approve_pr(
        self, db: AsyncSession, pr: PurchaseRequest, approver_id: int, notes: Optional[str] = None
    ) -> PurchaseRequest:
        if pr.status != PRStatus.PENDING_APPROVAL:
            raise ProcurementError(f"PR is not pending approval. Status: {pr.status}")
        pr.status = PRStatus.APPROVED
        pr.approver_id = approver_id
        pr.approved_at = datetime.utcnow()
        pr.approval_notes = notes
        pr.updated_by_id = approver_id
        await db.flush()
        return pr

    async def reject_pr(
        self, db: AsyncSession, pr: PurchaseRequest, approver_id: int, reason: str
    ) -> PurchaseRequest:
        if pr.status != PRStatus.PENDING_APPROVAL:
            raise ProcurementError(f"PR is not pending approval. Status: {pr.status}")
        pr.status = PRStatus.REJECTED
        pr.approver_id = approver_id
        pr.rejection_reason = reason
        pr.updated_by_id = approver_id
        await db.flush()
        return pr


approval_service = ApprovalService()


# ===========================================================================
# Purchase Request Service
# ===========================================================================
class PRService:

    async def create(
        self, db: AsyncSession, data: PRCreate, requester_id: int
    ) -> PurchaseRequest:
        total_est = sum(
            ln.quantity * ln.estimated_unit_price for ln in data.lines
        )
        pr = PurchaseRequest(
            request_number=f"PR-{JALALI_YEAR}-{_rand(5)}",
            requester_id=requester_id,
            department=data.department,
            priority=data.priority,
            required_date=data.required_date,
            justification=data.justification,
            status=PRStatus.DRAFT,
            total_estimated=total_est,
            created_by_id=requester_id,
            updated_by_id=requester_id,
        )
        db.add(pr)
        await db.flush()

        for ln in data.lines:
            line = PurchaseRequestLine(
                request_id=pr.id,
                item_id=ln.item_id,
                description=ln.description,
                quantity=ln.quantity,
                estimated_unit_price=ln.estimated_unit_price,
                uom=ln.uom,
                specifications=ln.specifications,
                sort_order=ln.sort_order,
                created_by_id=requester_id,
                updated_by_id=requester_id,
            )
            db.add(line)
        await db.flush()
        await db.refresh(pr)
        return pr

    async def convert_to_po(
        self,
        db: AsyncSession,
        pr: PurchaseRequest,
        vendor_id: int,
        user_id: int,
        expected_delivery: Optional[date] = None,
    ) -> PurchaseOrder:
        if pr.status != PRStatus.APPROVED:
            raise ProcurementError(f"Only APPROVED requests can be converted. Status: {pr.status}")

        vendor = await get_vendor(db, vendor_id)
        if not vendor:
            raise ProcurementError(f"Vendor {vendor_id} not found")
        if not vendor.is_approved:
            raise ProcurementError(f"Vendor '{vendor.name}' is not approved for purchase orders")

        # Reload lines
        r = await db.execute(
            select(PurchaseRequestLine).where(
                PurchaseRequestLine.request_id == pr.id,
                PurchaseRequestLine.status == PRLineStatus.PENDING,
            )
        )
        pr_lines = r.scalars().all()
        if not pr_lines:
            raise ProcurementError("No pending lines to convert")

        po_line_data = [
            type("L", (), {
                "item_id": ln.item_id or 0,
                "description": ln.description,
                "quantity": ln.quantity,
                "unit_price": ln.estimated_unit_price,
                "discount_percent": Decimal("0"),
                "tax_percent": Decimal("9"),
                "request_line_id": ln.id,
                "sort_order": ln.sort_order,
            })()
            for ln in pr_lines
        ]

        po_data = POCreate(
            vendor_id=vendor_id,
            request_id=pr.id,
            order_date=date.today(),
            expected_delivery=expected_delivery,
            lines=[],  # we'll add manually below
        )

        po = await po_service.create_po(db, po_data, user_id, pr_lines=pr_line_data)

        # Update PR lines as converted
        for ln in pr_lines:
            ln.status = PRLineStatus.FULFILLED
        pr.status = PRStatus.CONVERTED
        pr.updated_by_id = user_id
        await db.flush()
        return po


pr_service = PRService()


# ===========================================================================
# Purchase Order Service
# ===========================================================================
class POService:

    async def create_po(
        self,
        db: AsyncSession,
        data: POCreate,
        user_id: int,
        pr_lines=None,  # pre-built line specs from PR conversion
    ) -> PurchaseOrder:
        vendor = await get_vendor(db, data.vendor_id)
        if not vendor:
            raise ProcurementError(f"Vendor {data.vendor_id} not found")
        if not vendor.is_approved:
            raise ProcurementError(f"Vendor '{vendor.name}' is not approved")

        po = PurchaseOrder(
            po_number=f"PO-{JALALI_YEAR}-{_rand(5)}",
            vendor_id=data.vendor_id,
            request_id=data.request_id,
            order_date=data.order_date,
            expected_delivery=data.expected_delivery,
            delivery_location_id=data.delivery_location_id,
            terms=data.terms,
            notes=data.notes,
            status=POStatus.DRAFT,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        db.add(po)
        await db.flush()

        lines_to_use = pr_lines if pr_lines else data.lines
        subtotal = Decimal("0")
        tax_total = Decimal("0")
        discount_total = Decimal("0")

        for ln in lines_to_use:
            base = Decimal(str(ln.quantity)) * Decimal(str(ln.unit_price))
            disc = base * Decimal(str(ln.discount_percent)) / Decimal("100")
            net = base - disc
            tax = net * Decimal(str(ln.tax_percent)) / Decimal("100")
            line_total = net + tax
            subtotal += base
            discount_total += disc
            tax_total += tax

            po_line = PurchaseOrderLine(
                po_id=po.id,
                request_line_id=getattr(ln, "request_line_id", None),
                item_id=ln.item_id,
                description=ln.description,
                quantity=Decimal(str(ln.quantity)),
                unit_price=Decimal(str(ln.unit_price)),
                discount_percent=Decimal(str(ln.discount_percent)),
                tax_percent=Decimal(str(ln.tax_percent)),
                line_total=line_total,
                sort_order=getattr(ln, "sort_order", 0),
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            db.add(po_line)

        po.subtotal = subtotal
        po.discount_amount = discount_total
        po.tax_amount = tax_total
        po.total_amount = subtotal - discount_total + tax_total
        await db.flush()
        await db.refresh(po)
        return po

    async def send_po(self, db: AsyncSession, po: PurchaseOrder, user_id: int) -> PurchaseOrder:
        if po.status != POStatus.DRAFT:
            raise ProcurementError(f"Only DRAFT POs can be sent. Status: {po.status}")
        po.status = POStatus.SENT
        po.updated_by_id = user_id
        # TODO: trigger email to vendor
        await db.flush()
        return po


po_service = POService()


# ===========================================================================
# Receipt Service
# ===========================================================================
class ReceiptService:

    async def receive_goods(
        self,
        db: AsyncSession,
        data: ReceiptCreate,
        user_id: int,
    ) -> GoodsReceipt:
        """
        1. Validate PO is in a receivable state
        2. Create GoodsReceipt + lines
        3. Update PO line quantities received
        4. Create inventory INBOUND movements
        5. Update weighted average cost
        6. Create AP journal entry: Dr Inventory / Cr AP
        7. Update PO status
        8. Update vendor AP balance
        """
        po_r = await db.execute(
            select(PurchaseOrder).options(selectinload(PurchaseOrder.lines))
            .where(PurchaseOrder.id == data.po_id)
        )
        po = po_r.scalar_one_or_none()
        if not po:
            raise ProcurementError(f"Purchase order {data.po_id} not found")
        if po.status in (POStatus.RECEIVED, POStatus.PAID, POStatus.CANCELLED):
            raise ProcurementError(f"PO {po.po_number} cannot receive more goods (status: {po.status})")

        # Create receipt header
        receipt = GoodsReceipt(
            receipt_number=f"GRN-{JALALI_YEAR}-{_rand(5)}",
            po_id=po.id,
            receipt_date=data.receipt_date,
            received_by_id=user_id,
            delivery_note_number=data.delivery_note_number,
            notes=data.notes,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        db.add(receipt)
        await db.flush()

        total_receipt_value = Decimal("0")
        po_lines_map = {ln.id: ln for ln in po.lines}

        for rln in data.lines:
            po_line = po_lines_map.get(rln.po_line_id)
            if not po_line:
                raise ProcurementError(f"PO line {rln.po_line_id} not found on this PO")

            remaining = po_line.quantity - po_line.quantity_received
            if rln.quantity_received > remaining:
                raise ProcurementError(
                    f"Cannot receive {rln.quantity_received} for line {rln.po_line_id}. "
                    f"Remaining: {remaining}"
                )

            line_value = rln.quantity_received * rln.unit_price
            total_receipt_value += line_value

            # Create receipt line
            grn_line = GoodsReceiptLine(
                receipt_id=receipt.id,
                po_line_id=rln.po_line_id,
                item_id=rln.item_id,
                quantity_received=rln.quantity_received,
                unit_price=rln.unit_price,
                condition=rln.condition,
                rejection_reason=rln.rejection_reason,
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            db.add(grn_line)

            # Update PO line
            po_line.quantity_received += rln.quantity_received
            if po_line.quantity_received >= po_line.quantity:
                po_line.status = POLineStatus.RECEIVED
            else:
                po_line.status = POLineStatus.PARTIAL

            # Create inventory INBOUND movement + update weighted avg cost
            movement_id = await self._create_inbound_movement(
                db, po, grn_line, rln.unit_price, user_id
            )
            grn_line.stock_movement_id = movement_id

            # Update item weighted average cost
            await self._update_weighted_avg_cost(
                db, rln.item_id, rln.quantity_received, rln.unit_price
            )

        await db.flush()

        # Create AP journal entry
        je_id = await self._create_receipt_je(db, po, receipt, total_receipt_value, user_id)
        receipt.journal_entry_id = je_id

        # Update PO status
        all_received = all(
            ln.quantity_received >= ln.quantity for ln in po.lines
        )
        po.status = POStatus.RECEIVED if all_received else POStatus.PARTIAL_RECEIVED
        po.actual_delivery = data.receipt_date
        po.updated_by_id = user_id

        await db.flush()
        await update_vendor_ap_balance(db, po.vendor_id)
        await db.refresh(receipt)
        return receipt

    async def _create_inbound_movement(
        self,
        db: AsyncSession,
        po: PurchaseOrder,
        grn_line: GoodsReceiptLine,
        unit_price: Decimal,
        user_id: int,
    ) -> Optional[int]:
        """Create InventoryMovement (INBOUND) and update StockLevel."""
        try:
            from app.models.inventory import InventoryMovement, MovementType, StockLevel

            # Find or create stock level at delivery location
            location_id = po.delivery_location_id
            if location_id:
                stock_r = await db.execute(
                    select(StockLevel).where(
                        StockLevel.item_id == grn_line.item_id,
                        StockLevel.location_id == location_id,
                    )
                )
                stock = stock_r.scalar_one_or_none()
                if not stock:
                    stock = StockLevel(
                        item_id=grn_line.item_id,
                        location_id=location_id,
                        quantity_on_hand=Decimal("0"),
                        quantity_reserved=Decimal("0"),
                        quantity_available=Decimal("0"),
                        created_by_id=user_id,
                        updated_by_id=user_id,
                    )
                    db.add(stock)
                    await db.flush()

                qty_before = stock.quantity_on_hand
                stock.quantity_on_hand += grn_line.quantity_received
                stock.quantity_available = (
                    stock.quantity_on_hand - (stock.quantity_reserved or Decimal("0"))
                )
                await db.flush()
            else:
                qty_before = Decimal("0")
                location_id = None

            movement = InventoryMovement(
                item_id=grn_line.item_id,
                location_id=location_id,
                movement_type=MovementType.INBOUND,
                quantity=grn_line.quantity_received,
                quantity_before=qty_before,
                quantity_after=qty_before + grn_line.quantity_received,
                reference_number=po.po_number,
                reason=f"PO Receipt — {po.po_number}",
                unit_cost=unit_price,
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            db.add(movement)
            await db.flush()
            return movement.id
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Failed to create inbound movement")
            return None

    async def _update_weighted_avg_cost(
        self,
        db: AsyncSession,
        item_id: int,
        new_quantity: Decimal,
        new_unit_cost: Decimal,
    ) -> None:
        """
        Weighted average cost formula:
        new_avg = (old_qty * old_avg + new_qty * new_cost) / (old_qty + new_qty)
        Updates item.standard_cost in-place.
        """
        try:
            from app.models.inventory import InventoryItem, StockLevel

            item_r = await db.execute(select(InventoryItem).where(InventoryItem.id == item_id))
            item = item_r.scalar_one_or_none()
            if not item:
                return

            # Current on-hand qty across all locations
            qty_r = await db.execute(
                select(func.coalesce(func.sum(StockLevel.quantity_on_hand), Decimal("0")))
                .where(StockLevel.item_id == item_id)
            )
            current_qty = Decimal(str(qty_r.scalar_one() or "0"))
            # current_qty already includes the newly added qty (updated before this call)
            old_qty = current_qty - new_quantity
            old_cost = item.standard_cost or Decimal("0")

            if old_qty + new_quantity > Decimal("0"):
                new_avg = (old_qty * old_cost + new_quantity * new_unit_cost) / (old_qty + new_quantity)
                item.standard_cost = new_avg.quantize(Decimal("0.0001"))
                await db.flush()
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Failed to update weighted avg cost for item %s", item_id)

    async def _create_receipt_je(
        self,
        db: AsyncSession,
        po: PurchaseOrder,
        receipt: GoodsReceipt,
        total_value: Decimal,
        user_id: int,
    ) -> Optional[int]:
        """
        Dr 1130 — Inventory         [total_value]
          Cr 2110 — Accounts Payable  [total_value]

        بابت دریافت کالا از تأمین‌کننده
        """
        try:
            from app.services.accounting_service import accounting_service
            from app.models.finance import ReferenceType

            je = await accounting_service.build_and_create_entry(
                db,
                entry_date=receipt.receipt_date,
                description=f"Goods receipt — {receipt.receipt_number} (PO: {po.po_number})",
                description_fa=f"رسید کالا — {receipt.receipt_number}",
                reference_type=ReferenceType.INVENTORY,
                reference_id=receipt.id,
                lines=[
                    {
                        "account_code": "1130",
                        "debit": total_value,
                        "description": f"Inventory in: {po.po_number}",
                        "contact_id": po.vendor_id,
                        "contact_type": "vendor",
                    },
                    {
                        "account_code": "2110",
                        "credit": total_value,
                        "description": f"AP: {po.vendor_id} — {po.po_number}",
                        "contact_id": po.vendor_id,
                        "contact_type": "vendor",
                    },
                ],
                user_id=user_id,
            )
            return je.id
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Failed to create receipt JE")
            return None


receipt_service = ReceiptService()


# ===========================================================================
# 3-Way Match Service
# ===========================================================================
class ThreeWayMatchService:
    # Tolerances
    QTY_TOLERANCE = Decimal("0")        # Must match exactly
    PRICE_TOLERANCE_PCT = Decimal("1")  # 1% allowed
    AMOUNT_TOLERANCE = Decimal("1000")  # 1000 Toman

    async def perform_match(
        self,
        db: AsyncSession,
        invoice: VendorInvoice,
        user_id: int,
    ) -> ThreeWayMatchResult:
        """
        3-way match: PO ↔ most recent GoodsReceipt for that PO ↔ VendorInvoice
        """
        if not invoice.po_id:
            # No PO → 2-way match only (invoice vs nothing → flag for manual)
            return ThreeWayMatchResult(
                po_id=0,
                receipt_id=0,
                invoice_id=invoice.id,
                result=MatchResult.MATCH,
                po_total=Decimal("0"),
                receipt_total=Decimal("0"),
                invoice_total=invoice.total_amount,
                qty_variance=Decimal("0"),
                price_variance_pct=Decimal("0"),
                notes="No PO linked — manual approval required",
                auto_approved=False,
            )

        # Load PO
        po_r = await db.execute(
            select(PurchaseOrder).options(selectinload(PurchaseOrder.lines))
            .where(PurchaseOrder.id == invoice.po_id)
        )
        po = po_r.scalar_one_or_none()
        if not po:
            raise ProcurementError(f"PO {invoice.po_id} not found")

        # Load most recent receipt for this PO
        receipt_r = await db.execute(
            select(GoodsReceipt)
            .options(selectinload(GoodsReceipt.lines))
            .where(GoodsReceipt.po_id == po.id)
            .order_by(GoodsReceipt.receipt_date.desc())
            .limit(1)
        )
        receipt = receipt_r.scalar_one_or_none()

        po_total = po.total_amount
        receipt_total = (
            sum(ln.quantity_received * ln.unit_price for ln in receipt.lines)
            if receipt else Decimal("0")
        )
        invoice_total = invoice.total_amount

        # Quantity variance: receipt qty vs invoice qty (if receipt exists)
        qty_variance = Decimal("0")
        if receipt:
            receipt_qty = sum(ln.quantity_received for ln in receipt.lines)
            po_qty = sum(ln.quantity for ln in po.lines)
            qty_variance = abs(receipt_qty - po_qty)

        # Price variance
        price_variance = abs(po_total - invoice_total)
        price_variance_pct = (
            (price_variance / po_total * Decimal("100")).quantize(Decimal("0.01"))
            if po_total > Decimal("0") else Decimal("0")
        )

        qty_ok = qty_variance <= self.QTY_TOLERANCE
        price_ok = (
            price_variance_pct <= self.PRICE_TOLERANCE_PCT
            or price_variance <= self.AMOUNT_TOLERANCE
        )

        if qty_ok and price_ok:
            result = MatchResult.MATCH
            notes = "3-way match successful — auto-approved"
            auto_approved = True
        elif not qty_ok and not price_ok:
            result = MatchResult.BOTH_MISMATCH
            notes = f"Qty variance: {qty_variance}, Price variance: {price_variance_pct}%"
            auto_approved = False
        elif not qty_ok:
            result = MatchResult.QUANTITY_MISMATCH
            notes = f"Quantity variance: {qty_variance} units"
            auto_approved = False
        else:
            result = MatchResult.PRICE_MISMATCH
            notes = f"Price variance: {price_variance_pct}% ({price_variance} IRR)"
            auto_approved = False

        # Update invoice match result
        invoice.match_result = result
        invoice.match_notes = notes
        if auto_approved:
            invoice.status = VendorInvoiceStatus.APPROVED
            invoice.verified_by_id = user_id
            invoice.verified_at = datetime.utcnow()
            # Create AP JE if not already created by receipt
            if not invoice.journal_entry_id:
                await self._create_invoice_je(db, invoice, user_id)

        await db.flush()
        await update_vendor_ap_balance(db, invoice.vendor_id)

        return ThreeWayMatchResult(
            po_id=po.id,
            receipt_id=receipt.id if receipt else 0,
            invoice_id=invoice.id,
            result=result,
            po_total=po_total,
            receipt_total=receipt_total,
            invoice_total=invoice_total,
            qty_variance=qty_variance,
            price_variance_pct=price_variance_pct,
            notes=notes,
            auto_approved=auto_approved,
        )

    async def _create_invoice_je(
        self, db: AsyncSession, invoice: VendorInvoice, user_id: int
    ) -> None:
        """
        Create AP journal entry on invoice approval (if not already done at receipt).
        For direct invoices without prior receipt:
          Dr 1130 — Inventory  [amount]
          Dr 1140 — Prepaid VAT [tax]  (recoverable VAT)
            Cr 2110 — AP         [total]
        """
        try:
            from app.services.accounting_service import accounting_service
            from app.models.finance import ReferenceType

            lines = [
                {
                    "account_code": "1130",
                    "debit": invoice.amount,
                    "description": f"Vendor invoice: {invoice.invoice_number}",
                    "contact_id": invoice.vendor_id,
                    "contact_type": "vendor",
                },
            ]
            if invoice.tax_amount > Decimal("0"):
                lines.append({
                    "account_code": "1140",   # Prepaid/recoverable VAT
                    "debit": invoice.tax_amount,
                    "description": f"VAT recoverable: {invoice.invoice_number}",
                })
            lines.append({
                "account_code": "2110",
                "credit": invoice.total_amount,
                "description": f"AP: {invoice.invoice_number}",
                "contact_id": invoice.vendor_id,
                "contact_type": "vendor",
            })

            je = await accounting_service.build_and_create_entry(
                db,
                entry_date=invoice.invoice_date,
                description=f"Vendor invoice approved — {invoice.invoice_number}",
                description_fa=f"تأیید فاکتور تأمین‌کننده — {invoice.invoice_number}",
                reference_type=ReferenceType.INVOICE,
                reference_id=invoice.id,
                lines=lines,
                user_id=user_id,
            )
            invoice.journal_entry_id = je.id
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Failed to create invoice JE")


three_way_match = ThreeWayMatchService()


# ===========================================================================
# Vendor Payment Service
# ===========================================================================
class VendorPaymentService:

    async def process_payment(
        self,
        db: AsyncSession,
        data: VendorPaymentCreate,
        user_id: int,
    ) -> PaymentToVendor:
        """
        1. Create payment record
        2. JE: Dr 2110 AP / Cr Bank
        3. Allocate to oldest unpaid invoices
        4. Update vendor AP balance
        """
        vendor = await get_vendor(db, data.vendor_id)
        if not vendor:
            raise ProcurementError(f"Vendor {data.vendor_id} not found")

        payment = PaymentToVendor(
            payment_number=f"PAY-{JALALI_YEAR}-{_rand(5)}",
            **data.model_dump(),
            status=VendorPaymentStatus.PENDING,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        db.add(payment)
        await db.flush()

        # Create JE
        await self._create_payment_je(db, payment, user_id)

        # Allocate
        await self._allocate_payment(db, payment)

        payment.status = VendorPaymentStatus.CLEARED
        await db.flush()
        await update_vendor_ap_balance(db, data.vendor_id)
        return payment

    async def _create_payment_je(
        self, db: AsyncSession, payment: PaymentToVendor, user_id: int
    ) -> None:
        """
        Dr 2110 — Accounts Payable (Vendor)   [amount]
          Cr 1110 — Cash / Bank                [amount]
        پرداخت به تأمین‌کننده
        """
        try:
            from app.services.accounting_service import accounting_service
            from app.models.finance import ReferenceType
            from app.crud.finance import account_crud

            credit_acct = "1110"
            if payment.bank_account_id:
                bank = await account_crud.get(db, payment.bank_account_id)
                if bank:
                    credit_acct = bank.code

            je = await accounting_service.build_and_create_entry(
                db,
                entry_date=payment.payment_date,
                description=f"Vendor payment — {payment.payment_number}",
                description_fa=f"پرداخت به تأمین‌کننده — {payment.payment_number}",
                reference_type=ReferenceType.PAYMENT,
                reference_id=payment.id,
                lines=[
                    {
                        "account_code": "2110",
                        "debit": payment.amount,
                        "description": f"AP settlement: {payment.payment_number}",
                        "contact_id": payment.vendor_id,
                        "contact_type": "vendor",
                    },
                    {
                        "account_code": credit_acct,
                        "credit": payment.amount,
                        "description": f"Payment: {payment.reference_number or payment.payment_number}",
                    },
                ],
                user_id=user_id,
            )
            payment.journal_entry_id = je.id
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Failed to create vendor payment JE")

    async def _allocate_payment(self, db: AsyncSession, payment: PaymentToVendor) -> None:
        """Apply payment to oldest unpaid vendor invoices (oldest due date first)."""
        if payment.vendor_invoice_id:
            invoices = []
            inv = await db.get(VendorInvoice, payment.vendor_invoice_id)
            if inv:
                invoices = [inv]
        else:
            r = await db.execute(
                select(VendorInvoice)
                .where(
                    VendorInvoice.vendor_id == payment.vendor_id,
                    VendorInvoice.status == VendorInvoiceStatus.APPROVED,
                    VendorInvoice.amount_due > Decimal("0"),
                )
                .order_by(VendorInvoice.due_date.asc())
            )
            invoices = r.scalars().all()

        remaining = payment.amount
        for inv in invoices:
            if remaining <= Decimal("0"):
                break
            apply = min(remaining, inv.amount_due)
            inv.amount_paid += apply
            inv.amount_due -= apply
            if inv.amount_due <= Decimal("0.001"):
                inv.status = VendorInvoiceStatus.PAID
                inv.amount_due = Decimal("0")
            remaining -= apply

        await db.flush()


vendor_payment_service = VendorPaymentService()
