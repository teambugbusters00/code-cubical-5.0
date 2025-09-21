import React, { useState, useEffect } from 'react';
import Header from './Header';
import Navigation from './Navigation';
import { marketAPI } from '../api';

const News = () => {
  const [marketData, setMarketData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch real-time market data
  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        setLoading(true);
        setError(null);

        const indices = await marketAPI.getMarketIndices();
        setMarketData(indices);

      } catch (err) {
        console.error('Error fetching market data:', err);
        setError('Failed to load market data');
      } finally {
        setLoading(false);
      }
    };

    fetchMarketData();

    // Set up interval to refresh data every 60 seconds
    const interval = setInterval(fetchMarketData, 60000);

    return () => clearInterval(interval);
  }, []);

  const getSentimentColor = (change) => {
    if (change > 0) return 'text-green-500';
    if (change < 0) return 'text-red-500';
    return 'text-slate-500 dark:text-slate-400';
  };

  const getSentimentEmoji = (change) => {
    if (change > 0) return '🚀';
    if (change < 0) return '📉';
    return '➡️';
  };

  return (
    <div className="relative flex h-auto min-h-screen w-full flex-col justify-between group/design-root overflow-x-hidden">
      <div className="flex-grow">
        <Header title="Market News" />
        {loading && (
          <div className="flex justify-center items-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <p className="text-sm text-black/60 dark:text-white/60 mt-2">Loading market data...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded m-4">
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && (
          <main className="divide-y divide-slate-200 dark:divide-slate-800">
            {Object.entries(marketData).map(([symbol, data]) => (
              <div key={symbol} className="flex items-start gap-4 p-4">
                <div className="size-16 rounded-lg bg-gradient-to-r from-primary/20 to-primary/10 flex items-center justify-center">
                  <span className="text-2xl font-bold text-primary">{symbol}</span>
                </div>
                <div className="flex-1">
                  <p className="text-base font-medium text-slate-800 dark:text-slate-200">
                    {data.name}
                  </p>
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                    Current: ${data.current_price.toFixed(2)}
                  </p>
                  <div className="mt-1 flex items-center gap-2">
                    <span className="text-lg">{getSentimentEmoji(data.change)}</span>
                    <span className={`text-sm font-medium ${getSentimentColor(data.change)}`}>
                      {data.change >= 0 ? '+' : ''}{data.change.toFixed(2)} ({data.change_percent.toFixed(2)}%)
                    </span>
                  </div>
                </div>
              </div>
            ))}

            {/* Additional news items */}
            <div className="flex items-start gap-4 p-4">
              <div className="size-16 rounded-lg bg-gradient-to-r from-blue-500/20 to-blue-500/10 flex items-center justify-center">
                <span className="text-2xl">📰</span>
              </div>
              <div className="flex-1">
                <p className="text-base font-medium text-slate-800 dark:text-slate-200">
                  Real-time Financial News Integration
                </p>
                <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                  Live news feeds will be integrated soon
                </p>
                <div className="mt-1 flex items-center gap-2">
                  <span className="text-lg">📈</span>
                  <span className="text-sm font-medium text-blue-500">
                    Coming Soon
                  </span>
                </div>
              </div>
            </div>
          </main>
        )}
      </div>
      <Navigation />
    </div>
  );
};

export default News;