"""
High-Performance Redis Cache for PME Calculator

Provides async Redis caching to eliminate redundant calculations and achieve
sub-second response times for repeated requests.

Key Features:
- Async Redis connection pooling
- Smart cache key generation with payload hashing
- Configurable TTL for different data types
- JSON serialization for complex data structures
"""

import hashlib
import json
import logging
import os
from typing import Any, Optional

import redis.asyncio as redis

# Import db_views with error handling for different import contexts
try:
    from . import db_views
except ImportError:
    try:
        import db_views
    except ImportError:
        # Fallback for testing - create a mock db_views
        class MockDBViews:
            def get(self, fund_id):
                return None

        db_views = MockDBViews()

logger = logging.getLogger(__name__)

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
DEFAULT_TTL = 86_400  # 24 hours
CACHE_PREFIX = "pme"

# Redis availability flag for testing
REDIS_AVAILABLE = True

# Global connection pool
_redis_pool: redis.Redis | None = None


async def get_redis_pool() -> redis.Redis:
    """Get or create Redis connection pool."""
    global _redis_pool
    if not _redis_pool:
        try:
            _redis_pool = redis.from_url(
                REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
                retry_on_timeout=True,
            )
            # Test connection
            await _redis_pool.ping()
            logger.info(f"✅ Redis connected: {REDIS_URL}")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    return _redis_pool


def make_cache_key(endpoint: str, payload: dict[str, Any]) -> str:
    """
    Generate a deterministic cache key from endpoint and payload.

    Args:
        endpoint: API endpoint path (e.g., "/v1/metrics/irr_pme")
        payload: Request parameters as dictionary

    Returns:
        Hashed cache key with prefix
    """
    # Sort payload for consistent hashing
    payload_str = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()[:16]

    # Clean endpoint for key
    clean_endpoint = endpoint.replace("/", "_").replace("?", "_")

    return f"{CACHE_PREFIX}:{clean_endpoint}:{payload_hash}"


async def cache_get(key: str) -> dict[str, Any] | None:
    """
    Get cached value by key.

    Args:
        key: Cache key

    Returns:
        Cached data as dictionary or None if not found
    """
    try:
        redis = await get_redis_pool()
        cached_value = await redis.get(key)

        if cached_value:
            logger.debug(f"🎯 Cache HIT: {key}")
            return json.loads(cached_value)
        else:
            logger.debug(f"❌ Cache MISS: {key}")
            return None

    except Exception as e:
        logger.error(f"Cache get error for key {key}: {e}")
        return None


async def cache_get_with_l3_fallback(key: str, fund_id: str | None = None) -> dict[str, Any] | None:
    """
    Multi-tier cache retrieval: L1/L2 Redis -> L3 DuckDB fallback.

    Args:
        key: Cache key for Redis
        fund_id: Fund ID for DuckDB L3 lookup

    Returns:
        Cached data from any tier or None if not found
    """
    # L1/L2: Try Redis first
    if cached := await cache_get(key):
        return cached

    # L3: Try DuckDB materialized view fallback
    if fund_id and (l3_data := db_views.get(fund_id)):
        logger.debug(f"🎯 L3 DuckDB HIT for fund: {fund_id}")
        # Promote to L1/L2 cache for faster future access
        await cache_set(key, l3_data, ttl=86_400)
        return l3_data

    logger.debug(f"❌ All cache tiers MISS for key: {key}")
    return None


async def cache_set(key: str, value: dict[str, Any], ttl: int = DEFAULT_TTL) -> bool:
    """
    Set cached value with TTL.

    Args:
        key: Cache key
        value: Data to cache (must be JSON serializable)
        ttl: Time to live in seconds

    Returns:
        True if successful, False otherwise
    """
    try:
        redis = await get_redis_pool()
        # Always JSON serialize for consistency with cache_get
        serialized_value = json.dumps(value, default=str)

        await redis.set(key, serialized_value, ex=ttl)
        logger.debug(f"💾 Cache SET: {key} (TTL: {ttl}s)")
        return True

    except Exception as e:
        logger.error(f"Cache set error for key {key}: {e}")
        return False


async def cache_delete(key: str) -> bool:
    """Delete cached value by key."""
    try:
        redis = await get_redis_pool()
        result = await redis.delete(key)
        logger.debug(f"🗑️ Cache DELETE: {key}")
        return result > 0
    except Exception as e:
        logger.error(f"Cache delete error for key {key}: {e}")
        return False


async def cache_clear_pattern(pattern: str) -> int:
    """
    Clear all cache keys matching pattern.

    Args:
        pattern: Redis pattern (e.g., "pme:irr_pme:*")

    Returns:
        Number of keys deleted
    """
    try:
        redis = await get_redis_pool()
        keys = await redis.keys(pattern)
        if keys:
            deleted = await redis.delete(*keys)
            logger.info(f"🧹 Cache cleared: {deleted} keys matching {pattern}")
            return deleted
        return 0
    except Exception as e:
        logger.error(f"Cache clear error for pattern {pattern}: {e}")
        return 0


async def cache_stats() -> dict[str, Any]:
    """Get cache statistics."""
    try:
        # Check if event loop is running and functional
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            if loop.is_closed():
                return {"connected": False, "error": "Event loop is closed"}
        except RuntimeError:
            return {"connected": False, "error": "No event loop available"}

        redis = await get_redis_pool()
        info = await redis.info("memory")
        keyspace = await redis.info("keyspace")

        # Count PME-specific keys
        pme_keys = await redis.keys(f"{CACHE_PREFIX}:*")

        return {
            "redis_memory_used": info.get("used_memory_human", "unknown"),
            "redis_memory_peak": info.get("used_memory_peak_human", "unknown"),
            "total_keys": sum(
                db.get("keys", 0) for db in keyspace.values() if isinstance(db, dict)
            ),
            "pme_cache_keys": len(pme_keys),
            "connected": True,
        }
    except Exception as e:
        logger.error(f"Cache stats error: {e}")
        return {"connected": False, "error": str(e)}


# Cache decorators for common patterns
def cached_endpoint(ttl: int = DEFAULT_TTL):
    """
    Decorator for caching endpoint responses.

    Usage:
        @cached_endpoint(ttl=3600)
        async def my_endpoint(request_data):
            return expensive_calculation()
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            cache_key = make_cache_key(func.__name__, {"args": str(args), "kwargs": kwargs})

            # Try cache first
            cached_result = await cache_get(cache_key)
            if cached_result:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator


# Graceful shutdown
async def close_redis_pool():
    """Close Redis connection pool gracefully."""
    global _redis_pool
    if _redis_pool:
        await _redis_pool.aclose()
        _redis_pool = None
        logger.info("Redis connection pool closed")


# Compatibility aliases for tests
get_cache = cache_get
set_cache = cache_set
delete_cache = cache_delete


async def cache_exists(key: str) -> bool:
    """Check if a cache key exists."""
    try:
        redis = await get_redis_pool()
        exists = await redis.exists(key)
        return bool(exists)
    except Exception as e:
        logger.error(f"Cache exists error for key {key}: {e}")
        return False


async def init_cache() -> bool:
    """Initialize cache connection."""
    try:
        await get_redis_pool()
        return True
    except Exception:
        return False


def cached(ttl: int = DEFAULT_TTL, key_prefix: str = ""):
    """
    Decorator for caching function results with custom key prefix.

    Args:
        ttl: Time to live in seconds
        key_prefix: Custom prefix for cache keys

    Usage:
        @cached(ttl=3600, key_prefix="my_func")
        async def my_function(arg1, arg2):
            return expensive_calculation()
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            func_name = key_prefix or func.__name__
            cache_key = make_cache_key(func_name, {"args": str(args), "kwargs": kwargs})

            # Try cache first
            cached_result = await cache_get(cache_key)
            if cached_result:
                return cached_result

            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_set(cache_key, result, ttl)
            return result

        return wrapper

    return decorator


class CacheManager:
    """
    Cache manager singleton for backward compatibility with tests.
    This provides a class-based interface to the cache functions.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._redis_url = REDIS_URL
            self._default_ttl = DEFAULT_TTL  # Add missing attribute
            self.redis = None
            self.is_connected = False
            self._initialized = True

    async def initialize(self) -> bool:
        """Initialize Redis connection."""
        import pme_calculator.backend.cache as cache_module

        # Check if Redis is available (for testing purposes)
        if not getattr(cache_module, "REDIS_AVAILABLE", True):
            self.is_connected = False
            self.redis = None
            return False

        try:
            self.redis = await get_redis_pool()
            self.is_connected = True
            return True
        except Exception:
            self.is_connected = False
            self.redis = None
            return False

    async def close(self):
        """Close Redis connection."""
        if self.redis:
            # For testing, check if redis has close method
            if hasattr(self.redis, "close"):
                await self.redis.close()
            else:
                await close_redis_pool()
            self.is_connected = False
            self.redis = None

    async def get(self, key: str):
        """Get cached value."""
        if not self.is_connected or not self.redis:
            return None
        try:
            cached_value = await self.redis.get(key)
            if cached_value:
                try:
                    return json.loads(cached_value)
                except (json.JSONDecodeError, TypeError):
                    return cached_value  # Return as string if not JSON
            return None
        except Exception:
            return None

    async def set(self, key: str, value, ttl: int = None) -> bool:
        """Set cached value."""
        if not self.is_connected or not self.redis:
            return False
        try:
            # Use instance default TTL if none provided
            if ttl is None:
                ttl = self._default_ttl

            # Always JSON serialize for consistency with get method
            serialized_value = json.dumps(value, default=str)
            await self.redis.set(key, serialized_value, ex=ttl)
            return True
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        """Delete cached value."""
        if not self.is_connected or not self.redis:
            return False
        try:
            result = await self.redis.delete(key)
            return result > 0
        except Exception:
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if not self.is_connected or not self.redis:
            return False
        try:
            result = await self.redis.exists(key)
            return bool(result)
        except Exception:
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL for existing key."""
        if not self.is_connected or not self.redis:
            return False
        try:
            result = await self.redis.expire(key, ttl)
            return bool(result)
        except Exception:
            return False

    def generate_key(self, func_name: str, *args, **kwargs) -> str:
        """Generate cache key from arguments in the format expected by tests."""
        # Start with function name
        key_parts = [str(func_name)]

        # Check if we have only simple arguments (strings, numbers, None)
        def is_simple(obj):
            return obj is None or isinstance(obj, str | int | float | bool)

        all_simple = all(is_simple(arg) for arg in args) and all(
            is_simple(val) for val in kwargs.values()
        )

        if all_simple and (args or kwargs):
            # Simple case: create colon-separated key
            for arg in args:
                key_parts.append(str(arg) if arg is not None else "None")

            for key, value in sorted(kwargs.items()):
                key_parts.append(f"{key}:{value if value is not None else 'None'}")

            return ":".join(key_parts)

        elif args or kwargs:
            # Complex case: use hash for complex objects
            complex_data = {"args": args, "kwargs": kwargs}
            data_str = json.dumps(complex_data, sort_keys=True, default=str)
            data_hash = hashlib.sha256(data_str.encode()).hexdigest()[:8]
            return f"{func_name}:{data_hash}"
        else:
            # No arguments: just return function name
            return func_name

    def _generate_key(self, *args, **kwargs) -> str:
        """Private method alias for generate_key (for backward compatibility)."""
        return self.generate_key(*args, **kwargs)


# Create a default cache instance for compatibility
cache = CacheManager()
