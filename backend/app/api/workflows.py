from datetime import date
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.schemas.models import Medicine, MedicalRecord
from app.services.auth_service import get_current_user
from app.services.health_workflows import verify_fields, inspect_cabinet, analyze_trends

router = APIRouter(prefix="/workflows", tags=["workflows"], dependencies=[Depends(get_current_user)])


class VerificationRequest(BaseModel):
    fields: list[dict[str, Any]] = Field(default_factory=list, max_length=1000)


class CabinetRequest(BaseModel):
    medicines: list[Medicine] = Field(default_factory=list, max_length=500)
    as_of: date = Field(default_factory=date.today)
    low_stock: int = Field(default=3, ge=0)
    expiry_days: int = Field(default=30, ge=0, le=3650)


class TrendRequest(BaseModel):
    records: list[MedicalRecord] = Field(default_factory=list, max_length=500)


@router.post("/verify")
def verify(payload: VerificationRequest):
    return verify_fields(payload.fields)


@router.post("/cabinet")
def cabinet(payload: CabinetRequest):
    return inspect_cabinet(payload.medicines, payload.as_of, payload.low_stock, payload.expiry_days)


@router.post("/trends")
def trends(payload: TrendRequest):
    return analyze_trends(payload.records)


@router.get("/sources")
def sources():
    return {"sources": [
        {"id": "baike", "authority": "encyclopedia", "mode": "browser_candidate", "url": "https://baike.baidu.com"},
        {"id": "nmpa", "authority": "regulator", "mode": "manual_identity_lookup", "status": "access_unverified", "url": "https://www.nmpa.gov.cn/datasearch/home-index.html"},
        {"id": "novartis", "authority": "manufacturer", "mode": "reference_only", "status": "professional_audience_terms_need_review", "url": "https://www.e-leaflet-novartis.com.cn/#/pc"},
    ]}
