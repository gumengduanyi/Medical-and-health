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
    public_base_url: str = ""
    vector_db_url: str = ""
    vector_collection: str = "health_documents_bge_m3"
    local_llm_base_url: str = "http://localhost:11434"
    local_llm_model: str = "qwen3:14b"
    fast_llm_model: str = "qwen2.5:7b"
    embedding_model: str = "bge-m3"
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    reranker_enabled: bool = True
    reranker_cache_dir: str = "/Volumes/SHARE/health-assistant-models"
    ocr_python: str = "/Volumes/SHARE/ocr/.venv/bin/python"
    ocr_output_dir: str = "./uploads/ocr"
    ocr_timeout_seconds: int = 600
    rag_min_score: float = 1.0
    rag_top_k: int = 4
    rag_candidate_k: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
