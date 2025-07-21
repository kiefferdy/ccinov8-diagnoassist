"""
Settings Configuration for DiagnoAssist
Uses existing Supabase URL + ANON KEY method
"""

import os
from functools import lru_cache
from typing import List, Optional
from pydantic import BaseSettings, validator


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
    log_file: Optional[str] = "./logs/diagnoassist.log"
    
    # Performance Settings
    worker_processes: int = 1
    max_connections: int = 1000
    connection_pool_size: int = 10
    connection_pool_overflow: int = 20
    
    # Feature Flags
    enable_fhir_validation: bool = True
    enable_ai_diagnosis: bool = True
    enable_external_integrations: bool = False
    enable_audit_logging: bool = True
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @validator('supabase_url')
    def validate_supabase_url(cls, v):
        """Validate Supabase URL"""
        if not v:
            raise ValueError("SUPABASE_URL is required")
        if not v.startswith("https://"):
            raise ValueError("SUPABASE_URL must start with https://")
        if not "supabase.co" in v:
            raise ValueError("SUPABASE_URL must be a valid Supabase URL")
        return v
    
    @validator('supabase_anon_key')
    def validate_supabase_anon_key(cls, v):
        """Validate Supabase anonymous key"""
        if not v:
            raise ValueError("SUPABASE_ANON_KEY is required")
        if len(v) < 100:  # JWT tokens are typically much longer
            raise ValueError("SUPABASE_ANON_KEY appears to be invalid (too short)")
        return v
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        """Parse CORS origins from environment"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment setting"""
        valid_envs = ['development', 'staging', 'production']
        if v not in valid_envs:
            raise ValueError(f'Environment must be one of: {valid_envs}')
        return v
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        """Validate secret key"""
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v
    
    @property
    def is_development(self) -> bool:
        """Check if we're in development environment"""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if we're in production environment"""
        return self.environment == "production"
    
    @property
    def supabase_rest_url(self) -> str:
        """Get Supabase REST API URL"""
        return f"{self.supabase_url}/rest/v1"
    
    def get_supabase_headers(self) -> dict:
        """Get headers for Supabase REST API calls"""
        return {
            'apikey': self.supabase_anon_key,
            'Authorization': f'Bearer {self.supabase_anon_key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=minimal'
        }


@lru_cache()
def get_settings() -> Settings:
    """
    Create settings instance with caching
    """
    return Settings()