"""Plotly chart builders."""
from __future__ import annotations
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def line_revenue(df_ts: pd.DataFrame) -> go.Figure:
    fig = px.line(df_ts, x="Date", y=["Revenue", "Profit"], markers=True,
                  labels={"value": "USD", "variable": "Metric"})
    fig.update_layout(title="Revenue & Profit Over Time", hovermode="x unified",
                      legend_title_text="")
    return fig


def bar_top_products(df_top: pd.DataFrame) -> go.Figure:
    fig = px.bar(df_top.sort_values("Revenue"), x="Revenue", y="Product",
                  orientation="h", color="Profit", color_continuous_scale="Viridis",
                  hover_data=["Quantity"])
    fig.update_layout(title="Top Products by Revenue", height=480)
    return fig


def pie_categories(df_cat: pd.DataFrame) -> go.Figure:
    fig = px.pie(df_cat, names="Category", values="Revenue", hole=0.45)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(title="Revenue Share by Category")
    return fig


def heatmap_region_category(pivot: pd.DataFrame) -> go.Figure:
    fig = px.imshow(pivot, text_auto=".2s", aspect="auto",
                    color_continuous_scale="RdYlGn",
                    labels={"color": "Profit"})
    fig.update_layout(title="Profit Heatmap — Region × Category", height=460)
    return fig


def bar_region(df_reg: pd.DataFrame) -> go.Figure:
    fig = px.bar(df_reg, x="Region", y=["Revenue", "Profit"], barmode="group")
    fig.update_layout(title="Region Breakdown", legend_title_text="")
    return fig
