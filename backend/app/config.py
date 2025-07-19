"""
Configuration management for DiagnoAssist Backend
"""
from typing import List
from pydantic import validator
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database Configuration
    mongodb_uri: str
    mongodb_database: str = "DiagnoAssist"
    
    # FHIR Server Configuration
    fhir_server_url: str = "http://localhost:8080/fhir"
    
    # AI Configuration
    gemini_api_key: str
    
    # Authentication
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    project_name: str = "DiagnoAssist Backend"
    project_version: str = "1.0.0"
    
    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379"
    
    # WebSocket Configuration
    ws_heartbeat_interval: int = 30
    
    @validator("cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            # Handle string format from environment variable
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError("CORS origins must be a list or comma-separated string")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings"""
    return settings