"""
AI Module — Test Suite
TOP WorX ERP System

Tests:
  - Chat endpoint (placeholder response)
  - Predictions endpoint
  - Model listing
  - Content analysis
  - Dashboard
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_ai_chat(client: AsyncClient):
    resp = await client.post("/api/v1/ai/chat", json={
        "message": "What is our current inventory level?",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "reply" in data
    assert "model" in data


@pytest.mark.asyncio
async def test_ai_chat_with_context(client: AsyncClient):
    resp = await client.post("/api/v1/ai/chat", json={
        "message": "Show me sales data",
        "context": "sales",
    })
    assert resp.status_code == 200
    assert "reply" in resp.json()


@pytest.mark.asyncio
async def test_list_ai_models(client: AsyncClient):
    resp = await client.get("/api/v1/ai/models")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check model structure
    model = data[0]
    assert "name" in model
    assert "type" in model
    assert "status" in model


@pytest.mark.asyncio
async def test_generate_prediction(client: AsyncClient):
    resp = await client.post("/api/v1/ai/predictions", json={
        "model_type": "sales",
        "parameters": {"region": "north"},
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["model_type"] == "sales"
    assert "predictions" in data
    assert "confidence" in data


@pytest.mark.asyncio
async def test_analyze_content(client: AsyncClient):
    resp = await client.post("/api/v1/ai/analyze", json={
        "text": "This product is excellent and works perfectly.",
        "analysis_type": "sentiment",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["analysis_type"] == "sentiment"
    assert "result" in data


@pytest.mark.asyncio
async def test_detect_anomalies(client: AsyncClient):
    resp = await client.get("/api/v1/ai/monitoring/anomalies?module=sales")
    assert resp.status_code == 200
    data = resp.json()
    assert data["module"] == "sales"
    assert "anomalies" in data


@pytest.mark.asyncio
async def test_get_recommendations(client: AsyncClient):
    resp = await client.get("/api/v1/ai/recommendations?module=inventory")
    assert resp.status_code == 200
    data = resp.json()
    assert data["module"] == "inventory"
    assert "recommendations" in data


@pytest.mark.asyncio
async def test_ai_dashboard(client: AsyncClient):
    resp = await client.get("/api/v1/ai/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert "models_trained" in data
    assert "openai_configured" in data
