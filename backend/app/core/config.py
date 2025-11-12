from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    PROJECT_NAME: str = "Vigil - DevOps Monitoring Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database
    DATABASE_URL: str

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    ALERT_CHECK_INTERVAL_SECONDS: int = 60

    # Prometheus
    PROMETHEUS_URL: str = "http://prometheus:9090"

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]

    # WebSocket
    WS_METRICS_INTERVAL_SECONDS: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
