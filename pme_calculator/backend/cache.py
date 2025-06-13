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
from typing import Any, Dict, Optional

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


async def cache_get_with_l3_fallback(
    key: str, fund_id: str | None = None
) -> dict[str, Any] | None:
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
        serialized_value = json.dumps(value, default=str)  # Handle datetime objects

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
            cache_key = make_cache_key(
                func.__name__, {"args": str(args), "kwargs": kwargs}
            )

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
        await _redis_pool.close()
        _redis_pool = None
        logger.info("Redis connection pool closed")
