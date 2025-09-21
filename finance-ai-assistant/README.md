# 🚀 Enhanced Finance AI Assistant

A comprehensive, enterprise-grade financial data analysis and visualization platform with real-time streaming, AI-powered predictions, and multi-source data integration.

## ✨ Key Features

### 🔴 **Real-Time Data Streaming**
- **WebSocket Integration**: Live stock price updates via WebSocket connections
- **Multi-Source Aggregation**: Yahoo Finance, Alpha Vantage, and RapidAPI integration
- **Auto-Reconnection**: Automatic reconnection with exponential backoff
- **Market Indices**: Real-time S&P 500, NASDAQ, Dow Jones streaming

### 🤖 **AI-Powered Analytics**
- **Price Predictions**: 7-day stock price forecasting using machine learning
- **Technical Analysis**: RSI, MACD, Bollinger Bands, Moving Averages
- **Sentiment Analysis**: News sentiment scoring with TextBlob
- **Trend Detection**: Automated bullish/bearish trend identification

### 📊 **Advanced Data Sources**
- **Yahoo Finance** (yfinance) - Primary data source
- **Alpha Vantage** - Professional financial data API
- **RapidAPI Yahoo Finance** - Real-time market data
- **News API** - Financial news and sentiment analysis
- **Intelligent Fallback** - Automatic switching between data sources

### 🌐 **Interactive Dashboards**
- **React Frontend**: Modern, responsive dashboard with real-time updates
- **Streamlit Analytics**: Advanced data visualization and analysis
- **Technical Indicators**: Live RSI, MACD, volume analysis
- **Portfolio Tracking**: Multi-asset portfolio management

## 🚀 Features

### Core Components
- **FastAPI Backend**: RESTful API for financial data with Yahoo Finance integration
- **Pathway Data Processing**: Real-time data streaming and analysis pipeline
- **Streamlit Frontend**: Interactive web dashboard for data visualization
- **Technical Analysis**: RSI, Moving Averages, Bollinger Bands, and trend analysis
- **Market Overview**: Real-time market indices and stock information
- **Portfolio Tracking**: Stock portfolio management and performance analysis

### Key Capabilities
- 📊 Real-time stock price data from Yahoo Finance
- 📈 Interactive price charts with candlestick visualization
- 🔍 Stock search and filtering functionality
- 📱 Responsive web interface
- 🔧 Technical indicators and market analysis
- 📱 RESTful API for external integrations
- 🐳 Docker containerization support

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.8+)
- **Data Processing**: Pathway
- **Frontend**: Streamlit
- **Data Sources**: Yahoo Finance, Alpha Vantage
- **Visualization**: Plotly, Matplotlib
- **Database**: MongoDB (primary), PostgreSQL (optional)
- **Cache**: Redis (optional)
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Git
- Docker and Docker Compose (optional, for containerized deployment)

## 🚀 Quick Start

### Option 1: Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finance-ai-assistant
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env .env.local
   # Edit .env.local with your configuration
   ```

5. **Run the components**

   **Start FastAPI Backend:**
   ```bash
   cd backend
   python app.py
   ```
   Backend will be available at: http://localhost:8000

   **Start Streamlit Frontend:**
   ```bash
   cd frontend
   streamlit run app.py
   ```
   Frontend will be available at: http://localhost:8501

   **Start Pathway Data Processing:**
   ```bash
   cd data_processing
   python financial_pipeline.py
   ```
   Pathway service will be available at: http://localhost:8765

### Option 2: Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the applications**
   - Frontend: http://localhost:8501
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📖 Usage Guide

### Using the Streamlit Dashboard

1. **Market Overview**
   - View real-time market indices (S&P 500, NASDAQ, Dow Jones)
   - Monitor major market movements

2. **Stock Analysis**
   - Search for stocks by name or symbol
   - View detailed stock information
   - Analyze price charts with technical indicators
   - Review technical analysis (RSI, Moving Averages)

3. **Portfolio Tracker**
   - Add stocks to your watchlist
   - Track portfolio performance
   - View allocation and risk metrics

### API Usage

The FastAPI backend provides RESTful endpoints for programmatic access:

#### Stock Information
```bash
# Get stock info
GET /api/stocks/{symbol}/info

# Get current quote
GET /api/stocks/{symbol}/quote

# Get historical data
GET /api/stocks/{symbol}/history?period=1y&interval=1d

# Get technical analysis
GET /api/stocks/{symbol}/analysis

# Search stocks
GET /api/stocks/search?query=Apple&limit=10
```

#### Market Data
```bash
# Get market indices
GET /api/market/indices
```

### Example API Calls

```python
import requests

# Get Apple stock info
response = requests.get("http://localhost:8000/api/stocks/AAPL/info")
print(response.json())

# Search for technology stocks
response = requests.get("http://localhost:8000/api/stocks/search?query=tech&limit=5")
print(response.json())
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Frontend Configuration
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=8501

# External API Keys
ALPHA_VANTAGE_API_KEY=your_key_here
NEWS_API_KEY=your_key_here

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=finance_ai_assistant
MONGODB_USERNAME=your_mongodb_username
MONGODB_PASSWORD=your_mongodb_password
MONGODB_AUTH_SOURCE=admin

# Database Settings
ENABLE_MONGODB=true
ENABLE_MONGODB_PERSISTENCE=true

# Feature Flags
ENABLE_REAL_TIME_UPDATES=true
ENABLE_TECHNICAL_ANALYSIS=true
```

### Settings

Configuration is managed through the `config/settings.py` file. Key settings include:

- **Data Sources**: Enable/disable Yahoo Finance, Alpha Vantage
- **Cache Settings**: Redis configuration and TTL
- **Security**: CORS origins and secret keys
- **Feature Flags**: Enable/disable specific features

## 🗄️ MongoDB Integration

The application uses MongoDB as the primary database for persistent data storage.

### MongoDB Features

- **Stock Data Storage**: Real-time stock prices and historical data
- **News Articles**: Financial news with sentiment analysis
- **Portfolio Management**: User portfolios and holdings
- **Chat History**: Conversation history for the AI assistant
- **Technical Analysis**: Calculated indicators and analysis results
- **User Management**: User accounts and authentication

### MongoDB Setup

#### Option 1: Docker (Recommended)

MongoDB is included in the Docker Compose setup:

```bash
docker-compose up mongodb
```

MongoDB will be available at: `mongodb://localhost:27017`

#### Option 2: Local Installation

1. **Install MongoDB** (Ubuntu/Debian):
   ```bash
   sudo apt-get install mongodb
   sudo systemctl start mongodb
   sudo systemctl enable mongodb
   ```

2. **Install MongoDB** (macOS with Homebrew):
   ```bash
   brew install mongodb-community
   brew services start mongodb-community
   ```

3. **Verify Installation**:
   ```bash
   mongo --eval "db.adminCommand('ismaster')"
   ```

### Database Collections

The application uses the following MongoDB collections:

- **`stocks`**: Stock price data and company information
- **`news`**: Financial news articles with sentiment analysis
- **`portfolios`**: User portfolios and investment holdings
- **`users`**: User accounts and authentication data
- **`chat_history`**: AI assistant conversation history
- **`technical_analysis`**: Technical indicators and analysis results

### MongoDB API Endpoints

#### Stock Data
```bash
# Get stock history from database
GET /api/stocks/{symbol}/history-db?limit=100

# Create portfolio
POST /api/portfolios
Content-Type: application/json

{
  "user_id": "user123",
  "name": "My Portfolio",
  "holdings": [{"symbol": "AAPL", "shares": 10}],
  "total_value": 10000.0
}

# Get user portfolios
GET /api/portfolios/{user_id}
```

### MongoDB Configuration

Configure MongoDB connection in your `.env` file:

```env
# MongoDB Settings
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=finance_ai_assistant
MONGODB_USERNAME=admin
MONGODB_PASSWORD=password123
MONGODB_AUTH_SOURCE=admin

# Enable MongoDB features
ENABLE_MONGODB=true
ENABLE_MONGODB_PERSISTENCE=true
```

### Database Management

#### Backup Database
```bash
mongodump --db finance_ai_assistant --out backup/
```

#### Restore Database
```bash
mongorestore --db finance_ai_assistant backup/finance_ai_assistant/
```

#### Check Database Status
```bash
# Connect to MongoDB shell
mongo

# Switch to finance database
use finance_ai_assistant

# List collections
show collections

# Check document count
db.stocks.count()
db.news.count()
```

## 📊 Data Processing Pipeline

The Pathway data processing pipeline provides:

- **Real-time Data Streaming**: Continuous data ingestion from financial sources
- **Technical Indicators**: Automated calculation of RSI, MA, Bollinger Bands
- **Market Sentiment Analysis**: Price movement and trend analysis
- **Alert System**: Automated alerts for significant market events

### Running the Pipeline

```bash
cd data_processing
python financial_pipeline.py
```

## 🐳 Docker Deployment

### Development Environment
```bash
docker-compose -f docker-compose.yml up --build
```

### Production Environment
```bash
# Use production configuration
docker-compose -f docker-compose.prod.yml up -d
```

## 🧪 Testing

Run tests for individual components:

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
python -m pytest

# Data processing tests
cd data_processing
python -m pytest
```

## 📈 Monitoring and Logging

- **Application Logs**: Stored in `logs/` directory
- **Health Checks**: Available at `/health` endpoint
- **Metrics**: Performance monitoring and error tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:

- 📧 Email: support@financeai.com
- 📖 Documentation: [Link to docs]
- 🐛 Bug Reports: [GitHub Issues]
- 💬 Discussions: [GitHub Discussions]

## 🔄 Updates and Maintenance

### Regular Updates
- Dependencies are updated monthly
- Security patches applied immediately
- Performance optimizations as needed

### Backup and Recovery
- Database backups: Daily at 2 AM
- Configuration backups: Version controlled
- Log rotation: Weekly

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Basic stock analysis
- ✅ Real-time data integration
- ✅ Interactive dashboard

### Phase 2 (Next)
- 🔄 Advanced technical indicators
- 🔄 Portfolio optimization
- 🔄 News sentiment analysis
- 🔄 Machine learning predictions

### Phase 3 (Future)
- 🔄 Options and derivatives analysis
- 🔄 Social trading features
- 🔄 Mobile application
- 🔄 Multi-language support

---

**Built with ❤️ using Pathway, FastAPI, and Streamlit**

For more information, visit our [documentation](docs/) or [GitHub repository](https://github.com/your-org/finance-ai-assistant).

---

# 📊 Complete Workflow & Architecture Diagrams

## 🏗️ **1. System Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FINANCE AI ASSISTANT                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │   WEB UI    │    │  MOBILE APP │    │   API GATEWAY   │    │  ADMIN UI   │   │
│  │ Streamlit   │    │   React.js  │    │   FastAPI       │    │   Panel     │   │
│  │ Dashboard   │    │             │    │                 │    │             │   │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘   │
│         │                   │                   │                   │         │
│         └───────────────────┼───────────────────┼───────────────────┘         │
│                             │                   │                             │
│                    ┌────────▼────────┐          │                             │
│                    │  FASTAPI BACKEND │         │                             │
│                    │  (Port: 8000)   │─────────┘                             │
│                    └────────┬────────┘                                      │
│                             │                                               │
│                    ┌────────▼────────┐                                      │
│                    │  DATA SOURCES   │                                      │
│                    │  MANAGEMENT     │                                      │
│                    └────────┬────────┘                                      │
│                             │                                               │
│               ┌─────────────▼─────────────┐                                 │
│               │   MULTI-SOURCE DATA       │                                 │
│               │   FETCHING SYSTEM        │                                 │
│               │                          │                                 │
│               │ • Yahoo Finance (yfinance)│                                 │
│               │ • Alpha Vantage API       │                                 │
│               │ • RapidAPI Yahoo Finance  │                                 │
│               │ • Fallback Mechanisms     │                                 │
│               └─────────────┬─────────────┘                                 │
│                             │                                               │
│               ┌─────────────▼─────────────┐                                 │
│               │   CACHING LAYER          │                                 │
│               │                          │                                 │
│               │ • Redis Cache            │                                 │
│               │ • In-Memory Cache        │                                 │
│               │ • TTL Management         │                                 │
│               └─────────────┬─────────────┘                                 │
│                             │                                               │
│               ┌─────────────▼─────────────┐                                 │
│               │   DATABASE LAYER         │                                 │
│               │                          │                                 │
│               │ • MongoDB (Primary)      │                                 │
│               │ • PostgreSQL (Optional)  │                                 │
│               │ • Data Persistence       │                                 │
│               └─────────────┬─────────────┘                                 │
│                             │                                               │
│               ┌─────────────▼─────────────┐                                 │
│               │   REAL-TIME PROCESSING   │                                 │
│               │                          │                                 │
│               │ • Pathway Pipeline       │                                 │
│               │ • WebSocket Streaming    │                                 │
│               │ • Live Data Updates      │                                 │
│               └─────────────┬─────────────┘                                 │
│                             │                                               │
│               ┌─────────────▼─────────────┐                                 │
│               │   AI/ML PROCESSING       │                                 │
│               │                          │                                 │
│               │ • Price Predictions      │                                 │
│               │ • Technical Analysis     │                                 │
│               │ • Sentiment Analysis     │                                 │
│               └──────────────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 **2. Data Flow Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATA FLOW WORKFLOW                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  USER REQUEST → FRONTEND → BACKEND → DATA SOURCES → PROCESSING → RESPONSE │
│                                                                             │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐   │
│  │  USER   │───▶│STREAMLIT│───▶│ FASTAPI │───▶│  DATA   │───▶│PATHWAY  │──▶│
│  │INTERFACE│    │ DASH-   │    │ BACKEND │    │SOURCES  │    │PIPELINE │   │
│  │         │◀───│ BOARD   │◀───│         │◀───│         │◀───│         │◀──│
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘   │
│                                                                             │
│  Detailed Flow:                                                             │
│  1. User searches for stock symbol                                          │
│  2. Frontend sends request to FastAPI backend                               │
│  3. Backend checks cache first                                              │
│  4. If cache miss, queries multiple data sources                           │
│  5. Data sources return raw financial data                                 │
│  6. Pathway pipeline processes real-time data                              │
│  7. AI/ML models generate predictions and analysis                         │
│  8. Results cached and sent back to frontend                              │
│  9. Frontend displays interactive charts and metrics                       │
│  10. WebSocket connection maintains real-time updates                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔗 **3. Component Interaction Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      COMPONENT INTERACTION DIAGRAM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   STREAMLIT     │    │   FASTAPI       │    │   PATHWAY       │          │
│  │   FRONTEND      │    │   BACKEND       │    │   PROCESSING    │          │
│  │                 │    │                 │    │                 │          │
│  │ • Dashboard     │    │ • REST API      │    │ • Data Stream   │          │
│  │ • Charts        │    │ • Data Fetching │    │ • Real-time     │          │
│  │ • User Input    │    │ • Caching       │    │ • Analysis      │          │
│  │ • Real-time UI  │    │ • WebSocket     │    │ • Indicators    │          │
│  └───────┬─────────┘    └───────┬─────────┘    └───────┬─────────┘          │
│          │                     │                     │                      │
│          │ HTTP/REST           │ WebSocket/HTTP      │ Message Queue        │
│          │ Requests            │ Communication       │ (Internal)           │
│          ▼                     ▼                     ▼                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   REDIS CACHE   │    │   MONGODB       │    │   EXTERNAL APIs │          │
│  │                 │    │   DATABASE      │    │                 │          │
│  │ • Fast Access   │    │ • Persistence   │    │ • Yahoo Finance │          │
│  │ • TTL Management│    │ • Stock Data    │    │ • Alpha Vantage │          │
│  │ • Session Data  │    │ • User Data     │    │ • RapidAPI      │          │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘          │
│                                                                             │
│  Interaction Patterns:                                                      │
│  • Frontend ↔ Backend: HTTP REST API calls                                  │
│  • Backend ↔ Cache: Redis for fast data access                             │
│  • Backend ↔ Database: MongoDB for persistent storage                     │
│  • Backend ↔ External APIs: Multiple data source integration               │
│  • Backend ↔ Pathway: Real-time data processing pipeline                   │
│  • Frontend ↔ Backend: WebSocket for live updates                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 👤 **4. User Journey Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            USER JOURNEY FLOW                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  START → Market Overview → Stock Search → Analysis → Real-time Monitoring │
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   1. HOME PAGE  │───▶│ 2. MARKET       │───▶│ 3. STOCK        │───▶│     │
│  │                 │    │    OVERVIEW     │    │    SEARCH       │    │     │
│  │ • Welcome Screen│    │ • Indices Display│    │ • Symbol Input   │    │     │
│  │ • Navigation    │    │ • Real-time Data│    │ • Auto-complete  │    │     │
│  │ • Quick Access  │    │ • Market Trends │    │ • Filter Options │    │     │
│  └───────┬─────────┘    └───────┬─────────┘    └───────┬─────────┘          │
│          │                     │                     │                      │
│          ▼                     ▼                     ▼                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   4. STOCK      │    │ 5. TECHNICAL    │    │ 6. REAL-TIME    │───▶│ END │
│  │    ANALYSIS     │    │    ANALYSIS     │    │   MONITORING    │    │     │
│  │                 │    │                 │    │                 │    │     │
│  │ • Price Charts  │    │ • RSI, MACD     │    │ • Live Updates  │    │     │
│  │ • Historical    │    │ • Bollinger     │    │ • WebSocket     │    │     │
│  │ • Volume Data   │    │ • Trend Analysis│    │ • Alerts        │    │     │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘          │
│                                                                             │
│  User Actions:                                                              │
│  • Browse market indices and trends                                         │
│  • Search for specific stocks by name/symbol                                │
│  • View detailed price charts and historical data                          │
│  • Analyze technical indicators and patterns                               │
│  • Set up real-time monitoring and alerts                                  │
│  • Export data and generate reports                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🗄️ **5. Database Schema Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DATABASE SCHEMA DESIGN                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │    STOCKS       │    │     NEWS        │    │   PORTFOLIOS    │          │
│  │   COLLECTION    │    │   COLLECTION    │    │   COLLECTION    │          │
│  │                 │    │                 │    │                 │          │
│  │ • symbol        │    │ • title         │    │ • user_id       │          │
│  │ • company_name  │    │ • content       │    │ • portfolio_name│          │
│  │ • current_price │    │ • published_at  │    │ • holdings      │          │
│  │ • market_cap    │    │ • sentiment     │    │ • total_value   │          │
│  │ • pe_ratio      │    │ • source        │    │ • performance   │          │
│  │ • volume        │    │ • url           │    │ • risk_metrics  │          │
│  │ • sector        │    │ • tickers       │    │ • allocation    │          │
│  │ • industry      │    │ • relevance     │    │ • transactions  │          │
│  └───────┬─────────┘    └───────┬─────────┘    └───────┬─────────┘          │
│          │                     │                     │                      │
│          ▼                     ▼                     ▼                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   TECHNICAL     │    │     USERS       │    │   CHAT_HISTORY  │          │
│  │    ANALYSIS     │    │   COLLECTION    │    │   COLLECTION    │          │
│  │   COLLECTION    │    │                 │    │                 │          │
│  │                 │    │ • user_id       │    │ • user_id       │          │
│  │ • symbol        │    │ • username      │    │ • message_id    │          │
│  │ • rsi           │    │ • email         │    │ • user_message  │          │
│  │ • macd          │    │ • password_hash │    │ • ai_response   │          │
│  │ • bollinger     │    │ • preferences   │    │ • timestamp     │          │
│  │ • sma_20        │    │ • created_at    │    │ • conversation_id│         │
│  │ • sma_50        │    │ • last_login    │    │ • context       │          │
│  │ • trend         │    │ • api_keys      │    │ • feedback      │          │
│  │ • support_resist│    │ • subscription  │    │ • rating        │          │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘          │
│                                                                             │
│  Relationships:                                                             │
│  • Users can have multiple portfolios                                       │
│  • Portfolios contain multiple stock holdings                              │
│  • Technical analysis linked to specific stocks                            │
│  • News articles can reference multiple stocks                             │
│  • Chat history maintains conversation context                             │
│  • All collections include timestamps for audit trails                     │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🌐 **6. API Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           API ARCHITECTURE DIAGRAM                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   PUBLIC APIs   │    │  INTERNAL APIs  │    │  WEBSOCKET APIs │          │
│  │                 │    │                 │    │                 │          │
│  │ /api/stocks     │    │ /admin/*        │    │ /ws/stocks      │          │
│  │ /api/market     │    │ /health         │    │ /ws/market      │          │
│  │ /api/news       │    │ /metrics        │    │ /ws/alerts      │          │
│  │ /api/analysis   │    │ /debug          │    │                 │          │
│  └───────┬─────────┘    └───────┬─────────┘    └───────┬─────────┘          │
│          │                     │                     │                      │
│          ▼                     ▼                     ▼                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   RATE LIMITING │    │ AUTHENTICATION  │    │  INPUT VALIDATION│         │
│  │   & THROTTLING  │    │   & AUTHORIZATION│   │   & SANITIZATION │         │
│  │                 │    │                 │    │                  │         │
│  │ • 100 req/min   │    │ • JWT Tokens    │    │ • Pydantic Models│         │
│  │ • Burst limits  │    │ • API Keys      │    │ • Data Types     │         │
│  │ • User tiers    │    │ • Role-based    │    │ • Required Fields│         │
│  │ • Fair usage    │    │ • Rate limits   │    │ • Format Checks  │         │
│  └───────┬─────────┘    └───────┬─────────┘    └───────┬─────────┘          │
│          │                     │                     │                      │
│          ▼                     ▼                     ▼                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   BUSINESS      │    │   DATA ACCESS   │    │   RESPONSE      │          │
│  │    LOGIC LAYER  │    │     LAYER       │    │    FORMATTING   │          │
│  │                 │    │                 │    │                 │          │
│  │ • Stock Analysis│    │ • Database      │    │ • JSON Response │          │
│  │ • Predictions   │    │ • Cache         │    │ • Error Handling│          │
│  │ • Calculations  │    │ • External APIs │    │ • Status Codes  │          │
│  │ • Validations   │    │ • File System   │    │ • Headers       │          │
│  └───────┬─────────┘    └───────┬─────────┘    └───────┬─────────┘          │
│          │                     │                     │                      │
│          ▼                     ▼                     ▼                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   ERROR         │    │   LOGGING &     │    │   MONITORING    │          │
│  │   HANDLING      │    │   MONITORING    │    │   & ANALYTICS   │          │
│  │                 │    │                 │    │                 │          │
│  │ • Try/Catch     │    │ • Request Logs  │    │ • Performance   │          │
│  │ • Custom Errors │    │ • Error Tracking│    │ • Usage Stats   │          │
│  │ • HTTP Status   │    │ • Performance   │    │ • Error Rates   │          │
│  │ • User Messages │    │ • Audit Trails  │    │ • API Metrics   │          │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🚀 **7. Deployment Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DEPLOYMENT ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   LOAD BALANCER │    │   WEB SERVERS   │    │  BACKGROUND     │          │
│  │   (NGINX)       │    │   (GUNICORN)    │    │   WORKERS       │          │
│  │                 │    │                 │    │                 │          │
│  │ • SSL/TLS       │    │ • Auto-scaling  │    │ • Data Processing│         │
│  │ • Health Checks │    │ • Load Balancing│    │ • Batch Jobs    │          │
│  │ • Rate Limiting │    │ • SSL Termination│   │ • Scheduled Tasks│         │
│  │ • CDN Integration│   │ • Request Routing│   │ • Queue Workers │          │
│  └───────┬─────────┘    └───────┬─────────┘    └───────┬─────────┘          │
│          │                     │                     │                      │
│          ▼                     ▼                     ▼                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   APPLICATION   │    │   REDIS CACHE   │    │   MONGODB       │          │
│  │    SERVERS      │    │   CLUSTER       │    │   CLUSTER       │          │
│  │                 │    │                 │    │                 │          │
│  │ • FastAPI Apps  │    │ • Session Store │    │ • Primary DB    │          │
│  │ • WebSocket     │    │ • Cache Layer   │    │ • Replica Sets  │          │
│  │ • API Endpoints │    │ • Rate Limiting │    │ • Sharding      │          │
│  │ • File Uploads  │    │ • Distributed   │    │ • Backup/Recovery│         │
│  └───────┬─────────┘    └───────┬─────────┘    └───────┬─────────┘          │
│          │                     │                     │                      │
│          ▼                     ▼                     ▼                      │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   MESSAGE QUEUE │    │   FILE STORAGE  │    │   EXTERNAL APIs │          │
│  │   (RABBITMQ)    │    │   (S3/MINIO)    │    │                 │          │
│  │                 │    │                 │    │ • Yahoo Finance │          │
│  │ • Task Queue    │    │ • Static Files  │    │ • Alpha Vantage │          │
│  │ • Job Scheduling│    │ • User Uploads  │    │ • RapidAPI      │          │
│  │ • Event Driven  │    │ • Reports       │    │ • News APIs     │          │
│  │ • Async Tasks   │    │ • Backups       │    │ • Market Data   │          │
│  └─────────────────┘    └─────────────────┘    └─────────────────┘          │
│                                                                             │
│  Deployment Flow:                                                           │
│  1. User requests hit load balancer                                         │
│  2. Load balancer distributes to application servers                        │
│  3. Application servers handle requests and WebSocket connections           │
│  4. Redis provides fast caching and session management                     │
│  5. MongoDB stores persistent data with replication                        │
│  6. Background workers process heavy tasks asynchronously                  │
│  7. File storage handles uploads and static assets                         │
│  8. External APIs provide real-time market data                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 **8. Real-time Data Processing Flow**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     REAL-TIME DATA PROCESSING FLOW                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DATA INGESTION → PROCESSING → ANALYSIS → DISTRIBUTION → STORAGE          │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │  DATA       │───▶│  PATHWAY    │───▶│  AI/ML      │───▶│  WEBSOCKET  │──▶│
│  │  INGESTION  │    │  PROCESSING │    │  ANALYSIS   │    │  BROADCAST  │   │
│  │             │    │  PIPELINE   │    │  ENGINE     │    │             │   │
│  │ • Yahoo API │    │             │    │             │    │ • Live Data │   │
│  │ • Alpha V   │    │ • Real-time │    │ • Predictions│    │ • Real-time │   │
│  │ • RapidAPI  │    │ • Streaming  │    │ • Indicators │    │ • Updates   │   │
│  │ • WebSocket │    │ • Filtering  │    │ • Sentiment  │    │ • Alerts    │   │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘   │
│         │                   │                   │                   │         │
│         └───────────────────┼───────────────────┼───────────────────┘         │
│                             │                   │                             │
│                    ┌────────▼────────┐          │                             │
│                    │  REDIS CACHE    │         │                             │
│                    │                 │         │                             │
│                    │ • Fast Access   │         │                             │
│                    │ • TTL Management│         │                             │
│                    │ • Data Buffering│         │                             │
│                    └────────┬────────┘                                      │
│                             │                                               │
│                    ┌────────▼────────┐                                      │
│                    │  MONGODB        │                                      │
│                    │  DATABASE       │                                      │
│                    │                 │                                      │
│                    │ • Persistence   │                                      │
│                    │ • Historical    │                                      │
│                    │ • Analytics     │                                      │
│                    └─────────────────┘                                      │
│                                                                             │
│  Processing Steps:                                                          │
│  1. Data ingestion from multiple sources                                    │
│  2. Real-time processing through Pathway pipeline                           │
│  3. AI/ML analysis for predictions and indicators                          │
│  4. WebSocket broadcast to connected clients                               │
│  5. Caching for fast access                                                │
│  6. Database storage for persistence and analytics                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 📊 **9. Error Handling & Recovery Flow**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ERROR HANDLING & RECOVERY FLOW                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ERROR DETECTION → ANALYSIS → RECOVERY → NOTIFICATION → PREVENTION        │
│                                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐   │
│  │  ERROR      │───▶│  ERROR      │───▶│  RECOVERY   │───▶│  ALERTS &   │──▶│
│  │  DETECTION  │    │  ANALYSIS   │    │  ACTIONS    │    │  NOTIFICATION│   │
│  │             │    │             │    │             │    │             │   │
│  │ • API Fail  │    │ • Root Cause │    │ • Fallback  │    │ • Email     │   │
│  │ • DB Errors │    │ • Impact    │    │ • Retry     │    │ • Slack     │   │
│  │ • Cache Miss│    │ • Priority  │    │ • Circuit   │    │ • Dashboard │   │
│  │ • Timeout   │    │ • Pattern   │    │ • Graceful  │    │ • Logs      │   │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘   │
│         │                   │                   │                   │         │
│         └───────────────────┼───────────────────┼───────────────────┘         │
│                             │                   │                             │
│                    ┌────────▼────────┐          │                             │
│                    │  LOGGING &      │         │                             │
│                    │  MONITORING     │         │                             │
│                    │                 │         │                             │
│                    │ • Structured    │         │                             │
│                    │ • Centralized   │         │                             │
│                    │ • Performance   │         │                             │
│                    └────────┬────────┘                                      │
│                             │                                               │
│                    ┌────────▼────────┐                                      │
│                    │  PREVENTION     │                                      │
│                    │  MEASURES       │                                      │
│                    │                 │                                      │
│                    │ • Rate Limits   │                                      │
│                    │ • Circuit       │                                      │
│                    │ • Health Checks │                                      │
│                    └─────────────────┘                                      │
│                                                                             │
│  Recovery Strategies:                                                       │
│  • Automatic retry with exponential backoff                                 │
│  • Fallback to alternative data sources                                    │
│  • Circuit breaker pattern for failing services                           │
│  • Graceful degradation of features                                       │
│  • Database connection pooling and retry logic                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 🎯 **10. Application Workflow Summary**

### **Complete Request Flow:**
1. **User Interface** → Streamlit Dashboard
2. **API Gateway** → FastAPI Backend (Port 8000)
3. **Data Sources** → Multi-source fetching with fallbacks
4. **Caching Layer** → Redis for fast access
5. **Database** → MongoDB for persistence
6. **Real-time Processing** → Pathway pipeline
7. **AI/ML Analysis** → Predictions and technical indicators
8. **Response** → JSON to frontend
9. **WebSocket Updates** → Live data streaming
10. **User Display** → Interactive charts and metrics

### **Key Features Implemented:**
- ✅ **Multi-source data integration** (Yahoo Finance, Alpha Vantage, RapidAPI)
- ✅ **Real-time WebSocket streaming** for live updates
- ✅ **Intelligent caching** with Redis and in-memory fallback
- ✅ **Robust error handling** with automatic retry mechanisms
- ✅ **Technical analysis** (RSI, MACD, Bollinger Bands, Moving Averages)
- ✅ **AI-powered predictions** using machine learning
- ✅ **Interactive dashboards** with Plotly visualizations
- ✅ **Database persistence** with MongoDB
- ✅ **Scalable architecture** with load balancing support
- ✅ **Comprehensive logging** and monitoring

### **Architecture Benefits:**
- **High Availability**: Multiple data sources with automatic failover
- **Performance**: Caching layer and optimized queries
- **Scalability**: Microservices architecture with load balancing
- **Reliability**: Comprehensive error handling and recovery
- **Real-time**: WebSocket connections for live data
- **Analytics**: Technical indicators and AI predictions
- **User Experience**: Interactive dashboards and responsive UI

---

## 📈 **Performance Metrics & Monitoring**

### **System Health Endpoints:**
- `GET /health` - Overall system health
- `GET /api/metrics` - Performance metrics
- `GET /api/stocks/{symbol}/status` - Individual stock status

### **Key Performance Indicators:**
- **Response Time**: < 200ms for cached requests
- **Uptime**: 99.9% availability
- **Data Accuracy**: Multi-source validation
- **Real-time Updates**: < 1 second latency
- **Error Rate**: < 0.1% for critical operations

### **Monitoring Dashboard:**
- Real-time system metrics
- Error tracking and alerts
- Performance analytics
- User activity monitoring
- Database performance metrics

---

**These diagrams provide a comprehensive view of the Finance AI Assistant application's architecture, workflows, and component interactions. Each diagram shows different aspects of the system from high-level architecture to detailed error handling flows.**