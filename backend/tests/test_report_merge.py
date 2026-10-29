import asyncio
from io import BytesIO

import pytest
from starlette.datastructures import UploadFile

from app.api import upload
from app.db.models import UploadAssetORM
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.models import ReportORM
from app.schemas.models import ReportCreateRequest
from app.services import report_service
from app.services.health_workflows import analyze_trends


def test_report_requires_confirmation_and_valid_date():
    with pytest.raises(ValueError, match="确认"):
        report_service.create_report(ReportCreateRequest(name="报告"))
    with pytest.raises(ValueError, match="报告时间"):
        report_service.create_report(ReportCreateRequest(name="报告", confirmed=True, reportTime="bad"))


def test_confirmed_photo_report_preserves_fields_and_supports_trends(monkeypatch):
    engine = create_engine("sqlite://")
    ReportORM.__table__.create(engine)
    sessions = sessionmaker(bind=engine)
    records = []

    def save_record(record):
        record.id = "record-test"
        records.append(record)
        return record

    monkeypatch.setattr(report_service, "SessionLocal", sessions)
    monkeypatch.setattr(report_service.data_store, "create_record", save_record)
    payload = ReportCreateRequest(
        name="报告", confirmed=True, reportTime="2026-10-29 12:00",
        images=[{"name": "报告图片", "url": "/uploads/test.jpg"}],
        ocr={"fields": [{"label": "指标", "value": "1.23", "unit": "mg/L"}]},
    )
    result = report_service.create_report(payload)
    assert result["recordId"] == "record-test"
    assert records[0].date == "2026-10-29"
    assert records[0].status == "已确认"
    assert analyze_trends(records)["trends"][0]["points"][0]["value"] == "1.23"
    with sessions() as session:
        report = session.scalar(select(ReportORM))
        assert report.record_id == "record-test"
        assert "/uploads/test.jpg" in report.images
    engine.dispose()


def test_report_attachment_upload_persists_asset(monkeypatch, tmp_path):
    engine = create_engine("sqlite://")
    UploadAssetORM.__table__.create(engine)
    sessions = sessionmaker(bind=engine)
    monkeypatch.setattr(upload, "SessionLocal", sessions)
    monkeypatch.setattr(upload.settings, "upload_dir", str(tmp_path))
    file = UploadFile(filename="report.txt", file=BytesIO(b"test report"))
    result = asyncio.run(upload.upload_report_file(file))
    assert result["url"].startswith("/uploads/")
    assert (tmp_path / result["filename"]).read_bytes() == b"test report"
    with sessions() as session:
        asset = session.scalar(select(UploadAssetORM))
        assert asset.url == result["url"]
        assert asset.size == 11
    engine.dispose()
