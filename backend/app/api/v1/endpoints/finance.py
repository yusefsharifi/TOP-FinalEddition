# backend/app/api/v1/endpoints/finance.py
"""
Finance & Accounting Router — Async
TOP WorX ERP System

All endpoints use AsyncSession from app.api.deps.
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.api.deps import DBDep, CurrentUser
from app.core.accounting import (
    Accounting,
    AccountType,
    JournalEntry,
    AccountingError,
)
from app.models.finance import (
    Account,
    FiscalPeriod,
    JournalEntry as JournalEntryModel,
)
from app.schemas.finance import (
    FiscalPeriodCreate,
    FiscalPeriodResponse,
    AccountCreate,
    AccountUpdate,
    AccountResponse,
    AccountTreeResponse,
    AccountWithBalanceResponse,
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryResponse,
    JournalEntryStatus,
    ReferenceType,
    TrialBalanceResponse,
    BalanceSheetResponse,
    IncomeStatementResponse,
    AgingReportResponse,
    InventoryValuationResponse,
    ExchangeRateCreate,
    ContactType,
)

router = APIRouter()


# ===========================================================================
# HELPER: Async accounting service loader
# ===========================================================================

async def _get_accounting_service(db: DBDep, limit_entries: int = 5000) -> Accounting:
    """
    Build an Accounting service instance loaded from the database.
    """
    service = Accounting()
    # Eagerly load accounts
    accounts_r = await db.execute(
        select(Account).where(Account.is_active == True)
    )
    for acc in accounts_r.scalars().all():
        service.add_account(acc)
    # Limit journal entries to prevent memory exhaustion
    entries_r = await db.execute(
        select(JournalEntryModel)
        .order_by(JournalEntryModel.id.desc())
        .limit(limit_entries)
    )
    for entry in entries_r.scalars().all():
        service.journal_entries[entry.id] = entry
    return service


# ===========================================================================
# FISCAL PERIODS
# ===========================================================================

@router.post(
    "/periods",
    response_model=FiscalPeriodResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ایجاد دوره مالی جدید",
)
async def create_fiscal_period(
    data: FiscalPeriodCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> FiscalPeriodResponse:
    existing_r = await db.execute(
        select(FiscalPeriod).where(
            FiscalPeriod.year == data.year,
            FiscalPeriod.is_closed == False,
        )
    )
    if existing_r.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"یک دوره مالی باز برای سال {data.year} وجود دارد.",
        )

    period = FiscalPeriod(
        **data.model_dump(),
        created_by=current_user.id,
    )
    db.add(period)
    await db.commit()
    await db.refresh(period)
    return FiscalPeriodResponse.model_validate(period)


@router.get(
    "/periods",
    response_model=list[FiscalPeriodResponse],
    summary="لیست دوره‌های مالی",
)
async def list_fiscal_periods(
    db: DBDep,
    current_user: CurrentUser,
    year: Optional[int] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[FiscalPeriodResponse]:
    q = select(FiscalPeriod)
    if year is not None:
        q = q.where(FiscalPeriod.year == year)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [FiscalPeriodResponse.model_validate(r) for r in rows]


@router.post(
    "/periods/{period_id}/close",
    response_model=FiscalPeriodResponse,
    summary="بستن دوره مالی",
)
async def close_fiscal_period(
    period_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> FiscalPeriodResponse:
    period = await db.get(FiscalPeriod, period_id)
    if not period:
        raise HTTPException(status_code=404, detail="دوره مالی یافت نشد.")
    if period.is_closed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="این دوره مالی قبلاً بسته شده است.",
        )
    period.is_closed = True
    period.closed_by = current_user.id
    await db.commit()
    await db.refresh(period)
    return FiscalPeriodResponse.model_validate(period)


# ===========================================================================
# CHART OF ACCOUNTS
# ===========================================================================

@router.post(
    "/accounts",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ایجاد حساب جدید",
)
async def create_account(
    data: AccountCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> AccountResponse:
    existing_r = await db.execute(select(Account).where(Account.code == data.code))
    if existing_r.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"کد حساب '{data.code}' قبلاً ثبت شده است.",
        )
    account = Account(**data.model_dump(), created_by=current_user.id)
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return AccountResponse.model_validate(account)


@router.get(
    "/accounts",
    response_model=list[AccountResponse],
    summary="لیست حساب‌ها",
)
async def list_accounts(
    db: DBDep,
    current_user: CurrentUser,
    type: Optional[AccountType] = None,
    is_active: Optional[bool] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[AccountResponse]:
    q = select(Account)
    if type is not None:
        q = q.where(Account.type == type)
    if is_active is not None:
        q = q.where(Account.is_active == is_active)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [AccountResponse.model_validate(r) for r in rows]


@router.get(
    "/accounts/tree",
    response_model=list[AccountTreeResponse],
    summary="درخت حساب‌ها",
)
async def get_account_tree(
    db: DBDep,
    current_user: CurrentUser,
) -> list[AccountTreeResponse]:
    roots_r = await db.execute(
        select(Account).where(Account.parent_id == None, Account.is_active == True)
    )
    return [AccountTreeResponse.model_validate(r) for r in roots_r.scalars().all()]


@router.get(
    "/accounts/{account_id}",
    response_model=AccountResponse,
    summary="جزئیات یک حساب",
)
async def get_account(
    account_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> AccountResponse:
    account = await db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="حساب یافت نشد.")
    return AccountResponse.model_validate(account)


@router.patch(
    "/accounts/{account_id}",
    response_model=AccountResponse,
    summary="بروزرسانی حساب",
)
async def update_account(
    account_id: int,
    data: AccountUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> AccountResponse:
    account = await db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="حساب یافت نشد.")

    if data.code and data.code != account.code:
        dup_r = await db.execute(select(Account).where(Account.code == data.code))
        if dup_r.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"کد حساب '{data.code}' قبلاً ثبت شده است.",
            )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(account, field, value)
    account.updated_by = current_user.id

    await db.commit()
    await db.refresh(account)
    return AccountResponse.model_validate(account)


@router.delete(
    "/accounts/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="حذف حساب",
)
async def delete_account(
    account_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> None:
    account = await db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="حساب یافت نشد.")

    has_entries_r = await db.execute(
        select(JournalEntryModel).where(JournalEntryModel.account_id == account_id)
    )
    if has_entries_r.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="این حساب دارای اسناد حسابداری است و قابل حذف نیست.",
        )

    await db.delete(account)
    await db.commit()


@router.get(
    "/accounts/{account_id}/balance",
    response_model=AccountWithBalanceResponse,
    summary="مانده حساب",
)
async def get_account_balance(
    account_id: int,
    db: DBDep,
    current_user: CurrentUser,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> AccountWithBalanceResponse:
    account = await db.get(Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="حساب یافت نشد.")

    service = await _get_accounting_service(db)
    balance = service.get_account_balance(account_id, end_date or date.today())

    return AccountWithBalanceResponse.model_validate(
        {**account.__dict__, "balance": balance}
    )


# ===========================================================================
# JOURNAL ENTRIES
# ===========================================================================

@router.post(
    "/journal-entries",
    response_model=JournalEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ثبت سند حسابداری",
)
async def create_journal_entry(
    data: JournalEntryCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> JournalEntryResponse:
    try:
        entry = JournalEntryModel(
            **data.model_dump(),
            created_by=current_user.id,
            status=JournalEntryStatus.DRAFT,
        )
        db.add(entry)
        await db.commit()
        await db.refresh(entry)
        return JournalEntryResponse.model_validate(entry)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/journal-entries",
    response_model=list[JournalEntryResponse],
    summary="لیست اسناد حسابداری",
)
async def list_journal_entries(
    db: DBDep,
    current_user: CurrentUser,
    status_filter: Optional[JournalEntryStatus] = None,
    reference_type: Optional[ReferenceType] = None,
    reference_id: Optional[int] = None,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
) -> list[JournalEntryResponse]:
    q = select(JournalEntryModel)
    if status_filter is not None:
        q = q.where(JournalEntryModel.status == status_filter)
    if reference_type is not None:
        q = q.where(JournalEntryModel.reference_type == reference_type)
    if reference_id is not None:
        q = q.where(JournalEntryModel.reference_id == reference_id)
    rows = (await db.execute(q.offset(offset).limit(limit))).scalars().all()
    return [JournalEntryResponse.model_validate(r) for r in rows]


@router.get(
    "/journal-entries/{entry_id}",
    response_model=JournalEntryResponse,
    summary="جزئیات سند حسابداری",
)
async def get_journal_entry(
    entry_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> JournalEntryResponse:
    entry = await db.get(JournalEntryModel, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="سند حسابداری یافت نشد.")
    return JournalEntryResponse.model_validate(entry)


@router.patch(
    "/journal-entries/{entry_id}",
    response_model=JournalEntryResponse,
    summary="بروزرسانی سند حسابداری",
)
async def update_journal_entry(
    entry_id: int,
    data: JournalEntryUpdate,
    db: DBDep,
    current_user: CurrentUser,
) -> JournalEntryResponse:
    entry = await db.get(JournalEntryModel, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="سند حسابداری یافت نشد.")
    if entry.status == JournalEntryStatus.POSTED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="سند ثبت‌شده (Posted) قابل ویرایش نیست.",
        )

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entry, field, value)
    entry.updated_by = current_user.id

    await db.commit()
    await db.refresh(entry)
    return JournalEntryResponse.model_validate(entry)


@router.delete(
    "/journal-entries/{entry_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="حذف سند حسابداری",
)
async def delete_journal_entry(
    entry_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> None:
    entry = await db.get(JournalEntryModel, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="سند حسابداری یافت نشد.")
    if entry.status == JournalEntryStatus.POSTED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="سند ثبت‌شده (Posted) قابل حذف نیست.",
        )
    await db.delete(entry)
    await db.commit()


@router.post(
    "/journal-entries/{entry_id}/post",
    response_model=JournalEntryResponse,
    summary="تایید و ثبت نهایی سند",
)
async def post_journal_entry(
    entry_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> JournalEntryResponse:
    entry = await db.get(JournalEntryModel, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="سند حسابداری یافت نشد.")
    if entry.status == JournalEntryStatus.POSTED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="این سند قبلاً ثبت نهایی شده است.",
        )

    try:
        service = await _get_accounting_service(db)
        service.validate_journal_entry(entry)

        entry.status = JournalEntryStatus.POSTED
        entry.posted_by = current_user.id
        entry.posted_at = date.today()

        await db.commit()
        await db.refresh(entry)
        return JournalEntryResponse.model_validate(entry)
    except AccountingError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/journal-entries/{entry_id}/reverse",
    response_model=JournalEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="برگشت سند حسابداری",
)
async def reverse_journal_entry(
    entry_id: int,
    db: DBDep,
    current_user: CurrentUser,
) -> JournalEntryResponse:
    original = await db.get(JournalEntryModel, entry_id)
    if not original:
        raise HTTPException(status_code=404, detail="سند حسابداری یافت نشد.")
    if original.status != JournalEntryStatus.POSTED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="فقط اسناد ثبت‌شده (Posted) قابل برگشت هستند.",
        )

    try:
        reversal = JournalEntryModel(
            reference=f"REV-{original.reference}",
            description=f"برگشت سند: {original.description}",
            date=date.today(),
            status=JournalEntryStatus.POSTED,
            reversed_entry_id=original.id,
            created_by=current_user.id,
            posted_by=current_user.id,
            posted_at=date.today(),
        )
        # Load original lines to reverse them
        for line in original.lines:
            reversal.lines.append(
                type(line)(
                    account_id=line.account_id,
                    debit=line.credit,
                    credit=line.debit,
                    description=f"برگشت: {line.description}",
                )
            )
        db.add(reversal)
        original.is_reversed = True
        await db.commit()
        await db.refresh(reversal)
        return JournalEntryResponse.model_validate(reversal)
    except Exception as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


# ===========================================================================
# REPORTS
# ===========================================================================

@router.get(
    "/trial-balance",
    response_model=TrialBalanceResponse,
    summary="تراز آزمایشی",
)
async def get_trial_balance(
    db: DBDep,
    current_user: CurrentUser,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> TrialBalanceResponse:
    service = await _get_accounting_service(db)
    data = service.get_trial_balance(as_of_date=end_date or date.today())
    return TrialBalanceResponse.model_validate({"rows": data})


@router.get(
    "/balance-sheet",
    response_model=BalanceSheetResponse,
    summary="ترازنامه",
)
async def get_balance_sheet(
    db: DBDep,
    current_user: CurrentUser,
    as_of_date: Optional[date] = None,
) -> BalanceSheetResponse:
    service = await _get_accounting_service(db)
    data = service.get_balance_sheet(as_of_date=as_of_date or date.today())
    return BalanceSheetResponse.model_validate(data)


@router.get(
    "/income-statement",
    response_model=IncomeStatementResponse,
    summary="صورت سود و زیان",
)
async def get_income_statement(
    db: DBDep,
    current_user: CurrentUser,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> IncomeStatementResponse:
    service = await _get_accounting_service(db)
    _start = start_date or date(date.today().year, 1, 1)
    _end = end_date or date.today()
    data = service.get_income_statement(start_date=_start, end_date=_end)
    return IncomeStatementResponse.model_validate(data)


@router.get(
    "/aging",
    response_model=AgingReportResponse,
    summary="گزارش سنی دیون",
)
async def get_aging_report(
    db: DBDep,
    current_user: CurrentUser,
    contact_type: ContactType = Query(...),
    as_of_date: Optional[date] = None,
) -> AgingReportResponse:
    service = await _get_accounting_service(db)
    data = service.get_aging_report(
        contact_type=contact_type,
        as_of_date=as_of_date or date.today(),
    )
    return AgingReportResponse.model_validate(data)


@router.get(
    "/inventory-valuation",
    response_model=InventoryValuationResponse,
    summary="ارزیابی موجودی انبار",
)
async def get_inventory_valuation(
    db: DBDep,
    current_user: CurrentUser,
    as_of_date: Optional[date] = None,
) -> InventoryValuationResponse:
    service = await _get_accounting_service(db)
    data = service.get_inventory_valuation(
        as_of_date=as_of_date or date.today(),
    )
    return InventoryValuationResponse.model_validate(data)


# ===========================================================================
# EXCHANGE RATES
# ===========================================================================

@router.post(
    "/exchange-rates",
    response_model=ExchangeRateCreate,
    status_code=status.HTTP_201_CREATED,
    summary="ثبت نرخ ارز",
)
async def create_exchange_rate(
    data: ExchangeRateCreate,
    db: DBDep,
    current_user: CurrentUser,
) -> ExchangeRateCreate:
    # TODO: پیاده‌سازی مدل ExchangeRate در دیتابیس
    return data


# ===========================================================================
# HEALTH CHECK
# ===========================================================================

@router.get("/health", summary="وضعیت سرویس مالی")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "finance"}
