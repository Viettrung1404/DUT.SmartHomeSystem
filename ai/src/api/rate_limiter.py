"""
Rate Limiter for Vietnamese NLP Intent Classification API.

This module provides rate limiting using token bucket algorithm.

**Validates: Requirements 11.2**
"""

import time
from typing import Dict, Optional
import logging
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate Limiter using token bucket algorithm.
    
    This limiter:
    - Allows burst traffic up to bucket capacity
    - Refills tokens at constant rate
    - Thread-safe for concurrent requests
    """
    
    def __init__(self,
                 rate: int = 10,
                 per: int = 60,
                 burst: int = 20):
        """
        Initialize rate limiter.
        
        Args:
            rate: Number of requests allowed per time period
            per: Time period in seconds
            burst: Maximum burst capacity (bucket size)
        """
        self.rate = rate
        self.per = per
        self.burst = burst
        self.refill_rate = rate / per  # Tokens per second
        
        # Storage for token buckets per client
        self.buckets: Dict[str, Dict[str, float]] = defaultdict(
            lambda: {"tokens": float(burst), "last_refill": time.time()}
        )
        
        # Thread lock for thread safety
        self.lock = threading.Lock()
    
    def is_allowed(self, client_id: str) -> bool:
        """
        Check if request is allowed for client.
        
        Args:
            client_id: Client identifier (e.g., user_id, IP address)
            
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        with self.lock:
            bucket = self.buckets[client_id]
            current_time = time.time()
            
            # Refill tokens based on time elapsed
            time_elapsed = current_time - bucket["last_refill"]
            tokens_to_add = time_elapsed * self.refill_rate
            bucket["tokens"] = min(self.burst, bucket["tokens"] + tokens_to_add)
            bucket["last_refill"] = current_time
            
            # Check if request can be allowed
            if bucket["tokens"] >= 1.0:
                bucket["tokens"] -= 1.0
                return True
            else:
                logger.warning(f"Rate limit exceeded for client: {client_id}")
                return False
    
    def get_remaining_tokens(self, client_id: str) -> float:
        """
        Get remaining tokens for client.
        
        Args:
            client_id: Client identifier
            
        Returns:
            Number of remaining tokens
        """
        with self.lock:
            bucket = self.buckets[client_id]
            current_time = time.time()
            
            # Refill tokens
            time_elapsed = current_time - bucket["last_refill"]
            tokens_to_add = time_elapsed * self.refill_rate
            tokens = min(self.burst, bucket["tokens"] + tokens_to_add)
            
            return tokens
    
    def reset(self, client_id: str):
        """
        Reset rate limit for client.
        
        Args:
            client_id: Client identifier
        """
        with self.lock:
            if client_id in self.buckets:
                del self.buckets[client_id]
    
    def reset_all(self):
        """Reset rate limits for all clients."""
        with self.lock:
            self.buckets.clear()
