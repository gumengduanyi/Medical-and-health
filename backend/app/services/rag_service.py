from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any
from urllib import error, request

from app.schemas.models import ChatResponse, RagSource
from app.core.config import settings
from app.services import data_store
from app.services.knowledge_base import get_knowledge_documents
from app.services import reranker_service, vector_service


@dataclass(frozen=True)
class RagChunk:
    id: str
    title: str
    source_type: str
    content: str
    metadata: dict[str, Any]


_TERM_PATTERN = re.compile(r"[0-9a-zA-Z]+|[\u4e00-\u9fff]+")
_URGENT_KEYWORDS = ("胸痛", "呼吸困难", "晕厥", "意识模糊", "大出血", "呕血", "黑便", "急诊")
_OLLAMA_TIMEOUT_SECONDS = 120
_SYSTEM_PROMPT = """你是医疗健康资料整理助手，只能基于用户健康档案和检索证据回答。
规则：
1. 证据不足时必须说明资料不足，不要猜测。
2. 不做诊断，不开处方，不建议用户自行停药、换药或调整剂量。
3. 涉及胸痛、呼吸困难、晕厥、意识模糊、大出血、呕血、黑便等急症信号时，必须建议及时线下就医或急诊。
4. 回答要简洁、中文、面向普通用户，并明确提示“以医生意见为准”。
5. 每个医学结论都要能对应到给定证据。"""


def _build_chinese_ngrams(fragment: str) -> list[str]:
    grams: list[str] = []
    length = len(fragment)
    max_size = min(4, length)
    for size in range(2, max_size + 1):
        for start in range(0, length - size + 1):
            grams.append(fragment[start : start + size])
    if length <= 4:
        grams.append(fragment)
    return grams


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for match in _TERM_PATTERN.finditer(text.lower()):
        term = match.group(0)
        if re.fullmatch(r"[0-9a-zA-Z]+", term):
            if len(term) >= 2:
                tokens.append(term)
            continue
        tokens.extend(_build_chinese_ngrams(term))
    return tokens


def _score(query: str, content: str) -> float:
    query_tokens = Counter(_tokenize(query))
    if not query_tokens:
        return 0.0

    content_tokens = Counter(_tokenize(content))
    overlap = sum(min(count, content_tokens.get(token, 0)) for token, count in query_tokens.items())
    exact_bonus = sum(1.5 for token in query_tokens if len(token) >= 2 and token in content)
    return float(overlap + exact_bonus)


def _truncate(text: str, limit: int = 140) -> str:
    clean = re.sub(r"\s+", " ", text).strip()
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1] + "…"


def _build_profile_chunk() -> RagChunk:
    profile = data_store.get_profile()
    content = (
        f"姓名：{profile.name}；性别：{profile.sex}；年龄：{profile.age}；身高：{profile.height}cm；体重：{profile.weight}kg；"
        f"药物过敏史：{profile.allergy}；既往病史：{profile.disease}；家族史：{profile.family_history}。"
    )
    return RagChunk(
        id=profile.id,
        title="个人健康档案",
        source_type="profile",
        content=content,
        metadata={"profile_id": profile.id},
    )


def _build_record_chunks() -> list[RagChunk]:
    chunks: list[RagChunk] = []
    profile = data_store.get_profile()
    for record in data_store.list_records():
        chunks.append(
            RagChunk(
                id=record["id"],
                title=record["title"],
                source_type="record",
                content=f"{record['title']}；日期：{record['date']}；状态：{record['status']}。",
                metadata={"profile_id": profile.id, "record_id": record["id"], "record_date": record["date"]},
            )
        )
    return chunks


def _build_medicine_chunks() -> list[RagChunk]:
    chunks: list[RagChunk] = []
    profile = data_store.get_profile()
    for item in data_store.list_medicines():
        chunks.append(
            RagChunk(
                id=item.id or item.name,
                title=item.name,
                source_type="medicine",
                content=f"药品名称：{item.name}；用法用量：{item.dose}；库存：{item.stock}；有效期：{item.expire}；风险提示：{item.risk}。",
                metadata={"profile_id": profile.id, "medicine_id": item.id, "expire": item.expire},
            )
        )
    return chunks


def _build_knowledge_chunks() -> list[RagChunk]:
    chunks: list[RagChunk] = []
    for doc in get_knowledge_documents():
        chunks.append(
            RagChunk(
                id=doc.id,
                title=doc.title,
                source_type=doc.source_type,
                content=doc.content,
                metadata={"tags": list(doc.tags), "knowledge_id": doc.id},
            )
        )
    return chunks


def build_corpus() -> list[RagChunk]:
    return [
        _build_profile_chunk(),
        *_build_record_chunks(),
        *_build_medicine_chunks(),
        *_build_knowledge_chunks(),
    ]


def _is_urgent(message: str) -> bool:
    return any(keyword in message for keyword in _URGENT_KEYWORDS)


def _format_sources(chunks: list[RagChunk], scores: dict[str, float]) -> list[RagSource]:
    sources: list[RagSource] = []
    for chunk in chunks:
        sources.append(
            RagSource(
                id=chunk.id,
                title=chunk.title,
                source_type=chunk.source_type,
                excerpt=_truncate(chunk.content),
                score=round(scores.get(chunk.id, 0.0), 3),
                metadata=chunk.metadata,
            )
        )
    return sources


def _vector_hits_to_chunks(hits: list[vector_service.VectorHit]) -> list[RagChunk]:
    return [
        RagChunk(
            id=hit.id,
            title=hit.title,
            source_type=hit.source_type,
            content=hit.content,
            metadata={**hit.metadata, "retrieval": "qdrant", "vector_score": hit.score},
        )
        for hit in hits
    ]


def retrieve_relevant_chunks(message: str, corpus: list[RagChunk], limit: int | None = None) -> list[RagChunk]:
    result_limit = limit or settings.rag_top_k
    ranked = sorted(corpus, key=lambda chunk: (_score(message, chunk.content), len(chunk.content)), reverse=True)
    filtered = [chunk for chunk in ranked if _score(message, chunk.content) >= settings.rag_min_score]
    return filtered[:result_limit]


def _filter_corpus_for_profile(corpus: list[RagChunk], profile_id: str | None) -> list[RagChunk]:
    filtered: list[RagChunk] = []
    for chunk in corpus:
        chunk_profile_id = chunk.metadata.get("profile_id")
        if not chunk_profile_id or chunk_profile_id == profile_id:
            filtered.append(chunk)
    return filtered


def _profile_context_chunk(corpus: list[RagChunk], profile_id: str | None) -> RagChunk:
    profile_chunk = corpus[0]
    if profile_id == profile_chunk.metadata.get("profile_id"):
        return profile_chunk
    return RagChunk(
        id="public_context",
        title="未选择健康档案",
        source_type="context",
        content="当前请求未绑定具体健康档案。",
        metadata={},
    )


def _render_response(message: str, profile_chunk: RagChunk, hits: list[RagChunk]) -> str:
    if _is_urgent(message):
        return (
            "检索到急症相关信号。系统建议优先线下急诊或及时就医，不要继续依赖在线问答。"
            "如果你愿意，我可以继续帮你整理当前资料中的风险点。"
        )

    if not hits:
        return "当前资料不足，暂时没有检索到足够证据。你可以补充报告、药品信息或健康档案后再试。"

    top_titles = "、".join(hit.title for hit in hits[:3])
    content_parts = [f"我基于你的健康档案和已确认资料检索到以下相关内容：{top_titles}。"]

    if any(keyword in message for keyword in ("血压", "高血压")):
        content_parts.append("结合当前资料，建议继续连续记录血压趋势、保持低盐饮食，并按医嘱复诊；不要自行停药或调整处方药剂量。")
    elif any(keyword in message for keyword in ("药", "用药", "阿司匹林", "禁忌")):
        content_parts.append("结合药品记录和过敏史，请先确认药品名称、剂量和有效期，再决定是否继续使用；如涉及处方药，请遵医嘱。")
    elif any(keyword in message for keyword in ("报告", "体检", "指标", "血糖", "血脂")):
        content_parts.append("报告解读应优先看异常指标的趋势和复查建议，未确认的 OCR 内容只能视为识别结果，不能直接当作医疗结论。")
    else:
        content_parts.append("如果你想继续，我可以按‘报告、药品、健康档案、风险提醒’四个维度帮你整理成更清晰的结论。")

    return "".join(content_parts)


def _select_llm_model(context: dict[str, Any] | None = None) -> str:
    if context and isinstance(context, dict):
        if context.get("fast_mode") or context.get("mode") == "fast":
            return settings.fast_llm_model
        model = context.get("model")
        if isinstance(model, str) and model.strip():
            return model.strip()
    return settings.local_llm_model


def _strip_thinking(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()


def _call_ollama_chat(message: str, profile_chunk: RagChunk, hits: list[RagChunk], context: dict[str, Any] | None = None) -> str:
    evidence = "\n".join(
        f"[{index}] {chunk.title}（{chunk.source_type}）：{chunk.content}"
        for index, chunk in enumerate(hits[: settings.rag_top_k], start=1)
    )
    payload = {
        "model": _select_llm_model(context),
        "stream": False,
        "options": {"temperature": 0.2, "top_p": 0.8},
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"用户问题：{message}\n\n"
                    f"当前健康档案：{profile_chunk.content}\n\n"
                    f"检索证据：\n{evidence}\n\n"
                    "请基于证据回答，最后用一句话提醒不替代医生诊断。"
                ),
            },
        ],
    }
    data = json.dumps(payload).encode("utf-8")
    url = f"{settings.local_llm_base_url.rstrip('/')}/api/chat"
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=_OLLAMA_TIMEOUT_SECONDS) as response:
        result = json.loads(response.read().decode("utf-8"))
    content = result.get("message", {}).get("content", "")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("Ollama did not return assistant content")
    return _strip_thinking(content)


def generate_health_reply(message: str, context: dict[str, Any] | None = None) -> ChatResponse:
    corpus = build_corpus()
    profile_id = context.get("profile_id") if context and isinstance(context, dict) else None
    stored_profile_chunk = corpus[0]
    if profile_id and profile_id != stored_profile_chunk.metadata.get("profile_id"):
        return ChatResponse(
            content="当前会话资料和所选健康档案不一致，请先确认 profile_id 再进行检索。",
        )

    searchable_corpus = _filter_corpus_for_profile(corpus, profile_id)
    profile_chunk = _profile_context_chunk(corpus, profile_id)
    try:
        vector_service.upsert_documents(searchable_corpus)
        vector_hits = vector_service.search(message, profile_id=profile_id, limit=settings.rag_candidate_k)
    except Exception:
        vector_hits = []

    candidates = _vector_hits_to_chunks(vector_hits) if vector_hits else retrieve_relevant_chunks(message, searchable_corpus, settings.rag_candidate_k)
    hits = reranker_service.rerank(message, candidates, settings.rag_top_k)
    score_map = {chunk.id: _score(message, chunk.content) for chunk in hits}
    sources = _format_sources(hits, score_map)
    response_text = _render_response(message, profile_chunk, hits)
    requires_clinician = _is_urgent(message)

    if hits and not requires_clinician:
        try:
            response_text = _call_ollama_chat(message, profile_chunk, hits, context=context)
        except (error.URLError, TimeoutError, OSError, json.JSONDecodeError, RuntimeError, KeyError, TypeError, ValueError):
            response_text = _render_response(message, profile_chunk, hits)

    return ChatResponse(
        content=response_text,
        sources=sources,
        requires_clinician=requires_clinician,
    )