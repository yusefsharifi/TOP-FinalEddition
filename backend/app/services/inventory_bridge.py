"""
Finance Module — Inventory Accounting Bridge
TOP WorX ERP System

Automatically creates double-entry journal entries for every inventory movement.

Account mapping (from COA seed data):
  1130 — Inventory Asset
  2110 — Accounts Payable
  1110 — Cash & Bank
  4100 — Sales Revenue
  1120 — Accounts Receivable
  5100 — Cost of Goods Sold (COGS)
  5200 — Other Expense (Inventory Adjustment Loss)
  4200 — Other Income (Inventory Adjustment Gain)

INTEGRATION POINT ─── inventory_service.py ────────────────────────────────
After `await db.flush()` in process_inbound/process_outbound/adjust_stock,
call:
    from app.services.inventory_bridge import inventory_bridge
    await inventory_bridge.create_entry_for_movement(movement, item, db, user_id)
────────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.finance import account_crud, journal_entry_crud
from app.models.finance import (
    AccountSubtype, JournalEntryStatus, ReferenceType,
)
from app.services.accounting_service import AccountingError, accounting_service


# ---------------------------------------------------------------------------
# Account code constants (match your seeded COA exactly)
# ---------------------------------------------------------------------------
ACCT_INVENTORY = "1130"          # دارایی — موجودی کالا
ACCT_CASH = "1110"               # دارایی — صندوق و بانک
ACCT_AR = "1120"                 # دارایی — حسابهای دریافتنی
ACCT_AP = "2110"                 # بدهی — حسابهای پرداختنی
ACCT_SALES = "4100"              # درآمد — درآمد فروش
ACCT_COGS = "5100"               # هزینه — بهای تمام شده کالای فروش رفته
ACCT_INV_ADJ_EXPENSE = "5210"    # هزینه — تعدیل موجودی (زیان)
ACCT_INV_ADJ_INCOME = "4200"     # درآمد — تعدیل موجودی (سود)


class InventoryAccountingBridge:
    """
    Translates inventory movements into balanced journal entries.

    Called by inventory_service.py after each confirmed movement.
    Never commits — the inventory service transaction wraps everything.
    """

    async def create_entry_for_movement(
        self,
        movement,               # InventoryMovement ORM instance
        item,                   # InventoryItem ORM instance
        db: AsyncSession,
        user_id: Optional[int] = None,
        *,
        sale_price: Optional[Decimal] = None,       # For OUTBOUND: sale price per unit
        counterparty_account: str = ACCT_AP,         # Override default AP account
        contact_id: Optional[int] = None,
        contact_type_str: Optional[str] = None,
    ) -> None:
        """
        Determine movement type and dispatch to the appropriate entry builder.
        Silently skips TRANSFER movements (no P&L impact, internal only).
        """
        from app.models.inventory import MovementType  # avoid circular import

        move_type = movement.movement_type
        unit_cost = item.standard_cost or Decimal("0")
        total_cost = unit_cost * movement.quantity

        if total_cost == Decimal("0"):
            # Nothing to record (zero-cost item)
            return

        try:
            if move_type == MovementType.INBOUND:
                await self._entry_inbound(
                    db=db,
                    movement=movement,
                    total_cost=total_cost,
                    counterparty_account=counterparty_account,
                    contact_id=contact_id,
                    contact_type_str=contact_type_str,
                    user_id=user_id,
                )
            elif move_type == MovementType.OUTBOUND:
                await self._entry_outbound(
                    db=db,
                    movement=movement,
                    total_cost=total_cost,
                    sale_price=sale_price,
                    quantity=movement.quantity,
                    contact_id=contact_id,
                    contact_type_str=contact_type_str,
                    user_id=user_id,
                )
            elif move_type == MovementType.ADJUSTMENT:
                await self._entry_adjustment(
                    db=db,
                    movement=movement,
                    total_cost=abs(total_cost),
                    is_gain=(movement.quantity_after > movement.quantity_before),
                    user_id=user_id,
                )
            # TRANSFER, RETURN, SCRAP — add entries here as needed
        except AccountingError:
            # Log but don't crash the inventory operation.
            # DECISION POINT ⚙️: In production you may want to fail hard here
            # so inventory and GL are always in sync.
            import logging
            logging.getLogger(__name__).exception(
                "Failed to create accounting entry for movement %s", movement.id
            )

    async def _entry_inbound(
        self,
        *,
        db: AsyncSession,
        movement,
        total_cost: Decimal,
        counterparty_account: str,
        contact_id: Optional[int],
        contact_type_str: Optional[str],
        user_id: Optional[int],
    ) -> None:
        """
        Purchase / Receive goods:
          Dr 1130 — Inventory          [cost]
            Cr 2110 — Accounts Payable   [cost]

        بابت دریافت کالا — بدهکار موجودی، بستانکار حسابهای پرداختنی
        """
        await accounting_service.build_and_create_entry(
            db,
            entry_date=movement.movement_date.date() if hasattr(movement.movement_date, "date") else movement.movement_date,
            description=f"Inventory inbound — {movement.reference_number}",
            description_fa=f"دریافت کالا — {movement.reference_number}",
            reference_type=ReferenceType.INVENTORY,
            reference_id=movement.id,
            lines=[
                {
                    "account_code": ACCT_INVENTORY,
                    "debit": total_cost,
                    "description": f"Inbound: {movement.reference_number}",
                    "contact_id": contact_id,
                    "contact_type": contact_type_str,
                },
                {
                    "account_code": counterparty_account,
                    "credit": total_cost,
                    "description": f"Payable: {movement.reference_number}",
                    "contact_id": contact_id,
                    "contact_type": contact_type_str,
                },
            ],
            user_id=user_id,
        )

    async def _entry_outbound(
        self,
        *,
        db: AsyncSession,
        movement,
        total_cost: Decimal,
        sale_price: Optional[Decimal],
        quantity: Decimal,
        contact_id: Optional[int],
        contact_type_str: Optional[str],
        user_id: Optional[int],
    ) -> None:
        """
        Issue / Sell goods — two journal entries:

        1. COGS recognition:
           Dr 5100 — Cost of Goods Sold   [cost]
             Cr 1130 — Inventory            [cost]

        2. Revenue recognition (only if sale_price provided):
           Dr 1120 — Accounts Receivable   [revenue]
             Cr 4100 — Sales Revenue         [revenue]

        بابت فروش کالا — دو سند حسابداری
        """
        entry_date = movement.movement_date.date() if hasattr(movement.movement_date, "date") else movement.movement_date

        # Entry 1: COGS
        await accounting_service.build_and_create_entry(
            db,
            entry_date=entry_date,
            description=f"COGS — {movement.reference_number}",
            description_fa=f"بهای تمام شده کالای فروش رفته — {movement.reference_number}",
            reference_type=ReferenceType.INVENTORY,
            reference_id=movement.id,
            lines=[
                {
                    "account_code": ACCT_COGS,
                    "debit": total_cost,
                    "description": f"COGS: {movement.reference_number}",
                },
                {
                    "account_code": ACCT_INVENTORY,
                    "credit": total_cost,
                    "description": f"Inventory out: {movement.reference_number}",
                },
            ],
            user_id=user_id,
        )

        # Entry 2: Revenue (skip if this is an internal issue, not a sale)
        if sale_price is not None and sale_price > Decimal("0"):
            total_revenue = sale_price * quantity
            await accounting_service.build_and_create_entry(
                db,
                entry_date=entry_date,
                description=f"Sales revenue — {movement.reference_number}",
                description_fa=f"درآمد فروش — {movement.reference_number}",
                reference_type=ReferenceType.INVENTORY,
                reference_id=movement.id,
                lines=[
                    {
                        "account_code": ACCT_AR,
                        "debit": total_revenue,
                        "description": f"Revenue: {movement.reference_number}",
                        "contact_id": contact_id,
                        "contact_type": contact_type_str,
                    },
                    {
                        "account_code": ACCT_SALES,
                        "credit": total_revenue,
                        "description": f"Revenue: {movement.reference_number}",
                        "contact_id": contact_id,
                        "contact_type": contact_type_str,
                    },
                ],
                user_id=user_id,
            )

    async def _entry_adjustment(
        self,
        *,
        db: AsyncSession,
        movement,
        total_cost: Decimal,
        is_gain: bool,
        user_id: Optional[int],
    ) -> None:
        """
        Stock adjustment:

        Gain (found extra stock):
          Dr 1130 — Inventory
            Cr 4200 — Inventory Adjustment Income

        Loss (missing stock):
          Dr 5210 — Inventory Adjustment Expense
            Cr 1130 — Inventory

        تعدیل موجودی — سود یا زیان انبارداری
        """
        entry_date = movement.movement_date.date() if hasattr(movement.movement_date, "date") else movement.movement_date

        if is_gain:
            lines = [
                {"account_code": ACCT_INVENTORY, "debit": total_cost,
                 "description": f"Adj gain: {movement.reference_number}"},
                {"account_code": ACCT_INV_ADJ_INCOME, "credit": total_cost,
                 "description": f"Adj gain: {movement.reference_number}"},
            ]
            desc = f"Inventory adjustment gain — {movement.reference_number}"
            desc_fa = f"سود تعدیل موجودی — {movement.reference_number}"
        else:
            lines = [
                {"account_code": ACCT_INV_ADJ_EXPENSE, "debit": total_cost,
                 "description": f"Adj loss: {movement.reference_number}"},
                {"account_code": ACCT_INVENTORY, "credit": total_cost,
                 "description": f"Adj loss: {movement.reference_number}"},
            ]
            desc = f"Inventory adjustment loss — {movement.reference_number}"
            desc_fa = f"زیان تعدیل موجودی — {movement.reference_number}"

        await accounting_service.build_and_create_entry(
            db,
            entry_date=entry_date,
            description=desc,
            description_fa=desc_fa,
            reference_type=ReferenceType.INVENTORY,
            reference_id=movement.id,
            lines=lines,
            user_id=user_id,
        )

    # -----------------------------------------------------------------------
    # Inventory reconciliation
    # -----------------------------------------------------------------------

    async def get_inventory_gl_balance(self, db: AsyncSession) -> Decimal:
        """Returns the current GL balance of account 1130 (Inventory)."""
        account = await account_crud.get_by_code(db, ACCT_INVENTORY)
        if not account:
            return Decimal("0")
        total_dr, total_cr = await account_crud.get_balance(db, account.id)
        return total_dr - total_cr  # Inventory is an asset (debit-normal)

    async def get_physical_inventory_value(self, db: AsyncSession) -> Decimal:
        """
        Calculates physical inventory value from stock levels:
        SUM(quantity_on_hand * item.standard_cost)
        """
        from app.models.inventory import InventoryItem, StockLevel  # avoid circular

        result = await db.execute(
            select(
                func.coalesce(
                    func.sum(StockLevel.quantity_on_hand * InventoryItem.standard_cost),
                    Decimal("0"),
                )
            ).join(InventoryItem, InventoryItem.id == StockLevel.item_id)
            .where(InventoryItem.is_active.is_(True))
        )
        return Decimal(str(result.scalar_one() or "0"))

    async def reconcile(self, db: AsyncSession) -> dict:
        """Compare GL account 1130 with physical inventory valuation."""
        gl_balance = await self.get_inventory_gl_balance(db)
        physical_value = await self.get_physical_inventory_value(db)
        variance = physical_value - gl_balance
        return {
            "gl_balance": gl_balance,
            "physical_value": physical_value,
            "variance": variance,
            "is_reconciled": abs(variance) < Decimal("0.01"),
        }


# Singleton
inventory_bridge = InventoryAccountingBridge()
