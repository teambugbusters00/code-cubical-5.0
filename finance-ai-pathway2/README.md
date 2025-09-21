# 🤖 Finance AI Assistant

A comprehensive **Finance AI Assistant** built with **Pathway**, **FastAPI**, and **Streamlit** that provides real-time financial data analysis, news monitoring, portfolio tracking, and AI-powered insights using RAG (Retrieval-Augmented Generation).

## 🚀 Features

### Core Capabilities
- **Real-time Stock Data**: Live stock prices from Yahoo Finance and RapidAPI
- **Financial News Ingestion**: RSS feeds and API integration with sentiment analysis
- **Portfolio Management**: Track holdings, performance, and sector allocation
- **AI-Powered Chatbot**: RAG-based Q&A with financial context
- **Interactive Dashboards**: Beautiful visualizations with Plotly
- **Market Analysis**: Technical indicators, sentiment analysis, and trends
- **WebSocket Support**: Real-time data streaming

### Technical Stack
- **Backend**: FastAPI with async support
- **Data Processing**: Pathway for real-time streaming
- **AI/ML**: OpenAI GPT-4o-mini with RAG pipeline
- **Frontend**: Streamlit with interactive components
- **Data Sources**: Yahoo Finance, RSS feeds, News APIs
- **Vector Search**: Custom embedding and similarity search

## 📁 Project Structure

```
finance-ai-assistant/
│── data/                          # Sample data files
│   ├── stocks.csv                 # Stock market data
│   ├── news.csv                   # Financial news
│   └── portfolio.json             # Portfolio holdings
│
│── ingestion/                     # Data ingestion modules
│   ├── stock_stream.py            # Stock data fetching
│   ├── news_stream.py             # News data fetching
│   └── portfolio_stream.py        # Portfolio management
│
│── processing/                    # Data processing pipeline
│   ├── pipeline.py                # Main Pathway pipeline
│   ├── embeddings.py              # Text embeddings
│   └── indexing.py                # Vector indexing
│
│── rag/                           # RAG implementation
│   ├── rag_pipeline.py            # Main RAG pipeline
│   └── llm_config.py              # LLM configuration
│
│── api/                           # FastAPI backend
│   ├── server.py                  # Main API server
│   └── routes.py                  # Additional routes
│
│── ui/                            # Streamlit frontend
│   ├── streamlit_app.py           # Main application
│   └── components/                # UI components
│       ├── chat_box.py            # Chat interface
│       ├── stock_dashboard.py     # Stock visualizations
│       └── news_feed.py           # News display
│
│── tests/                         # Test files
│   ├── test_ingestion.py
│   ├── test_pipeline.py
│   └── test_api.py
│
│── requirements.txt               # Python dependencies
│── .env.example                   # Environment variables
│── README.md                      # This file
└── demo_plan.md                   # Demo instructions
```

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- pip package manager
- Git

### 1. Clone the Repository
```bash
git clone <repository-url>
cd finance-ai-assistant
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Required: OPENAI_API_KEY
# Optional: RAPIDAPI_KEY, NEWS_API_KEY, PATHWAY_LICENSE_KEY
```

### 5. Get API Keys

#### Required
- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)

#### Optional (for enhanced features)
- **RapidAPI Key**: Get from [RapidAPI](https://rapidapi.com/)
- **News API Key**: Get from [NewsAPI](https://newsapi.org/)
- **Pathway License**: Get from [Pathway](https://pathway.com/)

## 🚀 Usage

### Start the Backend API
```bash
# Terminal 1: Start FastAPI server
python -m uvicorn api.server:app --reload --host 0.0.0.0 --port 8000
```

### Start the Frontend
```bash
# Terminal 2: Start Streamlit app
streamlit run ui/streamlit_app.py
```

### Start Data Processing Pipeline
```bash
# Terminal 3: Start Pathway pipeline
python processing/pipeline.py
```

## 🌐 API Endpoints

### Core Endpoints
- `GET /` - API information and available endpoints
- `GET /health` - Health check and service status
- `POST /api/query` - RAG-powered financial queries
- `GET /api/stocks/{symbol}` - Stock information
- `GET /api/news` - Financial news feed
- `GET /api/portfolio` - Portfolio summary

### Advanced Endpoints
- `GET /api/stocks/{symbol}/analysis` - Comprehensive stock analysis
- `GET /api/stocks/{symbol}/history` - Historical price data
- `GET /api/sentiment/{symbol}` - Sentiment analysis
- `GET /api/market/overview` - Market overview
- `GET /api/portfolio/insights` - AI portfolio insights

### WebSocket Endpoints
- `WS /ws/stocks/{symbol}` - Real-time stock data
- `WS /ws/news` - Real-time news updates

## 💻 Frontend Features

### 1. Chatbot Interface
- **AI-Powered Q&A**: Ask questions about stocks, market trends, news
- **Context-Aware**: Uses RAG to provide relevant financial information
- **Conversation History**: Maintains chat context

### 2. Stocks Dashboard
- **Real-time Prices**: Live stock quotes and market data
- **Interactive Charts**: Price history with volume analysis
- **Technical Analysis**: Moving averages, RSI, MACD indicators
- **Stock Comparison**: Compare multiple stocks side-by-side

### 3. News Feed
- **Live News**: Real-time financial news from multiple sources
- **Sentiment Analysis**: Positive/negative/neutral classification
- **Filtering**: Filter by sentiment, symbol, date, source
- **Search**: Full-text search across news articles

### 4. Portfolio Monitor
- **Holdings Tracking**: Monitor your investment portfolio
- **Performance Metrics**: P&L, returns, sector allocation
- **Risk Analysis**: Diversification and risk assessment
- **AI Insights**: Machine learning-powered recommendations

### 5. Market Overview
- **Market Indices**: S&P 500, NASDAQ, Dow Jones tracking
- **Sector Analysis**: Performance by market sectors
- **Sentiment Summary**: Overall market sentiment
- **Trending Topics**: Popular stocks and news

## 🔧 Configuration

### Environment Variables
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Optional APIs
RAPIDAPI_KEY=your_rapidapi_key_here
NEWS_API_KEY=your_news_api_key_here
PATHWAY_LICENSE_KEY=your_pathway_license_key_here

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
DATA_REFRESH_INTERVAL=300
API_HOST=0.0.0.0
API_PORT=8000
STREAMLIT_PORT=8501
```

### Data Sources
- **Yahoo Finance**: Real-time stock prices and historical data
- **RSS Feeds**: Financial news from major sources
- **News APIs**: Enhanced news data and sentiment analysis
- **Alpha Vantage**: Additional market data (if configured)

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test Files
- `tests/test_ingestion.py` - Data ingestion tests
- `tests/test_pipeline.py` - Processing pipeline tests
- `tests/test_api.py` - API endpoint tests

## 📊 Sample Data

The project includes sample data files for testing:

- **stocks.csv**: Sample stock market data
- **news.csv**: Sample financial news with sentiment
- **portfolio.json**: Sample investment portfolio

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements.txt
   # Make sure you're in the virtual environment
   ```

2. **API Connection Issues**
   - Check your internet connection
   - Verify API keys in `.env` file
   - Check API rate limits

3. **Pathway Issues**
   - Ensure Pathway license key is set
   - Check Pathway documentation for troubleshooting

4. **Streamlit Display Issues**
   - Make sure port 8501 is not in use
   - Check browser compatibility

### Debug Mode
Enable debug mode in `.env`:
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Pathway** for real-time data processing
- **OpenAI** for AI capabilities
- **Streamlit** for the web interface
- **Yahoo Finance** for market data
- **FastAPI** for the REST API

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the demo plan for usage examples

---

**Happy Trading! 📈🚀**