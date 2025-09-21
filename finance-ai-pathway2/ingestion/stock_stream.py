"""
Stock Data Ingestion Module
Handles fetching real-time and historical stock data from multiple sources
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import asyncio
import httpx
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockDataIngestion:
    """Handles stock data ingestion from multiple sources"""

    def __init__(self):
        self.api_key = os.getenv('RAPIDAPI_KEY', '')
        self.base_url = 'https://yahoo-finance-real-time1.p.rapidapi.com'

    async def get_stock_quote_yfinance(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock quote using yfinance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")

            if data.empty:
                return None

            latest = data.iloc[-1]
            info = ticker.info

            return {
                'symbol': symbol,
                'name': info.get('longName', symbol),
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
                'sector': info.get('sector'),
                'industry': info.get('industry'),
                'source': 'yfinance',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"YFinance error for {symbol}: {e}")
            return None

    async def get_stock_quote_rapidapi(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get stock quote using RapidAPI Yahoo Finance"""
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
                'name': stock_data.get('longName', symbol),
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
                'sector': stock_data.get('sector', ''),
                'industry': stock_data.get('industry', ''),
                'source': 'rapidapi',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"RapidAPI error for {symbol}: {e}")
            return None

    async def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Get historical stock data"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)

            if data.empty:
                return pd.DataFrame()

            # Add symbol column
            data['symbol'] = symbol
            return data.reset_index()

        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return pd.DataFrame()

    async def get_multiple_stocks(self, symbols: List[str]) -> List[Dict[str, Any]]:
        """Get data for multiple stocks concurrently"""
        tasks = []
        for symbol in symbols:
            # Try RapidAPI first, fallback to yfinance
            task = self.get_stock_quote_rapidapi(symbol)
            tasks.append((symbol, task))

        results = []
        for symbol, task in tasks:
            try:
                result = await task
                if result:
                    results.append(result)
                else:
                    # Fallback to yfinance
                    yf_result = await self.get_stock_quote_yfinance(symbol)
                    if yf_result:
                        results.append(yf_result)
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                # Final fallback to yfinance
                try:
                    yf_result = await self.get_stock_quote_yfinance(symbol)
                    if yf_result:
                        results.append(yf_result)
                except:
                    pass

        return results

    async def get_market_indices(self) -> Dict[str, Any]:
        """Get major market indices data"""
        indices = ["^GSPC", "^IXIC", "^DJI", "^RUT"]  # S&P 500, NASDAQ, Dow Jones, Russell 2000
        index_data = {}

        for symbol in indices:
            try:
                data = await self.get_stock_quote_yfinance(symbol)
                if data:
                    index_data[symbol] = {
                        "name": self._get_index_name(symbol),
                        "current_price": data['current_price'],
                        "change": data['current_price'] - data['previous_close'],
                        "change_percent": ((data['current_price'] / data['previous_close'] - 1) * 100) if data['previous_close'] > 0 else 0,
                        "source": data['source']
                    }
            except Exception as e:
                logger.warning(f"Error fetching data for index {symbol}: {e}")
                continue

        return index_data

    def _get_index_name(self, symbol: str) -> str:
        """Get human-readable name for index symbol"""
        names = {
            "^GSPC": "S&P 500",
            "^IXIC": "NASDAQ Composite",
            "^DJI": "Dow Jones Industrial Average",
            "^RUT": "Russell 2000"
        }
        return names.get(symbol, symbol)

    async def get_sector_data(self, sector: str) -> List[Dict[str, Any]]:
        """Get stocks data for a specific sector"""
        # This would typically query a database or API for sector stocks
        # For now, return popular stocks from the sector
        sector_stocks = {
            "Technology": ["AAPL", "MSFT", "GOOGL", "NVDA", "TSLA"],
            "Financial Services": ["JPM", "V", "BAC", "WFC", "GS"],
            "Healthcare": ["JNJ", "PFE", "UNH", "ABT", "TMO"],
            "Consumer Discretionary": ["AMZN", "TSLA", "HD", "MCD", "NKE"],
            "Consumer Staples": ["WMT", "PG", "KO", "PEP", "COST"]
        }

        if sector not in sector_stocks:
            return []

        return await self.get_multiple_stocks(sector_stocks[sector])

    async def get_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive stock data for a single symbol"""
        try:
            # Try RapidAPI first, fallback to yfinance
            result = await self.get_stock_quote_rapidapi(symbol)
            if result:
                return result

            # Fallback to yfinance
            result = await self.get_stock_quote_yfinance(symbol)
            if result:
                return result

            return {
                'symbol': symbol,
                'error': 'Unable to fetch data from any source',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in get_stock_data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def calculate_technical_indicators(self, prices: List[float]) -> Dict[str, float]:
        """Calculate technical indicators from price data"""
        if len(prices) < 14:  # Need minimum data for RSI
            return {
                'rsi': 0.0,
                'sma_5': 0.0,
                'sma_10': 0.0,
                'sma_20': 0.0
            }

        try:
            # Calculate RSI
            def calculate_rsi(prices, period=14):
                deltas = np.diff(prices)
                gains = np.where(deltas > 0, deltas, 0)
                losses = np.where(deltas < 0, -deltas, 0)

                avg_gain = np.mean(gains[:period])
                avg_loss = np.mean(losses[:period])

                for i in range(period, len(gains)):
                    avg_gain = (avg_gain * (period - 1) + gains[i]) / period
                    avg_loss = (avg_loss * (period - 1) + losses[i]) / period

                rs = avg_gain / avg_loss if avg_loss != 0 else 0
                rsi = 100 - (100 / (1 + rs))
                return rsi

            # Calculate Simple Moving Averages
            sma_5 = np.mean(prices[-5:]) if len(prices) >= 5 else 0
            sma_10 = np.mean(prices[-10:]) if len(prices) >= 10 else 0
            sma_20 = np.mean(prices[-20:]) if len(prices) >= 20 else 0

            return {
                'rsi': float(round(calculate_rsi(np.array(prices)), 2)),
                'sma_5': float(round(sma_5, 2)),
                'sma_10': float(round(sma_10, 2)),
                'sma_20': float(round(sma_20, 2))
            }
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return {
                'rsi': 0.0,
                'sma_5': 0.0,
                'sma_10': 0.0,
                'sma_20': 0.0
            }

# Global instance
stock_ingestion = StockDataIngestion()

if __name__ == "__main__":
    async def main():
        # Test the stock ingestion
        symbols = ["AAPL", "MSFT", "GOOGL"]
        data = await stock_ingestion.get_multiple_stocks(symbols)
        print(f"Fetched data for {len(data)} stocks")

        # Test indices
        indices = await stock_ingestion.get_market_indices()
        print(f"Fetched data for {len(indices)} indices")

    asyncio.run(main())