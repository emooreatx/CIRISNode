import sqlite3
from typing import Generator
from cirisnode.config import settings

import os
from cirisnode.config import settings

# Use a relative path consistent with init_db.py to avoid path mismatch
DATABASE_PATH = "cirisnode/db/cirisnode.db"
# Ensure the directory exists
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# Dependency for database connection with connection pooling
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """Yield a SQLite connection for request handlers."""
    conn = sqlite3.connect(
        DATABASE_PATH,
        check_same_thread=False,  # Allows connection reuse across threads
        timeout=30  # Adjust timeout for high concurrency
    )
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
