from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse

from app.api.deps import get_services
from app.models.schemas import (
    CalendarCreateRequest,
    CalendarCreateResponse,
    GoogleAuthStartResponse,
    GoogleAuthStatus,
)


router = APIRouter(prefix="/api", tags=["calendar"])


@router.get("/auth/google/status", response_model=GoogleAuthStatus)
async def google_status(services=Depends(get_services)) -> GoogleAuthStatus:
    return services.calendar_service.auth_status()


@router.get("/auth/google/start", response_model=GoogleAuthStartResponse)
async def google_start(services=Depends(get_services)) -> GoogleAuthStartResponse:
    try:
        return services.calendar_service.start_auth()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/auth/google/callback")
async def google_callback(request: Request, state: str | None = None, services=Depends(get_services)):
    try:
        services.calendar_service.finish_auth(str(request.url), state)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return RedirectResponse(url=f"{services.settings.frontend_url}?google=connected")


@router.post("/auth/google/logout", response_model=GoogleAuthStatus)
async def google_logout(services=Depends(get_services)) -> GoogleAuthStatus:
    services.calendar_service.logout()
    return services.calendar_service.auth_status()


@router.post("/calendar/create-event", response_model=CalendarCreateResponse)
async def create_event(payload: CalendarCreateRequest, services=Depends(get_services)) -> CalendarCreateResponse:
    try:
        return services.calendar_service.create_event(payload)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
