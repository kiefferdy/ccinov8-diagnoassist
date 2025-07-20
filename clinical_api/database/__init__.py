"""Database layer for ICD-10 API"""

from .connection import get_db_connection, execute_query, execute_non_query, execute_many
from .models import create_tables, table_exists, table_has_data
from .seed_data import seed_database

__all__ = [
    "get_db_connection", "execute_query", "execute_non_query", "execute_many",
    "create_tables", "table_exists", "table_has_data", "seed_database"
]

# ---