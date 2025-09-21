import React, { useState, useEffect } from 'react';
import { stockAPI } from '../api';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Search, Plus, Star, TrendingUp, TrendingDown, DollarSign, BarChart3 } from 'lucide-react';

const StockDashboard = () => {
  const [selectedStock, setSelectedStock] = useState('AAPL');
  const [stockData, setStockData] = useState(null);
  const [stockHistory, setStockHistory] = useState([]);
  const [watchlist, setWatchlist] = useState(['AAPL', 'MSFT', 'TSLA']);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Popular stocks for dropdown
  const popularStocks = [
    { symbol: 'AAPL', name: 'Apple Inc.' },
    { symbol: 'MSFT', name: 'Microsoft Corporation' },
    { symbol: 'TSLA', name: 'Tesla, Inc.' },
    { symbol: 'GOOGL', name: 'Alphabet Inc.' },
    { symbol: 'NVDA', name: 'NVIDIA Corporation' },
    { symbol: 'META', name: 'Meta Platforms, Inc.' },
    { symbol: 'AMZN', name: 'Amazon.com, Inc.' },
    { symbol: 'NFLX', name: 'Netflix, Inc.' },
    { symbol: 'JPM', name: 'JPMorgan Chase & Co.' },
    { symbol: 'JNJ', name: 'Johnson & Johnson' },
  ];

  useEffect(() => {
    fetchStockData(selectedStock);
  }, [selectedStock]);

  const fetchStockData = async (symbol) => {
    try {
      setLoading(true);
      setError(null);

      const [quote, history] = await Promise.all([
        stockAPI.getStockQuote(symbol),
        stockAPI.getStockHistory(symbol, '1y', '1d')
      ]);

      setStockData(quote);

      // Process history data for chart
      const processedHistory = history.map(item => ({
        date: new Date(item.date).toLocaleDateString(),
        price: item.close,
        volume: item.volume,
      }));

      setStockHistory(processedHistory);

    } catch (err) {
      console.error('Error fetching stock data:', err);
      setError('Failed to load stock data');
    } finally {
      setLoading(false);
    }
  };

  const handleStockSelect = (symbol) => {
    setSelectedStock(symbol);
    setSearchTerm('');
  };

  const toggleWatchlist = (symbol) => {
    setWatchlist(prev =>
      prev.includes(symbol)
        ? prev.filter(s => s !== symbol)
        : [...prev, symbol]
    );
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('en-US').format(value);
  };

  const formatPercent = (value) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const filteredStocks = popularStocks.filter(stock =>
    stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    stock.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading && !stockData) {
    return (
      <div className="flex h-screen flex-col">
        <Header title="Stock Dashboard" />
        <main className="flex-1 overflow-y-auto p-4">
          <div className="flex justify-center items-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <p className="text-sm text-black/60 dark:text-white/60 mt-2">Loading stock data...</p>
            </div>
          </div>
        </main>
        <Navigation />
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col">
      <Header title="Stock Dashboard" />

      <main className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Stock Selector */}
        <div className="bg-white/10 dark:bg-white/5 rounded-xl p-6 border border-white/20 dark:border-white/10">
          <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-black/50 dark:text-white/50 w-5 h-5" />
              <input
                type="text"
                placeholder="Search stocks..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 rounded-lg bg-white/20 dark:bg-white/5 border border-white/20 dark:border-white/10 text-black dark:text-white placeholder-black/50 dark:placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-primary"
              />
              {searchTerm && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-white/10 dark:bg-white/5 backdrop-blur-sm rounded-lg border border-white/20 dark:border-white/10 max-h-60 overflow-y-auto z-10">
                  {filteredStocks.map((stock) => (
                    <button
                      key={stock.symbol}
                      onClick={() => handleStockSelect(stock.symbol)}
                      className="w-full text-left p-3 hover:bg-white/10 dark:hover:bg-white/5 transition-colors"
                    >
                      <div className="font-bold text-black dark:text-white">{stock.symbol}</div>
                      <div className="text-sm text-black/60 dark:text-white/60">{stock.name}</div>
                    </button>
                  ))}
                </div>
              )}
            </div>

            <div className="flex gap-2">
              <select
                value={selectedStock}
                onChange={(e) => handleStockSelect(e.target.value)}
                className="px-4 py-2 rounded-lg bg-white/20 dark:bg-white/5 border border-white/20 dark:border-white/10 text-black dark:text-white focus:outline-none focus:ring-2 focus:ring-primary"
              >
                {popularStocks.map((stock) => (
                  <option key={stock.symbol} value={stock.symbol}>
                    {stock.symbol} - {stock.name}
                  </option>
                ))}
              </select>

              <button
                onClick={() => toggleWatchlist(selectedStock)}
                className={`p-2 rounded-lg transition-colors ${
                  watchlist.includes(selectedStock)
                    ? 'bg-primary text-black'
                    : 'bg-white/10 dark:bg-white/5 text-white hover:bg-white/20 dark:hover:bg-white/10'
                }`}
              >
                <Star className={`w-5 h-5 ${watchlist.includes(selectedStock) ? 'fill-current' : ''}`} />
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <p>{error}</p>
          </div>
        )}

        {stockData && (
          <>
            {/* Stock Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white/10 dark:bg-white/5 rounded-xl p-4 border border-white/20 dark:border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <DollarSign className="w-5 h-5 text-primary" />
                  <span className="text-sm text-black/60 dark:text-white/60">Current Price</span>
                </div>
                <p className="text-2xl font-bold text-black dark:text-white">
                  {formatCurrency(stockData.current_price)}
                </p>
              </div>

              <div className="bg-white/10 dark:bg-white/5 rounded-xl p-4 border border-white/20 dark:border-white/10">
                <div className="flex items-center justify-between mb-2">
                  {stockData.current_price >= stockData.previous_close ? (
                    <TrendingUp className="w-5 h-5 text-green-500" />
                  ) : (
                    <TrendingDown className="w-5 h-5 text-red-500" />
                  )}
                  <span className="text-sm text-black/60 dark:text-white/60">Change</span>
                </div>
                <p className={`text-2xl font-bold ${stockData.current_price >= stockData.previous_close ? 'text-green-500' : 'text-red-500'}`}>
                  {formatCurrency(stockData.current_price - stockData.previous_close)}
                </p>
                <p className={`text-sm ${stockData.current_price >= stockData.previous_close ? 'text-green-500' : 'text-red-500'}`}>
                  {formatPercent(((stockData.current_price - stockData.previous_close) / stockData.previous_close) * 100)}
                </p>
              </div>

              <div className="bg-white/10 dark:bg-white/5 rounded-xl p-4 border border-white/20 dark:border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <BarChart3 className="w-5 h-5 text-primary" />
                  <span className="text-sm text-black/60 dark:text-white/60">Volume</span>
                </div>
                <p className="text-2xl font-bold text-black dark:text-white">
                  {formatNumber(stockData.volume || 0)}
                </p>
              </div>

              <div className="bg-white/10 dark:bg-white/5 rounded-xl p-4 border border-white/20 dark:border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <DollarSign className="w-5 h-5 text-primary" />
                  <span className="text-sm text-black/60 dark:text-white/60">Market Cap</span>
                </div>
                <p className="text-2xl font-bold text-black dark:text-white">
                  {formatCurrency(stockData.market_cap || 0)}
                </p>
              </div>
            </div>

            {/* Price Chart */}
            <div className="bg-white/10 dark:bg-white/5 rounded-xl p-6 border border-white/20 dark:border-white/10">
              <h2 className="text-xl font-bold text-black dark:text-white mb-4">Price Chart (1 Year)</h2>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={stockHistory}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis
                      dataKey="date"
                      stroke="rgba(255,255,255,0.6)"
                      fontSize={12}
                    />
                    <YAxis
                      stroke="rgba(255,255,255,0.6)"
                      fontSize={12}
                      tickFormatter={(value) => `$${value.toFixed(0)}`}
                    />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        border: '1px solid rgba(255,255,255,0.2)',
                        borderRadius: '8px',
                        color: 'white'
                      }}
                      formatter={(value) => [formatCurrency(value), 'Price']}
                      labelFormatter={(label) => `Date: ${label}`}
                    />
                    <Area
                      type="monotone"
                      dataKey="price"
                      stroke="#8B5CF6"
                      fill="rgba(139, 92, 246, 0.2)"
                      strokeWidth={2}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Watchlist */}
            <div className="bg-white/10 dark:bg-white/5 rounded-xl p-6 border border-white/20 dark:border-white/10">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-black dark:text-white">Watchlist</h2>
                <button className="text-primary hover:text-primary/80 text-sm font-medium">
                  Manage
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {watchlist.map((symbol) => (
                  <button
                    key={symbol}
                    onClick={() => handleStockSelect(symbol)}
                    className={`p-3 rounded-lg text-left transition-colors ${
                      selectedStock === symbol
                        ? 'bg-primary text-black'
                        : 'bg-white/5 dark:bg-white/5 hover:bg-white/10 dark:hover:bg-white/5'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-bold">{symbol}</p>
                        <p className="text-sm opacity-75">Stock</p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleWatchlist(symbol);
                        }}
                        className="text-yellow-500 hover:text-yellow-400"
                      >
                        <Star className="w-4 h-4 fill-current" />
                      </button>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </>
        )}
      </main>

      <Navigation />
    </div>
  );
};

export default StockDashboard;