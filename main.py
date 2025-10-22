import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
import hashlib
import time

from .cache import cache
from .ai_engine import AIEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Chatbot with Redis Caching",
    description="An AI-powered chatbot that uses Redis caching to improve response speed",
    version="1.0.0"
)

# Pydantic models
class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    query: str = Field(..., description="The user's question or query")

class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    query: str
    response: str
    cached: bool
    timestamp: float

def generate_cache_key(query: str) -> str:
    """Generate a consistent cache key for the query"""
    # Normalize query (lowercase, strip whitespace)
    normalized_query = query.lower().strip()
    # Create hash for consistent key length
    return hashlib.md5(normalized_query.encode()).hexdigest()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Chatbot with Redis Caching",
        "version": "1.0.0",
        "endpoints": {
            "/": "API information",
            "/chat": "POST - Submit chat queries",
            "/health": "GET - Health check",
            "/cache/stats": "GET - Cache statistics"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Redis connection
        cache.redis_client.ping()
        return {
            "status": "healthy", 
            "message": "AI Chatbot API is running",
            "redis": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": "AI Chatbot API is running but Redis is disconnected",
            "redis": "disconnected",
            "error": str(e)
        }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process chat queries with Redis caching.
    
    Before generating a response, checks if the query already exists in Redis.
    If cache hit → returns the cached response.
    If cache miss → calls AI generation, stores in Redis, and returns it.
    """
    try:
        query = request.query.strip()
        if not query:
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Generate cache key
        cache_key = generate_cache_key(query)
        
        # Check cache first
        cached_response = cache.get(cache_key)
        
        if cached_response:
            # Cache hit - return cached response
            logger.info(f"Cache HIT for query: '{query}'")
            return ChatResponse(
                query=cached_response["query"],
                response=cached_response["response"],
                cached=True,
                timestamp=cached_response["timestamp"]
            )
        else:
            # Cache miss - generate new response
            logger.info(f"Cache MISS for query: '{query}'")
            
            # Generate AI response
            ai_response = await AIEngine.generate_response(query)
            
            # Prepare response data
            response_data = {
                "query": query,
                "response": ai_response,
                "cached": False,
                "timestamp": time.time()
            }
            
            # Store in cache with 10-minute expiration
            cache.set(cache_key, response_data, expiration=600)
            
            return ChatResponse(**response_data)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    try:
        # Get Redis info
        info = cache.redis_client.info()
        
        return {
            "redis_version": info.get("redis_version"),
            "used_memory_human": info.get("used_memory_human"),
            "connected_clients": info.get("connected_clients"),
            "total_commands_processed": info.get("total_commands_processed"),
            "keyspace_hits": info.get("keyspace_hits"),
            "keyspace_misses": info.get("keyspace_misses"),
            "hit_rate": info.get("keyspace_hits", 0) / max(1, info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0))
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting cache statistics: {str(e)}"
        )

@app.delete("/cache/clear")
async def clear_cache():
    """Clear all cached responses"""
    try:
        success = cache.clear_all()
        if success:
            return {"message": "Cache cleared successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing cache: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
