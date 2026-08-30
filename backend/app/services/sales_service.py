# app/services/sales_service.py
"""
Sales Module — Sales Service (Merged)
TOP WorX ERP System

Core business logic:
  • Customer AR management
  • FIFO cost calculation for COGS
  • Invoice issue lifecycle (stock out + accounting + tax compliance)
  • Quote-to-invoice conversion
  • Credit limit enforcement
  • Overdue status update (scheduled job)
  • Payment recording & allocation
  • Reports: revenue, top customers, product margins, tax export
"""
from __future__ import annotations

import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.sales import customer_crud, invoice_crud, payment_crud, quote_crud
from app.models.sales import (
    Customer,
    InvoiceStatus,
    QuoteStatus,
    PaymentStatus,
    SalesInvoice,
    SalesInvoiceLine,
    SalesPayment,
    SalesQuote,
)
from app.schemas.sales import (
    CustomerCreate,
    CustomerUpdate,
    CustomerStatement,
    CustomerStatementLine,
    InvoiceCreate,
    InvoiceLineCreate,
    PaymentCreate,
    PaymentAllocate,
    ProductMarginRow,
    QuoteCreate,
    RevenueByPeriodRow,
    TaxExportLine,
    TopCustomerRow,
    InvoiceListItem,
)

logger = logging.getLogger(__name__)


class SalesError(Exception):
    """Business rule violation in Sales module."""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _next_sequence(prefix: str, last_number: Optional[str]) -> str:
    """Generate next sequential document number.  e.g. INV-000042"""
    if last_number is None:
        return f"{prefix}-000001"
    try:
        seq = int(last_number.split("-")[-1]) + 1
    except (ValueError, IndexError):
        seq = 1
    return f"{prefix}-{seq:06d}"


def _compute_invoice_totals(lines: list[SalesInvoiceLine]) -> dict:
    """Mutates lines in-place (sets tax_amount, line_total). Returns totals dict."""
    subtotal = Decimal("0")
    discount_amount = Decimal("0")
    tax_amount = Decimal("0")

    for ln in lines:
        base = ln.quantity * ln.unit_price
        subtotal += base
        discount_amount += ln.discount_amount
        net = base - ln.discount_amount
        ln.tax_amount = (net * ln.tax_percent / Decimal("100")).quantize(Decimal("0.01"))
        tax_amount += ln.tax_amount
        ln.line_total = (net + ln.tax_amount).quantize(Decimal("0.01"))

    return {
        "subtotal": subtotal.quantize(Decimal("0.01")),
        "discount_amount": discount_amount.quantize(Decimal("0.01")),
        "tax_amount": tax_amount.quantize(Decimal("0.01")),
        "total_amount": (subtotal - discount_amount + tax_amount).quantize(Decimal("0.01")),
    }


def _compute_quote_totals(lines: list) -> dict:
    """Mutates quote lines in-place. Returns totals dict."""
    subtotal = Decimal("0")
    discount_amount = Decimal("0")
    tax_amount = Decimal("0")

    for ln in lines:
        base = ln.quantity * ln.unit_price
        disc = (base * ln.discount_percent / Decimal("100")).quantize(Decimal("0.01"))
        net = base - disc
        tax = (net * ln.tax_percent / Decimal("100")).quantize(Decimal("0.01"))
        ln.line_total = (net + tax).quantize(Decimal("0.01"))
        subtotal += base
        discount_amount += disc
        tax_amount += tax

    return {
        "subtotal": subtotal.quantize(Decimal("0.01")),
        "discount_amount": discount_amount.quantize(Decimal("0.01")),
        "tax_amount": tax_amount.quantize(Decimal("0.01")),
        "total": (subtotal - discount_amount + tax_amount).quantize(Decimal("0.01")),
    }


# ===========================================================================
# Customer Service
# ===========================================================================

class CustomerService:

    @staticmethod
    async def get_or_404(db: AsyncSession, customer_id: int) -> Customer:
        customer = await customer_crud.get(db, customer_id)
        if not customer or not customer.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer {customer_id} not found.",
            )
        return customer

    @staticmethod
    async def create(
        db: AsyncSession,
        data: CustomerCreate,
        created_by_id: int,
    ) -> Customer:
        existing = await db.execute(
            select(Customer).where(Customer.code == data.code)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Customer code '{data.code}' already exists.",
            )
        return await customer_crud.create(db, data, user_id=created_by_id)

    @staticmethod
    async def update(
        db: AsyncSession,
        customer_id: int,
        data: CustomerUpdate,
        updated_by_id: int,
    ) -> Customer:
        customer = await CustomerService.get_or_404(db, customer_id)
        return await customer_crud.update(db, customer, data, user_id=updated_by_id)

    @staticmethod
    async def deactivate(db: AsyncSession, customer_id: int) -> None:
        customer = await CustomerService.get_or_404(db, customer_id)
        if customer.balance_due > Decimal("0"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate customer with outstanding balance.",
            )
        customer.is_active = False
        await db.flush()

    @staticmethod
    async def get_statement(
        db: AsyncSession,
        customer_id: int,
        as_of_date: date,
    ) -> CustomerStatement:
        customer = await CustomerService.get_or_404(db, customer_id)

        invoices_r = await db.execute(
            select(SalesInvoice)
            .where(
                and_(
                    SalesInvoice.customer_id == customer_id,
                    SalesInvoice.issue_date <= as_of_date,
                    SalesInvoice.status != InvoiceStatus.CANCELLED,
                )
            )
            .order_by(SalesInvoice.issue_date)
        )
        payments_r = await db.execute(
            select(SalesPayment)
            .where(
                and_(
                    SalesPayment.customer_id == customer_id,
                    SalesPayment.payment_date <= as_of_date,
                    SalesPayment.status == PaymentStatus.CLEARED,
                )
            )
            .order_by(SalesPayment.payment_date)
        )

        events: list[tuple] = []
        for inv in invoices_r.scalars():
            events.append((inv.issue_date, "invoice", inv))
        for pay in payments_r.scalars():
            events.append((pay.payment_date, "payment", pay))
        events.sort(key=lambda x: x[0])

        lines: list[CustomerStatementLine] = []
        running = Decimal("0")
        total_invoiced = Decimal("0")
        total_paid = Decimal("0")

        for evt_date, evt_type, obj in events:
            if evt_type == "invoice":
                debit, credit = obj.total_amount, Decimal("0")
                running += debit
                total_invoiced += debit
                ref = obj.invoice_number
            else:
                debit, credit = Decimal("0"), obj.amount
                running -= credit
                total_paid += credit
                ref = obj.payment_number

            lines.append(CustomerStatementLine(
                date=evt_date,
                type=evt_type,
                reference=ref,
                debit=debit,
                credit=credit,
                running_balance=running,
            ))

        return CustomerStatement(
            customer_id=customer_id,
            customer_name=customer.name,
            as_of_date=as_of_date,
            lines=lines,
            total_invoiced=total_invoiced,
            total_paid=total_paid,
            balance_due=running,
        )


# ===========================================================================
# Quote Service
# ===========================================================================

class QuoteService:

    @staticmethod
    async def create(
        db: AsyncSession,
        data: QuoteCreate,
        created_by_id: int,
    ) -> SalesQuote:
        customer = await CustomerService.get_or_404(db, data.customer_id)
        if not customer.is_active:
            raise SalesError("Cannot create quote for inactive customer.")
        return await quote_crud.create(db, data, user_id=created_by_id)

    @staticmethod
    async def send(
        db: AsyncSession,
        quote_id: int,
        user_id: int,
    ) -> SalesQuote:
        quote = await db.get(SalesQuote, quote_id)
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found.")
        if quote.status != QuoteStatus.DRAFT:
            raise SalesError(
                f"Only DRAFT quotes can be sent. Status: {quote.status}"
            )
        quote.status = QuoteStatus.SENT
        quote.updated_by_id = user_id
        await db.flush()
        # TODO: trigger email notification via notification service
        return quote

    @staticmethod
    async def convert_to_invoice(
        db: AsyncSession,
        quote_id: int,
        created_by_id: int,
    ) -> SalesInvoice:
        quote = await db.get(SalesQuote, quote_id)
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found.")
        if quote.status in (
            QuoteStatus.REJECTED,
            QuoteStatus.EXPIRED,
            QuoteStatus.CONVERTED,
        ):
            raise SalesError(
                f"Quote {quote.quote_number} cannot be converted — status: {quote.status}"
            )

        inv_lines = [
            InvoiceLineCreate(
                item_id=ln.item_id,
                description=ln.description,
                quantity=ln.quantity,
                unit_price=ln.unit_price,
                discount_amount=(
                    ln.quantity * ln.unit_price * ln.discount_percent / Decimal("100")
                ).quantize(Decimal("0.01")),
                tax_percent=ln.tax_percent,
                sort_order=ln.sort_order,
            )
            for ln in quote.lines
        ]
        inv_data = InvoiceCreate(
            customer_id=quote.customer_id,
            quote_id=quote.id,
            draft_date=date.today(),
            lines=inv_lines,
        )

        customer = await customer_crud.get(db, quote.customer_id)
        invoice = await invoice_crud.create_from_data(db, inv_data, customer, user_id=created_by_id)

        quote.status = QuoteStatus.CONVERTED
        quote.converted_to_invoice_id = invoice.id
        quote.updated_by_id = created_by_id
        await db.flush()
        return invoice


# ===========================================================================
# Invoice Service
# ===========================================================================

class InvoiceService:

    # -------------------------------------------------------------------
    # FIFO Cost Calculation
    # -------------------------------------------------------------------

    @staticmethod
    async def calculate_cogs_fifo(
        db: AsyncSession,
        item_id: int,
        quantity: Decimal,
    ) -> tuple[Decimal, Decimal]:
        """
        Returns (total_cost, unit_cost_avg) using FIFO from inbound movements.

        ⚙️  NOTE: This is a simplified weighted-FIFO over all inbound movements.
        For strict FIFO you need a `fifo_layers` table tracking remaining qty
        per inbound movement batch.
        """
        from app.models.inventory import InventoryMovement, MovementType  # avoid circular

        result = await db.execute(
            select(InventoryMovement)
            .where(
                InventoryMovement.item_id == item_id,
                InventoryMovement.movement_type == MovementType.INBOUND,
            )
            .order_by(InventoryMovement.movement_date.asc())
        )
        movements = result.scalars().all()

        remaining = quantity
        total_cost = Decimal("0")

        for mv in movements:
            if remaining <= Decimal("0"):
                break
            unit_cost = getattr(mv, "unit_cost", None) or Decimal("0")
            take = min(mv.quantity, remaining)
            total_cost += take * unit_cost
            remaining -= take

        # Fill any remaining qty with item's standard_cost
        if quantity > Decimal("0") and remaining > Decimal("0"):
            from app.models.inventory import InventoryItem
            item_r = await db.execute(
                select(InventoryItem).where(InventoryItem.id == item_id)
            )
            item = item_r.scalar_one_or_none()
            if item:
                total_cost += remaining * (item.standard_cost or Decimal("0"))

        unit_avg = (
            (total_cost / quantity).quantize(Decimal("0.0001"))
            if quantity else Decimal("0")
        )
        return total_cost.quantize(Decimal("0.0001")), unit_avg

    # -------------------------------------------------------------------
    # Create (DRAFT)
    # -------------------------------------------------------------------

    @staticmethod
    async def create(
        db: AsyncSession,
        data: InvoiceCreate,
        created_by_id: int,
    ) -> SalesInvoice:
        customer = await CustomerService.get_or_404(db, data.customer_id)
        if not customer.is_active:
            raise SalesError("Customer is inactive.")

        if customer.credit_limit > Decimal("0"):
            if customer.balance_due + _estimate_invoice_total(data) > customer.credit_limit:
                raise SalesError(
                    f"Credit limit exceeded. "
                    f"Limit: {customer.credit_limit}, "
                    f"Balance: {customer.balance_due}. "
                    f"سقف اعتبار مشتری تجاوز شده است."
                )

        return await invoice_crud.create_from_data(db, data, customer, user_id=created_by_id)

    # -------------------------------------------------------------------
    # Issue (DRAFT → ISSUED)  — full lifecycle
    # -------------------------------------------------------------------

    @staticmethod
    async def issue(
        db: AsyncSession,
        invoice_id: int,
        user_id: int,
    ) -> SalesInvoice:
        """
        Full issue flow:
        1. Validate state
        2. Validate credit limit
        3. Check stock availability per line
        4. Calculate FIFO costs
        5. Create OUTBOUND stock movements
        6. Create Revenue + VAT journal entry
        7. Create COGS journal entry
        8. Generate tax invoice number + QR
        9. Update invoice status & customer AR
        """
        invoice = await db.get(SalesInvoice, invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found.")
        if invoice.status != InvoiceStatus.DRAFT:
            raise SalesError(
                f"Only DRAFT invoices can be issued. Status: {invoice.status}"
            )

        customer = await customer_crud.get(db, invoice.customer_id)
        if not customer:
            raise SalesError("Customer not found.")

        # Credit limit check
        if customer.credit_limit > Decimal("0"):
            if customer.balance_due + invoice.total_amount > customer.credit_limit:
                raise SalesError(
                    f"Credit limit exceeded. "
                    f"Limit: {customer.credit_limit}, "
                    f"Current balance: {customer.balance_due}, "
                    f"Invoice: {invoice.total_amount}. "
                    f"سقف اعتبار مشتری تجاوز شده است."
                )

        # Reload lines
        lines_r = await db.execute(
            select(SalesInvoiceLine).where(SalesInvoiceLine.invoice_id == invoice.id)
        )
        lines = lines_r.scalars().all()

        # Step 1: Stock validation + FIFO costs
        for line in lines:
            from app.models.inventory import InventoryItem, StockLevel  # avoid circular

            item_r = await db.execute(
                select(InventoryItem).where(InventoryItem.id == line.item_id)
            )
            item = item_r.scalar_one_or_none()
            if not item:
                raise SalesError(f"Item {line.item_id} not found.")

            available_r = await db.execute(
                select(func.coalesce(func.sum(StockLevel.quantity_available), Decimal("0")))
                .where(StockLevel.item_id == line.item_id)
            )
            available = Decimal(str(available_r.scalar_one() or "0"))

            if available < line.quantity and not getattr(item, "allow_negative_stock", False):
                raise SalesError(
                    f"Insufficient stock for '{item.name}' (SKU: {item.sku}). "
                    f"Available: {available}, Requested: {line.quantity}. "
                    f"موجودی کافی نیست."
                )

            total_cost, unit_cost = await InvoiceService.calculate_cogs_fifo(
                db, line.item_id, line.quantity
            )
            line.unit_cost = unit_cost
            line.total_cost = total_cost

        await db.flush()

        # Step 2: Outbound stock movements
        first_movement_id: Optional[int] = None
        for line in lines:
            movement_id = await InvoiceService._create_outbound_movement(
                db, invoice, line, user_id
            )
            line.stock_movement_id = movement_id
            if first_movement_id is None:
                first_movement_id = movement_id

        # Step 3: Accounting entries
        from app.services.sales_accounting_bridge import sales_accounting_bridge
        revenue_je_id, cogs_je_id = await sales_accounting_bridge.create_invoice_entries(
            db, invoice, lines, customer, user_id
        )

        # Step 4: Tax compliance
        from app.services.tax_compliance_service import tax_compliance_service
        tax_number = tax_compliance_service.generate_tax_invoice_number(invoice.invoice_number)
        qr_data = tax_compliance_service.generate_invoice_qr_data(invoice, customer)

        # Step 5: Finalise invoice
        invoice.status = InvoiceStatus.ISSUED
        invoice.issue_date = date.today()
        invoice.revenue_journal_entry_id = revenue_je_id
        invoice.cogs_journal_entry_id = cogs_je_id
        invoice.stock_movement_id = first_movement_id
        invoice.tax_invoice_number = tax_number
        invoice.qr_data = qr_data
        invoice.updated_by_id = user_id
        await db.flush()

        # Step 6: Update customer AR
        await customer_crud.update_ar_balance(db, invoice.customer_id)
        return invoice

    # -------------------------------------------------------------------
    # Cancel
    # -------------------------------------------------------------------

    @staticmethod
    async def cancel(
        db: AsyncSession,
        invoice_id: int,
        user_id: int,
    ) -> SalesInvoice:
        """
        Cancel: reverse JEs, return stock, mark CANCELLED.
        Cannot cancel PAID invoices — use credit note instead.
        """
        invoice = await db.get(SalesInvoice, invoice_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found.")
        if invoice.status == InvoiceStatus.PAID:
            raise SalesError("Cannot cancel a fully paid invoice. Issue a credit note instead.")
        if invoice.status == InvoiceStatus.CANCELLED:
            raise SalesError("Invoice is already cancelled.")

        if invoice.status in (InvoiceStatus.ISSUED, InvoiceStatus.PARTIAL_PAID):
            from app.services.sales_accounting_bridge import sales_accounting_bridge
            await sales_accounting_bridge.reverse_invoice_entries(db, invoice, user_id)
            await InvoiceService._return_stock(db, invoice, user_id)

        invoice.status = InvoiceStatus.CANCELLED
        invoice.updated_by_id = user_id
        await db.flush()
        await customer_crud.update_ar_balance(db, invoice.customer_id)
        return invoice

    # -------------------------------------------------------------------
    # List for customer
    # -------------------------------------------------------------------

    @staticmethod
    async def list_for_customer(
        db: AsyncSession,
        customer_id: int,
        status_filter: Optional[InvoiceStatus] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[SalesInvoice]:
        q = select(SalesInvoice).where(SalesInvoice.customer_id == customer_id)
        if status_filter:
            q = q.where(SalesInvoice.status == status_filter)
        q = q.order_by(SalesInvoice.draft_date.desc()).offset(skip).limit(limit)
        result = await db.execute(q)
        return list(result.scalars())

    # -------------------------------------------------------------------
    # Mark overdue (scheduled job)
    # -------------------------------------------------------------------

    @staticmethod
    async def mark_overdue(db: AsyncSession) -> int:
        """
        Update status → OVERDUE for all past-due unpaid invoices.
        Returns the count of updated invoices.
        Run this daily via APScheduler / Celery beat.
        """
        today = date.today()
        r = await db.execute(
            select(SalesInvoice).where(
                SalesInvoice.due_date < today,
                SalesInvoice.status.in_([
                    InvoiceStatus.ISSUED,
                    InvoiceStatus.PARTIAL_PAID,
                ]),
            )
        )
        invoices = r.scalars().all()
        for inv in invoices:
            inv.status = InvoiceStatus.OVERDUE
        await db.flush()
        return len(invoices)

    # -------------------------------------------------------------------
    # Private: stock helpers
    # -------------------------------------------------------------------

    @staticmethod
    async def _create_outbound_movement(
        db: AsyncSession,
        invoice: SalesInvoice,
        line: SalesInvoiceLine,
        user_id: int,
    ) -> Optional[int]:
        """Create OUTBOUND inventory movement for one invoice line."""
        try:
            from app.models.inventory import InventoryMovement, MovementType, StockLevel

            stock_r = await db.execute(
                select(StockLevel)
                .where(
                    StockLevel.item_id == line.item_id,
                    StockLevel.quantity_on_hand >= line.quantity,
                )
                .order_by(StockLevel.quantity_on_hand.desc())
                .limit(1)
            )
            stock = stock_r.scalar_one_or_none()
            if not stock:
                return None

            qty_before = stock.quantity_on_hand
            stock.quantity_on_hand -= line.quantity
            stock.quantity_available = stock.quantity_on_hand - (
                stock.quantity_reserved or Decimal("0")
            )
            await db.flush()

            movement = InventoryMovement(
                item_id=line.item_id,
                location_id=stock.location_id,
                movement_type=MovementType.OUTBOUND,
                quantity=line.quantity,
                quantity_before=qty_before,
                quantity_after=stock.quantity_on_hand,
                reference_number=invoice.invoice_number,
                reason=f"Sale — Invoice {invoice.invoice_number}",
                notes=f"Customer: {invoice.customer_id}",
                unit_cost=line.unit_cost,
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            db.add(movement)
            await db.flush()
            return movement.id

        except Exception:
            logger.exception(
                "Failed to create outbound movement for invoice %s line %s",
                invoice.invoice_number,
                line.id,
            )
            return None

    @staticmethod
    async def _return_stock(
        db: AsyncSession,
        invoice: SalesInvoice,
        user_id: int,
    ) -> None:
        """Create INBOUND movements to reverse outbound stock deductions on cancel."""
        lines_r = await db.execute(
            select(SalesInvoiceLine).where(SalesInvoiceLine.invoice_id == invoice.id)
        )
        for line in lines_r.scalars().all():
            if not line.stock_movement_id:
                continue
            try:
                from app.models.inventory import InventoryMovement, MovementType, StockLevel

                orig = await db.get(InventoryMovement, line.stock_movement_id)
                if not orig or not orig.location_id:
                    continue

                stock_r = await db.execute(
                    select(StockLevel).where(
                        StockLevel.item_id == line.item_id,
                        StockLevel.location_id == orig.location_id,
                    )
                )
                stock = stock_r.scalar_one_or_none()
                if not stock:
                    continue

                qty_before = stock.quantity_on_hand
                stock.quantity_on_hand += line.quantity
                stock.quantity_available = stock.quantity_on_hand - (
                    stock.quantity_reserved or Decimal("0")
                )
                await db.flush()

                db.add(InventoryMovement(
                    item_id=line.item_id,
                    location_id=orig.location_id,
                    movement_type=MovementType.INBOUND,
                    quantity=line.quantity,
                    quantity_before=qty_before,
                    quantity_after=stock.quantity_on_hand,
                    reference_number=f"CANCEL-{invoice.invoice_number}",
                    reason=f"Cancellation of invoice {invoice.invoice_number}",
                    unit_cost=line.unit_cost,
                    created_by_id=user_id,
                    updated_by_id=user_id,
                ))
                await db.flush()

            except Exception:
                logger.exception(
                    "Failed to return stock for invoice %s line %s",
                    invoice.invoice_number,
                    line.id,
                )


# ===========================================================================
# Payment Service
# ===========================================================================

class PaymentService:

    @staticmethod
    async def create(
        db: AsyncSession,
        data: PaymentCreate,
        created_by_id: int,
    ) -> SalesPayment:
        customer = await CustomerService.get_or_404(db, data.customer_id)

        invoice: Optional[SalesInvoice] = None
        if data.invoice_id:
            invoice = await db.get(SalesInvoice, data.invoice_id)
            if not invoice or invoice.customer_id != data.customer_id:
                raise HTTPException(
                    status_code=400,
                    detail="Invoice not found or does not belong to this customer.",
                )
            if invoice.status in (InvoiceStatus.PAID, InvoiceStatus.CANCELLED):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invoice is already {invoice.status}.",
                )
            if data.amount > invoice.amount_due:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Payment amount {data.amount} exceeds "
                        f"invoice amount due {invoice.amount_due}."
                    ),
                )

        last = await db.execute(
            select(SalesPayment.payment_number)
            .order_by(SalesPayment.id.desc())
            .limit(1)
        )
        payment_number = _next_sequence("PAY", last.scalar_one_or_none())

        payment = SalesPayment(
            payment_number=payment_number,
            customer_id=data.customer_id,
            invoice_id=data.invoice_id,
            payment_date=data.payment_date,
            amount=data.amount,
            method=data.method,
            bank_account_id=data.bank_account_id,
            reference_number=data.reference_number,
            notes=data.notes,
            status=PaymentStatus.PENDING,
            created_by_id=created_by_id,
            updated_by_id=created_by_id,
        )
        db.add(payment)

        if invoice:
            await PaymentService._apply_to_invoice(db, payment, invoice, customer)

        await db.flush()
        return payment

    @staticmethod
    async def _apply_to_invoice(
        db: AsyncSession,
        payment: SalesPayment,
        invoice: SalesInvoice,
        customer: Customer,
    ) -> None:
        invoice.amount_paid += payment.amount
        invoice.amount_due -= payment.amount
        customer.total_paid += payment.amount
        customer.balance_due -= payment.amount

        if invoice.amount_due <= Decimal("0"):
            invoice.status = InvoiceStatus.PAID
        elif invoice.amount_paid > Decimal("0"):
            invoice.status = InvoiceStatus.PARTIAL_PAID

    @staticmethod
    async def allocate(
        db: AsyncSession,
        payment_id: int,
        data: PaymentAllocate,
    ) -> SalesPayment:
        payment = await db.get(SalesPayment, payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found.")
        if payment.invoice_id:
            raise HTTPException(
                status_code=400,
                detail="Payment is already allocated to an invoice.",
            )

        invoice = await db.get(SalesInvoice, data.invoice_id)
        if not invoice or invoice.customer_id != payment.customer_id:
            raise HTTPException(
                status_code=400,
                detail="Invoice not found or customer mismatch.",
            )
        if data.amount > payment.amount:
            raise HTTPException(
                status_code=400,
                detail="Allocation amount exceeds payment amount.",
            )

        payment.invoice_id = data.invoice_id
        customer = await db.get(Customer, payment.customer_id)
        await PaymentService._apply_to_invoice(db, payment, invoice, customer)
        await db.flush()
        return payment

    @staticmethod
    async def clear(db: AsyncSession, payment_id: int) -> SalesPayment:
        payment = await db.get(SalesPayment, payment_id)
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found.")
        if payment.status != PaymentStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Payment status is already {payment.status}.",
            )
        payment.status = PaymentStatus.CLEARED
        await db.flush()
        return payment


# ===========================================================================
# Report Service
# ===========================================================================

class ReportService:

    @staticmethod
    async def revenue_by_period(
        db: AsyncSession,
        from_date: date,
        to_date: date,
    ) -> list[RevenueByPeriodRow]:
        result = await db.execute(
            select(
                func.to_char(SalesInvoice.issue_date, "YYYY-MM").label("period"),
                func.count(SalesInvoice.id).label("invoice_count"),
                func.sum(SalesInvoice.subtotal).label("subtotal"),
                func.sum(SalesInvoice.discount_amount).label("discount"),
                func.sum(SalesInvoice.tax_amount).label("tax"),
                func.sum(SalesInvoice.total_amount).label("total"),
                func.sum(SalesInvoice.amount_paid).label("total_paid"),
                func.sum(SalesInvoice.amount_due).label("outstanding"),
            )
            .where(
                and_(
                    SalesInvoice.issue_date >= from_date,
                    SalesInvoice.issue_date <= to_date,
                    SalesInvoice.status != InvoiceStatus.CANCELLED,
                )
            )
            .group_by("period")
            .order_by("period")
        )
        return [
            RevenueByPeriodRow(
                period=row.period,
                invoice_count=row.invoice_count,
                subtotal=row.subtotal or Decimal("0"),
                discount=row.discount or Decimal("0"),
                tax=row.tax or Decimal("0"),
                total=row.total or Decimal("0"),
                total_paid=row.total_paid or Decimal("0"),
                outstanding=row.outstanding or Decimal("0"),
            )
            for row in result
        ]

    @staticmethod
    async def top_customers(
        db: AsyncSession,
        from_date: date,
        to_date: date,
        limit: int = 10,
    ) -> list[TopCustomerRow]:
        result = await db.execute(
            select(
                Customer.id,
                Customer.code,
                Customer.name,
                func.count(SalesInvoice.id).label("invoice_count"),
                func.sum(SalesInvoice.total_amount).label("total_revenue"),
                func.sum(SalesInvoice.amount_paid).label("total_paid"),
                func.sum(SalesInvoice.amount_due).label("balance_due"),
            )
            .join(SalesInvoice, SalesInvoice.customer_id == Customer.id)
            .where(
                and_(
                    SalesInvoice.issue_date >= from_date,
                    SalesInvoice.issue_date <= to_date,
                    SalesInvoice.status != InvoiceStatus.CANCELLED,
                )
            )
            .group_by(Customer.id, Customer.code, Customer.name)
            .order_by(func.sum(SalesInvoice.total_amount).desc())
            .limit(limit)
        )
        return [
            TopCustomerRow(
                customer_id=row.id,
                customer_code=row.code,
                customer_name=row.name,
                invoice_count=row.invoice_count,
                total_revenue=row.total_revenue or Decimal("0"),
                total_paid=row.total_paid or Decimal("0"),
                balance_due=row.balance_due or Decimal("0"),
            )
            for row in result
        ]

    @staticmethod
    async def product_margins(
        db: AsyncSession,
        from_date: date,
        to_date: date,
    ) -> list[ProductMarginRow]:
        result = await db.execute(
            select(
                SalesInvoiceLine.item_id,
                func.sum(SalesInvoiceLine.quantity).label("quantity_sold"),
                func.sum(SalesInvoiceLine.line_total).label("revenue"),
                func.sum(SalesInvoiceLine.total_cost).label("cogs"),
            )
            .join(SalesInvoice, SalesInvoice.id == SalesInvoiceLine.invoice_id)
            .where(
                and_(
                    SalesInvoice.issue_date >= from_date,
                    SalesInvoice.issue_date <= to_date,
                    SalesInvoice.status != InvoiceStatus.CANCELLED,
                )
            )
            .group_by(SalesInvoiceLine.item_id)
            .order_by(func.sum(SalesInvoiceLine.line_total).desc())
        )
        rows = []
        for row in result:
            revenue = row.revenue or Decimal("0")
            cogs = row.cogs or Decimal("0")
            gross_profit = revenue - cogs
            margin_pct = (
                (gross_profit / revenue * 100).quantize(Decimal("0.01"))
                if revenue > Decimal("0") else Decimal("0")
            )
            rows.append(ProductMarginRow(
                item_id=row.item_id,
                sku="",        # Enrich from inventory service if needed
                item_name="",
                quantity_sold=row.quantity_sold,
                revenue=revenue,
                cogs=cogs,
                gross_profit=gross_profit,
                margin_percent=margin_pct,
            ))
        return rows

    @staticmethod
    async def tax_export(
        db: AsyncSession,
        from_date: date,
        to_date: date,
    ) -> list[TaxExportLine]:
        result = await db.execute(
            select(SalesInvoice, Customer)
            .join(Customer, Customer.id == SalesInvoice.customer_id)
            .where(
                and_(
                    SalesInvoice.issue_date >= from_date,
                    SalesInvoice.issue_date <= to_date,
                    SalesInvoice.status.in_([
                        InvoiceStatus.ISSUED,
                        InvoiceStatus.PARTIAL_PAID,
                        InvoiceStatus.PAID,
                    ]),
                )
            )
            .order_by(SalesInvoice.issue_date)
        )
        lines = []
        for invoice, customer in result:
            tax_base = invoice.subtotal - invoice.discount_amount
            lines.append(TaxExportLine(
                invoice_number=invoice.invoice_number,
                tax_invoice_number=invoice.tax_invoice_number or "",
                issue_date=str(invoice.issue_date),
                customer_name=customer.name,
                customer_tax_id=customer.tax_id or "",
                economic_code=customer.economic_code or "",
                subtotal=invoice.subtotal,
                discount=invoice.discount_amount,
                tax_base=tax_base,
                vat_amount=invoice.tax_amount,
                total_amount=invoice.total_amount,
            ))
        return lines


# ===========================================================================
# Helper (private)
# ===========================================================================

def _estimate_invoice_total(data: InvoiceCreate) -> Decimal:
    """Quick pre-create credit limit estimate (no DB needed)."""
    total = Decimal("0")
    for ln in data.lines:
        base = ln.quantity * ln.unit_price
        net = base - ln.discount_amount
        tax = net * ln.tax_percent / Decimal("100")
        total += (net + tax)
    return total.quantize(Decimal("0.01"))


# ===========================================================================
# Singleton (backward-compat with existing imports)
# ===========================================================================

sales_service = SalesService()
