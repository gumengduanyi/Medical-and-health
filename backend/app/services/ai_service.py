from app.schemas.models import ChatResponse
from app.services.rag_service import generate_health_reply as rag_generate_health_reply


def generate_health_reply(message: str, context: dict | None = None) -> ChatResponse:
    return rag_generate_health_reply(message, context=context)


def get_daily_advice() -> list[str]:
    return [
        "血压连续偏高，建议低盐饮食并规律监测。",
        "阿司匹林库存偏低，建议 3 天内补货。",
        "完善过敏史后，AI 用药建议会更准确。",
    ]
