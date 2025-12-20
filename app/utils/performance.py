"""
Performance profiling utilities.
"""

import time
import functools
import logging
from typing import Callable, Any
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def timer(operation_name: str):
    """
    Context manager for timing operations.
    
    Usage:
        with timer("database_query"):
            result = await db.execute(query)
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = (time.perf_counter() - start) * 1000  # ms
        logger.info(f"⏱️  {operation_name}: {elapsed:.2f}ms")


def profile(func: Callable) -> Callable:
    """
    Decorator to profile function execution time.
    Works with both sync and async functions.
    
    Usage:
        @profile
        async def my_function():
            pass
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            logger.info(f"⏱️  {func.__name__}: {elapsed:.2f}ms")
    
    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = (time.perf_counter() - start) * 1000
            logger.info(f"⏱️  {func.__name__}: {elapsed:.2f}ms")
    
    # Return appropriate wrapper based on function type
    import asyncio
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


class PerformanceMonitor:
    """
    Monitor and collect performance metrics.
    """
    
    def __init__(self):
        self.metrics = {}
    
    def record(self, operation: str, duration_ms: float):
        """Record operation duration."""
        if operation not in self.metrics:
            self.metrics[operation] = {
                "count": 0,
                "total_ms": 0,
                "min_ms": float('inf'),
                "max_ms": 0,
                "avg_ms": 0
            }
        
        m = self.metrics[operation]
        m["count"] += 1
        m["total_ms"] += duration_ms
        m["min_ms"] = min(m["min_ms"], duration_ms)
        m["max_ms"] = max(m["max_ms"], duration_ms)
        m["avg_ms"] = m["total_ms"] / m["count"]
    
    def get_stats(self, operation: str = None) -> dict:
        """Get performance statistics."""
        if operation:
            return self.metrics.get(operation, {})
        return self.metrics
    
    def reset(self):
        """Reset all metrics."""
        self.metrics = {}


# Global performance monitor
performance_monitor = PerformanceMonitor()


@contextmanager
def monitor(operation: str):
    """
    Context manager for monitoring operation performance.
    
    Usage:
        with monitor("scraping"):
            data = scrape_website()
    """
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = (time.perf_counter() - start) * 1000
        performance_monitor.record(operation, elapsed)
        
        # Log slow operations (> 1 second)
        if elapsed > 1000:
            logger.warning(f"⚠️  Slow operation: {operation} took {elapsed:.2f}ms")


def log_slow_queries(threshold_ms: float = 100):
    """
    Decorator to log slow database queries.
    
    Usage:
        @log_slow_queries(threshold_ms=200)
        async def fetch_personas():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = await func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            
            if elapsed > threshold_ms:
                logger.warning(
                    f"🐌 Slow query: {func.__name__} took {elapsed:.2f}ms "
                    f"(threshold: {threshold_ms}ms)"
                )
            
            return result
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            
            if elapsed > threshold_ms:
                logger.warning(
                    f"🐌 Slow query: {func.__name__} took {elapsed:.2f}ms "
                    f"(threshold: {threshold_ms}ms)"
                )
            
            return result
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
