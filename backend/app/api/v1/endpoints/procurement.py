"""
Procurement Module — FastAPI Router
TOP WorX ERP System

INTEGRATION POINT: Register in api.py:
    from app.api.api_v1.endpoints.procurement import router as procurement_router
    api_router.include_router(procurement_router, prefix="/procurement", tags=["procurement"])
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from sqlalchemy.orm import selectinload

from app.models.procurement import (
    ApprovalRule, GoodsReceipt, POStatus, PRStatus, PurchaseOrder,
    PurchaseRequest, Vendor, VendorInvoice, VendorInvoiceStatus, PaymentToVendor,
)
from app.schemas.procurement import (
    ApprovalRuleCreate, ApprovalRuleResponse,
    DeliveryPerformanceRow, PendingApprovalRow, POCreate, POResponse,
    PRApprove, PRCreate, PRReject, PRResponse, ReceiptCreate, ReceiptResponse,
    SpendByVendorRow, VendorCreate, VendorInvoiceCreate, VendorInvoiceResponse,
    VendorPaymentCreate, VendorPaymentResponse, VendorResponse,
    VendorUpdate, ThreeWayMatchResult,
)
from app.services.procurement_service import (
    ProcurementError, approval_service, get_vendor, po_service, pr_service,
    receipt_service, three_way_match, vendor_payment_service,
    update_vendor_ap_balance,
)

# ---------------------------------------------------------------------------
# Real dependencies from centralized deps module
# ---------------------------------------------------------------------------
from app.api.deps import DBDep, CurrentUser as CU

router = APIRouter()


def _err(exc: ProcurementError) -> HTTPException:
    return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


# ===========================================================================
# VENDORS
# ===========================================================================
@router.post("/vendors", response_model=VendorResponse, status_code=201)
async def create_vendor(data: VendorCreate, db: DBDep, cu: CU) -> VendorResponse:
    # TODO: require_role(cu, ["admin", "procurement_manager"])
    existing = await db.execute(select(Vendor).where(Vendor.code == data.code))
    if existing.scalar_one_or_none():
        raise HTTPException(409, f"Vendor code '{data.code}' already exists")
    obj = Vendor(**data.model_dump(), created_by_id=cu.id, updated_by_id=cu.id)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return VendorResponse.model_validate(obj)


@router.get("/vendors", response_model=list[VendorResponse])
async def list_vendors(
    db: DBDep, cu: CU,
    is_active: Optional[bool] = True,
    is_approved: Optional[bool] = None,
    search: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[VendorResponse]:
    q = select(Vendor).order_by(Vendor.name)
    if is_active is not None:
        q = q.where(Vendor.is_active == is_active)
    if is_approved is not None:
        q = q.where(Vendor.is_approved == is_approved)
    if search:
        term = f"%{search}%"
        from sqlalchemy import or_
        q = q.where(or_(Vendor.name.ilike(term), Vendor.code.ilike(term)))
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [VendorResponse.model_validate(r) for r in rows]


@router.get("/vendors/{vendor_id}", response_model=VendorResponse)
async def get_vendor_endpoint(vendor_id: int, db: DBDep, cu: CU) -> VendorResponse:
    obj = await get_vendor(db, vendor_id)
    if not obj:
        raise HTTPException(404, "Vendor not found")
    return VendorResponse.model_validate(obj)


@router.put("/vendors/{vendor_id}", response_model=VendorResponse)
async def update_vendor(vendor_id: int, data: VendorUpdate, db: DBDep, cu: CU) -> VendorResponse:
    obj = await get_vendor(db, vendor_id)
    if not obj:
        raise HTTPException(404, "Vendor not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    obj.updated_by_id = cu.id
    await db.commit()
    return VendorResponse.model_validate(obj)


@router.get("/vendors/{vendor_id}/statement")
async def vendor_statement(
    vendor_id: int, db: DBDep, cu: CU,
    as_of_date: Optional[date] = None,
) -> dict:
    """AP statement: vendor invoices + payments in date order."""
    vendor = await get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(404, "Vendor not found")
    aod = as_of_date or date.today()

    inv_r = await db.execute(
        select(VendorInvoice)
        .where(VendorInvoice.vendor_id == vendor_id, VendorInvoice.invoice_date <= aod)
        .order_by(VendorInvoice.invoice_date)
    )
    invoices = inv_r.scalars().all()

    pay_r = await db.execute(
        select(PaymentToVendor)
        .where(PaymentToVendor.vendor_id == vendor_id, PaymentToVendor.payment_date <= aod)
        .order_by(PaymentToVendor.payment_date)
    )
    payments = pay_r.scalars().all()

    lines = []
    running = 0
    for inv in invoices:
        running += float(inv.total_amount)
        lines.append({"date": str(inv.invoice_date), "type": "invoice",
                      "reference": inv.invoice_number, "debit": float(inv.total_amount),
                      "credit": 0, "balance": running})
    for pay in payments:
        running -= float(pay.amount)
        lines.append({"date": str(pay.payment_date), "type": "payment",
                      "reference": pay.payment_number, "debit": 0,
                      "credit": float(pay.amount), "balance": running})

    lines.sort(key=lambda x: x["date"])
    return {"vendor_id": vendor_id, "vendor_name": vendor.name,
            "as_of_date": str(aod), "lines": lines, "balance_due": float(vendor.balance_due)}


# ===========================================================================
# APPROVAL RULES
# ===========================================================================
@router.post("/approval-rules", response_model=ApprovalRuleResponse, status_code=201)
async def create_approval_rule(data: ApprovalRuleCreate, db: DBDep, cu: CU) -> ApprovalRuleResponse:
    # TODO: require_role(cu, ["admin"])
    obj = ApprovalRule(**data.model_dump(), is_active=True, created_by_id=cu.id, updated_by_id=cu.id)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return ApprovalRuleResponse.model_validate(obj)


@router.get("/approval-rules", response_model=list[ApprovalRuleResponse])
async def list_approval_rules(db: DBDep, cu: CU) -> list[ApprovalRuleResponse]:
    rows = (await db.execute(select(ApprovalRule).order_by(ApprovalRule.sort_order))).scalars().all()
    return [ApprovalRuleResponse.model_validate(r) for r in rows]


# ===========================================================================
# PURCHASE REQUESTS
# ===========================================================================
@router.post("/requests", response_model=PRResponse, status_code=201)
async def create_pr(data: PRCreate, db: DBDep, cu: CU) -> PRResponse:
    obj = await pr_service.create(db, data, requester_id=cu.id)
    await db.commit()
    await db.refresh(obj)
    return PRResponse.model_validate(obj)


@router.get("/requests", response_model=list[PRResponse])
async def list_prs(
    db: DBDep, cu: CU,
    status: Optional[PRStatus] = None,
    department: Optional[str] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[PRResponse]:
    q = select(PurchaseRequest).options(selectinload(PurchaseRequest.lines)).order_by(PurchaseRequest.id.desc())
    if status:
        q = q.where(PurchaseRequest.status == status)
    if department:
        q = q.where(PurchaseRequest.department == department)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [PRResponse.model_validate(r) for r in rows]


@router.post("/requests/{pr_id}/submit", response_model=PRResponse)
async def submit_pr(pr_id: int, db: DBDep, cu: CU) -> PRResponse:
    pr = await db.get(PurchaseRequest, pr_id)
    if not pr:
        raise HTTPException(404, "Purchase request not found")
    try:
        pr = await approval_service.submit_pr(db, pr, user_id=cu.id)
    except ProcurementError as exc:
        raise _err(exc)
    await db.commit()
    return PRResponse.model_validate(pr)


@router.post("/requests/{pr_id}/approve", response_model=PRResponse)
async def approve_pr(pr_id: int, data: PRApprove, db: DBDep, cu: CU) -> PRResponse:
    # TODO: require_role(cu, ["manager", "director", "cfo", "admin"])
    pr = await db.get(PurchaseRequest, pr_id)
    if not pr:
        raise HTTPException(404, "Purchase request not found")
    try:
        pr = await approval_service.approve_pr(db, pr, approver_id=cu.id, notes=data.notes)
    except ProcurementError as exc:
        raise _err(exc)
    await db.commit()
    return PRResponse.model_validate(pr)


@router.post("/requests/{pr_id}/reject", response_model=PRResponse)
async def reject_pr(pr_id: int, data: PRReject, db: DBDep, cu: CU) -> PRResponse:
    pr = await db.get(PurchaseRequest, pr_id)
    if not pr:
        raise HTTPException(404, "Purchase request not found")
    try:
        pr = await approval_service.reject_pr(db, pr, approver_id=cu.id, reason=data.reason)
    except ProcurementError as exc:
        raise _err(exc)
    await db.commit()
    return PRResponse.model_validate(pr)


@router.post("/requests/{pr_id}/convert", response_model=POResponse, status_code=201)
async def convert_pr_to_po(
    pr_id: int, db: DBDep, cu: CU,
    vendor_id: int = Query(...),
    expected_delivery: Optional[date] = None,
) -> POResponse:
    pr = await db.execute(
        select(PurchaseRequest).options(selectinload(PurchaseRequest.lines)).where(PurchaseRequest.id == pr_id)
    )
    pr = pr.scalar_one_or_none()
    if not pr:
        raise HTTPException(404, "Purchase request not found")
    try:
        po = await pr_service.convert_to_po(db, pr, vendor_id=vendor_id, user_id=cu.id, expected_delivery=expected_delivery)
    except ProcurementError as exc:
        raise _err(exc)
    await db.commit()
    await db.refresh(po)
    return POResponse.model_validate(po)


# ===========================================================================
# PURCHASE ORDERS
# ===========================================================================
@router.post("/orders", response_model=POResponse, status_code=201)
async def create_po(data: POCreate, db: DBDep, cu: CU) -> POResponse:
    try:
        obj = await po_service.create_po(db, data, user_id=cu.id)
    except ProcurementError as exc:
        raise _err(exc)
    await db.commit()
    await db.refresh(obj)
    return POResponse.model_validate(obj)


@router.get("/orders", response_model=list[POResponse])
async def list_pos(
    db: DBDep, cu: CU,
    vendor_id: Optional[int] = None,
    status: Optional[POStatus] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[POResponse]:
    q = select(PurchaseOrder).options(selectinload(PurchaseOrder.lines)).order_by(PurchaseOrder.id.desc())
    if vendor_id:
        q = q.where(PurchaseOrder.vendor_id == vendor_id)
    if status:
        q = q.where(PurchaseOrder.status == status)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [POResponse.model_validate(r) for r in rows]


@router.get("/orders/{po_id}", response_model=POResponse)
async def get_po(po_id: int, db: DBDep, cu: CU) -> POResponse:
    r = await db.execute(
        select(PurchaseOrder).options(selectinload(PurchaseOrder.lines)).where(PurchaseOrder.id == po_id)
    )
    obj = r.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Purchase order not found")
    return POResponse.model_validate(obj)


@router.post("/orders/{po_id}/send", response_model=POResponse)
async def send_po(po_id: int, db: DBDep, cu: CU) -> POResponse:
    r = await db.execute(select(PurchaseOrder).where(PurchaseOrder.id == po_id))
    obj = r.scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Purchase order not found")
    try:
        obj = await po_service.send_po(db, obj, user_id=cu.id)
    except ProcurementError as exc:
        raise _err(exc)
    await db.commit()
    return POResponse.model_validate(obj)


@router.post("/orders/{po_id}/receive", response_model=ReceiptResponse, status_code=201)
async def receive_goods(data: ReceiptCreate, db: DBDep, cu: CU) -> ReceiptResponse:
    # Ensure po_id from path matches body
    try:
        receipt = await receipt_service.receive_goods(db, data, user_id=cu.id)
    except ProcurementError as exc:
        raise _err(exc)
    await db.commit()
    await db.refresh(receipt)
    return ReceiptResponse.model_validate(receipt)


# ===========================================================================
# VENDOR INVOICES
# ===========================================================================
@router.post("/invoices", response_model=VendorInvoiceResponse, status_code=201)
async def record_vendor_invoice(data: VendorInvoiceCreate, db: DBDep, cu: CU) -> VendorInvoiceResponse:
    from decimal import Decimal
    obj = VendorInvoice(
        invoice_number=data.invoice_number,
        po_id=data.po_id,
        vendor_id=data.vendor_id,
        invoice_date=data.invoice_date,
        due_date=data.due_date,
        received_date=data.received_date or date.today(),
        amount=data.amount,
        tax_amount=data.tax_amount,
        total_amount=data.amount + data.tax_amount,
        amount_due=data.amount + data.tax_amount,
        notes=data.notes,
        created_by_id=cu.id,
        updated_by_id=cu.id,
    )
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return VendorInvoiceResponse.model_validate(obj)


@router.get("/invoices", response_model=list[VendorInvoiceResponse])
async def list_vendor_invoices(
    db: DBDep, cu: CU,
    vendor_id: Optional[int] = None,
    status: Optional[VendorInvoiceStatus] = None,
    pending_only: bool = False,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[VendorInvoiceResponse]:
    q = select(VendorInvoice).order_by(VendorInvoice.due_date)
    if vendor_id:
        q = q.where(VendorInvoice.vendor_id == vendor_id)
    if status:
        q = q.where(VendorInvoice.status == status)
    if pending_only:
        q = q.where(VendorInvoice.status == VendorInvoiceStatus.PENDING_VERIFICATION)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [VendorInvoiceResponse.model_validate(r) for r in rows]


@router.post("/invoices/{invoice_id}/verify", response_model=ThreeWayMatchResult)
async def verify_vendor_invoice(invoice_id: int, db: DBDep, cu: CU) -> ThreeWayMatchResult:
    """Run 3-way match: PO ↔ Goods Receipt ↔ Vendor Invoice."""
    # TODO: require_role(cu, ["admin", "finance_manager", "procurement_manager"])
    r = await db.execute(select(VendorInvoice).where(VendorInvoice.id == invoice_id))
    inv = r.scalar_one_or_none()
    if not inv:
        raise HTTPException(404, "Vendor invoice not found")
    try:
        result = await three_way_match.perform_match(db, inv, user_id=cu.id)
    except ProcurementError as exc:
        raise _err(exc)
    await db.commit()
    return result


# ===========================================================================
# PAYMENTS TO VENDORS
# ===========================================================================
@router.post("/payments", response_model=VendorPaymentResponse, status_code=201)
async def pay_vendor(data: VendorPaymentCreate, db: DBDep, cu: CU) -> VendorPaymentResponse:
    # TODO: require_role(cu, ["admin", "finance_manager"])
    try:
        payment = await vendor_payment_service.process_payment(db, data, user_id=cu.id)
    except ProcurementError as exc:
        raise _err(exc)
    await db.commit()
    return VendorPaymentResponse.model_validate(payment)


@router.get("/payments", response_model=list[VendorPaymentResponse])
async def list_vendor_payments(
    db: DBDep, cu: CU,
    vendor_id: Optional[int] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[VendorPaymentResponse]:
    q = select(PaymentToVendor).order_by(PaymentToVendor.payment_date.desc())
    if vendor_id:
        q = q.where(PaymentToVendor.vendor_id == vendor_id)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [VendorPaymentResponse.model_validate(r) for r in rows]


# ===========================================================================
# REPORTS
# ===========================================================================
@router.get("/reports/spend-by-vendor", response_model=list[SpendByVendorRow])
async def spend_by_vendor(db: DBDep, cu: CU) -> list[SpendByVendorRow]:
    from decimal import Decimal
    rows = (await db.execute(
        select(
            Vendor.id, Vendor.code, Vendor.name,
            func.count(PurchaseOrder.id).label("po_count"),
            func.coalesce(func.sum(PurchaseOrder.total_amount), Decimal("0")).label("ordered"),
            Vendor.total_purchased, Vendor.total_paid, Vendor.balance_due,
        )
        .join(PurchaseOrder, PurchaseOrder.vendor_id == Vendor.id, isouter=True)
        .group_by(Vendor.id, Vendor.code, Vendor.name, Vendor.total_purchased, Vendor.total_paid, Vendor.balance_due)
        .order_by(func.sum(PurchaseOrder.total_amount).desc())
    )).all()
    return [
        SpendByVendorRow(
            vendor_id=r.id, vendor_code=r.code, vendor_name=r.name,
            po_count=r.po_count,
            total_ordered=Decimal(str(r.ordered)),
            total_received=Decimal(str(r.total_purchased)),
            total_paid=Decimal(str(r.total_paid)),
            balance_due=Decimal(str(r.balance_due)),
        )
        for r in rows
    ]


@router.get("/reports/pending-approvals", response_model=list[PendingApprovalRow])
async def pending_approvals(db: DBDep, cu: CU) -> list[PendingApprovalRow]:
    from datetime import datetime
    rows = (await db.execute(
        select(PurchaseRequest).where(PurchaseRequest.status == PRStatus.PENDING_APPROVAL)
        .order_by(PurchaseRequest.created_at.asc())
    )).scalars().all()

    today = datetime.utcnow()
    result = []
    for pr in rows:
        days = (today - pr.created_at.replace(tzinfo=None)).days if pr.created_at else 0
        result.append(PendingApprovalRow(
            request_id=pr.id, request_number=pr.request_number,
            requester_name=f"User {pr.requester_id}",
            department=pr.department, priority=pr.priority,
            total_estimated=pr.total_estimated,
            submitted_at=pr.updated_at,
            required_approver_role="manager",  # TODO: lookup from approval rule
            days_pending=days,
        ))
    return result


@router.get("/reports/ap-aging")
async def ap_aging(
    db: DBDep, cu: CU,
    as_of_date: date = Query(default=date.today()),
) -> dict:
    """AP aging from Finance module reporting service."""
    from app.services.reporting_service import reporting_service
    result = await reporting_service.aging_report(db, as_of_date, "vendor")
    return result.model_dump()


@router.get("/reports/delivery-performance", response_model=list[DeliveryPerformanceRow])
async def delivery_performance(db: DBDep, cu: CU) -> list[DeliveryPerformanceRow]:
    """On-time delivery rate per vendor."""
    from sqlalchemy import case
    rows = (await db.execute(
        select(
            Vendor.id, Vendor.name,
            func.count(PurchaseOrder.id).label("total"),
            func.sum(
                case(
                    (PurchaseOrder.actual_delivery <= PurchaseOrder.expected_delivery, 1),
                    else_=0,
                )
            ).label("on_time"),
        )
        .join(PurchaseOrder, PurchaseOrder.vendor_id == Vendor.id)
        .where(PurchaseOrder.actual_delivery.isnot(None))
        .group_by(Vendor.id, Vendor.name)
    )).all()

    return [
        DeliveryPerformanceRow(
            vendor_id=r.id, vendor_name=r.name,
            total_orders=r.total,
            on_time_deliveries=r.on_time or 0,
            late_deliveries=(r.total - (r.on_time or 0)),
            on_time_rate=round((r.on_time or 0) / r.total * 100, 1) if r.total else 0.0,
            avg_delay_days=0.0,  # TODO: compute avg(actual - expected) for late
        )
        for r in rows
    ]
