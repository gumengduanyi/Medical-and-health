from datetime import date
from concurrent.futures import ThreadPoolExecutor
import threading
import pytest

from app.schemas.models import Medicine, MedicalRecord, MedicalRecordItem, LeafletImportRequest, LeafletDiscoverRequest
from app.services.health_workflows import verify_fields, inspect_cabinet, analyze_trends
from app.services.leaflet_browser import BaikeBrowser, BaikeReadResult
from app.services.leaflet_candidates import CandidateStore
from app.services.leaflet_identity import compare_identity
from app.services import leaflet_service


def test_verify_missing_duplicate_and_date():
    result = verify_fields([{"label": "日期", "value": "bad"}, {"label": "", "value": ""}, {"label": "日期", "value": "bad"}])
    assert {issue["code"] for issue in result["issues"]} == {"missing", "duplicate", "date"}
    assert result["requires_confirmation"]


def test_cabinet_expiry_and_inventory():
    result = inspect_cabinet([Medicine(id="m1", name="药品", expire="2026-01-01", stock=0)], date(2026, 2, 1), 3, 30)
    assert {f["code"] for f in result["findings"]} == {"expired", "low_stock", "missing_identity"}


def test_trends_separate_units_and_exclude_unconfirmed():
    def record(rid, when, value, unit, status="已确认"):
        return MedicalRecord(id=rid, title="报告", date=when, status=status, items=[MedicalRecordItem(label="指标", value=value, unit=unit)])
    result = analyze_trends([record("1", "2026-01-01", "1", "mg"), record("2", "2026-02-01", "2", "mg"), record("3", "2026-03-01", "3", "g"), record("4", "bad", "4", "mg")])
    mg = next(t for t in result["trends"] if t["unit"] == "mg")
    assert mg["delta"] == "1"
    assert len(result["trends"]) == 2
    assert result["excluded"][0]["record_id"] == "4"


def test_identity_missing_is_not_conflict():
    result = compare_identity({"通用名": "测试药", "厂家": "甲厂", "规格": "20mg"}, "测试药\n规格：10mg")
    assert result == {"matched": ["通用名"], "missing": ["厂家"], "conflicting": ["规格"]}


def test_candidates_are_owner_and_content_bound():
    store = CandidateStore()
    doc = BaikeReadResult("文本", "https://baike.baidu.com/item/test", "ok", b"html")
    key, digest = store.remember("u1", {"name": "药"}, doc)
    assert store.resolve(key, "u1", {"name": "药"}, digest) is doc
    for owner, identity, version in [("u2", {"name": "药"}, digest), ("u1", {"name": "其他药"}, digest), ("u1", {"name": "药"}, "other")]:
        with pytest.raises(ValueError):
            store.resolve(key, owner, identity, version)


def test_browser_calls_from_different_threads_have_one_owner(monkeypatch):
    browser = BaikeBrowser()
    monkeypatch.setattr(browser, "_read_locked", lambda _: threading.get_ident())
    with ThreadPoolExecutor(max_workers=3) as callers:
        owners = list(callers.map(browser.read, ["a", "b", "c"]))
    browser.close()
    assert len(set(owners)) == 1


def test_import_requires_explicit_confirmation():
    with pytest.raises(ValueError, match="确认"):
        leaflet_service.import_baike_leaflet(LeafletImportRequest(generic_name="药"), owner="u")


def test_encyclopedia_confidence_is_capped(monkeypatch):
    monkeypatch.setattr(leaflet_service, "_read_baike_page", lambda _: BaikeReadResult("测试药\n作用功效\n文本\n用法用量\n文本\n禁忌\n文本", "https://baike.baidu.com/item/test", "ok", b"html"))
    result = leaflet_service._baike_candidate(LeafletDiscoverRequest(generic_name="测试药"))
    assert result.confidence < 0.5
