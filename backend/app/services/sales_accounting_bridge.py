"""
Sales Module — Accounting Bridge + Tax Compliance
TOP WorX ERP System

SalesAccountingBridge: creates GL entries when invoices are issued and
                       when payments are received.

TaxComplianceService: Iranian VAT (مالیات بر ارزش افزوده), tax invoice
                      numbers, QR codes, and tax authority export format.

Account mapping (from seeded COA):
  1120 — Accounts Receivable   (AR subledger)
  2130 — VAT Payable
  4100 — Sales Revenue
  5100 — Cost of Goods Sold
  1130 — Inventory
  1110 — Cash & Bank           (for payment receipt)
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sales import InvoiceStatus, PaymentStatus, SalesInvoice, SalesInvoiceLine, SalesPayment


# Account code constants — must match seeded COA in 0002_finance_module.py
ACCT_AR = "1120"
ACCT_CASH = "1110"
ACCT_INVENTORY = "1130"
ACCT_VAT_PAYABLE = "2130"
ACCT_SALES_REVENUE = "4100"
ACCT_COGS = "5100"

VAT_RATE = Decimal("9")


# ===========================================================================
# Sales Accounting Bridge
# ===========================================================================
class SalesAccountingBridge:

    async def create_invoice_entries(
        self,
        db: AsyncSession,
        invoice: SalesInvoice,
        lines: list[SalesInvoiceLine],
        customer,
        user_id: Optional[int] = None,
    ) -> tuple[Optional[int], Optional[int]]:
        """
        Creates two journal entries when an invoice is issued:

        Entry 1 — Revenue recognition:
          Dr 1120 — Accounts Receivable  [total_amount]
            Cr 4100 — Sales Revenue        [subtotal - discount]
            Cr 2130 — VAT Payable          [tax_amount]

        Entry 2 — COGS recognition:
          Dr 5100 — COGS                  [sum(line.total_cost)]
            Cr 1130 — Inventory            [sum(line.total_cost)]

        Returns (revenue_je_id, cogs_je_id)
        """
        from app.services.accounting_service import accounting_service
        from app.models.finance import ReferenceType

        entry_date = invoice.issue_date or date.today()
        net_revenue = invoice.subtotal - invoice.discount_amount
        total_cogs = sum(ln.total_cost for ln in lines)

        # ── Entry 1: Revenue ──────────────────────────────────────────────
        rev_lines = [
            {
                "account_code": ACCT_AR,
                "debit": invoice.total_amount,
                "description": f"Invoice {invoice.invoice_number}",
                "contact_id": invoice.customer_id,
                "contact_type": "customer",
            },
            {
                "account_code": ACCT_SALES_REVENUE,
                "credit": net_revenue,
                "description": f"Revenue — {invoice.invoice_number}",
            },
        ]
        if invoice.tax_amount > Decimal("0"):
            rev_lines.append({
                "account_code": ACCT_VAT_PAYABLE,
                "credit": invoice.tax_amount,
                "description": f"VAT — {invoice.invoice_number}",
            })

        try:
            rev_entry = await accounting_service.build_and_create_entry(
                db,
                entry_date=entry_date,
                description=f"Sales — Invoice {invoice.invoice_number}",
                description_fa=f"فروش — فاکتور {invoice.invoice_number}",
                reference_type=ReferenceType.INVOICE,
                reference_id=invoice.id,
                lines=rev_lines,
                user_id=user_id,
            )
            revenue_je_id = rev_entry.id
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Failed to create revenue JE for invoice %s", invoice.invoice_number)
            revenue_je_id = None

        # ── Entry 2: COGS ────────────────────────────────────────────────
        cogs_je_id = None
        if total_cogs > Decimal("0"):
            try:
                cogs_entry = await accounting_service.build_and_create_entry(
                    db,
                    entry_date=entry_date,
                    description=f"COGS — Invoice {invoice.invoice_number}",
                    description_fa=f"بهای تمام‌شده — فاکتور {invoice.invoice_number}",
                    reference_type=ReferenceType.INVOICE,
                    reference_id=invoice.id,
                    lines=[
                        {
                            "account_code": ACCT_COGS,
                            "debit": total_cogs,
                            "description": f"COGS: {invoice.invoice_number}",
                        },
                        {
                            "account_code": ACCT_INVENTORY,
                            "credit": total_cogs,
                            "description": f"Inventory out: {invoice.invoice_number}",
                        },
                    ],
                    user_id=user_id,
                )
                cogs_je_id = cogs_entry.id
            except Exception:
                import logging
                logging.getLogger(__name__).exception("Failed to create COGS JE for invoice %s", invoice.invoice_number)

        return revenue_je_id, cogs_je_id

    async def reverse_invoice_entries(
        self,
        db: AsyncSession,
        invoice: SalesInvoice,
        user_id: int,
    ) -> None:
        """Reverse revenue and COGS entries when an invoice is cancelled."""
        from app.crud.finance import journal_entry_crud
        from app.services.accounting_service import accounting_service

        reversal_date = date.today()

        for je_id in [invoice.revenue_journal_entry_id, invoice.cogs_journal_entry_id]:
            if je_id:
                entry = await journal_entry_crud.get(db, je_id, with_lines=True)
                if entry:
                    try:
                        reversal = await accounting_service.reverse_entry(
                            db, entry, reversal_date, user_id
                        )
                        await accounting_service.post_entry(db, reversal, user_id)
                    except Exception:
                        import logging
                        logging.getLogger(__name__).exception(
                            "Failed to reverse JE %s for invoice %s", je_id, invoice.invoice_number
                        )

    async def apply_payment(
        self,
        db: AsyncSession,
        payment: SalesPayment,
        user_id: Optional[int] = None,
    ) -> SalesPayment:
        """
        When a payment is received:

        Dr 1110 — Cash / Bank           [payment.amount]
          Cr 1120 — Accounts Receivable  [payment.amount]

        Then allocates to oldest unpaid invoices first.
        """
        from app.services.accounting_service import accounting_service
        from app.models.finance import ReferenceType

        # Determine debit account (Cash or Bank)
        # bank_account_id, if provided, is a finance.accounts.id — look up its code
        debit_acct_code = ACCT_CASH
        if payment.bank_account_id:
            from app.crud.finance import account_crud
            bank_acct = await account_crud.get(db, payment.bank_account_id)
            if bank_acct:
                debit_acct_code = bank_acct.code

        try:
            je = await accounting_service.build_and_create_entry(
                db,
                entry_date=payment.payment_date,
                description=f"Payment received — {payment.payment_number}",
                description_fa=f"دریافت وجه — {payment.payment_number}",
                reference_type=ReferenceType.PAYMENT,
                reference_id=payment.id,
                lines=[
                    {
                        "account_code": debit_acct_code,
                        "debit": payment.amount,
                        "description": f"Receipt: {payment.reference_number or payment.payment_number}",
                    },
                    {
                        "account_code": ACCT_AR,
                        "credit": payment.amount,
                        "description": f"Customer {payment.customer_id} payment",
                        "contact_id": payment.customer_id,
                        "contact_type": "customer",
                    },
                ],
                user_id=user_id,
            )
            payment.journal_entry_id = je.id
            payment.status = PaymentStatus.CLEARED
        except Exception:
            import logging
            logging.getLogger(__name__).exception("Failed to create payment JE %s", payment.payment_number)

        # Allocate to invoices (oldest due date first)
        await self._allocate_payment(db, payment, user_id)
        await db.flush()
        return payment

    async def _allocate_payment(
        self, db: AsyncSession, payment: SalesPayment, user_id: Optional[int]
    ) -> None:
        """Apply payment to oldest outstanding invoices for this customer."""
        from sqlalchemy import select, and_
        from app.models.sales import SalesInvoice, InvoiceStatus

        if payment.invoice_id:
            # Directed payment — apply to specific invoice only
            invoices_to_pay = []
            inv = await db.get(SalesInvoice, payment.invoice_id)
            if inv:
                invoices_to_pay = [inv]
        else:
            # Auto-allocate oldest-first
            result = await db.execute(
                select(SalesInvoice)
                .where(
                    SalesInvoice.customer_id == payment.customer_id,
                    SalesInvoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIAL_PAID, InvoiceStatus.OVERDUE]),
                    SalesInvoice.amount_due > Decimal("0"),
                )
                .order_by(SalesInvoice.due_date.asc())
            )
            invoices_to_pay = result.scalars().all()

        remaining = payment.amount
        for inv in invoices_to_pay:
            if remaining <= Decimal("0"):
                break
            apply = min(remaining, inv.amount_due)
            inv.amount_paid += apply
            inv.amount_due -= apply
            if inv.amount_due <= Decimal("0.001"):
                inv.status = InvoiceStatus.PAID
                inv.amount_due = Decimal("0")
            else:
                inv.status = InvoiceStatus.PARTIAL_PAID
            remaining -= apply

        await db.flush()

        # Update customer AR
        from app.crud.sales import customer_crud
        await customer_crud.update_ar_balance(db, payment.customer_id)

    async def calculate_customer_balance(
        self, db: AsyncSession, customer_id: int
    ) -> Decimal:
        """
        Returns live AR balance: sum of issued invoices minus sum of cleared payments.
        Should match GL account 1120 filtered by contact_id = customer_id.
        """
        from sqlalchemy import select, func
        from app.models.sales import SalesInvoice, SalesPayment, InvoiceStatus, PaymentStatus

        inv_r = await db.execute(
            select(func.coalesce(func.sum(SalesInvoice.amount_due), Decimal("0")))
            .where(
                SalesInvoice.customer_id == customer_id,
                SalesInvoice.status.notin_([InvoiceStatus.DRAFT, InvoiceStatus.CANCELLED]),
            )
        )
        return Decimal(str(inv_r.scalar_one() or "0"))


# ===========================================================================
# Tax Compliance Service
# ===========================================================================
class TaxComplianceService:
    """
    Iranian tax authority compliance.
    Reference: سازمان امور مالیاتی کشور — my.tax.gov.ir
    DECISION POINT ⚙️: Replace generate_tax_invoice_number() with actual
    sequential counter from DB sequence once tax authority API is integrated.
    """

    VAT_RATE = Decimal("9")

    def generate_tax_invoice_number(self, invoice_number: str) -> str:
        """
        Iranian tax invoice number format:
        Series (2 digits) + Year (4 digits) + Sequential (8 digits)
        Example: AA-1403-00000001
        DECISION POINT ⚙️: Series code must be registered with tax authority.
        Replace '01' with your registered seller series.
        """
        # Extract numeric portion from invoice_number for sequence
        digits = re.sub(r"\D", "", invoice_number)[-8:].zfill(8)
        year = date.today().year  # Use Jalali year in production
        return f"01-{year}-{digits}"

    def generate_invoice_qr_data(self, invoice: SalesInvoice, customer) -> str:
        """
        QR code payload per Iranian tax authority spec.
        Encodes: seller economic code, buyer tax ID, amounts, date.
        """
        data = {
            "seller_economic_code": "REPLACE_WITH_YOUR_ECONOMIC_CODE",
            "buyer_tax_id": getattr(customer, "tax_id", ""),
            "buyer_economic_code": getattr(customer, "economic_code", ""),
            "invoice_number": invoice.invoice_number,
            "tax_invoice_number": invoice.tax_invoice_number or "",
            "issue_date": invoice.issue_date.isoformat() if invoice.issue_date else "",
            "total_amount": str(invoice.total_amount),
            "tax_base": str(invoice.subtotal - invoice.discount_amount),
            "vat_amount": str(invoice.tax_amount),
            "currency": "IRR",
        }
        return json.dumps(data, ensure_ascii=False)

    def export_to_tax_system(self, invoice: SalesInvoice, customer, lines) -> dict:
        """
        Format for my.tax.gov.ir API submission.
        DECISION POINT ⚙️: Verify current API schema at
        https://my.tax.gov.ir — this format reflects 2024 spec.
        """
        tax_lines = []
        for ln in lines:
            net = ln.line_total - ln.tax_amount
            tax_lines.append({
                "commodityCode": str(ln.item_id),  # ISIC code — TODO: add to InventoryItem
                "description": ln.description,
                "count": str(ln.quantity),
                "unitPrice": str(ln.unit_price),
                "discount": str(ln.discount_amount),
                "taxBase": str(net),
                "vat": str(ln.tax_amount),
                "total": str(ln.line_total),
            })

        return {
            "header": {
                "taxType": "1",          # 1 = standard VAT invoice
                "serialNo": invoice.tax_invoice_number,
                "taxid": "REPLACE_WITH_YOUR_TAX_ID",
                "buyerTaxId": getattr(customer, "tax_id", ""),
                "buyerEconomicCode": getattr(customer, "economic_code", ""),
                "issueDate": invoice.issue_date.isoformat() if invoice.issue_date else "",
                "dueDate": invoice.due_date.isoformat() if invoice.due_date else "",
                "currency": "IRR",
                "totalAmount": str(invoice.total_amount),
                "totalDiscount": str(invoice.discount_amount),
                "totalTax": str(invoice.tax_amount),
                "totalNetAmount": str(invoice.subtotal - invoice.discount_amount),
            },
            "body": tax_lines,
        }

    def calculate_vat(self, net_amount: Decimal) -> Decimal:
        """9% VAT on net amount after discounts."""
        return (net_amount * self.VAT_RATE / Decimal("100")).quantize(Decimal("0.0001"))


# Singletons
sales_accounting_bridge = SalesAccountingBridge()
tax_compliance_service = TaxComplianceService()
