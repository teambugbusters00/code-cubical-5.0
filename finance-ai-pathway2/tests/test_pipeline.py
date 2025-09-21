"""
Tests for data processing pipeline and RAG components
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import pipeline modules
from processing.pipeline import FinancialDataPipeline
from processing.embeddings import TextEmbeddings
from processing.indexing import VectorIndexing
from rag.rag_pipeline import RAGPipeline
from rag.llm_config import LLMConfig


class TestFinancialDataPipeline:
    """Test Pathway-based data processing pipeline"""

    @pytest.fixture
    def pipeline(self):
        return FinancialDataPipeline()

    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initialization"""
        assert pipeline is not None
        assert hasattr(pipeline, 'process_stock_data')
        assert hasattr(pipeline, 'process_news_data')

    @pytest.mark.asyncio
    async def test_process_stock_data(self, pipeline):
        """Test stock data processing"""
        # Mock stock data
        stock_data = pd.DataFrame({
            'symbol': ['AAPL', 'AAPL', 'MSFT'],
            'price': [150.0, 151.0, 300.0],
            'volume': [1000000, 1100000, 800000],
            'timestamp': [datetime.now(), datetime.now(), datetime.now()]
        })

        with patch('processing.pipeline.pw.run') as mock_run:
            mock_run.return_value = stock_data

            result = await pipeline.process_stock_data(stock_data)

            assert result is not None
            assert len(result) > 0

    @pytest.mark.asyncio
    async def test_process_news_data(self, pipeline):
        """Test news data processing"""
        # Mock news data
        news_data = pd.DataFrame({
            'title': ['Apple releases new iPhone', 'Market volatility increases'],
            'content': ['Apple announced...', 'Market conditions...'],
            'sentiment_score': [0.8, -0.3],
            'timestamp': [datetime.now(), datetime.now()]
        })

        with patch('processing.pipeline.pw.run') as mock_run:
            mock_run.return_value = news_data

            result = await pipeline.process_news_data(news_data)

            assert result is not None
            assert len(result) > 0

    def test_error_handling(self, pipeline):
        """Test pipeline error handling"""
        # Test with invalid data
        invalid_data = None

        # Should handle errors gracefully
        result = asyncio.run(pipeline.process_stock_data(invalid_data))
        assert result is not None or result == []


class TestTextEmbeddings:
    """Test text embedding functionality"""

    @pytest.fixture
    def embeddings(self):
        return TextEmbeddings()

    def test_embeddings_initialization(self, embeddings):
        """Test embeddings initialization"""
        assert embeddings is not None
        assert hasattr(embeddings, 'generate_embedding')
        assert hasattr(embeddings, 'batch_generate_embeddings')

    def test_generate_embedding(self, embeddings):
        """Test single text embedding generation"""
        text = "Apple stock is performing well"

        with patch('processing.embeddings.sentence_transformers') as mock_st:
            mock_model = Mock()
            mock_model.encode.return_value = np.array([0.1, 0.2, 0.3])
            mock_st.SentenceTransformer.return_value = mock_model

            result = embeddings.generate_embedding(text)

            assert result is not None
            assert isinstance(result, np.ndarray)
            assert len(result) > 0

    def test_batch_generate_embeddings(self, embeddings):
        """Test batch embedding generation"""
        texts = [
            "Apple stock is performing well",
            "Market volatility increases",
            "Tesla announces new product"
        ]

        with patch('processing.embeddings.sentence_transformers') as mock_st:
            mock_model = Mock()
            mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]])
            mock_st.SentenceTransformer.return_value = mock_model

            result = embeddings.batch_generate_embeddings(texts)

            assert result is not None
            assert isinstance(result, np.ndarray)
            assert result.shape[0] == len(texts)

    def test_embedding_dimensions(self, embeddings):
        """Test embedding dimensions"""
        text = "Test text for embedding"

        with patch('processing.embeddings.sentence_transformers') as mock_st:
            mock_model = Mock()
            mock_model.encode.return_value = np.array([0.1] * 384)  # 384 dimensions
            mock_st.SentenceTransformer.return_value = mock_model

            result = embeddings.generate_embedding(text)

            assert result is not None
            assert len(result) == 384  # Standard sentence transformer dimension


class TestVectorIndexing:
    """Test vector indexing and search functionality"""

    @pytest.fixture
    def vector_index(self):
        return VectorIndexing()

    def test_index_initialization(self, vector_index):
        """Test vector index initialization"""
        assert vector_index is not None
        assert hasattr(vector_index, 'add_documents')
        assert hasattr(vector_index, 'search_similar')

    def test_add_documents(self, vector_index):
        """Test adding documents to index"""
        documents = [
            {
                'id': 'doc1',
                'text': 'Apple stock analysis',
                'metadata': {'symbol': 'AAPL', 'type': 'analysis'}
            },
            {
                'id': 'doc2',
                'text': 'Market news update',
                'metadata': {'symbol': 'SPY', 'type': 'news'}
            }
        ]

        embeddings = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])

        with patch('processing.indexing.FAISS') as mock_faiss:
            mock_index = Mock()
            mock_faiss.IndexFlatL2.return_value = mock_index

            result = vector_index.add_documents(documents, embeddings)

            assert result is not None
            assert vector_index.index is not None

    def test_search_similar(self, vector_index):
        """Test similarity search"""
        query_embedding = np.array([0.1, 0.2, 0.3])
        documents = [
            {'id': 'doc1', 'text': 'Apple stock analysis', 'metadata': {'symbol': 'AAPL'}},
            {'id': 'doc2', 'text': 'Market news update', 'metadata': {'symbol': 'SPY'}}
        ]

        with patch('processing.indexing.FAISS') as mock_faiss:
            mock_index = Mock()
            mock_index.search.return_value = (np.array([[0.1, 0.2]]), np.array([[0, 1]]))
            mock_faiss.IndexFlatL2.return_value = mock_index
            vector_index.index = mock_index
            vector_index.documents = documents

            result = vector_index.search_similar(query_embedding, top_k=2)

            assert result is not None
            assert len(result) <= 2
            assert isinstance(result[0], tuple)
            assert len(result[0]) == 2  # (score, document)

    def test_index_persistence(self, vector_index):
        """Test saving and loading index"""
        with patch('processing.indexing.FAISS') as mock_faiss:
            mock_index = Mock()
            mock_faiss.IndexFlatL2.return_value = mock_index
            vector_index.index = mock_index

            # Test save
            with patch('builtins.open', Mock()) as mock_file:
                vector_index.save_index('test_index.faiss')
                mock_index.train.assert_called()

            # Test load
            with patch('processing.indexing.FAISS.read_index') as mock_read:
                mock_read.return_value = mock_index
                loaded_index = VectorIndexing.load_index('test_index.faiss')
                assert loaded_index is not None


class TestRAGPipeline:
    """Test RAG pipeline functionality"""

    @pytest.fixture
    def rag_pipeline(self):
        return RAGPipeline()

    def test_rag_initialization(self, rag_pipeline):
        """Test RAG pipeline initialization"""
        assert rag_pipeline is not None
        assert hasattr(rag_pipeline, 'query')
        assert hasattr(rag_pipeline, 'analyze_sentiment')

    @pytest.mark.asyncio
    async def test_query_functionality(self, rag_pipeline):
        """Test RAG query functionality"""
        query = "What is the current price of Apple stock?"

        with patch('rag.rag_pipeline.openai.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Apple stock is currently trading at $150 per share"))]
            mock_client.return_value.chat.completions.create.return_value = mock_response

            result = await rag_pipeline.query(query)

            assert result is not None
            assert 'response' in result
            assert len(result['response']) > 0

    @pytest.mark.asyncio
    async def test_sentiment_analysis(self, rag_pipeline):
        """Test sentiment analysis functionality"""
        symbol = "AAPL"

        with patch('rag.rag_pipeline.news_ingestion') as mock_news:
            mock_news.get_company_specific_news.return_value = [
                {
                    'title': 'Apple stock rises on strong earnings',
                    'sentiment_score': 0.8,
                    'sentiment_label': 'positive'
                }
            ]

            result = await rag_pipeline.analyze_sentiment(symbol)

            assert result is not None
            assert 'symbol' in result
            assert 'sentiment_label' in result
            assert result['symbol'] == symbol

    @pytest.mark.asyncio
    async def test_portfolio_insights(self, rag_pipeline):
        """Test portfolio insights functionality"""
        portfolio_data = {
            'holdings': [
                {
                    'symbol': 'AAPL',
                    'shares': 100,
                    'avg_cost': 150.0
                }
            ],
            'total_value': 15000.0
        }

        with patch('rag.rag_pipeline.openai.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="Your portfolio shows good diversification with tech stocks"))]
            mock_client.return_value.chat.completions.create.return_value = mock_response

            result = await rag_pipeline.get_portfolio_insights(portfolio_data)

            assert result is not None
            assert 'insights' in result
            assert 'recommendations' in result

    def test_context_retrieval(self, rag_pipeline):
        """Test context retrieval for queries"""
        query = "Apple stock analysis"

        with patch('rag.rag_pipeline.vector_index') as mock_index:
            mock_index.search_similar.return_value = [
                (0.9, {'text': 'Apple is performing well', 'metadata': {'symbol': 'AAPL'}}),
                (0.8, {'text': 'Market analysis shows growth', 'metadata': {'symbol': 'SPY'}})
            ]

            context = rag_pipeline._retrieve_context(query)

            assert context is not None
            assert len(context) > 0
            assert 'text' in context[0]


class TestLLMConfig:
    """Test LLM configuration"""

    @pytest.fixture
    def llm_config(self):
        return LLMConfig()

    def test_config_initialization(self, llm_config):
        """Test LLM configuration initialization"""
        assert llm_config is not None
        assert hasattr(llm_config, 'model')
        assert hasattr(llm_config, 'temperature')
        assert hasattr(llm_config, 'max_tokens')

    def test_config_validation(self, llm_config):
        """Test configuration validation"""
        # Test valid config
        assert llm_config.validate_config()

        # Test invalid model
        llm_config.model = "invalid-model"
        assert not llm_config.validate_config()

        # Reset to valid
        llm_config.model = "gpt-4o-mini"
        assert llm_config.validate_config()

    def test_config_serialization(self, llm_config):
        """Test configuration serialization"""
        config_dict = llm_config.to_dict()

        assert isinstance(config_dict, dict)
        assert 'model' in config_dict
        assert 'temperature' in config_dict
        assert 'max_tokens' in config_dict

        # Test deserialization
        new_config = LLMConfig.from_dict(config_dict)
        assert new_config.openai_model == llm_config.openai_model
        assert new_config.temperature == llm_config.temperature


class TestPipelineIntegration:
    """Integration tests for the entire pipeline"""

    @pytest.mark.asyncio
    async def test_full_data_processing_pipeline(self):
        """Test complete data processing workflow"""
        pipeline = FinancialDataPipeline()

        # Mock input data
        stock_data = pd.DataFrame({
            'symbol': ['AAPL', 'MSFT'],
            'price': [150.0, 300.0],
            'volume': [1000000, 800000],
            'timestamp': [datetime.now(), datetime.now()]
        })

        news_data = pd.DataFrame({
            'title': ['Apple earnings report', 'Microsoft acquisition'],
            'content': ['Apple reports strong earnings...', 'Microsoft acquires company...'],
            'sentiment_score': [0.8, 0.6],
            'timestamp': [datetime.now(), datetime.now()]
        })

        # Process both data types
        stock_result = await pipeline.process_stock_data(stock_data)
        news_result = await pipeline.process_news_data(news_data)

        assert stock_result is not None
        assert news_result is not None

    @pytest.mark.asyncio
    async def test_rag_query_with_context(self):
        """Test RAG query with context retrieval"""
        rag_pipeline = RAGPipeline()

        query = "What is Apple's current stock performance?"

        # Mock context retrieval
        with patch.object(rag_pipeline, '_retrieve_context') as mock_retrieve:
            mock_retrieve.return_value = [
                {'text': 'Apple stock is up 5% this week', 'metadata': {'symbol': 'AAPL'}},
                {'text': 'Market shows positive sentiment for tech stocks', 'metadata': {'sector': 'Technology'}}
            ]

            # Mock LLM response
            with patch('rag.rag_pipeline.openai.AsyncClient') as mock_client:
                mock_response = Mock()
                mock_response.choices = [Mock(message=Mock(content="Based on recent data, Apple stock has shown positive performance with a 5% increase this week."))]
                mock_client.return_value.chat.completions.create.return_value = mock_response

                result = await rag_pipeline.query(query)

                assert result is not None
                assert 'response' in result
                assert 'context' in result
                assert len(result['context']) > 0

    def test_error_recovery(self):
        """Test error recovery mechanisms"""
        pipeline = FinancialDataPipeline()

        # Test with corrupted data
        corrupted_data = pd.DataFrame({
            'invalid_column': [1, 2, 3]
        })

        # Should handle errors gracefully
        result = asyncio.run(pipeline.process_stock_data(corrupted_data))
        assert result is not None

    def test_performance_monitoring(self):
        """Test performance monitoring"""
        import time

        pipeline = FinancialDataPipeline()

        # Mock data processing
        data = pd.DataFrame({
            'symbol': ['AAPL'] * 1000,
            'price': [150.0] * 1000,
            'volume': [1000000] * 1000,
            'timestamp': [datetime.now()] * 1000
        })

        start_time = time.time()
        result = asyncio.run(pipeline.process_stock_data(data))
        end_time = time.time()

        # Should complete within reasonable time
        processing_time = end_time - start_time
        assert processing_time < 10.0  # Less than 10 seconds for 1000 records
        assert result is not None


# Mock data for testing
MOCK_EMBEDDINGS = np.array([
    [0.1, 0.2, 0.3, 0.4],
    [0.5, 0.6, 0.7, 0.8],
    [0.9, 1.0, 1.1, 1.2]
])

MOCK_DOCUMENTS = [
    {
        'id': 'doc1',
        'text': 'Apple stock analysis and performance',
        'metadata': {'symbol': 'AAPL', 'type': 'analysis', 'timestamp': datetime.now().isoformat()}
    },
    {
        'id': 'doc2',
        'text': 'Market news and updates',
        'metadata': {'symbol': 'SPY', 'type': 'news', 'timestamp': datetime.now().isoformat()}
    },
    {
        'id': 'doc3',
        'text': 'Technology sector overview',
        'metadata': {'sector': 'Technology', 'type': 'report', 'timestamp': datetime.now().isoformat()}
    }
]

MOCK_QUERY_RESPONSE = {
    'response': 'Based on the latest data, Apple stock is performing well with positive market sentiment.',
    'context': [
        {'text': 'Apple reports strong Q4 earnings', 'score': 0.95},
        {'text': 'Market shows positive sentiment for tech stocks', 'score': 0.88}
    ],
    'confidence': 0.92,
    'timestamp': datetime.now().isoformat()
}