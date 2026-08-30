"""
Messages & Notifications Module — Test Suite
TOP WorX ERP System

Tests:
  - Conversations (DM and group)
  - Messages (send, list, read receipts)
  - Notifications (CRUD, unread count)
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


# ── Conversations ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_conversation(client: AsyncClient):
    resp = await client.post("/api/v1/messages/conversations", json={
        "participant_ids": [1, 2],
        "is_group": False,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["is_group"] is False
    assert len(data["participant_ids"]) >= 1  # At least the creator


@pytest.mark.asyncio
async def test_create_group_conversation(client: AsyncClient):
    resp = await client.post("/api/v1/messages/conversations", json={
        "title": "Project Alpha",
        "participant_ids": [1, 2, 3],
        "is_group": True,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Project Alpha"
    assert data["is_group"] is True


@pytest.mark.asyncio
async def test_list_conversations(client: AsyncClient):
    await client.post("/api/v1/messages/conversations", json={
        "participant_ids": [1],
    })

    resp = await client.get("/api/v1/messages/conversations")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_get_conversation(client: AsyncClient):
    resp = await client.post("/api/v1/messages/conversations", json={
        "participant_ids": [1],
    })
    conv_id = resp.json()["id"]

    resp = await client.get(f"/api/v1/messages/conversations/{conv_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == conv_id


# ── Messages ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_send_message(client: AsyncClient):
    resp = await client.post("/api/v1/messages/conversations", json={
        "participant_ids": [1],
    })
    conv_id = resp.json()["id"]

    resp = await client.post(f"/api/v1/messages/conversations/{conv_id}/messages", json={
        "content": "Hello, team!",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["content"] == "Hello, team!"
    assert data["sender_id"] == 1


@pytest.mark.asyncio
async def test_list_messages(client: AsyncClient):
    resp = await client.post("/api/v1/messages/conversations", json={
        "participant_ids": [1],
    })
    conv_id = resp.json()["id"]

    await client.post(f"/api/v1/messages/conversations/{conv_id}/messages", json={
        "content": "Message 1",
    })
    await client.post(f"/api/v1/messages/conversations/{conv_id}/messages", json={
        "content": "Message 2",
    })

    resp = await client.get(f"/api/v1/messages/conversations/{conv_id}/messages")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_mark_conversation_read(client: AsyncClient):
    resp = await client.post("/api/v1/messages/conversations", json={
        "participant_ids": [1],
    })
    conv_id = resp.json()["id"]

    resp = await client.post(f"/api/v1/messages/conversations/{conv_id}/read")
    assert resp.status_code == 200
    assert resp.json()["status"] == "read"


# ── Notifications ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_notification(client: AsyncClient):
    resp = await client.post("/api/v1/messages/notifications", json={
        "user_id": 1,
        "title": "New task assigned",
        "message": "You have been assigned to Task #42.",
        "severity": "info",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "New task assigned"
    assert data["is_read"] is False


@pytest.mark.asyncio
async def test_list_notifications(client: AsyncClient):
    await client.post("/api/v1/messages/notifications", json={
        "user_id": 1, "title": "N1", "message": "M1",
    })
    await client.post("/api/v1/messages/notifications", json={
        "user_id": 1, "title": "N2", "message": "M2",
    })

    resp = await client.get("/api/v1/messages/notifications")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


@pytest.mark.asyncio
async def test_mark_notification_read(client: AsyncClient):
    resp = await client.post("/api/v1/messages/notifications", json={
        "user_id": 1, "title": "Read me", "message": "Msg",
    })
    notif_id = resp.json()["id"]

    resp = await client.post(f"/api/v1/messages/notifications/{notif_id}/read")
    assert resp.status_code == 200
    assert resp.json()["status"] == "read"


@pytest.mark.asyncio
async def test_mark_all_notifications_read(client: AsyncClient):
    await client.post("/api/v1/messages/notifications", json={
        "user_id": 1, "title": "N1", "message": "M1",
    })
    await client.post("/api/v1/messages/notifications", json={
        "user_id": 1, "title": "N2", "message": "M2",
    })

    resp = await client.post("/api/v1/messages/notifications/read-all")
    assert resp.status_code == 200
    assert resp.json()["marked_read"] == 2


@pytest.mark.asyncio
async def test_unread_notification_count(client: AsyncClient):
    await client.post("/api/v1/messages/notifications", json={
        "user_id": 1, "title": "N1", "message": "M1",
    })
    await client.post("/api/v1/messages/notifications", json={
        "user_id": 1, "title": "N2", "message": "M2",
    })

    resp = await client.get("/api/v1/messages/notifications/unread-count")
    assert resp.status_code == 200
    assert resp.json()["unread_count"] == 2


@pytest.mark.asyncio
async def test_unread_count_after_read(client: AsyncClient):
    resp = await client.post("/api/v1/messages/notifications", json={
        "user_id": 1, "title": "N1", "message": "M1",
    })
    notif_id = resp.json()["id"]

    await client.post(f"/api/v1/messages/notifications/{notif_id}/read")

    resp = await client.get("/api/v1/messages/notifications/unread-count")
    assert resp.json()["unread_count"] == 0
