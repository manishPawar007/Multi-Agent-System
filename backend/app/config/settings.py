import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "OmniAgent AI"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "omniagent-ai-super-secret-production-key-change-in-production-2026"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./omniagent.db"

    # Ollama Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Default Local LLM & Embedding Settings
    DEFAULT_LLM_PROVIDER: str = "ollama"
    DEFAULT_LLM_MODEL: str = "llama3.2:latest"
    DEFAULT_EMBEDDING_MODEL: str = "nomic-embed-text"
    DEFAULT_TEMPERATURE: float = 0.7
    DEFAULT_MAX_TOKENS: int = 2048
    DEFAULT_TOP_P: float = 0.95

    # Optional Fallback Cloud Model (Google Gemini Free API)
    ENABLE_CLOUD_GEMINI: bool = False
    GEMINI_API_KEY: str = ""

    # Storage Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    UPLOAD_DIR: Path = BASE_DIR / "backend" / "uploads"
    CHROMA_DIR: Path = BASE_DIR / "backend" / "chroma_db"
    LOG_DIR: Path = BASE_DIR / "backend" / "logs"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.CHROMA_DIR.mkdir(parents=True, exist_ok=True)
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
