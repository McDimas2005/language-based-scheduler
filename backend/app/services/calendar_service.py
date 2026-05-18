from __future__ import annotations

import json
import secrets
from datetime import datetime
from pathlib import Path

from app.core.config import Settings
from app.core.logging import get_logger
from app.models.schemas import (
    CalendarCreateRequest,
    CalendarCreateResponse,
    GoogleAuthStartResponse,
    GoogleAuthStatus,
)


logger = get_logger(__name__)


class CalendarService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._last_state: str | None = None

    def is_configured(self) -> bool:
        return bool(self.settings.google_client_id and self.settings.google_client_secret)

    def auth_status(self) -> GoogleAuthStatus:
        warnings: list[str] = []
        if not self.is_configured():
            warnings.append("Google OAuth is not configured. Add GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET.")
        return GoogleAuthStatus(
            connected=self.settings.google_token_path.exists(),
            configured=self.is_configured(),
            scopes=self.settings.google_scopes,
            warnings=warnings,
        )

    def start_auth(self) -> GoogleAuthStartResponse:
        if not self.is_configured():
            raise RuntimeError("Google OAuth is not configured.")
        try:
            from google_auth_oauthlib.flow import Flow
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Google auth dependencies are not installed: {exc}") from exc

        state = secrets.token_urlsafe(24)
        self._last_state = state
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.settings.google_client_id,
                    "client_secret": self.settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.settings.google_redirect_uri],
                }
            },
            scopes=self.settings.google_scopes,
            state=state,
        )
        flow.redirect_uri = self.settings.google_redirect_uri
        authorization_url, returned_state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return GoogleAuthStartResponse(authorization_url=authorization_url, state=returned_state)

    def finish_auth(self, authorization_response: str, state: str | None) -> None:
        if self._last_state and state and state != self._last_state:
            raise RuntimeError("Google OAuth state mismatch.")
        try:
            from google_auth_oauthlib.flow import Flow
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Google auth dependencies are not installed: {exc}") from exc

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.settings.google_client_id,
                    "client_secret": self.settings.google_client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.settings.google_redirect_uri],
                }
            },
            scopes=self.settings.google_scopes,
            state=state,
        )
        flow.redirect_uri = self.settings.google_redirect_uri
        flow.fetch_token(authorization_response=authorization_response)
        self._save_credentials(flow.credentials)

    def logout(self) -> None:
        self.settings.google_token_path.unlink(missing_ok=True)

    def create_event(self, request: CalendarCreateRequest) -> CalendarCreateResponse:
        credentials = self._load_credentials()
        try:
            from googleapiclient.discovery import build
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Google Calendar dependencies are not installed: {exc}") from exc

        body = {
            "summary": request.title,
            "description": self._description(request),
            "start": {"dateTime": request.start_datetime, "timeZone": request.timezone},
            "end": {"dateTime": request.end_datetime, "timeZone": request.timezone},
        }
        service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
        event = service.events().insert(calendarId="primary", body=body).execute()
        return CalendarCreateResponse(
            calendar_event_id=event["id"],
            html_link=event.get("htmlLink"),
            status="created",
            created_at=datetime.utcnow(),
        )

    def _load_credentials(self):
        if not self.settings.google_token_path.exists():
            raise RuntimeError("Google Calendar is not connected.")
        try:
            from google.oauth2.credentials import Credentials
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Google auth dependencies are not installed: {exc}") from exc
        token_info = json.loads(self.settings.google_token_path.read_text())
        return Credentials.from_authorized_user_info(token_info, scopes=self.settings.google_scopes)

    def _save_credentials(self, credentials) -> None:
        token_path = Path(self.settings.google_token_path)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(credentials.to_json())
        logger.info("Saved Google OAuth token to %s", token_path)

    @staticmethod
    def _description(request: CalendarCreateRequest) -> str:
        parts = []
        if request.description:
            parts.append(request.description)
        if request.category:
            parts.append(f"Category: {request.category}")
        if request.notes:
            parts.append(f"Notes: {request.notes}")
        return "\n\n".join(parts)

