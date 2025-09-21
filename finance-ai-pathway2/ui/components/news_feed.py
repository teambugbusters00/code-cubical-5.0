"""
News Feed Component for Streamlit
Provides news display and filtering components
"""

import streamlit as st
from typing import List, Dict, Any, Optional

def display_news_item(news_item: Dict[str, Any], show_summary: bool = True):
    """Display a single news item"""
    st.markdown(f"""
    <div style="background-color: white; padding: 1rem; border-radius: 0.5rem; border: 1px solid #e0e0e0; margin-bottom: 1rem;">
        <h4 style="margin-bottom: 0.5rem;">{news_item['title']}</h4>
        {f'<p style="color: #666; margin-bottom: 0.5rem;">{news_item["summary"]}</p>' if show_summary and news_item.get('summary') else ''}
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
            <span style="font-size: 0.9rem; color: #666;">
                <strong>Source:</strong> {news_item['source']} |
                <strong>Published:</strong> {news_item['published_at'][:10]}
            </span>
            <span style="font-weight: bold; color: {'#28a745' if news_item['sentiment_label'] == 'positive' else '#dc3545' if news_item['sentiment_label'] == 'negative' else '#6c757d'};">
                {news_item['sentiment_label'].upper()} {'🚀' if news_item['sentiment_label'] == 'positive' else '⚠️' if news_item['sentiment_label'] == 'negative' else '📊'}
            </span>
        </div>
        <div style="margin-top: 0.5rem;">
            <a href="{news_item['url']}" target="_blank" style="color: #1f77b4;">Read full article →</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_news_list(news_data: List[Dict[str, Any]], max_items: int = 10):
    """Display a list of news items"""
    if not news_data:
        st.info("No news available")
        return

    for i, news_item in enumerate(news_data[:max_items], 1):
        display_news_item(news_item)

        if i < max_items and i < len(news_data):
            st.divider()

def create_sentiment_filter():
    """Create sentiment filter controls"""
    col1, col2, col3 = st.columns(3)

    with col1:
        positive_filter = st.checkbox("Positive", value=True)

    with col2:
        neutral_filter = st.checkbox("Neutral", value=True)

    with col3:
        negative_filter = st.checkbox("Negative", value=True)

    return {
        'positive': positive_filter,
        'neutral': neutral_filter,
        'negative': negative_filter
    }

def filter_news_by_sentiment(news_data: List[Dict[str, Any]], filters: Dict[str, bool]) -> List[Dict[str, Any]]:
    """Filter news by sentiment"""
    filtered_news = []

    for news_item in news_data:
        sentiment = news_item.get('sentiment_label', 'neutral')

        if filters.get(sentiment, True):
            filtered_news.append(news_item)

    return filtered_news

def create_symbol_filter():
    """Create symbol filter controls"""
    symbol_input = st.text_input("Filter by stock symbol (e.g., AAPL)", "")
    return symbol_input.upper() if symbol_input else ""

def filter_news_by_symbol(news_data: List[Dict[str, Any]], symbol: str) -> List[Dict[str, Any]]:
    """Filter news by stock symbol"""
    if not symbol:
        return news_data

    filtered_news = []

    for news_item in news_data:
        symbols = news_item.get('symbols', [])
        if symbol in symbols:
            filtered_news.append(news_item)

    return filtered_news

def display_sentiment_summary(news_data: List[Dict[str, Any]]):
    """Display sentiment summary"""
    if not news_data:
        return

    # Calculate sentiment counts
    sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}

    for news_item in news_data:
        sentiment = news_item.get('sentiment_label', 'neutral')
        sentiment_counts[sentiment] += 1

    total = len(news_data)

    # Display summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Total News", total)

    with col2:
        positive_pct = (sentiment_counts['positive'] / total * 100) if total > 0 else 0
        st.metric("Positive", f"{sentiment_counts['positive']} ({positive_pct".1f"}%)")

    with col3:
        neutral_pct = (sentiment_counts['neutral'] / total * 100) if total > 0 else 0
        st.metric("Neutral", f"{sentiment_counts['neutral']} ({neutral_pct".1f"}%)")

    with col4:
        negative_pct = (sentiment_counts['negative'] / total * 100) if total > 0 else 0
        st.metric("Negative", f"{sentiment_counts['negative']} ({negative_pct".1f"}%)")

    # Sentiment distribution chart
    st.subheader("Sentiment Distribution")
    import plotly.express as px

    sentiment_df = []
    for sentiment, count in sentiment_counts.items():
        sentiment_df.append({'Sentiment': sentiment.title(), 'Count': count})

    fig = px.pie(
        sentiment_df,
        values='Count',
        names='Sentiment',
        color='Sentiment',
        color_discrete_map={
            'Positive': '#28a745',
            'Neutral': '#6c757d',
            'Negative': '#dc3545'
        }
    )
    st.plotly_chart(fig, use_container_width=True)

def create_news_search():
    """Create news search interface"""
    search_query = st.text_input("Search news articles", "")
    return search_query

def search_news(news_data: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Search news by query"""
    if not query:
        return news_data

    query_lower = query.lower()
    matching_news = []

    for news_item in news_data:
        title = news_item.get('title', '').lower()
        summary = news_item.get('summary', '').lower()

        if query_lower in title or query_lower in summary:
            matching_news.append(news_item)

    return matching_news

def display_news_sources(news_data: List[Dict[str, Any]]):
    """Display news sources breakdown"""
    if not news_data:
        return

    # Count sources
    sources = {}
    for news_item in news_data:
        source = news_item.get('source', 'Unknown')
        sources[source] = sources.get(source, 0) + 1

    # Display source breakdown
    st.subheader("News Sources")

    col1, col2 = st.columns([2, 1])

    with col1:
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            st.write(f"• **{source}**: {count} articles")

    with col2:
        st.metric("Total Sources", len(sources))

def create_date_filter():
    """Create date filter controls"""
    col1, col2 = st.columns(2)

    with col1:
        days_back = st.selectbox(
            "Show news from last",
            [1, 3, 7, 14, 30],
            index=2
        )

    with col2:
        st.write(f"Showing news from the last {days_back} days")

    return days_back

def filter_news_by_date(news_data: List[Dict[str, Any]], days_back: int) -> List[Dict[str, Any]]:
    """Filter news by date"""
    from datetime import datetime, timedelta

    cutoff_date = datetime.now() - timedelta(days=days_back)

    filtered_news = []

    for news_item in news_data:
        try:
            published_date = datetime.fromisoformat(news_item['published_at'].replace('Z', '+00:00'))
            if published_date >= cutoff_date:
                filtered_news.append(news_item)
        except:
            # If date parsing fails, include the item
            filtered_news.append(news_item)

    return filtered_news

def display_trending_topics(news_data: List[Dict[str, Any]], top_n: int = 5):
    """Display trending topics"""
    if not news_data:
        return

    st.subheader("🔥 Trending Topics")

    # Extract keywords from titles (simplified)
    keywords = {}

    for news_item in news_data:
        title = news_item.get('title', '').lower()
        words = title.split()

        for word in words:
            if len(word) > 4:  # Only consider words longer than 4 characters
                keywords[word] = keywords.get(word, 0) + 1

    # Get top keywords
    top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:top_n]

    # Display trending topics
    cols = st.columns(min(len(top_keywords), 3))

    for i, (keyword, count) in enumerate(top_keywords):
        with cols[i % len(cols)]:
            st.metric(f"#{keyword.title()}", count)

def create_news_refresh_button():
    """Create news refresh button"""
    if st.button("🔄 Refresh News", type="primary"):
        st.rerun()

def display_news_analytics(news_data: List[Dict[str, Any]]):
    """Display news analytics"""
    if not news_data:
        return

    st.subheader("📊 News Analytics")

    # Time series of news
    try:
        dates = []
        for news_item in news_data:
            try:
                date = news_item['published_at'][:10]
                dates.append(date)
            except:
                pass

        if dates:
            from collections import Counter
            date_counts = Counter(dates)

            # Create simple time series
            st.write("**News Volume by Date:**")
            for date, count in sorted(date_counts.items()):
                st.write(f"- {date}: {count} articles")

    except Exception as e:
        st.error(f"Error creating analytics: {e}")