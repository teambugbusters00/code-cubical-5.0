import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { stockAPI, marketAPI } from '../api';
import Header from '../components/Header';
import Navigation from '../components/Navigation';
import { TrendingUp, TrendingDown, DollarSign, BarChart3, Users, MessageCircle } from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const [watchlist, setWatchlist] = useState([]);
  const [marketIndices, setMarketIndices] = useState({});
  const [portfolioSummary, setPortfolioSummary] = useState({
    totalValue: 0,
    totalGainLoss: 0,
    totalGainLossPercent: 0,
  });
  const [recentChats, setRecentChats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Sample watchlist stocks
  const watchlistSymbols = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'NVDA'];

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch watchlist data
        const watchlistData = [];
        for (const symbol of watchlistSymbols) {
          try {
            const quote = await stockAPI.getStockQuote(symbol);
            watchlistData.push({
              symbol,
              price: quote.current_price,
              change: quote.current_price - quote.previous_close,
              changePercent: ((quote.current_price - quote.previous_close) / quote.previous_close) * 100,
            });
          } catch (err) {
            console.error(`Error fetching ${symbol}:`, err);
          }
        }
        setWatchlist(watchlistData);

        // Fetch market indices
        const indices = await marketAPI.getMarketIndices();
        setMarketIndices(indices);

        // Calculate portfolio summary (mock data)
        const totalValue = watchlistData.reduce((sum, stock) => sum + stock.price, 0);
        const totalGainLoss = watchlistData.reduce((sum, stock) => sum + stock.change, 0);
        const totalGainLossPercent = totalValue > 0 ? (totalGainLoss / (totalValue - totalGainLoss)) * 100 : 0;

        setPortfolioSummary({
          totalValue,
          totalGainLoss,
          totalGainLossPercent,
        });

        // Mock recent chats
        setRecentChats([
          { id: 1, message: 'What is AAPL trading at?', time: '2 hours ago' },
          { id: 2, message: 'Show me market indices', time: '4 hours ago' },
          { id: 3, message: 'Portfolio analysis', time: '1 day ago' },
        ]);

      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();

    // Set up interval to refresh data every 60 seconds
    const interval = setInterval(fetchDashboardData, 60000);

    return () => clearInterval(interval);
  }, []);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatPercent = (value) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="flex h-screen flex-col">
        <Header title="Dashboard" />
        <main className="flex-1 overflow-y-auto p-4">
          <div className="flex justify-center items-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <p className="text-sm text-black/60 dark:text-white/60 mt-2">Loading dashboard...</p>
            </div>
          </div>
        </main>
        <Navigation />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen flex-col">
        <Header title="Dashboard" />
        <main className="flex-1 overflow-y-auto p-4">
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded m-4">
            <p>{error}</p>
          </div>
        </main>
        <Navigation />
      </div>
    );
  }

  return (
    <div className="flex h-screen flex-col">
      <Header title="Dashboard" />

      <main className="flex-1 overflow-y-auto p-4 space-y-6">
        {/* Welcome Section */}
        <div className="bg-gradient-to-r from-primary/20 to-primary/10 rounded-xl p-6">
          <h1 className="text-2xl font-bold text-black dark:text-white mb-2">
            Welcome back, {user?.username || 'User'}!
          </h1>
          <p className="text-black/60 dark:text-white/60">
            Here's your financial overview for today
          </p>
        </div>

        {/* Portfolio Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white/10 dark:bg-white/5 rounded-xl p-4 border border-white/20 dark:border-white/10">
            <div className="flex items-center justify-between mb-2">
              <DollarSign className="w-5 h-5 text-primary" />
              <span className="text-sm text-black/60 dark:text-white/60">Portfolio Value</span>
            </div>
            <p className="text-2xl font-bold text-black dark:text-white">
              {formatCurrency(portfolioSummary.totalValue)}
            </p>
          </div>

          <div className="bg-white/10 dark:bg-white/5 rounded-xl p-4 border border-white/20 dark:border-white/10">
            <div className="flex items-center justify-between mb-2">
              {portfolioSummary.totalGainLoss >= 0 ? (
                <TrendingUp className="w-5 h-5 text-green-500" />
              ) : (
                <TrendingDown className="w-5 h-5 text-red-500" />
              )}
              <span className="text-sm text-black/60 dark:text-white/60">Today's P&L</span>
            </div>
            <p className={`text-2xl font-bold ${portfolioSummary.totalGainLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {formatCurrency(portfolioSummary.totalGainLoss)}
            </p>
            <p className={`text-sm ${portfolioSummary.totalGainLoss >= 0 ? 'text-green-500' : 'text-red-500'}`}>
              {formatPercent(portfolioSummary.totalGainLossPercent)}
            </p>
          </div>

          <div className="bg-white/10 dark:bg-white/5 rounded-xl p-4 border border-white/20 dark:border-white/10">
            <div className="flex items-center justify-between mb-2">
              <BarChart3 className="w-5 h-5 text-primary" />
              <span className="text-sm text-black/60 dark:text-white/60">Holdings</span>
            </div>
            <p className="text-2xl font-bold text-black dark:text-white">
              {watchlist.length}
            </p>
            <p className="text-sm text-black/60 dark:text-white/60">Stocks</p>
          </div>
        </div>

        {/* Watchlist */}
        <div className="bg-white/10 dark:bg-white/5 rounded-xl p-6 border border-white/20 dark:border-white/10">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-black dark:text-white">Watchlist</h2>
            <button className="text-primary hover:text-primary/80 text-sm font-medium">
              View All
            </button>
          </div>
          <div className="space-y-3">
            {watchlist.slice(0, 5).map((stock) => (
              <div key={stock.symbol} className="flex items-center justify-between p-3 rounded-lg bg-white/5 dark:bg-white/5">
                <div>
                  <p className="font-bold text-black dark:text-white">{stock.symbol}</p>
                  <p className="text-sm text-black/60 dark:text-white/60">
                    {formatCurrency(stock.price)}
                  </p>
                </div>
                <div className="text-right">
                  <p className={`font-bold ${stock.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {stock.change >= 0 ? '+' : ''}{formatCurrency(stock.change)}
                  </p>
                  <p className={`text-sm ${stock.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                    {formatPercent(stock.changePercent)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Market Indices */}
        <div className="bg-white/10 dark:bg-white/5 rounded-xl p-6 border border-white/20 dark:border-white/10">
          <h2 className="text-xl font-bold text-black dark:text-white mb-4">Market Indices</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(marketIndices).slice(0, 4).map(([symbol, data]) => (
              <div key={symbol} className="p-4 rounded-lg bg-white/5 dark:bg-white/5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-bold text-black dark:text-white">{symbol}</p>
                    <p className="text-sm text-black/60 dark:text-white/60">{data.name}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-black dark:text-white">
                      {formatCurrency(data.current_price)}
                    </p>
                    <p className={`text-sm ${data.change >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                      {data.change >= 0 ? '+' : ''}{formatCurrency(data.change)} ({formatPercent(data.change_percent)})
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Recent Chats */}
          <div className="bg-white/10 dark:bg-white/5 rounded-xl p-6 border border-white/20 dark:border-white/10">
            <div className="flex items-center mb-4">
              <MessageCircle className="w-5 h-5 text-primary mr-2" />
              <h2 className="text-xl font-bold text-black dark:text-white">Recent Chats</h2>
            </div>
            <div className="space-y-3">
              {recentChats.map((chat) => (
                <div key={chat.id} className="p-3 rounded-lg bg-white/5 dark:bg-white/5">
                  <p className="text-sm text-black dark:text-white mb-1">{chat.message}</p>
                  <p className="text-xs text-black/60 dark:text-white/60">{chat.time}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white/10 dark:bg-white/5 rounded-xl p-6 border border-white/20 dark:border-white/10">
            <h2 className="text-xl font-bold text-black dark:text-white mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <button className="w-full p-3 rounded-lg bg-primary text-black font-medium hover:bg-primary/90 transition-colors">
                View Portfolio
              </button>
              <button className="w-full p-3 rounded-lg bg-white/10 dark:bg-white/5 text-white font-medium hover:bg-white/20 dark:hover:bg-white/10 transition-colors">
                Check News
              </button>
              <button className="w-full p-3 rounded-lg bg-white/10 dark:bg-white/5 text-white font-medium hover:bg-white/20 dark:hover:bg-white/10 transition-colors">
                Stock Analysis
              </button>
            </div>
          </div>
        </div>
      </main>

      <Navigation />
    </div>
  );
};

export default Dashboard;