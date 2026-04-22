"""Analytics computations for the dashboard."""
from __future__ import annotations
from typing import Dict, Any
import pandas as pd


def kpis(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {"total_revenue": 0, "total_profit": 0, "profit_margin": 0,
                "top_product": "—", "total_orders": 0, "avg_order_value": 0,
                "unique_customers": 0}
    rev = float(df["Revenue"].sum())
    prof = float(df["Profit"].sum())
    margin = (prof / rev * 100) if rev else 0
    top = df.groupby("Product")["Revenue"].sum().idxmax()
    return {
        "total_revenue": rev,
        "total_profit": prof,
        "profit_margin": margin,
        "top_product": top,
        "total_orders": int(len(df)),
        "avg_order_value": rev / len(df),
        "unique_customers": int(df["Customer_ID"].nunique()),
    }


def revenue_over_time(df: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Date", "Revenue", "Profit"])
    g = df.set_index("Date").resample(freq).agg({"Revenue": "sum", "Profit": "sum"}).reset_index()
    return g


def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Product", "Revenue", "Profit"])
    return (df.groupby("Product").agg(Revenue=("Revenue", "sum"),
                                        Profit=("Profit", "sum"),
                                        Quantity=("Quantity", "sum"))
              .reset_index().sort_values("Revenue", ascending=False).head(n))


def category_distribution(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Category", "Revenue"])
    return df.groupby("Category", as_index=False)["Revenue"].sum().sort_values("Revenue", ascending=False)


def region_category_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    return df.pivot_table(index="Region", columns="Category", values="Profit",
                          aggfunc="sum", fill_value=0)


def region_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["Region", "Revenue", "Profit", "Orders"])
    return (df.groupby("Region").agg(Revenue=("Revenue", "sum"),
                                       Profit=("Profit", "sum"),
                                       Orders=("Revenue", "count"))
              .reset_index().sort_values("Revenue", ascending=False))


def category_performance(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    out = (df.groupby("Category").agg(Revenue=("Revenue", "sum"),
                                        Profit=("Profit", "sum"),
                                        Quantity=("Quantity", "sum"))
              .reset_index())
    out["Margin_%"] = (out["Profit"] / out["Revenue"] * 100).round(2)
    return out.sort_values("Revenue", ascending=False)
