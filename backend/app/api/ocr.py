from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.schemas.models import OcrConfirmRequest, OcrConfirmResponse
from app.services.ocr_service import confirm_ocr_result, get_scan_job, submit_scan_job

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("/reports/scan", status_code=status.HTTP_202_ACCEPTED)
async def scan_report(source_type: str = Form(default="report"), file: UploadFile | None = File(default=None)):
    try:
        return submit_scan_job(file, source_type=source_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/medicines/scan", status_code=status.HTTP_202_ACCEPTED)
async def scan_medicine(file: UploadFile | None = File(default=None)):
    try:
        return submit_scan_job(file, source_type="medicine")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/jobs/{job_id}")
def get_ocr_job(job_id: str):
    try:
        return get_scan_job(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="OCR 任务不存在") from exc


@router.post("/confirm", response_model=OcrConfirmResponse)
def confirm_ocr(payload: OcrConfirmRequest):
    return confirm_ocr_result(payload)
