"""Tests for AI Reports endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_natural_language_query(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/reports/query", json={
        "query": "Show me total sales this month",
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_generate_report(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/reports/generate", json={
        "report_type": "sales_summary",
        "parameters": {"period": "monthly"},
    }, headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_ai_generate_report(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/reports/ai-generate", json={
        "prompt": "Generate a report on inventory levels",
    }, headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_list_reports(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/reports", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_report_templates(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/reports/templates", headers=auth_headers)
    assert resp.status_code == 200
