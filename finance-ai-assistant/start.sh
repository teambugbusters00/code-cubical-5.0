#!/bin/bash

# Finance AI Assistant Startup Script
# This script starts all components of the Finance AI Assistant

echo "🚀 Starting Finance AI Assistant..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if requirements.txt is newer than last install
if [ ! -f ".requirements_installed" ] || [ requirements.txt -nt .requirements_installed ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    touch .requirements_installed
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data

# Function to start a service
start_service() {
    local service_name=$1
    local command=$2
    local log_file=$3

    echo "▶️  Starting $service_name..."
    nohup $command > "$log_file" 2>&1 &
    echo "   PID: $!"
    echo "   Log: $log_file"
}

# Start Enhanced FastAPI Backend with multiple data sources
start_service "Enhanced FastAPI Backend" \
    "cd backend && python app.py" \
    "logs/backend.log"

# Wait a moment for backend to initialize
sleep 5

# Start React Frontend (stitch_finance_chatbot)
start_service "React Frontend Dashboard" \
    "cd ../stitch_finance_chatbot && npm start" \
    "logs/frontend.log"

# Wait a moment for frontend to initialize
sleep 3

# Start Streamlit Frontend (optional)
start_service "Streamlit Analytics Dashboard" \
    "cd frontend && streamlit run app.py --server.headless true --server.address 0.0.0.0" \
    "logs/streamlit.log"

echo ""
echo "🎉 Enhanced Finance AI Assistant Started Successfully!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Access Points:"
echo "   • 🚀 Main Dashboard: http://localhost:3000"
echo "   • 📊 Backend API: http://localhost:8000"
echo "   • 📈 Streamlit Analytics: http://localhost:8501"
echo "   • 📚 API Documentation: http://localhost:8000/docs"
echo ""
echo "🔑 API Keys Configured:"
echo "   • ✅ Alpha Vantage: AO4ZEXP2ULIH7ZXB"
echo "   • ✅ News API: 534b4f310dbc4b2e85b830dcdc2a4889"
echo "   • ✅ RapidAPI Yahoo Finance: abd8117907msh7c2a6123ee869eep132d51jsn8354fc10125a"
echo ""
echo "📡 Real-time Features:"
echo "   • WebSocket Stock Streaming: ws://localhost:8000/ws/stocks/{symbol}"
echo "   • Market Indices Streaming: ws://localhost:8000/ws/market"
echo "   • Auto-reconnection enabled"
echo ""
echo "🤖 AI Features:"
echo "   • Price Predictions (7-day forecast)"
echo "   • Technical Analysis (RSI, MACD, Bollinger Bands)"
echo "   • News Sentiment Analysis"
echo "   • Multi-source data aggregation"
echo ""
echo "📊 To check service status:"
echo "   • Backend health: curl http://localhost:8000/health"
echo "   • View logs: tail -f logs/*.log"
echo ""
echo "🛑 To stop all services:"
echo "   • Press Ctrl+C or run: pkill -f 'python.*app.py' && pkill -f 'npm.*start'"
echo ""
echo "📝 All services are running in the background with enhanced features!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"