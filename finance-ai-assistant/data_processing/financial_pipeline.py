"""
Financial Data Processing Pipeline (Simplified for Windows)
Handles financial data processing and analysis without Pathway
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
import asyncio
import threading
import time
import os

logger = logging.getLogger(__name__)

class FinancialDataProcessor:
    """
    Simplified financial data processing pipeline for Windows
    """

    def __init__(self):
        self.price_data = pd.DataFrame()
        self.analysis_data = pd.DataFrame()
        self.alerts_data = pd.DataFrame()
        self.is_running = False
        self.data_thread = None

    def load_sample_data(self) -> pd.DataFrame:
        """
        Load or create sample financial data
        """
        try:
            # Try to load existing data
            if os.path.exists("data/price_stream.csv"):
                data = pd.read_csv("data/price_stream.csv")
                data['timestamp'] = pd.to_datetime(data['timestamp'])
                logger.info(f"Loaded {len(data)} records from existing data")
                return data
        except Exception as e:
            logger.warning(f"Could not load existing data: {e}")

        # Create sample data
        logger.info("Creating sample financial data...")
        data = self._create_sample_data()
        self._save_data(data)
        return data

    def _create_sample_data(self, days: int = 30) -> pd.DataFrame:
        """
        Create sample financial data for testing
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # Sample stock symbols
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'JPM', 'JNJ']

        data_rows = []
        current_date = start_date

        while current_date <= end_date:
            if current_date.weekday() < 5:  # Only weekdays
                for symbol in symbols:
                    # Generate realistic price movements
                    base_price = 100 + (hash(symbol + str(current_date.date())) % 300)
                    volatility = np.random.normal(0, 0.03)  # 3% daily volatility
                    price = base_price * (1 + volatility)

                    data_rows.append({
                        'symbol': symbol,
                        'timestamp': current_date,
                        'price': round(price, 2),
                        'volume': np.random.randint(1000000, 10000000),
                        'source': 'simulated'
                    })

            current_date += timedelta(days=1)

        return pd.DataFrame(data_rows)

    def _save_data(self, data: pd.DataFrame):
        """
        Save data to CSV file
        """
        os.makedirs("data", exist_ok=True)
        data.to_csv("data/price_stream.csv", index=False)
        logger.info(f"Sample data saved to data/price_stream.csv")

    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for the data
        """
        result_data = []

        for symbol in data['symbol'].unique():
            symbol_data = data[data['symbol'] == symbol].copy()
            symbol_data = symbol_data.sort_values('timestamp')

            # Calculate SMA (Simple Moving Average)
            symbol_data['sma_20'] = symbol_data['price'].rolling(window=20, min_periods=1).mean()

            # Calculate RSI (Relative Strength Index)
            symbol_data['rsi'] = self._calculate_rsi(symbol_data['price'])

            # Calculate Bollinger Bands
            bb_result = self._calculate_bollinger_bands(symbol_data['price'])
            symbol_data['bb_upper'] = bb_result['upper']
            symbol_data['bb_middle'] = bb_result['middle']
            symbol_data['bb_lower'] = bb_result['lower']

            # Calculate price change
            symbol_data['price_change'] = symbol_data['price'].diff()

            # Determine sentiment
            symbol_data['sentiment'] = symbol_data['price_change'].apply(
                lambda x: 'bullish' if x > 0 else ('bearish' if x < 0 else 'neutral')
            )

            result_data.append(symbol_data)

        return pd.concat(result_data, ignore_index=True)

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate RSI for a price series
        """
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()

            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi.fillna(50.0)  # Fill NaN values with neutral RSI
        except:
            return pd.Series([50.0] * len(prices), index=prices.index)

    def _calculate_bollinger_bands(self, prices: pd.Series, period: int = 20) -> Dict[str, pd.Series]:
        """
        Calculate Bollinger Bands
        """
        sma = prices.rolling(window=period, min_periods=1).mean()
        std = prices.rolling(window=period, min_periods=1).std()

        return {
            'upper': sma + (std * 2),
            'middle': sma,
            'lower': sma - (std * 2)
        }

    def create_alerts(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Create alerts for significant market events
        """
        alerts = []

        for symbol in data['symbol'].unique():
            symbol_data = data[data['symbol'] == symbol].copy()

            # Price movement alerts (>5% change)
            price_changes = symbol_data['price'].pct_change()
            significant_moves = price_changes[abs(price_changes) > 0.05]

            for idx, change in significant_moves.items():
                alerts.append({
                    'symbol': symbol,
                    'timestamp': symbol_data.loc[idx, 'timestamp'],
                    'alert_type': 'price_movement',
                    'message': f"Significant price movement: {change:.2%}",
                    'value': change
                })

            # RSI alerts
            rsi_values = symbol_data['rsi']
            overbought = rsi_values[rsi_values > 70]
            oversold = rsi_values[rsi_values < 30]

            for idx in overbought.index:
                alerts.append({
                    'symbol': symbol,
                    'timestamp': symbol_data.loc[idx, 'timestamp'],
                    'alert_type': 'overbought',
                    'message': f"Overbought signal: RSI = {rsi_values.loc[idx]:.1f}",
                    'value': rsi_values.loc[idx]
                })

            for idx in oversold.index:
                alerts.append({
                    'symbol': symbol,
                    'timestamp': symbol_data.loc[idx, 'timestamp'],
                    'alert_type': 'oversold',
                    'message': f"Oversold signal: RSI = {rsi_values.loc[idx]:.1f}",
                    'value': rsi_values.loc[idx]
                })

        return pd.DataFrame(alerts)

    def start_data_processing(self):
        """
        Start the data processing pipeline
        """
        if self.is_running:
            logger.warning("Data processing is already running")
            return

        self.is_running = True
        logger.info("Starting financial data processing pipeline...")

        # Load initial data
        self.price_data = self.load_sample_data()
        self.analysis_data = self.calculate_technical_indicators(self.price_data)
        self.alerts_data = self.create_alerts(self.analysis_data)

        logger.info(f"Processed {len(self.price_data)} price records")
        logger.info(f"Generated {len(self.analysis_data)} analysis records")
        logger.info(f"Created {len(self.alerts_data)} alerts")

        # Start background thread for continuous updates
        self.data_thread = threading.Thread(target=self._continuous_update, daemon=True)
        self.data_thread.start()

    def _continuous_update(self):
        """
        Continuously update data in the background
        """
        while self.is_running:
            try:
                # Simulate real-time updates every 30 seconds
                time.sleep(30)

                # Add new data point
                latest_timestamp = self.price_data['timestamp'].max()
                new_timestamp = latest_timestamp + timedelta(minutes=30)

                # Generate new data points for all symbols
                new_data = []
                for symbol in self.price_data['symbol'].unique():
                    # Get the last price for this symbol
                    last_price = self.price_data[
                        (self.price_data['symbol'] == symbol) &
                        (self.price_data['timestamp'] == latest_timestamp)
                    ]['price'].iloc[0]

                    # Generate new price with some random movement
                    change = np.random.normal(0, 0.01)  # 1% volatility
                    new_price = last_price * (1 + change)

                    new_data.append({
                        'symbol': symbol,
                        'timestamp': new_timestamp,
                        'price': round(new_price, 2),
                        'volume': np.random.randint(1000000, 10000000),
                        'source': 'simulated'
                    })

                # Add new data
                new_df = pd.DataFrame(new_data)
                self.price_data = pd.concat([self.price_data, new_df], ignore_index=True)

                # Recalculate indicators
                self.analysis_data = self.calculate_technical_indicators(self.price_data)
                self.alerts_data = self.create_alerts(self.analysis_data)

                logger.info(f"Updated data at {new_timestamp} - Total records: {len(self.price_data)}")

            except Exception as e:
                logger.error(f"Error in continuous update: {e}")
                time.sleep(60)  # Wait longer on error

    def stop_data_processing(self):
        """
        Stop the data processing pipeline
        """
        self.is_running = False
        if self.data_thread:
            self.data_thread.join(timeout=5)
        logger.info("Financial data processing pipeline stopped")

    def get_latest_data(self) -> Dict[str, Any]:
        """
        Get the latest processed data
        """
        return {
            'price_data': self.price_data.tail(100).to_dict('records'),  # Last 100 records
            'analysis_data': self.analysis_data.tail(50).to_dict('records'),  # Last 50 records
            'alerts': self.alerts_data.tail(10).to_dict('records'),  # Last 10 alerts
            'last_update': datetime.now().isoformat(),
            'total_records': len(self.price_data)
        }

    def get_data_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the processed data
        """
        if self.price_data.empty:
            return {'message': 'No data available'}

        return {
            'symbols': self.price_data['symbol'].unique().tolist(),
            'total_records': len(self.price_data),
            'date_range': {
                'start': self.price_data['timestamp'].min().isoformat(),
                'end': self.price_data['timestamp'].max().isoformat()
            },
            'latest_prices': {
                symbol: group['price'].iloc[-1]
                for symbol, group in self.price_data.groupby('symbol')
            }
        }

# Utility functions for data integration
def create_sample_data() -> pd.DataFrame:
    """
    Create sample financial data for testing
    """
    # Generate sample data for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    # Sample stock symbols
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA']

    data_rows = []
    current_date = start_date

    while current_date <= end_date:
        if current_date.weekday() < 5:  # Only weekdays
            for symbol in symbols:
                # Generate realistic price movements
                base_price = 100 + (hash(symbol + str(current_date.date())) % 200)
                volatility = np.random.normal(0, 0.02)  # 2% daily volatility
                price = base_price * (1 + volatility)

                data_rows.append({
                    'symbol': symbol,
                    'timestamp': current_date,
                    'price': round(price, 2),
                    'volume': np.random.randint(1000000, 10000000),
                    'source': 'simulated'
                })

        current_date += timedelta(days=1)

    return pd.DataFrame(data_rows)

def save_sample_data(data: pd.DataFrame, filename: str = "data/price_stream.csv"):
    """
    Save sample data to CSV file
    """
    import os

    # Create data directory if it doesn't exist
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Save data
    data.to_csv(filename, index=False)
    logger.info(f"Sample data saved to {filename}")

if __name__ == "__main__":
    # Create and run the financial data processor
    processor = FinancialDataProcessor()

    # Start the data processing pipeline
    processor.start_data_processing()

    try:
        # Keep the main thread alive
        while processor.is_running:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        processor.stop_data_processing()