"""
Configuration settings for the Clinical Documentation API
"""

import os
from pathlib import Path

# Database settings
DATABASE_PATH = os.getenv("DATABASE_PATH", "icd10.db")
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# API settings
API_TITLE = "Clinical Documentation API"
API_DESCRIPTION = "API for clinical documentation with ICD-10 code support"
API_VERSION = "1.0.0"

# CORS settings
ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "http://localhost:5173",  # Vite dev server
]

# Search settings
DEFAULT_SEARCH_LIMIT = 10
MAX_SEARCH_LIMIT = 50
MIN_QUERY_LENGTH = 2
MIN_WORD_LENGTH = 3

# Server settings
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
RELOAD = os.getenv("RELOAD", "True").lower() == "true"