import logging
import os
from typing import Dict, Any
from openai import AsyncOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration - hardcoded for your GitHub AI model
BASE_URL = "https://models.github.ai/inference/v1"
API_KEY = ""
MODEL_NAME = "openai/gpt-4.1-nano"

# Debug: Log the loaded values
logger.info(f"Loaded BASE_URL: {BASE_URL}")
logger.info(f"Loaded API_KEY: {API_KEY[:20]}...")
logger.info(f"Loaded MODEL_NAME: {MODEL_NAME}")

# Initialize OpenAI client (using AsyncOpenAI like the travel agent)
openai_client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)


class AIEngine:
    """AI engine for generating responses using OpenAI"""
    
    @staticmethod
    async def generate_response(query: str) -> str:
        """
        Generate AI response for the given query using OpenAI.
        """
        logger.info(f"Generating AI response for query: {query}")
        
        try:
            # Call OpenAI API (async like the travel agent)
            response = await openai_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant. Provide clear, concise, and helpful responses."},
                    {"role": "user", "content": query}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            logger.info(f"Generated AI response: {ai_response[:100]}...")
            return ai_response
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            # Fallback to mock response if API fails
            return f"AI response to: {query} (API Error: {str(e)})"
    
    @staticmethod
    async def process_query(query: str) -> Dict[str, Any]:
        """
        Process a query and return structured response
        """
        try:
            # Generate AI response
            ai_response = await AIEngine.generate_response(query)
            
            return {
                "query": query,
                "response": ai_response,
                "cached": False,
                "timestamp": None  # Will be set by cache layer
            }
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            raise
