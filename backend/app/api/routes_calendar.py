from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.api.deps import get_services
from app.models.schemas import (
    CalendarCreateRequest,
    CalendarCreateResponse,
    GoogleAuthStatus,
    GoogleLogoutResponse,
)
from app.services.calendar_service import (
    GoogleCalendarConfigurationError,
    GoogleCalendarNotConnectedError,
    GoogleCalendarOAuthError,
)


router = APIRouter(prefix="/api", tags=["calendar"])


@router.get("/auth/google/status", response_model=GoogleAuthStatus)
async def google_status(services=Depends(get_services)) -> GoogleAuthStatus:
    return services.calendar_service.auth_status()


@router.get("/auth/google/start")
async def google_start(services=Depends(get_services)) -> RedirectResponse:
    try:
        response = services.calendar_service.start_auth()
    except GoogleCalendarConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return RedirectResponse(url=response.authorization_url)


@router.get("/auth/google/callback")
async def google_callback(request: Request, state: str | None = None, services=Depends(get_services)):
    try:
        services.calendar_service.finish_auth(str(request.url), state)
    except (GoogleCalendarConfigurationError, GoogleCalendarOAuthError, RuntimeError) as exc:
        query = urlencode({"auth": "error", "message": str(exc)})
        return RedirectResponse(url=f"{services.settings.frontend_url}?{query}")
    query = urlencode({"auth": "success"})
    return RedirectResponse(url=f"{services.settings.frontend_url}?{query}")


@router.post("/auth/google/logout", response_model=GoogleLogoutResponse)
async def google_logout(services=Depends(get_services)) -> GoogleLogoutResponse:
    services.calendar_service.logout()
    return GoogleLogoutResponse(status="success", connected=False)


@router.post("/calendar/create-event", response_model=CalendarCreateResponse)
async def create_event(payload: CalendarCreateRequest, services=Depends(get_services)) -> CalendarCreateResponse:
    try:
        return services.calendar_service.create_event(payload)
    except GoogleCalendarNotConnectedError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except GoogleCalendarOAuthError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    except GoogleCalendarConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
