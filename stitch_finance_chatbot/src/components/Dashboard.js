import React, { useState, useEffect, useRef } from 'react';
import Header from './Header';
import Navigation from './Navigation';
import { stockAPI, marketAPI, websocketAPI, predictionAPI } from '../api';

const Dashboard = () => {
  const [stockData, setStockData] = useState(null);
  const [marketIndices, setMarketIndices] = useState({});
  const [predictions, setPredictions] = useState(null);
  const [technicalAnalysis, setTechnicalAnalysis] = useState(null);
  const [alerts, setAlerts] = useState([
    {
      id: 1,
      name: 'AAPL Alert',
      condition: 'Above $160',
      enabled: true
    },
    {
      id: 2,
      name: 'MSFT Alert',
      condition: 'Below $400',
      enabled: false
    }
  ]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const wsConnectionRef = useRef(null);

  const toggleAlert = (id) => {
    setAlerts(alerts.map(alert =>
      alert.id === id ? { ...alert, enabled: !alert.enabled } : alert
    ));
  };

  // Fetch real-time data and setup WebSocket connections
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch market indices
        const indices = await marketAPI.getMarketIndices();
        setMarketIndices(indices);

        // Fetch sample stock data (AAPL)
        const stockQuote = await stockAPI.getStockQuote('AAPL');
        setStockData(stockQuote);

        // Fetch predictions
        const stockPredictions = await predictionAPI.getPredictions('AAPL', 7);
        setPredictions(stockPredictions);

        // Fetch technical analysis
        const analysis = await predictionAPI.getDetailedAnalysis('AAPL');
        setTechnicalAnalysis(analysis);

      } catch (err) {
        console.error('Error fetching dashboard data:', err);
        setError('Failed to load real-time data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();

    // Setup WebSocket connections for real-time data
    const setupWebSocket = () => {
      // Connect to AAPL real-time data
      wsConnectionRef.current = websocketAPI.connectToStock(
        'AAPL',
        (data) => {
          if (data.type === 'stock_update') {
            setStockData(data.data);
            setLastUpdate(new Date().toLocaleTimeString());
            setWsConnected(true);
          } else if (data.type === 'error') {
            console.error('WebSocket error:', data.message);
            setWsConnected(false);
          }
        },
        (error) => {
          console.error('WebSocket connection error:', error);
          setWsConnected(false);
        }
      );

      // Connect to market data
      websocketAPI.connectToMarket(
        (data) => {
          if (data.type === 'market_update') {
            setMarketIndices(data.data);
          } else if (data.type === 'error') {
            console.error('Market WebSocket error:', data.message);
          }
        },
        (error) => {
          console.error('Market WebSocket connection error:', error);
        }
      );
    };

    setupWebSocket();

    // Set up interval to refresh predictions and analysis every 5 minutes
    const analysisInterval = setInterval(fetchData, 300000);

    return () => {
      clearInterval(analysisInterval);
      websocketAPI.disconnectAll();
    };
  }, []);

  return (
    <div className="relative flex h-auto min-h-screen w-full flex-col justify-between">
      <div className="flex-grow">
        <Header title="Dashboard" />
        <main className="px-4 py-6">
          {loading && (
            <div className="flex justify-center items-center py-8">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="text-sm text-black/60 dark:text-white/60 mt-2">Loading real-time data...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              <p>{error}</p>
            </div>
          )}

          {!loading && !error && (
            <>
              {/* Real-time Status Indicator */}
              <div className="mb-4 flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${wsConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-sm text-black/60 dark:text-white/60">
                  {wsConnected ? 'Live Data' : 'Offline'} • Last Update: {lastUpdate || 'Never'}
                </span>
              </div>

              <section className="mb-8">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h2 className="text-base font-medium text-black/60 dark:text-white/60">Apple Inc. (AAPL)</h2>
                    <p className="text-4xl font-bold text-black dark:text-white mt-1">
                      ${stockData?.current_price?.toFixed(2) || 'N/A'}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <p className="text-sm font-medium text-black/60 dark:text-white/60">Today</p>
                      <p className={`text-sm font-bold ${stockData && stockData.current_price > stockData.previous_close ? 'text-primary' : 'text-red-500'}`}>
                        {stockData && stockData.current_price > stockData.previous_close ? '+' : ''}
                        {stockData ? ((stockData.current_price - stockData.previous_close) / stockData.previous_close * 100).toFixed(2) : '0.00'}%
                      </p>
                      <span className="text-xs text-black/40 dark:text-white/40">
                        Source: {stockData?.source || 'N/A'}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-black/60 dark:text-white/60">Market Cap</p>
                    <p className="text-lg font-semibold text-black dark:text-white">
                      ${(stockData?.market_cap / 1e12)?.toFixed(2) || 'N/A'}T
                    </p>
                  </div>
                </div>

                {/* Technical Indicators */}
                {technicalAnalysis && (
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-white/5 dark:bg-black/10 p-3 rounded-lg">
                      <p className="text-xs text-black/60 dark:text-white/60">RSI (14)</p>
                      <p className={`text-sm font-bold ${technicalAnalysis.indicators?.rsi > 70 ? 'text-red-500' : technicalAnalysis.indicators?.rsi < 30 ? 'text-green-500' : 'text-yellow-500'}`}>
                        {technicalAnalysis.indicators?.rsi || 'N/A'}
                      </p>
                    </div>
                    <div className="bg-white/5 dark:bg-black/10 p-3 rounded-lg">
                      <p className="text-xs text-black/60 dark:text-white/60">SMA (20)</p>
                      <p className="text-sm font-bold text-black dark:text-white">
                        ${technicalAnalysis.indicators?.sma_20?.toFixed(2) || 'N/A'}
                      </p>
                    </div>
                    <div className="bg-white/5 dark:bg-black/10 p-3 rounded-lg">
                      <p className="text-xs text-black/60 dark:text-white/60">Trend</p>
                      <p className={`text-sm font-bold ${technicalAnalysis.indicators?.trend === 'bullish' ? 'text-green-500' : technicalAnalysis.indicators?.trend === 'bearish' ? 'text-red-500' : 'text-yellow-500'}`}>
                        {technicalAnalysis.indicators?.trend?.toUpperCase() || 'N/A'}
                      </p>
                    </div>
                    <div className="bg-white/5 dark:bg-black/10 p-3 rounded-lg">
                      <p className="text-xs text-black/60 dark:text-white/60">Volume Ratio</p>
                      <p className="text-sm font-bold text-black dark:text-white">
                        {technicalAnalysis.indicators?.volume_ratio || 'N/A'}x
                      </p>
                    </div>
                  </div>
                )}

                <div className="mt-6">
                  <div className="relative h-48">
                    <svg className="absolute inset-0" fill="none" height="100%" preserveAspectRatio="none" viewBox="0 0 472 150" width="100%" xmlns="http://www.w3.org/2000/svg">
                      <path d="M0 109C18.1538 109 18.1538 21 36.3077 21C54.4615 21 54.4615 41 72.6154 41C90.7692 41 90.7692 93 108.923 93C127.077 93 127.077 33 145.231 33C163.385 33 163.385 101 181.538 101C199.692 101 199.692 61 217.846 61C236 61 236 45 254.154 45C272.308 45 272.308 121 290.462 121C308.615 121 308.615 149 326.769 149C344.923 149 344.923 1 363.077 1C381.231 1 381.231 81 399.385 81C417.538 81 417.538 129 435.692 129C453.846 129 453.846 25 472 25" stroke="#38e07b" strokeLinecap="round" strokeWidth="3"></path>
                      <path className="fill-transparent bg-chart-gradient-light dark:bg-chart-gradient-dark" d="M0 109C18.1538 109 18.1538 21 36.3077 21C54.4615 21 54.4615 41 72.6154 41C90.7692 41 90.7692 93 108.923 93C127.077 93 127.077 33 145.231 33C163.385 33 163.385 101 181.538 101C199.692 101 199.692 61 217.846 61C236 61 236 45 254.154 45C272.308 45 272.308 121 290.462 121C308.615 121 308.615 149 326.769 149C344.923 149 344.923 1 363.077 1C381.231 1 381.231 81 399.385 81C417.538 81 417.538 129 435.692 129C453.846 129 453.846 25 472 25V149H0V109Z"></path>
                    </svg>
                  </div>
                  <div className="flex justify-around mt-2">
                    <p className="text-xs font-medium text-black/60 dark:text-white/60">Jan</p>
                    <p className="text-xs font-medium text-black/60 dark:text-white/60">Feb</p>
                    <p className="text-xs font-medium text-black/60 dark:text-white/60">Mar</p>
                    <p className="text-xs font-medium text-black/60 dark:text-white/60">Apr</p>
                    <p className="text-xs font-medium text-black/60 dark:text-white/60">May</p>
                    <p className="text-xs font-medium text-black/60 dark:text-white/60">Jun</p>
                  </div>
                </div>
              </section>

              {/* Predictions Section */}
              {predictions && (
                <section className="mb-8">
                  <h2 className="text-xl font-bold text-black dark:text-white mb-4">📈 Price Predictions (Next 7 Days)</h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {predictions.predictions?.slice(0, 3).map((pred, index) => (
                      <div key={index} className="bg-white/5 dark:bg-black/10 p-4 rounded-lg">
                        <p className="text-sm text-black/60 dark:text-white/60">{pred.date}</p>
                        <p className="text-lg font-bold text-primary">
                          ${pred.predicted_price}
                        </p>
                        <p className="text-xs text-black/40 dark:text-white/40">
                          Confidence: {pred.confidence}%
                        </p>
                      </div>
                    ))}
                  </div>
                  <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                    <p className="text-sm text-blue-800 dark:text-blue-200">
                      <strong>Model:</strong> {predictions.model} |
                      <strong>Training Data:</strong> {predictions.training_data_points} points |
                      <strong>Last Actual:</strong> ${predictions.last_actual_price}
                    </p>
                  </div>
                </section>
              )}
              <section>
                <h2 className="text-xl font-bold text-black dark:text-white mb-4">Price Alerts</h2>
                <div className="space-y-2">
                  {alerts.map((alert) => (
                    <div key={alert.id} className="flex items-center justify-between p-3 rounded-lg bg-white/5 dark:bg-black/10">
                      <div className="flex items-center gap-4">
                        <div className="flex items-center justify-center size-12 rounded-lg bg-primary/20 dark:bg-primary/30 text-primary">
                          <svg fill="currentColor" height="24" viewBox="0 0 256 256" width="24" xmlns="http://www.w3.org/2000/svg">
                            <path d="M221.8,175.94C216.25,166.38,208,139.33,208,104a80,80,0,1,0-160,0c0,35.34-8.26,62.38-13.81,71.94A16,16,0,0,0,48,200H88.81a40,40,0,0,0,78.38,0H208a16,16,0,0,0,13.8-24.06ZM128,216a24,24,0,0,1-22.62-16h45.24A24,24,0,0,1,128,216ZM48,184c7.7-13.24,16-43.92,16-80a64,64,0,1,1,128,0c0,36.05,8.28,66.73,16,80Z"></path>
                          </svg>
                        </div>
                        <div>
                          <p className="font-medium text-black dark:text-white">{alert.name}</p>
                          <p className="text-sm text-black/60 dark:text-white/60">{alert.condition}</p>
                        </div>
                      </div>
                      <label className="relative inline-flex cursor-pointer items-center">
                        <input
                          className="peer sr-only"
                          type="checkbox"
                          checked={alert.enabled}
                          onChange={() => toggleAlert(alert.id)}
                        />
                        <div className={`peer h-6 w-11 rounded-full bg-black/20 dark:bg-white/20 peer-checked:bg-primary peer-checked:after:translate-x-full peer-checked:after:border-white after:absolute after:start-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border after:border-transparent after:bg-white after:transition-all`}></div>
                      </label>
                    </div>
                  ))}
                </div>
              </section>
            </>
          )}
        </main>
      </div>
      <Navigation />
    </div>
  );
};

export default Dashboard;