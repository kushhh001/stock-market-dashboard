import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="Stock Market Dashboard", layout="wide")

st.title("📈 Real-Time Stock Market Dashboard")
st.markdown("Track historical stock movements, volume, and technical indicators.")

# 2. Sidebar Controls
st.sidebar.header("User Settings")

ticker_options = ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN", "NVDA", "RELIANCE.NS", "TCS.NS"]
selected_ticker = st.sidebar.selectbox("Choose a Stock Symbol", ticker_options)

custom_ticker = st.sidebar.text_input("Or enter any ticker manually (e.g. INFY.NS, META):")
if custom_ticker:
    selected_ticker = custom_ticker.upper()

time_period = st.sidebar.selectbox(
    "Select Time Period",
    ("1mo", "3mo", "6mo", "1y", "2y", "5y"),
    index=3
)

# 3. Fetching Market Data
@st.cache_data(ttl=300)
def load_data(symbol, period):
    stock = yf.Ticker(symbol)
    df = stock.history(period=period)
    info = stock.info
    return df, info

try:
    df, info = load_data(selected_ticker, time_period)

    if df.empty:
        st.error(f"No price data found for {selected_ticker}. Please check the symbol.")
    else:
        # 4. Display Key Metrics
        company_name = info.get("shortName", selected_ticker)
        current_price = df["Close"].iloc[-1]
        previous_price = df["Close"].iloc[-2] if len(df) > 1 else current_price
        price_change = current_price - previous_price
        pct_change = (price_change / previous_price) * 100

        st.subheader(f"{company_name} ({selected_ticker})")
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"${current_price:.2f}", f"{price_change:+.2f} ({pct_change:+.2f}%)")
        col2.metric("52-Week High", f"${info.get('fiftyTwoWeekHigh', 0):.2f}")
        col3.metric("52-Week Low", f"${info.get('fiftyTwoWeekLow', 0):.2f}")

        # 5. Technical Indicators
        df["SMA_20"] = df["Close"].rolling(window=20).mean()
        df["SMA_50"] = df["Close"].rolling(window=50).mean()

        # 6. Interactive Candlestick Chart
        st.subheader("Price Movement & Moving Averages")
        fig = go.Figure()

        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Market Price"
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["SMA_20"],
            line=dict(color="orange", width=1.5),
            name="20-Day SMA"
        ))

        fig.add_trace(go.Scatter(
            x=df.index,
            y=df["SMA_50"],
            line=dict(color="blue", width=1.5),
            name="50-Day SMA"
        ))

        fig.update_layout(
            xaxis_rangeslider_visible=False,
            height=500,
            margin=dict(l=20, r=20, t=30, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

        # 7. Volume Chart & Historical Data Table
        st.subheader("Trading Volume")
        st.bar_chart(df["Volume"])

        with st.expander("View Raw Historical Data Table"):
            st.dataframe(df[["Open", "High", "Low", "Close", "Volume"]].tail(20))

except Exception as e:
    st.error(f"Error loading stock data: {e}")