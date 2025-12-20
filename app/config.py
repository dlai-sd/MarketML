"""
Configuration management for MarketML application.
Uses pydantic-settings for environment variable validation.
"""

from typing import Optional, Literal
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator

from app.constants import (
    API_V1_PREFIX,
    DEFAULT_DB_URL,
    API_VERSION
)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_env: Literal["development", "staging", "production"] = Field(
        default="development", 
        alias="APP_ENV",
        description="Application environment"
    )
    app_debug: bool = Field(default=True, alias="APP_DEBUG")
    app_log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", 
        alias="APP_LOG_LEVEL"
    )
    secret_key: str = Field(
        default="dev-secret-key-change-in-production", 
        alias="SECRET_KEY",
        min_length=20
    )
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key_production(cls, v: str, info) -> str:
        """Ensure secret key is changed in production."""
        if info.data.get("app_env") == "production" and v == "dev-secret-key-change-in-production":
            raise ValueError("Must set custom SECRET_KEY in production")
        return v
    
    # API
    api_v1_prefix: str = Field(default=API_V1_PREFIX, alias="API_V1_PREFIX")
    api_title: str = Field(default="MarketML Persona Builder API", alias="API_TITLE")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT", ge=1, le=65535)
    api_version: str = Field(default=API_VERSION, alias="API_VERSION")
    
    # Database
    database_url: str = Field(default=DEFAULT_DB_URL, alias="DATABASE_URL")
    
    # Redis
    redis_host: str = Field(default="redis", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    
    @property
    def redis_url(self) -> str:
        """Construct Redis URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"
    
    # Celery
    celery_broker_url: str = Field(default="redis://redis:6379/0", alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(default="redis://redis:6379/0", alias="CELERY_RESULT_BACKEND")
    
    # Qdrant
    qdrant_host: str = Field(default="qdrant", alias="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, alias="QDRANT_PORT")
    
    @property
    def qdrant_url(self) -> str:
        """Construct Qdrant URL."""
        return f"http://{self.qdrant_host}:{self.qdrant_port}"
    
    # Scraping
    scraper_timeout: int = Field(default=30, alias="SCRAPER_TIMEOUT")
    scraper_max_retries: int = Field(default=3, alias="SCRAPER_MAX_RETRIES")
    scraper_rate_limit: float = Field(default=1.0, alias="SCRAPER_RATE_LIMIT")
    user_agent: str = Field(
        default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        alias="USER_AGENT"
    )
    
    # LinkedIn (optional)
    linkedin_email: Optional[str] = Field(default=None, alias="LINKEDIN_EMAIL")
    linkedin_password: Optional[str] = Field(default=None, alias="LINKEDIN_PASSWORD")
    linkedin_session_cookie: Optional[str] = Field(default=None, alias="LINKEDIN_SESSION_COOKIE")
    
    # Google (optional)
    google_email: Optional[str] = Field(default=None, alias="GOOGLE_EMAIL")
    google_app_password: Optional[str] = Field(default=None, alias="GOOGLE_APP_PASSWORD")
    
    # LLM API
    deepseek_api_key: Optional[str] = Field(default=None, alias="DEEPSEEK_API_KEY")
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com/v1",
        alias="DEEPSEEK_BASE_URL"
    )
    
    # Feature Flags
    enable_llm_fallback: bool = Field(default=True, alias="ENABLE_LLM_FALLBACK")
    enable_caching: bool = Field(default=True, alias="ENABLE_CACHING")
    enable_monitoring: bool = Field(default=True, alias="ENABLE_MONITORING")
    
    # Monitoring
    prometheus_port: int = Field(default=9090, alias="PROMETHEUS_PORT")
    grafana_port: int = Field(default=3000, alias="GRAFANA_PORT")
    
    # Azure
    azure_subscription_id: Optional[str] = Field(default=None, alias="AZURE_SUBSCRIPTION_ID")
    azure_resource_group: str = Field(default="marketml-rg", alias="AZURE_RESOURCE_GROUP")
    azure_location: str = Field(default="centralindia", alias="AZURE_LOCATION")
    azure_container_registry: str = Field(default="marketmlacr", alias="AZURE_CONTAINER_REGISTRY")
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        populate_by_name = True


# Global settings instance
settings = Settings()
