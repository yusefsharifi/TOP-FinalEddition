"""Tests for AI Module Integration endpoints."""
import pytest
from httpx import AsyncClient


MODULES = [
    "inventory", "finance", "hr", "sales", "crm", "procurement",
    "projects", "quality", "hse", "bi", "documents", "contracts",
    "budget", "settings", "notifications", "messages", "calendar",
    "support", "tasks",
]


@pytest.mark.asyncio
async def test_list_modules(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/modules/list", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_cross_module_dashboard(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/modules/cross-module/dashboard", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "modules_analyzed" in data
    assert "total_insights" in data


@pytest.mark.asyncio
async def test_cross_module_correlations(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/modules/cross-module/correlations", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "correlations" in data


@pytest.mark.asyncio
async def test_module_insights(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/modules/inventory/insights", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "insights" in data


@pytest.mark.asyncio
async def test_module_predictions(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/modules/finance/predictions", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "predictions" in data


@pytest.mark.asyncio
async def test_module_recommendations(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/modules/hr/recommendations", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "recommendations" in data


@pytest.mark.asyncio
async def test_module_analytics(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/modules/sales/analytics", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_natural_query(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/modules/crm/natural-query", json={
        "query": "Show me top customers",
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "answer" in data or "result" in data


@pytest.mark.asyncio
@pytest.mark.parametrize("module", MODULES[:5])
async def test_module_insights_parametrized(client: AsyncClient, auth_headers: dict, module: str):
    resp = await client.get(f"/api/v1/ai/modules/{module}/insights", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize("module", MODULES[:5])
async def test_module_predictions_parametrized(client: AsyncClient, auth_headers: dict, module: str):
    resp = await client.get(f"/api/v1/ai/modules/{module}/predictions", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
@pytest.mark.parametrize("module", MODULES[:5])
async def test_module_recommendations_parametrized(client: AsyncClient, auth_headers: dict, module: str):
    resp = await client.get(f"/api/v1/ai/modules/{module}/recommendations", headers=auth_headers)
    assert resp.status_code == 200
