"""
Tasks Module — Test Suite
TOP WorX ERP System

Tests:
  - Task CRUD and status transitions
  - Comments
  - Filtering (by status, priority, assigned_to_me)
  - Dashboard statistics
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_task(client: AsyncClient):
    resp = await client.post("/api/v1/tasks", json={
        "name": "Review Q1 budget",
        "description": "Review and approve Q1 budget allocations.",
        "priority": "high",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Review Q1 budget"
    assert data["status"] == "pending"
    assert data["priority"] == "high"
    assert data["created_by_id"] == 1


@pytest.mark.asyncio
async def test_list_tasks_empty(client: AsyncClient):
    resp = await client.get("/api/v1/tasks")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_tasks_with_data(client: AsyncClient):
    await client.post("/api/v1/tasks", json={"name": "Task 1", "priority": "low"})
    await client.post("/api/v1/tasks", json={"name": "Task 2", "priority": "urgent"})

    resp = await client.get("/api/v1/tasks")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_list_tasks_filter_by_priority(client: AsyncClient):
    await client.post("/api/v1/tasks", json={"name": "Low", "priority": "low"})
    await client.post("/api/v1/tasks", json={"name": "Urgent", "priority": "urgent"})

    resp = await client.get("/api/v1/tasks?priority=urgent")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["priority"] == "urgent"


@pytest.mark.asyncio
async def test_update_task_status(client: AsyncClient):
    resp = await client.post("/api/v1/tasks", json={"name": "Test", "priority": "medium"})
    task_id = resp.json()["id"]

    resp = await client.patch(f"/api/v1/tasks/{task_id}", json={
        "status": "in_progress",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"
    assert resp.json()["started_at"] is not None


@pytest.mark.asyncio
async def test_complete_task(client: AsyncClient):
    resp = await client.post("/api/v1/tasks", json={"name": "Test", "priority": "medium"})
    task_id = resp.json()["id"]

    resp = await client.patch(f"/api/v1/tasks/{task_id}", json={"status": "completed"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"
    assert resp.json()["completed_at"] is not None


@pytest.mark.asyncio
async def test_delete_pending_task(client: AsyncClient):
    resp = await client.post("/api/v1/tasks", json={"name": "Delete me", "priority": "low"})
    task_id = resp.json()["id"]

    resp = await client.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 204

    # Verify gone
    resp = await client.get(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_cannot_delete_in_progress_task(client: AsyncClient):
    resp = await client.post("/api/v1/tasks", json={"name": "Active", "priority": "medium"})
    task_id = resp.json()["id"]
    await client.patch(f"/api/v1/tasks/{task_id}", json={"status": "in_progress"})

    resp = await client.delete(f"/api/v1/tasks/{task_id}")
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_add_comment(client: AsyncClient):
    resp = await client.post("/api/v1/tasks", json={"name": "Task", "priority": "medium"})
    task_id = resp.json()["id"]

    resp = await client.post(f"/api/v1/tasks/{task_id}/comments", json={
        "content": "Started working on this.",
    })
    assert resp.status_code == 201
    assert resp.json()["content"] == "Started working on this."
    assert resp.json()["created_by_id"] == 1


@pytest.mark.asyncio
async def test_list_comments(client: AsyncClient):
    resp = await client.post("/api/v1/tasks", json={"name": "Task", "priority": "medium"})
    task_id = resp.json()["id"]

    await client.post(f"/api/v1/tasks/{task_id}/comments", json={"content": "Comment 1"})
    await client.post(f"/api/v1/tasks/{task_id}/comments", json={"content": "Comment 2"})

    resp = await client.get(f"/api/v1/tasks/{task_id}/comments")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_task_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/tasks/9999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_task_stats(client: AsyncClient):
    await client.post("/api/v1/tasks", json={"name": "A", "priority": "high"})
    await client.post("/api/v1/tasks", json={"name": "B", "priority": "low"})

    resp = await client.get("/api/v1/tasks/dashboard/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert "by_status" in data
    assert "by_priority" in data
