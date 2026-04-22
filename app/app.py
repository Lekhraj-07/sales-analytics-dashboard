"""Streamlit entry point: Sales & Profitability Analytics Dashboard."""
from __future__ import annotations
import sys
from pathlib import Path

# Allow `streamlit run app/app.py` from project root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from src.config import load_config
from src.logger import get_logger
from src.pipeline import run_pipeline
from src import analytics, insights
from app import charts
from app.auth import login_gate, logout_button


@st.cache_data(show_spinner="Loading data pipeline...")
def _load_data(force: bool) -> pd.DataFrame:
    return run_pipeline(force=force)


def main() -> None:
    cfg = load_config()
    log = get_logger("app", level=cfg["logging"]["level"], fmt=cfg["logging"]["format"])

    st.set_page_config(page_title=cfg["app"]["title"],
                       page_icon=cfg["app"]["page_icon"],
                       layout=cfg["app"]["layout"])

    if not login_gate(cfg["auth"]):
        return

    st.title(f"{cfg['app']['page_icon']} {cfg['app']['title']}")
    st.caption("End-to-end analytics: ingestion · cleaning · feature engineering · SQLite · insights")

    # ---------- Sidebar ----------
    st.sidebar.header("Controls")
    if st.sidebar.button("🔄 Rebuild dataset"):
        _load_data.clear()
        df = _load_data(force=True)
        st.sidebar.success("Pipeline rerun complete.")
    else:
        try:
            df = _load_data(force=False)
        except Exception as e:  # pragma: no cover
            log.exception("Pipeline failed")
            st.error(f"Pipeline failed: {e}")
            return

    st.sidebar.divider()
    st.sidebar.subheader("Filters")

    min_d, max_d = df["Date"].min().date(), df["Date"].max().date()
    date_range = st.sidebar.date_input("Date range", value=(min_d, max_d),
                                        min_value=min_d, max_value=max_d)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        d_start, d_end = date_range
    else:
        d_start, d_end = min_d, max_d

    regions = sorted(df["Region"].dropna().unique().tolist())
    sel_regions = st.sidebar.multiselect("Region", regions, default=regions)

    categories = sorted(df["Category"].dropna().unique().tolist())
    sel_cats = st.sidebar.multiselect("Category", categories, default=categories)

    freq_label = st.sidebar.radio("Time grain", ["Daily", "Weekly", "Monthly"], index=2)
    freq_map = {"Daily": "D", "Weekly": "W", "Monthly": "ME"}

    st.sidebar.divider()
    logout_button()

    # ---------- Filter ----------
    mask = (
        (df["Date"].dt.date >= d_start)
        & (df["Date"].dt.date <= d_end)
        & (df["Region"].isin(sel_regions) if sel_regions else True)
        & (df["Category"].isin(sel_cats) if sel_cats else True)
    )
    fdf = df.loc[mask].copy()

    # ---------- KPIs ----------
    k = analytics.kpis(fdf)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"₹{k['total_revenue']:,.0f}")
    c2.metric("Total Profit", f"₹{k['total_profit']:,.0f}")
    c3.metric("Profit Margin", f"{k['profit_margin']:.1f}%")
    c4.metric("Top Product", k["top_product"])

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Orders", f"{k['total_orders']:,}")
    c6.metric("Avg Order Value", f"₹{k['avg_order_value']:,.2f}")
    c7.metric("Unique Customers", f"{k['unique_customers']:,}")
    c8.metric("Rows in DB", f"{len(df):,}")

    st.divider()

    # ---------- Tabs ----------
    tab_overview, tab_products, tab_geo, tab_insights, tab_data = st.tabs(
        ["📈 Overview", "🛒 Products", "🌍 Regions", "💡 Insights", "🗃 Data"]
    )

    with tab_overview:
        ts = analytics.revenue_over_time(fdf, freq=freq_map[freq_label])
        st.plotly_chart(charts.line_revenue(ts), use_container_width=True)
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(charts.pie_categories(analytics.category_distribution(fdf)),
                             use_container_width=True)
        with col_b:
            cat_perf = analytics.category_performance(fdf)
            st.subheader("Category Performance")
            st.dataframe(cat_perf, use_container_width=True, hide_index=True)

    with tab_products:
        top_n = st.slider("Top N products", 5, 25, 10)
        st.plotly_chart(charts.bar_top_products(analytics.top_products(fdf, n=top_n)),
                         use_container_width=True)

    with tab_geo:
        st.plotly_chart(charts.bar_region(analytics.region_breakdown(fdf)),
                         use_container_width=True)
        st.plotly_chart(charts.heatmap_region_category(analytics.region_category_heatmap(fdf)),
                         use_container_width=True)

    with tab_insights:
        st.subheader("Auto-generated business insights")
        items = insights.generate_insights(fdf)
        for item in items:
            with st.container(border=True):
                st.markdown(f"### {item['title']}")
                st.write(item["body"])
                st.success(f"**Recommendation:** {item['recommendation']}")

    with tab_data:
        st.subheader("Filtered data preview")
        st.dataframe(fdf.head(500), use_container_width=True, hide_index=True)
        csv_bytes = fdf.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download filtered CSV", data=csv_bytes,
                            file_name="filtered_sales.csv", mime="text/csv")


if __name__ == "__main__":
    main()
