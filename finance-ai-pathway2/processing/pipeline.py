"""
Main Processing Pipeline with Pathway Integration
Handles real-time data processing, streaming, and vector indexing
"""

import pathway as pw
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import asyncio
import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinanceDataPipeline:
    """Main processing pipeline for financial data using Pathway"""

    def __init__(self):
        self.pathway_license_key = os.getenv('PATHWAY_LICENSE_KEY', '')
        self.data_dir = "data"

        # Initialize Pathway tables
        self.stocks_table = None
        self.news_table = None
        self.portfolio_table = None

        # Initialize vector index
        self.vector_index = None

    def setup_pathway_tables(self):
        """Set up Pathway tables for data streaming"""

        # Stocks data table
        self.stocks_table = pw.io.csv.read(
            f"{self.data_dir}/stocks.csv",
            schema=StockSchema,
            mode="streaming"
        )

        # News data table
        self.news_table = pw.io.csv.read(
            f"{self.data_dir}/news.csv",
            schema=NewsSchema,
            mode="streaming"
        )

        # Portfolio data table
        self.portfolio_table = pw.io.csv.read(
            f"{self.data_dir}/portfolio.json",
            schema=PortfolioSchema,
            mode="streaming"
        )

        logger.info("Pathway tables initialized")

    def create_enriched_stocks_table(self):
        """Create enriched stocks table with computed metrics"""
        if not self.stocks_table:
            self.setup_pathway_tables()

        # Add computed columns
        enriched_stocks = self.stocks_table.select(
            symbol=pw.this.symbol,
            name=pw.this.name,
            sector=pw.this.sector,
            price=pw.this.price,
            change=pw.this.change,
            change_percent=pw.this.change_percent,
            volume=pw.this.volume,
            market_cap=pw.this.market_cap,
            pe_ratio=pw.this.pe_ratio,
            dividend_yield=pw.this.dividend_yield,
            high_52w=pw.this.high_52w,
            low_52w=pw.this.low_52w,
            # Computed metrics
            price_to_book_ratio=pw.this.market_cap / (pw.this.price * pw.this.volume / 1000000),  # Simplified
            volatility_score=pw.this.change_percent.abs() * 10,  # Simple volatility measure
            momentum_score=pw.this.change_percent * 100,  # Momentum indicator
            value_score=pw.apply(lambda x, y: 1/x if x > 0 else 0, pw.this.pe_ratio, pw.this.dividend_yield),  # Value indicator
            timestamp=pw.this.time
        )

        return enriched_stocks

    def create_enriched_news_table(self):
        """Create enriched news table with sentiment analysis and embeddings"""
        if not self.news_table:
            self.setup_pathway_tables()

        # Add computed columns for news
        enriched_news = self.news_table.select(
            symbol=pw.this.symbol,
            title=pw.this.title,
            summary=pw.this.summary,
            published_at=pw.this.published_at,
            sentiment_score=pw.this.sentiment_score,
            sentiment_label=pw.this.sentiment_label,
            url=pw.this.url,
            source=pw.this.source,
            # Computed metrics
            relevance_score=pw.this.sentiment_score.abs() * 10,  # How relevant the news is
            urgency_score=pw.apply(self._calculate_urgency_score, pw.this.published_at),  # How recent
            impact_score=pw.this.sentiment_score * pw.this.relevance_score,  # Overall impact
            # Text for embedding (combine title and summary)
            text_for_embedding=pw.this.title + " " + pw.this.summary,
            timestamp=pw.this.time
        )

        return enriched_news

    def _calculate_urgency_score(self, published_at: str) -> float:
        """Calculate urgency score based on how recent the news is"""
        try:
            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            hours_old = (datetime.now() - pub_date.replace(tzinfo=None)).total_seconds() / 3600

            if hours_old < 1:
                return 1.0  # Very recent
            elif hours_old < 24:
                return 0.8  # Today
            elif hours_old < 168:  # 7 days
                return 0.6  # This week
            else:
                return 0.3  # Older
        except:
            return 0.5  # Default score

    def create_portfolio_analysis_table(self):
        """Create portfolio analysis table with risk metrics"""
        if not self.portfolio_table:
            self.setup_pathway_tables()

        # Join portfolio with stocks data for real-time analysis
        portfolio_analysis = self.portfolio_table.join(
            self.stocks_table,
            pw.left.symbol == pw.right.symbol,
            "left_join"
        ).select(
            user_id=pw.left.user_id,
            portfolio_name=pw.left.portfolio_name,
            symbol=pw.left.symbol,
            company_name=pw.left.company_name,
            shares=pw.left.shares,
            avg_cost=pw.left.avg_cost,
            current_price=pw.right.price,
            market_value=pw.left.shares * pw.right.price,
            gain_loss=(pw.right.price - pw.left.avg_cost) * pw.left.shares,
            gain_loss_percent=((pw.right.price / pw.left.avg_cost) - 1) * 100,
            sector=pw.right.sector,
            weight=(pw.left.shares * pw.right.price) / pw.left.total_value * 100,
            # Risk metrics
            volatility_risk=pw.right.change_percent.abs() * 10,
            sector_diversification_score=pw.apply(self._calculate_diversification_score, pw.right.sector),
            timestamp=pw.this.time
        )

        return portfolio_analysis

    def _calculate_diversification_score(self, sector: str) -> float:
        """Calculate diversification score for a sector"""
        # This would typically use more sophisticated logic
        # For now, return a simple score based on sector concentration
        sector_weights = {
            'Technology': 0.8,
            'Financial Services': 0.7,
            'Healthcare': 0.9,
            'Consumer Discretionary': 0.6,
            'Consumer Staples': 0.8,
            'Energy': 0.5,
            'Materials': 0.4,
            'Utilities': 0.7,
            'Real Estate': 0.6,
            'Communication Services': 0.7,
            'Industrials': 0.6
        }
        return sector_weights.get(sector, 0.5)

    def setup_vector_index(self):
        """Set up vector index for news articles"""
        if not self.news_table:
            self.setup_pathway_tables()

        # Create embeddings for news articles
        # Note: This would typically use a proper embedding model
        # For demonstration, we'll use a simple text vectorization

        def create_text_embedding(text: str) -> List[float]:
            """Create simple text embedding (placeholder for real embedding model)"""
            # This is a simplified version - in production, use proper embeddings
            words = text.lower().split()[:50]  # Take first 50 words
            # Create a simple hash-based vector
            vector = []
            for i in range(384):  # Common embedding dimension
                hash_val = hash(f"{text}_{i}") % 1000 / 1000.0
                vector.append(hash_val)
            return vector

        # Create vector index table
        vectorized_news = self.news_table.select(
            id=pw.this.id,
            symbol=pw.this.symbol,
            title=pw.this.title,
            summary=pw.this.summary,
            embedding=pw.apply(create_text_embedding, pw.this.title + " " + pw.this.summary),
            sentiment_score=pw.this.sentiment_score,
            published_at=pw.this.published_at,
            timestamp=pw.this.time
        )

        # Set up the vector index
        self.vector_index = pw.index.VectorIndex(
            vectorized_news.embedding,
            vectorized_news,
            n_dimensions=384,
            metric=pw.index.VectorIndexMetric.COSINE
        )

        logger.info("Vector index setup completed")

    def run_pipeline(self):
        """Run the complete processing pipeline"""
        try:
            logger.info("Starting Finance Data Pipeline...")

            # Set up tables
            self.setup_pathway_tables()

            # Create enriched tables
            enriched_stocks = self.create_enriched_stocks_table()
            enriched_news = self.create_enriched_news_table()
            portfolio_analysis = self.create_portfolio_analysis_table()

            # Set up vector index
            self.setup_vector_index()

            # Output tables for monitoring
            pw.io.csv.write(enriched_stocks, f"{self.data_dir}/processed_stocks.csv")
            pw.io.csv.write(enriched_news, f"{self.data_dir}/processed_news.csv")
            pw.io.csv.write(portfolio_analysis, f"{self.data_dir}/portfolio_analysis.csv")

            logger.info("Pipeline running successfully")
            logger.info("Data will be processed in real-time as new files are added")

            # Run the pipeline
            pw.run()

        except Exception as e:
            logger.error(f"Error running pipeline: {e}")
            raise

    def get_real_time_stats(self) -> Dict[str, Any]:
        """Get real-time pipeline statistics"""
        try:
            if not all([self.stocks_table, self.news_table, self.portfolio_table]):
                self.setup_pathway_tables()

            # Get basic statistics
            stats = {
                'pipeline_status': 'running',
                'last_updated': datetime.now().isoformat(),
                'stocks_count': len(self.stocks_table) if self.stocks_table else 0,
                'news_count': len(self.news_table) if self.news_table else 0,
                'portfolio_count': len(self.portfolio_table) if self.portfolio_table else 0,
                'vector_index_ready': self.vector_index is not None
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting pipeline stats: {e}")
            return {'pipeline_status': 'error', 'error': str(e)}

# Pathway schemas
class StockSchema(pw.Schema):
    symbol: str
    name: str
    sector: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: float
    pe_ratio: float
    dividend_yield: float
    high_52w: float
    low_52w: float

class NewsSchema(pw.Schema):
    symbol: str
    title: str
    summary: str
    published_at: str
    sentiment_score: float
    sentiment_label: str
    url: str
    source: str

class PortfolioSchema(pw.Schema):
    user_id: str
    portfolio_name: str
    symbol: str
    company_name: str
    shares: float
    avg_cost: float
    total_value: float

# Global pipeline instance
pipeline = FinanceDataPipeline()

if __name__ == "__main__":
    # Test the pipeline
    try:
        stats = pipeline.get_real_time_stats()
        print("Pipeline Status:", stats)

        # Run the pipeline (this will run indefinitely)
        print("Starting pipeline...")
        pipeline.run_pipeline()

    except KeyboardInterrupt:
        print("Pipeline stopped by user")
    except Exception as e:
        print(f"Pipeline error: {e}")