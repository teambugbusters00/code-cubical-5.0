"""
Configuration settings for Finance AI Assistant
"""

import os
from typing import List, Optional
from pydantic import BaseModel, validator
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Backend Configuration
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    backend_reload: bool = True

    # Frontend Configuration
    frontend_host: str = "0.0.0.0"
    frontend_port: int = 8501

    # Data Processing Configuration
    pathway_host: str = "0.0.0.0"
    pathway_port: int = 8765

    # External API Keys
    alpha_vantage_api_key: Optional[str] = None
    news_api_key: Optional[str] = None
    redis_url: Optional[str] = None

    # Database Configuration
    database_url: Optional[str] = None

    # MongoDB Configuration
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_database: str = "finance_ai_assistant"
    mongodb_username: Optional[str] = None
    mongodb_password: Optional[str] = None
    mongodb_auth_source: str = "admin"

    # Database Collections
    stocks_collection: str = "stocks"
    news_collection: str = "news"
    portfolios_collection: str = "portfolios"
    users_collection: str = "users"
    chat_history_collection: str = "chat_history"
    technical_analysis_collection: str = "technical_analysis"

    # Database Settings
    enable_mongodb: bool = True
    enable_mongodb_persistence: bool = True

    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "logs/finance_assistant.log"

    # Data Sources
    yahoo_finance_enabled: bool = True
    alpha_vantage_enabled: bool = False

    # Cache Configuration
    cache_ttl_seconds: int = 300
    enable_redis_cache: bool = False

    # Security
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8501", "http://localhost:8000"]
    secret_key: str = "your-secret-key-change-this-in-production"

    # Feature Flags
    enable_real_time_updates: bool = True
    enable_technical_analysis: bool = True
    enable_news_integration: bool = False
    enable_portfolio_tracking: bool = False

    # Data Update Intervals (in seconds)
    price_update_interval: int = 60
    news_update_interval: int = 300
    analysis_update_interval: int = 120

    # Data directories
    data_dir: str = "data"
    logs_dir: str = "logs"

    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("backend_port", "frontend_port", "pathway_port")
    def validate_ports(cls, v):
        if not (1 <= v <= 65535):
            raise ValueError("Port must be between 1 and 65535")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Ensure required directories exist
Path(settings.data_dir).mkdir(exist_ok=True)
Path(settings.logs_dir).mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)