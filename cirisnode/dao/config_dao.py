import json
import sqlite3

from cirisnode.schema.config_models import CIRISConfigV1, LLMConfigV1


class ConfigDAO:
    """Data access object for CIRISNode configuration."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                version INTEGER NOT NULL,
                config_json TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def get_config(self) -> CIRISConfigV1:
        cur = self.conn.execute("SELECT config_json FROM config WHERE id = 1")
        row = cur.fetchone()
        if row is None:
            default = CIRISConfigV1(llm=LLMConfigV1())
            self.save_config(default)
            return default
        data = json.loads(row[0])
        return CIRISConfigV1.model_validate(data)

    def save_config(self, config: CIRISConfigV1) -> None:
        config_json = config.model_dump_json()
        self.conn.execute(
            "INSERT OR REPLACE INTO config (id, version, config_json) VALUES (1, ?, ?)",
            (config.version, config_json),
        )
        self.conn.commit()


def get_config_dao(db_conn: sqlite3.Connection) -> ConfigDAO:
    return ConfigDAO(db_conn)

from fastapi import Depends
from cirisnode.database import get_db


def get_config(db=Depends(get_db)) -> CIRISConfigV1:
    conn = next(db) if hasattr(db, "__iter__") and not isinstance(db, (str, bytes)) else db
    dao = ConfigDAO(conn)
    return dao.get_config()
