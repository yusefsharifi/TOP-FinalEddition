"""
Sales Module — CRUD Layer
TOP WorX ERP System
"""
from __future__ import annotations

import random
import string
from datetime import date
from decimal import Decimal
from typing import Optional, Sequence

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.sales import (
    Customer, CustomerCategory, InvoiceStatus, PaymentStatus,
    QuoteStatus, SalesInvoice, SalesInvoiceLine, SalesPayment,
    SalesQuote, SalesQuoteLine,
)
from app.schemas.sales import (
    CustomerCreate, CustomerUpdate, InvoiceCreate,
    PaymentCreate, QuoteCreate,
)


def _rand(n: int = 5) -> str:
    return "".join(random.choices(string.digits, k=n))


# ===========================================================================
# Customer CRUD
# ===========================================================================
class CustomerCRUD:
    async def get(self, db: AsyncSession, customer_id: int) -> Optional[Customer]:
        r = await db.execute(select(Customer).where(Customer.id == customer_id))
        return r.scalar_one_or_none()

    async def get_by_code(self, db: AsyncSession, code: str) -> Optional[Customer]:
        r = await db.execute(select(Customer).where(Customer.code == code))
        return r.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        is_active: Optional[bool] = True,
        category: Optional[CustomerCategory] = None,
        search: Optional[str] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[Customer]]:
        q = select(Customer).order_by(Customer.name)
        if is_active is not None:
            q = q.where(Customer.is_active == is_active)
        if category:
            q = q.where(Customer.category == category)
        if search:
            term = f"%{search}%"
            q = q.where(
                or_(Customer.name.ilike(term), Customer.code.ilike(term),
                    Customer.name_fa.ilike(term), Customer.tax_id.ilike(term))
            )
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def create(
        self, db: AsyncSession, data: CustomerCreate, user_id: Optional[int] = None
    ) -> Customer:
        obj = Customer(**data.model_dump(), created_by_id=user_id, updated_by_id=user_id)
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj

    async def update(
        self, db: AsyncSession, obj: Customer, data: CustomerUpdate, user_id: Optional[int] = None
    ) -> Customer:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(obj, field, value)
        obj.updated_by_id = user_id
        await db.flush()
        return obj

    async def update_ar_balance(self, db: AsyncSession, customer_id: int) -> None:
        """Recompute denormalised AR totals from live data."""
        inv_totals = await db.execute(
            select(
                func.coalesce(func.sum(SalesInvoice.total_amount), Decimal("0")).label("invoiced"),
                func.coalesce(func.sum(SalesInvoice.amount_paid), Decimal("0")).label("paid"),
            ).where(
                SalesInvoice.customer_id == customer_id,
                SalesInvoice.status.notin_([InvoiceStatus.DRAFT, InvoiceStatus.CANCELLED]),
            )
        )
        row = inv_totals.one()
        customer = await self.get(db, customer_id)
        if customer:
            customer.total_invoiced = Decimal(str(row.invoiced))
            customer.total_paid = Decimal(str(row.paid))
            customer.balance_due = customer.total_invoiced - customer.total_paid
            await db.flush()


# ===========================================================================
# Quote CRUD
# ===========================================================================
class QuoteCRUD:
    async def get(
        self, db: AsyncSession, quote_id: int, with_lines: bool = True
    ) -> Optional[SalesQuote]:
        q = select(SalesQuote).where(SalesQuote.id == quote_id)
        if with_lines:
            q = q.options(selectinload(SalesQuote.lines))
        r = await db.execute(q)
        return r.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        customer_id: Optional[int] = None,
        status: Optional[QuoteStatus] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[SalesQuote]]:
        q = select(SalesQuote).order_by(SalesQuote.id.desc())
        if customer_id:
            q = q.where(SalesQuote.customer_id == customer_id)
        if status:
            q = q.where(SalesQuote.status == status)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def create(
        self, db: AsyncSession, data: QuoteCreate, user_id: Optional[int] = None
    ) -> SalesQuote:
        from datetime import datetime
        year = 1403  # TODO: compute Jalali year from date
        quote_number = f"QT-{year}-{_rand(5)}"

        # Calculate totals
        subtotal = Decimal("0")
        discount_total = Decimal("0")
        tax_total = Decimal("0")
        for ln in data.lines:
            base = ln.quantity * ln.unit_price
            disc = base * ln.discount_percent / Decimal("100")
            net = base - disc
            tax = net * ln.tax_percent / Decimal("100")
            subtotal += base
            discount_total += disc
            tax_total += tax

        total = subtotal - discount_total + tax_total

        obj = SalesQuote(
            quote_number=quote_number,
            customer_id=data.customer_id,
            quote_date=data.quote_date,
            expiry_date=data.expiry_date,
            status=QuoteStatus.DRAFT,
            subtotal=subtotal,
            discount_amount=discount_total,
            tax_amount=tax_total,
            total=total,
            notes=data.notes,
            terms=data.terms,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        db.add(obj)
        await db.flush()

        for ln in data.lines:
            base = ln.quantity * ln.unit_price
            disc = base * ln.discount_percent / Decimal("100")
            net = base - disc
            tax = net * ln.tax_percent / Decimal("100")
            line_total = net + tax
            line = SalesQuoteLine(
                quote_id=obj.id,
                item_id=ln.item_id,
                description=ln.description,
                quantity=ln.quantity,
                unit_price=ln.unit_price,
                discount_percent=ln.discount_percent,
                tax_percent=ln.tax_percent,
                line_total=line_total,
                sort_order=ln.sort_order,
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            db.add(line)

        await db.flush()
        await db.refresh(obj)
        return obj


# ===========================================================================
# Invoice CRUD
# ===========================================================================
class InvoiceCRUD:
    async def get(
        self, db: AsyncSession, invoice_id: int, with_lines: bool = True
    ) -> Optional[SalesInvoice]:
        q = select(SalesInvoice).where(SalesInvoice.id == invoice_id)
        if with_lines:
            q = q.options(selectinload(SalesInvoice.lines))
        r = await db.execute(q)
        return r.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        customer_id: Optional[int] = None,
        status: Optional[InvoiceStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        overdue_only: bool = False,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[SalesInvoice]]:
        q = select(SalesInvoice).order_by(SalesInvoice.id.desc())
        if customer_id:
            q = q.where(SalesInvoice.customer_id == customer_id)
        if status:
            q = q.where(SalesInvoice.status == status)
        if date_from:
            q = q.where(SalesInvoice.issue_date >= date_from)
        if date_to:
            q = q.where(SalesInvoice.issue_date <= date_to)
        if overdue_only:
            q = q.where(
                SalesInvoice.due_date < date.today(),
                SalesInvoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIAL_PAID])
            )
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def create_from_data(
        self,
        db: AsyncSession,
        data: InvoiceCreate,
        customer,
        user_id: Optional[int] = None,
    ) -> SalesInvoice:
        year = 1403  # TODO: Jalali year
        invoice_number = f"INV-{year}-{_rand(5)}"

        due = data.due_date or (
            date.fromordinal(data.draft_date.toordinal() + customer.payment_terms)
        )

        obj = SalesInvoice(
            invoice_number=invoice_number,
            customer_id=data.customer_id,
            quote_id=data.quote_id,
            draft_date=data.draft_date,
            due_date=due,
            status=InvoiceStatus.DRAFT,
            subtotal=Decimal("0"),
            discount_amount=Decimal("0"),
            tax_amount=Decimal("0"),
            total_amount=Decimal("0"),
            amount_paid=Decimal("0"),
            amount_due=Decimal("0"),
            notes=data.notes,
            terms=data.terms,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        db.add(obj)
        await db.flush()

        subtotal = Decimal("0")
        discount_total = Decimal("0")
        tax_total = Decimal("0")

        for ln in data.lines:
            base = ln.quantity * ln.unit_price
            disc = ln.discount_amount
            net = base - disc
            tax = net * ln.tax_percent / Decimal("100")
            line_total = net + tax

            subtotal += base
            discount_total += disc
            tax_total += tax

            line = SalesInvoiceLine(
                invoice_id=obj.id,
                item_id=ln.item_id,
                description=ln.description,
                unit_of_measure=ln.unit_of_measure,
                quantity=ln.quantity,
                unit_price=ln.unit_price,
                discount_amount=disc,
                tax_amount=tax,
                line_total=line_total,
                unit_cost=Decimal("0"),    # filled by FIFO calc on issue
                total_cost=Decimal("0"),   # filled on issue
                revenue_account_id=ln.revenue_account_id,
                cogs_account_id=ln.cogs_account_id,
                sort_order=ln.sort_order,
                created_by_id=user_id,
                updated_by_id=user_id,
            )
            db.add(line)

        obj.subtotal = subtotal
        obj.discount_amount = discount_total
        obj.tax_amount = tax_total
        obj.total_amount = subtotal - discount_total + tax_total
        obj.amount_due = obj.total_amount

        await db.flush()
        await db.refresh(obj)
        return obj


# ===========================================================================
# Payment CRUD
# ===========================================================================
class PaymentCRUD:
    async def get(self, db: AsyncSession, payment_id: int) -> Optional[SalesPayment]:
        r = await db.execute(select(SalesPayment).where(SalesPayment.id == payment_id))
        return r.scalar_one_or_none()

    async def list(
        self,
        db: AsyncSession,
        *,
        customer_id: Optional[int] = None,
        status: Optional[PaymentStatus] = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[int, Sequence[SalesPayment]]:
        q = select(SalesPayment).order_by(SalesPayment.payment_date.desc())
        if customer_id:
            q = q.where(SalesPayment.customer_id == customer_id)
        if status:
            q = q.where(SalesPayment.status == status)
        total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
        rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
        return total, rows

    async def create(
        self, db: AsyncSession, data: PaymentCreate, user_id: Optional[int] = None
    ) -> SalesPayment:
        year = 1403
        payment_number = f"RCV-{year}-{_rand(5)}"
        obj = SalesPayment(
            payment_number=payment_number,
            **data.model_dump(),
            status=PaymentStatus.PENDING,
            created_by_id=user_id,
            updated_by_id=user_id,
        )
        db.add(obj)
        await db.flush()
        await db.refresh(obj)
        return obj


# ---------------------------------------------------------------------------
# Singletons
# ---------------------------------------------------------------------------
customer_crud = CustomerCRUD()
quote_crud = QuoteCRUD()
invoice_crud = InvoiceCRUD()
payment_crud = PaymentCRUD()
