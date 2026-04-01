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
    BACKEND_CORS_ORIGINS: list[str] = ["*"] # Consider restricting in production
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
