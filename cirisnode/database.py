import sqlite3
from typing import Generator

DATABASE_PATH = "cirisnode.db"

# Dependency for database connection

def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield a SQLite connection for request handlers."""
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
