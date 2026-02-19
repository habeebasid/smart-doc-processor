from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings from environment variables"""

    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True

    # Database
    database_url: str
    postgres_user: str = "docuser"  # Added
    postgres_password: str = "docpass"  # Added
    postgres_db: str = "smart_doc_db"  # Added

    # Groq API
    groq_api_key: str
    groq_model: str = "llama3-70b-8192"
    llm_provider: str = "groq"  # Added

    # Embedding Service
    embedding_provider: str = "voyage"
    voyage_api_key: str = ""

    # Storage
    upload_dir: str = "./storage/uploads"
    processed_dir: str = "./storage/processed"
    max_file_size: int = 10485760

    # RAG Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200
    top_k_results: int = 5

    # Redis & MCP
    redis_url: str = "redis://localhost:6379/0"  # Added
    mcp_server_port: int = 3000  # Added

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    """Cached settings instance"""
    return Settings()
