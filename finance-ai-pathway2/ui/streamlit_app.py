"""
Streamlit Frontend for Finance AI Assistant
Provides interactive web interface for financial data analysis
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from datetime import datetime, timedelta
import time
from typing import Dict, Any, List, Optional
import os

# Configure page
st.set_page_config(
    page_title="Finance AI Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

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
    .news-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .sentiment-positive {
        color: #28a745;
        font-weight: bold;
    }
    .sentiment-negative {
        color: #dc3545;
        font-weight: bold;
    }
    .sentiment-neutral {
        color: #6c757d;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application"""
    st.markdown('<div class="main-header">🤖 Finance AI Assistant</div>', unsafe_allow_html=True)

    # Sidebar navigation
    page = st.sidebar.selectbox(
        "Navigation",
        ["Chatbot", "Stocks Dashboard", "News Feed", "Portfolio Monitor", "Market Overview"]
    )

    # Display selected page
    if page == "Chatbot":
        show_chatbot()
    elif page == "Stocks Dashboard":
        show_stocks_dashboard()
    elif page == "News Feed":
        show_news_feed()
    elif page == "Portfolio Monitor":
        show_portfolio_monitor()
    elif page == "Market Overview":
        show_market_overview()

def show_chatbot():
    """Chatbot interface"""
    st.header("💬 AI Financial Assistant")

    # Initialize chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input
    user_input = st.chat_input("Ask me about stocks, market news, or financial analysis...")

    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Display user message
        with st.chat_message("user"):
            st.write(user_input)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = query_api("/api/query", {"query": user_input})
                    if response:
                        st.write(response["response"])

                        # Display context documents if available
                        if response.get("context_docs"):
                            with st.expander("📚 Context Sources"):
                                for i, doc in enumerate(response["context_docs"], 1):
                                    st.write(f"**{i}.** {doc['content']}")

                        # Add assistant response to history
                        st.session_state.chat_history.append({"role": "assistant", "content": response["response"]})
                    else:
                        st.error("Failed to get response from AI assistant")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def show_stocks_dashboard():
    """Stocks dashboard"""
    st.header("📊 Stocks Dashboard")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Stock symbol input
        symbol = st.text_input("Enter stock symbol (e.g., AAPL, MSFT, GOOGL)", "AAPL").upper()

        if st.button("Get Stock Data", type="primary"):
            with st.spinner(f"Fetching data for {symbol}..."):
                try:
                    # Get stock info
                    stock_data = query_api(f"/api/stocks/{symbol}")
                    if stock_data:
                        display_stock_info(stock_data)

                        # Get historical data
                        history_data = query_api(f"/api/stocks/{symbol}/history?period=1mo")
                        if history_data and history_data.get("data"):
                            display_stock_chart(history_data["data"], symbol)

                        # Get analysis
                        analysis_data = query_api(f"/api/stocks/{symbol}/analysis")
                        if analysis_data:
                            display_stock_analysis(analysis_data)

                    else:
                        st.error(f"Could not fetch data for {symbol}")

                except Exception as e:
                    st.error(f"Error fetching stock data: {str(e)}")

    with col2:
        st.subheader("📈 Market Indices")

        try:
            indices_data = query_api("/api/market/indices")
            if indices_data:
                for symbol, data in indices_data.items():
                    change_color = "green" if data["change"] >= 0 else "red"
                    st.metric(
                        label=f"{data['name']} ({symbol})",
                        value=f"${data['current_price']:.2f}",
                        delta=f"{data['change']:+.2f} ({data['change_percent']:+.2f}%)",
                        delta_color="normal" if data["change"] >= 0 else "inverse"
                    )
        except Exception as e:
            st.error(f"Error fetching market indices: {str(e)}")

def show_news_feed():
    """News feed interface"""
    st.header("📰 Financial News Feed")

    col1, col2 = st.columns([2, 1])

    with col1:
        # Get news data
        try:
            news_data = query_api("/api/news?limit=20")
            if news_data:
                for i, news_item in enumerate(news_data[:10], 1):
                    with st.container():
                        st.markdown(f"""
                        <div class="news-card">
                            <h4>{news_item['title']}</h4>
                            <p>{news_item['summary']}</p>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span><strong>Source:</strong> {news_item['source']}</span>
                                <span class="sentiment-{news_item['sentiment_label']}">{news_item['sentiment_label'].upper()} 🚀</span>
                            </div>
                            <div style="margin-top: 0.5rem;">
                                <a href="{news_item['url']}" target="_blank">Read more</a>
                                <span style="margin-left: 1rem; color: #666;">
                                    {news_item['published_at'][:10]}
                                </span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        if i < 10:  # Add separator except for last item
                            st.divider()

            else:
                st.info("No news data available")

        except Exception as e:
            st.error(f"Error fetching news: {str(e)}")

    with col2:
        st.subheader("🔍 Company News")

        # Company-specific news
        company_symbol = st.text_input("Enter company symbol", "AAPL").upper()

        if st.button("Get Company News"):
            try:
                company_news = query_api(f"/api/news/{company_symbol}?limit=5")
                if company_news:
                    st.write(f"**Recent news for {company_symbol}:**")
                    for news_item in company_news:
                        st.markdown(f"""
                        - **{news_item['title']}**
                          *{news_item['summary']}*
                          *Sentiment: {news_item['sentiment_label']} | Source: {news_item['source']}*
                        """)
                else:
                    st.info(f"No recent news for {company_symbol}")
            except Exception as e:
                st.error(f"Error fetching company news: {str(e)}")

def show_portfolio_monitor():
    """Portfolio monitor interface"""
    st.header("💼 Portfolio Monitor")

    try:
        # Get portfolio data
        portfolio_data = query_api("/api/portfolio")
        if portfolio_data:
            display_portfolio_summary(portfolio_data)

            # Get portfolio insights
            insights_data = query_api("/api/portfolio/insights")
            if insights_data:
                display_portfolio_insights(insights_data)

        else:
            st.info("No portfolio data available. Please add some holdings to get started.")

    except Exception as e:
        st.error(f"Error loading portfolio data: {str(e)}")

def show_market_overview():
    """Market overview interface"""
    st.header("🌍 Market Overview")

    try:
        # Get market overview data
        overview_data = query_api("/api/market/overview")
        if overview_data:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("📊 Market Indices")
                indices = overview_data.get("market_indices", {})
                for symbol, data in indices.items():
                    st.metric(
                        label=f"{data['name']}",
                        value=f"${data['current_price']:.2f}",
                        delta=f"{data['change']:+.2f}"
                    )

            with col2:
                st.subheader("📰 Top News")
                news = overview_data.get("top_news", [])
                for i, news_item in enumerate(news[:3], 1):
                    st.write(f"**{i}.** {news_item['title']}")
                    st.caption(news_item['summary'][:100] + "...")

            with col3:
                st.subheader("💭 Market Sentiment")
                sentiment = overview_data.get("sentiment_summary", {})
                st.metric("Positive Sentiment", sentiment.get("positive_count", 0))
                st.metric("Negative Sentiment", sentiment.get("negative_count", 0))
                st.metric("Neutral Sentiment", sentiment.get("neutral_count", 0))

            # Sentiment details
            st.subheader("📈 Top Sentiment Analysis")
            sentiments = overview_data.get("top_sentiments", [])
            for sentiment in sentiments:
                st.write(f"**{sentiment['symbol']}**: {sentiment['sentiment_label']} ({sentiment['sentiment_score']:.3f})")

        else:
            st.info("Market overview data not available")

    except Exception as e:
        st.error(f"Error loading market overview: {str(e)}")

# Helper functions
def query_api(endpoint: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Query the API"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        if data and endpoint.startswith("/api/query"):
            response = requests.post(url, json=data)
        else:
            response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
            return None
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
        return None

def display_stock_info(stock_data: Dict[str, Any]):
    """Display stock information"""
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

    # Additional info
    st.write(f"**Sector:** {stock_data.get('sector', 'N/A')}")
    st.write(f"**P/E Ratio:** {stock_data.get('pe_ratio', 'N/A')}")
    st.write(f"**Dividend Yield:** {stock_data.get('dividend_yield', 'N/A')}")

def display_stock_chart(history_data: List[Dict[str, Any]], symbol: str):
    """Display stock price chart"""
    st.subheader(f"📈 {symbol} Price History")

    # Convert to DataFrame
    df = pd.DataFrame(history_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')

    # Create chart
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

def display_stock_analysis(analysis_data: Dict[str, Any]):
    """Display stock analysis"""
    st.subheader("🔍 Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"**Trend:** {analysis_data['trend'].title()}")
        st.write(f"**52W High:** ${analysis_data.get('fifty_two_week_high', 'N/A')}")
        st.write(f"**52W Low:** ${analysis_data.get('fifty_two_week_low', 'N/A')}")

    with col2:
        sentiment = analysis_data.get('sentiment_analysis', {})
        if sentiment:
            st.write(f"**Sentiment:** {sentiment.get('sentiment_label', 'N/A').title()}")
            st.write(f"**News Count:** {sentiment.get('news_count', 0)}")

def display_portfolio_summary(portfolio_data: Dict[str, Any]):
    """Display portfolio summary"""
    st.subheader("📊 Portfolio Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total Value", f"${portfolio_data['total_value']",.2f"}")

    with col2:
        gain_loss = portfolio_data['total_gain_loss']
        color = "normal" if gain_loss >= 0 else "inverse"
        st.metric("Total P&L", f"${gain_loss",.2f"}", delta_color=color)

    with col3:
        st.metric("Holdings", portfolio_data['holdings_count'])

    with col4:
        st.metric("P&L %", f"{portfolio_data['total_gain_loss_percent']".2f"}%")

    # Sector allocation chart
    if portfolio_data.get('sector_allocation'):
        st.subheader("🏢 Sector Allocation")

        sectors = portfolio_data['sector_allocation']
        fig = px.pie(
            values=list(sectors.values()),
            names=list(sectors.keys()),
            title="Portfolio Sector Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)

def display_portfolio_insights(insights_data: Dict[str, Any]):
    """Display portfolio insights"""
    st.subheader("🧠 AI Insights")

    # Risk assessment
    risk = insights_data.get('risk_assessment', {})
    if risk:
        st.write(f"**Risk Level:** {risk.get('risk_level', 'unknown').title()}")
        st.write(f"**Diversification Score:** {risk.get('diversification_score', 0)} sectors")

    # Sentiment summary
    sentiment = insights_data.get('sentiment_summary', {})
    if sentiment:
        st.write("**Market Sentiment:**")
        st.write(f"- Positive: {sentiment.get('positive', 0)}")
        st.write(f"- Negative: {sentiment.get('negative', 0)}")
        st.write(f"- Neutral: {sentiment.get('neutral', 0)}")

    # Recommendations
    recommendations = insights_data.get('recommendations', [])
    if recommendations:
        st.subheader("💡 Recommendations")
        for i, rec in enumerate(recommendations, 1):
            st.write(f"{i}. {rec}")

if __name__ == "__main__":
    main()