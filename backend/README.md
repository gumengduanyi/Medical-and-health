# Python FastAPI 后端

用于给 uni-app 前端提供健康档案、药品管理、OCR 识别和 AI 问答接口。

当前 AI 问答已接入一个最小可用的医疗 RAG 骨架：

- MySQL / 向量库后续可替换为正式实现
- 先用个人健康档案、药品记录、体检报告和本地知识库做证据检索
- 回答会返回来源列表和安全提示，避免无证据输出

## RAG 配置

当前默认使用内存数据和本地知识库，便于先跑通医疗 RAG 流程。后续切换到 MySQL、Qdrant 和本地模型时，优先通过 `.env` 配置：

```bash
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/health_assistant
UPLOAD_DIR=./uploads
# 手机扫码访问时使用可被手机访问的局域网地址，例如 http://192.168.1.100:8000
PUBLIC_BASE_URL=
VECTOR_DB_URL=http://localhost:6333
LOCAL_LLM_BASE_URL=http://localhost:11434
LOCAL_LLM_MODEL=qwen3:14b
FAST_LLM_MODEL=qwen2.5:7b
EMBEDDING_MODEL=bge-m3
RERANKER_MODEL=BAAI/bge-reranker-v2-m3
RERANKER_CACHE_DIR=/Volumes/SHARE/health-assistant-models
RAG_MIN_SCORE=1.0
RAG_TOP_K=4
RAG_CANDIDATE_K=20
```

RAG 的安全规则在 `app/services/rag_service.py` 中集中处理：证据不足时不生成医学结论；急症关键词会触发线下就医提示；所有回答都会返回 `sources` 和 `safety_notice`。未绑定 `profile_id` 的请求只检索公共知识库，不会默认读取个人健康档案、药品或报告。

当前本地模型组合：

- Embedding：`bge-m3`，通过 Ollama `/api/embed` 生成 1024 维向量
- LLM：默认 `qwen3:14b`
- 快速模式：请求 `context.fast_mode=true` 时使用 `qwen2.5:7b`
- Reranker：`BAAI/bge-reranker-v2-m3`，通过 `sentence-transformers` 本地加载

Reranker 模型不会在聊天请求链路里联网下载；如果本地缓存不存在，系统会自动跳过重排序，避免接口被 Hugging Face 网络超时拖慢。首次准备模型可单独执行：

```bash
HF_HUB_DOWNLOAD_TIMEOUT=120 HF_HUB_ETAG_TIMEOUT=120 .venv/bin/python - <<'PY'
from sentence_transformers import CrossEncoder
CrossEncoder('BAAI/bge-reranker-v2-m3', cache_folder='/Volumes/SHARE/health-assistant-models')
PY
```

### 本地启动 MySQL + Qdrant

项目根目录提供了 `docker-compose.yml`：

```bash
docker compose up -d mysql qdrant
```

对应 `.env` 示例：

```bash
DATABASE_URL=mysql+pymysql://health_user:health_password@localhost:3306/health_assistant
VECTOR_DB_URL=http://localhost:6333
VECTOR_COLLECTION=health_documents_bge_m3
```

如果 `VECTOR_DB_URL` 为空或 Qdrant 未启动，系统会自动回退到本地检索，不影响接口启动。

## 启动

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## OCR 配置

后端 OCR 已复现 `/Volumes/SHARE/ocr/test.py` 的 PaddleOCR PPStructureV3 流程：表格识别、版面分析、文档方向分类和文档矫正都保持开启。由于当前主后端虚拟环境是 Python 3.14，而 PaddleOCR 示例环境使用 Python 3.13 且已安装可用依赖，后端通过子进程调用该环境：

```bash
OCR_PYTHON=/Volumes/SHARE/ocr/.venv/bin/python
OCR_OUTPUT_DIR=./uploads/ocr
OCR_TIMEOUT_SECONDS=600
```

接口：

- `POST /api/ocr/reports/scan`：上传报告、化验单、诊断记录图片，返回 `texts`、`layout`、结构化 `fields` 和可视化输出目录。
- `POST /api/ocr/medicines/scan`：上传药盒或药品图片，返回 OCR 文本和药品相关候选字段。
- `GET /api/upload/qrcode`：生成指向手机拍照页的二维码；可通过 `PUBLIC_BASE_URL` 配置局域网地址。
- `POST /api/upload/photo`：保存手机上传的图片并记录上传资产。
- `GET /upload/camera`：手机拍照或相册选择上传页。

OCR 返回结果仍需要用户确认后再入库；未确认内容不要直接进入 RAG 证据池。

## 接口

- `GET /api/ping`
- `GET /api/health/profile`
- `POST /api/health/profile`
- `GET /api/health/records`
- `GET /api/health/metrics`
- `GET /api/medicines`
- `POST /api/medicines`
- `PUT /api/medicines/{id}`
- `DELETE /api/medicines/{id}`
- `POST /api/ocr/reports/scan`
- `POST /api/ocr/medicines/scan`
- `POST /api/ai/chat`
- `GET /api/ai/advice`

## 后续接入 AI

后面可以在 `app/services/ai_service.py` 中替换为本地大模型调用，在 `app/services/rag_service.py` 中替换为 MySQL + 向量数据库 + 本地 Embedding/Reranker。
