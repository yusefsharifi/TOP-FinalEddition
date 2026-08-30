"""Tests for AI Assistant endpoints."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_conversation(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/assistant/conversations", json={
        "title": "گفتگوی تست",
        "module": "inventory",
    }, headers=auth_headers)
    assert resp.status_code in (200, 201)


@pytest.mark.asyncio
async def test_list_conversations(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/assistant/conversations", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_send_message(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/api/v1/ai/assistant/chat", json={
        "message": "وضعیت انبار چطوره؟",
        "module": "inventory",
    }, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data or "content" in data


@pytest.mark.asyncio
async def test_get_conversation_messages(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/api/v1/ai/assistant/conversations/1/messages", headers=auth_headers)
    assert resp.status_code in (200, 404)


@pytest.mark.asyncio
async def test_delete_conversation(client: AsyncClient, auth_headers: dict):
    resp = await client.delete("/api/v1/ai/assistant/conversations/1", headers=auth_headers)
    assert resp.status_code in (200, 204, 404)
