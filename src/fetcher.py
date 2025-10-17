import os
import time
import json
import random
from datetime import datetime

import requests
import pandas as pd
from dotenv import load_dotenv

from src import db

load_dotenv()

ALPHA_KEY = os.getenv('STOCK_API')

# Cache TTLs (seconds)
TTL_METRICS = 60 * 10      # 10 minutes
TTL_HISTORY = 60 * 60     # 1 hour
TTL_NEWS = 60 * 60 * 6    # 6 hours


def _cache_get(key, ttl):
    raw = db.cache_get(key)
    if not raw:
        return None
    try:
        obj = json.loads(raw)
        ts = obj.get('_cached_at', 0)
        if time.time() - ts > ttl:
            return None
        return obj.get('data')
    except Exception:
        return None


def _cache_set(key, data):
    obj = {'_cached_at': time.time(), 'data': data}
    db.cache_set(key, json.dumps(obj))


def _requests_with_retry(url, params=None, headers=None, max_attempts=3, backoff_base=1.0):
    headers = headers or {'User-Agent': 'stock-analyzer/1.0'}
    for attempt in range(max_attempts):
        try:
            r = requests.get(url, params=params, headers=headers, timeout=10)
        except requests.RequestException:
            # network error, retry
            sleep = backoff_base * (2 ** attempt) + random.random()
            time.sleep(sleep)
            continue

        if r.status_code == 200:
            return r
        if r.status_code in (429, 503):
            # backoff and retry
            sleep = backoff_base * (2 ** attempt) + random.random()
            time.sleep(sleep)
            continue
        # other errors: raise
        r.raise_for_status()
    # exhausted
    return None


def fetch_metrics_alpha(ticker, force_refresh=False):
    """Fetch company overview/metrics from Alpha Vantage (OVERVIEW endpoint).
    Returns a dict of common metric names. Caches results for TTL_METRICS."""
    if not ALPHA_KEY:
        raise RuntimeError('ALPHA_VANTAGE_KEY not set')

    key = f"alpha:metrics:{ticker}"
    if not force_refresh:
        cached = _cache_get(key, TTL_METRICS)
        if cached:
            return cached

    url = 'https://www.alphavantage.co/query'
    params = {'function': 'OVERVIEW', 'symbol': ticker, 'apikey': ALPHA_KEY}
    r = _requests_with_retry(url, params=params)
    if not r:
        return {}
    data = r.json()
    if not data:
        return {}

    # Map some fields to a consistent shape used by the app
    metrics = {
        'symbol': data.get('Symbol', ticker),
        'shortName': data.get('Name'),
        'longName': data.get('Description'),
        'marketCap': int(data.get('MarketCapitalization')) if data.get('MarketCapitalization') else None,
        'previousClose': None,
        'open': None,
        'dayHigh': None,
        'dayLow': None,
        'fiftyTwoWeekHigh': None,
        'fiftyTwoWeekLow': None,
        'trailingPE': float(data.get('PERatio')) if data.get('PERatio') else None,
        'forwardPE': None,
        'dividendYield': float(data.get('DividendYield')) if data.get('DividendYield') else None,
    }

    _cache_set(key, metrics)
    return metrics


def fetch_history_alpha(ticker, period='1y', interval='1d', force_refresh=False):
    """Fetch historical daily adjusted series from Alpha Vantage and return as a
    pandas DataFrame with a 'Date' column (naive datetime) and Open/High/Low/Close/Volume.
    Caches results for TTL_HISTORY.
    """
    if not ALPHA_KEY:
        raise RuntimeError('ALPHA_VANTAGE_KEY not set')

    key = f"alpha:history:{ticker}"
    if not force_refresh:
        cached = _cache_get(key, TTL_HISTORY)
        if cached:
            # cached is stored as list-of-dicts; convert back to DataFrame
            return pd.DataFrame(cached).assign(Date=lambda df: pd.to_datetime(df['Date']))

    url = 'https://www.alphavantage.co/query'
    params = {'function': 'TIME_SERIES_DAILY_ADJUSTED', 'symbol': ticker, 'outputsize': 'full', 'apikey': ALPHA_KEY}
    r = _requests_with_retry(url, params=params)
    if not r:
        return pd.DataFrame()
    j = r.json()
    ts = j.get('Time Series (Daily)') or {}
    rows = []
    for d, vals in ts.items():
        rows.append({
            'Date': d,
            'Open': float(vals.get('1. open', 'nan')),
            'High': float(vals.get('2. high', 'nan')),
            'Low': float(vals.get('3. low', 'nan')),
            'Close': float(vals.get('4. close', 'nan')),
            'Adj Close': float(vals.get('5. adjusted close', 'nan')),
            'Volume': int(vals.get('6. volume', 0)),
        })

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')

    # Optionally slice by period
    if period.endswith('y'):
        years = int(period[:-1])
        cutoff = pd.Timestamp.now() - pd.DateOffset(years=years)
        df = df[df['Date'] >= cutoff]

    # cache as list-of-dicts
    _cache_set(key, df.to_dict(orient='records'))
    return df


def fetch_metrics(ticker, force_refresh=False):
    """Fetch metrics using Alpha Vantage only."""
    return fetch_metrics_alpha(ticker, force_refresh=force_refresh)


def fetch_history(ticker, period='1y', interval='1d', force_refresh=False):
    return fetch_history_alpha(ticker, period=period, interval=interval, force_refresh=force_refresh)


def fetch_news(ticker, limit=20, force_refresh=False):
    """Fetch news using Alpha Vantage NEWS_SENTIMENT endpoint and cache results."""
    if not ALPHA_KEY:
        raise RuntimeError('ALPHA_VANTAGE_KEY not set')

    key = f"alpha:news:{ticker}"
    if not force_refresh:
        cached = _cache_get(key, TTL_NEWS)
        if cached:
            return cached

    url = 'https://www.alphavantage.co/query'
    params = {'function': 'NEWS_SENTIMENT', 'tickers': ticker, 'apikey': ALPHA_KEY}
    r = _requests_with_retry(url, params=params)
    if not r:
        return []
    j = r.json()
    # AlphaVantage returns a 'feed' list
    feed = j.get('feed') or j.get('items') or j.get('articles') or []
    results = []
    for item in feed[:limit]:
        title = item.get('title') or item.get('headline')
        urlv = item.get('url') or item.get('link')
        source = item.get('source') or item.get('provider_name') or 'AlphaVantage'
        published = item.get('time_published') or item.get('published_at') or item.get('time')
        # Normalize
        results.append({'title': title, 'url': urlv, 'source': source, 'published_at': published})

    _cache_set(key, results)
    return results
