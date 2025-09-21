#!/bin/bash

# 🚀 Enhanced Finance AI Assistant - Automated Setup Script
# This script will automatically set up the complete Finance AI Assistant system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/finance-ai-assistant"
FRONTEND_DIR="$PROJECT_DIR/stitch_finance_chatbot"
VENV_DIR="$BACKEND_DIR/venv"

echo -e "${PURPLE}🚀 Enhanced Finance AI Assistant - Automated Setup${NC}"
echo -e "${BLUE}=================================================${NC}"

# Function to print status messages
print_status() {
    echo -e "${CYAN}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -d "$BACKEND_DIR" ] || [ ! -d "$FRONTEND_DIR" ]; then
    print_error "Project structure not found!"
    print_error "Please ensure you're running this script from the project root directory."
    exit 1
fi

# Check system requirements
print_status "Checking system requirements..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed!"
    print_error "Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python version: $PYTHON_VERSION"

# Check Node.js version
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed!"
    print_error "Please install Node.js 16 or higher."
    exit 1
fi

NODE_VERSION=$(node --version)
print_success "Node.js version: $NODE_VERSION"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed!"
    print_error "Please install npm."
    exit 1
fi

NPM_VERSION=$(npm --version)
print_success "npm version: $NPM_VERSION"

print_status "System requirements check completed!"

# Setup Python virtual environment
print_status "Setting up Python virtual environment..."
if [ -d "$VENV_DIR" ]; then
    print_warning "Virtual environment already exists. Skipping creation."
else
    cd "$BACKEND_DIR"
    python3 -m venv venv
    print_success "Virtual environment created at $VENV_DIR"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install Python dependencies
print_status "Installing Python dependencies..."
cd "$BACKEND_DIR"
pip install -r requirements.txt > /dev/null 2>&1

# Install additional ML packages
print_status "Installing machine learning packages..."
pip install scikit-learn textblob redis pymongo motor > /dev/null 2>&1

# Download NLTK data for TextBlob
print_status "Downloading NLTK data..."
python3 -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)" > /dev/null 2>&1

print_success "Python environment setup completed!"

# Setup Node.js dependencies
print_status "Installing Node.js dependencies..."
cd "$FRONTEND_DIR"
npm install > /dev/null 2>&1
print_success "Node.js dependencies installed!"

# Create environment file
print_status "Creating environment configuration..."
if [ ! -f "$BACKEND_DIR/.env" ]; then
    cat > "$BACKEND_DIR/.env" << 'EOF'
# 🚀 Enhanced Finance AI Assistant - Environment Configuration
# Copy this file and update with your actual API keys

# API Keys (Required - Get these from respective services)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key_here
NEWS_API_KEY=your_news_api_key_here
RAPIDAPI_KEY=your_rapidapi_key_here

# System Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_HOST=0.0.0.0
FRONTEND_PORT=3000

# Feature Flags
ENABLE_REAL_TIME_UPDATES=true
ENABLE_TECHNICAL_ANALYSIS=true
ENABLE_NEWS_INTEGRATION=true
ENABLE_REDIS_CACHE=true
ENABLE_MONGODB=false

# Performance Settings
DATA_REFRESH_INTERVAL=30
MAX_RETRIES=3
CACHE_TTL=300

# Database Settings (Optional)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=finance_ai_assistant
REDIS_URL=redis://localhost:6379

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
EOF
    print_success "Environment file created at $BACKEND_DIR/.env"
    print_warning "Please update the API keys in .env file before running the application!"
else
    print_warning "Environment file already exists. Skipping creation."
fi

# Create logs directory
print_status "Creating logs directory..."
mkdir -p "$BACKEND_DIR/logs"
print_success "Logs directory created!"

# Create startup scripts
print_status "Creating startup scripts..."

# Create start.sh
cat > "$PROJECT_DIR/start.sh" << 'EOF'
#!/bin/bash

# 🚀 Enhanced Finance AI Assistant - Startup Script

echo "🚀 Starting Enhanced Finance AI Assistant..."
echo "=========================================="

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

# Start Backend
echo "📡 Starting FastAPI Backend..."
cd finance-ai-assistant
source venv/bin/activate
python backend/app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start Frontend
echo "🌐 Starting React Frontend..."
cd ../stitch_finance_chatbot
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ Services started successfully!"
echo ""
echo "📊 Access Points:"
echo "   🚀 Main Dashboard: http://localhost:3000"
echo "   📡 Backend API:    http://localhost:8000"
echo "   📚 API Docs:       http://localhost:8000/docs"
echo "   🔍 Health Check:   http://localhost:8000/health"
echo ""
echo "🛑 Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
wait
EOF

chmod +x "$PROJECT_DIR/start.sh"

# Create stop.sh
cat > "$PROJECT_DIR/stop.sh" << 'EOF'
#!/bin/bash

# 🛑 Enhanced Finance AI Assistant - Stop Script

echo "🛑 Stopping Enhanced Finance AI Assistant..."
echo "=========================================="

# Kill Python processes
echo "Stopping FastAPI backend..."
pkill -f "python backend/app.py" 2>/dev/null || true

# Kill Node.js processes
echo "Stopping React frontend..."
pkill -f "npm start" 2>/dev/null || true
pkill -f "node.*react-scripts" 2>/dev/null || true

# Kill any remaining processes
pkill -f "uvicorn" 2>/dev/null || true

echo "✅ All services stopped!"
EOF

chmod +x "$PROJECT_DIR/stop.sh"

print_success "Startup scripts created!"

# Create Docker setup (optional)
print_status "Creating Docker configuration..."
if [ ! -f "$BACKEND_DIR/docker-compose.yml" ]; then
    cat > "$BACKEND_DIR/docker-compose.yml" << 'EOF'
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ALPHA_VANTAGE_API_KEY=${ALPHA_VANTAGE_API_KEY}
      - NEWS_API_KEY=${NEWS_API_KEY}
      - RAPIDAPI_KEY=${RAPIDAPI_KEY}
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    build: ../stitch_finance_chatbot
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    restart: unless-stopped
EOF
    print_success "Docker Compose configuration created!"
fi

# Create Dockerfile for backend
cat > "$BACKEND_DIR/Dockerfile" << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install scikit-learn textblob redis pymongo motor

# Download NLTK data
RUN python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 8000

# Run the application
CMD ["python", "backend/app.py"]
EOF

# Create Dockerfile for frontend
cat > "$FRONTEND_DIR/Dockerfile" << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Expose port
EXPOSE 3000

# Start the application
CMD ["npm", "start"]
EOF

print_success "Docker configuration completed!"

# Create README for quick start
print_status "Creating quick start guide..."
cat > "$PROJECT_DIR/QUICK_START.md" << 'EOF'
# 🚀 Quick Start Guide

## One-Command Setup
```bash
./setup.sh
```

## Manual Start
```bash
# Start Backend
cd finance-ai-assistant
source venv/bin/activate
python backend/app.py

# Start Frontend (in another terminal)
cd stitch_finance_chatbot
npm start
```

## Access Points
- **Main Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## API Keys Required
Update `.env` file with your API keys:
- Alpha Vantage API Key
- News API Key
- RapidAPI Key

## Test Commands
```bash
# Health check
curl http://localhost:8000/health

# Stock data
curl "http://localhost:8000/api/stocks/AAPL/quote"

# Market indices
curl "http://localhost:8000/api/market/indices"
```

## Troubleshooting
- Check logs in `finance-ai-assistant/logs/`
- Verify API keys in `.env` file
- Ensure all ports (8000, 3000) are available
EOF

print_success "Quick start guide created!"

# Final setup summary
print_status "Setup completed! Here's what was installed:"
echo ""
echo -e "${GREEN}✅ Python Virtual Environment${NC}"
echo -e "${GREEN}✅ Python Dependencies (FastAPI, ML packages, etc.)${NC}"
echo -e "${GREEN}✅ Node.js Dependencies (React, Tailwind, etc.)${NC}"
echo -e "${GREEN}✅ Environment Configuration${NC}"
echo -e "${GREEN}✅ Startup Scripts${NC}"
echo -e "${GREEN}✅ Docker Configuration${NC}"
echo -e "${GREEN}✅ Documentation${NC}"
echo ""

print_warning "⚠️  Next Steps:"
echo "1. Update API keys in finance-ai-assistant/.env"
echo "2. Run './start.sh' to launch the application"
echo "3. Access the dashboard at http://localhost:3000"
echo ""

print_success "🎉 Setup completed successfully!"
print_success "Your Enhanced Finance AI Assistant is ready to use!"

# Show next steps
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Edit finance-ai-assistant/.env with your API keys"
echo "2. Run './start.sh' to start the application"
echo "3. Open http://localhost:3000 in your browser"
echo "4. Check the logs in finance-ai-assistant/logs/"
echo ""

echo -e "${PURPLE}💡 For more information, see:${NC}"
echo "- INSTALLATION_GUIDE.md - Complete installation guide"
echo "- PRESENTATION_CONTENT.md - Project presentation"
echo "- README.md - Project documentation"
echo ""

echo -e "${GREEN}🚀 Happy analyzing!${NC}"