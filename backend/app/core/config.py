from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "智能健康管理 API"
    app_env: str = "development"
    api_prefix: str = "/api"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "*"
    database_url: str = "sqlite:///./health_assistant.db"
    upload_dir: str = "./uploads"
    auth_token_secret: str = "dev-health-assistant-change-me"
    auth_token_ttl_seconds: int = 7 * 24 * 60 * 60
    assistant_name: str = "健康助手 AI"
    assistant_role: str = "本项目的医疗健康资料整理助手"
    assistant_scope: str = "个人健康档案、体检报告、药品记录、药品说明书和项目健康知识库"
    vector_db_url: str = ""
    vector_collection: str = "health_documents_bge_m3"
    local_llm_base_url: str = "http://localhost:11434"
    local_llm_model: str = "qwen3:14b"
    fast_llm_model: str = "qwen2.5:7b"
    local_llm_enabled: bool = False
    embedding_model: str = "bge-m3"
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_enabled: bool = False
    reranker_cache_dir: str = "/Volumes/SHARE/health-assistant-models"
    web_search_enabled: bool = True
    web_search_url: str = "http://127.0.0.1:8080/search"
    web_search_timeout_seconds: int = 8
    web_search_max_results: int = 5
    web_search_domains: str = "gov.cn,nhc.gov.cn,nmpa.gov.cn,who.int,cdc.gov,mayoclinic.org,medlineplus.gov"
    ocr_python: str = "/Volumes/SHARE/ocr/.venv/bin/python"
    ocr_output_dir: str = "./uploads/ocr"
    ocr_timeout_seconds: int = 600
    leaflet_output_dir: str = "./uploads/leaflets"
    leaflet_browser_timeout_seconds: int = 30
    leaflet_browser_ready_timeout_seconds: int = 8
    leaflet_browser_user_data_dir: str = "./runtime/leaflet-browser"
    leaflet_browser_executable_path: str = ""
    leaflet_browser_headless: bool = True
    leaflet_browser_max_retries: int = 1
    leaflet_admin_user_ids: str = ""
    rag_min_score: float = 1.0
    rag_top_k: int = 4
    rag_candidate_k: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def leaflet_admin_user_id_list(self) -> list[str]:
        return [user_id.strip() for user_id in self.leaflet_admin_user_ids.split(",") if user_id.strip()]

settings = Settings()
