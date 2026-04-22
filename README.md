# 📊 Sales & Profitability Analytics Dashboard

A production-grade, end-to-end data analytics project: synthetic but realistic
e-commerce sales data flows through a full pipeline (ingest → clean → feature
engineer → SQLite) and is surfaced in an interactive Streamlit dashboard with
KPIs, Plotly visualizations, and auto-generated business insights.

## Tech stack

- **Python 3.11**, **pandas**, **numpy**
- **Plotly** for all visualizations
- **Streamlit** for the dashboard UI
- **SQLite** for processed-data storage
- **PyYAML** for config

## Features

- Realistic 6,500+ row e-commerce dataset (seasonality, regional weighting, dirty rows)
- Cleaning layer: dedupe, null handling, type coercion, sanity filters
- Feature engineering: profit margin, monthly growth rate, 7-day & 30-day rolling averages
- SQLite persistence with indexes
- KPI cards (revenue, profit, margin, top product, AOV, customers)
- Interactive filters: date range, region, category, time grain
- Charts: line (revenue/profit over time), bar (top products), pie (category share),
  heatmap (region × category profit), grouped bar (region breakdown)
- 5–7 auto-generated business insights with actionable recommendations
- CSV export of filtered data
- Basic session-based auth gate (demo creds: `admin` / `admin123`)
- Streamlit caching, modular code, structured logging, YAML config

## Project structure

```
.
├── app/               # Streamlit UI layer
│   ├── app.py         # Entry point
│   ├── auth.py        # Login gate
│   └── charts.py      # Plotly figure builders
├── src/               # Backend / pipeline layer
│   ├── config.py
│   ├── data_generator.py
│   ├── cleaning.py
│   ├── features.py
│   ├── storage.py
│   ├── analytics.py
│   ├── insights.py
│   ├── pipeline.py
│   └── logger.py
├── config/
│   └── config.yaml    # All tunable settings
├── data/              # Generated CSV + SQLite DB (created at runtime)
├── .streamlit/
│   └── config.toml
├── requirements.txt
└── README.md
```

## Setup

```bash
pip install -r requirements.txt
streamlit run app/app.py --server.port 5000
```

The first run generates the dataset and builds `data/analytics.db`. Subsequent
runs load straight from SQLite. Use the **Rebuild dataset** button in the
sidebar to regenerate.

## Screenshots

<!-- screenshot: dashboard-overview.png -->
<!-- screenshot: insights-tab.png -->
<!-- screenshot: heatmap.png -->

## Notes for reviewers

- All values, paths, and credentials live in `config/config.yaml` — no hardcoded
  constants in the code.
- Logging routes to stdout via `src/logger.py`; level configurable in YAML.
- The pipeline is idempotent and cached; rebuild on demand from the UI.
