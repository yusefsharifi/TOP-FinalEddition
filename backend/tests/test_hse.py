"""
HSE Module — Test Suite
TOP WorX ERP System

Tests:
  - Incident CRUD and status transitions
  - Checklist creation and item updates
  - Safety alerts
  - Dashboard statistics
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_incident(client: AsyncClient):
    resp = await client.post("/api/v1/hse/incidents", json={
        "title": "Chemical spill in warehouse B",
        "description": "A container of solvent leaked on the floor.",
        "severity": "high",
        "location": "Warehouse B, Aisle 3",
        "department": "Production",
        "injured_persons": 0,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Chemical spill in warehouse B"
    assert data["severity"] == "high"
    assert data["status"] == "open"
    assert data["reported_by_id"] == 1


@pytest.mark.asyncio
async def test_list_incidents_empty(client: AsyncClient):
    resp = await client.get("/api/v1/hse/incidents")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_incidents_with_data(client: AsyncClient):
    # Create two incidents
    await client.post("/api/v1/hse/incidents", json={
        "title": "Incident 1", "description": "Desc", "severity": "low", "location": "Office",
    })
    await client.post("/api/v1/hse/incidents", json={
        "title": "Incident 2", "description": "Desc", "severity": "critical", "location": "Plant",
    })

    resp = await client.get("/api/v1/hse/incidents")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_list_incidents_filter_by_severity(client: AsyncClient):
    await client.post("/api/v1/hse/incidents", json={
        "title": "Low", "description": "Desc", "severity": "low", "location": "Office",
    })
    await client.post("/api/v1/hse/incidents", json={
        "title": "Critical", "description": "Desc", "severity": "critical", "location": "Plant",
    })

    resp = await client.get("/api/v1/hse/incidents?severity=critical")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["severity"] == "critical"


@pytest.mark.asyncio
async def test_update_incident_status(client: AsyncClient):
    # Create
    resp = await client.post("/api/v1/hse/incidents", json={
        "title": "Test", "description": "Desc", "severity": "medium", "location": "Lab",
    })
    incident_id = resp.json()["id"]

    # Update
    resp = await client.patch(f"/api/v1/hse/incidents/{incident_id}", json={
        "status": "under_investigation",
        "investigation_notes": "CCTV footage reviewed.",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "under_investigation"
    assert resp.json()["investigation_notes"] == "CCTV footage reviewed."


@pytest.mark.asyncio
async def test_incident_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/hse/incidents/9999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_checklist(client: AsyncClient):
    resp = await client.post("/api/v1/hse/checklists", json={
        "title": "Monthly fire safety inspection",
        "location": "Building A",
        "items": ["Extinguishers present", "Exit signs visible", "Fire alarm tested"],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Monthly fire safety inspection"
    assert data["status"] == "pending"
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_update_checklist_item(client: AsyncClient):
    # Create checklist
    resp = await client.post("/api/v1/hse/checklists", json={
        "title": "Test", "location": "Office",
        "items": ["Item A", "Item B"],
    })
    checklist_id = resp.json()["id"]
    item_id = resp.json()["items"][0]["id"]

    # Update item
    resp = await client.put(
        f"/api/v1/hse/checklists/{checklist_id}/items/{item_id}",
        json={"status": "passed", "notes": "All good"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "updated"


@pytest.mark.asyncio
async def test_create_alert(client: AsyncClient):
    resp = await client.post("/api/v1/hse/alerts", json={
        "title": "Chemical hazard warning",
        "message": "New solvent storage procedure in effect.",
        "severity": "high",
        "target_department": "Production",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Chemical hazard warning"
    assert data["created_by_id"] == 1


@pytest.mark.asyncio
async def test_hse_dashboard(client: AsyncClient):
    # Create some data
    await client.post("/api/v1/hse/incidents", json={
        "title": "Inc", "description": "Desc", "severity": "low", "location": "X",
    })
    await client.post("/api/v1/hse/alerts", json={
        "title": "Alert", "message": "Msg", "severity": "info",
    })

    resp = await client.get("/api/v1/hse/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "open_incidents" in data
    assert "active_alerts" in data
    assert data["active_alerts"] == 1
