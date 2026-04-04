from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "CITMS (Centralized IT Management System)"
    VERSION: str = "3.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "yoursecretkey_changethisinproduction"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Logs
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"
    
    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["*"]
    
    # SMTP / Notifications (Module 7)
    EMAILS_ENABLED: bool = True
    SMTP_HOST: str = "smtp.internal.citms.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    EMAILS_FROM_EMAIL: str = "noreply@citms.internal"
    ADMIN_EMAIL: str = "admin@citms.internal"

    # Storage / Reports (Module 8)
    S3_ENDPOINT: str = "minio:9000"
    S3_ACCESS_KEY: str = "minio_admin"
    S3_SECRET_KEY: str = "minio_secret"
    S3_BUCKET_REPORTS: str = "citms-reports"
    S3_SECURE: bool = False

    # RustDesk Remote Control (v3.6 §5.5)
    RUSTDESK_API_URL: str = "http://rustdesk-api.internal:21114"
    # Token used by CITMS to call RustDesk's administrative API
    RUSTDESK_API_TOKEN: str = "citms_rustdesk_admin_token"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
