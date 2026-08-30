"""Tests for Report module endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_report(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/reports/reports/", json={
        "name": "گزارش تست",
        "type": "sales_summary",
        "parameters": {"period": "monthly"},
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_get_report(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/reports/reports/1", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_create_template(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/reports/report-templates/", json={
        "name": "قالب تست",
        "type": "sales",
        "columns": ["date", "amount", "status"],
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_templates(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/reports/report-templates/public", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_create_schedule(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/reports/report-schedules/", json={
        "report_id": 1,
        "frequency": "daily",
        "recipients": ["admin@topworx.com"],
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_scheduled_reports(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/reports/reports/scheduled", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_sales_summary(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/reports/reports/sales-summary", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_product_performance(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/reports/reports/product-performance", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_customer_analysis(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/reports/reports/customer-analysis", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_sales_rep_performance(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/reports/reports/sales-rep-performance", headers=auth_headers)
    assert resp.status_code == 200
