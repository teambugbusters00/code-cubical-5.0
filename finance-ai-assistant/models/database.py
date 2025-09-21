"""
MongoDB database connection and models for Finance AI Assistant
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import Document, init_beanie
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from config.settings import settings

class StockData(Document):
    """Stock data model"""
    symbol: str = Field(..., description="Stock symbol")
    company_name: str = Field(..., description="Company name")
    price: float = Field(..., description="Current price")
    change: float = Field(..., description="Price change")
    change_percent: float = Field(..., description="Percentage change")
    volume: int = Field(..., description="Trading volume")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    pe_ratio: Optional[float] = Field(None, description="Price to earnings ratio")
    dividend_yield: Optional[float] = Field(None, description="Dividend yield")
    high_52_week: Optional[float] = Field(None, description="52-week high")
    low_52_week: Optional[float] = Field(None, description="52-week low")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data timestamp")

    class Settings:
        name = settings.stocks_collection

class NewsArticle(Document):
    """News article model"""
    title: str = Field(..., description="Article title")
    summary: str = Field(..., description="Article summary")
    content: Optional[str] = Field(None, description="Full article content")
    url: str = Field(..., description="Article URL")
    source: str = Field(..., description="News source")
    published_at: datetime = Field(..., description="Publication date")
    symbols: List[str] = Field(default_factory=list, description="Related stock symbols")
    sentiment: str = Field(..., description="Sentiment analysis (positive/negative/neutral)")
    sentiment_score: float = Field(..., description="Sentiment score (-1 to 1)")
    tags: List[str] = Field(default_factory=list, description="Article tags")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Data timestamp")

    class Settings:
        name = settings.news_collection

class Portfolio(Document):
    """User portfolio model"""
    user_id: str = Field(..., description="User identifier")
    name: str = Field(..., description="Portfolio name")
    holdings: List[Dict[str, Any]] = Field(default_factory=list, description="Stock holdings")
    total_value: float = Field(default=0.0, description="Total portfolio value")
    total_change: float = Field(default=0.0, description="Total change")
    total_change_percent: float = Field(default=0.0, description="Total change percentage")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation date")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update")

    class Settings:
        name = settings.portfolios_collection

class User(Document):
    """User model"""
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    hashed_password: str = Field(..., description="Hashed password")
    is_active: bool = Field(default=True, description="Account status")
    portfolios: List[str] = Field(default_factory=list, description="User portfolios")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Account creation date")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update")

    class Settings:
        name = settings.users_collection
        indexes = [
            "username",
            "email"
        ]

class ChatMessage(Document):
    """Chat message model"""
    user_id: str = Field(..., description="User identifier")
    message: str = Field(..., description="User message")
    response: str = Field(..., description="AI response")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Settings:
        name = settings.chat_history_collection

class TechnicalAnalysis(Document):
    """Technical analysis data model"""
    symbol: str = Field(..., description="Stock symbol")
    analysis_type: str = Field(..., description="Analysis type (RSI, MACD, etc.)")
    data: Dict[str, Any] = Field(..., description="Analysis data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")

    class Settings:
        name = settings.technical_analysis_collection

class DatabaseConnection:
    """MongoDB connection manager"""

    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database = None

    async def connect(self):
        """Initialize database connection"""
        try:
            # Build MongoDB connection string
            if settings.mongodb_username and settings.mongodb_password:
                connection_string = (
                    f"mongodb://{settings.mongodb_username}:{settings.mongodb_password}"
                    f"@{settings.mongodb_url.split('://')[1]}"
                    f"/{settings.mongodb_database}?authSource={settings.mongodb_auth_source}"
                )
            else:
                connection_string = f"mongodb://{settings.mongodb_url}/{settings.mongodb_database}"

            self.client = AsyncIOMotorClient(connection_string)
            self.database = self.client[settings.mongodb_database]

            # Initialize Beanie with the document models
            await init_beanie(
                database=self.client[settings.mongodb_database],  # type: ignore
                document_models=[
                    StockData,
                    NewsArticle,
                    Portfolio,
                    User,
                    ChatMessage,
                    TechnicalAnalysis
                ]
            )

            print(f"✅ Connected to MongoDB: {settings.mongodb_database}")
        except Exception as e:
            print(f"❌ Failed to connect to MongoDB: {e}")
            raise

    async def disconnect(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            print("🔌 Disconnected from MongoDB")

    async def get_database(self):
        """Get database instance"""
        return self.database

    async def health_check(self) -> bool:
        """Check database connection health"""
        try:
            if self.client:
                await self.client.admin.command('ping')
                return True
            return False
        except Exception:
            return False

# Global database connection instance
db_connection = DatabaseConnection()

async def get_database():
    """Dependency injection for database"""
    return await db_connection.get_database()

async def init_database():
    """Initialize database connection"""
    await db_connection.connect()

async def close_database():
    """Close database connection"""
    await db_connection.disconnect()