// API service for connecting to Python backend
const API_BASE_URL = 'http://localhost:8000/api';
const WS_BASE_URL = 'ws://localhost:8000/ws';

// Helper function to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }
  return response.json();
};

// WebSocket connection manager
class WebSocketManager {
  constructor() {
    this.connections = new Map();
    this.reconnectAttempts = new Map();
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 3000;
  }

  connect(symbol, onMessage, onError = null) {
    const wsUrl = `${WS_BASE_URL}/stocks/${symbol}`;

    if (this.connections.has(symbol)) {
      console.log(`WebSocket already connected for ${symbol}`);
      return this.connections.get(symbol);
    }

    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log(`WebSocket connected for ${symbol}`);
      this.reconnectAttempts.set(symbol, 0);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onclose = () => {
      console.log(`WebSocket disconnected for ${symbol}`);
      this.connections.delete(symbol);

      // Attempt to reconnect
      this.attemptReconnect(symbol, onMessage, onError);
    };

    ws.onerror = (error) => {
      console.error(`WebSocket error for ${symbol}:`, error);
      if (onError) onError(error);
    };

    this.connections.set(symbol, ws);
    return ws;
  }

  attemptReconnect(symbol, onMessage, onError) {
    const attempts = this.reconnectAttempts.get(symbol) || 0;

    if (attempts < this.maxReconnectAttempts) {
      this.reconnectAttempts.set(symbol, attempts + 1);
      console.log(`Attempting to reconnect for ${symbol} (attempt ${attempts + 1}/${this.maxReconnectAttempts})`);

      setTimeout(() => {
        this.connect(symbol, onMessage, onError);
      }, this.reconnectDelay * (attempts + 1));
    } else {
      console.error(`Max reconnection attempts reached for ${symbol}`);
    }
  }

  disconnect(symbol) {
    const ws = this.connections.get(symbol);
    if (ws) {
      ws.close();
      this.connections.delete(symbol);
      this.reconnectAttempts.delete(symbol);
    }
  }

  disconnectAll() {
    this.connections.forEach((ws, symbol) => {
      this.disconnect(symbol);
    });
  }
}

const wsManager = new WebSocketManager();

// Stock API functions
export const stockAPI = {
  // Search for stocks
  searchStocks: async (query, limit = 10) => {
    const response = await fetch(`${API_BASE_URL}/stocks/search?query=${query}&limit=${limit}`);
    return handleResponse(response);
  },

  // Get stock quote
  getStockQuote: async (symbol) => {
    const response = await fetch(`${API_BASE_URL}/stocks/${symbol}/quote`);
    return handleResponse(response);
  },

  // Get stock info
  getStockInfo: async (symbol) => {
    const response = await fetch(`${API_BASE_URL}/stocks/${symbol}/info`);
    return handleResponse(response);
  },

  // Get stock history
  getStockHistory: async (symbol, period = '1y', interval = '1d') => {
    const response = await fetch(`${API_BASE_URL}/stocks/${symbol}/history?period=${period}&interval=${interval}`);
    return handleResponse(response);
  },

  // Get stock analysis
  getStockAnalysis: async (symbol) => {
    const response = await fetch(`${API_BASE_URL}/stocks/${symbol}/analysis`);
    return handleResponse(response);
  }
};

// Market data API functions
export const marketAPI = {
  // Get market indices
  getMarketIndices: async () => {
    const response = await fetch(`${API_BASE_URL}/market/indices`);
    return handleResponse(response);
  }
};

// Portfolio API functions
export const portfolioAPI = {
  // Get user portfolios
  getUserPortfolios: async (userId) => {
    const response = await fetch(`${API_BASE_URL}/portfolios/${userId}`);
    return handleResponse(response);
  },

  // Create portfolio
  createPortfolio: async (portfolioData) => {
    const response = await fetch(`${API_BASE_URL}/portfolios`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(portfolioData),
    });
    return handleResponse(response);
  }
};

// Chat API functions (for future implementation)
export const chatAPI = {
  // Send chat message
  sendMessage: async (message) => {
    // This would connect to a chat endpoint when implemented
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });
    return handleResponse(response);
  }
};

// WebSocket API functions
export const websocketAPI = {
  // Connect to stock real-time data
  connectToStock: (symbol, onMessage, onError = null) => {
    return wsManager.connect(symbol, onMessage, onError);
  },

  // Connect to market indices real-time data
  connectToMarket: (onMessage, onError = null) => {
    return wsManager.connect('market', onMessage, onError);
  },

  // Disconnect from stock data
  disconnectFromStock: (symbol) => {
    wsManager.disconnect(symbol);
  },

  // Disconnect from all connections
  disconnectAll: () => {
    wsManager.disconnectAll();
  }
};

// Enhanced stock API with prediction support
export const predictionAPI = {
  // Get stock price predictions
  getPredictions: async (symbol, days = 7) => {
    const response = await fetch(`${API_BASE_URL}/stocks/${symbol}/predict?days=${days}`);
    return handleResponse(response);
  },

  // Get detailed technical analysis
  getDetailedAnalysis: async (symbol) => {
    const response = await fetch(`${API_BASE_URL}/stocks/${symbol}/analysis/detailed`);
    return handleResponse(response);
  }
};

// Health check
export const checkAPIHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL.replace('/api', '')}/health`);
    return response.ok;
  } catch (error) {
    console.error('API health check failed:', error);
    return false;
  }
};

export default {
  stockAPI,
  marketAPI,
  portfolioAPI,
  chatAPI,
  websocketAPI,
  predictionAPI,
  checkAPIHealth
};