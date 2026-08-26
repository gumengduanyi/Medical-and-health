from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/ping")
def ping():
    return {
        "message": "pong",
        "service": settings.app_name,
        "env": settings.app_env,
    }
