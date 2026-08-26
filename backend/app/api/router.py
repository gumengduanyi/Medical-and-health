from fastapi import APIRouter

from app.api.ai import router as ai_router
from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.medicines import router as medicines_router
from app.api.ocr import router as ocr_router
from app.api.ping import router as ping_router
from app.api.upload import router as upload_router

api_router = APIRouter()
api_router.include_router(ping_router)
api_router.include_router(auth_router)
api_router.include_router(health_router)
api_router.include_router(medicines_router)
api_router.include_router(ocr_router)
api_router.include_router(ai_router)
api_router.include_router(upload_router)
