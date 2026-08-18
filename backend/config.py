"""
Configuration management using Pydantic settings.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/karna_kavach"
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_KEY: str = ""

    # LLM APIs
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379"

    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Security
    SECRET_KEY: str = "change-this-in-production"
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    # Model Configuration
    MODEL_PATH: str = "backend/models/fraud_classifier_v1.pkl"
    SYNTHETIC_DATA_PATH: str = "data/synthetic_transactions/transactions.csv"
    ATTACK_TAXONOMY_PATH: str = "data/attack_taxonomy.json"

    # LLM Settings
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GROQ_MODEL: str = "qwen/qwen3.6-27b"
    MAX_TOKENS: int = 2048
    TEMPERATURE: float = 0.7

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()
