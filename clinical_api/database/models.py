"""
Database table definitions and initialization
"""

from clinical_api.database.connection import execute_non_query, execute_query


def create_tables():
    """Create database tables if they don't exist"""
    create_icd10_table_sql = """
        CREATE TABLE IF NOT EXISTS icd10_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            category TEXT,
            search_terms TEXT
        )
    """
    execute_non_query(create_icd10_table_sql)


def table_exists(table_name: str) -> bool:
    """Check if a table exists in the database"""
    query = """
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    """
    result = execute_query(query, (table_name,))
    return len(result) > 0


def table_has_data(table_name: str) -> bool:
    """Check if a table has any data"""
    query = f"SELECT COUNT(*) FROM {table_name}"
    result = execute_query(query)
    return result[0][0] > 0 if result else False