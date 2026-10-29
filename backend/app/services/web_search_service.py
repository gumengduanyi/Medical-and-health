from __future__ import annotations

import json
from urllib import parse, request

from app.core.config import settings
from app.schemas.models import RagSource


_LOCAL_HTTP_OPENER = request.build_opener(request.ProxyHandler({}))


def _trusted_domains() -> set[str]:
    return {
        item.strip().lower()
        for item in settings.web_search_domains.split(",")
        if item.strip()
    }


def _is_trusted_url(url: str) -> bool:
    hostname = parse.urlparse(url).hostname or ""
    hostname = hostname.lower().removeprefix("www.")
    return any(hostname == domain or hostname.endswith(f".{domain}") for domain in _trusted_domains())


def _search_query(message: str) -> str:
    # Do not send profile identifiers or conversational filler to an external service.
    query = message.strip()
    for marker in ("我的", "我现在", "我最近", "我个人", "帮我"):
        query = query.replace(marker, "")
    return " ".join(query.split())[:240]


def search(message: str) -> list[RagSource]:
    if not settings.web_search_enabled:
        return []

    query = _search_query(message)
    if not query:
        return []

    params = parse.urlencode({
        "q": query,
        "format": "json",
        "language": "zh-CN",
    })
    url = f"{settings.web_search_url.rstrip('?')}&{params}" if "?" in settings.web_search_url else f"{settings.web_search_url}?{params}"
    req = request.Request(url, headers={"Accept": "application/json", "User-Agent": "HealthAssistant/1.0"})

    try:
        with _LOCAL_HTTP_OPENER.open(req, timeout=settings.web_search_timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return []

    results = payload.get("results", []) if isinstance(payload, dict) else []
    sources: list[RagSource] = []
    for index, item in enumerate(results):
        if not isinstance(item, dict):
            continue
        result_url = str(item.get("url", "")).strip()
        title = str(item.get("title", "")).strip()
        excerpt = str(item.get("content", "")).strip()
        if not result_url or not title or not excerpt:
            continue
        trusted = _is_trusted_url(result_url)
        sources.append(
            RagSource(
                id=f"web_{index}",
                title=title,
                source_type="web",
                excerpt=excerpt[:500],
                score=1.0 if trusted else 0.5,
                metadata={
                    "url": result_url,
                    "domain": parse.urlparse(result_url).hostname or "",
                    "trusted_domain": trusted,
                    "published_at": str(item.get("publishedDate", "")),
                    "engine": ",".join(item.get("engines", [])) if isinstance(item.get("engines"), list) else "",
                },
            )
        )

    return sorted(sources, key=lambda source: source.score, reverse=True)[: settings.web_search_max_results]