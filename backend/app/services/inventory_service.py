"""
Inventory Module - Service Layer (Business Logic)
TOP WorX ERP System

All public methods operate within a single AsyncSession that is managed by
the caller (FastAPI dependency). Methods flush but do NOT commit — the router
commits after all operations succeed, giving us a clean transaction boundary.
"""
from __future__ import annotations

import base64
import io
import random
import string
from datetime import datetime
from decimal import Decimal
from typing import Optional

import barcode as python_barcode
import qrcode
from barcode.writer import ImageWriter
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.inventory import (
    audit_crud,
    item_crud,
    location_crud,
    movement_crud,
    stock_crud,
)
from app.models.inventory import (
    InventoryAudit,
    InventoryAuditLine,
    InventoryItem,
    InventoryMovement,
    MovementType,
    StockLevel,
)
from app.schemas.inventory import (
    InboundMovementCreate,
    InventoryAuditCreate,
    InventoryAuditLineCreate,
    InventoryItemCreate,
    OutboundMovementCreate,
    StockAdjustRequest,
    StockTransferRequest,
)


class InventoryServiceError(Exception):
    """Base exception for business rule violations."""


class InsufficientStockError(InventoryServiceError):
    pass


class ItemHasStockError(InventoryServiceError):
    pass


class DuplicateSKUError(InventoryServiceError):
    pass


class InventoryService:
    # -----------------------------------------------------------------------
    # SKU / Barcode / QR generation
    # -----------------------------------------------------------------------

    async def generate_sku(self, db: AsyncSession, prefix: str = "ITEM") -> str:
        """
        Generate a unique SKU in the form PREFIX-XXXXX.

        DECISION POINT ⚙️: Adjust the prefix/format to match your naming convention.
        Options:
          - Category-based:  ELEC-00042
          - Date-based:      ITEM-20240115-001
          - Sequential:      ITEM-00001  (current)
        """
        prefix = prefix.upper()[:8]
        for attempt in range(20):
            suffix = "".join(random.choices(string.digits, k=5))
            candidate = f"{prefix}-{suffix}"
            existing = await item_crud.get_by_sku(db, candidate)
            if existing is None:
                return candidate
        # Fallback to longer random suffix
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"{prefix}-{suffix}"

    def generate_barcode_base64(self, sku: str) -> str:
        """
        Generate a CODE128 barcode as a base64-encoded PNG.

        DECISION POINT ⚙️: Choose barcode symbology:
          - Code128 (current) — alphanumeric, widely supported
          - EAN13 — retail standard, requires 12-digit numeric input
          - QR only — if you want a single code for both scanning use cases
        """
        buffer = io.BytesIO()
        code128 = python_barcode.get_barcode_class("code128")
        bc = code128(sku, writer=ImageWriter())
        bc.write(buffer)
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")

    def generate_qr_base64(self, payload: dict) -> str:
        """Generate a QR code containing item metadata as base64 PNG."""
        import json

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=2,
        )
        qr.add_data(json.dumps(payload))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("utf-8")

    # -----------------------------------------------------------------------
    # Reference number generation
    # -----------------------------------------------------------------------

    def _movement_ref(self, prefix: str) -> str:
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        rand = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        return f"{prefix}-{ts}-{rand}"

    def _audit_ref(self) -> str:
        ts = datetime.utcnow().strftime("%Y%m%d")
        rand = "".join(random.choices(string.digits, k=5))
        return f"AUDIT-{ts}-{rand}"

    # -----------------------------------------------------------------------
    # Item creation
    # -----------------------------------------------------------------------

    async def create_item(
        self,
        db: AsyncSession,
        data: InventoryItemCreate,
        user_id: Optional[int] = None,
    ) -> InventoryItem:
        # 1. Resolve SKU
        if data.sku:
            existing = await item_crud.get_by_sku(db, data.sku)
            if existing:
                raise DuplicateSKUError(f"SKU '{data.sku}' already exists")
            sku = data.sku
        else:
            # Auto-generate from category prefix if category is provided
            prefix = "ITEM"
            sku = await self.generate_sku(db, prefix)

        # 2. Generate barcode and QR code
        barcode_b64 = self.generate_barcode_base64(sku)
        qr_payload = {"sku": sku, "system": "TOP WorX ERP"}
        qr_b64 = self.generate_qr_base64(qr_payload)

        # 3. Persist
        item = await item_crud.create(
            db,
            data=data,
            sku=sku,
            barcode=sku,  # use SKU as barcode value; base64 stored in qr_code
            qr_code=qr_b64,
            user_id=user_id,
        )
        return item

    # -----------------------------------------------------------------------
    # Stock availability check (used by reservation system)
    # -----------------------------------------------------------------------

    async def check_availability(
        self,
        db: AsyncSession,
        item_id: int,
        location_id: int,
        required_quantity: Decimal,
    ) -> bool:
        """
        Returns True if enough available (on_hand - reserved) stock exists.
        Used for soft-reservation before outbound movements.
        """
        stock = await stock_crud.get_or_create(db, item_id, location_id)
        return stock.quantity_available >= required_quantity

    # -----------------------------------------------------------------------
    # Inbound (receive goods)
    # -----------------------------------------------------------------------

    async def process_inbound(
        self,
        db: AsyncSession,
        data: InboundMovementCreate,
        user_id: Optional[int] = None,
    ) -> InventoryMovement:
        item = await item_crud.get(db, data.item_id)
        if not item or not item.is_active:
            raise InventoryServiceError(f"Item {data.item_id} not found or inactive")

        location = await location_crud.get(db, data.to_location_id)
        if not location or not location.is_active or not location.is_receivable:
            raise InventoryServiceError(
                f"Location {data.to_location_id} not found or not receivable"
            )

        stock = await stock_crud.get_or_create(db, data.item_id, data.to_location_id, user_id)
        qty_before = stock.quantity_on_hand
        qty_after = qty_before + data.quantity

        # Update stock
        stock.quantity_on_hand = qty_after
        stock.updated_by = user_id

        # Update last purchase price on item
        if data.unit_cost is not None:
            item.last_purchase_price = data.unit_cost
            item.updated_by = user_id

        movement = await movement_crud.create(
            db,
            item_id=data.item_id,
            movement_type=MovementType.INBOUND,
            quantity=data.quantity,
            quantity_before=qty_before,
            quantity_after=qty_after,
            reference_number=self._movement_ref("IN"),
            to_location_id=data.to_location_id,
            supplier_id=data.supplier_id,
            unit_cost=data.unit_cost,
            reason=data.reason,
            notes=data.notes,
            external_reference=data.external_reference,
            user_id=user_id,
        )
        await db.flush()
        return movement

    # -----------------------------------------------------------------------
    # Outbound (issue goods)
    # -----------------------------------------------------------------------

    async def process_outbound(
        self,
        db: AsyncSession,
        data: OutboundMovementCreate,
        user_id: Optional[int] = None,
    ) -> InventoryMovement:
        item = await item_crud.get(db, data.item_id)
        if not item or not item.is_active:
            raise InventoryServiceError(f"Item {data.item_id} not found or inactive")

        location = await location_crud.get(db, data.from_location_id)
        if not location or not location.is_active or not location.is_pickable:
            raise InventoryServiceError(
                f"Location {data.from_location_id} not found or not pickable"
            )

        stock = await stock_crud.get_or_create(db, data.item_id, data.from_location_id, user_id)
        qty_before = stock.quantity_on_hand
        qty_after = qty_before - data.quantity

        # Check available stock
        if stock.quantity_available < data.quantity and not item.allow_negative_stock:
            raise InsufficientStockError(
                f"Insufficient stock: available={stock.quantity_available}, "
                f"requested={data.quantity}"
            )

        stock.quantity_on_hand = qty_after
        stock.updated_by = user_id

        movement = await movement_crud.create(
            db,
            item_id=data.item_id,
            movement_type=MovementType.OUTBOUND,
            quantity=data.quantity,
            quantity_before=qty_before,
            quantity_after=qty_after,
            reference_number=self._movement_ref("OUT"),
            from_location_id=data.from_location_id,
            reason=data.reason,
            notes=data.notes,
            external_reference=data.external_reference,
            user_id=user_id,
        )
        await db.flush()
        return movement

    # -----------------------------------------------------------------------
    # Transfer (atomic: decrease source, increase destination)
    # -----------------------------------------------------------------------

    async def transfer_stock(
        self,
        db: AsyncSession,
        data: StockTransferRequest,
        user_id: Optional[int] = None,
    ) -> tuple[InventoryMovement, InventoryMovement]:
        """
        Performs a two-sided transfer in a single DB transaction.
        Returns (outbound_movement, inbound_movement).
        The caller must commit the session.
        """
        item = await item_crud.get(db, data.item_id)
        if not item or not item.is_active:
            raise InventoryServiceError(f"Item {data.item_id} not found or inactive")

        from_loc = await location_crud.get(db, data.from_location_id)
        to_loc = await location_crud.get(db, data.to_location_id)

        if not from_loc or not from_loc.is_active or not from_loc.is_pickable:
            raise InventoryServiceError(f"Source location {data.from_location_id} invalid")
        if not to_loc or not to_loc.is_active or not to_loc.is_receivable:
            raise InventoryServiceError(f"Destination location {data.to_location_id} invalid")

        from_stock = await stock_crud.get_or_create(
            db, data.item_id, data.from_location_id, user_id
        )
        to_stock = await stock_crud.get_or_create(
            db, data.item_id, data.to_location_id, user_id
        )

        if from_stock.quantity_available < data.quantity and not item.allow_negative_stock:
            raise InsufficientStockError(
                f"Insufficient stock at source: available={from_stock.quantity_available}"
            )

        ref_base = self._movement_ref("TRF")

        # Decrease source
        from_before = from_stock.quantity_on_hand
        from_stock.quantity_on_hand -= data.quantity
        from_stock.updated_by = user_id

        out_mv = await movement_crud.create(
            db,
            item_id=data.item_id,
            movement_type=MovementType.TRANSFER,
            quantity=data.quantity,
            quantity_before=from_before,
            quantity_after=from_stock.quantity_on_hand,
            reference_number=f"{ref_base}-OUT",
            from_location_id=data.from_location_id,
            to_location_id=data.to_location_id,
            reason=data.reason,
            notes=data.notes,
            external_reference=data.external_reference,
            user_id=user_id,
        )

        # Increase destination
        to_before = to_stock.quantity_on_hand
        to_stock.quantity_on_hand += data.quantity
        to_stock.updated_by = user_id

        in_mv = await movement_crud.create(
            db,
            item_id=data.item_id,
            movement_type=MovementType.TRANSFER,
            quantity=data.quantity,
            quantity_before=to_before,
            quantity_after=to_stock.quantity_on_hand,
            reference_number=f"{ref_base}-IN",
            from_location_id=data.from_location_id,
            to_location_id=data.to_location_id,
            reason=data.reason,
            notes=data.notes,
            external_reference=data.external_reference,
            user_id=user_id,
        )

        await db.flush()
        return out_mv, in_mv

    # -----------------------------------------------------------------------
    # Manual adjustment
    # -----------------------------------------------------------------------

    async def adjust_stock(
        self,
        db: AsyncSession,
        data: StockAdjustRequest,
        user_id: Optional[int] = None,
    ) -> InventoryMovement:
        item = await item_crud.get(db, data.item_id)
        if not item or not item.is_active:
            raise InventoryServiceError(f"Item {data.item_id} not found or inactive")

        stock = await stock_crud.get_or_create(db, data.item_id, data.location_id, user_id)
        qty_before = stock.quantity_on_hand

        # Compute new quantity
        if data.new_quantity is not None:
            qty_after = data.new_quantity
        else:
            qty_after = qty_before + data.quantity_delta  # type: ignore[operator]

        if qty_after < Decimal("0") and not item.allow_negative_stock:
            raise InsufficientStockError(
                f"Adjustment would result in negative stock: {qty_after}"
            )

        delta = qty_after - qty_before
        if delta == Decimal("0"):
            raise InventoryServiceError("Adjustment quantity results in no change")

        stock.quantity_on_hand = qty_after
        stock.updated_by = user_id

        movement = await movement_crud.create(
            db,
            item_id=data.item_id,
            movement_type=MovementType.ADJUSTMENT,
            quantity=abs(delta),
            quantity_before=qty_before,
            quantity_after=qty_after,
            reference_number=self._movement_ref("ADJ"),
            from_location_id=data.location_id if delta < 0 else None,
            to_location_id=data.location_id if delta > 0 else None,
            reason=data.reason,
            notes=data.notes,
            external_reference=data.external_reference,
            user_id=user_id,
        )
        await db.flush()
        return movement

    # -----------------------------------------------------------------------
    # Physical count / audit
    # -----------------------------------------------------------------------

    async def create_audit(
        self,
        db: AsyncSession,
        data: InventoryAuditCreate,
        user_id: Optional[int] = None,
    ) -> InventoryAudit:
        """
        Creates an audit session and pre-populates lines with current system quantities
        for all items at the specified location (or all locations if not specified).
        """
        ref = self._audit_ref()
        audit = await audit_crud.create(
            db,
            reference_number=ref,
            description=data.description,
            location_id=data.location_id,
            scheduled_date=data.scheduled_date,
            notes=data.notes,
            user_id=user_id,
        )

        # Pre-populate lines
        stock_rows: list[StockLevel] = []
        if data.location_id:
            stock_rows = list(await stock_crud.get_by_location(db, data.location_id))
        else:
            _, stock_rows = await stock_crud.list(db, limit=10_000)  # type: ignore[assignment]

        for row in stock_rows:
            await audit_crud.add_line(
                db,
                audit_id=audit.id,
                item_id=row.item_id,
                location_id=row.location_id,
                system_quantity=row.quantity_on_hand,
                user_id=user_id,
            )

        await db.flush()
        return audit

    async def submit_audit_count(
        self,
        db: AsyncSession,
        audit_id: int,
        lines: list[InventoryAuditLineCreate],
        user_id: Optional[int] = None,
    ) -> InventoryAudit:
        """Record physical count results against an open audit session."""
        audit = await audit_crud.get(db, audit_id, with_lines=True)
        if not audit:
            raise InventoryServiceError(f"Audit {audit_id} not found")
        if audit.status not in (
            "draft",
            "in_progress",
        ):
            raise InventoryServiceError(
                f"Cannot submit count for audit in status '{audit.status}'"
            )

        audit.status = "in_progress"
        line_map = {(ln.item_id, ln.location_id): ln for ln in audit.lines}

        for count_line in lines:
            key = (count_line.item_id, count_line.location_id)
            existing = line_map.get(key)
            if existing:
                existing.counted_quantity = count_line.counted_quantity
                existing.variance = count_line.counted_quantity - existing.system_quantity
                existing.updated_by = user_id
            else:
                # Item not pre-populated (added to location after audit started)
                system_qty = Decimal("0")
                stock = await stock_crud.get_or_create(
                    db, count_line.item_id, count_line.location_id
                )
                system_qty = stock.quantity_on_hand
                await audit_crud.add_line(
                    db,
                    audit_id=audit_id,
                    item_id=count_line.item_id,
                    location_id=count_line.location_id,
                    system_quantity=system_qty,
                    counted_quantity=count_line.counted_quantity,
                    user_id=user_id,
                )

        audit.updated_by = user_id
        await db.flush()
        return audit

    async def approve_and_reconcile_audit(
        self,
        db: AsyncSession,
        audit_id: int,
        approver_id: int,
    ) -> InventoryAudit:
        """
        Approve the audit and automatically post adjustment movements for all variances.
        """
        audit = await audit_crud.get(db, audit_id, with_lines=True)
        if not audit:
            raise InventoryServiceError(f"Audit {audit_id} not found")
        if audit.status != "in_progress":
            raise InventoryServiceError("Audit must be in_progress to approve")

        for line in audit.lines:
            if line.counted_quantity is None:
                continue  # Skip uncounted lines
            if line.variance and line.variance != Decimal("0"):
                await self.adjust_stock(
                    db,
                    StockAdjustRequest(
                        item_id=line.item_id,
                        location_id=line.location_id,
                        new_quantity=line.counted_quantity,
                        reason=f"Physical count reconciliation — Audit {audit.reference_number}",
                    ),
                    user_id=approver_id,
                )
                line.is_reconciled = True
                line.updated_by = approver_id

        audit.status = "approved"
        audit.completed_date = datetime.utcnow()
        audit.approved_by = approver_id
        audit.updated_by = approver_id
        await db.flush()
        return audit

    # -----------------------------------------------------------------------
    # Delete guard
    # -----------------------------------------------------------------------

    async def assert_can_delete_item(self, db: AsyncSession, item_id: int) -> None:
        """Raise if item has any stock > 0 anywhere."""
        from sqlalchemy import select as sa_select

        result = await db.execute(
            sa_select(func.sum(StockLevel.quantity_on_hand)).where(
                StockLevel.item_id == item_id
            )
        )
        total: Optional[Decimal] = result.scalar_one_or_none()
        if total and total > Decimal("0"):
            raise ItemHasStockError(
                f"Cannot delete item {item_id}: total stock on hand = {total}"
            )


# Singleton
inventory_service = InventoryService()
