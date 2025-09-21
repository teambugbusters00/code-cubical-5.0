"""
Enhanced Finance AI Assistant Backend API
Built with FastAPI, integrates with multiple data sources for comprehensive real-time financial data
"""

from fastapi import FastAPI, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import asyncio
import json
from contextlib import asynccontextmanager
import httpx
# Import with error handling for optional dependencies
try:
    from alpha_vantage.timeseries import TimeSeries
    from alpha_vantage.fundamentaldata import FundamentalData
    ALPHA_VANTAGE_AVAILABLE = True
except ImportError:
    ALPHA_VANTAGE_AVAILABLE = False
    print("Warning: Alpha Vantage not available - some features will be limited")

try:
    import redis
    import pickle
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Warning: Redis not available - using in-memory cache")

try:
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: Scikit-learn not available - AI predictions will be limited")

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("Warning: TextBlob not available - sentiment analysis will be limited")

import os
from dotenv import load_dotenv
import warnings
import requests
from datetime import datetime, timedelta
import re
warnings.filterwarnings('ignore')

# Load environment variables
load_dotenv()

# Enhanced Data Source Management
class DataSourceManager:
    def __init__(self):
        self.sources = {
            'yfinance': YFinanceSource(),
            'alpha_vantage': AlphaVantageSource(),
            'rapidapi': RapidAPISource(),
            'fallback': FallbackSource()
        }
        self.cache = DataCache()

    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get stock quote with fallback mechanism"""
        for source_name, source in self.sources.items():
            try:
                # Use different method names for different sources
                if source_name == 'rapidapi':
                    data = await source.get_quote_rapidapi(symbol)
                else:
                    data = await source.get_quote(symbol)

                if data:
                    # Cache the successful result
                    await self.cache.set(f"quote_{symbol}", data, ttl=300)  # 5 minutes
                    return data
            except Exception as e:
                logger.warning(f"Data source {source_name} failed for {symbol}: {e}")
                continue

        # Try cache as last resort
        cached_data = await self.cache.get(f"quote_{symbol}")
        if cached_data:
            return cached_data

        # Return fallback data instead of raising exception
        logger.warning(f"All data sources failed for {symbol}, returning fallback data")
        return {
            'symbol': symbol,
            'current_price': 0.0,
            'previous_close': 0.0,
            'day_high': 0.0,
            'day_low': 0.0,
            'volume': 0,
            'market_cap': None,
            'pe_ratio': None,
            'dividend_yield': None,
            'fifty_two_week_high': None,
            'fifty_two_week_low': None,
            'source': 'fallback'
        }

    async def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Get historical data with fallback mechanism"""
        cache_key = f"history_{symbol}_{period}_{interval}"

        # Try cache first
        cached_data = await self.cache.get(cache_key)
        if cached_data is not None:
            return cached_data

        for source_name, source in self.sources.items():
            try:
                # Use different method names for different sources
                if source_name == 'rapidapi':
                    data = await source.get_historical_data_rapidapi(symbol, period, interval)
                else:
                    data = await source.get_historical_data(symbol, period, interval)

                if not data.empty:
                    await self.cache.set(cache_key, data, ttl=3600)  # 1 hour
                    return data
            except Exception as e:
                logger.warning(f"Data source {source_name} failed for {symbol} history: {e}")
                continue

        # Return empty DataFrame instead of raising exception
        logger.warning(f"All data sources failed for {symbol} historical data, returning empty DataFrame")
        return pd.DataFrame()

# Individual Data Sources
class YFinanceSource:
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if data.empty:
                return None

            latest = data.iloc[-1]
            info = ticker.info

            return {
                'symbol': symbol,
                'current_price': round(latest['Close'], 2),
                'previous_close': round(latest['Close'] if len(data) < 2 else data.iloc[-2]['Close'], 2),
                'day_high': round(latest['High'], 2),
                'day_low': round(latest['Low'], 2),
                'volume': int(latest['Volume']),
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'dividend_yield': info.get('dividendYield'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
                'source': 'yfinance'
            }
        except Exception as e:
            logger.error(f"YFinance error for {symbol}: {e}")
            return None

    async def get_historical_data(self, symbol: str, period: str, interval: str) -> pd.DataFrame:
        try:
            ticker = yf.Ticker(symbol)
            return ticker.history(period=period, interval=interval)
        except Exception as e:
            logger.error(f"YFinance history error for {symbol}: {e}")
            return pd.DataFrame()

class AlphaVantageSource:
    def __init__(self):
        self.api_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')
        self.ts = None
        self.fd = None

        if self.api_key:
            try:
                if ALPHA_VANTAGE_AVAILABLE:
                    self.ts = TimeSeries(key=self.api_key, output_format='pandas')
                    self.fd = FundamentalData(key=self.api_key, output_format='pandas')
                    logger.info("Alpha Vantage initialized successfully")
                else:
                    logger.warning("Alpha Vantage package not available")
            except Exception as e:
                logger.warning(f"Failed to initialize Alpha Vantage: {e}")

    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock quote from Alpha Vantage"""
        if not self.api_key or not self.ts:
            return None

        try:
            # Get daily data
            data, meta_data = self.ts.get_quote_endpoint(symbol)
            if data is None or data.empty:
                return None

            latest = data.iloc[0]  # Most recent data point

            return {
                'symbol': symbol,
                'current_price': round(float(latest['4. close']), 2),
                'previous_close': round(float(latest['8. previous close']), 2),
                'day_high': round(float(latest['3. high']), 2),
                'day_low': round(float(latest['4. close']), 2),  # Using close as fallback
                'volume': int(latest['6. volume']),
                'source': 'alpha_vantage'
            }
        except Exception as e:
            logger.error(f"Alpha Vantage error for {symbol}: {e}")
            return None

    async def get_historical_data(self, symbol: str, period: str, interval: str) -> pd.DataFrame:
        """Get historical data from Alpha Vantage"""
        if not self.api_key or not self.ts:
            return pd.DataFrame()

        try:
            # Map period to Alpha Vantage parameters
            period_map = {
                '1d': 'TIME_SERIES_DAILY',
                '1mo': 'TIME_SERIES_DAILY',
                '3mo': 'TIME_SERIES_DAILY',
                '6mo': 'TIME_SERIES_DAILY',
                '1y': 'TIME_SERIES_DAILY',
                '2y': 'TIME_SERIES_DAILY',
                '5y': 'TIME_SERIES_DAILY'
            }

            function = period_map.get(period, 'TIME_SERIES_DAILY')

            if function == 'TIME_SERIES_DAILY':
                data, meta_data = self.ts.get_daily(symbol, outputsize='full')
                return data
            else:
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"Alpha Vantage history error for {symbol}: {e}")
            return pd.DataFrame()

class RapidAPISource:
    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY', '')
        self.base_url = 'https://yahoo-finance-real-time1.p.rapidapi.com'

    async def get_quote_rapidapi(self, symbol: str) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            return None

        try:
            headers = {
                'x-rapidapi-key': self.api_key,
                'x-rapidapi-host': 'yahoo-finance-real-time1.p.rapidapi.com'
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/stock/get-summary?symbol={symbol}&lang=en-US&region=US",
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

            if 'data' not in data:
                return None

            stock_data = data['data']
            return {
                'symbol': symbol,
                'current_price': stock_data.get('currentPrice', 0),
                'previous_close': stock_data.get('previousClose', 0),
                'day_high': stock_data.get('dayHigh', 0),
                'day_low': stock_data.get('dayLow', 0),
                'volume': stock_data.get('volume', 0),
                'market_cap': stock_data.get('marketCap', 0),
                'pe_ratio': stock_data.get('trailingPE', 0),
                'dividend_yield': stock_data.get('dividendYield', 0),
                'fifty_two_week_high': stock_data.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': stock_data.get('fiftyTwoWeekLow', 0),
                'source': 'rapidapi'
            }
        except Exception as e:
            logger.error(f"RapidAPI error for {symbol}: {e}")
            return None

    async def get_historical_data_rapidapi(self, symbol: str, period: str, interval: str) -> pd.DataFrame:
        if not self.api_key:
            return pd.DataFrame()

        try:
            headers = {
                'x-rapidapi-key': self.api_key,
                'x-rapidapi-host': 'yahoo-finance-real-time1.p.rapidapi.com'
            }

            # Map period to RapidAPI parameters
            period_map = {
                '1d': '1d',
                '5d': '5d',
                '1mo': '1mo',
                '3mo': '3mo',
                '6mo': '6mo',
                '1y': '1y',
                '2y': '2y',
                '5y': '5y'
            }

            range_param = period_map.get(period, '1y')

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/stock/get-historical-data?symbol={symbol}&period1=1640995200&period2=1704067200&interval={interval}&lang=en-US&region=US",
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()

            if 'data' not in data:
                return pd.DataFrame()

            # Convert to DataFrame
            historical_data = []
            for item in data['data']:
                historical_data.append({
                    'Date': pd.to_datetime(item['date'], unit='s'),
                    'Open': item.get('open', 0),
                    'High': item.get('high', 0),
                    'Low': item.get('low', 0),
                    'Close': item.get('close', 0),
                    'Volume': item.get('volume', 0)
                })

            return pd.DataFrame(historical_data)
        except Exception as e:
            logger.error(f"RapidAPI history error for {symbol}: {e}")
            return pd.DataFrame()


class FallbackSource:
    async def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        # Return basic structure with N/A values
        return {
            'symbol': symbol,
            'current_price': 0.0,
            'previous_close': 0.0,
            'day_high': 0.0,
            'day_low': 0.0,
            'volume': 0,
            'source': 'fallback'
        }

    async def get_historical_data(self, symbol: str, period: str, interval: str) -> pd.DataFrame:
        return pd.DataFrame()

# Data Caching
class DataCache:
    def __init__(self):
        self.redis_client = None
        self.memory_cache = {}

        try:
            if REDIS_AVAILABLE:
                redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
                self.redis_client = redis.from_url(redis_url)
                logger.info("Redis cache enabled")
            else:
                logger.info("Redis not available, using in-memory cache")
        except Exception as e:
            logger.warning(f"Redis initialization failed: {e}")
            logger.info("Using in-memory cache")

    async def get(self, key: str) -> Optional[Any]:
        # Try Redis first if available
        if self.redis_client:
            try:
                data = self.redis_client.get(key)
                if data:
                    try:
                        return pickle.loads(data)
                    except Exception as e:
                        logger.warning(f"Cache pickle load error: {e}")
            except Exception as e:
                logger.warning(f"Cache get error: {e}")

        # Fallback to memory cache
        return self.memory_cache.get(key)

    async def set(self, key: str, value: Any, ttl: int = 3600):
        # Store in memory cache
        self.memory_cache[key] = value

        # Store in Redis if available
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, pickle.dumps(value))
            except Exception as e:
                logger.warning(f"Cache set error: {e}")

# For development without MongoDB - using dummy classes
class StockData:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def insert(self):
        pass

class NewsArticle:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def insert(self):
        pass

class Portfolio:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def insert(self):
        pass

class User:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def insert(self):
        pass

class ChatMessage:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def insert(self):
        pass

class TechnicalAnalysis:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def insert(self):
        pass

async def init_database():
    pass

async def close_database():
    pass

# Configuration
class Settings:
    def __init__(self):
        self.enable_mongodb = os.getenv('ENABLE_MONGODB', 'false').lower() == 'true'
        self.enable_mongodb_persistence = os.getenv('ENABLE_MONGODB_PERSISTENCE', 'false').lower() == 'true'
        self.enable_redis = os.getenv('ENABLE_REDIS', 'true').lower() == 'true'
        self.enable_real_time = os.getenv('ENABLE_REAL_TIME', 'true').lower() == 'true'
        self.data_refresh_interval = int(os.getenv('DATA_REFRESH_INTERVAL', '30'))  # seconds
        self.max_retries = int(os.getenv('MAX_RETRIES', '3'))

settings = Settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize data source manager
data_manager = DataSourceManager()

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Finance AI Assistant Backend")

    # Initialize database connection
    if settings.enable_mongodb:
        try:
            await init_database()
            logger.info("Database connection initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    yield

    # Shutdown
    logger.info("Shutting down Finance AI Assistant Backend")

    # Close database connection
    if settings.enable_mongodb:
        try:
            await close_database()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")

# Create FastAPI app
app = FastAPI(
    title="Finance AI Assistant API",
    description="A comprehensive financial data API with Yahoo Finance integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket CORS headers
@app.middleware("http")
async def websocket_cors_middleware(request, call_next):
    """Add CORS headers for WebSocket connections"""
    response = await call_next(request)

    # Add CORS headers for WebSocket upgrade requests
    if request.headers.get("upgrade") == "websocket":
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "*"

    return response

# Pydantic models
class StockInfo(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    name: str = Field(..., description="Company name")
    sector: Optional[str] = Field(None, description="Company sector")
    industry: Optional[str] = Field(None, description="Company industry")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    pe_ratio: Optional[float] = Field(None, description="Price to earnings ratio")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield")

class StockPrice(BaseModel):
    symbol: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: float

class MarketData(BaseModel):
    symbol: str
    current_price: float
    previous_close: float
    day_high: float
    day_low: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None

class HistoricalDataRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    period: str = Field("1y", description="Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)")
    interval: str = Field("1d", description="Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query for stocks")
    limit: int = Field(10, description="Maximum number of results")

# Dependency for Yahoo Finance ticker
def get_yfinance_ticker(symbol: str):
    """Get Yahoo Finance ticker object"""
    try:
        ticker = yf.Ticker(symbol)
        return ticker
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching ticker for {symbol}: {str(e)}")

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Finance AI Assistant API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/stocks/{symbol}/predict-test")
async def predict_stock_price_test(symbol: str, days: int = 7):
    """
    Simple test prediction endpoint without ML
    """
    try:
        logger.info(f"Test prediction for {symbol} with {days} days")

        # Simple mock prediction
        predictions = []
        for i in range(days):
            predictions.append({
                "date": (datetime.now() + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                "predicted_price": 250.0 + (i * 2.5),  # Simple mock prediction
                "confidence": 0.75
            })

        return {
            "symbol": symbol,
            "predictions": predictions,
            "model": "Test Model",
            "training_data_points": 100,
            "last_actual_price": 245.5,
            "prediction_date": datetime.now().isoformat(),
            "note": "This is a test endpoint without machine learning"
        }

    except Exception as e:
        logger.error(f"Error in test prediction for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error in test prediction: {str(e)}")

@app.get("/api/stocks/search", response_model=List[Dict[str, Any]])
async def search_stocks(request: SearchRequest = Depends()):
    """
    Search for stocks by company name or symbol
    """
    try:
        # This is a simplified search - in production, you'd use a proper financial data API
        # For now, we'll return some popular stocks that match the query
        popular_stocks = [
            {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Technology"},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services"},
            {"symbol": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare"},
            {"symbol": "V", "name": "Visa Inc.", "sector": "Financial Services"},
            {"symbol": "WMT", "name": "Walmart Inc.", "sector": "Consumer Staples"},
        ]

        # Filter based on query
        filtered_stocks = [
            stock for stock in popular_stocks
            if request.query.lower() in stock["name"].lower() or
               request.query.lower() in stock["symbol"].lower()
        ]

        return filtered_stocks[:request.limit]

    except Exception as e:
        logger.error(f"Error searching stocks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching stocks: {str(e)}")

@app.get("/api/stocks/{symbol}/info", response_model=StockInfo)
async def get_stock_info(symbol: str):
    """
    Get basic information about a stock
    """
    try:
        ticker = get_yfinance_ticker(symbol)

        # Get basic info
        info = ticker.info

        stock_info = StockInfo(
            symbol=symbol,
            name=info.get('longName', symbol),
            sector=info.get('sector'),
            industry=info.get('industry'),
            market_cap=info.get('marketCap'),
            pe_ratio=info.get('trailingPE'),
            dividend_yield=info.get('dividendYield')
        )

        return stock_info

    except Exception as e:
        logger.error(f"Error fetching stock info for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching stock info: {str(e)}")

@app.get("/api/stocks/{symbol}/quote", response_model=MarketData)
async def get_stock_quote(symbol: str):
    """
    Get current market data for a stock with enhanced data sources
    """
    try:
        # Use the data source manager for robust data fetching
        quote_data = await data_manager.get_stock_quote(symbol)

        if not quote_data:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")

        market_data = MarketData(
            symbol=symbol,
            current_price=quote_data['current_price'],
            previous_close=quote_data['previous_close'],
            day_high=quote_data['day_high'],
            day_low=quote_data['day_low'],
            volume=quote_data['volume'],
            market_cap=quote_data.get('market_cap'),
            pe_ratio=quote_data.get('pe_ratio'),
            dividend_yield=quote_data.get('dividend_yield'),
            fifty_two_week_high=quote_data.get('fifty_two_week_high'),
            fifty_two_week_low=quote_data.get('fifty_two_week_low')
        )

        # Save to MongoDB if enabled
        if settings.enable_mongodb and settings.enable_mongodb_persistence:
            try:
                stock_data = StockData(
                    symbol=symbol,
                    company_name=quote_data.get('company_name', symbol),
                    price=market_data.current_price,
                    change=market_data.current_price - market_data.previous_close,
                    change_percent=((market_data.current_price / market_data.previous_close - 1) * 100) if market_data.previous_close > 0 else 0,
                    volume=market_data.volume,
                    market_cap=market_data.market_cap,
                    pe_ratio=market_data.pe_ratio,
                    dividend_yield=market_data.dividend_yield,
                    high_52_week=market_data.fifty_two_week_high,
                    low_52_week=market_data.fifty_two_week_low,
                    data_source=quote_data.get('source', 'unknown')
                )
                await stock_data.insert()
                logger.info(f"Saved stock data for {symbol} to MongoDB")
            except Exception as db_error:
                logger.warning(f"Failed to save to MongoDB: {db_error}")

        return market_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock quote for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching stock quote: {str(e)}")

@app.get("/api/stocks/{symbol}/history", response_model=List[StockPrice])
async def get_stock_history(request: HistoricalDataRequest = Depends()):
    """
    Get historical price data for a stock
    """
    try:
        ticker = get_yfinance_ticker(request.symbol)

        # Get historical data
        data = ticker.history(period=request.period, interval=request.interval)

        if data.empty:
            raise HTTPException(status_code=404, detail=f"No historical data found for symbol {request.symbol}")

        # Convert to list of StockPrice objects
        stock_prices = []
        for timestamp, row in data.iterrows():
            stock_price = StockPrice(
                symbol=request.symbol,
                timestamp=timestamp.to_pydatetime(),
                open=round(row['Open'], 2),
                high=round(row['High'], 2),
                low=round(row['Low'], 2),
                close=round(row['Close'], 2),
                volume=int(row['Volume']),
                adj_close=round(row['Close'], 2)  # Simplified for this example
            )
            stock_prices.append(stock_price)

        return stock_prices

    except Exception as e:
        logger.error(f"Error fetching historical data for {request.symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")

@app.get("/api/stocks/{symbol}/analysis")
async def get_stock_analysis(symbol: str):
    """
    Get basic technical analysis for a stock
    """
    try:
        ticker = get_yfinance_ticker(symbol)

        # Get historical data for analysis (last 200 days)
        data = ticker.history(period="1y")

        if data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")

        # Calculate basic metrics
        current_price = data['Close'].iloc[-1]
        sma_20 = data['Close'].tail(20).mean()
        sma_50 = data['Close'].tail(50).mean()
        rsi = calculate_rsi(data['Close'])

        # Determine trend
        trend = "neutral"
        if current_price > sma_20 > sma_50:
            trend = "bullish"
        elif current_price < sma_20 < sma_50:
            trend = "bearish"

        analysis = {
            "symbol": symbol,
            "current_price": round(current_price, 2),
            "sma_20": round(sma_20, 2),
            "sma_50": round(sma_50, 2),
            "rsi": round(rsi, 2),
            "trend": trend,
            "analysis_date": datetime.now().isoformat()
        }

        return analysis

    except Exception as e:
        logger.error(f"Error performing analysis for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error performing analysis: {str(e)}")

def calculate_rsi(prices: pd.Series, period: int = 14) -> float:
    """
    Calculate Relative Strength Index (RSI)
    """
    try:
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean().tail(1)
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean().tail(1)

        avg_gain = gain.mean()
        avg_loss = loss.mean()

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi
    except:
        return 50.0  # Return neutral RSI if calculation fails

@app.get("/api/market/indices")
async def get_market_indices():
    """
    Get major market indices data
    """
    try:
        indices = ["^GSPC", "^IXIC", "^DJI", "^RUT"]  # S&P 500, NASDAQ, Dow Jones, Russell 2000
        index_data = {}

        for symbol in indices:
            try:
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="1d")
                if not data.empty:
                    latest = data.iloc[-1]
                    info = ticker.info

                    index_data[symbol] = {
                        "name": info.get('shortName', symbol),
                        "current_price": round(latest['Close'], 2),
                        "change": round(latest['Close'] - (latest['Close'] if len(data) < 2 else data.iloc[-2]['Close']), 2),
                        "change_percent": round(((latest['Close'] / (latest['Close'] if len(data) < 2 else data.iloc[-2]['Close']) - 1) * 100), 2)
                    }
            except Exception as e:
                logger.warning(f"Error fetching data for index {symbol}: {str(e)}")
                continue

        return index_data

    except Exception as e:
        logger.error(f"Error fetching market indices: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching market indices: {str(e)}")

# MongoDB-specific endpoints (disabled for development)
@app.get("/api/stocks/{symbol}/history-db")
async def get_stock_history_from_db(symbol: str, limit: int = 100):
    """
    Get stock history from MongoDB (disabled for development)
    """
    raise HTTPException(status_code=503, detail="MongoDB functionality disabled for development")

@app.post("/api/portfolios")
async def create_portfolio(portfolio_data: Dict[str, Any]):
    """
    Create a new portfolio (disabled for development)
    """
    raise HTTPException(status_code=503, detail="MongoDB functionality disabled for development")

@app.get("/api/portfolios/{user_id}")
async def get_user_portfolios(user_id: str):
    """
    Get portfolios for a user (disabled for development)
    """
    raise HTTPException(status_code=503, detail="MongoDB functionality disabled for development")

# WebSocket connection manager for real-time data
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            # Don't disconnect immediately, just log the error
            # The connection might still be usable

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting WebSocket message: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)

    async def send_personal_message_safe(self, message: str, websocket: WebSocket):
        """Send message only if connection is still active"""
        try:
            # Check if connection is still in active connections
            if websocket in self.active_connections:
                await websocket.send_text(message)
            else:
                logger.warning("Attempted to send message to inactive WebSocket connection")
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            # Only disconnect if it's a real connection error
            if "Cannot call" in str(e):
                self.disconnect(websocket)

manager = ConnectionManager()

@app.websocket("/ws/stocks/{symbol}")
async def websocket_endpoint(websocket: WebSocket, symbol: str):
    """
    WebSocket endpoint for real-time stock data streaming
    """
    try:
        await manager.connect(websocket)
        logger.info(f"WebSocket connected for {symbol}")

        while True:
            # Get real-time data
            try:
                quote_data = await data_manager.get_stock_quote(symbol)
                if quote_data:
                    # Send data to client using safe method
                    await manager.send_personal_message_safe(json.dumps({
                        "type": "stock_update",
                        "symbol": symbol,
                        "data": quote_data,
                        "timestamp": datetime.now().isoformat()
                    }), websocket)

                # Wait before next update
                await asyncio.sleep(settings.data_refresh_interval)

            except Exception as e:
                logger.error(f"Error in WebSocket for {symbol}: {e}")
                try:
                    await manager.send_personal_message_safe(json.dumps({
                        "type": "error",
                        "message": f"Error fetching data for {symbol}: {str(e)}"
                    }), websocket)
                except:
                    pass
                await asyncio.sleep(5)  # Wait longer on error

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected for {symbol}")
    except Exception as e:
        logger.error(f"Unexpected error in WebSocket for {symbol}: {e}")
        manager.disconnect(websocket)

@app.websocket("/ws/market")
async def market_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time market indices streaming
    """
    try:
        await manager.connect(websocket)
        logger.info("Market WebSocket connected")

        while True:
            # Get market indices data
            try:
                indices_data = await get_market_indices_data()
                if indices_data:
                    # Send data to client using safe method
                    await manager.send_personal_message_safe(json.dumps({
                        "type": "market_update",
                        "data": indices_data,
                        "timestamp": datetime.now().isoformat()
                    }), websocket)

                # Wait before next update
                await asyncio.sleep(settings.data_refresh_interval)

            except Exception as e:
                logger.error(f"Error in market WebSocket: {e}")
                try:
                    await manager.send_personal_message_safe(json.dumps({
                        "type": "error",
                        "message": f"Error fetching market data: {str(e)}"
                    }), websocket)
                except:
                    pass
                await asyncio.sleep(5)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Market WebSocket disconnected")
    except Exception as e:
        logger.error(f"Unexpected error in market WebSocket: {e}")
        manager.disconnect(websocket)

async def get_market_indices_data():
    """Get comprehensive market indices data"""
    try:
        indices = ["^GSPC", "^IXIC", "^DJI", "^RUT"]  # S&P 500, NASDAQ, Dow Jones, Russell 2000
        index_data = {}

        for symbol in indices:
            try:
                # Use fallback data for market indices if API fails
                try:
                    quote_data = await data_manager.get_stock_quote(symbol)
                    if quote_data:
                        index_data[symbol] = {
                            "name": get_index_name(symbol),
                            "current_price": quote_data['current_price'],
                            "change": quote_data['current_price'] - quote_data['previous_close'],
                            "change_percent": ((quote_data['current_price'] / quote_data['previous_close'] - 1) * 100) if quote_data['previous_close'] > 0 else 0,
                            "source": quote_data.get('source', 'unknown')
                        }
                except Exception as api_error:
                    logger.warning(f"API failed for {symbol}, using fallback data: {api_error}")
                    # Fallback data for major indices
                    fallback_data = {
                        "^GSPC": {"name": "S&P 500", "price": 4500.0, "change": 25.0},
                        "^IXIC": {"name": "NASDAQ Composite", "price": 14000.0, "change": 100.0},
                        "^DJI": {"name": "Dow Jones Industrial Average", "price": 35000.0, "change": 150.0},
                        "^RUT": {"name": "Russell 2000", "price": 2000.0, "change": -10.0}
                    }

                    if symbol in fallback_data:
                        data = fallback_data[symbol]
                        index_data[symbol] = {
                            "name": data["name"],
                            "current_price": data["price"],
                            "change": data["change"],
                            "change_percent": (data["change"] / (data["price"] - data["change"])) * 100 if data["price"] - data["change"] > 0 else 0,
                            "source": "fallback"
                        }
            except Exception as e:
                logger.warning(f"Error fetching data for index {symbol}: {str(e)}")
                continue

        return index_data

    except Exception as e:
        logger.error(f"Error fetching market indices: {str(e)}")
        return {}

def get_index_name(symbol: str) -> str:
    """Get human-readable name for index symbol"""
    names = {
        "^GSPC": "S&P 500",
        "^IXIC": "NASDAQ Composite",
        "^DJI": "Dow Jones Industrial Average",
        "^RUT": "Russell 2000"
    }
    return names.get(symbol, symbol)

# Enhanced prediction endpoint
@app.get("/api/stocks/{symbol}/predict")
async def predict_stock_price(symbol: str, days: int = Query(7, description="Number of days to predict")):
    """
    Predict future stock prices using machine learning
    """
    try:
        logger.info(f"Starting prediction for {symbol} with {days} days")

        # Get historical data for training
        historical_data = await data_manager.get_historical_data(symbol, period="1y", interval="1d")

        if historical_data.empty or len(historical_data) < 30:
            logger.warning(f"Insufficient historical data for {symbol}: {len(historical_data)} rows")
            raise HTTPException(status_code=400, detail="Insufficient historical data for prediction")

        # Prepare data for prediction
        df = historical_data.reset_index()
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')

        # Feature engineering
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['Volatility'] = df['Close'].rolling(window=10).std()
        df['Price_Change'] = df['Close'].pct_change()

        # Remove NaN values
        df = df.dropna()

        if len(df) < 30:
            logger.warning(f"Insufficient data after processing for {symbol}: {len(df)} rows")
            raise HTTPException(status_code=400, detail="Insufficient data after processing")

        # Check if ML libraries are available
        if not SKLEARN_AVAILABLE:
            # Fallback to simple trend-based prediction
            logger.info(f"ML libraries not available, using trend-based prediction for {symbol}")

            # Simple trend-based prediction
            last_price = df['Close'].iloc[-1]
            trend = df['Close'].tail(10).mean() - df['Close'].tail(20).mean()

            predictions = []
            current_price = last_price

            for i in range(days):
                # Simple linear trend prediction
                if trend > 0:
                    # Upward trend
                    change_percent = 0.02  # 2% daily growth
                elif trend < 0:
                    # Downward trend
                    change_percent = -0.02  # 2% daily decline
                else:
                    # Sideways trend
                    change_percent = 0.005  # 0.5% daily movement

                predicted_price = current_price * (1 + change_percent)
                predictions.append({
                    "date": (df['Date'].iloc[-1] + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                    "predicted_price": round(predicted_price, 2),
                    "confidence": 0.65  # Lower confidence for trend-based prediction
                })
                current_price = predicted_price

            result = {
                "symbol": symbol,
                "predictions": predictions,
                "model": "Trend-Based Analysis",
                "training_data_points": len(df),
                "last_actual_price": round(last_price, 2),
                "prediction_date": datetime.now().isoformat(),
                "note": "Using trend-based prediction (ML libraries not available)"
            }

        else:
            # Use machine learning prediction
            logger.info(f"Using ML prediction for {symbol}")

            # Prepare features and target
            features = ['SMA_5', 'SMA_20', 'Volatility', 'Price_Change', 'Volume']
            X = df[features].values
            y = df['Close'].values

            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Train model
            model = LinearRegression()
            model.fit(X_scaled, y)

            # Make predictions
            last_data = df[features].iloc[-1].values.reshape(1, -1)
            last_data_scaled = scaler.transform(last_data)

            predictions = []
            current_data = last_data_scaled.copy()

            for i in range(days):
                pred_price = model.predict(current_data)[0]

                # Create prediction record
                predictions.append({
                    "date": (df['Date'].iloc[-1] + timedelta(days=i+1)).strftime('%Y-%m-%d'),
                    "predicted_price": round(pred_price, 2),
                    "confidence": 0.85  # Higher confidence for ML prediction
                })

                # Update features for next prediction (simplified)
                current_data[0][0] = pred_price  # Update SMA_5 with prediction
                current_data[0][1] = df['SMA_20'].iloc[-1]  # Keep SMA_20
                current_data[0][2] = df['Volatility'].iloc[-1]  # Keep volatility
                current_data[0][3] = (pred_price - df['Close'].iloc[-1]) / df['Close'].iloc[-1]  # Price change

            result = {
                "symbol": symbol,
                "predictions": predictions,
                "model": "Linear Regression",
                "training_data_points": len(df),
                "last_actual_price": round(df['Close'].iloc[-1], 2),
                "prediction_date": datetime.now().isoformat()
            }

        logger.info(f"Successfully generated predictions for {symbol}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error predicting price for {symbol}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error predicting price: {str(e)}")

# Enhanced technical analysis with more indicators
@app.get("/api/stocks/{symbol}/analysis/detailed")
async def get_detailed_technical_analysis(symbol: str):
    """
    Get comprehensive technical analysis with multiple indicators
    """
    try:
        # Get historical data
        data = await data_manager.get_historical_data(symbol, period="1y", interval="1d")

        if data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")

        df = data.reset_index()
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date')

        # Calculate comprehensive indicators
        analysis = {
            "symbol": symbol,
            "analysis_date": datetime.now().isoformat(),
            "indicators": {}
        }

        # Moving averages
        analysis["indicators"]["sma_20"] = round(df['Close'].tail(20).mean(), 2)
        analysis["indicators"]["sma_50"] = round(df['Close'].tail(50).mean(), 2)
        analysis["indicators"]["sma_200"] = round(df['Close'].tail(200).mean(), 2) if len(df) >= 200 else None

        # RSI
        analysis["indicators"]["rsi"] = round(calculate_rsi(df['Close']), 2)

        # MACD
        macd_data = calculate_macd(df['Close'])
        analysis["indicators"]["macd"] = macd_data["macd"]
        analysis["indicators"]["macd_signal"] = macd_data["signal"]
        analysis["indicators"]["macd_histogram"] = macd_data["histogram"]

        # Bollinger Bands
        bb_data = calculate_bollinger_bands(df['Close'])
        analysis["indicators"]["bb_upper"] = bb_data["upper"]
        analysis["indicators"]["bb_middle"] = bb_data["middle"]
        analysis["indicators"]["bb_lower"] = bb_data["lower"]
        analysis["indicators"]["bb_position"] = bb_data["position"]

        # Volume analysis
        analysis["indicators"]["volume_sma"] = round(df['Volume'].tail(20).mean(), 0)
        analysis["indicators"]["volume_ratio"] = round(df['Volume'].iloc[-1] / df['Volume'].tail(20).mean(), 2)

        # Trend analysis
        analysis["indicators"]["trend"] = determine_trend(df['Close'])

        # Support and resistance levels
        analysis["indicators"]["support_resistance"] = find_support_resistance(df['Close'])

        return analysis

    except Exception as e:
        logger.error(f"Error performing detailed analysis for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error performing analysis: {str(e)}")

def calculate_macd(prices: pd.Series, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9):
    """Calculate MACD indicator"""
    try:
        fast_ema = prices.ewm(span=fast_period, adjust=False).mean()
        slow_ema = prices.ewm(span=slow_period, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal = macd.ewm(span=signal_period, adjust=False).mean()
        histogram = macd - signal

        return {
            "macd": round(macd.iloc[-1], 4),
            "signal": round(signal.iloc[-1], 4),
            "histogram": round(histogram.iloc[-1], 4)
        }
    except:
        return {"macd": 0, "signal": 0, "histogram": 0}

def calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2):
    """Calculate Bollinger Bands"""
    try:
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)

        current_price = prices.iloc[-1]
        position = (current_price - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1]) if (upper.iloc[-1] - lower.iloc[-1]) > 0 else 0.5

        return {
            "upper": round(upper.iloc[-1], 2),
            "middle": round(sma.iloc[-1], 2),
            "lower": round(lower.iloc[-1], 2),
            "position": round(position, 2)
        }
    except:
        return {"upper": 0, "middle": 0, "lower": 0, "position": 0.5}

def determine_trend(prices: pd.Series) -> str:
    """Determine overall trend"""
    try:
        sma_20 = prices.tail(20).mean()
        sma_50 = prices.tail(50).mean()
        current_price = prices.iloc[-1]

        if current_price > sma_20 > sma_50:
            return "bullish"
        elif current_price < sma_20 < sma_50:
            return "bearish"
        else:
            return "neutral"
    except:
        return "neutral"

def find_support_resistance(prices: pd.Series, lookback: int = 20):
    """Find support and resistance levels"""
    try:
        recent_prices = prices.tail(lookback)
        high = recent_prices.max()
        low = recent_prices.min()

        return {
            "resistance": round(high, 2),
            "support": round(low, 2),
            "range": round(high - low, 2)
        }
    except:
        return {"resistance": 0, "support": 0, "range": 0}

# News and Sentiment Analysis
class NewsAnalyzer:
    def __init__(self):
        self.news_api_key = os.getenv('NEWS_API_KEY', '')
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY', '')

    async def get_company_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent news for a company"""
        try:
            # Use Alpha Vantage News API if available
            if self.alpha_vantage_key:
                return await self._get_alpha_vantage_news(symbol, limit)
            else:
                # Fallback to mock news data
                return self._get_mock_news(symbol, limit)
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return []

    async def _get_alpha_vantage_news(self, symbol: str, limit: int) -> List[Dict[str, Any]]:
        """Get news from Alpha Vantage"""
        try:
            url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={symbol}&apikey={self.alpha_vantage_key}&limit={limit}"
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
                        'sentiment': sentiment,
                        'source': 'Alpha Vantage'
                    })

            return news_items
        except Exception as e:
            logger.error(f"Alpha Vantage news error: {e}")
            return []

    def _get_mock_news(self, symbol: str, limit: int) -> List[Dict[str, Any]]:
        """Generate mock news data for development"""
        mock_news = [
            {
                'title': f"{symbol} Reports Strong Quarterly Earnings",
                'summary': f"{symbol} has exceeded market expectations with robust quarterly performance.",
                'url': f'https://example.com/news/{symbol}-earnings',
                'published_at': (datetime.now() - timedelta(hours=i)).isoformat(),
                'sentiment': 'positive',
                'source': 'Mock Data'
            } for i in range(min(limit, 5))
        ]

        # Add some neutral/negative news
        mock_news.extend([
            {
                'title': f"Market Analysis: {symbol} Trading Volume Update",
                'summary': f"Trading volume for {symbol} shows mixed signals in recent sessions.",
                'url': f'https://example.com/news/{symbol}-volume',
                'published_at': (datetime.now() - timedelta(hours=i+5)).isoformat(),
                'sentiment': 'neutral',
                'source': 'Mock Data'
            } for i in range(min(limit-5, 3))
        ])

        return mock_news

    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of text using TextBlob or simple keyword analysis"""
        try:
            if TEXTBLOB_AVAILABLE:
                try:
                    blob = TextBlob(text)
                    polarity = blob.sentiment.polarity

                    if polarity > 0.1:
                        return 'positive'
                    elif polarity < -0.1:
                        return 'negative'
                    else:
                        return 'neutral'
                except Exception as e:
                    logger.warning(f"TextBlob analysis failed: {e}")

            # Fallback to simple keyword-based analysis
            text_lower = text.lower()
            positive_words = ['good', 'great', 'excellent', 'profit', 'gain', 'up', 'rise', 'strong', 'bullish']
            negative_words = ['bad', 'terrible', 'loss', 'down', 'fall', 'weak', 'bearish', 'decline', 'drop']

            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            if positive_count > negative_count:
                return 'positive'
            elif negative_count > positive_count:
                return 'negative'
            else:
                return 'neutral'
        except:
            return 'neutral'

    async def get_sentiment_summary(self, symbol: str) -> Dict[str, Any]:
        """Get sentiment summary for a company"""
        try:
            news = await self.get_company_news(symbol, 20)

            if not news:
                return {
                    'symbol': symbol,
                    'overall_sentiment': 'neutral',
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0,
                    'total_articles': 0
                }

            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}

            for article in news:
                sentiment = article.get('sentiment', 'neutral')
                sentiment_counts[sentiment] += 1

            total = len(news)
            # Find the sentiment with highest count
            overall_sentiment = 'neutral'
            max_count = 0
            for sentiment, count in sentiment_counts.items():
                if count > max_count:
                    max_count = count
                    overall_sentiment = sentiment

            return {
                'symbol': symbol,
                'overall_sentiment': overall_sentiment,
                'sentiment_score': (sentiment_counts['positive'] - sentiment_counts['negative']) / total,
                'positive_count': sentiment_counts['positive'],
                'negative_count': sentiment_counts['negative'],
                'neutral_count': sentiment_counts['neutral'],
                'total_articles': total,
                'recent_articles': news[:5]  # Return 5 most recent articles
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment for {symbol}: {e}")
            return {
                'symbol': symbol,
                'overall_sentiment': 'neutral',
                'sentiment_score': 0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_articles': 0
            }

# Initialize news analyzer
news_analyzer = NewsAnalyzer()

# News and Sentiment Analysis Endpoints
@app.get("/api/stocks/{symbol}/news")
async def get_stock_news(symbol: str, limit: int = 10):
    """
    Get recent news articles for a stock with sentiment analysis
    """
    try:
        news = await news_analyzer.get_company_news(symbol, limit)
        return news
    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@app.get("/api/stocks/{symbol}/sentiment")
async def get_stock_sentiment(symbol: str):
    """
    Get sentiment analysis summary for a stock
    """
    try:
        sentiment_summary = await news_analyzer.get_sentiment_summary(symbol)
        return sentiment_summary
    except Exception as e:
        logger.error(f"Error analyzing sentiment for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")

@app.get("/api/market/news")
async def get_market_news(limit: int = 20):
    """
    Get general market news and sentiment
    """
    try:
        # Get news for major indices
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        all_news = []

        for symbol in symbols:
            try:
                news = await news_analyzer.get_company_news(symbol, 5)
                all_news.extend(news)
            except Exception as e:
                logger.warning(f"Error fetching news for {symbol}: {e}")
                continue

        # Sort by date and limit
        all_news.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        return all_news[:limit]
    except Exception as e:
        logger.error(f"Error fetching market news: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching market news: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Enhanced Finance AI Assistant Backend")
    logger.info(f"Real-time updates: {settings.enable_real_time}")
    logger.info(f"MongoDB enabled: {settings.enable_mongodb}")
    logger.info(f"Data refresh interval: {settings.data_refresh_interval}s")
    uvicorn.run(app, host="0.0.0.0", port=8000)