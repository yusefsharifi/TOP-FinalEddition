"""
Sales Module — Reporting Service
TOP WorX ERP System
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sales import (
    Customer, InvoiceStatus, SalesInvoice,
    SalesInvoiceLine, SalesPayment,
)
from app.schemas.sales import (
    CustomerStatement, CustomerStatementLine,
    ProductMarginRow, RevenueByPeriodRow, TopCustomerRow,
)


class SalesReportingService:

    async def revenue_by_period(
        self,
        db: AsyncSession,
        year: Optional[int] = None,
        months: int = 12,
    ) -> list[RevenueByPeriodRow]:
        """Monthly revenue summary — last N months."""
        from sqlalchemy import extract, cast, String

        q = (
            select(
                extract("year", SalesInvoice.issue_date).label("yr"),
                extract("month", SalesInvoice.issue_date).label("mo"),
                func.count(SalesInvoice.id).label("cnt"),
                func.coalesce(func.sum(SalesInvoice.subtotal), Decimal("0")).label("sub"),
                func.coalesce(func.sum(SalesInvoice.discount_amount), Decimal("0")).label("disc"),
                func.coalesce(func.sum(SalesInvoice.tax_amount), Decimal("0")).label("tax"),
                func.coalesce(func.sum(SalesInvoice.total_amount), Decimal("0")).label("total"),
                func.coalesce(func.sum(SalesInvoice.amount_paid), Decimal("0")).label("paid"),
            )
            .where(
                SalesInvoice.status.notin_([InvoiceStatus.DRAFT, InvoiceStatus.CANCELLED]),
                SalesInvoice.issue_date.isnot(None),
            )
            .group_by("yr", "mo")
            .order_by("yr", "mo")
        )
        if year:
            q = q.where(extract("year", SalesInvoice.issue_date) == year)

        rows = (await db.execute(q)).all()
        return [
            RevenueByPeriodRow(
                period=f"{int(r.yr)}-{int(r.mo):02d}",
                invoice_count=r.cnt,
                subtotal=Decimal(str(r.sub)),
                discount=Decimal(str(r.disc)),
                tax=Decimal(str(r.tax)),
                total=Decimal(str(r.total)),
                total_paid=Decimal(str(r.paid)),
                outstanding=Decimal(str(r.total)) - Decimal(str(r.paid)),
            )
            for r in rows
        ]

    async def top_customers(
        self, db: AsyncSession, limit: int = 20
    ) -> list[TopCustomerRow]:
        q = (
            select(
                Customer.id,
                Customer.code,
                Customer.name,
                func.count(SalesInvoice.id).label("cnt"),
                func.coalesce(func.sum(SalesInvoice.total_amount), Decimal("0")).label("total"),
                func.coalesce(func.sum(SalesInvoice.amount_paid), Decimal("0")).label("paid"),
                Customer.balance_due,
            )
            .join(SalesInvoice, SalesInvoice.customer_id == Customer.id, isouter=True)
            .where(SalesInvoice.status.notin_([InvoiceStatus.DRAFT, InvoiceStatus.CANCELLED]))
            .group_by(Customer.id, Customer.code, Customer.name, Customer.balance_due)
            .order_by(func.sum(SalesInvoice.total_amount).desc())
            .limit(limit)
        )
        rows = (await db.execute(q)).all()
        return [
            TopCustomerRow(
                customer_id=r.id,
                customer_code=r.code,
                customer_name=r.name,
                invoice_count=r.cnt,
                total_revenue=Decimal(str(r.total)),
                total_paid=Decimal(str(r.paid)),
                balance_due=Decimal(str(r.balance_due)),
            )
            for r in rows
        ]

    async def product_margin(
        self,
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ) -> list[ProductMarginRow]:
        """Revenue minus COGS per inventory item."""
        from app.models.inventory import InventoryItem

        q = (
            select(
                InventoryItem.id,
                InventoryItem.sku,
                InventoryItem.name,
                func.coalesce(func.sum(SalesInvoiceLine.quantity), Decimal("0")).label("qty"),
                func.coalesce(func.sum(SalesInvoiceLine.line_total), Decimal("0")).label("revenue"),
                func.coalesce(func.sum(SalesInvoiceLine.total_cost), Decimal("0")).label("cost"),
            )
            .join(SalesInvoiceLine, SalesInvoiceLine.item_id == InventoryItem.id)
            .join(SalesInvoice, SalesInvoice.id == SalesInvoiceLine.invoice_id)
            .where(SalesInvoice.status.notin_([InvoiceStatus.DRAFT, InvoiceStatus.CANCELLED]))
            .group_by(InventoryItem.id, InventoryItem.sku, InventoryItem.name)
            .order_by(func.sum(SalesInvoiceLine.line_total).desc())
        )
        if date_from:
            q = q.where(SalesInvoice.issue_date >= date_from)
        if date_to:
            q = q.where(SalesInvoice.issue_date <= date_to)

        rows = (await db.execute(q)).all()
        result = []
        for r in rows:
            rev = Decimal(str(r.revenue))
            cost = Decimal(str(r.cost))
            gp = rev - cost
            margin = (gp / rev * Decimal("100")).quantize(Decimal("0.01")) if rev else Decimal("0")
            result.append(ProductMarginRow(
                item_id=r.id, sku=r.sku, item_name=r.name,
                quantity_sold=Decimal(str(r.qty)),
                revenue=rev, cogs=cost, gross_profit=gp, margin_percent=margin,
            ))
        return result

    async def customer_statement(
        self,
        db: AsyncSession,
        customer_id: int,
        as_of_date: Optional[date] = None,
    ) -> CustomerStatement:
        """Full AR statement: invoices and payments in date order."""
        from app.crud.sales import customer_crud

        customer = await customer_crud.get(db, customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        aod = as_of_date or date.today()

        # Invoices
        inv_r = await db.execute(
            select(SalesInvoice).where(
                SalesInvoice.customer_id == customer_id,
                SalesInvoice.issue_date <= aod,
                SalesInvoice.status.notin_([InvoiceStatus.DRAFT, InvoiceStatus.CANCELLED]),
            ).order_by(SalesInvoice.issue_date)
        )
        invoices = inv_r.scalars().all()

        # Payments
        pay_r = await db.execute(
            select(SalesPayment).where(
                SalesPayment.customer_id == customer_id,
                SalesPayment.payment_date <= aod,
                SalesPayment.status == "cleared",
            ).order_by(SalesPayment.payment_date)
        )
        payments = pay_r.scalars().all()

        # Merge into chronological statement
        lines: list[CustomerStatementLine] = []
        running = Decimal("0")

        events: list[dict] = []
        for inv in invoices:
            events.append({"date": inv.issue_date, "type": "invoice", "obj": inv})
        for pay in payments:
            events.append({"date": pay.payment_date, "type": "payment", "obj": pay})
        events.sort(key=lambda e: e["date"])

        for ev in events:
            if ev["type"] == "invoice":
                obj = ev["obj"]
                running += obj.total_amount
                lines.append(CustomerStatementLine(
                    date=obj.issue_date,
                    type="invoice",
                    reference=obj.invoice_number,
                    debit=obj.total_amount,
                    credit=Decimal("0"),
                    running_balance=running,
                ))
            else:
                obj = ev["obj"]
                running -= obj.amount
                lines.append(CustomerStatementLine(
                    date=obj.payment_date,
                    type="payment",
                    reference=obj.payment_number,
                    debit=Decimal("0"),
                    credit=obj.amount,
                    running_balance=running,
                ))

        return CustomerStatement(
            customer_id=customer_id,
            customer_name=customer.name,
            as_of_date=aod,
            lines=lines,
            total_invoiced=customer.total_invoiced,
            total_paid=customer.total_paid,
            balance_due=customer.balance_due,
        )


sales_reporting = SalesReportingService()
