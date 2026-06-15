from __future__ import annotations

import base64
import json
import os
import secrets
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.request import Request as UrlRequest
from urllib.request import urlopen

from app.core.config import Settings
from app.core.logging import get_logger
from app.models.schemas import (
    CalendarCreateRequest,
    CalendarCreateResponse,
    GoogleAuthStartResponse,
    GoogleAuthStatus,
)


logger = get_logger(__name__)


class GoogleCalendarNotConnectedError(RuntimeError):
    pass


class GoogleCalendarConfigurationError(RuntimeError):
    pass


class GoogleCalendarOAuthError(RuntimeError):
    pass


class CalendarService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._last_state: str | None = None

    def is_configured(self) -> bool:
        return self.settings.google_calendar_configured

    def auth_status(self) -> GoogleAuthStatus:
        warnings: list[str] = []
        configured = self.is_configured()
        if not configured:
            message = "Google Calendar is not configured for this deployment."
            return GoogleAuthStatus(
                connected=False,
                configured=False,
                optional=True,
                message=message,
                scopes=self.settings.google_scopes,
                warnings=warnings,
            )

        try:
            credentials, account = self._get_valid_credentials(required=False)
        except GoogleCalendarOAuthError as exc:
            warnings.append(str(exc))
            return GoogleAuthStatus(
                connected=False,
                configured=configured,
                optional=True,
                scopes=self.settings.google_scopes,
                warnings=warnings,
            )

        return GoogleAuthStatus(
            connected=credentials is not None,
            configured=configured,
            optional=True,
            email=account.get("email"),
            name=account.get("name"),
            picture=account.get("picture"),
            scopes=self.settings.google_scopes,
            warnings=warnings,
        )

    def start_auth(self) -> GoogleAuthStartResponse:
        if not self.is_configured():
            raise GoogleCalendarConfigurationError("Google Calendar is not configured for this deployment.")
        try:
            from google_auth_oauthlib.flow import Flow
        except Exception as exc:  # pragma: no cover
            raise GoogleCalendarConfigurationError(f"Google auth dependencies are not installed: {exc}") from exc

        state = secrets.token_urlsafe(24)
        self._last_state = state
        flow = self._build_flow(state=state)
        authorization_url, returned_state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent select_account",
        )
        return GoogleAuthStartResponse(authorization_url=authorization_url, state=returned_state)

    def finish_auth(self, authorization_response: str, state: str | None) -> None:
        if self._last_state and state and state != self._last_state:
            raise GoogleCalendarOAuthError("Google OAuth state mismatch. Please try signing in again.")
        if not self.is_configured():
            raise GoogleCalendarConfigurationError("Google Calendar is not configured for this deployment.")

        flow = self._build_flow(state=state)
        try:
            flow.fetch_token(authorization_response=authorization_response)
        except Exception as exc:
            logger.warning("Google OAuth token exchange failed: %s", exc)
            raise GoogleCalendarOAuthError("Google sign-in failed. Please try again.") from exc

        credentials = flow.credentials
        account = self._extract_account(credentials)
        self._save_credentials(credentials, account=account)

    def logout(self) -> None:
        self.settings.google_token_path.unlink(missing_ok=True)

    def create_event(self, request: CalendarCreateRequest) -> CalendarCreateResponse:
        if not self.is_configured():
            raise GoogleCalendarConfigurationError(
                "Google Calendar creation is not configured in this deployment. "
                "Event draft generation is still available."
            )
        credentials, _account = self._get_valid_credentials(required=True)
        try:
            from googleapiclient.discovery import build
        except Exception as exc:  # pragma: no cover
            raise GoogleCalendarConfigurationError(f"Google Calendar dependencies are not installed: {exc}") from exc

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

    def _build_flow(self, state: str | None):
        from google_auth_oauthlib.flow import Flow

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
        return flow

    def _get_valid_credentials(self, required: bool):
        if not self.settings.google_token_path.exists():
            if required:
                raise GoogleCalendarNotConnectedError("Connect Google Calendar first.")
            return None, {}

        credentials, account = self._load_credentials()
        if credentials.valid:
            return credentials, account

        if credentials.expired and credentials.refresh_token:
            try:
                self._refresh_credentials(credentials)
            except Exception as exc:
                logger.warning("Google credential refresh failed: %s", exc)
                if required:
                    raise GoogleCalendarOAuthError("Google Calendar access expired. Please sign in again.") from exc
                raise GoogleCalendarOAuthError("Google Calendar access expired. Please sign in again.") from exc
            self._save_credentials(credentials, account=account)
            if credentials.valid:
                return credentials, account

        if required:
            raise GoogleCalendarNotConnectedError("Connect Google Calendar first.")
        return None, account

    def _refresh_credentials(self, credentials) -> None:
        try:
            from google.auth.transport.requests import Request
        except Exception as exc:  # pragma: no cover
            raise GoogleCalendarConfigurationError(f"Google auth dependencies are not installed: {exc}") from exc
        credentials.refresh(Request())

    def _load_credentials(self):
        try:
            from google.oauth2.credentials import Credentials
        except Exception as exc:  # pragma: no cover
            raise GoogleCalendarConfigurationError(f"Google auth dependencies are not installed: {exc}") from exc

        record = json.loads(self.settings.google_token_path.read_text())
        credentials_info = record.get("credentials", record)
        account = record.get("account", {})
        credentials = Credentials.from_authorized_user_info(credentials_info, scopes=self.settings.google_scopes)
        return credentials, account

    def _save_credentials(self, credentials, account: dict[str, str | None] | None = None) -> None:
        token_path = Path(self.settings.google_token_path)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "credentials": json.loads(credentials.to_json()),
            "account": {key: value for key, value in (account or {}).items() if value},
        }
        token_path.write_text(json.dumps(record, indent=2))
        try:
            os.chmod(token_path, 0o600)
        except OSError:
            logger.debug("Could not chmod Google OAuth token file at %s", token_path)
        logger.info("Saved Google OAuth token to %s", token_path)

    def _extract_account(self, credentials) -> dict[str, str | None]:
        account = self._account_from_id_token(getattr(credentials, "id_token", None))
        if account.get("email"):
            return account
        userinfo = self._account_from_userinfo(getattr(credentials, "token", None))
        return {**account, **userinfo}

    def _account_from_id_token(self, token: str | None) -> dict[str, str | None]:
        if not token:
            return {}
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import id_token

            claims = id_token.verify_oauth2_token(token, Request(), self.settings.google_client_id)
        except Exception as exc:
            logger.debug("Could not verify Google id_token for account display: %s", exc)
            claims = self._decode_unverified_jwt(token)
            if claims.get("aud") and claims.get("aud") != self.settings.google_client_id:
                return {}
        return self._account_from_claims(claims)

    def _account_from_userinfo(self, access_token: str | None) -> dict[str, str | None]:
        if not access_token:
            return {}
        request = UrlRequest(
            "https://openidconnect.googleapis.com/v1/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        try:
            with urlopen(request, timeout=5) as response:
                claims = json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            logger.debug("Could not retrieve Google userinfo for account display: %s", exc)
            return {}
        return self._account_from_claims(claims)

    @staticmethod
    def _decode_unverified_jwt(token: str) -> dict[str, Any]:
        try:
            payload = token.split(".")[1]
            padded = payload + "=" * (-len(payload) % 4)
            return json.loads(base64.urlsafe_b64decode(padded.encode("ascii")).decode("utf-8"))
        except Exception:
            return {}

    @staticmethod
    def _account_from_claims(claims: dict[str, Any]) -> dict[str, str | None]:
        return {
            "email": claims.get("email"),
            "name": claims.get("name"),
            "picture": claims.get("picture"),
        }

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
