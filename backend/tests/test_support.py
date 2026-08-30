"""
Tests for Support & Ticketing Module endpoints.
TOP WorX ERP System
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_ticket(client: AsyncClient, auth_headers: dict):
    """Test ticket creation."""
    response = await client.post(
        "/api/v1/support/tickets",
        json={
            "subject": "Test Support Ticket",
            "description": "This is a test support ticket",
            "category": "general",
            "priority": "medium",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "ticket_number" in data


@pytest.mark.asyncio
async def test_my_tickets(client: AsyncClient, auth_headers: dict):
    """Test listing my tickets."""
    response = await client.get(
        "/api/v1/support/tickets",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_all_tickets(client: AsyncClient, auth_headers: dict):
    """Test listing all tickets (agent view)."""
    response = await client.get(
        "/api/v1/support/tickets/all",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_agent_dashboard(client: AsyncClient, auth_headers: dict):
    """Test agent dashboard."""
    response = await client.get(
        "/api/v1/support/dashboard",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "my_open_tickets" in data
    assert "queue" in data


@pytest.mark.asyncio
async def test_list_kb_articles(client: AsyncClient, auth_headers: dict):
    """Test knowledge base article listing."""
    response = await client.get(
        "/api/v1/support/kb",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_search_kb(client: AsyncClient, auth_headers: dict):
    """Test knowledge base search."""
    response = await client.get(
        "/api/v1/support/kb/search?q=test",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_teams(client: AsyncClient, auth_headers: dict):
    """Test support teams listing."""
    response = await client.get(
        "/api/v1/support/teams",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_team(client: AsyncClient, auth_headers: dict):
    """Test team creation."""
    response = await client.post(
        "/api/v1/support/teams",
        json={
            "name": "Test Team",
            "name_fa": "تیم تست",
            "email": "team@test.com",
            "categories": ["general"],
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_list_sla_policies(client: AsyncClient, auth_headers: dict):
    """Test SLA policies listing."""
    response = await client.get(
        "/api/v1/support/sla",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_sla_policy(client: AsyncClient, auth_headers: dict):
    """Test SLA policy creation."""
    response = await client.post(
        "/api/v1/support/sla",
        json={
            "name": "Standard SLA",
            "is_default": True,
            "response_times": {"low": 240, "medium": 120, "high": 60, "critical": 15},
            "resolution_times": {"low": 2880, "medium": 1440, "high": 480, "critical": 240},
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_performance_report(client: AsyncClient, auth_headers: dict):
    """Test performance report."""
    response = await client.get(
        "/api/v1/support/reports/performance",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_satisfaction_report(client: AsyncClient, auth_headers: dict):
    """Test satisfaction report."""
    response = await client.get(
        "/api/v1/support/reports/satisfaction",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "avg_csat" in data
