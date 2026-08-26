from __future__ import annotations

import json
import math
import uuid
from dataclasses import dataclass
from functools import lru_cache
from typing import Any
from urllib import error, request

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, FieldCondition, Filter, IsEmptyCondition, MatchValue, PayloadField, PointStruct, VectorParams
from app.core.config import settings


@dataclass(frozen=True)
class VectorHit:
    id: str
    title: str
    source_type: str
    content: str
    score: float
    metadata: dict[str, Any]


OLLAMA_TIMEOUT_SECONDS = 30
_INDEXED_SIGNATURE: str | None = None


def _is_enabled() -> bool:
    return bool(settings.vector_db_url.strip())


def _client() -> QdrantClient:
    return QdrantClient(url=settings.vector_db_url)


def _ollama_json(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    url = f"{settings.local_llm_base_url.rstrip('/')}{path}"
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with request.urlopen(req, timeout=OLLAMA_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def _normalize(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / magnitude for value in vector]


def embed_text(text: str) -> list[float]:
    clean_text = text.strip() or "空文本"
    try:
        result = _ollama_json("/api/embed", {"model": settings.embedding_model, "input": clean_text})
        embeddings = result.get("embeddings")
        if isinstance(embeddings, list) and embeddings:
            return _normalize([float(value) for value in embeddings[0]])
    except (error.URLError, TimeoutError, OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        pass

    result = _ollama_json("/api/embeddings", {"model": settings.embedding_model, "prompt": clean_text})
    embedding = result.get("embedding")
    if not isinstance(embedding, list) or not embedding:
        raise RuntimeError(f"Ollama model {settings.embedding_model} did not return an embedding")
    return _normalize([float(value) for value in embedding])


@lru_cache(maxsize=1)
def embedding_size() -> int:
    return len(embed_text("健康档案向量维度探测"))


def _point_id(chunk_id: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"health-assistant:{settings.vector_collection}:{chunk_id}"))


def ensure_collection() -> None:
    if not _is_enabled():
        return
    client = _client()
    collections = client.get_collections().collections
    if any(collection.name == settings.vector_collection for collection in collections):
        return
    client.create_collection(
        collection_name=settings.vector_collection,
        vectors_config=VectorParams(size=embedding_size(), distance=Distance.COSINE),
    )


def upsert_documents(chunks: list[Any]) -> None:
    global _INDEXED_SIGNATURE
    if not _is_enabled() or not chunks:
        return
    signature = "|".join(f"{chunk.id}:{hash(chunk.content)}" for chunk in chunks)
    if signature == _INDEXED_SIGNATURE:
        return
    ensure_collection()
    points = []
    for chunk in chunks:
        payload = {
            "chunk_id": chunk.id,
            "title": chunk.title,
            "source_type": chunk.source_type,
            "content": chunk.content,
            **chunk.metadata,
        }
        points.append(
            PointStruct(
                id=_point_id(chunk.id),
                vector=embed_text(chunk.content),
                payload=payload,
            )
        )
    _client().upsert(collection_name=settings.vector_collection, points=points)
    _INDEXED_SIGNATURE = signature


def search(message: str, profile_id: str | None = None, limit: int | None = None) -> list[VectorHit]:
    if not _is_enabled():
        return []

    ensure_collection()
    should = [IsEmptyCondition(is_empty=PayloadField(key="profile_id"))]
    if profile_id:
        should.append(FieldCondition(key="profile_id", match=MatchValue(value=profile_id)))

    query_filter = Filter(should=should)
    result = _client().search(
        collection_name=settings.vector_collection,
        query_vector=embed_text(message),
        query_filter=query_filter,
        limit=limit or settings.rag_top_k,
        with_payload=True,
    )

    hits: list[VectorHit] = []
    for item in result:
        payload = item.payload or {}
        hits.append(
            VectorHit(
                id=str(payload.get("chunk_id", item.id)),
                title=str(payload.get("title", "检索片段")),
                source_type=str(payload.get("source_type", "vector")),
                content=str(payload.get("content", "")),
                score=float(item.score or 0.0),
                metadata={key: value for key, value in payload.items() if key not in {"chunk_id", "title", "source_type", "content"}},
            )
        )
    return hits