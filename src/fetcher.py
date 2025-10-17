import yfinance as yf
import requests
from bs4 import BeautifulSoup
from datetime import datetime


def fetch_metrics(ticker):
    t = yf.Ticker(ticker)
    info = t.info if hasattr(t, 'info') else {}
    # select a few helpful metrics
    metrics = {
        'symbol': info.get('symbol', ticker),
        'shortName': info.get('shortName'),
        'longName': info.get('longName'),
        'marketCap': info.get('marketCap'),
        'previousClose': info.get('previousClose'),
        'open': info.get('open'),
        'dayHigh': info.get('dayHigh'),
        'dayLow': info.get('dayLow'),
        'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh'),
        'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow'),
        'trailingPE': info.get('trailingPE'),
        'forwardPE': info.get('forwardPE'),
        'dividendYield': info.get('dividendYield'),
    }
    return metrics


def fetch_history(ticker, period='1y', interval='1d'):
    t = yf.Ticker(ticker)
    hist = t.history(period=period, interval=interval)
    hist = hist.reset_index()
    hist['Date'] = hist['Date'].dt.tz_localize(None)
    return hist


def fetch_news_yahoo(ticker, limit=20):
    """Scrape Yahoo Finance news for a ticker. Returns list of articles."""
    url = f"https://finance.yahoo.com/quote/{ticker}/news"
    r = requests.get(url, headers={'User-Agent': 'stock-analyzer/1.0'})
    if r.status_code != 200:
        return []
    soup = BeautifulSoup(r.text, 'lxml')
    items = soup.select('h3 a')
    results = []
    for it in items[:limit]:
        title = it.get_text(strip=True)
        href = it.get('href')
        if href and href.startswith('/'): 
            href = 'https://finance.yahoo.com' + href
        results.append({'title': title, 'url': href, 'source': 'Yahoo Finance', 'published_at': datetime.utcnow().isoformat()})
    return results
