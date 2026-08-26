# my-uniapp-demo

这是一个前后端分离项目：

```text
my-uniapp-demo/
  frontend/    uni-app 小程序前端
  backend/     Python/FastAPI 后端 API
```

## 前端

前端目录：`frontend/`

使用 HBuilderX 或微信开发者工具时，请打开：

```text
/Volumes/SHARE/my-uniapp-demo/frontend
```

前端 API 配置：

```text
frontend/config/api.config.js
```

## 后端

后端目录：`backend/`

启动方式：

```text
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

默认接口地址：

```text
http://localhost:8000/api
```

健康检查：

```text
GET http://localhost:8000/api/ping
```

## 功能模块

- OCR 报告识别：`/api/ocr`
- 药品管理：`/api/medicines`
- 健康档案：`/api/health`
- AI 问答：`/api/ai`

## RAG / AI 接入

后端已经有一个最小可用的医疗 RAG 骨架：

```text
backend/app/services/ai_service.py
backend/app/services/rag_service.py
backend/app/services/knowledge_base.py
```

当前版本先用内存健康档案、药品记录、报告记录和本地知识库做检索，回答会返回 `sources` 和 `safety_notice`。后续可以按这个顺序替换：

1. MySQL 保存用户、档案、药品、报告、指标和审计日志。
2. Qdrant 保存确认后的报告分块、说明书和医学知识向量。
3. 本地 Embedding / Reranker 负责召回和重排序。
4. 本地 LLM 只基于检索证据生成回答。

本地 MySQL + Qdrant 可用 Docker Compose 启动：

```text
docker compose up -d mysql qdrant
```
