"""
Documents Module — Test Suite
TOP WorX ERP System

Tests:
  - Document metadata CRUD
  - Version tracking
  - Category filtering
  - Deletion
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_document(client: AsyncClient):
    resp = await client.post("/api/v1/documents", json={
        "name": "Q1 Financial Report",
        "description": "Quarterly financial report for Q1 2024.",
        "category": "report",
        "tags": ["finance", "quarterly"],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Q1 Financial Report"
    assert data["category"] == "report"
    assert data["version"] == 1
    assert data["tags"] == ["finance", "quarterly"]


@pytest.mark.asyncio
async def test_list_documents_empty(client: AsyncClient):
    resp = await client.get("/api/v1/documents")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_documents_with_data(client: AsyncClient):
    await client.post("/api/v1/documents", json={"name": "Doc 1", "category": "general"})
    await client.post("/api/v1/documents", json={"name": "Doc 2", "category": "contract"})

    resp = await client.get("/api/v1/documents")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_list_documents_filter_by_category(client: AsyncClient):
    await client.post("/api/v1/documents", json={"name": "Report", "category": "report"})
    await client.post("/api/v1/documents", json={"name": "Contract", "category": "contract"})

    resp = await client.get("/api/v1/documents?category=report")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["category"] == "report"


@pytest.mark.asyncio
async def test_list_documents_search(client: AsyncClient):
    await client.post("/api/v1/documents", json={"name": "Budget Plan 2024", "category": "general"})
    await client.post("/api/v1/documents", json={"name": "Tax Return", "category": "general"})

    resp = await client.get("/api/v1/documents?search=budget")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


@pytest.mark.asyncio
async def test_get_document(client: AsyncClient):
    resp = await client.post("/api/v1/documents", json={"name": "Test", "category": "general"})
    doc_id = resp.json()["id"]

    resp = await client.get(f"/api/v1/documents/{doc_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test"


@pytest.mark.asyncio
async def test_document_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/documents/9999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_document(client: AsyncClient):
    resp = await client.post("/api/v1/documents", json={"name": "Delete me", "category": "general"})
    doc_id = resp.json()["id"]

    resp = await client.delete(f"/api/v1/documents/{doc_id}")
    assert resp.status_code == 204

    resp = await client.get(f"/api/v1/documents/{doc_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_document_versions_empty(client: AsyncClient):
    resp = await client.post("/api/v1/documents", json={"name": "New", "category": "general"})
    doc_id = resp.json()["id"]

    resp = await client.get(f"/api/v1/documents/{doc_id}/versions")
    assert resp.status_code == 200
    assert resp.json() == []
