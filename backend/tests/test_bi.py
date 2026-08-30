"""
Tests for BI Module endpoints.
TOP WorX ERP System
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ceo_dashboard(client: AsyncClient, auth_headers: dict):
    """Test CEO dashboard endpoint."""
    response = await client.get(
        "/api/v1/bi/dashboard/ceo?year=1403&month=1",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_cfo_dashboard(client: AsyncClient, auth_headers: dict):
    """Test CFO dashboard endpoint."""
    response = await client.get(
        "/api/v1/bi/dashboard/cfo?year=1403&month=1",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_sales_dashboard(client: AsyncClient, auth_headers: dict):
    """Test Sales dashboard endpoint."""
    response = await client.get(
        "/api/v1/bi/dashboard/sales?year=1403&month=1",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_inventory_dashboard(client: AsyncClient, auth_headers: dict):
    """Test Inventory dashboard endpoint."""
    response = await client.get(
        "/api/v1/bi/dashboard/inventory",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_hr_dashboard(client: AsyncClient, auth_headers: dict):
    """Test HR dashboard endpoint."""
    response = await client.get(
        "/api/v1/bi/dashboard/hr?year=1403&month=1",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_get_all_kpis(client: AsyncClient, auth_headers: dict):
    """Test KPIs endpoint."""
    response = await client.get(
        "/api/v1/bi/kpis?year=1403&month=1",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_list_alerts(client: AsyncClient, auth_headers: dict):
    """Test alerts listing endpoint."""
    response = await client.get(
        "/api/v1/bi/alerts",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_alert_rule(client: AsyncClient, auth_headers: dict):
    """Test alert rule creation."""
    response = await client.post(
        "/api/v1/bi/alerts/rules",
        json={
            "name": "Test Alert Rule",
            "metric": "revenue",
            "condition": "below",
            "threshold": 1000000,
            "severity": "warning",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == "Test Alert Rule"


@pytest.mark.asyncio
async def test_list_report_templates(client: AsyncClient, auth_headers: dict):
    """Test report templates listing."""
    response = await client.get(
        "/api/v1/bi/reports/templates",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_build_report(client: AsyncClient, auth_headers: dict):
    """Test report building."""
    response = await client.post(
        "/api/v1/bi/reports/build",
        json={
            "base_table": "sales",
            "dimensions": ["customer"],
            "measures": ["total_amount"],
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
