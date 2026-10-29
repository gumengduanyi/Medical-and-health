import json

from app.services import web_search_service


def test_search_returns_trusted_sources_first(monkeypatch):
    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps({
                "results": [
                    {"title": "普通结果", "url": "https://example.com/a", "content": "普通摘要"},
                    {"title": "官方指南", "url": "https://www.nhc.gov.cn/guide", "content": "官方摘要"},
                ]
            }).encode("utf-8")

    monkeypatch.setattr(web_search_service._LOCAL_HTTP_OPENER, "open", lambda *_args, **_kwargs: FakeResponse())

    sources = web_search_service.search("高血压最新指南")

    assert len(sources) == 2
    assert sources[0].title == "官方指南"
    assert sources[0].metadata["trusted_domain"] is True
    assert sources[1].metadata["trusted_domain"] is False


def test_search_fails_closed_when_searxng_is_unavailable(monkeypatch):
    def raise_error(*_args, **_kwargs):
        raise OSError("SearXNG unavailable")

    monkeypatch.setattr(web_search_service._LOCAL_HTTP_OPENER, "open", raise_error)

    assert web_search_service.search("高血压最新指南") == []
