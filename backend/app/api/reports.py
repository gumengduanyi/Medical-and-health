from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.schemas.models import ReportCreateRequest, ReportCreateResponse, ReportSummary
from app.services.report_service import create_report, list_report_entries

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", response_model=list[ReportSummary])
def list_reports(category: Optional[str] = Query(default=None)):
    return list_report_entries(category)


@router.post("", response_model=ReportCreateResponse)
def submit_report(payload: ReportCreateRequest):
    if not payload.name.strip():
        raise HTTPException(status_code=400, detail="报告名称不能为空")
    return create_report(payload)
