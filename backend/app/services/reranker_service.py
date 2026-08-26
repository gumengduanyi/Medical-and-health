from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from app.core.config import settings


_MODEL: Any | None = None
_LOAD_FAILED_UNTIL = 0.0
_FAILURE_COOLDOWN_SECONDS = 600


def _local_snapshot_path(cache_dir: Path) -> Path | None:
    model_dir = cache_dir / settings.reranker_model.replace("/", "--")
    if not model_dir.exists():
        model_dir = cache_dir / f"models--{settings.reranker_model.replace('/', '--')}"
    ref_file = model_dir / "refs" / "main"
    if not ref_file.exists():
        return None

    snapshot_id = ref_file.read_text(encoding="utf-8").strip()
    snapshot_dir = model_dir / "snapshots" / snapshot_id
    if (snapshot_dir / "config.json").exists():
        return snapshot_dir
    return None


def _load_model() -> Any | None:
    global _MODEL, _LOAD_FAILED_UNTIL
    if not settings.reranker_enabled:
        return None
    if _MODEL is not None:
        return _MODEL
    if time.monotonic() < _LOAD_FAILED_UNTIL:
        return None

    try:
        from sentence_transformers import CrossEncoder

        cache_dir = Path(settings.reranker_cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("HF_HOME", str(cache_dir))
        os.environ.setdefault("HF_HUB_CACHE", str(cache_dir / "huggingface"))
        model_path = _local_snapshot_path(cache_dir) or settings.reranker_model
        _MODEL = CrossEncoder(str(model_path), local_files_only=True)
        return _MODEL
    except (ImportError, OSError, RuntimeError, ValueError):
        _LOAD_FAILED_UNTIL = time.monotonic() + _FAILURE_COOLDOWN_SECONDS
        return None


def rerank(query: str, chunks: list[Any], limit: int) -> list[Any]:
    model = _load_model()
    if not model or not chunks:
        return chunks[:limit]

    try:
        scores = model.predict([(query, chunk.content) for chunk in chunks], show_progress_bar=False)
        ranked = sorted(zip(chunks, scores, strict=True), key=lambda item: float(item[1]), reverse=True)
        return [chunk for chunk, _ in ranked[:limit]]
    except (OSError, RuntimeError, ValueError):
        return chunks[:limit]