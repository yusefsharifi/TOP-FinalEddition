"""
Contracts Module — Test Suite
TOP WorX ERP System

Tests:
  - Contract CRUD
  - Approval workflow (DRAFT → PENDING → APPROVED → ACTIVE)
  - Termination and renewal
  - History audit trail
  - Dashboard statistics
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_contract(client: AsyncClient):
    resp = await client.post("/api/v1/contracts", json={
        "title": "Software License Agreement",
        "contract_type": "service",
        "counterparty_name": "TechCorp Inc.",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "value": 50000,
        "currency": "USD",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Software License Agreement"
    assert data["status"] == "draft"
    assert data["contract_type"] == "service"


@pytest.mark.asyncio
async def test_list_contracts_empty(client: AsyncClient):
    resp = await client.get("/api/v1/contracts")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_update_draft_contract(client: AsyncClient):
    resp = await client.post("/api/v1/contracts", json={
        "title": "Draft", "contract_type": "lease",
        "counterparty_name": "Landlord LLC",
        "start_date": "2024-01-01", "end_date": "2024-12-31",
    })
    contract_id = resp.json()["id"]

    resp = await client.patch(f"/api/v1/contracts/{contract_id}", json={
        "title": "Updated Draft",
        "value": 100000,
    })
    assert resp.status_code == 200
    assert resp.json()["title"] == "Updated Draft"
    assert resp.json()["value"] == 100000


@pytest.mark.asyncio
async def test_cannot_update_non_draft_contract(client: AsyncClient):
    resp = await client.post("/api/v1/contracts", json={
        "title": "Active", "contract_type": "service",
        "counterparty_name": "X",
        "start_date": "2024-01-01", "end_date": "2024-12-31",
    })
    contract_id = resp.json()["id"]
    # Submit → approve → activate
    await client.post(f"/api/v1/contracts/{contract_id}/submit")
    await client.post(f"/api/v1/contracts/{contract_id}/approve")
    await client.post(f"/api/v1/contracts/{contract_id}/activate")

    resp = await client.patch(f"/api/v1/contracts/{contract_id}", json={"title": "Hacked"})
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_approval_workflow(client: AsyncClient):
    resp = await client.post("/api/v1/contracts", json={
        "title": "Workflow Test", "contract_type": "purchase",
        "counterparty_name": "Supplier A",
        "start_date": "2024-01-01", "end_date": "2024-06-30",
    })
    cid = resp.json()["id"]

    # Submit
    resp = await client.post(f"/api/v1/contracts/{cid}/submit")
    assert resp.json()["status"] == "pending_approval"

    # Approve
    resp = await client.post(f"/api/v1/contracts/{cid}/approve")
    assert resp.json()["status"] == "approved"
    assert resp.json()["approved_by_id"] == 1

    # Activate
    resp = await client.post(f"/api/v1/contracts/{cid}/activate")
    assert resp.json()["status"] == "active"


@pytest.mark.asyncio
async def test_terminate_contract(client: AsyncClient):
    resp = await client.post("/api/v1/contracts", json={
        "title": "Terminate Me", "contract_type": "service",
        "counterparty_name": "X",
        "start_date": "2024-01-01", "end_date": "2024-12-31",
    })
    cid = resp.json()["id"]
    await client.post(f"/api/v1/contracts/{cid}/submit")
    await client.post(f"/api/v1/contracts/{cid}/approve")
    await client.post(f"/api/v1/contracts/{cid}/activate")

    resp = await client.post(f"/api/v1/contracts/{cid}/terminate")
    assert resp.json()["status"] == "terminated"


@pytest.mark.asyncio
async def test_renew_contract(client: AsyncClient):
    resp = await client.post("/api/v1/contracts", json={
        "title": "Renew Me", "contract_type": "lease",
        "counterparty_name": "Landlord",
        "start_date": "2024-01-01", "end_date": "2024-12-31",
    })
    cid = resp.json()["id"]
    await client.post(f"/api/v1/contracts/{cid}/submit")
    await client.post(f"/api/v1/contracts/{cid}/approve")
    await client.post(f"/api/v1/contracts/{cid}/activate")

    resp = await client.post(f"/api/v1/contracts/{cid}/renew?new_end_date=2025-12-31")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "active"
    assert data["end_date"] == "2025-12-31"


@pytest.mark.asyncio
async def test_contract_stats(client: AsyncClient):
    await client.post("/api/v1/contracts", json={
        "title": "A", "contract_type": "service",
        "counterparty_name": "X",
        "start_date": "2024-01-01", "end_date": "2024-12-31",
    })

    resp = await client.get("/api/v1/contracts/dashboard/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert "by_type" in data
