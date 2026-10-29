from fastapi import APIRouter, HTTPException

from app.schemas.models import ReportCreateRequest, ReportCreateResponse
from app.services.report_service import create_report

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("", response_model=ReportCreateResponse)
def submit_report(payload: ReportCreateRequest):
    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="报告名称不能为空")
    try:
        return create_report(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
