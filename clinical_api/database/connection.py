"""
Database connection and session management
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator

from clinical_api.config import DATABASE_PATH


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        yield conn
    finally:
        conn.close()


def execute_query(query: str, params: tuple = ()) -> list:
    """Execute a SELECT query and return results"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()


def execute_non_query(query: str, params: tuple = ()) -> None:
    """Execute an INSERT/UPDATE/DELETE query"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()


def execute_many(query: str, params_list: list) -> None:
    """Execute multiple queries with different parameters"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(query, params_list)
        conn.commit()