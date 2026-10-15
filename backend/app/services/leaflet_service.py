from __future__ import annotations

import hashlib
import html
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib import parse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from app.core.config import settings
from app.db.models import DrugLeafletORM, DrugLeafletSectionORM
from app.db.session import SessionLocal
from app.schemas.models import (
    LeafletCandidate,
    LeafletDiscoverRequest,
    LeafletDiscoverResponse,
    LeafletImportRequest,
    LeafletImportResponse,
    LeafletSection,
)
from app.services import vector_service


TARGET_LEAFLET_SECTIONS = ("作用功效", "用法用量", "禁忌")
LEAFLET_SECTION_BOUNDARIES = (
    "药品名称",
    "成份",
    "成分",
    "性状",
    "适应症",
    "功能主治",
    "主要功效",
    "适用病症",
    "规格",
    "用法用量",
    "不良反应",
    "禁忌",
    "药品禁忌",
    "注意事项",
    "孕妇及哺乳期妇女用药",
    "儿童用药",
    "老年用药",
    "药物相互作用",
    "药物过量",
    "药理毒理",
    "药代动力学",
    "贮藏",
    "贮藏方法",
    "包装",
    "有效期",
    "执行标准",
    "批准文号",
    "生产企业",
    "药性分析",
)
SECTION_ALIASES = {
    "作用功效": "作用功效",
    "作用与功效": "作用功效",
    "功效": "作用功效",
    "功能主治": "作用功效",
    "主要功效": "作用功效",
    "适用病症": "作用功效",
    "适应症": "作用功效",
    "用法用量": "用法用量",
    "禁忌": "禁忌",
    "药品禁忌": "禁忌",
    "禁忌症": "禁忌",
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


def _normalise_text(text: str) -> str:
    text = html.unescape(text).replace("\r\n", "\n").replace("\r", "\n")
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    noise_lines = {"播报", "编辑", "讨论", "收藏", "赞", "上传视频"}
    return re.sub(
        r"\n{3,}",
        "\n\n",
        "\n".join(line for line in lines if line and line not in noise_lines),
    ).strip()


def _baike_page_url(generic_name: str) -> str:
    return f"https://baike.baidu.com/item/{parse.quote(generic_name.strip(), safe='')}"


def _read_baike_page(generic_name: str) -> tuple[str, str, str, bytes]:
    page_url = _baike_page_url(generic_name)
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page(locale="zh-CN")
                response = page.goto(
                    page_url,
                    wait_until="domcontentloaded",
                    timeout=settings.leaflet_browser_timeout_seconds * 1000,
                )
                page.wait_for_timeout(1200)
                text = _normalise_text(page.locator("body").inner_text(timeout=5000))
                title = _normalise_text(page.title())
                status_code = response.status if response else 0
                if status_code in {401, 403} or any(
                    marker in f"{title}\n{text}" for marker in ("百度安全验证", "请完成下方验证", "扫码验证")
                ):
                    return "", page.url, "human_verification_required", b""
                if not text:
                    return "", page.url, "empty_page", b""
                return text, page.url, "ok", page.content().encode("utf-8")
            finally:
                browser.close()
    except PlaywrightTimeoutError as exc:
        raise ValueError("百度百科页面加载超时") from exc
    except Exception as exc:
        raise ValueError(f"百度百科浏览器读取失败：{exc}") from exc


def _split_sections(text: str) -> list[tuple[str, str]]:
    section_names = (*LEAFLET_SECTION_BOUNDARIES, *SECTION_ALIASES.keys())
    pattern = re.compile(
        rf"^\s*(?P<section>{'|'.join(map(re.escape, section_names))})\s*(?:[:：]\s*(?P<inline>.*))?$"
    )
    sections: list[tuple[str, str]] = []
    current_name: str | None = None
    current_lines: list[str] = []

    def flush() -> None:
        if current_name is None:
            return
        content = _normalise_text("\n".join(current_lines))
        if content:
            sections.append((current_name, content))

    for line in text.splitlines():
        match = pattern.match(line)
        if match:
            flush()
            current_name = SECTION_ALIASES.get(match.group("section"), match.group("section"))
            current_lines = [match.group("inline")] if match.group("inline") else []
        elif current_name is not None:
            current_lines.append(line)

    flush()
    if not sections:
        return [("全文", text)]
    return sections


def _filter_target_sections(sections: list[tuple[str, str]]) -> list[tuple[str, str]]:
    selected: list[tuple[str, str]] = []
    for section_name, content in sections:
        canonical_name = SECTION_ALIASES.get(section_name, section_name)
        if canonical_name in TARGET_LEAFLET_SECTIONS:
            selected.append((canonical_name, content))
    return selected


def _leaflet_response(leaflet: DrugLeafletORM, sections: list[DrugLeafletSectionORM]) -> LeafletImportResponse:
    return LeafletImportResponse(
        id=leaflet.id,
        generic_name=leaflet.generic_name,
        brand_name=leaflet.brand_name,
        dosage_form=leaflet.dosage_form,
        specification=leaflet.specification,
        manufacturer=leaflet.manufacturer,
        approval_number=leaflet.approval_number,
        source_url=leaflet.source_url,
        source_type=leaflet.source_type,
        raw_file_path=leaflet.raw_file_path,
        content_type=leaflet.content_type,
        content_hash=leaflet.content_hash,
        status=leaflet.status,
        sections=[
            LeafletSection(id=item.id, section_name=item.section_name, section_order=item.section_order, content=item.content)
            for item in sections
        ],
    )


def _store_leaflet(
    payload: LeafletImportRequest,
    downloaded: DownloadedLeaflet,
    text: str,
    content_type: str,
    source_url: str,
    source_type: str,
) -> LeafletImportResponse:
    content_hash = hashlib.sha256(downloaded.content).hexdigest()
    output_dir = Path(settings.leaflet_output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    suffix = ".pdf" if content_type == "application/pdf" else ".json" if content_type == "application/json" else ".html"
    raw_path = output_dir / f"{content_hash}{suffix}"
    if not raw_path.exists():
        raw_path.write_bytes(downloaded.content)

    with SessionLocal() as session:
        existing = session.query(DrugLeafletORM).filter_by(content_hash=content_hash).first()
        if existing:
            sections = session.query(DrugLeafletSectionORM).filter_by(leaflet_id=existing.id).order_by(DrugLeafletSectionORM.section_order).all()
            return _leaflet_response(existing, sections)

        leaflet = DrugLeafletORM(
            id=f"leaflet_{uuid.uuid4().hex}",
            generic_name=payload.generic_name.strip(),
            brand_name=payload.brand_name.strip(),
            dosage_form=payload.dosage_form.strip(),
            specification=payload.specification.strip(),
            manufacturer=payload.manufacturer.strip(),
            approval_number=payload.approval_number.strip(),
            source_url=source_url or downloaded.final_url,
            source_type=source_type,
            raw_file_path=str(raw_path),
            content_type=content_type,
            content_hash=content_hash,
            published_at=payload.published_at.strip(),
            status="pending_review",
        )
        session.add(leaflet)
        sections: list[DrugLeafletSectionORM] = []
        selected_sections = _filter_target_sections(_split_sections(text))
        if not selected_sections:
            raise ValueError("说明书中没有找到作用功效、用法用量或禁忌章节")
        for order, (section_name, section_content) in enumerate(selected_sections):
            section = DrugLeafletSectionORM(
                id=f"{leaflet.id}_{order}",
                leaflet_id=leaflet.id,
                section_name=section_name,
                section_order=order,
                content=section_content,
                content_hash=hashlib.sha256(section_content.encode("utf-8")).hexdigest(),
            )
            session.add(section)
            sections.append(section)
        session.commit()
        return _leaflet_response(leaflet, sections)


def import_baike_leaflet(payload: LeafletImportRequest) -> LeafletImportResponse:
    generic_name = payload.generic_name.strip()
    if not generic_name:
        raise ValueError("百度百科导入需要药品通用名")
    text, page_url, page_status, html = _read_baike_page(generic_name)
    if page_status == "human_verification_required":
        raise ValueError("百度百科要求完成安全验证，智能体已停止读取，请人工打开页面完成验证后再导入")
    if page_status != "ok":
        raise ValueError("百度百科页面没有返回可读取内容")
    downloaded = DownloadedLeaflet(
        content=html,
        content_type="text/html",
        final_url=page_url,
    )
    return _store_leaflet(
        payload,
        downloaded,
        text,
        "text/html",
        page_url,
        "baike_browser_agent",
    )


def _section_map(sections: list[tuple[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for section_name, content in sections:
        result[section_name] = f"{result[section_name]}\n{content}".strip() if section_name in result else content
    return result


def _baike_candidate(payload: LeafletDiscoverRequest) -> LeafletCandidate:
    generic_name = payload.generic_name.strip()
    text, page_url, page_status, _ = _read_baike_page(generic_name)
    if page_status == "human_verification_required":
        return LeafletCandidate(
            source_type="baike_browser_agent",
            source_url=page_url,
            title=generic_name,
            confidence=0.0,
            status="human_verification_required",
            reason="百度百科要求完成安全验证，智能体已停止读取，不会绕过验证。",
        )
    if page_status != "ok":
        raise ValueError("百度百科页面没有返回可读取内容")
    selected_sections = _filter_target_sections(_split_sections(text))
    section_map = _section_map(selected_sections)
    sections_found = list(section_map)
    missing_sections = [name for name in ("作用功效", "用法用量", "禁忌") if name not in section_map]
    return LeafletCandidate(
        source_type="baike_browser_agent",
        source_url=page_url,
        title=generic_name,
        confidence=round(0.2 + 0.1 * len(sections_found), 2),
        sections_found=sections_found,
        sections=section_map,
        missing_sections=missing_sections,
        reason="已通过正常浏览器读取公开词条；百度百科不是正式说明书，导入前必须人工审核。",
    )


def discover_leaflet_candidates(payload: LeafletDiscoverRequest) -> LeafletDiscoverResponse:
    generic_name = payload.generic_name.strip()
    if not generic_name:
        raise ValueError("自动发现说明书需要药品通用名")

    try:
        candidate = _baike_candidate(payload)
    except ValueError:
        candidate = None
    return LeafletDiscoverResponse(generic_name=generic_name, candidates=[candidate] if candidate else [])


def list_leaflets() -> list[LeafletImportResponse]:
    with SessionLocal() as session:
        leaflets = session.query(DrugLeafletORM).order_by(DrugLeafletORM.fetched_at.desc()).all()
        result: list[LeafletImportResponse] = []
        for leaflet in leaflets:
            sections = session.query(DrugLeafletSectionORM).filter_by(leaflet_id=leaflet.id).order_by(DrugLeafletSectionORM.section_order).all()
            result.append(_leaflet_response(leaflet, sections))
        return result


def approved_chunks() -> list[LeafletChunk]:
    chunks: list[LeafletChunk] = []
    with SessionLocal() as session:
        leaflets = session.query(DrugLeafletORM).filter_by(status="approved").all()
        for leaflet in leaflets:
            sections = (
                session.query(DrugLeafletSectionORM)
                .filter_by(leaflet_id=leaflet.id)
                .order_by(DrugLeafletSectionORM.section_order)
                .all()
            )
            for section in sections:
                chunks.append(
                    LeafletChunk(
                        id=section.id,
                        title=f"{leaflet.generic_name} - {section.section_name}",
                        source_type="drug_leaflet",
                        content=section.content,
                        metadata={
                            "drug_name": leaflet.generic_name,
                            "brand_name": leaflet.brand_name,
                            "manufacturer": leaflet.manufacturer,
                            "specification": leaflet.specification,
                            "approval_number": leaflet.approval_number,
                            "section": section.section_name,
                            "source_url": leaflet.source_url,
                            "version_date": leaflet.published_at,
                            "review_status": leaflet.status,
                            "source_type": leaflet.source_type,
                        },
                    )
                )
    return chunks


def approve_leaflet(leaflet_id: str) -> LeafletImportResponse | None:
    with SessionLocal() as session:
        leaflet = session.get(DrugLeafletORM, leaflet_id)
        if leaflet is None:
            return None
        sections = session.query(DrugLeafletSectionORM).filter_by(leaflet_id=leaflet.id).order_by(DrugLeafletSectionORM.section_order).all()
        leaflet.status = "approved"
        session.commit()

        chunks = [
            LeafletChunk(
                id=section.id,
                title=f"{leaflet.generic_name} - {section.section_name}",
                source_type="drug_leaflet",
                content=section.content,
                metadata={
                    "drug_name": leaflet.generic_name,
                    "brand_name": leaflet.brand_name,
                    "manufacturer": leaflet.manufacturer,
                    "specification": leaflet.specification,
                    "approval_number": leaflet.approval_number,
                    "section": section.section_name,
                    "source_url": leaflet.source_url,
                    "version_date": leaflet.published_at,
                    "review_status": leaflet.status,
                    "source_type": leaflet.source_type,
                },
            )
            for section in sections
        ]
        vector_service.upsert_documents(chunks)
        return _leaflet_response(leaflet, sections)