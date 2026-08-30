"""Tests for Finance / Accounting module endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_account(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/accounting/accounts", json={
        "code": "1101",
        "name": "صندوق",
        "type": "asset",
        "is_active": True,
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_accounts(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/accounting/accounts", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_create_journal_entry(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/accounting/journal-entries", json={
        "date": "2025-01-01",
        "description": "ورودی صندوق",
        "lines": [
            {"account_code": "1101", "debit": 1000, "credit": 0},
            {"account_code": "3101", "debit": 0, "credit": 1000},
        ],
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_journal_entries(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/accounting/journal-entries", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_trial_balance(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/accounting/trial-balance", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_financial_statements(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/accounting/financial-statements", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_bank_account(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/accounting/bank-accounts", json={
        "name": "حساب بانک ملت",
        "bank_name": "ملت",
        "account_number": "12345678",
        "account_type": "checking",
        "currency": "IRR",
        "current_balance": 0,
        "is_active": True,
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_bank_accounts(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/accounting/bank-accounts", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_budget(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/accounting/budgets", json={
        "name": "بودجه ۱۴۰۴",
        "account_code": "3101",
        "amount": 50000000,
        "period": "2025-01",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_budgets(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/accounting/budgets", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_dashboard(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/accounting/dashboard", headers=auth_headers)
    assert resp.status_code == 200
