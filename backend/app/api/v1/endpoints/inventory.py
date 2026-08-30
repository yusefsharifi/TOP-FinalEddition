"""
Inventory Module - FastAPI Router
TOP WorX ERP System

Mount in api.py:
    from app.api.v1.endpoints.inventory import router as inventory_router
    api_router.include_router(inventory_router, prefix="/inventory", tags=["inventory"])
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select

from app.crud.inventory import (
    audit_crud,
    category_crud,
    item_crud,
    location_crud,
    movement_crud,
    stock_crud,
    supplier_crud,
)
from app.models.inventory import (
    InventoryItem,
    MovementType,
    StockLevel,
)
from app.schemas.inventory import (
    InboundMovementCreate,
    InventoryAuditCreate,
    InventoryAuditLineCreate,
    InventoryAuditResponse,
    InventoryCategoryCreate,
    InventoryCategoryResponse,
    InventoryCategoryUpdate,
    InventoryItemCreate,
    InventoryItemDetailResponse,
    InventoryItemResponse,
    InventoryItemUpdate,
    InventoryLocationCreate,
    InventoryLocationResponse,
    InventoryLocationUpdate,
    InventoryMovementResponse,
    LowStockReportItem,
    MovementSummaryItem,
    OutboundMovementCreate,
    StockAdjustRequest,
    StockLevelResponse,
    StockTransferRequest,
    SupplierCreate,
    SupplierResponse,
    SupplierUpdate,
)
from app.services.inventory_service import (
    DuplicateSKUError,
    InsufficientStockError,
    InventoryServiceError,
    ItemHasStockError,
    inventory_service,
)

# ---------------------------------------------------------------------------
# Real dependencies from centralized deps module
# ---------------------------------------------------------------------------
from app.api.deps import DBDep, CurrentUser
from app.api.v1.endpoints.roles import require_roles

# ---------------------------------------------------------------------------
router = APIRouter()


# ===========================================================================
# CATEGORIES
# ===========================================================================
@router.post(
    "/categories",
    response_model=InventoryCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: InventoryCategoryCreate,
    db: DBDep,
    current_user: CurrentUser,
    _: CurrentUser = Depends(require_roles(["admin", "manager"])),
) -> InventoryCategoryResponse:
    existing = await category_crud.get_by_code(db, data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category code '{data.code}' already exists",
        )
    obj = await category_crud.create(db, data, user_id=current_user.id)
    await db.commit()
    return InventoryCategoryResponse.model_validate(obj)


@router.get("/categories", response_model=list[InventoryCategoryResponse])
async def list_categories(
    db: DBDep,
    current_user: CurrentUser,
    parent_id: Optional[int] = None,
    is_active: Optional[bool] = True,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[InventoryCategoryResponse]:
    _, rows = await category_crud.list(
        db, parent_id=parent_id, is_active=is_active, offset=offset, limit=limit
    )
    return [InventoryCategoryResponse.model_validate(r) for r in rows]


# ===========================================================================
# SUPPLIERS
# ===========================================================================
@router.post(
    "/suppliers",
    response_model=SupplierResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_supplier(
    data: SupplierCreate,
    db: DBDep,
    current_user: CurrentUser,
    _: CurrentUser = Depends(require_roles(["admin", "manager"])),
) -> SupplierResponse:
    existing = await supplier_crud.get_by_code(db, data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Supplier code '{data.code}' already exists",
        )
    obj = await supplier_crud.create(db, data, user_id=current_user.id)
    await db.commit()
    return SupplierResponse.model_validate(obj)


@router.get("/suppliers", response_model=list[SupplierResponse])
async def list_suppliers(
    db: DBDep,
    current_user: CurrentUser,
    search: Optional[str] = None,
    is_active: Optional[bool] = True,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[SupplierResponse]:
    _, rows = await supplier_crud.list(
        db, is_active=is_active, search=search, offset=offset, limit=limit
    )
    return [SupplierResponse.model_validate(r) for r in rows]


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> SupplierResponse:
    obj = await supplier_crud.get(db, supplier_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Supplier not found")
    obj = await supplier_crud.update(db, obj, data, user_id=current_user.id)
    await db.commit()
    return SupplierResponse.model_validate(obj)


# ===========================================================================
# LOCATIONS
# ===========================================================================
@router.post(
    "/locations",
    response_model=InventoryLocationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_location(
    data: InventoryLocationCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> InventoryLocationResponse:
    # TODO: require_role(current_user, ["admin", "manager"])
    existing = await location_crud.get_by_code(db, data.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Location code '{data.code}' already exists",
        )
    obj = await location_crud.create(db, data, user_id=current_user.id)
    await db.commit()
    return InventoryLocationResponse.model_validate(obj)


@router.get("/locations", response_model=list[InventoryLocationResponse])
async def list_locations(
    db: DBDep,
    current_user: CurrentUser,
    warehouse: Optional[str] = None,
    is_active: Optional[bool] = True,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[InventoryLocationResponse]:
    _, rows = await location_crud.list(
        db, warehouse=warehouse, is_active=is_active, offset=offset, limit=limit
    )
    return [InventoryLocationResponse.model_validate(r) for r in rows]


@router.put("/locations/{location_id}", response_model=InventoryLocationResponse)
async def update_location(
    location_id: int,
    data: InventoryLocationUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> InventoryLocationResponse:
    obj = await location_crud.get(db, location_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Location not found")
    obj = await location_crud.update(db, obj, data, user_id=current_user.id)
    await db.commit()
    return InventoryLocationResponse.model_validate(obj)


# ===========================================================================
# ITEMS
# ===========================================================================
@router.post(
    "/items",
    response_model=InventoryItemResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_item(
    data: InventoryItemCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> InventoryItemResponse:
    # TODO: require_role(current_user, ["admin", "manager"])
    try:
        item = await inventory_service.create_item(db, data, user_id=current_user.id)
    except DuplicateSKUError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    await db.commit()
    await db.refresh(item)
    return InventoryItemResponse.model_validate(item)


@router.get("/items", response_model=list[InventoryItemResponse])
async def list_items(
    db: DBDep,
    current_user: CurrentUser,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    low_stock: bool = False,
    is_active: Optional[bool] = True,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[InventoryItemResponse]:
    _, rows = await item_crud.list(
        db,
        category_id=category_id,
        search=search,
        low_stock=low_stock,
        is_active=is_active,
        offset=offset,
        limit=limit,
    )
    return [InventoryItemResponse.model_validate(r) for r in rows]


@router.get("/items/{item_id}", response_model=InventoryItemDetailResponse)
async def get_item(
    item_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> InventoryItemDetailResponse:
    item = await item_crud.get(db, item_id, with_stock=True)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return InventoryItemDetailResponse.model_validate(item)


@router.put("/items/{item_id}", response_model=InventoryItemResponse)
async def update_item(
    item_id: int,
    data: InventoryItemUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> InventoryItemResponse:
    # TODO: require_role(current_user, ["admin", "manager"])
    item = await item_crud.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    item = await item_crud.update(db, item, data, user_id=current_user.id)
    await db.commit()
    return InventoryItemResponse.model_validate(item)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> None:
    # TODO: require_role(current_user, ["admin"])
    item = await item_crud.get(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    try:
        await inventory_service.assert_can_delete_item(db, item_id)
    except ItemHasStockError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    await item_crud.soft_delete(db, item, user_id=current_user.id)
    await db.commit()


# ===========================================================================
# STOCK LEVELS
# ===========================================================================
@router.get("/stock", response_model=list[StockLevelResponse])
async def get_stock_levels(
    db: DBDep,
    current_user: CurrentUser,
    item_id: Optional[int] = None,
    location_id: Optional[int] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[StockLevelResponse]:
    _, rows = await stock_crud.list(
        db, item_id=item_id, location_id=location_id, offset=offset, limit=limit
    )
    return [StockLevelResponse.model_validate(r) for r in rows]


@router.post("/stock/adjust", response_model=InventoryMovementResponse)
async def adjust_stock(
    data: StockAdjustRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> InventoryMovementResponse:
    # TODO: require_role(current_user, ["admin", "manager"])
    try:
        movement = await inventory_service.adjust_stock(db, data, user_id=current_user.id)
    except (InventoryServiceError, InsufficientStockError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    await db.commit()
    return InventoryMovementResponse.model_validate(movement)


@router.post("/stock/transfer", response_model=list[InventoryMovementResponse])
async def transfer_stock(
    data: StockTransferRequest,
    db: DBDep,
    current_user: CurrentUser,
) -> list[InventoryMovementResponse]:
    # TODO: require_role(current_user, ["admin", "manager", "warehouse"])
    try:
        out_mv, in_mv = await inventory_service.transfer_stock(
            db, data, user_id=current_user.id
        )
    except (InventoryServiceError, InsufficientStockError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    await db.commit()
    return [
        InventoryMovementResponse.model_validate(out_mv),
        InventoryMovementResponse.model_validate(in_mv),
    ]


# ===========================================================================
# MOVEMENTS
# ===========================================================================
@router.get("/movements", response_model=list[InventoryMovementResponse])
async def list_movements(
    db: DBDep,
    current_user: CurrentUser,
    item_id: Optional[int] = None,
    location_id: Optional[int] = None,
    movement_type: Optional[MovementType] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[InventoryMovementResponse]:
    _, rows = await movement_crud.list(
        db,
        item_id=item_id,
        location_id=location_id,
        movement_type=movement_type,
        date_from=date_from,
        date_to=date_to,
        offset=offset,
        limit=limit,
    )
    return [InventoryMovementResponse.model_validate(r) for r in rows]


@router.post(
    "/movements/inbound",
    response_model=InventoryMovementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def receive_goods(
    data: InboundMovementCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> InventoryMovementResponse:
    # TODO: require_role(current_user, ["admin", "manager", "warehouse"])
    try:
        movement = await inventory_service.process_inbound(db, data, user_id=current_user.id)
    except InventoryServiceError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    await db.commit()
    return InventoryMovementResponse.model_validate(movement)


@router.post(
    "/movements/outbound",
    response_model=InventoryMovementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def issue_goods(
    data: OutboundMovementCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> InventoryMovementResponse:
    # TODO: require_role(current_user, ["admin", "manager", "warehouse"])
    try:
        movement = await inventory_service.process_outbound(db, data, user_id=current_user.id)
    except InsufficientStockError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except InventoryServiceError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    await db.commit()
    return InventoryMovementResponse.model_validate(movement)


# ===========================================================================
# AUDIT
# ===========================================================================
@router.post(
    "/audits",
    response_model=InventoryAuditResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_audit(
    data: InventoryAuditCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> InventoryAuditResponse:
    # TODO: require_role(current_user, ["admin", "manager"])
    audit = await inventory_service.create_audit(db, data, user_id=current_user.id)
    await db.commit()
    await db.refresh(audit)
    return InventoryAuditResponse.model_validate(audit)


@router.get("/audits", response_model=list[InventoryAuditResponse])
async def list_audits(
    db: DBDep,
    current_user: CurrentUser,
    location_id: Optional[int] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[InventoryAuditResponse]:
    _, rows = await audit_crud.list(
        db, location_id=location_id, offset=offset, limit=limit
    )
    return [InventoryAuditResponse.model_validate(r) for r in rows]


@router.post("/audits/{audit_id}/count", response_model=InventoryAuditResponse)
async def submit_count(
    audit_id: int,
    lines: list[InventoryAuditLineCreate],
    db: DBDep,
    current_user: CurrentUser,
) -> InventoryAuditResponse:
    # TODO: require_role(current_user, ["admin", "manager", "warehouse"])
    try:
        audit = await inventory_service.submit_audit_count(
            db, audit_id, lines, user_id=current_user.id
        )
    except InventoryServiceError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    await db.commit()
    return InventoryAuditResponse.model_validate(audit)


@router.post("/audits/{audit_id}/approve", response_model=InventoryAuditResponse)
async def approve_audit(
    audit_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> InventoryAuditResponse:
    # TODO: require_role(current_user, ["admin"])
    try:
        audit = await inventory_service.approve_and_reconcile_audit(
            db, audit_id, approver_id=current_user.id
        )
    except InventoryServiceError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    await db.commit()
    return InventoryAuditResponse.model_validate(audit)


# ===========================================================================
# REPORTS
# ===========================================================================
@router.get("/reports/low-stock", response_model=list[LowStockReportItem])
async def low_stock_report(
    db: DBDep,
    current_user: CurrentUser,
    location_id: Optional[int] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[LowStockReportItem]:
    """Items where quantity_on_hand <= effective reorder point."""
    from sqlalchemy.orm import aliased

    sl = aliased(StockLevel)
    item = aliased(InventoryItem)
    from app.models.inventory import InventoryLocation

    loc = aliased(InventoryLocation)

    q = (
        select(
            item.id.label("item_id"),
            item.sku,
            item.name.label("item_name"),
            loc.id.label("location_id"),
            loc.code.label("location_code"),
            sl.quantity_on_hand,
            (sl.quantity_on_hand - sl.quantity_reserved).label("quantity_available"),
            func.coalesce(sl.reorder_point, item.global_reorder_point).label("reorder_point"),
        )
        .join(sl, sl.item_id == item.id)
        .join(loc, loc.id == sl.location_id)
        .where(
            sl.quantity_on_hand
            <= func.coalesce(sl.reorder_point, item.global_reorder_point)
        )
        .where(item.is_active.is_(True))
    )
    if location_id:
        q = q.where(sl.location_id == location_id)

    rows = (await db.execute(q.offset(offset).limit(limit))).all()
    return [
        LowStockReportItem(
            item_id=r.item_id,
            sku=r.sku,
            item_name=r.item_name,
            location_id=r.location_id,
            location_code=r.location_code,
            quantity_on_hand=r.quantity_on_hand,
            quantity_available=r.quantity_available,
            reorder_point=r.reorder_point,
            shortage=r.reorder_point - r.quantity_available,
        )
        for r in rows
    ]


@router.get("/reports/movement-summary", response_model=list[MovementSummaryItem])
async def movement_summary_report(
    db: DBDep,
    current_user: CurrentUser,
    date_from: datetime = Query(..., description="Start of period (ISO 8601)"),
    date_to: datetime = Query(..., description="End of period (ISO 8601)"),
    item_id: Optional[int] = None,
) -> list[MovementSummaryItem]:
    """Aggregate movements by type and item for the given period."""
    from app.models.inventory import InventoryMovement as MV

    q = (
        select(
            MV.movement_type,
            MV.item_id,
            InventoryItem.sku,
            InventoryItem.name.label("item_name"),
            func.sum(MV.quantity).label("total_quantity"),
            func.count(MV.id).label("movement_count"),
        )
        .join(InventoryItem, InventoryItem.id == MV.item_id)
        .where(
            and_(
                MV.movement_date >= date_from,
                MV.movement_date <= date_to,
            )
        )
        .group_by(MV.movement_type, MV.item_id, InventoryItem.sku, InventoryItem.name)
    )
    if item_id:
        q = q.where(MV.item_id == item_id)

    rows = (await db.execute(q)).all()
    return [
        MovementSummaryItem(
            movement_type=r.movement_type,
            item_id=r.item_id,
            sku=r.sku,
            item_name=r.item_name,
            total_quantity=r.total_quantity,
            movement_count=r.movement_count,
            period_start=date_from,
            period_end=date_to,
        )
        for r in rows
    ]
