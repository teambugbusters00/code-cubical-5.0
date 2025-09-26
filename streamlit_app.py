import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
import os

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="Finance AI Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------------------
# API Configuration
# -------------------------------
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# -------------------------------
# Custom CSS (UI Layer)
# -------------------------------
st.markdown("""
<style>
    .block-container { padding: 2rem 2rem; background: radial-gradient(circle at top left, #0E1117, #111418 60%); color: #E0E0E0; }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0E1117, #1A1E25); border-right: 1px solid #2C303E; }
    .main-header { font-size: 2.5rem; font-weight: 800; text-align: center; background: linear-gradient(90deg, #00BFFF, #58A6FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 1.5rem; }
    .glass-card { background: rgba(20, 24, 32, 0.7); border-radius: 16px; border: 1px solid rgba(0, 191, 255, 0.25); padding: 1rem; margin-bottom: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.4); }
    .chat-user { background: #00BFFF; color: white; padding: 10px 16px; border-radius: 14px 14px 0 14px; margin: 8px; float: right; max-width: 70%; }
    .chat-assistant { background: #1E222C; color: #E0E0E0; padding: 10px 16px; border-radius: 14px 14px 14px 0; margin: 8px; float: left; max-width: 70%; border: 1px solid #2C303E; }
    .news-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1rem; }
    .news-card { background: rgba(25, 28, 36, 0.9); padding: 1rem; border-radius: 14px; border-left: 5px solid #00BFFF; transition: all 0.2s ease-in-out; }
    .news-card:hover { transform: scale(1.03); border-left: 5px solid #58A6FF; }
    .news-card h4 { color: #00BFFF; font-size: 1.1rem; margin-bottom: 0.5rem; }
    .sentiment-positive {color:#3CB371; font-weight:600;}
    .sentiment-negative {color:#FF6347; font-weight:600;}
    .sentiment-neutral {color:#A9A9A9; font-weight:600;}
    [data-testid="stMetric"] { background: linear-gradient(160deg, #1C2028, #2C303E); border-radius: 12px; padding: 1rem; border: 1px solid rgba(0,191,255,0.25); transition: transform 0.2s ease; }
    [data-testid="stMetric"]:hover {transform: scale(1.04);}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# API Helper
# -------------------------------
def query_api(endpoint: str, data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    try:
        if data:
            response = requests.post(f"{API_BASE_URL}/{endpoint}", json=data)
        else:
            response = requests.get(f"{API_BASE_URL}/{endpoint}")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
    return None

# -------------------------------
# Pages
# -------------------------------
def show_home():
    st.markdown('<div class="main-header">🤖 Finance AI Assistant</div>', unsafe_allow_html=True)
    st.write("Welcome to your all-in-one finance dashboard 🚀")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Market Sentiment", "Bullish", "+5%")
    with col2:
        st.metric("Portfolio Value", "$120,500", "+3.4%")
    with col3:
        st.metric("Top Gainer", "AAPL", "+2.1%")

    data = pd.DataFrame({"Stock": ["AAPL", "MSFT", "GOOGL", "AMZN"], "Performance": [2.1, -0.8, 1.4, 0.6]})
    fig = px.bar(data, x="Stock", y="Performance", color="Performance", color_continuous_scale="Blues", title="Daily Stock Performance")
    st.plotly_chart(fig, use_container_width=True)


def show_chatbot():
    st.markdown('<div class="main-header">💬 AI Chatbot</div>', unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        role, text = msg["role"], msg["content"]
        css_class = "chat-user" if role == "user" else "chat-assistant"
        st.markdown(f'<div class="{css_class}">{text}</div>', unsafe_allow_html=True)

    user_input = st.chat_input("Ask a financial question...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = query_api("chat", {"message": user_input})
        if response and "reply" in response:
            st.session_state.messages.append({"role": "assistant", "content": response["reply"]})


def show_stocks_dashboard():
    st.markdown('<div class="main-header">📊 Stocks Dashboard</div>', unsafe_allow_html=True)
    symbol = st.text_input("Enter Stock Symbol (e.g., AAPL)")
    if symbol:
        data = query_api("stock_analysis", {"symbol": symbol})
        if data:
            col1, col2 = st.columns([2, 1])
            with col1:
                df = pd.DataFrame(data["history"])
                fig = px.line(df, x="date", y="close", title=f"{symbol} Price History")
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                st.metric("Current Price", f"${data['current_price']}")
                st.metric("Change", f"{data['change_percent']}%")


def show_news_feed():
    st.markdown('<div class="main-header">📰 News Feed</div>', unsafe_allow_html=True)
    news = query_api("news")
    if news and "articles" in news:
        st.markdown('<div class="news-grid">', unsafe_allow_html=True)
        for article in news["articles"]:
            st.markdown(f'<div class="news-card"><h4>{article["title"]}</h4><p>{article["summary"]}</p><p class="sentiment-{article["sentiment"]}">Sentiment: {article["sentiment"]}</p></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def show_portfolio_monitor():
    st.markdown('<div class="main-header">📈 Portfolio Monitor</div>', unsafe_allow_html=True)
    portfolio = query_api("portfolio")
    if portfolio and "assets" in portfolio:
        df = pd.DataFrame(portfolio["assets"])
        col1, col2 = st.columns([2, 1])
        with col1:
            st.dataframe(df)
        with col2:
            fig = px.pie(df, names="asset", values="value", title="Portfolio Distribution")
            st.plotly_chart(fig, use_container_width=True)


def show_market_overview():
    st.markdown('<div class="main-header">🌍 Market Overview</div>', unsafe_allow_html=True)
    data = query_api("market_overview")
    if data and "indices" in data:
        st.dataframe(pd.DataFrame(data["indices"]))

# -------------------------------
# App Router
# -------------------------------
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio("Go to:", ["Home", "Chatbot", "Stocks Dashboard", "News Feed", "Portfolio Monitor", "Market Overview"])

if page == "Home":
    show_home()
elif page == "Chatbot":
    show_chatbot()
elif page == "Stocks Dashboard":
    show_stocks_dashboard()
elif page == "News Feed":
    show_news_feed()
elif page == "Portfolio Monitor":
    show_portfolio_monitor()
elif page == "Market Overview":
    show_market_overview()