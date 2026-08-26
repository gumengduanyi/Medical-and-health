from fastapi import APIRouter

from app.schemas.models import ChatRequest, ChatResponse
from app.services.ai_service import generate_health_reply, get_daily_advice

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    return generate_health_reply(payload.message, context=payload.context)


@router.get("/advice")
def advice():
    return get_daily_advice()
