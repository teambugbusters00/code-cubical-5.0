#!/usr/bin/env python3
"""
Demo Data Generator for Finance AI Assistant
Generates sample financial data for testing and demonstration purposes
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Optional, List
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_stock_data(
    symbols: list,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    output_dir: str = "data"
) -> None:
    """
    Generate sample stock price data for demonstration

    Args:
        symbols: List of stock symbols to generate data for
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        output_dir: Directory to save generated data
    """
    if start_date is None:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    if end_date is None:
        end_date = datetime.now().strftime('%Y-%m-%d')

    logger.info(f"Generating stock data from {start_date} to {end_date}")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    all_data = []

    for symbol in symbols:
        logger.info(f"Generating data for {symbol}")

        # Generate date range (weekdays only)
        date_range = pd.date_range(start=start_date, end=end_date, freq='B')  # Business days only

        # Generate realistic price movements
        base_price = 100 + (hash(symbol) % 400)  # Different base price for each symbol
        n_days = len(date_range)

        # Generate price series with some trend and volatility
        np.random.seed(hash(symbol) % 10000)  # Different seed for each symbol

        # Create trend component
        trend = np.linspace(0, np.random.uniform(-50, 100), n_days)

        # Create random walk component
        random_walk = np.random.normal(0, np.random.uniform(1, 5), n_days).cumsum()

        # Combine components
        price_series = base_price + trend + random_walk

        # Ensure prices stay positive
        price_series = np.maximum(price_series, 1)

        # Generate volume data
        base_volume = np.random.randint(1000000, 10000000)
        volume_series = np.random.normal(base_volume, base_volume * 0.3, n_days).astype(int)
        volume_series = np.maximum(volume_series, 100000)

        # Create OHLC data (Open, High, Low, Close)
        # For simplicity, we'll use Close as base and generate OHLC around it
        close_prices = price_series
        open_prices = close_prices + np.random.normal(0, close_prices * 0.02, n_days)
        high_prices = np.maximum(open_prices, close_prices) + np.abs(np.random.normal(0, close_prices * 0.01, n_days))
        low_prices = np.minimum(open_prices, close_prices) - np.abs(np.random.normal(0, close_prices * 0.01, n_days))

        # Create DataFrame for this symbol
        symbol_data = pd.DataFrame({
            'symbol': symbol,
            'timestamp': date_range,
            'open': np.round(open_prices, 2),
            'high': np.round(high_prices, 2),
            'low': np.round(low_prices, 2),
            'close': np.round(close_prices, 2),
            'volume': volume_series,
            'source': 'demo'
        })

        all_data.append(symbol_data)

    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)

    # Save to CSV
    output_file = os.path.join(output_dir, "demo_stock_data.csv")
    combined_data.to_csv(output_file, index=False)

    logger.info(f"Generated {len(combined_data)} records for {len(symbols)} symbols")
    logger.info(f"Data saved to {output_file}")

    # Display summary statistics
    print("\nData Generation Summary:")
    print(f"Symbols: {', '.join(symbols)}")
    print(f"Date range: {start_date} to {end_date}")
    print(f"Total records: {len(combined_data)}")
    print(f"Output file: {output_file}")

    # Show price range for each symbol
    print("\n💰 Price Summary:")
    for symbol in symbols:
        symbol_data = combined_data[combined_data['symbol'] == symbol]
        min_price = symbol_data['low'].min()
        max_price = symbol_data['high'].max()
        avg_price = symbol_data['close'].mean()
        print(f"  {symbol}: ${min_price:.2f} - ${max_price:.2f} (avg: ${avg_price:.2f})")

def generate_market_indices_data(output_dir: str = "data") -> None:
    """
    Generate sample market indices data
    """
    logger.info("Generating market indices data")

    indices = {
        '^GSPC': 'S&P 500',
        '^IXIC': 'NASDAQ Composite',
        '^DJI': 'Dow Jones Industrial Average',
        '^RUT': 'Russell 2000'
    }

    # Generate date range for the last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')

    all_indices_data = []

    for symbol, name in indices.items():
        logger.info(f"Generating data for {name} ({symbol})")

        # Generate index values
        base_value = 3000 + (hash(symbol) % 2000)
        n_days = len(date_range)

        np.random.seed(hash(symbol + "index") % 10000)

        # Create trend and random components
        trend = np.linspace(0, np.random.uniform(-200, 300), n_days)
        random_walk = np.random.normal(0, np.random.uniform(10, 30), n_days).cumsum()

        index_series = base_value + trend + random_walk

        # Create DataFrame
        index_data = pd.DataFrame({
            'symbol': symbol,
            'name': name,
            'timestamp': date_range,
            'value': np.round(index_series, 2),
            'change': np.round(np.random.normal(0, 20, n_days), 2),
            'change_percent': np.round(np.random.normal(0, 1, n_days), 3),
            'source': 'demo'
        })

        all_indices_data.append(index_data)

    # Combine all indices data
    combined_indices = pd.concat(all_indices_data, ignore_index=True)

    # Save to CSV
    output_file = os.path.join(output_dir, "demo_indices_data.csv")
    combined_indices.to_csv(output_file, index=False)

    logger.info(f"Generated indices data saved to {output_file}")

    print("\nMarket Indices Summary:")
    for symbol, name in indices.items():
        symbol_data = combined_indices[combined_indices['symbol'] == symbol]
        current_value = symbol_data['value'].iloc[-1]
        change = symbol_data['change'].iloc[-1]
        print(f"  {name}: {current_value:.2f} ({change:+.2f})")

def generate_sample_portfolio_data(output_dir: str = "data") -> None:
    """
    Generate sample portfolio data for demonstration
    """
    logger.info("Generating sample portfolio data")

    # Sample portfolio holdings
    portfolio = [
        {'symbol': 'AAPL', 'shares': 100, 'avg_cost': 150.00},
        {'symbol': 'MSFT', 'shares': 50, 'avg_cost': 300.00},
        {'symbol': 'GOOGL', 'shares': 25, 'avg_cost': 2500.00},
        {'symbol': 'AMZN', 'shares': 30, 'avg_cost': 3000.00},
        {'symbol': 'TSLA', 'shares': 20, 'avg_cost': 800.00},
    ]

    # Generate daily portfolio values for the last 90 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    date_range = pd.date_range(start=start_date, end=end_date, freq='B')

    portfolio_data = []

    for date in date_range:
        total_value = 0
        total_cost = 0

        for holding in portfolio:
            # Simulate price movement
            base_price = holding['avg_cost']
            days_from_start = (date - start_date).days
            volatility = np.random.normal(0, 0.02) * np.sqrt(days_from_start / 30)
            current_price = base_price * (1 + volatility)

            holding_value = holding['shares'] * current_price
            holding_cost = holding['shares'] * holding['avg_cost']

            total_value += holding_value
            total_cost += holding_cost

        daily_return = (total_value - total_cost) / total_cost * 100

        portfolio_data.append({
            'date': date,
            'total_value': round(total_value, 2),
            'total_cost': round(total_cost, 2),
            'daily_return': round(daily_return, 2),
            'source': 'demo'
        })

    # Create DataFrame and save
    portfolio_df = pd.DataFrame(portfolio_data)
    output_file = os.path.join(output_dir, "demo_portfolio_data.csv")
    portfolio_df.to_csv(output_file, index=False)

    logger.info(f"Generated portfolio data saved to {output_file}")

    print("\n💼 Sample Portfolio Summary:")
    latest_data = portfolio_data[-1]
    print(f"  Total Value: ${latest_data['total_value']:,.2f}")
    print(f"  Total Cost: ${latest_data['total_cost']:,.2f}")
    print(f"  Total Return: {latest_data['daily_return']:+.2f}%")

def main():
    """Main function to generate all demo data"""
    print("🎯 Finance AI Assistant - Demo Data Generator")
    print("=" * 50)

    # Define symbols for demo data
    demo_symbols = [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
        'NVDA', 'JPM', 'JNJ', 'V', 'WMT',
        'NFLX', 'DIS', 'BA', 'UNH', 'HD'
    ]

    # Generate all types of demo data
    try:
        generate_stock_data(demo_symbols)
        generate_market_indices_data()
        generate_sample_portfolio_data()

        print("\nDemo data generation completed successfully!")
        print("\nGenerated files:")
        print("  • data/demo_stock_data.csv")
        print("  • data/demo_indices_data.csv")
        print("  • data/demo_portfolio_data.csv")
        print("\nYou can now start the Finance AI Assistant and use this demo data!")

    except Exception as e:
        logger.error(f"Error generating demo data: {e}")
        print(f"\nError generating demo data: {e}")

if __name__ == "__main__":
    main()