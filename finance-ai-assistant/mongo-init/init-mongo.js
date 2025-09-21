// MongoDB initialization script for Finance AI Assistant

// Create collections with indexes
db = db.getSiblingDB('finance_ai_assistant');

// Create collections
db.createCollection('stocks');
db.createCollection('news');
db.createCollection('portfolios');
db.createCollection('users');
db.createCollection('chat_history');
db.createCollection('technical_analysis');

// Create indexes for better performance
db.stocks.createIndex({ "symbol": 1, "timestamp": -1 });
db.stocks.createIndex({ "timestamp": -1 });

db.news.createIndex({ "symbols": 1, "published_at": -1 });
db.news.createIndex({ "sentiment": 1 });
db.news.createIndex({ "published_at": -1 });

db.portfolios.createIndex({ "user_id": 1, "updated_at": -1 });

db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true });

db.chat_history.createIndex({ "user_id": 1, "timestamp": -1 });

db.technical_analysis.createIndex({ "symbol": 1, "analysis_type": 1, "timestamp": -1 });

// Insert sample data
print("Inserting sample stock data...");

// Sample stock data
db.stocks.insertMany([
    {
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
        "price": 175.50,
        "change": 2.30,
        "change_percent": 1.33,
        "volume": 45000000,
        "market_cap": 2800000000000,
        "pe_ratio": 28.5,
        "dividend_yield": 0.5,
        "high_52_week": 198.23,
        "low_52_week": 124.17,
        "timestamp": new Date()
    },
    {
        "symbol": "MSFT",
        "company_name": "Microsoft Corporation",
        "price": 378.85,
        "change": -1.20,
        "change_percent": -0.32,
        "volume": 28000000,
        "market_cap": 2800000000000,
        "pe_ratio": 32.1,
        "dividend_yield": 0.7,
        "high_52_week": 420.82,
        "low_52_week": 309.45,
        "timestamp": new Date()
    },
    {
        "symbol": "GOOGL",
        "company_name": "Alphabet Inc.",
        "price": 139.69,
        "change": 0.85,
        "change_percent": 0.61,
        "volume": 22000000,
        "market_cap": 1800000000000,
        "pe_ratio": 25.8,
        "dividend_yield": 0.0,
        "high_52_week": 153.78,
        "low_52_week": 83.45,
        "timestamp": new Date()
    }
]);

print("✅ Sample data inserted successfully!");
print("📊 Collections created:");
print("   - stocks (with indexes)");
print("   - news (with indexes)");
print("   - portfolios (with indexes)");
print("   - users (with indexes)");
print("   - chat_history (with indexes)");
print("   - technical_analysis (with indexes)");