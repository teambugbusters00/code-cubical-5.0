"""
News Data Ingestion Module
Handles fetching financial news from multiple sources including RSS feeds and APIs
"""

import feedparser
import requests
import pandas as pd
from datetime import datetime, timedelta
import logging
import asyncio
import httpx
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv
from textblob import TextBlob

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsDataIngestion:
    """Handles financial news ingestion from multiple sources"""

    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')

        # RSS feed URLs for financial news
        self.rss_feeds = {
            'yahoo_finance': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'marketwatch': 'https://feeds.marketwatch.com/marketwatch/marketpulse/',
            'reuters_business': 'https://feeds.reuters.com/Reuters/businessNews',
            'cnbc': 'https://www.cnbc.com/id/100003114/device/rss/rss.html',
            'bloomberg': 'https://feeds.bloomberg.com/markets/news.rss'
        }

    async def get_news_from_rss(self, feed_url: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get news from RSS feed"""
        try:
            # Use requests for RSS feeds (feedparser doesn't support async)
            response = requests.get(feed_url, timeout=10)
            response.raise_for_status()

            feed = feedparser.parse(response.content)
            news_items = []

            for entry in feed.entries[:limit]:
                # Analyze sentiment
                sentiment = self._analyze_sentiment(entry.title + ' ' + (entry.summary if hasattr(entry, 'summary') else ''))

                news_item = {
                    'title': entry.title,
                    'summary': entry.summary if hasattr(entry, 'summary') else '',
                    'url': entry.link,
                    'published_at': self._parse_date(entry.published if hasattr(entry, 'published') else datetime.now().isoformat()),
                    'sentiment_score': sentiment['score'],
                    'sentiment_label': sentiment['label'],
                    'source': feed.feed.title if hasattr(feed.feed, 'title') else 'RSS Feed',
                    'symbols': self._extract_symbols(entry.title + ' ' + (entry.summary if hasattr(entry, 'summary') else ''))
                }
                news_items.append(news_item)

            return news_items

        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
            return []

    async def get_news_from_alpha_vantage(self, symbol: str = '', limit: int = 10) -> List[Dict[str, Any]]:
        """Get news from Alpha Vantage API"""
        if not self.alpha_vantage_key:
            return []

        try:
            url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&apikey={self.alpha_vantage_key}&limit={limit}"
            if symbol:
                url += f"&tickers={symbol}"

            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            news_items = []
            if 'feed' in data:
                for item in data['feed'][:limit]:
                    sentiment = self._analyze_sentiment(item.get('title', '') + ' ' + item.get('summary', ''))

                    news_items.append({
                        'title': item.get('title', ''),
                        'summary': item.get('summary', ''),
                        'url': item.get('url', ''),
                        'published_at': item.get('time_published', ''),
                        'sentiment_score': sentiment['score'],
                        'sentiment_label': sentiment['label'],
                        'source': 'Alpha Vantage',
                        'symbols': [symbol] if symbol else []
                    })

            return news_items

        except Exception as e:
            logger.error(f"Alpha Vantage news error: {e}")
            return []

    async def get_news_from_newsapi(self, query: str = 'finance', limit: int = 20) -> List[Dict[str, Any]]:
        """Get news from News API"""
        if not self.news_api_key:
            return []

        try:
            url = f"https://newsapi.org/v2/everything?q={query}&apiKey={self.news_api_key}&language=en&pageSize={limit}&sortBy=publishedAt"

            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()

            news_items = []
            if data.get('status') == 'ok' and 'articles' in data:
                for article in data['articles'][:limit]:
                    sentiment = self._analyze_sentiment(article.get('title', '') + ' ' + article.get('description', ''))

                    news_items.append({
                        'title': article.get('title', ''),
                        'summary': article.get('description', ''),
                        'url': article.get('url', ''),
                        'published_at': article.get('publishedAt', ''),
                        'sentiment_score': sentiment['score'],
                        'sentiment_label': sentiment['label'],
                        'source': article.get('source', {}).get('name', 'News API'),
                        'symbols': self._extract_symbols(article.get('title', '') + ' ' + article.get('description', ''))
                    })

            return news_items

        except Exception as e:
            logger.error(f"News API error: {e}")
            return []

    async def get_all_news(self, symbols: Optional[List[str]] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get news from all available sources"""
        all_news = []

        # Get RSS news
        rss_tasks = []
        for feed_name, feed_url in self.rss_feeds.items():
            rss_tasks.append(self.get_news_from_rss(feed_url, limit=10))

        # Get Alpha Vantage news for specific symbols
        if symbols:
            for symbol in symbols:
                all_news.extend(await self.get_news_from_alpha_vantage(symbol, limit=5))

        # Get general financial news from News API
        all_news.extend(await self.get_news_from_newsapi('finance OR stocks OR market', limit=20))

        # Collect RSS news
        rss_results = await asyncio.gather(*rss_tasks, return_exceptions=True)
        for result in rss_results:
            if isinstance(result, list):
                all_news.extend(result)

        # Remove duplicates and sort by date
        seen_urls = set()
        unique_news = []

        for news in all_news:
            if news['url'] not in seen_urls:
                seen_urls.add(news['url'])
                unique_news.append(news)

        # Sort by published date (most recent first)
        unique_news.sort(key=lambda x: x['published_at'], reverse=True)

        return unique_news[:limit]

    async def get_company_specific_news(self, symbol: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get news specific to a company/symbol"""
        company_news = []

        # Get news from Alpha Vantage for this symbol
        av_news = await self.get_news_from_alpha_vantage(symbol, limit=10)
        company_news.extend(av_news)

        # Get general news and filter for this symbol
        general_news = await self.get_all_news(limit=50)
        symbol_news = [news for news in general_news if symbol in news.get('symbols', [])]

        company_news.extend(symbol_news)

        # Sort by date and limit
        company_news.sort(key=lambda x: x['published_at'], reverse=True)
        return company_news[:limit]

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity

            if polarity > 0.1:
                label = 'positive'
                emoji = '🚀'
            elif polarity < -0.1:
                label = 'negative'
                emoji = '⚠️'
            else:
                label = 'neutral'
                emoji = '📊'

            return {
                'score': round(polarity, 3),
                'label': label,
                'emoji': emoji
            }
        except Exception as e:
            logger.warning(f"Sentiment analysis error: {e}")
            return {
                'score': 0.0,
                'label': 'neutral',
                'emoji': '📊'
            }

    def _extract_symbols(self, text: str) -> List[str]:
        """Extract stock symbols from text"""
        # Common stock symbols (this is a simplified version)
        # In production, you'd use a more comprehensive symbol database
        common_symbols = {
            'Apple': 'AAPL', 'Microsoft': 'MSFT', 'Google': 'GOOGL', 'Amazon': 'AMZN',
            'Tesla': 'TSLA', 'NVIDIA': 'NVDA', 'JPMorgan': 'JPM', 'Johnson & Johnson': 'JNJ',
            'Visa': 'V', 'Walmart': 'WMT', 'Meta': 'META', 'Netflix': 'NFLX',
            'Coca-Cola': 'KO', 'Pepsi': 'PEP', 'McDonald': 'MCD', 'Nike': 'NKE'
        }

        found_symbols = []
        text_lower = text.lower()

        for company, symbol in common_symbols.items():
            if company.lower() in text_lower:
                found_symbols.append(symbol)

        return list(set(found_symbols))  # Remove duplicates

    def _parse_date(self, date_str: str) -> str:
        """Parse date string to ISO format"""
        try:
            # Try different date formats
            if date_str:
                # Remove timezone info and parse
                date_str = date_str.split('+')[0].split('T')[0] + 'T' + date_str.split('T')[1].split('+')[0] if 'T' in date_str else date_str
                return datetime.fromisoformat(date_str.replace('Z', '+00:00')).isoformat()
            else:
                return datetime.now().isoformat()
        except:
            return datetime.now().isoformat()

    async def get_news_data(self, symbols: Optional[List[str]] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get comprehensive news data from all sources"""
        try:
            # Get news from all available sources
            news_data = await self.get_all_news(symbols=symbols, limit=limit)

            # Add additional metadata
            for news_item in news_data:
                news_item['timestamp'] = datetime.now().isoformat()
                news_item['source_type'] = 'aggregated'

            return news_data

        except Exception as e:
            logger.error(f"Error in get_news_data: {e}")
            return [{
                'title': 'Error fetching news',
                'summary': 'Unable to retrieve news data',
                'url': '',
                'published_at': datetime.now().isoformat(),
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'source': 'System',
                'symbols': [],
                'timestamp': datetime.now().isoformat(),
                'source_type': 'error',
                'error': str(e)
            }]

# Global instance
news_ingestion = NewsDataIngestion()

if __name__ == "__main__":
    async def main():
        # Test news ingestion
        print("Testing news ingestion...")

        # Get general news
        news = await news_ingestion.get_all_news(limit=5)
        print(f"Fetched {len(news)} news items")

        # Get company-specific news
        aapl_news = await news_ingestion.get_company_specific_news('AAPL', limit=3)
        print(f"Fetched {len(aapl_news)} Apple-specific news items")

        for item in news[:3]:
            print(f"- {item['title']} ({item['sentiment_emoji']})")

    asyncio.run(main())