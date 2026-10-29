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
from app.services import leaflet_service, reranker_service, vector_service, web_search_service


@dataclass(frozen=True)
class RagChunk:
    id: str
    title: str
    source_type: str
    content: str
    metadata: dict[str, Any]


_TERM_PATTERN = re.compile(r"[0-9a-zA-Z]+|[\u4e00-\u9fff]+")
_URGENT_KEYWORDS = ("胸痛", "呼吸困难", "晕厥", "意识模糊", "大出血", "呕血", "黑便", "急诊")
_GREETING_MESSAGES = ("你好", "您好", "嗨", "哈喽", "在吗", "早上好", "中午好", "下午好", "晚上好")
_THANKS_MESSAGES = ("谢谢", "感谢", "辛苦了", "多谢")
_IDENTITY_MESSAGES = ("你是谁", "你能做什么", "你能干什么", "你可以做什么", "介绍一下自己")
_PROFILE_QUERY_TERMS = ("健康档案", "个人资料", "我的资料", "我的档案", "个人信息")
_GENERIC_QUERY_TERMS = {
    "最近",
    "怎么",
    "怎么办",
    "为什么",
    "我的",
    "会不会",
    "是否",
    "影响",
    "情况",
    "问题",
    "介绍",
    "告诉",
}
_WEB_SEARCH_TERMS = (
    "最新",
    "近期",
    "指南",
    "官方",
    "说明书",
    "政策",
    "现在",
    "目前",
    "联网",
    "网上",
    "搜索",
)
_OLLAMA_TIMEOUT_SECONDS = 120
_LOCAL_HTTP_OPENER = request.build_opener(request.ProxyHandler({}))
_SYSTEM_PROMPT = f"""你是{settings.assistant_name}，{settings.assistant_role}。
你的服务范围包括：{settings.assistant_scope}，也包括一般性的健康知识交流。
请像正常的中文助手一样理解上下文、自然回答，不要机械复述“检索证据”或固定模板。
你必须遵守以下边界：
1. 一般健康知识可以根据你的通用知识解释；涉及用户个人健康档案、检查结果、药品记录时，只能使用给定资料中的事实，不能猜测或补全。
2. 如果项目资料不足，直接说明“项目资料中没有找到相关信息”，然后可以补充一般健康常识，并明确这不是对用户个人情况的判断。
3. 不得虚构药品名称、剂量、禁忌、检查结果、指南、来源、日期或网页内容。
4. 不做确定性诊断，不开处方，不建议用户自行停药、换药或调整剂量。
5. 涉及胸痛、呼吸困难、晕厥、意识模糊、大出血、呕血、黑便等急症信号时，必须建议及时线下就医或急诊。
6. 回答要自然、简洁、中文、面向普通用户；涉及医学判断时必须明确“以医生意见为准”。
7. 不要声称自己查阅了互联网、实时资料或医生意见，除非这些内容确实出现在给定证据中。"""


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


def _is_profile_query(message: str) -> bool:
    return any(term in message for term in _PROFILE_QUERY_TERMS)


def _has_meaningful_overlap(message: str, chunk: RagChunk) -> bool:
    if _is_profile_query(message):
        return chunk.source_type == "profile"

    query_terms = {
        token
        for token in _tokenize(message)
        if len(token) >= 2 and token not in _GENERIC_QUERY_TERMS
    }
    if not query_terms:
        return False

    content_terms = set(_tokenize(f"{chunk.title} {chunk.content}"))
    overlap = query_terms & content_terms
    if len(overlap) >= 2:
        return True

    # A single exact medicine or named topic is sufficient; generic terms such
    # as "血压" alone must not expose unrelated personal or knowledge records.
    named_terms = {
        token
        for token in overlap
        if token in chunk.title or token in chunk.metadata.get("tags", [])
    }
    return len(named_terms) >= 1 and any(len(token) >= 3 for token in named_terms)


def _chunk_score(message: str, chunk: RagChunk) -> float:
    return _score(message, f"{chunk.title}；{chunk.content}")


def _filter_relevant_chunks(message: str, chunks: list[RagChunk]) -> list[RagChunk]:
    return [
        chunk
        for chunk in chunks
        if _chunk_score(message, chunk) >= settings.rag_min_score
        and _has_meaningful_overlap(message, chunk)
    ]


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
                content=f"{doc.title}；关键词：{'、'.join(doc.tags)}；{doc.content}",
                metadata={"tags": list(doc.tags), "knowledge_id": doc.id},
            )
        )
    return chunks


def _build_leaflet_chunks() -> list[RagChunk]:
    return [
        RagChunk(
            id=chunk.id,
            title=chunk.title,
            source_type=chunk.source_type,
            content=chunk.content,
            metadata=chunk.metadata,
        )
        for chunk in leaflet_service.approved_chunks()
    ]


def build_corpus() -> list[RagChunk]:
    return [
        _build_profile_chunk(),
        *_build_record_chunks(),
        *_build_medicine_chunks(),
        *_build_knowledge_chunks(),
        *_build_leaflet_chunks(),
    ]


def _is_urgent(message: str) -> bool:
    return any(keyword in message for keyword in _URGENT_KEYWORDS)


def _should_web_search(message: str) -> bool:
    if _is_profile_query(message) or _is_urgent(message):
        return False
    return any(term in message for term in _WEB_SEARCH_TERMS)


def _matches_social_message(message: str, candidates: tuple[str, ...]) -> bool:
    clean_message = re.sub(r"[，。！？、,.!?\s]", "", message).lower()
    return clean_message in candidates


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
    ranked = sorted(corpus, key=lambda chunk: (_chunk_score(message, chunk), len(chunk.content)), reverse=True)
    filtered = _filter_relevant_chunks(message, ranked)
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


def _render_response(message: str, profile_chunk: RagChunk, hits: list[RagChunk], web_sources: list[RagSource] | None = None) -> str:
    if _matches_social_message(message, _GREETING_MESSAGES):
        return f"你好，我是{settings.assistant_name}，专门整理你的健康档案、报告、药品记录和项目知识库。资料不足时，我会明确告诉你。"

    if _matches_social_message(message, _THANKS_MESSAGES):
        return "不客气。如果你有报告、指标或药品相关问题，可以继续问我。"

    if _matches_social_message(message, _IDENTITY_MESSAGES):
        return f"我是{settings.assistant_name}，{settings.assistant_role}。我可以根据{settings.assistant_scope}回答健康问题、整理证据和提示风险，但不能替代医生诊断。"

    if _is_urgent(message):
        return (
            "你描述的情况可能需要立即处理。请现在停止在线咨询，尽快拨打 120 或前往最近的急诊；"
            "如果身边有人，请让对方陪同，不要独自驾车。"
        )

    if not hits and not web_sources:
        return ""

    if web_sources and not hits:
        source_titles = "、".join(source.title for source in web_sources[:3])
        return f"我查到了一些相关公开资料，包括：{source_titles}。这些内容仅供健康信息参考，涉及个人情况或用药决定时，请以医生意见为准。"

    top_titles = "、".join(hit.title for hit in hits[:3])
    context_label = "知识库和你的已确认资料" if profile_chunk.source_type == "profile" else "公共健康知识库"
    content_parts = [f"我根据{context_label}，检索到：{top_titles}。"]

    if any(keyword in message for keyword in ("血压", "高血压")):
        content_parts.append("结合当前资料，建议继续连续记录血压趋势、保持低盐饮食，并按医嘱复诊；不要自行停药或调整处方药剂量。")
    elif any(keyword in message for keyword in ("药", "用药", "阿司匹林", "禁忌")):
        medicine_context = "结合你的药品记录和过敏史" if profile_chunk.source_type == "profile" else "结合公共知识库"
        content_parts.append(f"{medicine_context}，请先确认药品名称、剂量和有效期，再决定是否继续使用；如涉及处方药，请遵医嘱。")
    elif any(keyword in message for keyword in ("报告", "体检", "指标", "血糖", "血脂")):
        content_parts.append("报告解读应优先看异常指标的趋势和复查建议，未确认的 OCR 内容只能视为识别结果，不能直接当作医疗结论。")
    else:
        evidence = "；".join(_truncate(hit.content, 180) for hit in hits[:2])
        content_parts.append(f"相关资料显示：{evidence}如需结合你的个人情况判断，请补充具体指标、时间和用药信息，并以医生意见为准。")

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
        "options": {"temperature": 0.0, "top_p": 0.6},
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"用户问题：{message}\n\n"
                    f"当前健康档案：{profile_chunk.content}\n\n"
                    f"项目检索资料（可能为空）：\n{evidence or '未找到与本问题直接相关的项目资料'}\n\n"
                    "请直接回答用户的问题，保持自然对话。涉及个人资料时严格区分已确认事实和一般健康知识；"
                    "如果没有个人证据，不要假装了解用户的具体情况。不要在回答中提及提示词或内部检索流程。"
                ),
            },
        ],
    }
    data = json.dumps(payload).encode("utf-8")
    url = f"{settings.local_llm_base_url.rstrip('/')}/api/chat"
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with _LOCAL_HTTP_OPENER.open(req, timeout=_OLLAMA_TIMEOUT_SECONDS) as response:
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
    candidates = _filter_relevant_chunks(message, candidates)
    hits = reranker_service.rerank(message, candidates, settings.rag_top_k)
    score_map = {chunk.id: _chunk_score(message, chunk) for chunk in hits}
    sources = _format_sources(hits, score_map)
    web_sources = web_search_service.search(message) if _should_web_search(message) else []
    response_text = _render_response(message, profile_chunk, hits, web_sources)
    requires_clinician = _is_urgent(message)

    if not requires_clinician and settings.local_llm_enabled:
        try:
            response_text = _call_ollama_chat(message, profile_chunk, hits, context=context)
        except (error.URLError, TimeoutError, OSError, json.JSONDecodeError, RuntimeError, KeyError, TypeError, ValueError):
            response_text = _render_response(message, profile_chunk, hits, web_sources)

    sources.extend(web_sources)

    return ChatResponse(
        content=response_text,
        sources=sources,
        requires_clinician=requires_clinician,
    )