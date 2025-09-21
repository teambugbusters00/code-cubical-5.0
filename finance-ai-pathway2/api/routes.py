"""
Additional API Routes for Finance AI Assistant
Provides specialized endpoints for advanced financial analysis
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

# Import our modules
from ingestion.stock_stream import stock_ingestion
from rag.rag_pipeline import rag_pipeline

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

@router.get("/api/stocks/{symbol}/analysis")
async def get_stock_analysis(symbol: str):
    """
    Get comprehensive stock analysis
    """
    try:
        # Get stock data
        stock_data = await stock_ingestion.get_stock_quote_yfinance(symbol)

        if not stock_data:
            raise HTTPException(status_code=404, detail=f"Stock {symbol} not found")

        # Get sentiment analysis
        sentiment_data = await rag_pipeline.analyze_sentiment(symbol)

        # Get recent news
        from ingestion.news_stream import news_ingestion
        news_data = await news_ingestion.get_company_specific_news(symbol, limit=5)

        # Calculate additional metrics
        current_price = stock_data['current_price']
        previous_close = stock_data['previous_close']
        day_change = current_price - previous_close
        day_change_percent = (day_change / previous_close * 100) if previous_close > 0 else 0

        # Determine trend
        trend = "neutral"
        if day_change_percent > 2:
            trend = "bullish"
        elif day_change_percent < -2:
            trend = "bearish"

        analysis = {
            "symbol": symbol,
            "name": stock_data.get('name', symbol),
            "current_price": current_price,
            "previous_close": previous_close,
            "day_change": round(day_change, 2),
            "day_change_percent": round(day_change_percent, 2),
            "trend": trend,
            "volume": stock_data.get('volume', 0),
            "market_cap": stock_data.get('market_cap'),
            "pe_ratio": stock_data.get('pe_ratio'),
            "dividend_yield": stock_data.get('dividend_yield'),
            "fifty_two_week_high": stock_data.get('fifty_two_week_high'),
            "fifty_two_week_low": stock_data.get('fifty_two_week_low'),
            "sector": stock_data.get('sector', ''),
            "sentiment_analysis": sentiment_data,
            "recent_news": news_data,
            "analysis_timestamp": datetime.now().isoformat()
        }

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing stock {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing stock: {str(e)}")

@router.get("/api/stocks/{symbol}/history")
async def get_stock_history(
    symbol: str,
    period: str = Query("1y", description="Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)"),
    interval: str = Query("1d", description="Data interval (1d, 1wk, 1mo)")
):
    """
    Get historical stock data
    """
    try:
        historical_data = await stock_ingestion.get_historical_data(symbol, period, interval)

        if historical_data.empty:
            raise HTTPException(status_code=404, detail=f"No historical data found for {symbol}")

        # Convert to list of dictionaries
        records = historical_data.reset_index().to_dict('records')

        return {
            "symbol": symbol,
            "period": period,
            "interval": interval,
            "data_points": len(records),
            "data": records,
            "timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching historical data: {str(e)}")

@router.get("/api/market/overview")
async def get_market_overview():
    """
    Get comprehensive market overview
    """
    try:
        # Get market indices
        indices_data = await stock_ingestion.get_market_indices()

        # Get top news
        from ingestion.news_stream import news_ingestion
        news_data = await news_ingestion.get_all_news(limit=10)

        # Get top sentiment analysis for major stocks
        major_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
        sentiment_data = []

        for symbol in major_symbols:
            try:
                sentiment = await rag_pipeline.analyze_sentiment(symbol)
                sentiment_data.append(sentiment)
            except:
                continue

        overview = {
            "timestamp": datetime.now().isoformat(),
            "market_indices": indices_data,
            "top_news": news_data[:5],
            "sentiment_summary": {
                "positive_count": sum(1 for s in sentiment_data if s['sentiment_label'] == 'positive'),
                "negative_count": sum(1 for s in sentiment_data if s['sentiment_label'] == 'negative'),
                "neutral_count": sum(1 for s in sentiment_data if s['sentiment_label'] == 'neutral'),
                "total_analyzed": len(sentiment_data)
            },
            "top_sentiments": sentiment_data[:5]
        }

        return overview

    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting market overview: {str(e)}")

@router.get("/api/portfolio/insights")
async def get_portfolio_insights():
    """
    Get AI-powered portfolio insights
    """
    try:
        # Load portfolio data
        from ingestion.portfolio_stream import portfolio_ingestion
        portfolio_data = portfolio_ingestion.load_portfolio_data()

        if not portfolio_data:
            raise HTTPException(status_code=404, detail="No portfolio data found")

        # Get portfolio insights
        insights = await rag_pipeline.get_portfolio_insights(portfolio_data)

        # Add additional analysis
        holdings = portfolio_data.get('holdings', [])
        symbols = [holding['symbol'] for holding in holdings]

        # Get sentiment for all holdings
        sentiment_summary = {
            'positive': 0,
            'negative': 0,
            'neutral': 0
        }

        for symbol in symbols:
            try:
                sentiment = await rag_pipeline.analyze_sentiment(symbol)
                sentiment_summary[sentiment['sentiment_label']] += 1
            except:
                sentiment_summary['neutral'] += 1

        # Calculate risk metrics
        total_value = portfolio_data.get('total_value', 0)
        sector_allocation = portfolio_data.get('sector_allocation', {})

        # Determine risk level
        risk_level = "moderate"
        if len(sector_allocation) <= 2:
            risk_level = "high"  # Low diversification
        elif len(sector_allocation) >= 5:
            risk_level = "low"  # High diversification

        enhanced_insights = {
            **insights,
            "risk_assessment": {
                "risk_level": risk_level,
                "diversification_score": len(sector_allocation),
                "sector_concentration": max(sector_allocation.values()) if sector_allocation else 0
            },
            "sentiment_summary": sentiment_summary,
            "recommendations": generate_portfolio_recommendations(insights, risk_level)
        }

        return enhanced_insights

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting portfolio insights: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting portfolio insights: {str(e)}")

def generate_portfolio_recommendations(insights: Dict[str, Any], risk_level: str) -> List[str]:
    """
    Generate portfolio recommendations based on analysis
    """
    recommendations = []

    # Risk-based recommendations
    if risk_level == "high":
        recommendations.append("Consider diversifying across more sectors to reduce risk")
        recommendations.append("Review your sector concentration and consider rebalancing")

    if risk_level == "low":
        recommendations.append("Your portfolio shows good diversification")
        recommendations.append("Consider reviewing individual stock performance")

    # Sentiment-based recommendations
    sentiment_summary = insights.get('sentiment_summary', {})
    positive_count = sentiment_summary.get('positive', 0)
    negative_count = sentiment_summary.get('negative', 0)

    if negative_count > positive_count:
        recommendations.append("Monitor stocks with negative sentiment more closely")
        recommendations.append("Consider reviewing your holdings in light of recent news")

    if positive_count > 0:
        recommendations.append("Positive sentiment in your holdings is encouraging")

    # Performance-based recommendations
    total_gain_loss_percent = insights.get('total_gain_loss_percent', 0)
    if total_gain_loss_percent < -10:
        recommendations.append("Portfolio shows significant losses - consider reviewing your strategy")
    elif total_gain_loss_percent > 20:
        recommendations.append("Strong portfolio performance - consider taking some profits")

    return recommendations

@router.get("/api/search")
async def search_financial_data(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum results"),
    doc_types: str = Query("news,stock", description="Document types to search (comma-separated)")
):
    """
    Search across all financial data
    """
    try:
        # Parse document types
        doc_type_list = [dt.strip() for dt in doc_types.split(',') if dt.strip()]

        # Import search function
        from processing.indexing import search_financial_data

        # Perform search
        search_results = search_financial_data(query, top_k=limit, doc_types=doc_type_list)

        # Format results
        formatted_results = []
        for score, doc in search_results:
            formatted_results.append({
                "score": score,
                "content": doc.get('title', doc.get('name', str(doc))),
                "doc_type": doc.get('doc_type', 'unknown'),
                "metadata": {
                    "symbol": doc.get('symbol', ''),
                    "sentiment_score": doc.get('sentiment_score', 0),
                    "published_at": doc.get('published_at', ''),
                    "sector": doc.get('sector', ''),
                    "price": doc.get('price', 0)
                }
            })

        return {
            "query": query,
            "total_results": len(formatted_results),
            "results": formatted_results,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error searching financial data: {e}")
        raise HTTPException(status_code=500, detail=f"Error searching data: {str(e)}")

@router.get("/api/trends/{symbol}")
async def get_stock_trends(symbol: str, days: int = Query(30, description="Number of days to analyze")):
    """
    Get trend analysis for a stock
    """
    try:
        # Get historical data
        historical_data = await stock_ingestion.get_historical_data(symbol, f"{days}d", "1d")

        if historical_data.empty:
            raise HTTPException(status_code=404, detail=f"No trend data found for {symbol}")

        # Calculate trends
        recent_data = historical_data.tail(10)  # Last 10 days
        older_data = historical_data.tail(30).head(20)  # Previous 20 days

        recent_avg = recent_data['Close'].mean()
        older_avg = older_data['Close'].mean()

        # Determine trend
        trend_direction = "sideways"
        if recent_avg > older_avg * 1.05:
            trend_direction = "upward"
        elif recent_avg < older_avg * 0.95:
            trend_direction = "downward"

        # Calculate volatility
        volatility = historical_data['Close'].pct_change().std() * 100

        # Get sentiment trend
        sentiment_data = await rag_pipeline.analyze_sentiment(symbol)

        trends = {
            "symbol": symbol,
            "analysis_period_days": days,
            "trend_direction": trend_direction,
            "trend_strength": abs(recent_avg - older_avg) / older_avg * 100,
            "volatility_percent": round(volatility, 2),
            "current_price": historical_data['Close'].iloc[-1],
            "price_change_10d": ((recent_data['Close'].iloc[-1] / recent_data['Close'].iloc[0] - 1) * 100) if len(recent_data) > 1 else 0,
            "sentiment_trend": sentiment_data.get('sentiment_label', 'neutral'),
            "data_points": len(historical_data),
            "timestamp": datetime.now().isoformat()
        }

        return trends

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing trends for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Error analyzing trends: {str(e)}")