# app/api/v1/endpoints/sales.py
"""
Sales Module — FastAPI Router
TOP WorX ERP System

INTEGRATION POINT: Register in api.py:
    from app.api.v1.endpoints.sales import router as sales_router
    api_router.include_router(sales_router, prefix="/sales", tags=["Sales"])
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Response, status

from app.api.deps import DBDep, CurrentUser
from app.crud.sales import customer_crud, invoice_crud, payment_crud, quote_crud
from app.models.sales import (
    CustomerCategory,
    InvoiceStatus,
    PaymentStatus,
    QuoteStatus,
)
from app.schemas.sales import (
    CustomerCreate,
    CustomerResponse,
    CustomerStatement,
    CustomerUpdate,
    InvoiceCreate,
    InvoiceListItem,
    InvoiceResponse,
    PaymentAllocate,
    PaymentCreate,
    PaymentResponse,
    ProductMarginRow,
    QuoteCreate,
    QuoteResponse,
    RevenueByPeriodRow,
    TaxExportLine,
    TopCustomerRow,
)
from app.services.sales_service import (
    CustomerService,
    InvoiceService,
    PaymentService,
    QuoteService,
    ReportService,
    SalesError,
)

router = APIRouter(prefix="/sales", tags=["Sales"])


def _sales_error(exc: SalesError) -> HTTPException:
    return HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


# ===========================================================================
# CUSTOMERS
# ===========================================================================

@router.post(
    "/customers",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new customer",
)
async def create_customer(
    data: CustomerCreate,
    db: DBDep,
    cu: CurrentUser,
) -> CustomerResponse:
    # TODO: require_role(cu, ["admin", "sales_manager"])
    try:
        obj = await CustomerService.create(db, data, cu.id)
    except SalesError as exc:
        raise _sales_error(exc)
    await db.commit()
    await db.refresh(obj)
    return CustomerResponse.model_validate(obj)


@router.get(
    "/customers",
    response_model=list[CustomerResponse],
    summary="List customers",
)
async def list_customers(
    db: DBDep,
    cu: CurrentUser,
    search: Optional[str] = None,
    category: Optional[CustomerCategory] = None,
    is_active: Optional[bool] = True,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[CustomerResponse]:
    _, rows = await customer_crud.list(
        db,
        is_active=is_active,
        category=category,
        search=search,
        offset=offset,
        limit=limit,
    )
    return [CustomerResponse.model_validate(r) for r in rows]


@router.get(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
    summary="Get customer by ID",
)
async def get_customer(
    customer_id: int,
    db: DBDep,
    cu: CurrentUser,
) -> CustomerResponse:
    obj = await CustomerService.get_or_404(db, customer_id)
    return CustomerResponse.model_validate(obj)


@router.patch(
    "/customers/{customer_id}",
    response_model=CustomerResponse,
    summary="Update customer",
)
async def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: DBDep,
    cu: CurrentUser,
) -> CustomerResponse:
    try:
        obj = await CustomerService.update(db, customer_id, data, cu.id)
    except SalesError as exc:
        raise _sales_error(exc)
    await db.commit()
    await db.refresh(obj)
    return CustomerResponse.model_validate(obj)


@router.delete(
    "/customers/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deactivate customer (soft delete)",
)
async def deactivate_customer(
    customer_id: int,
    db: DBDep,
    cu: CurrentUser,
) -> None:
    try:
        await CustomerService.deactivate(db, customer_id)
    except SalesError as exc:
        raise _sales_error(exc)
    await db.commit()


@router.get(
    "/customers/{customer_id}/statement",
    response_model=CustomerStatement,
    summary="Customer account statement",
)
async def customer_statement(
    customer_id: int,
    db: DBDep,
    cu: CurrentUser,
    as_of_date: date = Query(default_factory=date.today),
) -> CustomerStatement:
    try:
        return await CustomerService.get_statement(db, customer_id, as_of_date)
    except (SalesError, ValueError) as exc:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=str(exc))


# ===========================================================================
# QUOTES
# ===========================================================================

@router.post(
    "/quotes",
    response_model=QuoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create sales quote",
)
async def create_quote(
    data: QuoteCreate,
    db: DBDep,
    cu: CurrentUser,
) -> QuoteResponse:
    try:
        obj = await QuoteService.create(db, data, cu.id)
    except SalesError as exc:
        raise _sales_error(exc)
    await db.commit()
    await db.refresh(obj)
    return QuoteResponse.model_validate(obj)


@router.get(
    "/quotes",
    response_model=list[QuoteResponse],
    summary="List quotes",
)
async def list_quotes(
    db: DBDep,
    cu: CurrentUser,
    customer_id: Optional[int] = None,
    quote_status: Optional[QuoteStatus] = Query(None, alias="status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[QuoteResponse]:
    _, rows = await quote_crud.list(
        db,
        customer_id=customer_id,
        status=quote_status,
        offset=offset,
        limit=limit,
    )
    return [QuoteResponse.model_validate(r) for r in rows]


@router.get(
    "/quotes/{quote_id}",
    response_model=QuoteResponse,
    summary="Get quote by ID",
)
async def get_quote(
    quote_id: int,
    db: DBDep,
    cu: CurrentUser,
) -> QuoteResponse:
    obj = await quote_crud.get(db, quote_id, with_lines=True)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Quote not found")
    return QuoteResponse.model_validate(obj)


@router.post(
    "/quotes/{quote_id}/send",
    response_model=QuoteResponse,
    summary="Mark quote as SENT",
)
async def send_quote(
    quote_id: int,
    db: DBDep,
    cu: CurrentUser,
) -> QuoteResponse:
    try:
        obj = await QuoteService.send(db, quote_id, user_id=cu.id)
    except SalesError as exc:
        raise _sales_error(exc)
    await db.commit()
    return QuoteResponse.model_validate(obj)


@router.post(
    "/quotes/{quote_id}/convert",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Convert quote to invoice",
)
async def convert_quote(
    quote_id: int,
    db: DBDep,
    cu: CurrentUser,
) -> InvoiceResponse:
    try:
        invoice = await QuoteService.convert_to_invoice(db, quote_id, cu.id)
    except SalesError as exc:
        raise _sales_error(exc)
    await db.commit()
    await db.refresh(invoice)
    return InvoiceResponse.model_validate(invoice)


# ===========================================================================
# INVOICES
# ===========================================================================

@router.post(
    "/invoices",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create sales invoice (DRAFT)",
)
async def create_invoice(
    data: InvoiceCreate,
    db: DBDep,
    cu: CurrentUser,
) -> InvoiceResponse:
    try:
        obj = await InvoiceService.create(db, data, cu.id)
    except SalesError as exc:
        raise _sales_error(exc)
    await db.commit()
    await db.refresh(obj)
    return InvoiceResponse.model_validate(obj)


@router.get(
    "/invoices",
    response_model=list[InvoiceListItem],
    summary="List all invoices",
)
async def list_invoices(
    db: DBDep,
    cu: CurrentUser,
    customer_id: Optional[int] = None,
    invoice_status: Optional[InvoiceStatus] = Query(None, alias="status"),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    overdue_only: bool = False,
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[InvoiceListItem]:
    _, rows = await invoice_crud.list(
        db,
        customer_id=customer_id,
        status=invoice_status,
        date_from=date_from,
        date_to=date_to,
        overdue_only=overdue_only,
        offset=offset,
        limit=limit,
    )
    today = date.today()
    result = []
    for r in rows:
        age = (today - r.due_date).days if r.due_date else None
        item = InvoiceListItem.model_validate(r)
        item.age_days = age
        result.append(item)
    return result


@router.get(
    "/customers/{customer_id}/invoices",
    response_model=list[InvoiceListItem],
    summary="List invoices for a customer",
)
async def list_customer_invoices(
    customer_id: int,
    db: DBDep,
    cu: CurrentUser,
    invoice_status: Optional[InvoiceStatus] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[InvoiceListItem]:
    invoices = await InvoiceService.list_for_customer(
        db, customer_id, invoice_status, skip, limit
    )
    return [InvoiceListItem.model_validate(inv) for inv in invoices]


@router.get(
    "/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Get invoice by ID",
)
async def get_invoice(
    invoice_id: int,
    db: DBDep,
    cu: CurrentUser,
) -> InvoiceResponse:
    obj = await invoice_crud.get(db, invoice_id, with_lines=True)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    return InvoiceResponse.model_validate(obj)


@router.post(
    "/invoices/{invoice_id}/issue",
    response_model=InvoiceResponse,
    summary="Issue invoice (DRAFT → ISSUED)",
)
async def issue_invoice(
    invoice_id: int,
    db: DBDep,
    cu: CurrentUser,
) -> InvoiceResponse:
    # TODO: require_role(cu, ["admin", "sales_manager"])
    try:
        obj = await InvoiceService.issue(db, invoice_id, user_id=cu.id)
    except SalesError as exc:
        raise _sales_error(exc)
    await db.commit()
    await db.refresh(obj)
    return InvoiceResponse.model_validate(obj)


@router.post(
    "/invoices/{invoice_id}/cancel",
    response_model=InvoiceResponse,
    summary="Cancel invoice",
)
async def cancel_invoice(
    invoice_id: int,
    db: DBDep,
    cu: CurrentUser,
) -> InvoiceResponse:
    # TODO: require_role(cu, ["admin", "sales_manager"])
    try:
        obj = await InvoiceService.cancel(db, invoice_id, user_id=cu.id)
    except SalesError as exc:
        raise _sales_error(exc)
    await db.commit()
    return InvoiceResponse.model_validate(obj)


@router.get(
    "/invoices/{invoice_id}/pdf",
    summary="Generate PDF invoice",
)
async def invoice_pdf(
    invoice_id: int,
    db: DBDep,
    cu: CurrentUser,
) -> Response:
    obj = await invoice_crud.get(db, invoice_id, with_lines=True)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    customer = await customer_crud.get(db, obj.customer_id)
    try:
        from app.services.pdf_service import generate_invoice_pdf
        pdf_bytes = await generate_invoice_pdf(obj, customer)
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{obj.invoice_number}.pdf"'
            },
        )
    except ImportError:
        raise HTTPException(
            status.HTTP_501_NOT_IMPLEMENTED,
            detail="PDF generation requires ReportLab: pip install reportlab",
        )


@router.get(
    "/invoices/{invoice_id}/tax-export",
    response_model=dict,
    summary="Export invoice in Iranian tax authority format",
)
async def invoice_tax_export(
    invoice_id: int,
    db: DBDep,
    cu: CurrentUser,
) -> dict:
    obj = await invoice_crud.get(db, invoice_id, with_lines=True)
    if not obj:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Invoice not found")
    customer = await customer_crud.get(db, obj.customer_id)
    from app.services.sales_accounting_bridge import tax_compliance_service
    return tax_compliance_service.export_to_tax_system(obj, customer, obj.lines)


# ===========================================================================
# PAYMENTS
# ===========================================================================

@router.post(
    "/payments",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record a customer payment",
)
async def create_payment(
    data: PaymentCreate,
    db: DBDep,
    cu: CurrentUser,
) -> PaymentResponse:
    # TODO: require_role(cu, ["admin", "finance_manager", "sales_manager"])
    try:
        payment = await PaymentService.create(db, data, cu.id)
    except SalesError as exc:
        raise _sales_error(exc)
    await db.commit()
    await db.refresh(payment)
    return PaymentResponse.model_validate(payment)


@router.get(
    "/payments",
    response_model=list[PaymentResponse],
    summary="List payments",
)
async def list_payments(
    db: DBDep,
    cu: CurrentUser,
    customer_id: Optional[int] = None,
    payment_status: Optional[PaymentStatus] = Query(None, alias="status"),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[PaymentResponse]:
    _, rows = await payment_crud.list(
        db,
        customer_id=customer_id,
        status=payment_status,
        offset=offset,
        limit=limit,
    )
    return [PaymentResponse.model_validate(r) for r in rows]


@router.post(
    "/payments/{payment_id}/allocate",
    response_model=PaymentResponse,
    summary="Allocate unallocated payment to a specific invoice",
)
async def allocate_payment(
    payment_id: int,
    data: PaymentAllocate,
    db: DBDep,
    cu: CurrentUser,
) -> PaymentResponse:
    try:
        payment = await PaymentService.allocate(db, payment_id, data)
    except SalesError as exc:
        raise _sales_error(exc)
    await db.commit()
    return PaymentResponse.model_validate(payment)


@router.post(
    "/payments/{payment_id}/clear",
    response_model=PaymentResponse,
    summary="Mark payment as CLEARED",
)
async def clear_payment(
    payment_id: int,
    db: DBDep,
    cu: CurrentUser,
) -> PaymentResponse:
    try:
        payment = await PaymentService.clear(db, payment_id)
    except SalesError as exc:
        raise _sales_error(exc)
    await db.commit()
    return PaymentResponse.model_validate(payment)


# ===========================================================================
# REPORTS
# ===========================================================================

@router.get(
    "/reports/revenue-by-period",
    response_model=list[RevenueByPeriodRow],
    summary="Revenue grouped by calendar period",
)
async def report_revenue_by_period(
    db: DBDep,
    cu: CurrentUser,
    from_date: date = Query(...),
    to_date: date = Query(...),
) -> list[RevenueByPeriodRow]:
    return await ReportService.revenue_by_period(db, from_date, to_date)


@router.get(
    "/reports/top-customers",
    response_model=list[TopCustomerRow],
    summary="Top customers by revenue",
)
async def report_top_customers(
    db: DBDep,
    cu: CurrentUser,
    from_date: date = Query(...),
    to_date: date = Query(...),
    limit: int = Query(10, ge=1, le=100),
) -> list[TopCustomerRow]:
    return await ReportService.top_customers(db, from_date, to_date, limit)


@router.get(
    "/reports/product-margins",
    response_model=list[ProductMarginRow],
    summary="Product gross margin analysis",
)
async def report_product_margins(
    db: DBDep,
    cu: CurrentUser,
    from_date: date = Query(...),
    to_date: date = Query(...),
) -> list[ProductMarginRow]:
    return await ReportService.product_margins(db, from_date, to_date)


@router.get(
    "/reports/tax-export",
    response_model=list[TaxExportLine],
    summary="Tax export for Iranian tax authority",
)
async def report_tax_export(
    db: DBDep,
    cu: CurrentUser,
    from_date: date = Query(...),
    to_date: date = Query(...),
) -> list[TaxExportLine]:
    return await ReportService.tax_export(db, from_date, to_date)


@router.get(
    "/reports/ar-aging",
    summary="AR aging report (from Finance module)",
)
async def report_ar_aging(
    db: DBDep,
    cu: CurrentUser,
    as_of_date: date = Query(default_factory=date.today),
) -> dict:
    from app.services.reporting_service import reporting_service
    result = await reporting_service.aging_report(db, as_of_date, "customer")
    return result.model_dump()
