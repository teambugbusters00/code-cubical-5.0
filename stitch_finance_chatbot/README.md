# Finance AI Assistant

A comprehensive React-based frontend application for financial data analysis, portfolio management, and AI-powered chatbot assistance. Built with modern web technologies and designed for seamless user experience.

## 🚀 Features

### 🔐 Authentication System
- User registration and login
- JWT-based authentication
- Protected routes
- Persistent sessions

### 📊 Dashboard
- Portfolio overview with real-time data
- Market indices tracking
- Watchlist management
- Recent activity summary

### 🤖 AI Chatbot
- Real-time financial data integration
- Stock price queries
- Market analysis assistance
- Portfolio recommendations

### 📈 Stock Analysis
- Interactive stock charts (Recharts)
- Real-time price tracking
- Technical indicators
- Watchlist functionality
- Stock search and selection

### 📰 News & Market Data
- Real-time market indices
- Financial news integration
- Sentiment analysis
- Market trend visualization

### 💼 Portfolio Management
- Holdings tracking
- Performance analytics
- Profit/Loss calculations
- Portfolio diversification insights

### ⚙️ Settings & Preferences
- Dark/Light mode toggle
- Profile management
- Notification preferences
- Account security settings

## 🛠️ Tech Stack

- **React 18** - Modern React with hooks
- **React Router DOM** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls
- **Recharts** - Data visualization library
- **Lucide React** - Beautiful icons
- **Context API** - State management

## 📋 Prerequisites

- Node.js (v16 or higher)
- npm or yarn package manager
- FastAPI backend running on `http://localhost:8000`

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd finance-ai-assistant
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   Navigate to `http://localhost:3000`

## 📁 Project Structure

```
src/
├── api/                    # API service functions
├── components/            # Reusable UI components
│   ├── Header.js         # App header component
│   ├── Navigation.js     # Bottom navigation
│   └── ProtectedRoute.js # Route protection
├── context/              # React Context providers
│   └── AuthContext.js    # Authentication context
├── pages/                # Page components
│   ├── Login.js          # Login page
│   ├── Signup.js         # Registration page
│   ├── Dashboard.js      # Main dashboard
│   ├── StockDashboard.js # Stock analysis page
│   └── Settings.js       # Settings page
├── App.js               # Main app component
└── index.js             # App entry point
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_WS_BASE_URL=ws://localhost:8000/ws
```

### Tailwind Configuration
The app uses Tailwind CSS with custom configuration:

- Dark mode support via class strategy
- Custom color palette
- Extended typography and spacing

## 🎨 Styling

### Dark Mode
The application supports both light and dark themes:

- Toggle via Settings page
- Persistent user preference
- System preference detection

### Color Scheme
- **Primary**: `#38e07b` (Finance green)
- **Background Light**: `#f6f8f7`
- **Background Dark**: `#122017`

## 🔐 Authentication Flow

1. **Registration**: Create account with username, email, password
2. **Login**: JWT token stored in localStorage
3. **Protected Routes**: Automatic redirect to login if not authenticated
4. **Session Management**: Token validation on app load

## 📊 API Integration

The frontend connects to a FastAPI backend with the following endpoints:

- `/api/auth/login` - User authentication
- `/api/auth/signup` - User registration
- `/api/stocks/{symbol}/quote` - Stock quotes
- `/api/stocks/{symbol}/history` - Historical data
- `/api/market/indices` - Market indices
- `/api/chat` - Chatbot integration

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

### Deploy to Netlify/Vercel
1. Build the application
2. Deploy the `build` folder
3. Configure environment variables
4. Set up custom domain (optional)

## 🔧 Development

### Available Scripts
- `npm start` - Start development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### Code Quality
- ESLint configuration included
- Prettier formatting
- Component-based architecture

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop (1200px+)
- Tablet (768px - 1199px)
- Mobile (320px - 767px)

## 🔒 Security Features

- JWT token authentication
- Protected API routes
- Input validation and sanitization
- Secure localStorage usage
- HTTPS enforcement in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API documentation

## 🔄 Updates

The application supports:
- Real-time data updates
- WebSocket connections for live data
- Automatic refresh intervals
- Manual refresh options

---

**Built with ❤️ for the financial technology community**
