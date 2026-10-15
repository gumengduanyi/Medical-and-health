from fastapi import APIRouter, HTTPException

from app.schemas.models import (
    LeafletDiscoverRequest,
    LeafletDiscoverResponse,
    LeafletImportRequest,
    LeafletImportResponse,
)
from app.services import leaflet_service

router = APIRouter(prefix="/leaflets", tags=["leaflets"])


@router.post("/auto-discover", response_model=LeafletDiscoverResponse)
def discover_leaflet_candidates(payload: LeafletDiscoverRequest):
    try:
        return leaflet_service.discover_leaflet_candidates(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/import-baike", response_model=LeafletImportResponse, status_code=201)
def import_baike_leaflet(payload: LeafletImportRequest):
    try:
        return leaflet_service.import_baike_leaflet(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[LeafletImportResponse])
def list_leaflets():
    return leaflet_service.list_leaflets()


@router.post("/{leaflet_id}/approve", response_model=LeafletImportResponse)
def approve_leaflet(leaflet_id: str):
    try:
        leaflet = leaflet_service.approve_leaflet(leaflet_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if leaflet is None:
        raise HTTPException(status_code=404, detail="说明书不存在")
    return leaflet