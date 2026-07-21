# Campaign Performance Dashboard

A single-page Streamlit dashboard (`main.py`) visualizing Unilever campaign
performance (visits, conversions, brands, prize themes, timelines) via
`streamlit-echarts`, plus an AI-generated executive summary (`ai_summary.py`,
OpenAI) and a click-through Campaign Detail page (`pages/1_Campaign_Detail.py`).

Data is pulled live from a Google Sheet at runtime (`common.py`) — the CSV
under `data/` is a static reference copy only and has no effect on the app.

## Local development

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in OPENAI_API_KEY
streamlit run main.py
```

Runs at http://localhost:8501. Without `OPENAI_API_KEY` set, everything works
except the AI Summary card, which shows a warning instead of a report.

## ⚠️ Before you touch requirements.txt

`streamlit-echarts` is pinned to `==0.4.0` on purpose. Every version from
0.5.0 onward on PyPI crashes on import against current Streamlit releases
(a component-registration API mismatch, unrelated to this app's code) —
verified with Streamlit's `AppTest` harness. Don't unpin it without
re-verifying the app actually boots (`streamlit run main.py` and load the
page — an import crash won't show up in a syntax check).

## Deployment

Pick whichever matches your host; all three run the exact same app.

### Streamlit Community Cloud

1. Push this repo to GitHub.
2. On [share.streamlit.io](https://share.streamlit.io), create an app pointing
   at this repo, branch `main`, entrypoint `main.py`.
3. In the app's **Settings → Secrets**, add:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
4. Deploy. Streamlit Cloud manages the port/process for you.

### Docker

```bash
docker build -t campaign-performance .
docker run -d --name campaign-performance \
  -p 8501:8501 \
  --env-file .env \
  --restart unless-stopped \
  campaign-performance
```

Health check: `curl http://localhost:8501/_stcore/health`.

### VPS / bare metal (systemd + Nginx)

Clone the repo, create a venv, install requirements, and set up `.env` as in
[Local development](#local-development), then:

**`/etc/systemd/system/campaign-performance.service`**
```ini
[Unit]
Description=Campaign Performance Dashboard
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/campaign-performance
EnvironmentFile=/opt/campaign-performance/.env
ExecStart=/opt/campaign-performance/.venv/bin/streamlit run main.py \
    --server.port=8501 --server.address=127.0.0.1 --server.headless=true
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now campaign-performance
```

**Nginx reverse proxy** (`/etc/nginx/sites-available/campaign-performance`):
```nginx
server {
    listen 80;
    server_name your-domain.example;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Streamlit uses a WebSocket connection, so the `Upgrade`/`Connection` headers
above are required — without them the app loads but reruns/interactions hang.

### Other PaaS (Railway, Render, Heroku, etc.)

`Procfile` is included (`web: streamlit run main.py --server.port=$PORT
--server.address=0.0.0.0 --server.headless=true`) for platforms that expect
one. Set `OPENAI_API_KEY` in the platform's environment variable settings.
