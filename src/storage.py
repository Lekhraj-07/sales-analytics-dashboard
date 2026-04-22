"""SQLite storage layer."""
from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Dict, Any
import pandas as pd

from src.logger import get_logger

log = get_logger(__name__)


def save_to_sqlite(df: pd.DataFrame, cfg: Dict[str, Any]) -> Path:
    db_path = Path(cfg["data"]["db_path"])
    db_path.parent.mkdir(parents=True, exist_ok=True)
    table = cfg["data"]["table_name"]
    with sqlite3.connect(db_path) as conn:
        df.to_sql(table, conn, if_exists="replace", index=False)
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_date ON {table}(Date)")
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_region ON {table}(Region)")
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table}_category ON {table}(Category)")
        conn.commit()
    log.info("Persisted %d rows to %s (table=%s)", len(df), db_path, table)
    return db_path


def load_from_sqlite(cfg: Dict[str, Any]) -> pd.DataFrame:
    db_path = Path(cfg["data"]["db_path"])
    table = cfg["data"]["table_name"]
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql(f"SELECT * FROM {table}", conn, parse_dates=["Date"])
    log.info("Loaded %d rows from %s", len(df), db_path)
    return df


def db_exists(cfg: Dict[str, Any]) -> bool:
    return Path(cfg["data"]["db_path"]).exists()
