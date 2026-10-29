from app.schemas.models import LeafletDiscoverRequest
from app.services.leaflet_service import (
    BaikeBrowser,
    BaikeReadResult,
    _match_baike_identity,
    _split_sections,
    _baike_candidate,
)


class FakeResponse:
    def __init__(self, status=200):
        self.status = status


class FakeLocator:
    def __init__(self, text):
        self.text = text

    def inner_text(self, timeout=0):
        return self.text


class FakePage:
    url = "https://baike.baidu.com/item/example"

    def __init__(self, text, title=""):
        self.text = text
        self.title_text = title
        self.closed = False

    def title(self):
        return self.title_text

    def locator(self, _selector):
        return FakeLocator(self.text)

    def content(self):
        return "<html></html>"

    def wait_for_timeout(self, _timeout):
        return None

    def close(self):
        self.closed = True


def test_split_sections_normalizes_target_headings():
    sections = _split_sections("一、作用与功效\n缓解症状\n用法用量：每日一次\n禁忌\n过敏者禁用")

    assert sections == [
        ("作用功效", "缓解症状"),
        ("用法用量", "每日一次"),
        ("禁忌", "过敏者禁用"),
    ]


def test_match_identity_reports_matches_and_mismatches():
    payload = LeafletDiscoverRequest(
        generic_name="阿托伐他汀钙片",
        manufacturer="甲制药厂",
        specification="20mg",
        approval_number="国药准字H123",
    )
    result = BaikeReadResult(
        text="阿托伐他汀钙片\n规格20mg",
        final_url="https://baike.baidu.com/item/test",
        status="ok",
        title="阿托伐他汀钙片_百度百科",
    )

    score, matched, mismatched = _match_baike_identity(payload, result)

    assert score == 0.5
    assert matched == ["通用名", "规格"]
    assert mismatched == ["厂家", "批准文号"]


def test_discover_preserves_browser_failure_status(monkeypatch):
    monkeypatch.setattr(
        "app.services.leaflet_service._read_baike_page",
        lambda _: BaikeReadResult(
            text="",
            final_url="https://baike.baidu.com/item/example",
            status="not_found",
            reason="没有找到对应词条",
        ),
    )

    candidate = _baike_candidate(LeafletDiscoverRequest(generic_name="测试药品"))

    assert candidate.status == "not_found"
    assert candidate.reason == "没有找到对应词条"


def test_browser_read_stops_on_verification_without_retry(monkeypatch):
    browser = BaikeBrowser()
    page = FakePage("百度安全验证", "百度安全验证")

    result = browser._read_page(page, FakeResponse(403), 1, 0)

    assert result.status == "human_verification_required"
    assert result.http_status == 403