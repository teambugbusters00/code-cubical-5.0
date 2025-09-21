"""
RAG Pipeline Module
Handles Retrieval-Augmented Generation for financial queries
"""

import os
import logging
import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGPipeline:
    """Retrieval-Augmented Generation pipeline for financial data"""

    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

        # Import here to handle optional dependencies
        try:
            import openai
            self.openai_client = openai.OpenAI(api_key=self.openai_api_key)
            self.openai_available = True
        except ImportError:
            logger.warning("OpenAI not available - RAG will use fallback responses")
            self.openai_client = None
            self.openai_available = False

        # Import search engine
        from processing.indexing import search_engine

        self.search_engine = search_engine

    async def query(self, user_query: str, context_limit: int = 5) -> Dict[str, Any]:
        """Process a user query using RAG"""
        try:
            logger.info(f"Processing RAG query: {user_query}")

            # Step 1: Retrieve relevant context
            context_docs = await self._retrieve_context(user_query, context_limit)

            # Step 2: Generate response using context
            response = await self._generate_response(user_query, context_docs)

            # Step 3: Format and return result
            result = {
                'query': user_query,
                'response': response,
                'context_docs': context_docs,
                'timestamp': datetime.now().isoformat(),
                'model_used': self.openai_model if self.openai_available else 'fallback'
            }

            return result

        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            return {
                'query': user_query,
                'response': f"I apologize, but I encountered an error processing your query: {str(e)}",
                'context_docs': [],
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

    async def _retrieve_context(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant context documents for the query"""
        try:
            # Search across all document types
            search_results = self.search_engine.search(query, top_k=limit)

            # Format context documents
            context_docs = []
            for score, doc in search_results:
                context_doc = {
                    'content': self._format_document_content(doc),
                    'score': score,
                    'doc_type': doc.get('doc_type', 'unknown'),
                    'metadata': {
                        'symbol': doc.get('symbol', ''),
                        'title': doc.get('title', doc.get('name', '')),
                        'sentiment_score': doc.get('sentiment_score', 0),
                        'published_at': doc.get('published_at', ''),
                        'sector': doc.get('sector', ''),
                        'price': doc.get('price', 0)
                    }
                }
                context_docs.append(context_doc)

            logger.info(f"Retrieved {len(context_docs)} context documents")
            return context_docs

        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    def _format_document_content(self, doc: Dict[str, Any]) -> str:
        """Format document content for context"""
        if doc.get('doc_type') == 'news':
            return f"News: {doc.get('title', '')} - {doc.get('summary', '')}"
        elif doc.get('doc_type') == 'stock':
            return f"Stock: {doc.get('name', '')} ({doc.get('symbol', '')}) - Price: ${doc.get('price', 0):.2f}, Sector: {doc.get('sector', '')}"
        elif doc.get('doc_type') == 'portfolio':
            return f"Portfolio: {doc.get('company_name', '')} ({doc.get('symbol', '')}) - Shares: {doc.get('shares', 0)}, Value: ${doc.get('market_value', 0):.2f}"
        else:
            return str(doc)

    async def _generate_response(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """Generate response using retrieved context"""
        if not self.openai_available:
            return self._generate_fallback_response(query, context_docs)

        try:
            # Prepare context for OpenAI
            context_text = self._prepare_context_text(context_docs)

            # Create system prompt
            system_prompt = self._create_system_prompt()

            # Create user prompt
            user_prompt = f"Context:\n{context_text}\n\nQuery: {query}"

            # Call OpenAI API
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model=self.openai_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=500,
                    temperature=0.3
                )

                return response.choices[0].message.content.strip()
            else:
                return self._generate_fallback_response(query, context_docs)

        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            return self._generate_fallback_response(query, context_docs)

    def _generate_fallback_response(self, query: str, context_docs: List[Dict[str, Any]]) -> str:
        """Generate fallback response when OpenAI is not available"""
        if not context_docs:
            return "I don't have enough information to answer your query. Please try rephrasing or ask about specific stocks."

        # Simple rule-based response generation
        response_parts = []

        # Analyze context for key information
        positive_news = [doc for doc in context_docs if doc['metadata'].get('sentiment_score', 0) > 0.1]
        negative_news = [doc for doc in context_docs if doc['metadata'].get('sentiment_score', 0) < -0.1]

        # Generate response based on query type
        query_lower = query.lower()

        if 'price' in query_lower or 'stock' in query_lower:
            stock_docs = [doc for doc in context_docs if doc['doc_type'] == 'stock']
            if stock_docs:
                doc = stock_docs[0]
                symbol = doc['metadata'].get('symbol', 'Unknown')
                price = doc['metadata'].get('price', 0)
                response_parts.append(f"The current price for {symbol} is ${price:.2f}")

        if 'news' in query_lower or 'happening' in query_lower:
            if positive_news:
                response_parts.append(f"Good news: {positive_news[0]['content']}")
            if negative_news:
                response_parts.append(f"Concerning news: {negative_news[0]['content']}")

        if 'portfolio' in query_lower:
            portfolio_docs = [doc for doc in context_docs if doc['doc_type'] == 'portfolio']
            if portfolio_docs:
                total_value = sum(doc['metadata'].get('market_value', 0) for doc in portfolio_docs)
                response_parts.append(f"Portfolio value: ${total_value:.2f}")

        if not response_parts:
            response_parts.append("Based on the available information:")
            if context_docs:
                response_parts.append(context_docs[0]['content'])
            else:
                response_parts.append("No context information available.")

        return ". ".join(response_parts) + "."

    def _prepare_context_text(self, context_docs: List[Dict[str, Any]]) -> str:
        """Prepare context text for OpenAI"""
        context_parts = []

        for i, doc in enumerate(context_docs, 1):
            content = doc['content']
            score = doc['score']
            doc_type = doc['doc_type']

            context_parts.append(f"[{i}] ({doc_type}, relevance: {score:.2f}) {content}")

        return "\n".join(context_parts) if context_parts else ""

    def _create_system_prompt(self) -> str:
        """Create system prompt for financial assistant"""
        return """You are a knowledgeable financial assistant AI. Your role is to provide helpful, accurate, and insightful responses about financial markets, stocks, and investment information.

Guidelines:
- Be informative and provide specific data when available
- Explain financial concepts clearly
- Be neutral and factual - don't give investment advice
- Use the provided context to inform your response
- If you don't have enough information, say so clearly
- Format numbers and prices appropriately
- Be concise but comprehensive

You have access to real-time financial data including:
- Stock prices and market data
- Financial news and sentiment analysis
- Portfolio information
- Market indices and sector data

Always base your responses on the provided context and be transparent about data sources."""

    async def analyze_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Analyze sentiment for a specific symbol"""
        try:
            # Search for news related to the symbol
            news_results = self.search_engine.search(symbol, top_k=10, doc_types=['news'])

            if not news_results:
                return {
                    'symbol': symbol,
                    'sentiment_score': 0.0,
                    'sentiment_label': 'neutral',
                    'news_count': 0,
                    'analysis': 'No recent news found for analysis'
                }

            # Calculate average sentiment
            sentiment_scores = [doc.get('sentiment_score', 0) for _, doc in news_results]
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0

            # Determine sentiment label
            if avg_sentiment > 0.1:
                sentiment_label = 'positive'
            elif avg_sentiment < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'

            # Get recent news for context
            recent_news = [doc for _, doc in news_results[:3]]

            return {
                'symbol': symbol,
                'sentiment_score': round(avg_sentiment, 3),
                'sentiment_label': sentiment_label,
                'news_count': len(news_results),
                'recent_news': recent_news,
                'analysis': f"Based on {len(news_results)} recent news articles, sentiment is {sentiment_label} with score {avg_sentiment:.3f}"
            }

        except Exception as e:
            logger.error(f"Error analyzing sentiment for {symbol}: {e}")
            return {
                'symbol': symbol,
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'news_count': 0,
                'analysis': f'Error analyzing sentiment: {str(e)}'
            }

    async def get_portfolio_insights(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate insights for a portfolio"""
        try:
            # Get symbols from portfolio
            symbols = [holding['symbol'] for holding in portfolio_data.get('holdings', [])]

            if not symbols:
                return {
                    'portfolio_value': portfolio_data.get('total_value', 0),
                    'insights': 'No holdings found in portfolio',
                    'recommendations': []
                }

            # Get news for portfolio symbols
            all_insights = []
            for symbol in symbols:
                sentiment_analysis = await self.analyze_sentiment(symbol)
                all_insights.append({
                    'symbol': symbol,
                    'sentiment': sentiment_analysis
                })

            # Generate portfolio-level insights
            positive_count = sum(1 for insight in all_insights if insight['sentiment']['sentiment_label'] == 'positive')
            negative_count = sum(1 for insight in all_insights if insight['sentiment']['sentiment_label'] == 'negative')

            insights = []
            if positive_count > len(symbols) / 2:
                insights.append("Overall positive sentiment across portfolio holdings")
            elif negative_count > len(symbols) / 2:
                insights.append("Overall negative sentiment across portfolio holdings")
            else:
                insights.append("Mixed sentiment across portfolio holdings")

            # Sector analysis
            sector_allocation = portfolio_data.get('sector_allocation', {})
            top_sector = max(sector_allocation.items(), key=lambda x: x[1]) if sector_allocation else ('None', 0)
            insights.append(f"Top sector allocation: {top_sector[0]} ({top_sector[1]:.1f}%)")

            return {
                'portfolio_value': portfolio_data.get('total_value', 0),
                'total_holdings': len(symbols),
                'positive_sentiment_count': positive_count,
                'negative_sentiment_count': negative_count,
                'insights': insights,
                'symbol_insights': all_insights
            }

        except Exception as e:
            logger.error(f"Error generating portfolio insights: {e}")
            return {
                'portfolio_value': portfolio_data.get('total_value', 0),
                'insights': f'Error generating insights: {str(e)}',
                'recommendations': []
            }

# Global RAG pipeline instance
rag_pipeline = RAGPipeline()

async def query_financial_data(user_query: str, context_limit: int = 5) -> Dict[str, Any]:
    """Query financial data using RAG pipeline"""
    return await rag_pipeline.query(user_query, context_limit)

async def analyze_stock_sentiment(symbol: str) -> Dict[str, Any]:
    """Analyze sentiment for a specific stock"""
    return await rag_pipeline.analyze_sentiment(symbol)

if __name__ == "__main__":
    async def main():
        # Test the RAG pipeline
        print("Testing RAG pipeline...")

        # Test query
        result = await query_financial_data("What is happening with Apple stock?", context_limit=3)
        print(f"Query result: {result['response']}")

        # Test sentiment analysis
        sentiment = await analyze_stock_sentiment("AAPL")
        print(f"Apple sentiment: {sentiment['sentiment_label']} ({sentiment['sentiment_score']})")

        asyncio.run(main())