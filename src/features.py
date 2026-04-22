"""Feature engineering: profit margin, growth, rolling averages."""
from __future__ import annotations
import numpy as np
import pandas as pd

from src.logger import get_logger

log = get_logger(__name__)


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns. Returns enriched copy."""
    df = df.copy()
    df["Profit_Margin"] = np.where(df["Revenue"] > 0,
                                    (df["Profit"] / df["Revenue"]) * 100, 0.0)
    df["Profit_Margin"] = df["Profit_Margin"].round(2)

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["Quarter"] = df["Date"].dt.to_period("Q").astype(str)
    df["Weekday"] = df["Date"].dt.day_name()

    # Daily aggregate for rolling averages on revenue series
    daily = df.groupby(df["Date"].dt.date)["Revenue"].sum().sort_index()
    rolling7 = daily.rolling(7, min_periods=1).mean()
    rolling30 = daily.rolling(30, min_periods=1).mean()
    rolling_map7 = rolling7.to_dict()
    rolling_map30 = rolling30.to_dict()
    df["Revenue_Rolling_7d"] = df["Date"].dt.date.map(rolling_map7).round(2)
    df["Revenue_Rolling_30d"] = df["Date"].dt.date.map(rolling_map30).round(2)

    # Monthly growth %
    monthly = df.groupby("Month")["Revenue"].sum().sort_index()
    growth = monthly.pct_change().fillna(0) * 100
    growth_map = growth.round(2).to_dict()
    df["Monthly_Growth_Rate"] = df["Month"].map(growth_map)

    log.info("Engineered features for %d rows", len(df))
    return df
