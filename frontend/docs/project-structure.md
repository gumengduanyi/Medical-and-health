# 项目结构说明

当前目录是前后端分离后的 `frontend/` 子项目，负责 uni-app 小程序前端。Python/FastAPI 后端服务位于项目根目录的 `backend/`。

## 目录约定

```text
config/                  后端接口地址、环境配置
services/                统一请求封装和业务接口模块
services/modules/        按业务拆分的 API service
constants/               路由、业务枚举和常量
store/                   本地状态/缓存封装，后续可替换为 Pinia/Vuex
store-recovered/         从恢复改动中保留的认证状态模块
types/                   领域数据结构约定
utils/                   通用工具，例如路由跳转
components/              原有可复用组件目录
components-recovered/    从构建 source map 恢复的可复用组件
pages/                   原页面目录（当前由工作区同步清理）
pages-recovered/         当前实际使用的恢复页面目录
static/                  静态资源
```

## 页面归属

```text
pages-recovered/index/              首页仪表盘
pages-recovered/medication/         药箱主页
pages-recovered/health_records/     健康档案
pages-recovered/mine/               我的/设置
pages-recovered/medicine_form/      药品录入
pages-recovered/healthInfo/         个人健康信息
pages-recovered/ocr_scan/           OCR 报告识别
pages-recovered/ai_chat/            AI 健康问答
```

## 后端接入位置

- 修改接口基础地址：`config/api.config.js`
- 新增接口模块：`services/modules/*.service.js`
- 页面中优先调用 service，不直接写 `uni.request`
- 后端项目目录：`../backend/`
- 当前默认后端地址：`http://localhost:8000/api`

## 建议后端模块

```text
/api/ocr                 OCR 识别
/api/medicines           药品管理
/api/health              健康档案和指标
/api/ai                  AI 对话和建议
/api/auth                登录/用户授权
```

## 后续建议

1. 后端确定接口后，只改 `config/api.config.js` 和 `services/modules/*`。
2. 页