"""
Comprehensive tests for the Redis cache module.
Tests all functionality including edge cases and error conditions.
"""

import json
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from cache import (
    CacheManager,
    cache_exists,
    cached,
    delete_cache,
    get_cache,
    init_cache,
    set_cache,
)


@pytest_asyncio.fixture
async def cache_manager():
    """Fixture to provide a clean cache manager instance."""
    manager = CacheManager()
    yield manager
    # Cleanup - close any connections
    try:
        await manager.close()
    except Exception:
        pass  # Ignore cleanup errors


class TestCacheManager:
    """Test cases for CacheManager singleton."""

    def test_singleton_pattern(self):
        """Test that CacheManager is a proper singleton."""
        cache1 = CacheManager()
        cache2 = CacheManager()
        assert cache1 is cache2
        assert id(cache1) == id(cache2)

    def test_singleton_initialization(self):
        """Test singleton initialization only happens once."""
        cache1 = CacheManager()
        original_redis_url = cache1._redis_url

        cache2 = CacheManager()
        assert cache2._redis_url == original_redis_url

    @pytest.mark.asyncio
    async def test_initialize_without_redis(self):
        """Test initialization when Redis is not available."""
        with patch("pme_calculator.backend.cache.REDIS_AVAILABLE", False):
            cache_manager = CacheManager()
            result = await cache_manager.initialize()
            assert result is False
            assert cache_manager.is_connected is False
            assert cache_manager.redis is None

    @pytest.mark.asyncio
    async def test_initialize_with_redis_success(self):
        """Test successful Redis initialization."""
        mock_redis = AsyncMock()
        mock_redis.ping = AsyncMock()

        # Patch the get_redis_pool function directly
        with patch("cache.get_redis_pool", return_value=mock_redis):
            cache_manager = CacheManager()
            result = await cache_manager.initialize()

            assert result is True
            assert cache_manager.is_connected is True
            assert cache_manager.redis is mock_redis

    @pytest.mark.asyncio
    async def test_initialize_with_redis_failure(self):
        """Test Redis initialization failure."""
        # Mock get_redis_pool to raise an exception
        with patch("cache.get_redis_pool", side_effect=Exception("Connection failed")):
            cache_manager = CacheManager()
            result = await cache_manager.initialize()

            assert result is False
            assert cache_manager.is_connected is False
            assert cache_manager.redis is None

    @pytest.mark.asyncio
    async def test_close_connection(self):
        """Test closing Redis connection."""
        mock_redis = AsyncMock()
        mock_redis.aclose = AsyncMock()

        cache_manager = CacheManager()
        cache_manager.redis = mock_redis
        cache_manager.is_connected = True

        await cache_manager.close()

        assert cache_manager.is_connected is False

    @pytest.mark.asyncio
    async def test_get_not_connected(self):
        """Test get when not connected."""
        cache_manager = CacheManager()
        cache_manager.is_connected = False
        cache_manager.redis = None

        result = await cache_manager.get("test_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_success_json(self):
        """Test successful get with JSON data."""
        mock_redis = AsyncMock()
        test_data = {"key": "value", "number": 42}
        mock_redis.get = AsyncMock(return_value=json.dumps(test_data))

        cache_manager = CacheManager()
        cache_manager.redis = mock_redis
        cache_manager.is_connected = True

        result = await cache_manager.get("test_key")

        assert result == test_data
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_success_string(self):
        """Test successful get with string data."""
        mock_redis = AsyncMock()
        test_data = "simple string"
        mock_redis.get = AsyncMock(return_value=test_data)

        cache_manager = CacheManager()
        cache_manager.redis = mock_redis
        cache_manager.is_connected = True

        result = await cache_manager.get("test_key")

        assert result == test_data
        mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_get_key_not_found(self):
        """Test get when key doesn't exist."""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)

        cache_manager = CacheManager()
        cache_manager.redis = mock_redis
        cache_manager.is_connected = True

        result = await cache_manager.get("nonexistent_key")

        assert result is None
        mock_redis.get.assert_called_once_with("nonexistent_key")

    @pytest.mark.asyncio
    async def test_get_exception_handling(self):
        """Test exception handling in get method."""
        mock_redis = AsyncMock()
        mock_redis.get = AsyncMock(side_effect=Exception("Redis error"))

        cache_manager = CacheManager()
        cache_manager.redis = mock_redis
        cache_manager.is_connected = True

        result = await cache_manager.get("test_key")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_not_connected(self):
        """Test set when not connected."""
        cache_manager = CacheManager()
        cache_manager.is_connected = False
        cache_manager.redis = None

        result = await cache_manager.set("test_key", "test_value")
        assert result is False

    @pytest.mark.asyncio
    async def test_set_success_string(self):
        """Test successful set with string data."""
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock()

        cache_manager = CacheManager()
        cache_manager.redis = mock_redis
        cache_manager.is_connected = True
        cache_manager._default_ttl = 3600

        result = await cache_manager.set("test_key", "test_value")

        assert result is True
        mock_redis.set.assert_called_once_with("test_key", "test_value", ex=3600)

    @pytest.mark.asyncio
    async def test_set_success_json(self):
        """Test successful set with JSON data."""
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock()

        cache_manager = CacheManager()
        cache_manager.redis = mock_redis
        cache_manager.is_connected = True
        cache_manager._default_ttl = 3600

        test_data = {"key": "value", "number": 42}
        result = await cache_manager.set("test_key", test_data, ttl=300)

        assert result is True
        mock_redis.set.assert_called_once_with(
            "test_key", json.dumps(test_data, default=str), ex=300
        )

    @pytest.mark.asyncio
    async def test_set_exception_handling(self):
        """Test exception handling in set method."""
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock(side_effect=Exception("Redis error"))

        cache_manager = CacheManager()
        cache_manager.redis = mock_redis
        cache_manager.is_connected = True

        result = await cache_manager.set("test_key", "test_value")

        assert result is False

    @pytest.mark.asyncio
    async def test_delete_success(self):
        """Test successful delete."""
        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(return_value=1)

        cache_manager = CacheManager()
        cache_manager.redis = mock_redis
        cache_manager.is_connected = True

        result = await cache_manager.delete("test_key")

        assert result is True
        mock_redis.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_delete_key_not_found(self):
        """Test delete when key doesn't exist."""
        mock_redis = AsyncMock()
        mock_redis.delete = AsyncMock(return_value=0)

        cache_manager = CacheManager()
        cache_manager.redis = mock_redis
        cache_manager.is_connected = True

        result = await cache_manager.delete("nonexistent_key")

        assert result is False

    @pytest.mark.asyncio
    async def test_exists_success(self):
        """Test successful exists check."""
        mock_redis = AsyncMock()
        mock_redis.exists = AsyncMock(return_value=1)

        cache_manager = CacheManager()
        cache_manager.redis = mock_redis
        cache_manager.is_connected = True

        result = await cache_manager.exists("test_key")

        assert result is True
        mock_redis.exists.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_expire_success(self):
        """Test successful expire."""
        mock_redis = AsyncMock()
        mock_redis.expire = AsyncMock(return_value=1)

        cache_manager = CacheManager()
        cache_manager.redis = mock_redis
        cache_manager.is_connected = True

        result = await cache_manager.expire("test_key", 300)

        assert result is True
        mock_redis.expire.assert_called_once_with("test_key", 300)

    def test_generate_key_simple(self):
        """Test key generation with simple arguments."""
        cache_manager = CacheManager()

        key = cache_manager._generate_key(
            "test_func", "arg1", "arg2", param1="value1", param2="value2"
        )

        expected = "test_func:arg1:arg2:param1:value1:param2:value2"
        assert key == expected

    def test_generate_key_complex_objects(self):
        """Test key generation with complex objects."""
        cache_manager = CacheManager()

        complex_arg = {"nested": {"data": [1, 2, 3]}}
        key = cache_manager._generate_key("test_func", complex_arg)

        # Should contain the function name and a hash
        assert key.startswith("test_func:")
        assert len(key.split(":")) == 2  # prefix + hash
        assert len(key.split(":")[1]) == 8  # 8-character hash


class TestCachedDecorator:
    """Test cases for the @cached decorator."""

    @pytest.mark.asyncio
    async def test_cached_decorator_cache_hit(self):
        """Test cached decorator with cache hit."""
        # Mock the cache functions directly
        with (
            patch("cache.cache_get", return_value="cached_result") as mock_get,
            patch("cache.cache_set") as mock_set,
        ):

            @cached(ttl=300)
            async def test_function(arg1, arg2):
                return "computed_result"

            result = await test_function("value1", "value2")

            assert result == "cached_result"
            mock_get.assert_called_once()
            mock_set.assert_not_called()

    @pytest.mark.asyncio
    async def test_cached_decorator_cache_miss(self):
        """Test cached decorator with cache miss."""
        # Mock the cache functions directly
        with (
            patch("cache.cache_get", return_value=None) as mock_get,
            patch("cache.cache_set", return_value=True) as mock_set,
        ):

            @cached(ttl=300)
            async def test_function(arg1, arg2):
                return "computed_result"

            result = await test_function("value1", "value2")

            assert result == "computed_result"
            mock_get.assert_called_once()
            mock_set.assert_called_once()

    @pytest.mark.asyncio
    async def test_cached_decorator_custom_prefix(self):
        """Test cached decorator with custom prefix."""
        # Mock the cache functions directly
        with (
            patch("cache.cache_get", return_value=None) as mock_get,
            patch("cache.cache_set", return_value=True) as mock_set,
        ):

            @cached(ttl=300, key_prefix="custom_prefix")
            async def test_function(arg1):
                return "result"

            result = await test_function("value1")

            assert result == "result"
            mock_get.assert_called_once()
            # Verify the key has the custom prefix
            call_args = mock_get.call_args[0]
            assert "custom_prefix" in call_args[0]


class TestConvenienceFunctions:
    """Test convenience function aliases."""

    @pytest.mark.asyncio
    async def test_get_cache(self):
        """Test get_cache convenience function."""
        # Mock the Redis connection that the convenience function uses
        with patch("cache.get_redis_pool") as mock_pool:
            mock_redis = AsyncMock()
            mock_redis.get.return_value = '"test_value"'  # JSON string
            mock_pool.return_value = mock_redis

            result = await get_cache("test_key")
            assert result == "test_value"
            mock_redis.get.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_set_cache(self):
        """Test set_cache convenience function."""
        # Mock the Redis connection that the convenience function uses
        with patch("cache.get_redis_pool") as mock_pool:
            mock_redis = AsyncMock()
            mock_redis.set.return_value = True
            mock_pool.return_value = mock_redis

            result = await set_cache("test_key", "test_value", 300)
            assert result is True
            mock_redis.set.assert_called_once_with("test_key", "test_value", ex=300)

    @pytest.mark.asyncio
    async def test_delete_cache(self):
        """Test delete_cache convenience function."""
        # Mock the Redis connection that the convenience function uses
        with patch("cache.get_redis_pool") as mock_pool:
            mock_redis = AsyncMock()
            mock_redis.delete.return_value = 1  # Redis returns count of deleted keys
            mock_pool.return_value = mock_redis

            result = await delete_cache("test_key")
            assert result is True
            mock_redis.delete.assert_called_once_with("test_key")

    @pytest.mark.asyncio
    async def test_cache_exists(self):
        """Test cache_exists convenience function."""
        # Mock the Redis connection that the convenience function uses
        with patch("cache.get_redis_pool") as mock_pool:
            mock_redis = AsyncMock()
            mock_redis.exists.return_value = 1  # Redis returns 1 for exists
            mock_pool.return_value = mock_redis

            result = await cache_exists("test_key")
            assert result is True
            mock_redis.exists.assert_called_once_with("test_key")


class TestInitialization:
    """Test initialization functions."""

    @pytest.mark.asyncio
    async def test_init_cache(self):
        """Test init_cache function."""
        with patch("cache.get_redis_pool") as mock_pool:
            mock_pool.return_value = AsyncMock()
            result = await init_cache()
            assert result is True
            mock_pool.assert_called_once()


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_generate_key_empty_args(self):
        """Test key generation with empty arguments."""
        cache_manager = CacheManager()

        key = cache_manager._generate_key("test_func")

        assert key == "test_func"

    def test_generate_key_none_values(self):
        """Test key generation with None values."""
        cache_manager = CacheManager()

        key = cache_manager._generate_key("test_func", None, param=None)

        # Should handle None values gracefully
        assert "test_func" in key

    @pytest.mark.asyncio
    async def test_set_serialization_error(self):
        """Test set method with unserializable data."""
        mock_redis = AsyncMock()
        mock_redis.set = AsyncMock()

        cache_manager = CacheManager()
        cache_manager.redis = mock_redis
        cache_manager.is_connected = True

        # Create an unserializable object
        class UnserializableClass:
            def __init__(self):
                self.func = lambda x: x  # Functions are not JSON serializable

        unserializable_obj = UnserializableClass()

        # Should handle serialization gracefully using default=str
        result = await cache_manager.set("test_key", unserializable_obj)

        assert result is True
        mock_redis.set.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
