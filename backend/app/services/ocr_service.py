from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import textwrap
import time
from pathlib import Path
from typing import Any

from fastapi import UploadFile

from app.core.config import settings
from app.schemas.models import MedicalRecord, Medicine, OcrConfirmRequest, OcrConfirmResponse
from app.services import data_store


def _safe_filename(name: str | None) -> str:
    suffix = Path(name or "upload.jpg").suffix.lower() or ".jpg"
    if suffix not in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
        suffix = ".jpg"
    return f"ocr_{int(time.time() * 1000)}{suffix}"


def _save_upload(file: UploadFile) -> Path:
    output_dir = Path(settings.ocr_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / _safe_filename(file.filename)
    with image_path.open("wb") as target:
        shutil.copyfileobj(file.file, target)
    return image_path


def _run_ppstructure(image_path: Path) -> dict[str, Any]:
    script = textwrap.dedent(
        """
        import json
        import sys
        from pathlib import Path

        import cv2
        from paddleocr import PPStructureV3


        def safe_call(obj, method_name, *args):
            method = getattr(obj, method_name, None)
            if not callable(method):
                return False
            try:
                method(*args)
                return True
            except Exception:
                return False


        image_path = Path(sys.argv[1])
        output_dir = Path(sys.argv[2])
        visual_dir = output_dir / 'visual'
        visual_dir.mkdir(parents=True, exist_ok=True)

        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f'图片读取失败: {image_path}')

        engine = PPStructureV3(
            use_table_recognition=True,
            use_doc_orientation_classify=True,
            use_doc_unwarping=True,
        )
        result = engine.predict(
            image,
            use_table_recognition=True,
            use_doc_orientation_classify=True,
            use_doc_unwarping=True,
            use_e2e_wireless_table_rec_model=True,
        )

        first = result[0] if result else None
        if first is not None:
            safe_call(first, 'save_to_img', str(visual_dir))
            safe_call(first, 'save_to_html', str(visual_dir))
            safe_call(first, 'save_to_xlsx', str(visual_dir))

        serializable = json.loads(json.dumps(result, ensure_ascii=False, default=str))
        print(json.dumps(serializable, ensure_ascii=False))
        """
    )
    output_dir = image_path.parent / f"{image_path.stem}_structure"
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".py", encoding="utf-8", delete=False) as script_file:
        script_file.write(script)
        script_path = Path(script_file.name)

    try:
        completed = subprocess.run(
            [settings.ocr_python, str(script_path), str(image_path), str(output_dir)],
            capture_output=True,
            text=True,
            timeout=settings.ocr_timeout_seconds,
            check=True,
        )
    finally:
        script_path.unlink(missing_ok=True)

    stdout = completed.stdout.strip().splitlines()
    if not stdout:
        raise RuntimeError("PaddleOCR 没有返回识别结果")
    return {"raw": json.loads(stdout[-1]), "output_dir": str(output_dir)}


def _extract_texts(page: dict[str, Any]) -> list[str]:
    texts = page.get("overall_ocr_res", {}).get("rec_texts", [])
    return [str(text).strip() for text in texts if str(text).strip()]


def _extract_layout_boxes(page: dict[str, Any]) -> list[dict[str, Any]]:
    boxes = page.get("layout_det_res", {}).get("boxes", [])
    return [
        {
            "label": str(item.get("label", "")),
            "score": round(float(item.get("score", 0.0)), 3),
            "coordinate": item.get("coordinate", []),
        }
        for item in boxes
        if isinstance(item, dict)
    ]


def _field_status(label: str, value: str, reference: str = "") -> str:
    try:
        number = float(value.replace("<", "").replace(",", ""))
    except ValueError:
        return "normal"

    match = re.search(r"([0-9.]+)\s*[~～-]\s*([0-9.]+)", reference)
    if not match:
        return "warning" if any(key in label for key in ("血压", "血糖", "胆固醇")) else "normal"
    low, high = float(match.group(1)), float(match.group(2))
    return "warning" if number < low or number > high else "normal"


def _extract_report_fields(texts: list[str]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for index, text in enumerate(texts):
        value = ""
        reference = ""
        if index + 1 < len(texts) and re.fullmatch(r"<?[0-9]+(?:\.[0-9]+)?", texts[index + 1]):
            value = texts[index + 1]
        if index + 2 < len(texts) and re.search(r"[0-9.]+\s*[~～-]\s*[0-9.]+", texts[index + 2]):
            reference = texts[index + 2]
        if value and re.search(r"[\u4e00-\u9fff]", text):
            fields.append(
                {
                    "label": text,
                    "value": value,
                    "reference": reference,
                    "status": _field_status(text, value, reference),
                }
            )
        if len(fields) >= 20:
            break
    return fields


def _extract_medicine_fields(texts: list[str]) -> list[dict[str, Any]]:
    joined = " ".join(texts)
    fields = []
    if texts:
        fields.append({"label": "识别文本", "value": joined[:120], "status": "pending"})
    for keyword in ("用法", "用量", "规格", "有效期", "生产日期", "批准文号"):
        match = next((text for text in texts if keyword in text), "")
        if match:
            fields.append({"label": keyword, "value": match, "status": "pending"})
    return fields[:8]


def scan_upload(file: UploadFile, source_type: str = "report") -> dict[str, Any]:
    if file is None:
        raise ValueError("请上传需要识别的图片")

    image_path = _save_upload(file)
    result = _run_ppstructure(image_path)
    pages = result["raw"]
    page = pages[0] if pages else {}
    texts = _extract_texts(page)
    boxes = _extract_layout_boxes(page)
    table_scores = [box["score"] for box in boxes if box["label"] == "table"]
    fields = _extract_medicine_fields(texts) if source_type == "medicine" else _extract_report_fields(texts)
    confidence = round(max(table_scores or [0]) * 100)

    return {
        "id": image_path.stem,
        "sourceType": source_type,
        "confidence": confidence,
        "fields": fields,
        "texts": texts,
        "layout": boxes,
        "page": {
            "width": page.get("width"),
            "height": page.get("height"),
            "angle": page.get("doc_preprocessor_res", {}).get("angle"),
        },
        "file": file.filename or image_path.name,
        "storedFile": str(image_path),
        "outputDir": result["output_dir"],
        "message": "PaddleOCR PPStructureV3 识别完成，请核对后再入库。",
    }


def _field_value(fields: list[dict[str, Any]], labels: tuple[str, ...]) -> str:
    for field in fields:
        label = str(field.get("label", ""))
        if any(name in label for name in labels):
            return str(field.get("value", "")).strip()
    return ""


def _record_content(payload: OcrConfirmRequest) -> str:
    lines = []
    for field in payload.fields:
        label = str(field.get("label", "")).strip()
        value = str(field.get("value", "")).strip()
        reference = str(field.get("reference", "")).strip()
        status = str(field.get("status", "")).strip()
        if label and value:
            suffix = f"，参考范围 {reference}" if reference else ""
            warning = "，需关注" if status == "warning" else ""
            lines.append(f"{label}：{value}{suffix}{warning}")
    if not lines and payload.texts:
        lines = payload.texts[:20]

    source_note = f"来源图片：{payload.stored_file}" if payload.stored_file else "来源：OCR 上传识别"
    return "；".join(lines + [source_note])


def confirm_ocr_result(payload: OcrConfirmRequest) -> OcrConfirmResponse:
    source_type = payload.source_type
    if source_type == "medicine":
        joined_text = " ".join(payload.texts)
        name = _field_value(payload.fields, ("药品名称", "识别文本")) or (payload.texts[0] if payload.texts else "OCR 识别药品")
        medicine = data_store.create_medicine(
            Medicine(
                name=name[:80],
                dose=_field_value(payload.fields, ("用法", "用量", "规格")),
                stock=0,
                expire=_field_value(payload.fields, ("有效期", "生产日期")),
                risk=f"OCR 确认入库，原文：{joined_text[:120]}",
            )
        )
        return OcrConfirmResponse(sourceType="medicine", medicine=medicine, message="OCR 药品信息已确认入库。")

    title = payload.title or "OCR 识别报告"
    record = data_store.create_record(
        MedicalRecord(
            title=title[:80],
            date=time.strftime("%Y-%m-%d"),
            status="已确认",
            content=_record_content(payload),
        )
    )
    return OcrConfirmResponse(sourceType=source_type, record=record, message="OCR 报告已确认入库。")