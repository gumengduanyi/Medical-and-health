from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.schemas.models import (
    LeafletDiscoverRequest,
    LeafletDiscoverResponse,
    LeafletImportRequest,
    LeafletImportResponse,
    LeafletReviewRequest,
    UserProfile,
)
from app.services.auth_service import get_current_user
from app.services import leaflet_service

router = APIRouter(prefix="/leaflets", tags=["leaflets"])


@router.post("/auto-discover", response_model=LeafletDiscoverResponse)
def discover_leaflet_candidates(
    payload: LeafletDiscoverRequest,
    current_user: UserProfile = Depends(get_current_user),
):
    try:
        return leaflet_service.discover_leaflet_candidates(payload, owner=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/import-baike", response_model=LeafletImportResponse, status_code=201)
def import_baike_leaflet(
    payload: LeafletImportRequest,
    current_user: UserProfile = Depends(get_current_user),
):
    try:
        return leaflet_service.import_baike_leaflet(payload, owner=current_user.id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[LeafletImportResponse])
def list_leaflets(current_user: UserProfile = Depends(get_current_user)):
    return leaflet_service.list_leaflets()


@router.post("/{leaflet_id}/approve", response_model=LeafletImportResponse)
def approve_leaflet(
    leaflet_id: str,
    payload: LeafletReviewRequest,
    current_user: UserProfile = Depends(get_current_user),
):
    if current_user.id not in settings.leaflet_admin_user_id_list:
        raise HTTPException(status_code=403, detail="当前用户没有说明书审核权限")
    try:
        leaflet = leaflet_service.approve_leaflet(leaflet_id, current_user.id, payload.note)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if leaflet is None:
        raise HTTPException(status_code=404, detail="说明书不存在")
    return leaflet