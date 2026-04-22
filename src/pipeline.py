"""End-to-end pipeline orchestration."""
from __future__ import annotations
from typing import Dict, Any
import pandas as pd

from src.config import load_config
from src.data_generator import generate_and_save
from src.cleaning import clean_sales
from src.features import engineer_features
from src.storage import save_to_sqlite, load_from_sqlite, db_exists
from src.logger import get_logger

log = get_logger(__name__)


def run_pipeline(force: bool = False, cfg: Dict[str, Any] | None = None) -> pd.DataFrame:
    """Run ingestion -> cleaning -> features -> storage. Returns final df."""
    cfg = cfg or load_config()
    if not force and db_exists(cfg):
        log.info("DB exists; loading cached processed data.")
        return load_from_sqlite(cfg)

    log.info("Running full pipeline...")
    csv_path = generate_and_save(cfg)
    raw = pd.read_csv(csv_path, parse_dates=["Date"])
    cleaned = clean_sales(raw)
    enriched = engineer_features(cleaned)
    save_to_sqlite(enriched, cfg)
    return enriched
