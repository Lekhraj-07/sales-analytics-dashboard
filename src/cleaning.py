"""Data cleaning layer."""
from __future__ import annotations
import pandas as pd

from src.logger import get_logger

log = get_logger(__name__)


REQUIRED_COLUMNS = ["Date", "Customer_ID", "Product", "Category",
                     "Region", "Quantity", "Revenue", "Cost"]


def clean_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Clean: dedupe, fill/drop nulls, enforce types, derive Profit."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    before = len(df)
    df = df.drop_duplicates().copy()
    log.info("Removed %d duplicate rows", before - len(df))

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    for col in ("Revenue", "Cost", "Quantity"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows missing critical numerics or dates
    critical = ["Date", "Revenue", "Cost", "Quantity"]
    dropped = df[critical].isna().any(axis=1).sum()
    df = df.dropna(subset=critical)
    log.info("Dropped %d rows with missing critical fields", dropped)

    # Impute categorical nulls
    df["Region"] = df["Region"].fillna("Unknown")
    df["Category"] = df["Category"].fillna("Uncategorized")
    df["Product"] = df["Product"].fillna("Unknown Product")

    # Sanity filters
    df = df[(df["Quantity"] > 0) & (df["Revenue"] >= 0) & (df["Cost"] >= 0)]

    df["Profit"] = (df["Revenue"] - df["Cost"]).round(2)
    df = df.sort_values("Date").reset_index(drop=True)
    log.info("Cleaned dataset: %d rows", len(df))
    return df
