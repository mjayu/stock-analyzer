# Stock Analyzer

Small Streamlit dashboard to analyze stock metrics and show news.

This repository contains a minimal Streamlit app that:

- Fetches stock metrics and historical prices using `yfinance`.
- Scrapes recent news for a ticker from Yahoo Finance (fallback).
- Caches scraped news into a local SQLite database at `data/stock_analyzer.db`.

## Files

- `app.py` — Streamlit UI and application glue.
- `src/fetcher.py` — wrappers around `yfinance` and a simple Yahoo news scraper.
- `src/db.py` — tiny SQLite helper to store news and a small cache table.
- `requirements.txt` — Python dependency list.

## Quick start (Linux / macOS)

1. Install system dependencies (needed for Pillow and building some packages):

```bash
sudo apt-get update
sudo apt-get install -y libjpeg-dev zlib1g-dev libpng-dev build-essential python3-dev
```

2. Create and activate a virtual environment, then install Python packages:

```bash
python -m venv .venv
source .venv/bin/activate
.venv/bin/pip install --upgrade pip setuptools wheel
.venv/bin/pip install -r requirements.txt
```

3. Run the Streamlit app (headless or normally):

```bash
# headless (server only)
.venv/bin/streamlit run app.py --server.headless true --server.port 8501

# or normal (opens in browser)
.venv/bin/streamlit run app.py
```

You should see Streamlit print URLs like `Network URL: http://10.x.x.x:8501` and/or `Local URL: http://localhost:8501`.

## Accessing the app

- If you're on the same machine, open `http://localhost:8501` in your browser.
- In cloud/dev environments (Codespaces, Codespaces-like), use the provider's port forwarding or preview feature to open port `8501`.

## Environment variables and API keys

- The app currently scrapes Yahoo Finance for headline links. For production-grade news, use an official news API (NewsAPI, GNews, Bing News Search, etc.).
- Add API keys to a `.env` file at the repo root and load them in `src/fetcher.py` if you wire a news provider. A sample `.env` is already created.

## Troubleshooting

- `streamlit: command not found` — make sure you installed dependencies into the virtualenv and you run the `streamlit` binary from `.venv/bin/streamlit` or activate the venv.
- `Failed building wheel for pillow` or JPEG header errors — install `libjpeg-dev` (see step 1). Many pillow failures are resolved by system image libs.
- If yfinance fails or is slow, check network connectivity and consider caching results or using a data provider with an API key.

## Files of interest

- `app.py` — Streamlit UI
- `src/fetcher.py` — data fetching functions (`fetch_metrics`, `fetch_history`, `fetch_news_yahoo`)
- `src/db.py` — SQLite helpers for news cache

## Next steps / improvements

- Replace the Yahoo scraper with a news API and add optional sentiment analysis.
- Add technical indicators: SMA, EMA, RSI and plotting with candlesticks.
- Add tests for `fetcher.py` and `db.py`, and a small GitHub Actions CI to run them.
- Add caching or rate-limiting to reduce repeated network calls.

If you want, I can implement any of the improvements above (pick one) and wire in an API key-based news provider and add tests/CI.

# stock-analyzer by Martin yu