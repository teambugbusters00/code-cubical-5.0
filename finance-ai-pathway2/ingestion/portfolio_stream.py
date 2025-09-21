"""
Portfolio Data Ingestion Module
Handles portfolio data management and analysis
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioDataIngestion:
    """Handles portfolio data ingestion and analysis"""

    def __init__(self, data_file: str = "data/portfolio.json"):
        self.data_file = data_file
        self.portfolio_data = None

    def load_portfolio_data(self) -> Dict[str, Any]:
        """Load portfolio data from JSON file"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.portfolio_data = json.load(f)
                logger.info(f"Loaded portfolio data from {self.data_file}")
                return self.portfolio_data
            else:
                logger.warning(f"Portfolio data file {self.data_file} not found")
                return self._create_sample_portfolio()
        except Exception as e:
            logger.error(f"Error loading portfolio data: {e}")
            return self._create_sample_portfolio()

    def save_portfolio_data(self, portfolio_data: Dict[str, Any]) -> bool:
        """Save portfolio data to JSON file"""
        try:
            # Update timestamp
            portfolio_data['updated_at'] = datetime.now().isoformat()

            with open(self.data_file, 'w') as f:
                json.dump(portfolio_data, f, indent=2)

            self.portfolio_data = portfolio_data
            logger.info(f"Saved portfolio data to {self.data_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving portfolio data: {e}")
            return False

    def _create_sample_portfolio(self) -> Dict[str, Any]:
        """Create a sample portfolio for demonstration"""
        return {
            "user_id": "demo_user",
            "portfolio_name": "Sample Tech Portfolio",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "total_value": 100000.0,
            "total_invested": 95000.0,
            "total_gain_loss": 5000.0,
            "total_gain_loss_percent": 5.26,
            "holdings": [
                {
                    "symbol": "AAPL",
                    "company_name": "Apple Inc.",
                    "shares": 50,
                    "avg_cost": 150.0,
                    "current_price": 175.0,
                    "market_value": 8750.0,
                    "gain_loss": 1250.0,
                    "gain_loss_percent": 16.67,
                    "sector": "Technology",
                    "weight": 8.75
                },
                {
                    "symbol": "MSFT",
                    "company_name": "Microsoft Corporation",
                    "shares": 30,
                    "avg_cost": 300.0,
                    "current_price": 350.0,
                    "market_value": 10500.0,
                    "gain_loss": 1500.0,
                    "gain_loss_percent": 16.67,
                    "sector": "Technology",
                    "weight": 10.5
                },
                {
                    "symbol": "GOOGL",
                    "company_name": "Alphabet Inc.",
                    "shares": 20,
                    "avg_cost": 120.0,
                    "current_price": 140.0,
                    "market_value": 2800.0,
                    "gain_loss": 400.0,
                    "gain_loss_percent": 16.67,
                    "sector": "Technology",
                    "weight": 2.8
                }
            ],
            "sector_allocation": {
                "Technology": 22.05,
                "Consumer Discretionary": 0.0,
                "Financial Services": 0.0,
                "Healthcare": 0.0,
                "Consumer Staples": 0.0,
                "Energy": 0.0,
                "Materials": 0.0,
                "Utilities": 0.0,
                "Real Estate": 0.0,
                "Communication Services": 0.0,
                "Industrials": 0.0
            }
        }

    def add_holding(self, symbol: str, shares: float, avg_cost: float, company_name: str = "") -> bool:
        """Add a new holding to the portfolio"""
        if not self.portfolio_data:
            self.load_portfolio_data()

        if not self.portfolio_data:
            return False

        # Create new holding
        new_holding = {
            "symbol": symbol,
            "company_name": company_name or symbol,
            "shares": shares,
            "avg_cost": avg_cost,
            "current_price": avg_cost,  # Will be updated with real price later
            "market_value": shares * avg_cost,
            "gain_loss": 0.0,
            "gain_loss_percent": 0.0,
            "sector": "Unknown",
            "weight": 0.0
        }

        self.portfolio_data['holdings'].append(new_holding)
        return self._update_portfolio_metrics()

    def remove_holding(self, symbol: str) -> bool:
        """Remove a holding from the portfolio"""
        if not self.portfolio_data:
            self.load_portfolio_data()

        if not self.portfolio_data:
            return False

        # Find and remove the holding
        for i, holding in enumerate(self.portfolio_data['holdings']):
            if holding['symbol'] == symbol:
                del self.portfolio_data['holdings'][i]
                return self._update_portfolio_metrics()

        return False

    def update_holding_price(self, symbol: str, current_price: float) -> bool:
        """Update the current price of a holding"""
        if not self.portfolio_data:
            self.load_portfolio_data()

        if not self.portfolio_data:
            return False

        for holding in self.portfolio_data['holdings']:
            if holding['symbol'] == symbol:
                holding['current_price'] = current_price
                holding['market_value'] = holding['shares'] * current_price
                holding['gain_loss'] = (current_price - holding['avg_cost']) * holding['shares']
                holding['gain_loss_percent'] = ((current_price / holding['avg_cost']) - 1) * 100
                return self._update_portfolio_metrics()

        return False

    def _update_portfolio_metrics(self) -> bool:
        """Update portfolio-level metrics"""
        if not self.portfolio_data or not self.portfolio_data['holdings']:
            return False

        holdings = self.portfolio_data['holdings']
        total_value = sum(holding['market_value'] for holding in holdings)
        total_invested = sum(holding['shares'] * holding['avg_cost'] for holding in holdings)

        # Update individual weights
        for holding in holdings:
            holding['weight'] = (holding['market_value'] / total_value) * 100 if total_value > 0 else 0

        # Update sector allocation
        sector_allocation = {}
        for holding in holdings:
            sector = holding.get('sector', 'Unknown')
            if sector not in sector_allocation:
                sector_allocation[sector] = 0
            sector_allocation[sector] += holding['weight']

        # Update portfolio data
        self.portfolio_data.update({
            'total_value': total_value,
            'total_invested': total_invested,
            'total_gain_loss': total_value - total_invested,
            'total_gain_loss_percent': ((total_value / total_invested) - 1) * 100 if total_invested > 0 else 0,
            'sector_allocation': sector_allocation,
            'updated_at': datetime.now().isoformat()
        })

        return True

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get portfolio summary statistics"""
        if not self.portfolio_data:
            self.load_portfolio_data()

        if not self.portfolio_data:
            return {}

        return {
            'total_value': self.portfolio_data.get('total_value', 0),
            'total_invested': self.portfolio_data.get('total_invested', 0),
            'total_gain_loss': self.portfolio_data.get('total_gain_loss', 0),
            'total_gain_loss_percent': self.portfolio_data.get('total_gain_loss_percent', 0),
            'holdings_count': len(self.portfolio_data.get('holdings', [])),
            'top_holdings': sorted(
                self.portfolio_data.get('holdings', []),
                key=lambda x: x.get('market_value', 0),
                reverse=True
            )[:5],
            'sector_allocation': self.portfolio_data.get('sector_allocation', {}),
            'last_updated': self.portfolio_data.get('updated_at', '')
        }

    def get_holding_symbols(self) -> List[str]:
        """Get list of all symbols in the portfolio"""
        if not self.portfolio_data:
            self.load_portfolio_data()

        if not self.portfolio_data:
            return []

        return [holding['symbol'] for holding in self.portfolio_data.get('holdings', [])]

    def export_to_csv(self, filename: str = "data/portfolio_export.csv") -> bool:
        """Export portfolio data to CSV"""
        try:
            if not self.portfolio_data:
                self.load_portfolio_data()

            if not self.portfolio_data:
                return False

            # Convert holdings to DataFrame
            holdings_df = pd.DataFrame(self.portfolio_data.get('holdings', []))

            # Add portfolio metadata
            holdings_df['portfolio_name'] = self.portfolio_data.get('portfolio_name', '')
            holdings_df['total_value'] = self.portfolio_data.get('total_value', 0)
            holdings_df['export_date'] = datetime.now().isoformat()

            # Save to CSV
            holdings_df.to_csv(filename, index=False)
            logger.info(f"Portfolio exported to {filename}")
            return True

        except Exception as e:
            logger.error(f"Error exporting portfolio to CSV: {e}")
            return False

# Global instance
portfolio_ingestion = PortfolioDataIngestion()

if __name__ == "__main__":
    # Test the portfolio ingestion
    portfolio = portfolio_ingestion.load_portfolio_data()
    print(f"Loaded portfolio: {portfolio.get('portfolio_name', 'Unknown')}")
    print(f"Total holdings: {len(portfolio.get('holdings', []))}")
    print(f"Total value: ${portfolio.get('total_value', 0):,.2f}")

    # Test adding a holding
    success = portfolio_ingestion.add_holding("TSLA", 10, 250.0, "Tesla Inc.")
    if success:
        print("Successfully added Tesla holding")
        summary = portfolio_ingestion.get_portfolio_summary()
        print(f"Updated total value: ${summary['total_value']:,.2f}")