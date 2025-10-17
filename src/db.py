import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "stock_analyzer.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

CREATE_NEWS_TABLE = """
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    title TEXT,
    url TEXT,
    source TEXT,
    published_at TEXT,
    fetched_at TEXT DEFAULT (datetime('now'))
);
"""

CREATE_CACHE_TABLE = """
CREATE TABLE IF NOT EXISTS cache (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);
"""


def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute(CREATE_NEWS_TABLE)
        c.execute(CREATE_CACHE_TABLE)
        conn.commit()


def save_news(ticker, articles):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        for a in articles:
            c.execute(
                "INSERT INTO news (ticker, title, url, source, published_at) VALUES (?, ?, ?, ?, ?)",
                (ticker, a.get('title'), a.get('url'), a.get('source'), a.get('published_at')),
            )
        conn.commit()


def get_news(ticker, limit=20):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT title, url, source, published_at FROM news WHERE ticker=? ORDER BY published_at DESC LIMIT ?", (ticker, limit))
        rows = c.fetchall()
    return [dict(title=r[0], url=r[1], source=r[2], published_at=r[3]) for r in rows]


def cache_set(key, value):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("REPLACE INTO cache (key, value, updated_at) VALUES (?, ?, datetime('now'))", (key, value))
        conn.commit()


def cache_get(key):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute("SELECT value FROM cache WHERE key=?", (key,))
        row = c.fetchone()
    return row[0] if row else None
