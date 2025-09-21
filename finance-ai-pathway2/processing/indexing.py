"""
Indexing Module
Handles vector indexing and search functionality for RAG
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging
import json
import os
from datetime import datetime
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStore:
    """Vector store for efficient similarity search"""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vectors = []
        self.metadata = []
        self.id_to_index = {}
        self.index_built = False

    def add(self, vector: List[float], metadata: Dict[str, Any], doc_id: Optional[str] = None):
        """Add a vector to the store"""
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension {len(vector)} doesn't match store dimension {self.dimension}")

        # Generate ID if not provided
        if doc_id is None:
            doc_id = f"doc_{len(self.vectors)}"

        self.vectors.append(vector)
        self.metadata.append(metadata)
        self.id_to_index[doc_id] = len(self.vectors) - 1
        self.index_built = False

    def build_index(self):
        """Build the vector index"""
        if not self.vectors:
            logger.warning("No vectors to build index")
            return

        self.vectors_array = np.array(self.vectors)
        self.index_built = True
        logger.info(f"Built vector index with {len(self.vectors)} vectors")

    def search(self, query_vector: List[float], top_k: int = 5, threshold: float = 0.0) -> List[Tuple[float, Dict[str, Any]]]:
        """Search for similar vectors"""
        if not self.index_built:
            self.build_index()

        if not self.index_built or len(self.vectors) == 0:
            return []

        query_array = np.array(query_vector)
        query_norm = np.linalg.norm(query_array)

        if query_norm == 0:
            return []

        # Calculate cosine similarities
        similarities = np.dot(self.vectors_array, query_array) / (np.linalg.norm(self.vectors_array, axis=1) * query_norm)

        # Get top-k results above threshold
        results = []
        for i, sim in enumerate(similarities):
            if sim >= threshold:
                results.append((float(sim), self.metadata[i]))

        # Sort by similarity and return top-k
        results.sort(key=lambda x: x[0], reverse=True)
        return results[:top_k]

    def save(self, filepath: str):
        """Save vector store to disk"""
        try:
            data = {
                'dimension': self.dimension,
                'vectors': self.vectors,
                'metadata': self.metadata,
                'id_to_index': self.id_to_index
            }

            with open(filepath, 'w') as f:
                json.dump(data, f)

            logger.info(f"Saved vector store to {filepath}")

        except Exception as e:
            logger.error(f"Error saving vector store: {e}")

    def load(self, filepath: str) -> bool:
        """Load vector store from disk"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            self.dimension = data['dimension']
            self.vectors = data['vectors']
            self.metadata = data['metadata']
            self.id_to_index = data['id_to_index']
            self.index_built = False

            logger.info(f"Loaded vector store from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False

class SearchEngine:
    """Main search engine for financial data"""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.news_store = VectorStore(dimension)
        self.stocks_store = VectorStore(dimension)
        self.portfolio_store = VectorStore(dimension)

        # Inverted index for keyword search
        self.keyword_index = defaultdict(list)

    def index_news(self, news_data: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Index news articles"""
        for i, (news_item, embedding) in enumerate(zip(news_data, embeddings)):
            doc_id = f"news_{i}"
            news_item['doc_id'] = doc_id
            news_item['doc_type'] = 'news'

            self.news_store.add(embedding, news_item, doc_id)

            # Build keyword index
            text = f"{news_item.get('title', '')} {news_item.get('summary', '')}"
            words = set(text.lower().split())
            for word in words:
                self.keyword_index[word].append(doc_id)

        logger.info(f"Indexed {len(news_data)} news articles")

    def index_stocks(self, stock_data: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Index stock information"""
        for i, (stock_item, embedding) in enumerate(zip(stock_data, embeddings)):
            doc_id = f"stock_{i}"
            stock_item['doc_id'] = doc_id
            stock_item['doc_type'] = 'stock'

            self.stocks_store.add(embedding, stock_item, doc_id)

            # Build keyword index
            text = f"{stock_item.get('name', '')} {stock_item.get('sector', '')}"
            words = set(text.lower().split())
            for word in words:
                self.keyword_index[word].append(doc_id)

        logger.info(f"Indexed {len(stock_data)} stock items")

    def index_portfolio(self, portfolio_data: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Index portfolio information"""
        for i, (portfolio_item, embedding) in enumerate(zip(portfolio_data, embeddings)):
            doc_id = f"portfolio_{i}"
            portfolio_item['doc_id'] = doc_id
            portfolio_item['doc_type'] = 'portfolio'

            self.portfolio_store.add(embedding, portfolio_item, doc_id)

        logger.info(f"Indexed {len(portfolio_data)} portfolio items")

    def search(self, query: str, top_k: int = 5, doc_types: Optional[List[str]] = None) -> List[Tuple[float, Dict[str, Any]]]:
        """Search across all indexed data"""
        if doc_types is None:
            doc_types = ['news', 'stock', 'portfolio']

        all_results = []

        # Vector search
        if 'news' in doc_types and len(self.news_store.vectors) > 0:
            # Create query embedding (simplified)
            query_embedding = self._create_query_embedding(query)
            news_results = self.news_store.search(query_embedding, top_k)
            all_results.extend(news_results)

        if 'stock' in doc_types and len(self.stocks_store.vectors) > 0:
            query_embedding = self._create_query_embedding(query)
            stock_results = self.stocks_store.search(query_embedding, top_k)
            all_results.extend(stock_results)

        if 'portfolio' in doc_types and len(self.portfolio_store.vectors) > 0:
            query_embedding = self._create_query_embedding(query)
            portfolio_results = self.portfolio_store.search(query_embedding, top_k)
            all_results.extend(portfolio_results)

        # Keyword search as fallback
        keyword_results = self._keyword_search(query, top_k)
        all_results.extend(keyword_results)

        # Remove duplicates and sort by score
        seen_ids = set()
        unique_results = []

        for score, item in sorted(all_results, key=lambda x: x[0], reverse=True):
            doc_id = item.get('doc_id')
            if doc_id and doc_id not in seen_ids:
                seen_ids.add(doc_id)
                unique_results.append((score, item))

        return unique_results[:top_k]

    def _create_query_embedding(self, query: str) -> List[float]:
        """Create embedding for query (simplified)"""
        # This would typically use the same embedding model as the documents
        # For now, create a simple deterministic embedding
        embedding = []
        for i in range(self.dimension):
            hash_val = hash(f"{query}_{i}") % 1000 / 1000.0
            embedding.append(hash_val)
        return embedding

    def _keyword_search(self, query: str, top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        """Perform keyword-based search"""
        query_words = set(query.lower().split())
        doc_scores = defaultdict(float)

        # Score documents based on keyword matches
        for word in query_words:
            if word in self.keyword_index:
                for doc_id in self.keyword_index[word]:
                    doc_scores[doc_id] += 1

        # Convert to results format
        results = []
        for doc_id, score in sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]:
            # Find the document in our stores
            for store in [self.news_store, self.stocks_store, self.portfolio_store]:
                if doc_id in store.id_to_index:
                    idx = store.id_to_index[doc_id]
                    metadata = store.metadata[idx]
                    results.append((score / len(query_words), metadata))  # Normalize score
                    break

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        return {
            'total_documents': len(self.news_store.vectors) + len(self.stocks_store.vectors) + len(self.portfolio_store.vectors),
            'news_documents': len(self.news_store.vectors),
            'stock_documents': len(self.stocks_store.vectors),
            'portfolio_documents': len(self.portfolio_store.vectors),
            'unique_keywords': len(self.keyword_index),
            'index_built': all(store.index_built for store in [self.news_store, self.stocks_store, self.portfolio_store])
        }

    def save_index(self, filepath: str):
        """Save search index to disk"""
        try:
            # Save vector stores
            self.news_store.save(f"{filepath}_news.json")
            self.stocks_store.save(f"{filepath}_stocks.json")
            self.portfolio_store.save(f"{filepath}_portfolio.json")

            # Save keyword index
            with open(f"{filepath}_keywords.json", 'w') as f:
                json.dump(dict(self.keyword_index), f)

            logger.info(f"Saved search index to {filepath}")

        except Exception as e:
            logger.error(f"Error saving search index: {e}")

    def load_index(self, filepath: str) -> bool:
        """Load search index from disk"""
        try:
            # Load vector stores
            self.news_store.load(f"{filepath}_news.json")
            self.stocks_store.load(f"{filepath}_stocks.json")
            self.portfolio_store.load(f"{filepath}_portfolio.json")

            # Load keyword index
            with open(f"{filepath}_keywords.json", 'r') as f:
                self.keyword_index.update(json.load(f))

            logger.info(f"Loaded search index from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error loading search index: {e}")
            return False

# Global search engine instance
search_engine = SearchEngine()

def search_financial_data(query: str, top_k: int = 5, doc_types: Optional[List[str]] = None) -> List[Tuple[float, Dict[str, Any]]]:
    """Search financial data using the global search engine"""
    return search_engine.search(query, top_k, doc_types)

def get_search_stats() -> Dict[str, Any]:
    """Get search engine statistics"""
    return search_engine.get_stats()

if __name__ == "__main__":
    # Test the search engine
    print("Testing search engine...")

    # Sample data
    sample_news = [
        {
            'title': 'Apple Reports Strong Q4 Earnings',
            'summary': 'Apple Inc. exceeded market expectations with robust quarterly performance',
            'symbol': 'AAPL',
            'sentiment_score': 0.85
        },
        {
            'title': 'Tesla Stock Declines on Production Concerns',
            'summary': 'Investors express concerns over Tesla production capabilities',
            'symbol': 'TSLA',
            'sentiment_score': -0.65
        }
    ]

    sample_stocks = [
        {
            'symbol': 'AAPL',
            'name': 'Apple Inc.',
            'sector': 'Technology',
            'price': 175.43
        },
        {
            'symbol': 'TSLA',
            'name': 'Tesla Inc.',
            'sector': 'Consumer Discretionary',
            'price': 248.50
        }
    ]

    # Create simple embeddings
    def create_simple_embedding(text: str) -> List[float]:
        embedding = []
        for i in range(384):
            hash_val = hash(f"{text}_{i}") % 1000 / 1000.0
            embedding.append(hash_val)
        return embedding

    news_embeddings = [create_simple_embedding(f"{item['title']} {item['summary']}") for item in sample_news]
    stock_embeddings = [create_simple_embedding(f"{item['name']} {item['sector']}") for item in sample_stocks]

    # Index data
    search_engine.index_news(sample_news, news_embeddings)
    search_engine.index_stocks(sample_stocks, stock_embeddings)

    # Test search
    results = search_financial_data("Apple earnings", top_k=3)
    print(f"Search results: {len(results)} items found")

    for score, item in results:
        print(f"- {item.get('title', item.get('name', 'Unknown'))} (score: {score:.3f})")

    # Print stats
    stats = get_search_stats()
    print(f"Search engine stats: {stats}")