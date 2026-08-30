"""Tests for HR module endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_employee(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/hr/employees", json={
        "first_name": "علی",
        "last_name": "احمدی",
        "national_code": "1234567890",
        "email": "ali@test.com",
        "phone": "09121234567",
        "department_id": 1,
        "position": "برنامه‌نویس",
        "hire_date": "2025-01-01",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_employees(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/hr/employees", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_get_employee(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/hr/employees/1", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_create_department(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/hr/departments", json={
        "name": "فناوری اطلاعات",
        "code": "IT",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_departments(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/hr/departments", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_create_leave(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/hr/leaves", json={
        "employee_id": 1,
        "leave_type": "annual",
        "start_date": "2025-06-01",
        "end_date": "2025-06-03",
        "reason": "مرخصی سالانه",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_leaves(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/hr/leaves", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_check_in(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/hr/attendance/check-in", headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_attendance_summary(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/hr/attendance/summary", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_payroll_periods(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/hr/payroll/periods", headers=auth_headers)
    assert resp.status_code == 200
