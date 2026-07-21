# Campaign Performance Dashboard

A single-page Streamlit dashboard (`main.py`) visualizing Unilever campaign
performance (visits, conversions, brands, prize themes, timelines) via
`streamlit-echarts`, plus an AI-generated executive summary (`ai_summary.py`,
OpenAI) and a click-through Campaign Detail page (`pages/1_Campaign_Detail.py`).

Data is pulled live from a Google Sheet at runtime (`common.py`) — the CSV
under `data/` is a static reference copy only and has no effect on the app.

## Setup

```bash
pip install -r requirements.txt
```

Configure `OPENAI_API_KEY` in `.streamlit/secrets.toml` (gitignored):

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then fill it in
```

A real process env var (e.g. set by systemd/the container/the platform) works
too — the app checks secrets.toml first, then falls back to the environment.
Without a key set, everything works except the AI Summary card, which shows
a warning instead of a report.

## Run

```bash
streamlit run main.py
```

Local dev: opens on http://localhost:8501.

For a production process, add the flags your setup needs, e.g.:

```bash
streamlit run main.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
```

Process management (systemd/supervisor/pm2/etc.) and any reverse proxy
(Nginx/Caddy) are up to the deploy team's existing conventions — nothing in
this app requires a specific one. One thing worth knowing: Streamlit uses a
WebSocket connection, so a reverse proxy in front of it must forward the
`Upgrade`/`Connection` headers, or reruns and interactions will hang instead
of erroring.

## ⚠️ Before you touch requirements.txt

`streamlit-echarts` is pinned to `==0.4.0` on purpose. Every version from
0.5.0 onward on PyPI crashes on import against current Streamlit releases
(a component-registration API mismatch, unrelated to this app's code) —
verified with Streamlit's `AppTest` harness. Don't unpin it without
re-verifying the app actually boots (`streamlit run main.py` and load the
page — an import crash won't show up in a syntax check).
