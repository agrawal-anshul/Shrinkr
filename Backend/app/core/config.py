from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "Shrinkr+"
    API_VERSION: str = "1.0.0"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 1
    RELOAD: bool = True
    
    # CORS
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/shrinkr"
    PYTHONPATH: str = "/app"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour in seconds

    # JWT Auth Config
    SECRET_KEY: str = "shrinkr-dev-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Rate Limiting
    RATE_LIMIT_DEFAULT: int = 100  # requests per window
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour in seconds
    
    # URL Shortener Config
    DEFAULT_URL_CODE_LENGTH: int = 6
    MAX_URL_CODE_LENGTH: int = 20
    MAX_CUSTOM_ALIAS_LENGTH: int = 20
    MAX_BULK_URLS: int = 50
    MAX_DAILY_USER_URLS: int = 1000
    
    # Security
    MIN_PASSWORD_LENGTH: int = 8
    HASH_ALGORITHM: str = "bcrypt"
    PEPPER: str = ""  # Additional secret for password hashing
    
    # Analytics
    ANALYTICS_MAX_DAYS: int = 365
    ANALYTICS_DEFAULT_DAYS: int = 30
    
    # QR Code
    QR_CODE_DEFAULT_SIZE: int = 10
    QR_CODE_MIN_SIZE: int = 5
    QR_CODE_MAX_SIZE: int = 20
    
    # Logging
    LOG_LEVEL: str = "INFO"

    def is_development(self) -> bool:
        return self.ENVIRONMENT.lower() == "development"
    
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# Initialize settings singleton from environment variables
settings = Settings()

# Log settings in development mode
if settings.is_development() and settings.DEBUG:
    import logging
    logger = logging.getLogger("uvicorn")
    logger.info("🔧 Loading settings from environment")
    for setting, value in settings.dict().items():
        # Don't log sensitive settings
        if setting in ["SECRET_KEY", "PEPPER"]:
            logger.info(f"🔧 {setting}: **********")
        else:
            logger.info(f"🔧 {setting}: {value}")