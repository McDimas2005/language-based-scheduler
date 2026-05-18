import pytest
import httpx

from app.main import app


@pytest.mark.anyio
async def test_health_route():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "models" in body


@pytest.mark.anyio
async def test_analyze_text_route_returns_draft():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/analyze-text",
            json={"text": "Create lunch with friends tomorrow at 12"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["needs_user_confirmation"] is True
    assert body["title"] == "Lunch with friends"
    assert body["time"] == "12:00"


@pytest.mark.anyio
async def test_invalid_audio_upload_rejected():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/transcribe",
            files={"file": ("note.txt", b"not audio", "text/plain")},
        )
    assert response.status_code == 400
