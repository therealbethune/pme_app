"""
Tests for Redis Cache Module

Tests the high-performance Redis caching system including:
- Basic cache operations (get/set/delete)
- Cache key generation
- TTL functionality
- Error handling
- Performance characteristics
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio

from pme_calculator.backend.cache import (
    cache_clear_pattern,
    cache_delete,
    cache_get,
    cache_set,
    cache_stats,
    close_redis_pool,
    make_cache_key,
    reset_cache_for_testing,
)


class TestCacheKeyGeneration:
    """Test cache key generation logic."""

    def test_make_cache_key_basic(self):
        """Test basic cache key generation."""
        key = make_cache_key("/v1/metrics/irr_pme", {"fund_id": "test123"})
        assert key.startswith("pme:_v1_metrics_irr_pme:")
        assert len(key.split(":")) == 3

    def test_make_cache_key_deterministic(self):
        """Test that identical inputs produce identical keys."""
        payload = {"fund_id": "test123", "start_date": "2020-01-01"}
        key1 = make_cache_key("/v1/metrics/irr_pme", payload)
        key2 = make_cache_key("/v1/metrics/irr_pme", payload)
        assert key1 == key2

    def test_make_cache_key_order_independent(self):
        """Test that parameter order doesn't affect key generation."""
        payload1 = {"fund_id": "test123", "start_date": "2020-01-01"}
        payload2 = {"start_date": "2020-01-01", "fund_id": "test123"}
        key1 = make_cache_key("/v1/metrics/irr_pme", payload1)
        key2 = make_cache_key("/v1/metrics/irr_pme", payload2)
        assert key1 == key2

    def test_make_cache_key_different_payloads(self):
        """Test that different payloads produce different keys."""
        key1 = make_cache_key("/v1/metrics/irr_pme", {"fund_id": "test123"})
        key2 = make_cache_key("/v1/metrics/irr_pme", {"fund_id": "test456"})
        assert key1 != key2


@pytest.mark.asyncio
class TestCacheOperations:
    """Test Redis cache operations."""

    async def test_cache_roundtrip_basic(self):
        """Test basic cache set and get operations."""
        key = make_cache_key("/v1/metrics/irr_pme", {"fund_id": "test123"})
        test_data = {"irr": 0.15, "pme": 1.25, "status": "success"}

        # Set cache
        success = await cache_set(key, test_data, ttl=60)
        assert success is True

        # Get cache
        cached_data = await cache_get(key)
        assert cached_data == test_data

        # Cleanup
        await cache_delete(key)

    async def test_cache_miss(self):
        """Test cache miss returns None."""
        key = make_cache_key("/v1/metrics/nonexistent", {"fund_id": "missing"})
        cached_data = await cache_get(key)
        assert cached_data is None

    async def test_cache_delete(self):
        """Test cache deletion."""
        key = make_cache_key("/v1/metrics/test_delete", {"fund_id": "delete_me"})
        test_data = {"test": "data"}

        # Set and verify
        await cache_set(key, test_data)
        cached_data = await cache_get(key)
        assert cached_data == test_data

        # Delete and verify
        deleted = await cache_delete(key)
        assert deleted is True

        cached_data = await cache_get(key)
        assert cached_data is None

    async def test_cache_complex_data(self):
        """Test caching complex data structures."""
        key = make_cache_key("/v1/metrics/complex", {"fund_id": "complex_test"})
        complex_data = {
            "metrics": {"irr": 0.15, "pme": 1.25, "tvpi": 2.1},
            "cashflows": [
                {"date": "2020-01-01", "amount": -1000000},
                {"date": "2021-01-01", "amount": 500000},
                {"date": "2022-01-01", "amount": 1500000},
            ],
            "metadata": {
                "calculation_date": "2024-01-01",
                "fund_name": "Test Fund LP",
                "benchmark": "S&P 500",
            },
        }

        # Set and get
        await cache_set(key, complex_data, ttl=60)
        cached_data = await cache_get(key)

        assert cached_data == complex_data
        assert cached_data["metrics"]["irr"] == 0.15
        assert len(cached_data["cashflows"]) == 3

        # Cleanup
        await cache_delete(key)


@pytest.mark.asyncio
class TestCachePatterns:
    """Test cache pattern operations."""

    async def test_cache_clear_pattern(self):
        """Test clearing cache keys by pattern."""
        # Set multiple keys with same pattern
        base_payload = {"fund_id": "pattern_test"}
        keys = []

        for i in range(3):
            payload = {**base_payload, "variant": i}
            key = make_cache_key("/v1/metrics/pattern_test", payload)
            keys.append(key)
            await cache_set(key, {"data": f"test_{i}"})

        # Verify all keys exist
        for key in keys:
            cached_data = await cache_get(key)
            assert cached_data is not None

        # Clear pattern
        deleted_count = await cache_clear_pattern("pme:_v1_metrics_pattern_test:*")
        assert deleted_count == 3

        # Verify all keys are gone
        for key in keys:
            cached_data = await cache_get(key)
            assert cached_data is None


@pytest.mark.asyncio
class TestCacheStats:
    """Test cache statistics and monitoring."""

    def setup_method(self):
        """Reset cache state before each test."""
        reset_cache_for_testing()

    @patch("pme_calculator.backend.cache.get_redis_pool")
    async def test_cache_stats(self, mock_get_pool):
        """Test cache statistics retrieval."""
        # Mock Redis to avoid event loop issues in test environment
        mock_redis = AsyncMock()
        mock_redis.info.return_value = {
            "used_memory_human": "1.23M",
            "used_memory_peak_human": "2.34M",
        }
        mock_redis.keys.return_value = ["pme:key1", "pme:key2"]
        mock_get_pool.return_value = mock_redis

        stats = await cache_stats()

        assert "connected" in stats
        assert stats["connected"] is True
        assert "redis_memory_used" in stats
        assert "pme_cache_keys" in stats
        assert isinstance(stats["pme_cache_keys"], int)
        assert stats["pme_cache_keys"] == 2


@pytest.mark.asyncio
class TestCacheErrorHandling:
    """Test cache error handling and resilience."""

    def setup_method(self):
        """Reset cache state before each test."""
        reset_cache_for_testing()

    @patch("pme_calculator.backend.cache.get_redis_pool")
    async def test_cache_get_error_handling(self, mock_get_pool):
        """Test cache get handles Redis errors gracefully."""
        # Mock Redis to raise an exception
        mock_redis = AsyncMock()
        mock_redis.get.side_effect = Exception("Redis connection error")
        mock_get_pool.return_value = mock_redis

        key = make_cache_key("/v1/metrics/error_test", {"fund_id": "error"})
        result = await cache_get(key)

        assert result is None  # Should return None on error, not raise

    @patch("pme_calculator.backend.cache.get_redis_pool")
    async def test_cache_set_error_handling(self, mock_get_pool):
        """Test cache set handles Redis errors gracefully."""
        # Mock Redis to raise an exception
        mock_redis = AsyncMock()
        mock_redis.set.side_effect = Exception("Redis connection error")
        mock_get_pool.return_value = mock_redis

        key = make_cache_key("/v1/metrics/error_test", {"fund_id": "error"})
        result = await cache_set(key, {"test": "data"})

        assert result is False  # Should return False on error, not raise


@pytest.mark.asyncio
class TestCachePerformance:
    """Test cache performance characteristics."""

    async def test_cache_performance_basic(self):
        """Test basic cache performance."""
        import time

        key = make_cache_key("/v1/metrics/perf_test", {"fund_id": "perf123"})
        test_data = {"irr": 0.15, "pme": 1.25}

        # Measure set performance
        start_time = time.time()
        await cache_set(key, test_data)
        set_time = time.time() - start_time

        # Measure get performance
        start_time = time.time()
        cached_data = await cache_get(key)
        get_time = time.time() - start_time

        # Basic performance assertions
        assert set_time < 0.1  # Should be under 100ms
        assert get_time < 0.05  # Should be under 50ms
        assert cached_data == test_data

        # Cleanup
        await cache_delete(key)


# Integration test for the example from the sprint
async def _cache_roundtrip_example():
    """Example roundtrip test from the sprint specification."""
    key = make_cache_key("/v1/metrics/irr_pme", {"fund": "X"})
    await cache_set(key, {"answer": 42}, ttl=5)
    cached_result = await cache_get(key)
    return cached_result["answer"]


def test_cache_roundtrip_sprint_example():
    """Test the exact example from the sprint specification."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_cache_roundtrip_example())
        assert result == 42
    finally:
        loop.close()


# Cleanup fixture
@pytest_asyncio.fixture(scope="session", autouse=True)
async def cleanup_cache():
    """Clean up cache connections after tests."""
    yield
    try:
        await close_redis_pool()
    except Exception:
        pass  # Ignore cleanup errors if event loop is already closed
