"""Synthetic but realistic e-commerce sales data generator."""
from __future__ import annotations
from pathlib import Path
from typing import Dict, Any
import numpy as np
import pandas as pd

from src.logger import get_logger

log = get_logger(__name__)


def _product_catalog(categories: Dict[str, list]) -> pd.DataFrame:
    """Build a product catalog with stable unit prices and costs per product."""
    rng = np.random.default_rng(7)
    rows = []
    for cat, products in categories.items():
        for p in products:
            base_price = float(rng.uniform(25, 1500))
            margin = float(rng.uniform(0.18, 0.55))
            unit_cost = round(base_price * (1 - margin), 2)
            rows.append({
                "Product": p,
                "Category": cat,
                "Unit_Price": round(base_price, 2),
                "Unit_Cost": unit_cost,
            })
    return pd.DataFrame(rows)


def generate_sales(cfg: Dict[str, Any]) -> pd.DataFrame:
    """Generate a realistic sales dataset.

    Includes seasonality (Q4 lift), regional weighting, and a small share of
    dirty rows (nulls + duplicates) so the cleaning layer has real work to do.
    """
    seed = int(cfg["data"]["random_seed"])
    n = int(cfg["data"]["rows"])
    rng = np.random.default_rng(seed)

    start = pd.Timestamp(cfg["data"]["start_date"])
    end = pd.Timestamp(cfg["data"]["end_date"])
    days = (end - start).days

    catalog = _product_catalog(cfg["categories"])
    regions = cfg["regions"]
    region_weights = np.array([0.35, 0.27, 0.22, 0.10, 0.06])
    region_weights = region_weights / region_weights.sum()

    # Date with seasonality: Q4 boost
    day_offsets = rng.integers(0, days + 1, size=n)
    dates = start + pd.to_timedelta(day_offsets, unit="D")
    months = dates.month
    season_boost = np.where(np.isin(months, [11, 12]), 1.7,
                    np.where(np.isin(months, [6, 7, 8]), 1.15, 1.0))

    prod_idx = rng.integers(0, len(catalog), size=n)
    products = catalog.iloc[prod_idx].reset_index(drop=True)

    quantity = np.maximum(1, rng.poisson(lam=2.4, size=n) +
                          (rng.random(n) < 0.15).astype(int) * rng.integers(1, 5, size=n))
    quantity = (quantity * season_boost).round().astype(int).clip(min=1)

    discount = np.where(rng.random(n) < 0.30, rng.uniform(0.05, 0.30, n), 0.0)

    revenue = (products["Unit_Price"].to_numpy() * quantity * (1 - discount)).round(2)
    cost = (products["Unit_Cost"].to_numpy() * quantity).round(2)

    customers = (10000 + rng.integers(0, 4500, size=n)).astype(int)
    region = rng.choice(regions, size=n, p=region_weights)

    df = pd.DataFrame({
        "Date": dates,
        "Customer_ID": [f"C{c:05d}" for c in customers],
        "Product": products["Product"].to_numpy(),
        "Category": products["Category"].to_numpy(),
        "Region": region,
        "Quantity": quantity,
        "Revenue": revenue,
        "Cost": cost,
    })

    # Inject realistic dirt
    null_idx = rng.choice(df.index, size=int(n * 0.012), replace=False)
    df.loc[null_idx[: len(null_idx) // 2], "Revenue"] = np.nan
    df.loc[null_idx[len(null_idx) // 2:], "Region"] = None

    dup_idx = rng.choice(df.index, size=int(n * 0.008), replace=False)
    dupes = df.loc[dup_idx].copy()
    df = pd.concat([df, dupes], ignore_index=True)

    log.info("Generated %d raw sales rows (with %d nulls, %d duplicates injected)",
              len(df), len(null_idx), len(dup_idx))
    return df


def generate_and_save(cfg: Dict[str, Any]) -> Path:
    """Generate dataset and persist raw CSV."""
    df = generate_sales(cfg)
    out = Path(cfg["data"]["raw_csv_path"])
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    log.info("Wrote raw dataset to %s", out)
    return out
