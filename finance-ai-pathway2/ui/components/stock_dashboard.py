"""
Stock Dashboard Component for Streamlit
Provides stock visualization and analysis components
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any, List, Optional

def display_stock_metrics(stock_data: Dict[str, Any]):
    """Display key stock metrics"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Current Price", f"${stock_data['price']".2f"}")

    with col2:
        change_color = "normal" if stock_data['change'] >= 0 else "inverse"
        st.metric("Change", f"${stock_data['change']"+.2f"}", delta_color=change_color)

    with col3:
        st.metric("Volume", f"{stock_data['volume']","}")

    with col4:
        st.metric("Market Cap", f"${stock_data.get('market_cap', 0)","}" if stock_data.get('market_cap') else "N/A")

def display_stock_chart(history_data: List[Dict[str, Any]], symbol: str):
    """Display interactive stock price chart"""
    st.subheader(f"📈 {symbol} Price History")

    if not history_data:
        st.warning("No historical data available")
        return

    # Convert to DataFrame
    df = pd.DataFrame(history_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')

    # Create dual-axis chart
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Price line
    fig.add_trace(
        go.Scatter(x=df.index, y=df['Close'], name="Close Price", line=dict(color="#1f77b4")),
        secondary_y=False
    )

    # Volume bars
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name="Volume", marker_color="#ff7f0e", opacity=0.3),
        secondary_y=True
    )

    fig.update_layout(
        title=f"{symbol} Stock Price & Volume",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        yaxis2_title="Volume"
    )

    st.plotly_chart(fig, use_container_width=True)

def display_technical_indicators(stock_data: Dict[str, Any]):
    """Display technical indicators"""
    st.subheader("📊 Technical Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Key Metrics:**")
        st.write(f"- 52W High: ${stock_data.get('fifty_two_week_high', 'N/A')}")
        st.write(f"- 52W Low: ${stock_data.get('fifty_two_week_low', 'N/A')}")
        st.write(f"- P/E Ratio: {stock_data.get('pe_ratio', 'N/A')}")
        st.write(f"- Dividend Yield: {stock_data.get('dividend_yield', 'N/A')}")

    with col2:
        st.write("**Market Data:**")
        st.write(f"- Sector: {stock_data.get('sector', 'N/A')}")
        st.write(f"- Volume: {stock_data.get('volume', 0)","}")
        st.write(f"- Market Cap: ${stock_data.get('market_cap', 0)","}")

def display_sector_comparison(stock_data: Dict[str, Any]):
    """Display sector comparison"""
    st.subheader("🏢 Sector Analysis")

    if not stock_data.get('sector'):
        st.info("Sector information not available")
        return

    # Mock sector data for demonstration
    sector_data = {
        'Technology': {'avg_pe': 25.5, 'avg_yield': 0.8, 'performance': 15.2},
        'Financial Services': {'avg_pe': 12.3, 'avg_yield': 2.1, 'performance': 8.7},
        'Healthcare': {'avg_pe': 18.9, 'avg_yield': 1.5, 'performance': 12.4},
        'Consumer Discretionary': {'avg_pe': 22.1, 'avg_yield': 0.9, 'performance': 10.8},
        'Consumer Staples': {'avg_pe': 20.5, 'avg_yield': 2.3, 'performance': 6.2}
    }

    sector = stock_data.get('sector')
    if sector in sector_data:
        data = sector_data[sector]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Sector Avg P/E", f"{data['avg_pe']".1f"}")
        with col2:
            st.metric("Sector Avg Yield", f"{data['avg_yield']".1f"}%")
        with col3:
            st.metric("Sector Performance", f"{data['performance']"+.1f"}%")

def display_price_alerts(stock_data: Dict[str, Any]):
    """Display price alerts and warnings"""
    st.subheader("🚨 Price Alerts")

    current_price = stock_data.get('price', 0)
    high_52w = stock_data.get('fifty_two_week_high')
    low_52w = stock_data.get('fifty_two_week_low')

    alerts = []

    if high_52w and current_price >= high_52w * 0.95:
        alerts.append("⚠️ Price near 52-week high")

    if low_52w and current_price <= low_52w * 1.05:
        alerts.append("⚠️ Price near 52-week low")

    if stock_data.get('change_percent', 0) < -5:
        alerts.append("🔻 Significant price decline today")

    if stock_data.get('change_percent', 0) > 5:
        alerts.append("🔺 Significant price increase today")

    if alerts:
        for alert in alerts:
            st.warning(alert)
    else:
        st.success("✅ No significant price alerts")

def create_stock_comparison(symbols: List[str], stock_data_list: List[Dict[str, Any]]):
    """Create comparison chart for multiple stocks"""
    st.subheader("📊 Stock Comparison")

    if len(symbols) < 2:
        st.info("Add at least 2 stocks to compare")
        return

    # Create comparison data
    comparison_data = []
    for symbol, data in zip(symbols, stock_data_list):
        comparison_data.append({
            'Symbol': symbol,
            'Price': data.get('price', 0),
            'Change %': data.get('change_percent', 0),
            'Volume': data.get('volume', 0),
            'Market Cap': data.get('market_cap', 0)
        })

    df = pd.DataFrame(comparison_data)

    # Price comparison
    fig = px.bar(df, x='Symbol', y='Price', title='Stock Price Comparison')
    st.plotly_chart(fig, use_container_width=True)

    # Performance comparison
    fig2 = px.bar(df, x='Symbol', y='Change %', title='Daily Performance Comparison',
                  color='Change %', color_continuous_scale='RdYlGn')
    st.plotly_chart(fig2, use_container_width=True)

def display_portfolio_allocation(portfolio_data: Dict[str, Any]):
    """Display portfolio allocation"""
    st.subheader("📊 Portfolio Allocation")

    if not portfolio_data.get('sector_allocation'):
        st.info("No sector allocation data available")
        return

    # Create pie chart
    sectors = portfolio_data['sector_allocation']
    fig = px.pie(
        values=list(sectors.values()),
        names=list(sectors.keys()),
        title="Portfolio Sector Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

    # Display allocation table
    st.subheader("Sector Breakdown")
    allocation_df = pd.DataFrame([
        {'Sector': sector, 'Allocation %': allocation}
        for sector, allocation in sectors.items()
    ])
    st.dataframe(allocation_df)

def display_risk_metrics(stock_data: Dict[str, Any]):
    """Display risk metrics"""
    st.subheader("⚠️ Risk Analysis")

    # Calculate basic risk metrics
    change_pct = abs(stock_data.get('change_percent', 0))

    col1, col2, col3 = st.columns(3)

    with col1:
        if change_pct > 3:
            risk_level = "High"
            color = "🔴"
        elif change_pct > 1.5:
            risk_level = "Medium"
            color = "🟡"
        else:
            risk_level = "Low"
            color = "🟢"

        st.metric("Volatility Risk", f"{color} {risk_level}")

    with col2:
        pe_ratio = stock_data.get('pe_ratio', 0)
        if pe_ratio > 30:
            valuation = "Overvalued"
        elif pe_ratio < 15:
            valuation = "Undervalued"
        else:
            valuation = "Fair Value"

        st.metric("Valuation", valuation)

    with col3:
        sector = stock_data.get('sector', '')
        if sector in ['Technology', 'Biotechnology']:
            sector_risk = "High"
        elif sector in ['Utilities', 'Consumer Staples']:
            sector_risk = "Low"
        else:
            sector_risk = "Medium"

        st.metric("Sector Risk", sector_risk)

def create_watchlist_manager():
    """Create watchlist management interface"""
    st.subheader("⭐ Watchlist")

    # Initialize watchlist in session state
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = []

    col1, col2 = st.columns([3, 1])

    with col1:
        new_symbol = st.text_input("Add stock to watchlist", "").upper()

        if st.button("Add to Watchlist"):
            if new_symbol and new_symbol not in st.session_state.watchlist:
                st.session_state.watchlist.append(new_symbol)
                st.success(f"Added {new_symbol} to watchlist")
                st.rerun()

    with col2:
        if st.button("Clear Watchlist"):
            st.session_state.watchlist = []
            st.rerun()

    # Display watchlist
    if st.session_state.watchlist:
        st.write("**Current Watchlist:**")
        for symbol in st.session_state.watchlist:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"• {symbol}")
            with col2:
                if st.button(f"Remove {symbol}", key=f"remove_{symbol}"):
                    st.session_state.watchlist.remove(symbol)
                    st.rerun()
    else:
        st.info("Your watchlist is empty")

def display_market_heatmap():
    """Display market heatmap"""
    st.subheader("🔥 Market Heatmap")

    # Mock heatmap data
    sectors = ['Technology', 'Financial', 'Healthcare', 'Energy', 'Consumer']
    heatmap_data = []

    for sector in sectors:
        for i in range(5):  # 5 stocks per sector
            heatmap_data.append({
                'Sector': sector,
                'Symbol': f'{sector[:3].upper()}{i+1}',
                'Performance': (i - 2) * 5 + (hash(sector) % 20 - 10),  # Mock performance
                'Volume': 1000000 + i * 500000
            })

    df = pd.DataFrame(heatmap_data)

    # Create heatmap
    fig = px.scatter(df, x='Sector', y='Symbol', size='Volume', color='Performance',
                     color_continuous_scale='RdYlGn', size_max=60)
    st.plotly_chart(fig, use_container_width=True)