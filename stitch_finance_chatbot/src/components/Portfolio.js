import React, { useState, useEffect } from 'react';
import Header from './Header';
import Navigation from './Navigation';
import { stockAPI } from '../api';

const Portfolio = () => {
  const [holdings, setHoldings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Sample portfolio stocks to fetch
  const portfolioSymbols = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'NVDA'];

  // Fetch real-time portfolio data
  useEffect(() => {
    const fetchPortfolioData = async () => {
      try {
        setLoading(true);
        setError(null);

        const portfolioData = [];

        // Fetch data for each stock in portfolio
        for (const symbol of portfolioSymbols) {
          try {
            const quote = await stockAPI.getStockQuote(symbol);
            const info = await stockAPI.getStockInfo(symbol);

            portfolioData.push({
              id: symbol,
              symbol: symbol,
              shares: Math.floor(Math.random() * 100) + 1, // Random shares for demo
              image: `https://logo.clearbit.com/${symbol.toLowerCase()}.com`, // Company logo
              value: quote.current_price,
              change: quote.current_price - quote.previous_close,
              changePercent: ((quote.current_price - quote.previous_close) / quote.previous_close) * 100,
              companyName: info.name
            });
          } catch (err) {
            console.error(`Error fetching data for ${symbol}:`, err);
          }
        }

        setHoldings(portfolioData);

      } catch (err) {
        console.error('Error fetching portfolio data:', err);
        setError('Failed to load portfolio data');
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolioData();

    // Set up interval to refresh data every 60 seconds
    const interval = setInterval(fetchPortfolioData, 60000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col min-h-screen">
      <Header title="Portfolio" />
      <main className="flex-1 overflow-y-auto pb-24">
        {loading && (
          <div className="flex justify-center items-center py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <p className="text-sm text-black/60 dark:text-white/60 mt-2">Loading portfolio data...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded m-4">
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && (
          <>
            <div className="p-4">
              <h2 className="text-xl font-bold text-black dark:text-white mb-4">Your Holdings</h2>
              <div className="space-y-3">
                {holdings.map((holding) => (
                  <div key={holding.id} className="flex items-center gap-4 p-3 rounded-lg bg-white/5 dark:bg-white/5">
                    <div
                      className="w-12 h-12 rounded-lg bg-cover bg-center bg-gray-200 flex items-center justify-center"
                      style={{ backgroundImage: `url("${holding.image}")` }}
                    >
                      {!holding.image && (
                        <span className="text-xs font-bold text-gray-600">{holding.symbol}</span>
                      )}
                    </div>
                    <div className="flex-1">
                      <p className="font-bold text-black dark:text-white">{holding.symbol}</p>
                      <p className="text-sm text-black/60 dark:text-white/60">{holding.shares} shares</p>
                      {holding.companyName && (
                        <p className="text-xs text-black/40 dark:text-white/40 truncate">{holding.companyName}</p>
                      )}
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-black dark:text-white">${holding.value.toFixed(2)}</p>
                      <p className={`text-sm ${holding.change >= 0 ? 'text-primary' : 'text-red-500'}`}>
                        {holding.change >= 0 ? '+' : ''}{holding.change.toFixed(2)} ({holding.changePercent.toFixed(2)}%)
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            <div className="px-4 mt-6">
              <h2 className="text-xl font-bold text-black dark:text-white mb-4">News Impact</h2>
              <div className="space-y-4">
                <div className="rounded-xl overflow-hidden bg-background-light dark:bg-background-dark shadow-md border border-white/10 dark:border-white/10">
                  <div className="h-32 bg-gradient-to-r from-primary/20 to-primary/10 flex items-center justify-center">
                    <p className="text-black/60 dark:text-white/60">Real-time news integration coming soon</p>
                  </div>
                  <div className="p-4">
                    <p className="text-xs text-black/60 dark:text-white/60 mb-1">Feature Update</p>
                    <h3 className="font-bold text-black dark:text-white mb-2">News Integration</h3>
                    <p className="text-sm text-black/80 dark:text-white/80">Real-time financial news will be integrated with your portfolio data.</p>
                  </div>
                </div>
              </div>
            </div>
          </>
        )}
      </main>
      <Navigation />
    </div>
  );
};

export default Portfolio;