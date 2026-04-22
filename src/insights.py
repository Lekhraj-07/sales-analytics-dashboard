"""Auto-generated business insights."""
from __future__ import annotations
from typing import List
import pandas as pd


def _fmt_money(x: float) -> str:
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:.2f}M"
    if abs(x) >= 1_000:
        return f"${x/1_000:.1f}K"
    return f"${x:,.0f}"


def generate_insights(df: pd.DataFrame) -> List[dict]:
    """Return a list of {title, body, recommendation} dicts."""
    if df.empty:
        return [{"title": "No data", "body": "Adjust filters to see insights.",
                 "recommendation": "Reset the date range or category filter."}]

    out: List[dict] = []

    # 1. Top product
    prod = df.groupby("Product")["Revenue"].sum().sort_values(ascending=False)
    top_p, top_rev = prod.index[0], prod.iloc[0]
    share = top_rev / df["Revenue"].sum() * 100
    out.append({
        "title": f"Top performer: {top_p}",
        "body": f"{top_p} generated {_fmt_money(top_rev)} ({share:.1f}% of total revenue).",
        "recommendation": "Protect inventory for this SKU and feature it in cross-sell flows.",
    })

    # 2. Most profitable category by margin
    cat = df.groupby("Category").agg(Rev=("Revenue", "sum"), Prof=("Profit", "sum"))
    cat["Margin"] = cat["Prof"] / cat["Rev"] * 100
    best_cat = cat["Margin"].idxmax()
    out.append({
        "title": f"Best margin category: {best_cat}",
        "body": f"{best_cat} runs at {cat.loc[best_cat,'Margin']:.1f}% margin on {_fmt_money(cat.loc[best_cat,'Rev'])} revenue.",
        "recommendation": f"Allocate more marketing spend to {best_cat} — each dollar returns the most profit.",
    })

    # 3. Worst margin category
    worst_cat = cat["Margin"].idxmin()
    if worst_cat != best_cat:
        out.append({
            "title": f"Margin pressure in {worst_cat}",
            "body": f"{worst_cat} is your weakest margin at {cat.loc[worst_cat,'Margin']:.1f}%.",
            "recommendation": "Renegotiate supplier costs or trim discounting on this category.",
        })

    # 4. Region leader / laggard
    reg = df.groupby("Region")["Revenue"].sum().sort_values(ascending=False)
    if len(reg) >= 2:
        out.append({
            "title": f"Region leader: {reg.index[0]}",
            "body": f"{reg.index[0]} drives {_fmt_money(reg.iloc[0])} vs. {_fmt_money(reg.iloc[-1])} from {reg.index[-1]}.",
            "recommendation": f"Investigate why {reg.index[-1]} underperforms — pricing, logistics, or local demand.",
        })

    # 5. Monthly trend
    monthly = df.groupby(df["Date"].dt.to_period("M"))["Revenue"].sum().sort_index()
    if len(monthly) >= 2:
        last, prev = monthly.iloc[-1], monthly.iloc[-2]
        delta = (last - prev) / prev * 100 if prev else 0
        direction = "up" if delta >= 0 else "down"
        out.append({
            "title": f"Latest month {direction} {abs(delta):.1f}% MoM",
            "body": f"{monthly.index[-1]} revenue: {_fmt_money(last)} vs. {monthly.index[-2]} {_fmt_money(prev)}.",
            "recommendation": ("Double down on whatever campaign drove this lift." if delta >= 0
                                else "Run a quick post-mortem — was it seasonality, stockouts, or pricing?"),
        })

    # 6. Seasonality
    by_month = df.groupby(df["Date"].dt.month)["Revenue"].sum()
    peak_m = int(by_month.idxmax())
    month_name = pd.Timestamp(2024, peak_m, 1).strftime("%B")
    out.append({
        "title": f"Seasonal peak in {month_name}",
        "body": f"{month_name} consistently records the highest revenue across the dataset.",
        "recommendation": f"Plan inventory and ad spend uplift 4–6 weeks ahead of {month_name}.",
    })

    # 7. Customer concentration
    cust = df.groupby("Customer_ID")["Revenue"].sum().sort_values(ascending=False)
    top10_share = cust.head(10).sum() / cust.sum() * 100
    out.append({
        "title": "Customer concentration",
        "body": f"Top 10 customers account for {top10_share:.1f}% of revenue across {len(cust):,} unique buyers.",
        "recommendation": ("Launch a VIP retention program — losing a top customer would hurt." if top10_share > 5
                            else "Healthy long-tail. Focus on average-order-value lifts across the base."),
    })

    return out
