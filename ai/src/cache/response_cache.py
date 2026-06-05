"""
Response Cache for Vietnamese NLP Intent Classification API.

This module provides Redis-based caching for API responses.

**Validates: Requirements 12.4**
"""

import json
import hashlib
import logging
from typing import Optional, Dict, Any
import redis
from datetime import timedelta

logger = logging.getLogger(__name__)


class ResponseCache:
    """
    Response Cache using Redis.
    
    This cache:
    - Stores responses for identical requests
    - Uses 5-minute TTL
    - Generates cache keys from request hash
    - Thread-safe (Redis handles concurrency)
    """
    
    DEFAULT_TTL = 300  # 5 minutes in seconds
    
    def __init__(self,
                 redis_url: str = "redis://localhost:6379/0",
                 ttl: int = DEFAULT_TTL):
        """
        Initialize response cache.
        
        Args:
            redis_url: Redis connection URL
            ttl: Time-to-live in seconds (default 300 = 5 minutes)
        """
        self.ttl = ttl
        
        try:
            self.redis_client = redis.from_url(redis_url, decode_responses=True)
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {redis_url}")
        except redis.ConnectionError as e:
            logger.warning(f"Failed to connect to Redis: {e}. Cache disabled.")
            self.redis_client = None
    
    def _generate_cache_key(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate cache key from request parameters.
        
        Args:
            text: Input text
            context: Optional device context
            
        Returns:
            Cache key string
        """
        # Create deterministic string from request
        cache_data = {
            "text": text.strip().lower(),
            "context": context or {}
        }
        
        # Generate hash
        cache_str = json.dumps(cache_data, sort_keys=True)
        cache_hash = hashlib.sha256(cache_str.encode()).hexdigest()
        
        return f"intent_cache:{cache_hash}"
    
    def get(self, text: str, context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached response.
        
        Args:
            text: Input text
            context: Optional device context
            
        Returns:
            Cached response dict or None if not found
        """
        if not self.redis_client:
            return None
        
        try:
            cache_key = self._generate_cache_key(text, context)
            cached_value = self.redis_client.get(cache_key)
            
            if cached_value:
                logger.debug(f"Cache hit for key: {cache_key}")
                return json.loads(cached_value)
            else:
                logger.debug(f"Cache miss for key: {cache_key}")
                return None
        
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    def set(self,
            text: str,
            response: Dict[str, Any],
            context: Optional[Dict[str, Any]] = None):
        """
        Set cached response.
        
        Args:
            text: Input text
            response: Response to cache
            context: Optional device context
        """
        if not self.redis_client:
            return
        
        try:
            cache_key = self._generate_cache_key(text, context)
            cache_value = json.dumps(response)
            
            self.redis_client.setex(
                cache_key,
                timedelta(seconds=self.ttl),
                cache_value
            )
            
            logger.debug(f"Cached response for key: {cache_key}")
        
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
    
    def delete(self, text: str, context: Optional[Dict[str, Any]] = None):
        """
        Delete cached response.
        
        Args:
            text: Input text
            context: Optional device context
        """
        if not self.redis_client:
            return
        
        try:
            cache_key = self._generate_cache_key(text, context)
            self.redis_client.delete(cache_key)
            logger.debug(f"Deleted cache for key: {cache_key}")
        
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
    
    def clear(self):
        """Clear all cached responses."""
        if not self.redis_client:
            return
        
        try:
            # Delete all keys matching pattern
            pattern = "intent_cache:*"
            keys = self.redis_client.keys(pattern)
            
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cached responses")
        
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache stats
        """
        if not self.redis_client:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info("stats")
            
            return {
                "enabled": True,
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_keys": len(self.redis_client.keys("intent_cache:*"))
            }
        
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"enabled": True, "error": str(e)}
