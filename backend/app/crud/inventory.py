"""
Inventory Module - CRUD Layer (Repository Pattern)
TOP WorX ERP System

All methods take an AsyncSession and return ORM instances.
Business logic (stock balancing, movement creation) lives in inventory_service.py.
"""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.inventory import (
    AuditStatus,
    InventoryAudit,
    InventoryAuditLine,
    InventoryCategory,
    InventoryItem,
    InventoryLocation,
    InventoryMovement,
    MovementType,
    StockLevel,
    Supplier,
)
from app.schemas.inventory import (
    InventoryCategoryCreate,
    InventoryCategoryUpdate,
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryLocationCreate,
    InventoryLocationUpdate,
    SupplierCreate,
    SupplierUpdate,
)


# ===========================================================================
# Category CRUD
# ===========================================================================
class CategoryCRUD:
    async def get(self, db: AsyncSession, category_id: int) -> Optional[InventoryCategory]:
        result = await db.execute(
            select(InventoryCategory).where(InventoryCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[InventoryCategory]:
        result = await db.execute(
            select(InventoryCategory).where(InventoryCategory.code == code.upper())
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        parent_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[InventoryCategory]]:
        q = select(InventoryCategory)
        if parent_id is not None:
            q = q.where(InventoryCategory.parent_id == parent_id)
        if is_active is not None:
            q = q.where(InventoryCategory.is_active == is_active)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def create(
        self, db: AsyncSession, data: InventoryCategoryCreate, user_id: Optional[int] = None
    ) -> InventoryCategory:
        obj = InventoryCategory(**data.model_dump(), created_by=user_id, updated_by=user_id)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def update(
        self,
        db: AsyncSession,
        obj: InventoryCategory,
        data: InventoryCategoryUpdate,
        user_id: Optional[int] = None,
    ) -> InventoryCategory:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        obj.updated_by = user_id
        await db.flush()
        await db.refresh(obj)
        return obj


# ===========================================================================
# Supplier CRUD
# ===========================================================================
class SupplierCRUD:
    async def get(self, db: AsyncSession, supplier_id: int) -> Optional[Supplier]:
        result = await db.execute(select(Supplier).where(Supplier.id == supplier_id))
        return result.scalar_one_or_none()

    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Supplier]:
        result = await db.execute(select(Supplier).where(Supplier.code == code.upper()))
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[Supplier]]:
        q = select(Supplier)
        if is_active is not None:
            q = q.where(Supplier.is_active == is_active)
        if search:
            q = q.where(
                or_(
                    Supplier.name.ilike(f"%{search}%"),
                    Supplier.code.ilike(f"%{search}%"),
                )
            )
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def create(
        self, db: AsyncSession, data: SupplierCreate, user_id: Optional[int] = None
    ) -> Supplier:
        obj = Supplier(**data.model_dump(), created_by=user_id, updated_by=user_id)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def update(
        self,
        db: AsyncSession,
        obj: Supplier,
        data: SupplierUpdate,
        user_id: Optional[int] = None,
    ) -> Supplier:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        obj.updated_by = user_id
        await db.flush()
        await db.refresh(obj)
        return obj


# ===========================================================================
# InventoryItem CRUD
# ===========================================================================
class InventoryItemCRUD:
    async def get(
        self, db: AsyncSession, item_id: int, with_stock: bool = False
    ) -> Optional[InventoryItem]:
        q = select(InventoryItem).where(InventoryItem.id == item_id)
        if with_stock:
            q = q.options(
                selectinload(InventoryItem.stock_levels).selectinload(StockLevel.location),
                selectinload(InventoryItem.category),
                selectinload(InventoryItem.default_supplier),
            )
        result = await db.execute(q)
        return result.scalar_one_or_none()

    async def get_by_sku(self, db: AsyncSession, sku: str) -> Optional[InventoryItem]:
        result = await db.execute(
            select(InventoryItem).where(InventoryItem.sku == sku.upper())
        )
        return result.scalar_one_or_none()

    async def get_by_barcode(self, db: AsyncSession, barcode: str) -> Optional[InventoryItem]:
        result = await db.execute(
            select(InventoryItem).where(InventoryItem.barcode == barcode)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = True,
        search: Optional[str] = None,
        low_stock: bool = False,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[InventoryItem]]:
        q = select(InventoryItem)
        if is_active is not None:
            q = q.where(InventoryItem.is_active == is_active)
        if category_id is not None:
            q = q.where(InventoryItem.category_id == category_id)
        if search:
            q = q.where(
                or_(
                    InventoryItem.name.ilike(f"%{search}%"),
                    InventoryItem.sku.ilike(f"%{search}%"),
                    InventoryItem.barcode.ilike(f"%{search}%"),
                )
            )
        if low_stock:
            # Items where any stock level is at or below its effective reorder point
            q = q.join(InventoryItem.stock_levels).where(
                StockLevel.quantity_on_hand <= InventoryItem.global_reorder_point
            )
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def create(
        self,
        db: AsyncSession,
        data: InventoryItemCreate,
        sku: str,
        barcode: Optional[str] = None,
        qr_code: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> InventoryItem:
        payload = data.model_dump(exclude={"sku"})
        obj = InventoryItem(
            **payload,
            sku=sku,
            barcode=barcode,
            qr_code=qr_code,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def update(
        self,
        db: AsyncSession,
        obj: InventoryItem,
        data: InventoryItemUpdate,
        user_id: Optional[int] = None,
    ) -> InventoryItem:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        obj.updated_by = user_id
        await db.flush()
        await db.refresh(obj)
        return obj

    async def soft_delete(
        self, db: AsyncSession, obj: InventoryItem, user_id: Optional[int] = None
    ) -> InventoryItem:
        obj.is_active = False
        obj.updated_by = user_id
        await db.flush()
        return obj


# ===========================================================================
# InventoryLocation CRUD
# ===========================================================================
class InventoryLocationCRUD:
    async def get(self, db: AsyncSession, location_id: int) -> Optional[InventoryLocation]:
        result = await db.execute(
            select(InventoryLocation).where(InventoryLocation.id == location_id)
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[InventoryLocation]:
        result = await db.execute(
            select(InventoryLocation).where(InventoryLocation.code == code.upper())
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        warehouse: Optional[str] = None,
        is_active: Optional[bool] = True,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[InventoryLocation]]:
        q = select(InventoryLocation)
        if warehouse:
            q = q.where(InventoryLocation.warehouse.ilike(f"%{warehouse}%"))
        if is_active is not None:
            q = q.where(InventoryLocation.is_active == is_active)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def create(
        self, db: AsyncSession, data: InventoryLocationCreate, user_id: Optional[int] = None
    ) -> InventoryLocation:
        obj = InventoryLocation(**data.model_dump(), created_by=user_id, updated_by=user_id)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def update(
        self,
        db: AsyncSession,
        obj: InventoryLocation,
        data: InventoryLocationUpdate,
        user_id: Optional[int] = None,
    ) -> InventoryLocation:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        obj.updated_by = user_id
        await db.flush()
        await db.refresh(obj)
        return obj


# ===========================================================================
# StockLevel CRUD
# ===========================================================================
class StockLevelCRUD:
    async def get_or_create(
        self,
        db: AsyncSession,
        item_id: int,
        location_id: int,
        user_id: Optional[int] = None,
    ) -> StockLevel:
        result = await db.execute(
            select(StockLevel).where(
                and_(StockLevel.item_id == item_id, StockLevel.location_id == location_id)
            )
        )
        obj = result.scalar_one_or_none()
        if obj is None:
            obj = StockLevel(
                item_id=item_id,
                location_id=location_id,
                created_by=user_id,
                updated_by=user_id,
            )
            db.add(obj)
            await db.flush()
            await db.refresh(obj)
        return obj

    async def get_by_item(
        self,
        db: AsyncSession,
        item_id: int,
        with_location: bool = False,
    ) -> Sequence[StockLevel]:
        q = select(StockLevel).where(StockLevel.item_id == item_id)
        if with_location:
            q = q.options(selectinload(StockLevel.location))
        return (await db.execute(q)).scalars().all()

    async def get_by_location(
        self, db: AsyncSession, location_id: int
    ) -> Sequence[StockLevel]:
        result = await db.execute(
            select(StockLevel).where(StockLevel.location_id == location_id)
        )
        return result.scalars().all()

    async def list(
        self,
        db: AsyncSession,
        *,
        item_id: Optional[int] = None,
        location_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[int, Sequence[StockLevel]]:
        q = select(StockLevel).options(
            selectinload(StockLevel.location), selectinload(StockLevel.item)
        )
        if item_id is not None:
            q = q.where(StockLevel.item_id == item_id)
        if location_id is not None:
            q = q.where(StockLevel.location_id == location_id)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows


# ===========================================================================
# InventoryMovement CRUD
# ===========================================================================
class InventoryMovementCRUD:
    async def get(self, db: AsyncSession, movement_id: int) -> Optional[InventoryMovement]:
        result = await db.execute(
            select(InventoryMovement).where(InventoryMovement.id == movement_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        item_id: Optional[int] = None,
        location_id: Optional[int] = None,
        movement_type: Optional[MovementType] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[int, Sequence[InventoryMovement]]:
        q = select(InventoryMovement).options(
            selectinload(InventoryMovement.item),
            selectinload(InventoryMovement.from_location),
            selectinload(InventoryMovement.to_location),
        )
        if item_id is not None:
            q = q.where(InventoryMovement.item_id == item_id)
        if location_id is not None:
            q = q.where(
                or_(
                    InventoryMovement.from_location_id == location_id,
                    InventoryMovement.to_location_id == location_id,
                )
            )
        if movement_type is not None:
            q = q.where(InventoryMovement.movement_type == movement_type)
        if date_from is not None:
            q = q.where(InventoryMovement.movement_date >= date_from)
        if date_to is not None:
            q = q.where(InventoryMovement.movement_date <= date_to)
        q = q.order_by(InventoryMovement.movement_date.desc())
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def create(
        self,
        db: AsyncSession,
        *,
        item_id: int,
        movement_type: MovementType,
        quantity: Decimal,
        quantity_before: Decimal,
        quantity_after: Decimal,
        reference_number: str,
        from_location_id: Optional[int] = None,
        to_location_id: Optional[int] = None,
        supplier_id: Optional[int] = None,
        unit_cost: Optional[Decimal] = None,
        reason: Optional[str] = None,
        notes: Optional[str] = None,
        external_reference: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> InventoryMovement:
        obj = InventoryMovement(
            item_id=item_id,
            movement_type=movement_type,
            quantity=quantity,
            quantity_before=quantity_before,
            quantity_after=quantity_after,
            reference_number=reference_number,
            from_location_id=from_location_id,
            to_location_id=to_location_id,
            supplier_id=supplier_id,
            unit_cost=unit_cost,
            reason=reason,
            notes=notes,
            external_reference=external_reference,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj


# ===========================================================================
# InventoryAudit CRUD
# ===========================================================================
class InventoryAuditCRUD:
    async def get(
        self, db: AsyncSession, audit_id: int, with_lines: bool = False
    ) -> Optional[InventoryAudit]:
        q = select(InventoryAudit).where(InventoryAudit.id == audit_id)
        if with_lines:
            q = q.options(selectinload(InventoryAudit.lines))
        result = await db.execute(q)
        return result.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        status: Optional[AuditStatus] = None,
        location_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[InventoryAudit]]:
        q = select(InventoryAudit)
        if status:
            q = q.where(InventoryAudit.status == status)
        if location_id:
            q = q.where(InventoryAudit.location_id == location_id)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def create(
        self,
        db: AsyncSession,
        reference_number: str,
        description: Optional[str] = None,
        location_id: Optional[int] = None,
        scheduled_date: Optional[datetime] = None,
        notes: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> InventoryAudit:
        obj = InventoryAudit(
            reference_number=reference_number,
            description=description,
            location_id=location_id,
            scheduled_date=scheduled_date,
            notes=notes,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def add_line(
        self,
        db: AsyncSession,
        audit_id: int,
        item_id: int,
        location_id: int,
        system_quantity: Decimal,
        counted_quantity: Optional[Decimal] = None,
        user_id: Optional[int] = None,
    ) -> InventoryAuditLine:
        variance = (
            counted_quantity - system_quantity if counted_quantity is not None else None
        )
        line = InventoryAuditLine(
            audit_id=audit_id,
            item_id=item_id,
            location_id=location_id,
            system_quantity=system_quantity,
            counted_quantity=counted_quantity,
            variance=variance,
            created_by=user_id,
            updated_by=user_id,
        )
        db.add(line)
        await db.flush()
        await db.refresh(line)
        return line


# ---------------------------------------------------------------------------
# Singleton instances (import these in service / routers)
# ---------------------------------------------------------------------------
category_crud = CategoryCRUD()
supplier_crud = SupplierCRUD()
item_crud = InventoryItemCRUD()
location_crud = InventoryLocationCRUD()
stock_crud = StockLevelCRUD()
movement_crud = InventoryMovementCRUD()
audit_crud = InventoryAuditCRUD()
