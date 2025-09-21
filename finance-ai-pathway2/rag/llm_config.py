"""
LLM Configuration Module
Handles LLM setup and configuration for RAG pipeline
"""

import os
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMConfig:
    """Configuration for LLM models"""

    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '500'))
        self.temperature = float(os.getenv('TEMPERATURE', '0.3'))
        self.timeout = int(os.getenv('LLM_TIMEOUT', '30'))

        # Validate configuration
        self.validate_config()

    def validate_config(self):
        """Validate LLM configuration"""
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found - LLM features will be limited")

        if self.temperature < 0 or self.temperature > 2:
            logger.warning(f"Temperature {self.temperature} is outside recommended range (0-2)")
            self.temperature = max(0, min(2, self.temperature))

        if self.max_tokens < 1 or self.max_tokens > 4000:
            logger.warning(f"Max tokens {self.max_tokens} is outside recommended range (1-4000)")
            self.max_tokens = max(1, min(4000, self.max_tokens))

    def get_config_dict(self) -> Dict[str, Any]:
        """Get configuration as dictionary"""
        return {
            'model': self.openai_model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'timeout': self.timeout,
            'api_configured': bool(self.openai_api_key)
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'LLMConfig':
        """Create LLMConfig instance from dictionary"""
        config = cls.__new__(cls)  # Create instance without calling __init__

        config.openai_api_key = config_dict.get('openai_api_key', '')
        config.openai_model = config_dict.get('model', 'gpt-4o-mini')
        config.max_tokens = config_dict.get('max_tokens', 500)
        config.temperature = config_dict.get('temperature', 0.3)
        config.timeout = config_dict.get('timeout', 30)

        # Validate configuration
        config.validate_config()

        return config

class LLMClient(ABC):
    """Abstract base class for LLM clients"""

    @abstractmethod
    async def generate_response(self, messages: list, **kwargs) -> str:
        """Generate response from LLM"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if LLM client is available"""
        pass

class OpenAIClient(LLMClient):
    """OpenAI client for LLM interactions"""

    def __init__(self, config: LLMConfig):
        self.config = config
        self.client = None

        if config.openai_api_key:
            try:
                import openai
                self.client = openai.OpenAI(api_key=config.openai_api_key)
                logger.info("OpenAI client initialized successfully")
            except ImportError:
                logger.error("OpenAI package not installed")
            except Exception as e:
                logger.error(f"Error initializing OpenAI client: {e}")

    async def generate_response(self, messages: list, **kwargs) -> str:
        """Generate response using OpenAI"""
        if not self.client:
            raise RuntimeError("OpenAI client not available")

        try:
            # Merge kwargs with config defaults
            request_params = {
                'model': self.config.openai_model,
                'messages': messages,
                'max_tokens': kwargs.get('max_tokens', self.config.max_tokens),
                'temperature': kwargs.get('temperature', self.config.temperature),
                'timeout': kwargs.get('timeout', self.config.timeout)
            }

            # Call OpenAI API
            response = self.client.chat.completions.create(**request_params)

            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                raise RuntimeError("No response generated from OpenAI")

        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            raise

    def is_available(self) -> bool:
        """Check if OpenAI client is available"""
        return self.client is not None

class MockLLMClient(LLMClient):
    """Mock LLM client for testing and fallback"""

    def __init__(self, config: LLMConfig):
        self.config = config
        logger.info("Mock LLM client initialized")

    async def generate_response(self, messages: list, **kwargs) -> str:
        """Generate mock response"""
        user_message = ""
        for msg in messages:
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break

        # Generate simple responses based on keywords
        response_text = self._generate_mock_response(user_message)
        return response_text

    def _generate_mock_response(self, query: str) -> str:
        """Generate mock response based on query content"""
        query_lower = query.lower()

        # Financial query responses
        if 'price' in query_lower or 'stock' in query_lower:
            return "Based on current market data, I can provide you with real-time stock prices and analysis. The stock market is dynamic and prices fluctuate throughout the trading day."

        elif 'news' in query_lower or 'happening' in query_lower:
            return "I can provide you with the latest financial news and market updates. The news landscape is constantly evolving with new developments in various sectors."

        elif 'portfolio' in query_lower:
            return "Portfolio analysis involves examining your investment holdings, diversification, and performance metrics. I can help you understand your portfolio composition and risk exposure."

        elif 'sentiment' in query_lower:
            return "Market sentiment analysis involves examining news, social media, and other indicators to gauge investor confidence and market direction."

        elif 'earnings' in query_lower or 'quarterly' in query_lower:
            return "Earnings reports provide crucial information about a company's financial performance. I can help you analyze quarterly results and their market impact."

        else:
            return "I'm here to help you with financial analysis, market insights, and investment information. Please provide more specific details about what you'd like to know."

    def is_available(self) -> bool:
        """Mock client is always available"""
        return True

class LLMManager:
    """Manager for LLM clients with fallback support"""

    def __init__(self):
        self.config = LLMConfig()

        # Initialize clients
        self.openai_client = OpenAIClient(self.config)
        self.mock_client = MockLLMClient(self.config)

        # Set primary client
        self.primary_client = self.openai_client if self.openai_client.is_available() else self.mock_client

        logger.info(f"LLM Manager initialized with {type(self.primary_client).__name__} as primary client")

    async def generate_response(self, messages: list, **kwargs) -> str:
        """Generate response with fallback support"""
        try:
            # Try primary client first
            if self.primary_client.is_available():
                return await self.primary_client.generate_response(messages, **kwargs)
            else:
                # Fallback to mock client
                logger.warning("Primary LLM client not available, using fallback")
                return await self.mock_client.generate_response(messages, **kwargs)

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Final fallback
            return await self.mock_client.generate_response(messages, **kwargs)

    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        models = []

        if self.openai_client.is_available():
            models.append(self.config.openai_model)

        models.append("mock")
        return models

    def get_config_info(self) -> Dict[str, Any]:
        """Get configuration information"""
        return {
            'primary_client': type(self.primary_client).__name__,
            'available_clients': [type(client).__name__ for client in [self.openai_client, self.mock_client]],
            'config': self.config.get_config_dict()
        }

# Global LLM manager instance
llm_manager = LLMManager()

async def generate_financial_response(messages: list, **kwargs) -> str:
    """Generate financial response using LLM manager"""
    return await llm_manager.generate_response(messages, **kwargs)

def get_llm_config_info() -> Dict[str, Any]:
    """Get LLM configuration information"""
    return llm_manager.get_config_info()

if __name__ == "__main__":
    # Test LLM configuration
    config_info = get_llm_config_info()
    print(f"LLM Configuration: {config_info}")

    # Test response generation
    async def test_response():
        messages = [
            {"role": "system", "content": "You are a financial assistant."},
            {"role": "user", "content": "What is the current price of Apple stock?"}
        ]

        response = await generate_financial_response(messages)
        print(f"Generated response: {response}")

    import asyncio
    asyncio.run(test_response())