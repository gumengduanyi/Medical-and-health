from fastapi import APIRouter

from app.schemas.models import HealthProfile
from app.services import data_store

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/profile", response_model=HealthProfile)
def get_profile():
    return data_store.get_profile()


@router.post("/profile", response_model=HealthProfile)
def save_profile(payload: HealthProfile):
    return data_store.save_profile(payload)


@router.get("/records")
def get_records():
    return data_store.list_records()


@router.get("/metrics")
def get_metrics():
    return {
        "bloodPressure": [
            {"day": "一", "value": 62},
            {"day": "二", "value": 68},
            {"day": "三", "value": 74},
            {"day": "四", "value": 71},
            {"day": "五", "value": 82},
            {"day": "六", "value": 78},
            {"day": "日", "value": 86},
        ]
    }
