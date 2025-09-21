"""
Finance AI Assistant Frontend - Streamlit Dashboard
Interactive financial analysis and visualization dashboard
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import time
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
BACKEND_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Finance AI Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 0.25rem solid #1f77b4;
    }
    .sidebar-header {
        font-size: 1.25rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def get_backend_data(endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
    """
    Fetch data from the FastAPI backend
    """
    try:
        url = f"{BACKEND_URL}{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {e}")
        logger.error(f"Backend request failed: {e}")
        return None

def display_stock_search():
    """Stock search and selection interface"""
    st.header("🔍 Stock Search & Analysis")

    col1, col2 = st.columns([2, 1])

    with col1:
        search_query = st.text_input(
            "Search for stocks",
            placeholder="Enter company name or symbol (e.g., Apple, AAPL)"
        )

    with col2:
        limit = st.selectbox("Max results", [5, 10, 15, 20], index=1)

    if search_query:
        with st.spinner("Searching stocks..."):
            results = get_backend_data("/api/stocks/search", {"query": search_query, "limit": limit})

        if results:
            st.subheader(f"Found {len(results)} results for '{search_query}'")

            # Create a selection interface
            stock_options = {f"{stock['symbol']} - {stock['name']}": stock['symbol'] for stock in results}
            selected_stock = st.selectbox("Select a stock for analysis", list(stock_options.keys()))

            if selected_stock:
                symbol = stock_options[selected_stock]
                return symbol

    return None

def display_stock_info(symbol: str):
    """Display comprehensive stock information"""
    st.header(f"📊 {symbol} - Stock Analysis")

    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Price Chart", "Technical Analysis", "News & Alerts"])

    with tab1:
        display_stock_overview(symbol)

    with tab2:
        display_price_chart(symbol)

    with tab3:
        display_technical_analysis(symbol)

    with tab4:
        display_news_alerts(symbol)

def display_stock_overview(symbol: str):
    """Display stock overview information"""
    col1, col2, col3 = st.columns(3)

    with col1:
        with st.spinner("Loading stock info..."):
            info = get_backend_data(f"/api/stocks/{symbol}/info")

        if info:
            st.subheader("Company Information")
            st.write(f"**Name:** {info.get('name', 'N/A')}")
            st.write(f"**Sector:** {info.get('sector', 'N/A')}")
            st.write(f"**Industry:** {info.get('industry', 'N/A')}")

    with col2:
        with st.spinner("Loading market data..."):
            quote = get_backend_data(f"/api/stocks/{symbol}/quote")

        if quote:
            st.subheader("Market Data")
            st.metric("Current Price", f"${quote.get('current_price', 'N/A')}")
            st.metric("Day High", f"${quote.get('day_high', 'N/A')}")
            st.metric("Day Low", f"${quote.get('day_low', 'N/A')}")
            st.metric("Volume", f"{quote.get('volume', 'N/A'):,}")

    with col3:
        with st.spinner("Loading analysis..."):
            analysis = get_backend_data(f"/api/stocks/{symbol}/analysis")

        if analysis:
            st.subheader("Technical Indicators")
            st.metric("SMA (20)", f"${analysis.get('sma_20', 'N/A')}")
            st.metric("SMA (50)", f"${analysis.get('sma_50', 'N/A')}")
            st.metric("RSI", f"{analysis.get('rsi', 'N/A')}")
            st.write(f"**Trend:** {analysis.get('trend', 'N/A').title()}")

def display_price_chart(symbol: str):
    """Display interactive price chart"""
    st.subheader("Price History")

    # Time period selection
    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox(
            "Time Period",
            ["1mo", "3mo", "6mo", "1y", "2y", "5y"],
            index=3
        )
    with col2:
        interval = st.selectbox(
            "Interval",
            ["1d", "1wk", "1mo"],
            index=0
        )

    with st.spinner("Loading price history..."):
        history = get_backend_data(f"/api/stocks/{symbol}/history", {"period": period, "interval": interval})

    if history:
        # Convert to DataFrame for plotting
        df = pd.DataFrame(history)

        # Create candlestick chart
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            subplot_titles=(f'{symbol} Price Chart', 'Volume'),
            row_heights=[0.7, 0.3]
        )

        # Price candlestick
        fig.add_trace(
            go.Candlestick(
                x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'],
                name='Price'
            ),
            row=1, col=1
        )

        # Volume bar chart
        fig.add_trace(
            go.Bar(
                x=df['timestamp'],
                y=df['volume'],
                name='Volume',
                marker_color='rgba(31, 119, 180, 0.3)'
            ),
            row=2, col=1
        )

        fig.update_layout(
            height=600,
            title_text=f"{symbol} Historical Price Data",
            xaxis_rangeslider_visible=False
        )

        st.plotly_chart(fig, use_container_width=True)

        # Display data table
        with st.expander("View Raw Data"):
            st.dataframe(df)

def display_technical_analysis(symbol: str):
    """Display technical analysis indicators"""
    st.subheader("Technical Analysis")

    with st.spinner("Loading technical analysis..."):
        analysis = get_backend_data(f"/api/stocks/{symbol}/analysis")

    if analysis:
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Current Price", f"${analysis.get('current_price', 'N/A')}")
            st.metric("SMA (20)", f"${analysis.get('sma_20', 'N/A')}")
            st.metric("SMA (50)", f"${analysis.get('sma_50', 'N/A')}")

        with col2:
            rsi = analysis.get('rsi', 50)
            st.metric("RSI (14)", f"{rsi}")

            # RSI indicator
            if rsi > 70:
                st.error("⚠️ Overbought (RSI > 70)")
            elif rsi < 30:
                st.warning("💡 Oversold (RSI < 30)")
            else:
                st.success("✅ Neutral RSI")

        with col3:
            trend = analysis.get('trend', 'neutral')
            if trend == 'bullish':
                st.success("📈 Bullish Trend")
            elif trend == 'bearish':
                st.error("📉 Bearish Trend")
            else:
                st.info("➡️ Neutral Trend")

def display_news_alerts(symbol: str):
    """Display news and alerts (placeholder for now)"""
    st.subheader("News & Market Alerts")

    st.info("📝 News integration coming soon...")

    # Placeholder for alerts
    st.write("### Market Alerts")
    st.write("• Price movement alerts")
    st.write("• Technical indicator signals")
    st.write("• Volume spikes")
    st.write("• Market sentiment changes")

def display_market_overview():
    """Display market overview dashboard"""
    st.header("🌍 Market Overview")

    with st.spinner("Loading market indices..."):
        indices = get_backend_data("/api/market/indices")

    if indices:
        # Create columns for different indices
        cols = st.columns(len(indices))

        for i, (symbol, data) in enumerate(indices.items()):
            with cols[i]:
                st.subheader(data.get('name', symbol))
                st.metric(
                    "Current",
                    f"${data.get('current_price', 'N/A')}",
                    delta=f"{data.get('change', 0):+.2f} ({data.get('change_percent', 0):+.2f}%)"
                )

def display_portfolio_tracker():
    """Portfolio tracking interface"""
    st.header("💼 Portfolio Tracker")

    st.info("🚧 Portfolio tracking feature coming soon...")

    # Placeholder for portfolio features
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Holdings")
        st.write("• Add stocks to your portfolio")
        st.write("• Track performance over time")
        st.write("• View allocation breakdown")

    with col2:
        st.subheader("Performance")
        st.write("• Daily P&L tracking")
        st.write("• Historical performance charts")
        st.write("• Risk metrics")

def main():
    """Main application function"""
    # Sidebar navigation
    st.sidebar.markdown('<div class="sidebar-header">Finance AI Assistant</div>', unsafe_allow_html=True)

    # Navigation menu
    page = st.sidebar.selectbox(
        "Navigation",
        ["Market Overview", "Stock Analysis", "Portfolio Tracker", "Settings"],
        index=0
    )

    # Display current time
    st.sidebar.write(f"**Last Updated:** {datetime.now().strftime('%H:%M:%S')}")

    # Main content based on selected page
    if page == "Market Overview":
        display_market_overview()

    elif page == "Stock Analysis":
        symbol = display_stock_search()
        if symbol:
            display_stock_info(symbol)

    elif page == "Portfolio Tracker":
        display_portfolio_tracker()

    elif page == "Settings":
        st.header("⚙️ Settings")
        st.write("### Backend Configuration")
        st.text_input("Backend URL", value=BACKEND_URL, key="backend_url")

        st.write("### Display Options")
        st.checkbox("Enable real-time updates", value=True)
        st.checkbox("Show technical indicators", value=True)
        st.checkbox("Enable alerts", value=True)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>Finance AI Assistant - Built with Streamlit, FastAPI, and Pathway</p>
            <p>Data provided by Yahoo Finance</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()