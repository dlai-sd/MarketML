"""
Rate limiting middleware for API endpoints.
"""

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Optional
import time
import redis.asyncio as aioredis
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Token bucket rate limiter using Redis.
    Implements per-IP rate limiting with sliding window.
    """
    
    def __init__(self, app, redis_client: Optional[aioredis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
        
        # Rate limit configuration
        self.limits = {
            "/v1/personas/generate": {"requests": 10, "window": 60},  # 10 req/min
            "/v1/feedback": {"requests": 30, "window": 60},  # 30 req/min
            "default": {"requests": 100, "window": 60}  # 100 req/min
        }
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting."""
        
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/metrics"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        if not await self._check_rate_limit(client_ip, request.url.path):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": self._get_retry_after(request.url.path)
                },
                headers={
                    "Retry-After": str(self._get_retry_after(request.url.path))
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(
            self._get_limit(request.url.path)["requests"]
        )
        response.headers["X-RateLimit-Window"] = str(
            self._get_limit(request.url.path)["window"]
        )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"
    
    def _get_limit(self, path: str) -> Dict[str, int]:
        """Get rate limit for path."""
        for pattern, limit in self.limits.items():
            if pattern in path:
                return limit
        return self.limits["default"]
    
    def _get_retry_after(self, path: str) -> int:
        """Get retry-after seconds."""
        return self._get_limit(path)["window"]
    
    async def _check_rate_limit(self, client_ip: str, path: str) -> bool:
        """
        Check if request should be rate limited.
        Uses sliding window algorithm with Redis.
        """
        if not self.redis_client:
            # No Redis, allow all requests
            return True
        
        limit = self._get_limit(path)
        key = f"ratelimit:{client_ip}:{path}"
        window = limit["window"]
        max_requests = limit["requests"]
        
        try:
            # Get current timestamp
            now = int(time.time())
            window_start = now - window
            
            # Add current request
            await self.redis_client.zadd(key, {str(now): now})
            
            # Remove old requests outside window
            await self.redis_client.zremrangebyscore(key, 0, window_start)
            
            # Count requests in window
            count = await self.redis_client.zcard(key)
            
            # Set expiry
            await self.redis_client.expire(key, window)
            
            # Check if under limit
            return count <= max_requests
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # On error, allow request
            return True


class CachingMiddleware(BaseHTTPMiddleware):
    """
    Response caching middleware for GET requests.
    """
    
    def __init__(self, app, redis_client: Optional[aioredis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
        self.ttl = 300  # 5 minutes default TTL
        
        # Paths to cache
        self.cacheable_paths = [
            "/v1/personas/",  # GET persona by ID
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Cache GET requests."""
        
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Check if path is cacheable
        if not any(request.url.path.startswith(p) for p in self.cacheable_paths):
            return await call_next(request)
        
        # Try to get from cache
        cache_key = f"cache:{request.url.path}"
        
        if self.redis_client:
            try:
                cached = await self.redis_client.get(cache_key)
                if cached:
                    logger.debug(f"Cache hit: {cache_key}")
                    return JSONResponse(
                        content=cached.decode("utf-8"),
                        headers={"X-Cache": "HIT"}
                    )
            except Exception as e:
                logger.error(f"Cache read failed: {e}")
        
        # Process request
        response = await call_next(request)
        
        # Cache successful responses
        if response.status_code == 200 and self.redis_client:
            try:
                # Note: This is simplified, in production you'd need to
                # properly serialize the response
                response.headers["X-Cache"] = "MISS"
            except Exception as e:
                logger.error(f"Cache write failed: {e}")
        
        return response
