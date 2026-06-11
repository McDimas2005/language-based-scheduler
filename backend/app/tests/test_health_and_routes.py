import pytest
import httpx

from app.main import app
from app.core.config import Settings
from app.services.calendar_service import CalendarService


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


def make_calendar_settings(tmp_path):
    return Settings(
        google_client_id="client-id.apps.googleusercontent.com",
        google_client_secret="client-secret",
        google_redirect_uri="http://localhost:8001/api/auth/google/callback",
        google_token_path=tmp_path / "google_token.json",
        frontend_url="http://localhost:5173",
    )


@pytest.mark.anyio
async def test_google_start_redirect_includes_account_chooser(tmp_path, monkeypatch):
    settings = make_calendar_settings(tmp_path)
    services = app.state.services
    monkeypatch.setattr(services, "settings", settings)
    monkeypatch.setattr(services, "calendar_service", CalendarService(settings))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test", follow_redirects=False) as client:
        response = await client.get("/api/auth/google/start")

    assert response.status_code in {302, 307}
    location = response.headers["location"]
    assert "accounts.google.com" in location
    assert "access_type=offline" in location
    assert "include_granted_scopes=true" in location
    assert "prompt=consent+select_account" in location
    assert "https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fcalendar.events" in location
    assert "openid" in location
    assert "email" in location
    assert "profile" in location


@pytest.mark.anyio
async def test_google_status_disconnected(tmp_path, monkeypatch):
    settings = make_calendar_settings(tmp_path)
    services = app.state.services
    monkeypatch.setattr(services, "settings", settings)
    monkeypatch.setattr(services, "calendar_service", CalendarService(settings))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/auth/google/status")

    assert response.status_code == 200
    body = response.json()
    assert body["connected"] is False
    assert body["configured"] is True


@pytest.mark.anyio
async def test_google_logout_disconnected_is_success(tmp_path, monkeypatch):
    settings = make_calendar_settings(tmp_path)
    services = app.state.services
    monkeypatch.setattr(services, "settings", settings)
    monkeypatch.setattr(services, "calendar_service", CalendarService(settings))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/auth/google/logout")

    assert response.status_code == 200
    assert response.json() == {"status": "success", "connected": False}


@pytest.mark.anyio
async def test_calendar_create_requires_google_connection(tmp_path, monkeypatch):
    settings = make_calendar_settings(tmp_path)
    services = app.state.services
    monkeypatch.setattr(services, "settings", settings)
    monkeypatch.setattr(services, "calendar_service", CalendarService(settings))

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/calendar/create-event",
            json={
                "title": "Study session",
                "start_datetime": "2026-06-07T10:00:00+07:00",
                "end_datetime": "2026-06-07T11:00:00+07:00",
                "timezone": "Asia/Jakarta",
            },
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Connect Google Calendar first."


def test_auth_status_refreshes_expired_credentials(tmp_path, monkeypatch):
    settings = make_calendar_settings(tmp_path)
    service = CalendarService(settings)
    settings.google_token_path.write_text(
        """
        {
          "credentials": {
            "token": "old-token",
            "refresh_token": "refresh-token",
            "token_uri": "https://oauth2.googleapis.com/token",
            "client_id": "client-id.apps.googleusercontent.com",
            "client_secret": "client-secret",
            "expiry": "2020-01-01T00:00:00Z",
            "scopes": ["https://www.googleapis.com/auth/calendar.events", "openid", "email", "profile"]
          },
          "account": {"email": "user@example.com", "name": "User Name"}
        }
        """
    )

    def fake_refresh(credentials):
        credentials.token = "new-token"
        credentials.expiry = None

    monkeypatch.setattr(service, "_refresh_credentials", fake_refresh)

    status = service.auth_status()

    assert status.connected is True
    assert status.email == "user@example.com"
    saved = settings.google_token_path.read_text()
    assert "new-token" in saved
