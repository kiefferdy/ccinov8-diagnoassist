"""
Settings Configuration for DiagnoAssist
Fixed for Pydantic V2 and pydantic-settings
"""

import os
from functools import lru_cache
from typing import List, Optional

try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for older pydantic versions
    from pydantic import BaseSettings

from pydantic import validator


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Application Settings
    app_name: str = "DiagnoAssist"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Supabase Settings (Your current working setup)
    supabase_url: str = ""
    supabase_anon_key: str = ""
    
    # Database Settings (Optional - for future SQLAlchemy direct connection)
    database_url: Optional[str] = None
    database_echo: bool = False
    
    # Security Settings
    secret_key: str = "your-secret-key-change-this"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Settings
    api_v1_str: str = "/api/v1"
    cors_origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8080"
    ]
    
    # FHIR Settings
    fhir_base_url: str = "http://localhost:8000/fhir"
    fhir_version: str = "R4"
    fhir_server_name: str = "DiagnoAssist FHIR Server"
    fhir_server_version: str = "1.0.0"
    fhir_publisher: str = "DiagnoAssist Medical Systems"
    
    # AI Settings
    openai_api_key: Optional[str] = None
    ai_model: str = "gpt-4"
    ai_temperature: float = 0.3
    ai_max_tokens: int = 1500
    
    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: Optional[str] = None
    
    # Performance Settings
    request_timeout: int = 30
    max_request_size: int = 100 * 1024 * 1024  # 100MB
    
    # Validation
    @validator('environment')
    def validate_environment(cls, v):
        valid_envs = ['development', 'staging', 'production', 'testing']
        if v not in valid_envs:
            return 'development'
        return v
    
    @validator('supabase_url')
    def validate_supabase_url(cls, v):
        if v and not v.startswith('https://'):
            raise ValueError('Supabase URL must start with https://')
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()