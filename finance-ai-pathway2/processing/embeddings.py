"""
Embeddings and Vector Processing Module
Handles text embeddings and vector operations for RAG
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
import logging
import os
from datetime import datetime
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingModel(ABC):
    """Abstract base class for embedding models"""

    @abstractmethod
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts into embeddings"""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """Get embedding dimension"""
        pass

class SimpleEmbeddingModel(EmbeddingModel):
    """Simple embedding model for demonstration (not for production)"""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension

    def encode(self, texts: List[str]) -> np.ndarray:
        """Create simple hash-based embeddings"""
        embeddings = []

        for text in texts:
            # Create deterministic but varied embeddings based on text content
            words = text.lower().split()[:50]  # Take first 50 words
            embedding = []

            for i in range(self.dimension):
                # Create a pseudo-random but deterministic value based on text content
                hash_input = f"{text}_{i}_{len(words)}"
                hash_val = hash(hash_input) % 1000 / 1000.0
                embedding.append(hash_val)

            embeddings.append(embedding)

        return np.array(embeddings)

    def get_dimension(self) -> int:
        return self.dimension

class SentenceTransformerModel(EmbeddingModel):
    """Sentence transformer model for production use"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
            self.model_name = model_name
        except ImportError:
            logger.warning("sentence-transformers not available, falling back to simple model")
            self.model = SimpleEmbeddingModel()
            self.model_name = "simple"

    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts using sentence transformer"""
        if isinstance(self.model, SimpleEmbeddingModel):
            return self.model.encode(texts)
        else:
            return self.model.encode(texts)

    def get_dimension(self) -> int:
        if isinstance(self.model, SimpleEmbeddingModel):
            return self.model.get_dimension()
        else:
            dimension = self.model.get_sentence_embedding_dimension()
            return dimension if dimension is not None else 384  # fallback dimension

class VectorIndex:
    """Simple vector index for similarity search"""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self.vectors = []
        self.metadata = []
        self.index_built = False

    def add_vectors(self, vectors: np.ndarray, metadata: List[Dict[str, Any]]):
        """Add vectors to the index"""
        if vectors.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension {vectors.shape[1]} doesn't match index dimension {self.dimension}")

        self.vectors.extend(vectors)
        self.metadata.extend(metadata)
        self.index_built = False

    def build_index(self):
        """Build the vector index (simplified)"""
        if not self.vectors:
            logger.warning("No vectors to build index")
            return

        self.vectors_array = np.array(self.vectors)
        self.index_built = True
        logger.info(f"Built index with {len(self.vectors)} vectors")

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        """Search for similar vectors"""
        if not self.index_built:
            self.build_index()

        if not self.index_built or len(self.vectors) == 0:
            return []

        # Calculate cosine similarity
        query_norm = np.linalg.norm(query_vector)
        vectors_norm = np.linalg.norm(self.vectors_array, axis=1)

        if query_norm == 0 or np.any(vectors_norm == 0):
            return []

        similarities = np.dot(self.vectors_array, query_vector) / (vectors_norm * query_norm)

        # Get top-k results
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append((float(similarities[idx]), self.metadata[idx]))

        return results

class TextProcessor:
    """Handles text preprocessing for embeddings"""

    def __init__(self):
        self.stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him',
            'her', 'us', 'them', 'my', 'your', 'his', 'its', 'our', 'their',
            'mine', 'yours', 'hers', 'ours', 'theirs'
        }

    def preprocess_text(self, text: str) -> str:
        """Preprocess text for better embeddings"""
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Remove special characters but keep financial terms
        text = ''.join(c for c in text if c.isalnum() or c in ' .,-%$')

        # Remove stop words (optional - sometimes hurts financial text understanding)
        # words = [word for word in text.split() if word not in self.stop_words]
        # text = ' '.join(words)

        return text.strip()

    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []

        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)

        return chunks

class EmbeddingManager:
    """Manages embeddings for different types of content"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.embedding_model = SentenceTransformerModel(model_name)
        self.text_processor = TextProcessor()
        self.vector_index = VectorIndex(self.embedding_model.get_dimension())

    def create_news_embedding(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """Create embedding for a news item"""
        # Combine title and summary for embedding
        text = f"{news_item.get('title', '')} {news_item.get('summary', '')}"

        # Preprocess text
        processed_text = self.text_processor.preprocess_text(text)

        # Create embedding
        embedding = self.embedding_model.encode([processed_text])[0]

        # Add embedding to news item
        news_item['embedding'] = embedding.tolist()
        news_item['text_processed'] = processed_text

        return news_item

    def create_stock_embedding(self, stock_item: Dict[str, Any]) -> Dict[str, Any]:
        """Create embedding for stock information"""
        # Create text representation of stock data
        text = f"{stock_item.get('name', '')} {stock_item.get('sector', '')} stock price {stock_item.get('price', 0)} change {stock_item.get('change_percent', 0)}%"

        # Preprocess text
        processed_text = self.text_processor.preprocess_text(text)

        # Create embedding
        embedding = self.embedding_model.encode([processed_text])[0]

        # Add embedding to stock item
        stock_item['embedding'] = embedding.tolist()
        stock_item['text_processed'] = processed_text

        return stock_item

    def build_search_index(self, items: List[Dict[str, Any]], item_type: str = 'news'):
        """Build search index from items"""
        vectors = []
        metadata = []

        for item in items:
            if item_type == 'news':
                processed_item = self.create_news_embedding(item)
            elif item_type == 'stock':
                processed_item = self.create_stock_embedding(item)
            else:
                continue

            if 'embedding' in processed_item:
                vectors.append(processed_item['embedding'])
                metadata.append(processed_item)

        if vectors:
            self.vector_index.add_vectors(np.array(vectors), metadata)
            self.vector_index.build_index()

        logger.info(f"Built search index with {len(vectors)} {item_type} items")

    def search_similar(self, query: str, top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        """Search for similar items given a query"""
        # Preprocess query
        processed_query = self.text_processor.preprocess_text(query)

        # Create query embedding
        query_embedding = self.embedding_model.encode([processed_query])[0]

        # Search
        results = self.vector_index.search(query_embedding, top_k)

        return results

    def get_embedding_dimension(self) -> int:
        """Get embedding dimension"""
        return self.embedding_model.get_dimension()

# Global embedding manager
embedding_manager = EmbeddingManager()

def create_embeddings_for_news(news_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create embeddings for news data"""
    return [embedding_manager.create_news_embedding(item) for item in news_data]

def create_embeddings_for_stocks(stock_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Create embeddings for stock data"""
    return [embedding_manager.create_stock_embedding(item) for item in stock_data]

def search_news(query: str, top_k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
    """Search news using embeddings"""
    return embedding_manager.search_similar(query, top_k)

if __name__ == "__main__":
    # Test the embedding system
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

    # Create embeddings
    embedded_news = create_embeddings_for_news(sample_news)
    print(f"Created embeddings for {len(embedded_news)} news items")

    # Build search index
    embedding_manager.build_search_index(embedded_news, 'news')

    # Test search
    results = search_news("Apple earnings", top_k=2)
    print(f"Search results: {len(results)} items found")

    for score, item in results:
        print(f"- {item['title']} (similarity: {score:.3f})")