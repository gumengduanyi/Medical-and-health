from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.models import OcrConfirmRequest, OcrConfirmResponse
from app.services.ocr_service import confirm_ocr_result, scan_upload

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post("/reports/scan")
async def scan_report(source_type: str = Form(default="report"), file: UploadFile | None = File(default=None)):
    try:
        return scan_upload(file, source_type=source_type)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PaddleOCR 识别失败: {exc}") from exc


@router.post("/medicines/scan")
async def scan_medicine(file: UploadFile | None = File(default=None)):
    try:
        return scan_upload(file, source_type="medicine")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"PaddleOCR 识别失败: {exc}") from exc


@router.post("/confirm", response_model=OcrConfirmResponse)
def confirm_ocr(payload: OcrConfirmRequest):
    return confirm_ocr_result(payload)
