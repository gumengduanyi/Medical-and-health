from __future__ import annotations

import json
import re
import subprocess
import tempfile
import textwrap
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

from fastapi import UploadFile

from app.core.config import settings
from app.schemas.models import MedicalRecord, MedicalRecordItem, Medicine, OcrConfirmRequest, OcrConfirmResponse
from app.services import data_store
from app.services.upload_service import detect_image_type


OCR_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="ocr-job")
OCR_JOBS: dict[str, dict[str, Any]] = {}
OCR_JOBS_LOCK = Lock()
MAX_OCR_IMAGE_SIZE = 15 * 1024 * 1024
OCR_EXTENSIONS = {
    "jpeg": ".jpg",
    "png": ".png",
    "gif": ".gif",
    "webp": ".webp",
    "heic": ".heic",
}


def _safe_filename(name: str | None, detected_type: str = "jpeg") -> str:
    suffix = Path(name or "upload.jpg").suffix.lower()
    expected = OCR_EXTENSIONS.get(detected_type, ".jpg")
    allowed = {expected, ".jpeg" if expected == ".jpg" else expected}
    if suffix not in allowed:
        suffix = expected
    return f"ocr_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}{suffix}"


def _save_upload(file: UploadFile) -> Path:
    if file is None:
        raise ValueError("请上传需要识别的图片")

    content = file.file.read()
    if not content:
        raise ValueError("上传的图片为空")
    if len(content) > MAX_OCR_IMAGE_SIZE:
        raise ValueError("图片大小不能超过 15MB")

    detected_type = detect_image_type(content)
    if detected_type is None:
        raise ValueError("仅支持有效图片文件")

    output_dir = Path(settings.ocr_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    image_path = output_dir / _safe_filename(file.filename, detected_type)
    image_path.write_bytes(content)
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

        # OCR 对小字和低对比度照片更敏感，先做轻量放大和局部对比度增强。
        height, width = image.shape[:2]
        if max(height, width) < 2400:
            scale = min(2.0, 2400 / max(height, width))
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        lightness, a_channel, b_channel = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        image = cv2.cvtColor(cv2.merge((clahe.apply(lightness), a_channel, b_channel)), cv2.COLOR_LAB2BGR)

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
            check=False,
        )
    finally:
        script_path.unlink(missing_ok=True)

    if completed.returncode != 0:
        error_output = (completed.stderr or completed.stdout or "").strip()
        detail = error_output[-2000:] if error_output else "无错误输出"
        raise RuntimeError(f"OCR 引擎执行失败（退出码 {completed.returncode}）：{detail}")

    stdout = completed.stdout.strip().splitlines()
    if not stdout:
        raise RuntimeError("PaddleOCR 没有返回识别结果")
    return {"raw": json.loads(stdout[-1]), "output_dir": str(output_dir)}


def _extract_texts(page: dict[str, Any]) -> list[str]:
    texts = page.get("overall_ocr_res", {}).get("rec_texts", [])
    cleaned: list[str] = []
    for text in texts:
        value = re.sub(r"\s+", " ", str(text)).strip()
        if value and value not in cleaned:
            cleaned.append(value)
    return cleaned


def _normalise_generated_html(output_dir: str) -> None:
    header = """
<thead><tr>
<th>指标名称</th><th>检测值</th><th>异常标记</th><th>参考范围</th><th>单位</th>
</tr></thead>""".strip()
    style = """
<meta charset="utf-8"><style>
body { margin: 24px; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif; color: #17231F; }
table { border-collapse: collapse; min-width: 860px; width: 100%; }
th, td { border: 1px solid #DDE7E1; padding: 10px 12px; text-align: left; }
th { background: #E1F3ED; color: #0E7F72; font-weight: 600; }
tr:nth-child(even) td { background: #F7FBF9; }
</style>""".strip()
    for html_path in Path(output_dir).rglob("*.html"):
        content = html_path.read_text(encoding="utf-8")
        if "<thead>" not in content and "<table>" in content:
            content = content.replace("<table>", f"<table>{header}", 1)
        if "<meta charset=" not in content and "<html><body>" in content:
            content = content.replace("<html><body>", f"<html><head>{style}</head><body>", 1)
        html_path.write_text(content, encoding="utf-8")


def _extract_ocr_scores(page: dict[str, Any]) -> list[float]:
    scores = page.get("overall_ocr_res", {}).get("rec_scores", [])
    values = []
    for score in scores:
        try:
            values.append(float(score))
        except (TypeError, ValueError):
            continue
    return values


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

    match = re.search(r"([0-9.,]+)\s*[~～至-]\s*([0-9.,]+)", reference)
    if not match:
        return "warning" if any(key in label for key in ("血压", "血糖", "胆固醇")) else "normal"
    low, high = float(match.group(1).replace(",", "")), float(match.group(2).replace(",", ""))
    return "warning" if number < low or number > high else "normal"


_NUMERIC_VALUE = re.compile(r"^[<≤>]?[0-9]+(?:[.,][0-9]+)?$")
_REFERENCE_RANGE = re.compile(r"[<≤>]?[0-9.,]+\s*[~～至-]\s*[<≤>]?[0-9.,]+")


def _numeric_token(text: str) -> bool:
    return bool(_NUMERIC_VALUE.fullmatch(text.strip()))


def _reference_token(text: str) -> bool:
    return bool(_REFERENCE_RANGE.search(text.strip()))


def _normalise_unit(text: str) -> str:
    return re.sub(r"\s+", "", text).strip()


def _unit_token(text: str) -> bool:
    value = _normalise_unit(text)
    return bool(value) and not re.search(r"[\u4e00-\u9fff]", value) and bool(
        re.fullmatch(r"[A-Za-zμΩ%/·^0-9-]+", value)
    )


def _field_from_inline_text(text: str) -> tuple[str, str, str, str] | None:
    match = re.search(
        r"(?P<label>[\u4e00-\u9fff][\u4e00-\u9fff()（）0-9A-Za-z+\- ]{1,40}?)\s*"
        r"(?P<value>[<≤>]?[0-9]+(?:[.,][0-9]+)?)\s*"
        r"(?:↑|↓|高|低)?\s*"
        r"(?P<reference>[0-9.,]+\s*[~～至-]\s*[0-9.,]+)?\s*"
        r"(?P<unit>[A-Za-zμΩ%/·^0-9-]+)?",
        text,
    )
    if not match:
        return None
    return (
        match.group("label").strip(),
        match.group("value").strip(),
        (match.group("reference") or "").strip(),
        _normalise_unit(match.group("unit") or ""),
    )


def _extract_report_fields(texts: list[str]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    for index, text in enumerate(texts):
        inline = _field_from_inline_text(text)
        label = text
        value = ""
        reference = ""
        unit = ""
        if inline:
            label, value, reference, unit = inline
        else:
            for offset in range(1, min(5, len(texts) - index)):
                candidate = texts[index + offset]
                if (
                    re.search(r"[\u4e00-\u9fff]", candidate)
                    and not _numeric_token(candidate)
                    and not _reference_token(candidate)
                ):
                    break
                if not value and _numeric_token(candidate):
                    value = candidate
                if _reference_token(candidate):
                    reference = candidate
                    if index + offset + 1 < len(texts) and _unit_token(texts[index + offset + 1]):
                        unit = _normalise_unit(texts[index + offset + 1])
                    break
        if value and re.search(r"[\u4e00-\u9fff]", label):
            fields.append(
                {
                    "label": label,
                    "value": value,
                    "reference": reference,
                    "unit": unit,
                    "status": _field_status(label, value, reference),
                }
            )
        if len(fields) >= 100:
            break
    return fields


def _extract_medicine_fields(texts: list[str]) -> list[dict[str, Any]]:
    fields: list[dict[str, Any]] = []
    labelled_keywords = ("药品名称", "通用名称", "商品名称", "用法用量", "用法", "用量", "规格", "有效期", "生产日期", "批准文号")

    def add_field(label: str, value: str) -> None:
        value = re.sub(r"\s+", " ", value).strip(" ：:：")
        if value and not any(item["label"] == label for item in fields):
            fields.append({"label": label, "value": value, "status": "pending"})

    for text in texts:
        for keyword in labelled_keywords:
            match = re.search(rf"{re.escape(keyword)}\s*[：:]?\s*(.+)", text)
            if match:
                add_field(keyword, match.group(1))
                break

    name_field = next((item for item in fields if item["label"] in ("药品名称", "通用名称", "商品名称")), None)
    if name_field is None:
        ignored = ("用法", "用量", "规格", "有效期", "生产日期", "批准文号", "注意事项", "禁忌")
        candidate = next(
            (text for text in texts if len(text) >= 2 and not text.isdigit() and not any(keyword in text for keyword in ignored)),
            "",
        )
        if candidate:
            add_field("药品名称", candidate[:80])

    if texts:
        add_field("识别文本", " ".join(texts)[:240])
    return fields[:10]


def _scan_image_path(image_path: Path, original_filename: str = "", source_type: str = "report") -> dict[str, Any]:
    result = _run_ppstructure(image_path)
    pages = result["raw"]
    page = pages[0] if pages else {}
    texts = _extract_texts(page)
    ocr_scores = _extract_ocr_scores(page)
    boxes = _extract_layout_boxes(page)
    table_scores = [box["score"] for box in boxes if box["label"] == "table"]
    fields = _extract_medicine_fields(texts) if source_type == "medicine" else _extract_report_fields(texts)
    score_groups = [score for score in ocr_scores if score > 0]
    if score_groups:
        confidence = round(sum(score_groups) / len(score_groups) * 100)
    elif table_scores:
        confidence = round(sum(table_scores) / len(table_scores) * 100)
    else:
        confidence = 0

    _normalise_generated_html(result["output_dir"])
    return {
        "id": image_path.stem,
        "sourceType": source_type,
        "confidence": confidence,
        "fields": fields,
        "texts": texts,
        "layout": boxes,
        "ocrScores": [round(score, 3) for score in ocr_scores[:200]],
        "page": {
            "width": page.get("width"),
            "height": page.get("height"),
            "angle": page.get("doc_preprocessor_res", {}).get("angle"),
        },
        "file": original_filename or image_path.name,
        "storedFile": str(image_path),
        "outputDir": result["output_dir"],
        "message": "PaddleOCR PPStructureV3 识别完成，请核对后再入库。",
    }


def scan_upload(file: UploadFile, source_type: str = "report") -> dict[str, Any]:
    image_path = _save_upload(file)
    return _scan_image_path(image_path, file.filename or image_path.name, source_type)


def _utc_now() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _update_job(job_id: str, **changes: Any) -> None:
    with OCR_JOBS_LOCK:
        OCR_JOBS[job_id].update(changes)


def _run_scan_job(job_id: str, image_path: Path, original_filename: str, source_type: str) -> None:
    _update_job(job_id, status="processing", startedAt=_utc_now(), message="OCR 识别中")
    try:
        result = _scan_image_path(image_path, original_filename, source_type)
    except Exception as exc:
        _update_job(job_id, status="failed", error=str(exc), completedAt=_utc_now(), message="OCR 识别失败")
        return
    _update_job(job_id, status="succeeded", result=result, completedAt=_utc_now(), message="OCR 识别完成")


def submit_scan_job(file: UploadFile, source_type: str = "report") -> dict[str, Any]:
    image_path = _save_upload(file)
    job_id = uuid.uuid4().hex
    job = {
        "jobId": job_id,
        "status": "queued",
        "sourceType": source_type,
        "createdAt": _utc_now(),
        "message": "OCR 任务已创建",
    }
    with OCR_JOBS_LOCK:
        OCR_JOBS[job_id] = job
    OCR_EXECUTOR.submit(_run_scan_job, job_id, image_path, file.filename or image_path.name, source_type)
    return job.copy()


def get_scan_job(job_id: str) -> dict[str, Any]:
    with OCR_JOBS_LOCK:
        job = OCR_JOBS.get(job_id)
        if job is None:
            raise KeyError(job_id)
        return job.copy()


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


def _record_items(payload: OcrConfirmRequest) -> list[MedicalRecordItem]:
    items: list[MedicalRecordItem] = []
    for field in payload.fields:
        label = str(field.get("label", "")).strip()
        value = str(field.get("value", "")).strip()
        if not label or not value or label == "识别文本":
            continue
        items.append(
            MedicalRecordItem(
                label=label,
                value=value,
                unit=str(field.get("unit", "")).strip(),
                reference=str(field.get("reference", "")).strip(),
                status=str(field.get("status", "normal")).strip() or "normal",
            )
        )
    return items


def confirm_ocr_result(payload: OcrConfirmRequest) -> OcrConfirmResponse:
    source_type = payload.source_type
    if not payload.fields and not payload.texts:
        raise ValueError("没有可确认的 OCR 结果")
    if source_type == "medicine":
        joined_text = " ".join(payload.texts)
        name = _field_value(payload.fields, ("药品名称", "通用名称", "商品名称"))
        if not name:
            name = next((field.get("value", "") for field in payload.fields if field.get("label") != "识别文本"), "")
        name = str(name).strip() or (payload.texts[0] if payload.texts else "OCR 识别药品")
        medicine = data_store.create_medicine(
            Medicine(
                name=name[:80],
                dose=_field_value(payload.fields, ("用法用量", "用法", "用量", "规格")),
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
            items=_record_items(payload),
        )
    )
    return OcrConfirmResponse(sourceType=source_type, record=record, message="OCR 报告已确认入库。")