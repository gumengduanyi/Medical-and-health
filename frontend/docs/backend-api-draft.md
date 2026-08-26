# 后端接口草案

基础地址默认配置在 `config/api.config.js`：

```text
http://localhost:3000/api
```

## OCR

### POST `/ocr/reports/scan`

上传体检报告、诊断记录、化验单。

请求：`multipart/form-data`

字段：

- `file`: 图片或 PDF
- `sourceType`: `report | diagnosis | lab`

响应示例：

```json
{
  "id": "ocr_001",
  "sourceType": "report",
  "confidence": 94,
  "fields": [
    { "label": "血压", "value": "145/96", "status": "warning" }
  ]
}
```

### POST `/ocr/medicines/scan`

上传药盒或说明书。

## 药品

### GET `/medicines`

获取药品列表。

### POST `/medicines`

新增药品。

```json
{
  "name": "阿司匹林肠溶片",
  "dose": "0.1g × 1片，饭后",
  "stock": 60,
  "expire": "2027-12-10"
}
```

## 健康档案

### GET `/health/profile`

获取个人健康信息。

### POST `/health/profile`

保存个人健康信息。

### GET `/health/records`

获取报告、诊疗记录。

### GET `/health/metrics`

获取指标趋势。

## AI

### POST `/ai/chat`

发送健康问答消息。

```json
{
  "message": "我的血压为什么偏高？",
  "contextIds": ["record_001", "medicine_001"]
}
```

### GET `/ai/advice`

获取首页 AI 建议。
