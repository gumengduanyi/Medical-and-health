import json
from datetime import datetime
from uuid import uuid4

from app.db.models import ReportORM
from app.db.session import SessionLocal
from app.schemas.models import MedicalRecord, MedicalRecordItem, ReportCreateRequest
from app.services import data_store


def _build_record_items(payload: ReportCreateRequest) -> list[MedicalRecordItem]:
    items: list[MedicalRecordItem] = []
    for position, field in enumerate(payload.ocr.fields):
        if not isinstance(field, dict):
            continue
        label = str(field.get("label") or field.get("name") or "").strip()
        if not label:
            continue
        items.append(
            MedicalRecordItem(
                position=position,
                label=label,
                value=str(field.get("value") or ""),
                unit=str(field.get("unit") or ""),
                reference=str(field.get("reference") or ""),
                status=str(field.get("status") or "normal"),
            )
        )
    return items


def create_report(payload: ReportCreateRequest) -> dict[str, str]:
    if not payload.confirmed:
        raise ValueError("请核对报告资料后再确认归档")
    try:
        report_date = datetime.fromisoformat(payload.report_time).date().isoformat()
    except ValueError as exc:
        raise ValueError("请按报告填写有效的报告时间") from exc
    report_id = f"report_{uuid4().hex}"
    record = data_store.create_record(
        MedicalRecord(
            title=payload.name,
            date=report_date,
            status="已确认",
            content=payload.remark,
            items=_build_record_items(payload),
        )
    )

    with SessionLocal() as session:
        session.add(
            ReportORM(
                id=report_id,
                name=payload.name,
                category=payload.category,
                entry_time=payload.entry_time,
                report_time=payload.report_time,
                remark=payload.remark,
                images=json.dumps([item.model_dump() for item in payload.images], ensure_ascii=False),
                files=json.dumps([item.model_dump() for item in payload.files], ensure_ascii=False),
                stored_file=payload.ocr.stored_file,
                output_dir=payload.ocr.output_dir,
                record_id=record.id,
            )
        )
        session.commit()

    return {"id": report_id, "recordId": record.id, "message": "报告已保存"}
