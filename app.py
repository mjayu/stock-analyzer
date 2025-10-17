import streamlit as st
from datetime import date
import pandas as pd
from src import fetcher, db


st.set_page_config(page_title='Stock Analyzer', layout='wide')

# init DB
try:
    db.init_db()
except Exception as e:
    st.error(f"DB init error: {e}")

st.title('Stock Analyzer')

with st.sidebar:
    ticker = st.text_input('Ticker', value='AAPL')
    period = st.selectbox('History period', ['1mo','3mo','6mo','1y','2y','5y'], index=3)
    interval = st.selectbox('Interval', ['1d','1wk','1mo'], index=0)
    show_news = st.checkbox('Show news', value=True)
    refresh = st.button('Refresh (bypass cache)')

if ticker:
    try:
        metrics = fetcher.fetch_metrics(ticker, force_refresh=refresh)
        st.subheader(f"{metrics.get('shortName') or metrics.get('symbol')} ({metrics.get('symbol')})")
        cols = st.columns(4)
        cols[0].metric('Previous Close', metrics.get('previousClose'))
        cols[1].metric('Market Cap', metrics.get('marketCap'))
        cols[2].metric('PE (TTM)', metrics.get('trailingPE'))
        cols[3].metric('Dividend Yield', metrics.get('dividendYield'))

        hist = fetcher.fetch_history(ticker, period=period, interval=interval, force_refresh=refresh)
        if not hist.empty:
            st.line_chart(hist.set_index('Date')['Close'])

        st.header('Key Metrics')
        st.table(pd.DataFrame.from_dict(metrics, orient='index', columns=['value']))

        if show_news:
            articles = db.get_news(ticker)
            if not articles:
                articles = fetcher.fetch_news_yahoo(ticker, limit=10, force_refresh=refresh)
                db.save_news(ticker, articles)
            st.header('News')
            for a in articles:
                st.write(f"- [{a['title']}]({a['url']}) — {a.get('source')} ({a.get('published_at')})")
    except Exception as e:
        st.error(f"Error fetching data: {e}")
