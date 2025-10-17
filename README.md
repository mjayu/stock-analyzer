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

# Stock Analyzer

Small Streamlit dashboard to analyze stock metrics and show news.

This repository now uses Alpha Vantage as the primary data provider. It fetches:

- Company overview and fundamentals (OVERVIEW)
- Historical daily adjusted prices (TIME_SERIES_DAILY_ADJUSTED)
- News via the NEWS_SENTIMENT endpoint

All network calls are cached in `data/stock_analyzer.db` to reduce API quota usage and avoid rate-limit errors.

## Files of interest

- `app.py` — Streamlit UI and app glue. Includes a "Refresh (bypass cache)" button in the sidebar.
- `src/fetcher.py` — Alpha Vantage-only fetchers with retries and caching.
- `src/db.py` — SQLite helpers for news cache and a small key/value cache table.
- `scripts/setup_env.sh` — creates `.venv`, installs requirements, and prepares `.env`.
- `scripts/run_app.sh` — helper to run the Streamlit app from `.venv` (background/foreground).

## Requirements

- You must have an Alpha Vantage API key. Sign up at: https://www.alphavantage.co
- Add the key to `.env` (at the repo root):

```bash
ALPHA_VANTAGE_KEY=your_api_key_here
```

## Quick start

1. Install system deps (if running locally and you need Pillow support):

```bash
sudo apt-get update
sudo apt-get install -y libjpeg-dev zlib1g-dev libpng-dev build-essential python3-dev
```

2. Run the setup script (creates venv and installs Python deps):

```bash
./scripts/setup_env.sh --no-system-deps
```

3. Start the app (background):

```bash
./scripts/run_app.sh
```

Or foreground:

```bash
./scripts/run_app.sh --foreground
```

4. Open the app in your browser (default port 8501) or use your cloud provider's port-forwarding/preview feature.

## Notes on rate limits and caching

- Alpha Vantage free tier has rate limits (typically 5 requests/min). The app caches responses in `data/stock_analyzer.db`:
	- Metrics TTL: 10 minutes
	- History TTL: 1 hour
	- News TTL: 6 hours
- Use the "Refresh (bypass cache)" button in the sidebar to force a cache bypass for the current ticker.

## Troubleshooting

- `ALPHA_VANTAGE_KEY not set` — add your key to `.env` and restart the app.
- If you hit API limits, wait a minute or upgrade to a higher plan (or switch to another provider like Finnhub).

## Next improvements I can implement

- Compute `previousClose`, `open`, `dayHigh`, and `dayLow` from the latest time-series if you want those populated.
- Add a UI indicator showing "data source: Alpha Vantage (cached: X minutes)".
- Add a fallback provider (Finnhub) to use when Alpha Vantage hits rate limits.

If you want any of these, tell me which and I will implement it.