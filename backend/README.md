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
AUTH_TOKEN_SECRET=change-me-in-production
AUTH_TOKEN_TTL_SECONDS=604800
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

- `POST /api/ocr/reports/scan`：上传报告、化验单、诊断记录图片，创建 OCR 异步任务并返回 `jobId`。
- `POST /api/ocr/medicines/scan`：上传药盒或药品图片，创建 OCR 异步任务并返回 `jobId`。
- `GET /api/ocr/jobs/{job_id}`：查询 OCR 任务状态，成功后返回 `texts`、`layout`、结构化 `fields` 和可视化输出目录。
- `POST /api/upload/photo`：保存手机上传的图片并记录上传资产。
- `GET /upload/camera`：手机拍照或相册选择上传页。

药箱 OCR 会先把上传图片保存到 `OCR_OUTPUT_DIR`，再执行 PaddleOCR。识别到药品通用名后，后端会自动调用百度百科浏览器智能体，返回 `leafletCandidate`，其中包含 `作用功效`、`用法用量`、`禁忌` 三个目标章节的候选内容或缺失标记。用户确认入库时，药品记录会写入 `medicines` 表，同时保存 `image_path`、`ocr_output_dir`、`specification`、`manufacturer` 和 `approval_number`；若百度候选可用，还会导入到 `drug_leaflets` 和 `drug_leaflet_sections`，状态保持 `pending_review` 等待人工审核。

## 药品说明书自动采集

浏览器智能体依赖 Playwright Chromium。首次部署后执行 `python -m playwright install chromium`；自动化访问遇到安全验证时会停止并交给人工处理。

说明书采集只保留百度百科浏览器智能体这一条路径。`POST /api/leaflets/auto-discover` 根据药品通用名打开百度百科词条，读取浏览器可见页面，并返回低置信度候选、实际找到的章节和缺失章节。系统不调用百度百科公开接口，也不接受其他网站 URL 或外部说明书 URL。

批准文号、生产企业和规格可以作为 OCR 识别结果保存并供人工审核，但不会改变百度百科词条的访问路径。自动发现只读取和解析页面，不写入说明书数据库。若页面出现百度安全验证、登录要求、空页面或访问异常，候选会返回 `human_verification_required`，系统停止自动读取，不绕过验证。

例如：

```bash
curl -X POST http://localhost:8000/api/leaflets/auto-discover \
	-H 'Content-Type: application/json' \
	-d '{
		"generic_name": "阿托伐他汀钙片",
		"manufacturer": "生产企业名称",
		"approval_number": "国药准字H00000000",
		"specification": "20mg"
	}'
```

当前只收录三个知识类别：`作用功效`、`用法用量`、`禁忌`。正式说明书的“适应症”“作用与功效”和“药品禁忌”等标题会归一化；其他章节不会写入知识库。

也可以按药品通用名自动定位百度百科词条。`/api/leaflets/import-baike` 会通过正常 Chromium 浏览器读取词条的可见页面并保存 HTML 原文，再按目标章节导入；它不调用百度百科公开接口。页面若要求安全验证，接口会返回人工接管提示；导入后仍是 `pending_review`，不能替代药品生产企业或监管机构发布的正式说明书：

```bash
curl -X POST http://localhost:8000/api/leaflets/import-baike \
	-H 'Content-Type: application/json' \
	-d '{
		"generic_name": "阿托伐他汀钙片",
		"specification": "20mg"
	}'
```

导入结果默认为 `pending_review`。人工确认来源、药品身份和章节内容后，调用 `POST /api/leaflets/{id}/approve` 发布；`GET /api/leaflets` 可以查看导入记录。

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
