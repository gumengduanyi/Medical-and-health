from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib import parse

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

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
from app.services.leaflet_candidates import candidate_store


from app.services.leaflet_parser import (TARGET_LEAFLET_SECTIONS, _normalise_text, _split_sections, _filter_target_sections)
from app.services.leaflet_identity import compare_identity


from app.services.leaflet_browser import (BaikeBrowser, BaikeReadResult, DownloadedLeaflet, LeafletChunk, _BAIKE_BROWSER)


def _baike_page_url(generic_name: str) -> str:
    return f"https://baike.baidu.com/item/{parse.quote(generic_name.strip(), safe='')}"


def _read_baike_page(generic_name: str) -> BaikeReadResult:
    page_url = _baike_page_url(generic_name)
    try:
        return _BAIKE_BROWSER.read(page_url)
    except PlaywrightTimeoutError as exc:
        raise ValueError("百度百科页面加载超时") from exc
    except Exception as exc:
        if "Executable doesn't exist" in str(exc):
            raise ValueError("未安装 Playwright Chromium，请执行 python -m playwright install chromium") from exc
        raise ValueError(f"百度百科浏览器读取失败：{exc}") from exc


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
        confirmed_by=leaflet.confirmed_by,
        confirmed_at=leaflet.confirmed_at.isoformat() if leaflet.confirmed_at else None,
        index_status=leaflet.index_status,
        reviewedBy=leaflet.reviewed_by,
        reviewedAt=leaflet.reviewed_at.isoformat() if leaflet.reviewed_at else None,
        reviewNote=leaflet.review_note,
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
    owner: str = "",
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
            confirmed_by=owner,
            confirmed_at=datetime.now(timezone.utc),
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


def import_baike_leaflet(payload: LeafletImportRequest, owner: str = "") -> LeafletImportResponse:
    generic_name = payload.generic_name.strip()
    if not generic_name:
        raise ValueError("百度百科导入需要药品通用名")
    if not owner or not payload.confirmed:
        raise ValueError("请确认采集内容后再导入")
    identity = {key: getattr(payload, key) for key in ("generic_name", "manufacturer", "approval_number", "specification")}
    read_result = candidate_store.resolve(payload.candidate_id, owner, identity, payload.content_hash)
    if read_result.status == "human_verification_required":
        raise ValueError("百度百科要求完成安全验证，智能体已停止读取，请人工打开页面完成验证后再导入")
    if read_result.status != "ok":
        raise ValueError("百度百科页面没有返回可读取内容")
    downloaded = DownloadedLeaflet(
        content=read_result.html,
        content_type="text/html",
        final_url=read_result.final_url,
    )
    return _store_leaflet(
        payload,
        downloaded,
        read_result.text,
        "text/html",
        read_result.final_url,
        "baike_browser_agent",
        owner=owner,
    )


def _section_map(sections: list[tuple[str, str]]) -> dict[str, str]:
    result: dict[str, str] = {}
    for section_name, content in sections:
        result[section_name] = f"{result[section_name]}\n{content}".strip() if section_name in result else content
    return result


def _match_baike_identity(payload: LeafletDiscoverRequest, read_result: BaikeReadResult) -> tuple[float, list[str], list[str]]:
    searchable_text = f"{read_result.title}\n{read_result.text}"
    fields = (
        ("通用名", payload.generic_name),
        ("厂家", payload.manufacturer),
        ("规格", payload.specification),
        ("批准文号", payload.approval_number),
    )
    provided = [(label, value.strip()) for label, value in fields if value and value.strip()]
    if not provided:
        return 0.2, [], []
    matched = [label for label, value in provided if value in searchable_text]
    mismatched = [label for label, value in provided if value not in searchable_text]
    return round(len(matched) / len(provided), 2), matched, mismatched


def _baike_candidate(payload: LeafletDiscoverRequest, owner: str = "") -> LeafletCandidate:
    generic_name = payload.generic_name.strip()
    read_result = _read_baike_page(generic_name)
    if read_result.status == "human_verification_required":
        return LeafletCandidate(
            source_type="baike_browser_agent",
            source_url=read_result.final_url,
            title=generic_name,
            confidence=0.0,
            status="human_verification_required",
            httpStatus=read_result.http_status,
            attempts=read_result.attempts,
            elapsedMs=read_result.elapsed_ms,
            reason="百度百科要求完成安全验证，智能体已停止读取，不会绕过验证。",
        )
    if read_result.status != "ok":
        return LeafletCandidate(
            source_type="baike_browser_agent",
            source_url=read_result.final_url,
            title=generic_name,
            confidence=0.0,
            status=read_result.status,
            httpStatus=read_result.http_status,
            attempts=read_result.attempts,
            elapsedMs=read_result.elapsed_ms,
            reason=read_result.reason or "百度百科页面没有返回可读取内容。",
        )
    selected_sections = _filter_target_sections(_split_sections(read_result.text))
    section_map = _section_map(selected_sections)
    sections_found = list(section_map)
    missing_sections = [name for name in ("作用功效", "用法用量", "禁忌") if name not in section_map]
    identity = compare_identity({"通用名": payload.generic_name, "厂家": payload.manufacturer, "规格": payload.specification, "批准文号": payload.approval_number}, f"{read_result.title}\n{read_result.text}")
    matched_fields = identity["matched"]
    mismatched_fields = identity["conflicting"]
    provided_count = sum(len(items) for items in identity.values())
    identity_score = len(matched_fields) / max(1, provided_count)
    section_score = len(sections_found) / len(TARGET_LEAFLET_SECTIONS)
    candidate_id, digest = candidate_store.remember(owner, payload.model_dump(), read_result) if owner else ("", "")
    return LeafletCandidate(
        source_type="baike_browser_agent",
        source_url=read_result.final_url,
        title=generic_name,
        confidence=min(0.49, round(identity_score * 0.7 + section_score * 0.3, 2)),
        candidate_id=candidate_id,
        content_hash=digest,
        missing_identity_fields=identity["missing"],
        conflicting_fields=identity["conflicting"],
        sections_found=sections_found,
        sections=section_map,
        missing_sections=missing_sections,
        httpStatus=read_result.http_status,
        attempts=read_result.attempts,
        elapsedMs=read_result.elapsed_ms,
        matched_fields=matched_fields,
        mismatched_fields=mismatched_fields,
        reason=(
            "已通过正常浏览器读取公开词条；百度百科不是正式说明书，导入前必须人工审核。"
            if not mismatched_fields
            else f"页面已读取，但以下身份字段未在页面中匹配：{'、'.join(mismatched_fields)}；导入前必须人工核对。"
        ),
    )


def discover_leaflet_candidates(payload: LeafletDiscoverRequest, owner: str = "") -> LeafletDiscoverResponse:
    generic_name = payload.generic_name.strip()
    if not generic_name:
        raise ValueError("自动发现说明书需要药品通用名")

    candidate = _baike_candidate(payload, owner=owner)
    return LeafletDiscoverResponse(generic_name=generic_name, candidates=[candidate])


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


def approve_leaflet(leaflet_id: str, reviewer_id: str, review_note: str = "") -> LeafletImportResponse | None:
    with SessionLocal() as session:
        leaflet = session.get(DrugLeafletORM, leaflet_id)
        if leaflet is None:
            return None
        sections = session.query(DrugLeafletSectionORM).filter_by(leaflet_id=leaflet.id).order_by(DrugLeafletSectionORM.section_order).all()
        if not leaflet.confirmed_by or leaflet.confirmed_at is None:
            raise ValueError("该内容尚未完成用户确认，请重新发现并确认")
        leaflet.status = "approved"
        leaflet.index_status = "pending"
        leaflet.reviewed_by = reviewer_id
        leaflet.reviewed_at = datetime.now(timezone.utc)
        leaflet.review_note = review_note.strip()
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
        try:
            vector_service.upsert_documents(chunks)
            leaflet.index_status = "synced" if settings.vector_db_url.strip() else "disabled"
        except Exception:
            leaflet.index_status = "failed"
        session.commit()
        return _leaflet_response(leaflet, sections)