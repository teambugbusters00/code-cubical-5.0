"""
Tests for data ingestion modules
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from datetime import datetime, timedelta

# Import modules to test
from ingestion.stock_stream import StockDataIngestion
from ingestion.news_stream import NewsDataIngestion
from ingestion.portfolio_stream import PortfolioDataIngestion


class TestStockDataIngestion:
    """Test stock data ingestion functionality"""

    @pytest.fixture
    def stock_ingestion(self):
        return StockDataIngestion()

    @pytest.mark.asyncio
    async def test_fetch_yahoo_finance_data(self, stock_ingestion):
        """Test fetching data from Yahoo Finance"""
        # Mock yfinance
        with patch('ingestion.stock_stream.yf') as mock_yf:
            mock_stock = Mock()
            mock_stock.history.return_value = pd.DataFrame({
                'Open': [100, 101, 102],
                'High': [105, 106, 107],
                'Low': [99, 100, 101],
                'Close': [104, 105, 106],
                'Volume': [1000, 1100, 1200]
            })
            mock_yf.Ticker.return_value = mock_stock

            result = await stock_ingestion.fetch_yahoo_finance_data('AAPL')

            assert result is not None
            assert 'symbol' in result
            assert 'price' in result
            assert 'change' in result
            assert result['symbol'] == 'AAPL'

    @pytest.mark.asyncio
    async def test_fetch_rapidapi_data(self, stock_ingestion):
        """Test fetching data from RapidAPI"""
        with patch('ingestion.stock_stream.httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                'Global Quote': {
                    '01. symbol': 'AAPL',
                    '05. price': '150.00',
                    '09. change': '2.50',
                    '10. change percent': '1.69%'
                }
            }
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await stock_ingestion.fetch_rapidapi_data('AAPL')

            assert result is not None
            assert result['symbol'] == 'AAPL'
            assert result['price'] == '150.00'

    def test_calculate_technical_indicators(self, stock_ingestion):
        """Test technical indicators calculation"""
        # Sample price data
        prices = [100, 102, 101, 105, 107, 106, 108]

        indicators = stock_ingestion.calculate_technical_indicators(prices)

        assert 'rsi' in indicators
        assert 'sma_5' in indicators
        assert 'sma_10' in indicators
        assert isinstance(indicators['rsi'], float)
        assert isinstance(indicators['sma_5'], float)


class TestNewsDataIngestion:
    """Test news data ingestion functionality"""

    @pytest.fixture
    def news_ingestion(self):
        return NewsDataIngestion()

    @pytest.mark.asyncio
    async def test_fetch_rss_news(self, news_ingestion):
        """Test RSS news fetching"""
        with patch('ingestion.news_stream.feedparser.parse') as mock_parse:
            mock_feed = Mock()
            mock_feed.entries = [
                Mock(title='Test News 1', summary='Summary 1', published_parsed=(2024, 1, 1, 0, 0, 0, 0, 0, 0)),
                Mock(title='Test News 2', summary='Summary 2', published_parsed=(2024, 1, 2, 0, 0, 0, 0, 0, 0))
            ]
            mock_parse.return_value = mock_feed

            result = await news_ingestion.fetch_rss_news()

            assert len(result) == 2
            assert result[0]['title'] == 'Test News 1'
            assert result[1]['title'] == 'Test News 2'

    @pytest.mark.asyncio
    async def test_fetch_news_api_data(self, news_ingestion):
        """Test News API data fetching"""
        with patch('ingestion.news_stream.httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.json.return_value = {
                'status': 'ok',
                'articles': [
                    {
                        'title': 'Market News 1',
                        'description': 'Description 1',
                        'publishedAt': '2024-01-01T00:00:00Z',
                        'source': {'name': 'Test Source'}
                    }
                ]
            }
            mock_response.status_code = 200
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

            result = await news_ingestion.fetch_news_api_data()

            assert len(result) == 1
            assert result[0]['title'] == 'Market News 1'

    def test_analyze_sentiment(self, news_ingestion):
        """Test sentiment analysis"""
        # Test positive sentiment
        positive_text = "Apple stock soars to new heights with record profits"
        sentiment = news_ingestion.analyze_sentiment(positive_text)

        assert sentiment in ['positive', 'negative', 'neutral']
        assert isinstance(sentiment, str)

        # Test negative sentiment
        negative_text = "Market crashes as tech stocks plummet"
        sentiment = news_ingestion.analyze_sentiment(negative_text)

        assert sentiment in ['positive', 'negative', 'neutral']
        assert isinstance(sentiment, str)


class TestPortfolioDataIngestion:
    """Test portfolio data ingestion functionality"""

    @pytest.fixture
    def portfolio_ingestion(self):
        return PortfolioDataIngestion()

    def test_load_portfolio_data(self, portfolio_ingestion):
        """Test portfolio data loading"""
        # Mock portfolio data
        portfolio_data = {
            'holdings': [
                {
                    'symbol': 'AAPL',
                    'shares': 100,
                    'avg_cost': 150.00
                },
                {
                    'symbol': 'GOOGL',
                    'shares': 50,
                    'avg_cost': 2800.00
                }
            ]
        }

        with patch('ingestion.portfolio_stream.json.load') as mock_load:
            mock_load.return_value = portfolio_data

            result = portfolio_ingestion.load_portfolio_data()

            assert result is not None
            assert len(result['holdings']) == 2
            assert result['holdings'][0]['symbol'] == 'AAPL'

    def test_calculate_portfolio_metrics(self, portfolio_ingestion):
        """Test portfolio metrics calculation"""
        portfolio_data = {
            'holdings': [
                {
                    'symbol': 'AAPL',
                    'shares': 100,
                    'avg_cost': 150.00
                }
            ]
        }

        # Mock current prices
        current_prices = {'AAPL': 160.00}

        metrics = portfolio_ingestion.calculate_portfolio_metrics(portfolio_data, current_prices)

        assert 'total_value' in metrics
        assert 'total_cost' in metrics
        assert 'total_pnl' in metrics
        assert 'total_return' in metrics
        assert metrics['total_value'] == 16000.00  # 100 * 160

    def test_sector_allocation(self, portfolio_ingestion):
        """Test sector allocation calculation"""
        portfolio_data = {
            'holdings': [
                {'symbol': 'AAPL', 'shares': 100, 'avg_cost': 150.00},
                {'symbol': 'MSFT', 'shares': 50, 'avg_cost': 300.00}
            ]
        }

        # Mock sector data
        sector_data = {
            'AAPL': 'Technology',
            'MSFT': 'Technology'
        }

        allocation = portfolio_ingestion.calculate_sector_allocation(portfolio_data, sector_data)

        assert 'Technology' in allocation
        assert allocation['Technology'] > 0
        assert isinstance(allocation['Technology'], float)


class TestDataIngestionIntegration:
    """Integration tests for data ingestion"""

    @pytest.mark.asyncio
    async def test_full_stock_data_pipeline(self):
        """Test complete stock data ingestion pipeline"""
        stock_ingestion = StockDataIngestion()

        # Mock both data sources
        with patch.object(stock_ingestion, 'fetch_yahoo_finance_data') as mock_yahoo, \
             patch.object(stock_ingestion, 'fetch_rapidapi_data') as mock_rapidapi:

            mock_yahoo.return_value = {
                'symbol': 'AAPL',
                'price': '150.00',
                'change': '2.50'
            }
            mock_rapidapi.return_value = {
                'symbol': 'AAPL',
                'price': '150.00',
                'change': '2.50'
            }

            result = await stock_ingestion.get_stock_data('AAPL')

            assert result is not None
            assert result['symbol'] == 'AAPL'
            assert 'price' in result
            assert 'change' in result

    @pytest.mark.asyncio
    async def test_full_news_data_pipeline(self):
        """Test complete news data ingestion pipeline"""
        news_ingestion = NewsDataIngestion()

        # Mock both data sources
        with patch.object(news_ingestion, 'fetch_rss_news') as mock_rss, \
             patch.object(news_ingestion, 'fetch_news_api_data') as mock_api:

            mock_rss.return_value = [
                {
                    'title': 'Test News 1',
                    'summary': 'Summary 1',
                    'published': datetime.now()
                }
            ]
            mock_api.return_value = [
                {
                    'title': 'Test News 2',
                    'description': 'Description 2',
                    'publishedAt': datetime.now().isoformat()
                }
            ]

            result = await news_ingestion.get_news_data()

            assert len(result) >= 1
            assert 'title' in result[0]
            assert 'sentiment' in result[0]

    def test_error_handling(self):
        """Test error handling in data ingestion"""
        stock_ingestion = StockDataIngestion()

        # Test with invalid symbol
        result = asyncio.run(stock_ingestion.get_stock_data('INVALID_SYMBOL'))

        # Should handle errors gracefully
        assert result is not None
        assert 'error' in result or 'symbol' in result