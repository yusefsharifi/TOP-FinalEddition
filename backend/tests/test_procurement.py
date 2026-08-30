"""
Tests for Procurement Module endpoints.
TOP WorX ERP System
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_vendor(client: AsyncClient, auth_headers: dict):
    """Test vendor creation."""
    response = await client.post(
        "/api/v1/procurement/vendors",
        json={
            "code": "VEND-001",
            "name": "Test Vendor",
            "name_fa": "تامین‌کننده تست",
            "contact_email": "vendor@test.com",
            "contact_phone": "021-12345678",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["code"] == "VEND-001"


@pytest.mark.asyncio
async def test_list_vendors(client: AsyncClient, auth_headers: dict):
    """Test vendor listing."""
    response = await client.get(
        "/api/v1/procurement/vendors",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_purchase_request(client: AsyncClient, auth_headers: dict):
    """Test purchase request creation."""
    response = await client.post(
        "/api/v1/procurement/requests",
        json={
            "department": "IT",
            "priority": "medium",
            "description": "Test purchase request",
            "lines": [
                {
                    "item_name": "Test Item",
                    "quantity": 10,
                    "unit_price": 100000,
                }
            ],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_list_purchase_requests(client: AsyncClient, auth_headers: dict):
    """Test purchase request listing."""
    response = await client.get(
        "/api/v1/procurement/requests",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_approval_rule(client: AsyncClient, auth_headers: dict):
    """Test approval rule creation."""
    response = await client.post(
        "/api/v1/procurement/approval-rules",
        json={
            "name": "Test Approval Rule",
            "min_amount": 1000000,
            "approver_role": "manager",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_list_approval_rules(client: AsyncClient, auth_headers: dict):
    """Test approval rules listing."""
    response = await client.get(
        "/api/v1/procurement/approval-rules",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_spend_by_vendor_report(client: AsyncClient, auth_headers: dict):
    """Test spend by vendor report."""
    response = await client.get(
        "/api/v1/procurement/reports/spend-by-vendor",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_pending_approvals_report(client: AsyncClient, auth_headers: dict):
    """Test pending approvals report."""
    response = await client.get(
        "/api/v1/procurement/reports/pending-approvals",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
