import React, { useState, useEffect } from 'react';
import Header from './Header';
import Navigation from './Navigation';
import { stockAPI, marketAPI } from '../api';

const Chatbot = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'bot',
      avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuBZebf4RCTy6FnXuM9az7eyokwf6ezlN3Zwaa0N5xmJ6rTLGI8iaC0MbUXAJp8uulsHV4kMw_9h1D0oEyPNOds7NeTrZ2Ab8bzn-4-q_0Aye6RvEPOqqPWBDAPudGEnnNtryajxvLjh1xEamQ0CLmW87unZUZgsUAmJWYLjbMTBmZc3rkNRcd7wBS0z1e9TaIWVp-CJGLRI2vODYon3cZL2qZd3_ECzB3waO_0jZpbHoG87SDL26FXtOgm0LidYByoXu9lLKPnVy8kO',
      name: 'Finance Bot',
      text: 'Hi there! I\'m connected to real-time financial data. How can I help you with your finances today?',
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (inputMessage.trim()) {
      const userMessage = {
        id: messages.length + 1,
        sender: 'user',
        avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuD7xQIgFGzrQVhNVwiaJlKjlja1mzKyUxpjbUnvlb-ngy_FekpvM_feI67B4RuTgS71hYaE_tfRP7Un4WQWbsP5TGwa3h17LhbI5E5uXyAPmLL-Zx06eJ3sc5pRJTD1ULIbbRvjvpXohbi91E8Cc0svOPQzCvPYatTsQgyA3I7tdubLjYgWrXNF9fXzfeYKmitYRVmFvE-9Z_5GNRgGuhZAx0IE72_2rNrLOPk5wvkeUh0mcgfYwTt3dV4xV1CH1x4t5QIMoMkjwLtl',
        name: 'User',
        text: inputMessage,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages(prev => [...prev, userMessage]);
      const currentInput = inputMessage;
      setInputMessage('');
      setIsLoading(true);

      try {
        // For now, we'll create intelligent responses based on keywords
        // In the future, this would connect to a proper chat API
        let botResponse = '';

        if (currentInput.toLowerCase().includes('stock') || currentInput.toLowerCase().includes('price')) {
          try {
            const stockSymbol = extractStockSymbol(currentInput);
            if (stockSymbol) {
              const quote = await stockAPI.getStockQuote(stockSymbol);
              botResponse = `📊 Real-time data for ${stockSymbol}:\n• Current Price: $${quote.current_price.toFixed(2)}\n• Change: ${quote.current_price > quote.previous_close ? '+' : ''}$${(quote.current_price - quote.previous_close).toFixed(2)} (${((quote.current_price - quote.previous_close) / quote.previous_close * 100).toFixed(2)}%)`;
            } else {
              botResponse = 'I can provide real-time stock quotes! Please specify a stock symbol (e.g., "AAPL price" or "What\'s MSFT trading at?")';
            }
          } catch (error) {
            botResponse = 'I\'m having trouble fetching stock data right now. Please try again in a moment.';
          }
        } else if (currentInput.toLowerCase().includes('market') || currentInput.toLowerCase().includes('indices')) {
          try {
            const indices = await marketAPI.getMarketIndices();
            const marketSummary = Object.entries(indices)
              .map(([symbol, data]) => `${symbol}: $${data.current_price.toFixed(2)} (${data.change >= 0 ? '+' : ''}${data.change.toFixed(2)})`)
              .join('\n');
            botResponse = `📈 Current Market Indices:\n${marketSummary}`;
          } catch (error) {
            botResponse = 'I\'m having trouble fetching market data right now. Please try again in a moment.';
          }
        } else if (currentInput.toLowerCase().includes('portfolio') || currentInput.toLowerCase().includes('holdings')) {
          botResponse = '💼 I can help you analyze your portfolio! You can view your current holdings in the Portfolio tab, or ask me about specific stocks in your portfolio.';
        } else if (currentInput.toLowerCase().includes('news')) {
          botResponse = '📰 You can find the latest market news and indices data in the News tab. I can also provide real-time updates on specific stocks or market sectors.';
        } else {
          botResponse = '🤖 I\'m connected to real-time financial data! I can help you with:\n• Stock prices and quotes\n• Market indices data\n• Portfolio analysis\n• Financial news updates\n\nWhat would you like to know?';
        }

        const botMessage = {
          id: messages.length + 2,
          sender: 'bot',
          avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAhcdULi2aIU9o-tEaA4KQaeG6ml4hm-vB3Q29CE5T5BzER7O_tTPSUbvRvUiQ0tz0L-3-98s6BaP2NhOeqe1T0HkvGq6EemolEiOk4bkeYi1Gn2I-0Xa0MofYMoOm-CyNNX_bTpHpFn3xoasaNitL540xBcDcjbKEOeG8Xv7Q-Qqa_lPbbWBiJcabBwhCAdiwPP7z8EMquMZnHoGkSRRjqpeI3-_gQwQDqTxZ0OroQtFldDujrDlPVl9zdpLqFbZreUwSxzPixPDG4',
          name: 'Finance Bot',
          text: botResponse,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };

        setMessages(prev => [...prev, botMessage]);

      } catch (error) {
        console.error('Error in chat:', error);
        const errorMessage = {
          id: messages.length + 2,
          sender: 'bot',
          avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAhcdULi2aIU9o-tEaA4KQaeG6ml4hm-vB3Q29CE5T5BzER7O_tTPSUbvRvUiQ0tz0L-3-98s6BaP2NhOeqe1T0HkvGq6EemolEiOk4bkeYi1Gn2I-0Xa0MofYMoOm-CyNNX_bTpHpFn3xoasaNitL540xBcDcjbKEOeG8Xv7Q-Qqa_lPbbWBiJcabBwhCAdiwPP7z8EMquMZnHoGkSRRjqpeI3-_gQwQDqTxZ0OroQtFldDujrDlPVl9zdpLqFbZreUwSxzPixPDG4',
          name: 'Finance Bot',
          text: 'I apologize, but I\'m experiencing technical difficulties. Please try again in a moment.',
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        setMessages(prev => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    }
  };

  // Helper function to extract stock symbol from message
  const extractStockSymbol = (message) => {
    const words = message.toUpperCase().split(' ');
    const stockSymbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'JPM', 'JNJ', 'V', 'WMT', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'PYPL', 'ADBE', 'CRM', 'XOM', 'BAC', 'KO', 'NKE', 'MCD', 'ABT', 'COST', 'TXN', 'LLY', 'WFC'];

    for (const word of words) {
      if (stockSymbols.includes(word)) {
        return word;
      }
    }
    return null;
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="flex h-screen flex-col">
      <Header title="Chatbot" showBackButton={true} />
      <main className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start gap-3 ${
              message.sender === 'user' ? 'justify-end' : ''
            }`}
          >
            {message.sender === 'bot' && (
              <div className="flex-shrink-0">
                <img
                  alt={`${message.name} Avatar`}
                  className="w-8 h-8 rounded-full"
                  src={message.avatar}
                />
              </div>
            )}
            <div className={`flex flex-col gap-1 ${message.sender === 'user' ? 'items-end' : ''}`}>
              <span className="text-sm text-white/50">{message.name}</span>
              <div
                className={`p-3 rounded-lg rounded-bl-none max-w-xs ${
                  message.sender === 'user'
                    ? 'bg-primary text-black rounded-br-none'
                    : 'bg-primary/20 dark:bg-primary/10 text-white'
                }`}
              >
                <p className="text-white whitespace-pre-line">{message.text}</p>
              </div>
            </div>
            {message.sender === 'user' && (
              <div className="flex-shrink-0">
                <img
                  alt={`${message.name} Avatar`}
                  className="w-8 h-8 rounded-full"
                  src={message.avatar}
                />
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0">
              <img
                alt="Finance Bot Avatar"
                className="w-8 h-8 rounded-full"
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuAhcdULi2aIU9o-tEaA4KQaeG6ml4hm-vB3Q29CE5T5BzER7O_tTPSUbvRvUiQ0tz0L-3-98s6BaP2NhOeqe1T0HkvGq6EemolEiOk4bkeYi1Gn2I-0Xa0MofYMoOm-CyNNX_bTpHpFn3xoasaNitL540xBcDcjbKEOeG8Xv7Q-Qqa_lPbbWBiJcabBwhCAdiwPP7z8EMquMZnHoGkSRRjqpeI3-_gQwQDqTxZ0OroQtFldDujrDlPVl9zdpLqFbZreUwSxzPixPDG4"
              />
            </div>
            <div className="flex flex-col gap-1">
              <span className="text-sm text-white/50">Finance Bot</span>
              <div className="p-3 rounded-lg rounded-bl-none max-w-xs bg-primary/20 dark:bg-primary/10 text-white">
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <p className="text-white">Analyzing your request...</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
      <footer className="bg-background-light dark:bg-background-dark">
        <div className="px-4 py-3">
          <div className="flex items-center bg-primary/20 dark:bg-primary/10 rounded-lg">
            <input
              className="form-input flex-1 bg-transparent border-none text-white placeholder-white/50 focus:ring-0"
              placeholder="Type your message..."
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
            />
            <button className="p-2 text-white/50 hover:text-white">
              <svg fill="currentColor" height="20" viewBox="0 0 256 256" width="20" xmlns="http://www.w3.org/2000/svg">
                <path d="M216,40H40A16,16,0,0,0,24,56V200a16,16,0,0,0,16,16H216a16,16,0,0,0,16-16V56A16,16,0,0,0,216,40Zm0,16V158.75l-26.07-26.06a16,16,0,0,0-22.63,0l-20,20-44-44a16,16,0,0,0-22.62,0L40,149.37V56ZM40,172l52-52,80,80H40Zm176,28H194.63l-36-36,20-20L216,181.38V200ZM144,100a12,12,0,1,1,12,12A12,12,0,0,1,144,100Z"></path>
              </svg>
            </button>
            <button
              className="bg-primary text-black font-bold py-2 px-4 rounded-lg m-1"
              onClick={handleSendMessage}
            >
              Send
            </button>
          </div>
        </div>
        <Navigation />
      </footer>
    </div>
  );
};

export default Chatbot;