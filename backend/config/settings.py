import os
from typing import Optional, List
from pydantic import BaseSettings, validator
from functools import lru_cache

class Settings(BaseSettings):
    """
    Application settings with environment variable support
    """
    
    # Basic App Settings
    app_name: str = "DiagnoAssist API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"  # development, staging, production
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Database Settings
    database_url: str = "sqlite:///./diagnoassist.db"
    database_echo: bool = False  # Set to True for SQL logging
    
    # Security Settings
    secret_key: str = "your-super-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS Settings
    cors_origins: List[str] = [
        "http://localhost:3000",  # React dev server
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173"
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # FHIR Settings
    fhir_version: str = "4.0.1"
    fhir_base_url: str = "https://diagnoassist.com/fhir/R4"
    fhir_publisher: str = "DiagnoAssist"
    fhir_contact_email: str = "support@diagnoassist.com"
    
    # External FHIR Servers
    external_fhir_servers: List[str] = [
        "https://r4.ontoserver.csiro.au/fhir",  # CSIRO Ontology Server
        "https://tx.fhir.org/r4"  # FHIR Terminology Server
    ]
    
    # AI Service Settings
    ai_service_url: Optional[str] = None
    ai_service_api_key: Optional[str] = None
    ai_service_timeout: int = 30
    ai_service_max_retries: int = 3
    
    # Medical Coding Settings
    icd10_api_url: Optional[str] = None
    loinc_api_url: Optional[str] = None
    snomed_api_url: Optional[str] = None
    
    # File Storage Settings
    upload_max_size: int = 10 * 1024 * 1024  # 10MB
    upload_allowed_types: List[str] = [
        "image/jpeg", "image/png", "image/gif",
        "application/pdf", "text/plain",
        "application/dicom"  # Medical imaging
    ]
    file_storage_path: str = "./uploads"
    
    # Email Settings (for notifications)
    smtp_server: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_use_tls: bool = True
    
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
    
    @validator('database_url')
    def validate_database_url(cls, v):
        if v.startswith('sqlite'):
            # Ensure SQLite directory exists
            db_path = v.replace('sqlite:///', '')
            os.makedirs(os.path.dirname(db_path) if os.path.dirname(db_path) else '.', exist_ok=True)
        return v
    
    @validator('cors_origins', pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('environment')
    def validate_environment(cls, v):
        valid_envs = ['development', 'staging', 'production']
        if v not in valid_envs:
            raise ValueError(f'Environment must be one of: {valid_envs}')
        return v


@lru_cache()
def get_settings() -> Settings:
    """
    Create settings instance with caching
    """
    return Settings()
