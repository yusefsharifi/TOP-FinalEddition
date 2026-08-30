"""Tests for AI Scheduler endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_scheduler_status(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/scheduler/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "running" in data
    assert "paused" in data


@pytest.mark.asyncio
async def test_scheduler_start(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/scheduler/start", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scheduler_stop(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/scheduler/stop", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scheduler_pause(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/scheduler/pause", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scheduler_resume(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/scheduler/resume", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scheduler_jobs(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/scheduler/jobs", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_scheduler_stats(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/scheduler/stats", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scheduler_history(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/scheduler/history", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scheduler_run_all(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/scheduler/run-all", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scheduler_setup_presets(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/scheduler/presets/default", headers=auth_headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_scheduler_clear_history(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/scheduler/clear-history", headers=auth_headers)
    assert resp.status_code == 200
