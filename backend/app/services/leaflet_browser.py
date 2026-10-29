from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright
from app.core.config import settings
from app.services.leaflet_parser import _normalise_text, TARGET_LEAFLET_SECTIONS

def _looks_like_verification_page(title: str, text: str) -> bool:
    content = f"{title}\n{text}"
    return any(
        marker in content
        for marker in (
            "百度安全验证",
            "请完成下方验证",
            "扫码验证",
            "安全验证",
            "访问频繁",
            "登录后查看",
            "验证码",
        )
    )


BAIKE_FAILURE_MESSAGES = {
    "human_verification_required": "百度百科要求完成安全验证或登录，系统已停止自动读取。",
    "not_found": "没有找到对应的百度百科词条。",
    "empty_page": "百度百科返回了空页面。",
}


@dataclass(frozen=True)
class DownloadedLeaflet:
    content: bytes
    content_type: str
    final_url: str


@dataclass(frozen=True)
class LeafletChunk:
    id: str
    title: str
    source_type: str
    content: str
    metadata: dict[str, Any]


@dataclass(frozen=True)
class BaikeReadResult:
    text: str
    final_url: str
    status: str
    html: bytes = b""
    reason: str = ""
    title: str = ""
    http_status: int = 0
    attempts: int = 1
    elapsed_ms: int = 0


class BaikeBrowser:
    """Own Playwright on one worker thread; use a fresh page per read."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._worker = ThreadPoolExecutor(max_workers=1, thread_name_prefix="leaflet-browser")
        self._playwright = None
        self._context = None
        self._browser = None
        self._closed = False

    def _start(self) -> None:
        if self._playwright is not None and self._context is not None:
            return
        self._playwright = sync_playwright().start()
        browser_args = {
            "headless": settings.leaflet_browser_headless,
        }
        if settings.leaflet_browser_executable_path:
            browser_args["executable_path"] = settings.leaflet_browser_executable_path
        user_data_dir = Path(settings.leaflet_browser_user_data_dir)
        user_data_dir.mkdir(parents=True, exist_ok=True)
        self._context = self._playwright.chromium.launch_persistent_context(
            str(user_data_dir),
            locale="zh-CN",
            viewport={"width": 1365, "height": 900},
            timezone_id="Asia/Shanghai",
            **browser_args,
        )
        self._context.set_default_timeout(5000)
        self._context.set_default_navigation_timeout(settings.leaflet_browser_timeout_seconds * 1000)

    def close(self) -> None:
        with self._lock:
            if self._playwright is not None:
                self._worker.submit(self._close_locked).result()
            if not self._closed:
                self._closed = True
                self._worker.shutdown(wait=True)

    def _close_locked(self) -> None:
        try:
            if self._context is not None:
                self._context.close()
            if self._browser is not None:
                self._browser.close()
            if self._playwright is not None:
                self._playwright.stop()
        finally:
            self._context = None
            self._browser = None
            self._playwright = None

    def read(self, page_url: str) -> BaikeReadResult:
        with self._lock:
            return self._worker.submit(self._read_locked, page_url).result()

    def _read_locked(self, page_url: str) -> BaikeReadResult:
        started_at = time.monotonic()
        last_error: Exception | None = None
        for attempt in range(1, settings.leaflet_browser_max_retries + 2):
            page = None
            context = None
            try:
                self._start()
                context = self._context
                page = context.new_page()
                response = page.goto(
                    page_url,
                    wait_until="domcontentloaded",
                    timeout=settings.leaflet_browser_timeout_seconds * 1000,
                )
                result = self._read_page(page, response, attempt, started_at)
                if result.status not in {"timeout", "browser_error"}:
                    return result
            except PlaywrightTimeoutError as exc:
                last_error = exc
            except Exception as exc:
                last_error = exc
            finally:
                if page is not None:
                    page.close()
            if attempt <= settings.leaflet_browser_max_retries:
                self._close_locked()
                time.sleep(min(1.5, 0.4 * attempt))
        elapsed_ms = int((time.monotonic() - started_at) * 1000)
        if isinstance(last_error, PlaywrightTimeoutError):
            return BaikeReadResult(
                "", page_url, "timeout", reason="百度百科页面加载超时，请稍后重试。", attempts=attempt, elapsed_ms=elapsed_ms
            )
        return BaikeReadResult(
            "",
            page_url,
            "browser_error",
            reason=f"百度百科浏览器读取失败：{last_error}",
            attempts=attempt,
            elapsed_ms=elapsed_ms,
        )

    def _read_page(self, page, response, attempt: int, started_at: float) -> BaikeReadResult:
        status_code = response.status if response else 0
        page_url = page.url
        ready_deadline = time.monotonic() + settings.leaflet_browser_ready_timeout_seconds
        title = ""
        text = ""
        while time.monotonic() < ready_deadline:
            title = _normalise_text(page.title())
            text = _normalise_text(page.locator("body").inner_text(timeout=2000))
            if status_code in {401, 403, 429} or _looks_like_verification_page(title, text):
                return BaikeReadResult(
                    "", page_url, "human_verification_required",
                    reason=BAIKE_FAILURE_MESSAGES["human_verification_required"],
                    title=title, http_status=status_code, attempts=attempt,
                    elapsed_ms=int((time.monotonic() - started_at) * 1000),
                )
            if status_code == 404 or "百度百科尚未收录" in text or "找不到相关页面" in text:
                return BaikeReadResult(
                    "", page_url, "not_found", reason=BAIKE_FAILURE_MESSAGES["not_found"],
                    title=title, http_status=status_code, attempts=attempt,
                    elapsed_ms=int((time.monotonic() - started_at) * 1000),
                )
            if any(name in text for name in TARGET_LEAFLET_SECTIONS) or "适应症" in text or "功能主治" in text:
                return BaikeReadResult(
                    text, page_url, "ok", page.content().encode("utf-8"), title=title,
                    http_status=status_code, attempts=attempt,
                    elapsed_ms=int((time.monotonic() - started_at) * 1000),
                )
            page.wait_for_timeout(250)
        return BaikeReadResult(
            "", page_url, "empty_page", reason=BAIKE_FAILURE_MESSAGES["empty_page"],
            title=title, http_status=status_code, attempts=attempt,
            elapsed_ms=int((time.monotonic() - started_at) * 1000),
        )


_BAIKE_BROWSER = BaikeBrowser()
