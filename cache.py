import redis
import json
import logging
from typing import Optional, Dict, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisCache:
    """Redis cache manager for AI chatbot responses"""
    
    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis(
                host=host, 
                port=port, 
                db=db, 
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response by query"""
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                logger.info(f"Cache HIT for query: {key}")
                return json.loads(cached_data)
            else:
                logger.info(f"Cache MISS for query: {key}")
                return None
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    def set(self, key: str, value: Dict[str, Any], expiration: int = 600) -> bool:
        """Set cached response with expiration (default 10 minutes)"""
        try:
            serialized_value = json.dumps(value)
            result = self.redis_client.setex(key, expiration, serialized_value)
            logger.info(f"Cached response for query: {key} (expires in {expiration}s)")
            return result
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete cached response"""
        try:
            result = self.redis_client.delete(key)
            logger.info(f"Deleted cache for query: {key}")
            return bool(result)
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all cached responses"""
        try:
            result = self.redis_client.flushdb()
            logger.info("Cleared all cache")
            return result
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False

# Global cache instance
cache = RedisCache()
