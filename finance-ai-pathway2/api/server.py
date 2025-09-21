"""
FastAPI Server for Finance AI Assistant
Provides REST API endpoints for financial data and RAG queries
"""

from fastapi import FastAPI, HTTPException, Depends, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
import asyncio
import json
from datetime import datetime
from contextlib import asynccontextmanager

# Import our modules
from ingestion.stock_stream import stock_ingestion
from ingestion.news_stream import news_ingestion
from ingestion.portfolio_stream import portfolio_ingestion
from rag.rag_pipeline import rag_pipeline
from rag.llm_config import llm_manager
from processing.indexing import search_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    logger.info("Starting Finance AI Assistant API")

    # Startup tasks
    try:
        # Initialize search engine with sample data
        await initialize_search_engine()
        logger.info("Search engine initialized")
    except Exception as e:
        logger.error(f"Error initializing search engine: {e}")

    yield

    # Shutdown tasks
    logger.info("Shutting down Finance AI Assistant API")

async def initialize_search_engine():
    """Initialize search engine with sample data"""
    try:
        # Load sample data
        import pandas as pd

        # Load stocks data
        try:
            stocks_df = pd.read_csv("data/stocks.csv")
            stock_data = stocks_df.to_dict('records')

            # Create simple embeddings for stocks
            def create_stock_embedding(stock):
                text = f"{stock['name']} {stock['sector']} stock"
                embedding = []
                for i in range(384):
                    hash_val = hash(f"{text}_{i}") % 1000 / 1000.0
                    embedding.append(hash_val)
                return embedding

            stock_embeddings = [create_stock_embedding(stock) for stock in stock_data]
            search_engine.index_stocks(stock_data, stock_embeddings)  # type: ignore

        except Exception as e:
            logger.warning(f"Could not load stocks data: {e}")

        # Load news data
        try:
            news_df = pd.read_csv("data/news.csv")
            news_data = news_df.to_dict('records')

            # Create simple embeddings for news
            def create_news_embedding(news):
                text = f"{news['title']} {news['summary']}"
                embedding = []
                for i in range(384):
                    hash_val = hash(f"{text}_{i}") % 1000 / 1000.0
                    embedding.append(hash_val)
                return embedding

            news_embeddings = [create_news_embedding(news) for news in news_data]
            search_engine.index_news(news_data, news_embeddings)  # type: ignore

        except Exception as e:
            logger.warning(f"Could not load news data: {e}")

    except Exception as e:
        logger.error(f"Error initializing search engine: {e}")

# Create FastAPI app
app = FastAPI(
    title="Finance AI Assistant API",
    description="A comprehensive financial data API with RAG capabilities",
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

# Pydantic models
class QueryRequest(BaseModel):
    query: str = Field(..., description="User query")
    context_limit: int = Field(5, description="Maximum number of context documents")

class QueryResponse(BaseModel):
    query: str
    response: str
    context_docs: List[Dict[str, Any]]
    timestamp: str
    model_used: str

class StockInfo(BaseModel):
    symbol: str
    name: str
    sector: Optional[str]
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]

class NewsItem(BaseModel):
    title: str
    summary: str
    url: str
    published_at: str
    sentiment_score: float
    sentiment_label: str
    source: str
    symbols: List[str]

class PortfolioSummary(BaseModel):
    total_value: float
    total_invested: float
    total_gain_loss: float
    total_gain_loss_percent: float
    holdings_count: int
    top_holdings: List[Dict[str, Any]]
    sector_allocation: Dict[str, float]

class SentimentAnalysis(BaseModel):
    symbol: str
    sentiment_score: float
    sentiment_label: str
    news_count: int
    recent_news: List[Dict[str, Any]]
    analysis: str

# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Finance AI Assistant API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "query": "/api/query",
            "stocks": "/api/stocks/{symbol}",
            "news": "/api/news",
            "sentiment": "/api/sentiment/{symbol}",
            "portfolio": "/api/portfolio"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "llm": llm_manager.get_config_info(),
            "search_engine": search_engine.get_stats()
        }
    }

@app.post("/api/query", response_model=QueryResponse)
async def query_financial_data(request: QueryRequest):
    """
    Query financial data using RAG pipeline
    """
    try:
        result = await rag_pipeline.query(request.query, request.context_limit)
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/api/stocks/{symbol}", response_model=StockInfo)
async def get_stock_info(symbol: str):
    """
    Get stock information
    """
    try:
        stock_data = await stock_ingestion.get_stock_quote_yfinance(symbol)

        if not stock_data:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")

        return StockInfo(
            symbol=stock_data['symbol'],
            name=stock_data['name'],
            sector=stock_data.get('sector', ''),
            price=stock_data['current_price'],
            change=stock_data['current_price'] - stock_data['previous_close'],
            change_percent=((stock_data['current_price'] / stock_data['previous_close'] - 1) * 100) if stock_data['previous_close'] > 0 else 0,
            volume=stock_data['volume'],
            market_cap=stock_data.get('market_cap'),
            pe_ratio=stock_data.get('pe_ratio'),
            dividend_yield=stock_data.get('dividend_yield')
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stock info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching stock info: {str(e)}")

@app.get("/api/stocks", response_model=List[StockInfo])
async def get_multiple_stocks(symbols: str = Query(..., description="Comma-separated list of stock symbols")):
    """
    Get information for multiple stocks
    """
    try:
        symbol_list = [s.strip() for s in symbols.split(',') if s.strip()]
        stock_data_list = await stock_ingestion.get_multiple_stocks(symbol_list)

        result = []
        for stock_data in stock_data_list:
            result.append(StockInfo(
                symbol=stock_data['symbol'],
                name=stock_data['name'],
                sector=stock_data.get('sector', ''),
                price=stock_data['current_price'],
                change=stock_data['current_price'] - stock_data['previous_close'],
                change_percent=((stock_data['current_price'] / stock_data['previous_close'] - 1) * 100) if stock_data['previous_close'] > 0 else 0,
                volume=stock_data['volume'],
                market_cap=stock_data.get('market_cap'),
                pe_ratio=stock_data.get('pe_ratio'),
                dividend_yield=stock_data.get('dividend_yield')
            ))

        return result

    except Exception as e:
        logger.error(f"Error fetching multiple stocks: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching stocks: {str(e)}")

@app.get("/api/news", response_model=List[NewsItem])
async def get_news(limit: int = Query(20, description="Maximum number of news items")):
    """
    Get financial news
    """
    try:
        news_data = await news_ingestion.get_all_news(limit=limit)

        result = []
        for news_item in news_data:
            result.append(NewsItem(
                title=news_item['title'],
                summary=news_item['summary'],
                url=news_item['url'],
                published_at=news_item['published_at'],
                sentiment_score=news_item['sentiment_score'],
                sentiment_label=news_item['sentiment_label'],
                source=news_item['source'],
                symbols=news_item.get('symbols', [])
            ))

        return result

    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@app.get("/api/news/{symbol}", response_model=List[NewsItem])
async def get_company_news(symbol: str, limit: int = Query(10, description="Maximum number of news items")):
    """
    Get news for a specific company
    """
    try:
        news_data = await news_ingestion.get_company_specific_news(symbol, limit)

        result = []
        for news_item in news_data:
            result.append(NewsItem(
                title=news_item['title'],
                summary=news_item['summary'],
                url=news_item['url'],
                published_at=news_item['published_at'],
                sentiment_score=news_item['sentiment_score'],
                sentiment_label=news_item['sentiment_label'],
                source=news_item['source'],
                symbols=news_item.get('symbols', [])
            ))

        return result

    except Exception as e:
        logger.error(f"Error fetching news for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching company news: {str(e)}")

@app.get("/api/sentiment/{symbol}", response_model=SentimentAnalysis)
async def get_sentiment_analysis(symbol: str):
    """
    Get sentiment analysis for a stock
    """
    try:
        sentiment_data = await rag_pipeline.analyze_sentiment(symbol)
        return SentimentAnalysis(**sentiment_data)

    except Exception as e:
        logger.error(f"Error analyzing sentiment for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing sentiment: {str(e)}")

@app.get("/api/portfolio", response_model=PortfolioSummary)
async def get_portfolio_summary():
    """
    Get portfolio summary
    """
    try:
        portfolio_data = portfolio_ingestion.load_portfolio_data()
        summary = portfolio_ingestion.get_portfolio_summary()

        return PortfolioSummary(
            total_value=summary['total_value'],
            total_invested=summary['total_invested'],
            total_gain_loss=summary['total_gain_loss'],
            total_gain_loss_percent=summary['total_gain_loss_percent'],
            holdings_count=summary['holdings_count'],
            top_holdings=summary['top_holdings'],
            sector_allocation=summary['sector_allocation']
        )

    except Exception as e:
        logger.error(f"Error getting portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting portfolio summary: {str(e)}")

@app.get("/api/market/indices")
async def get_market_indices():
    """
    Get major market indices
    """
    try:
        indices_data = await stock_ingestion.get_market_indices()
        return indices_data

    except Exception as e:
        logger.error(f"Error fetching market indices: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching market indices: {str(e)}")

# WebSocket endpoint for real-time data
@app.websocket("/ws/stocks/{symbol}")
async def websocket_stock_data(websocket: WebSocket, symbol: str):
    """
    WebSocket endpoint for real-time stock data
    """
    await websocket.accept()

    try:
        while True:
            # Get real-time stock data
            stock_data = await stock_ingestion.get_stock_quote_yfinance(symbol)

            if stock_data:
                await websocket.send_json({
                    "type": "stock_update",
                    "symbol": symbol,
                    "data": stock_data,
                    "timestamp": datetime.now().isoformat()
                })

            # Wait before next update
            await asyncio.sleep(30)  # Update every 30 seconds

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for {symbol}")
    except Exception as e:
        logger.error(f"Error in WebSocket for {symbol}: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Error fetching data: {str(e)}"
            })
        except:
            pass

@app.websocket("/ws/news")
async def websocket_news_data(websocket: WebSocket):
    """
    WebSocket endpoint for real-time news updates
    """
    await websocket.accept()

    try:
        while True:
            # Get latest news
            news_data = await news_ingestion.get_all_news(limit=5)

            await websocket.send_json({
                "type": "news_update",
                "data": news_data,
                "timestamp": datetime.now().isoformat()
            })

            # Wait before next update
            await asyncio.sleep(60)  # Update every minute

    except WebSocketDisconnect:
        logger.info("News WebSocket disconnected")
    except Exception as e:
        logger.error(f"Error in news WebSocket: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Error fetching news: {str(e)}"
            })
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Finance AI Assistant API")
    uvicorn.run(app, host="0.0.0.0", port=8000)