"""
Mock Tests for Redis Cache Module

Tests cache functionality using mocked Redis to verify logic without requiring
a running Redis server. This allows testing in environments where Redis
is not available.
"""

import asyncio
import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from pme_calculator.backend.cache import (
    make_cache_key,
    cache_get,
    cache_set,
    cache_delete,
    cache_clear_pattern,
    cache_stats
)

class TestCacheKeyGeneration:
    """Test cache key generation (no Redis required)."""
    
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

@pytest.mark.asyncio
class TestCacheOperationsMocked:
    """Test cache operations with mocked Redis."""
    
    @patch('pme_calculator.backend.cache.get_redis_pool')
    async def test_cache_set_success(self, mock_get_pool):
        """Test successful cache set operation."""
        # Mock Redis
        mock_redis = AsyncMock()
        mock_redis.set.return_value = True
        mock_get_pool.return_value = mock_redis
        
        # Test cache set
        key = "test:key"
        data = {"test": "data"}
        result = await cache_set(key, data, ttl=60)
        
        assert result is True
        mock_redis.set.assert_called_once()
        
        # Verify the call arguments
        call_args = mock_redis.set.call_args
        assert call_args[0][0] == key  # key
        assert json.loads(call_args[0][1]) == data  # value
        assert call_args[1]['ex'] == 60  # TTL
    
    @patch('pme_calculator.backend.cache.get_redis_pool')
    async def test_cache_get_hit(self, mock_get_pool):
        """Test successful cache get (hit)."""
        # Mock Redis
        mock_redis = AsyncMock()
        test_data = {"test": "data"}
        mock_redis.get.return_value = json.dumps(test_data)
        mock_get_pool.return_value = mock_redis
        
        # Test cache get
        key = "test:key"
        result = await cache_get(key)
        
        assert result == test_data
        mock_redis.get.assert_called_once_with(key)
    
    @patch('pme_calculator.backend.cache.get_redis_pool')
    async def test_cache_get_miss(self, mock_get_pool):
        """Test cache get miss."""
        # Mock Redis
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        mock_get_pool.return_value = mock_redis
        
        # Test cache get
        key = "test:key"
        result = await cache_get(key)
        
        assert result is None
        mock_redis.get.assert_called_once_with(key)
    
    @patch('pme_calculator.backend.cache.get_redis_pool')
    async def test_cache_delete_success(self, mock_get_pool):
        """Test successful cache delete."""
        # Mock Redis
        mock_redis = AsyncMock()
        mock_redis.delete.return_value = 1  # 1 key deleted
        mock_get_pool.return_value = mock_redis
        
        # Test cache delete
        key = "test:key"
        result = await cache_delete(key)
        
        assert result is True
        mock_redis.delete.assert_called_once_with(key)
    
    @patch('pme_calculator.backend.cache.get_redis_pool')
    async def test_cache_clear_pattern(self, mock_get_pool):
        """Test cache pattern clearing."""
        # Mock Redis
        mock_redis = AsyncMock()
        mock_redis.keys.return_value = ["key1", "key2", "key3"]
        mock_redis.delete.return_value = 3
        mock_get_pool.return_value = mock_redis
        
        # Test pattern clear
        pattern = "test:*"
        result = await cache_clear_pattern(pattern)
        
        assert result == 3
        mock_redis.keys.assert_called_once_with(pattern)
        mock_redis.delete.assert_called_once_with("key1", "key2", "key3")
    
    @patch('pme_calculator.backend.cache.get_redis_pool')
    async def test_cache_stats(self, mock_get_pool):
        """Test cache statistics."""
        # Mock Redis
        mock_redis = AsyncMock()
        mock_redis.info.side_effect = [
            {"used_memory_human": "1.5M", "used_memory_peak_human": "2.0M"},  # memory info
            {"db0": {"keys": 100}}  # keyspace info
        ]
        mock_redis.keys.return_value = ["pme:key1", "pme:key2"]
        mock_get_pool.return_value = mock_redis
        
        # Test stats
        stats = await cache_stats()
        
        assert stats["connected"] is True
        assert stats["redis_memory_used"] == "1.5M"
        assert stats["total_keys"] == 100
        assert stats["pme_cache_keys"] == 2

@pytest.mark.asyncio
class TestCacheErrorHandling:
    """Test cache error handling with mocked failures."""
    
    @patch('pme_calculator.backend.cache.get_redis_pool')
    async def test_cache_get_error_handling(self, mock_get_pool):
        """Test cache get handles Redis errors gracefully."""
        # Mock Redis to raise an exception
        mock_redis = AsyncMock()
        mock_redis.get.side_effect = Exception("Redis connection error")
        mock_get_pool.return_value = mock_redis
        
        key = "test:key"
        result = await cache_get(key)
        
        assert result is None  # Should return None on error, not raise
    
    @patch('pme_calculator.backend.cache.get_redis_pool')
    async def test_cache_set_error_handling(self, mock_get_pool):
        """Test cache set handles Redis errors gracefully."""
        # Mock Redis to raise an exception
        mock_redis = AsyncMock()
        mock_redis.set.side_effect = Exception("Redis connection error")
        mock_get_pool.return_value = mock_redis
        
        key = "test:key"
        result = await cache_set(key, {"test": "data"})
        
        assert result is False  # Should return False on error, not raise

def test_cache_roundtrip_sprint_example_mocked():
    """Test the exact example from the sprint specification with mocked Redis."""
    
    async def _mock_roundtrip():
        with patch('pme_calculator.backend.cache.get_redis_pool') as mock_get_pool:
            # Mock Redis for set operation
            mock_redis = AsyncMock()
            mock_redis.set.return_value = True
            mock_redis.get.return_value = json.dumps({"answer": 42})
            mock_get_pool.return_value = mock_redis
            
            # Execute the example
            key = make_cache_key("/v1/metrics/irr_pme", {"fund": "X"})
            await cache_set(key, {"answer": 42}, ttl=5)
            cached_result = await cache_get(key)
            return cached_result["answer"]
    
    # Run the test
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_mock_roundtrip())
        assert result == 42
    finally:
        loop.close()

class TestCacheIntegration:
    """Integration tests for cache functionality."""
    
    def test_cache_key_consistency(self):
        """Test that cache keys are consistent across different scenarios."""
        # Test various endpoint patterns
        endpoints = [
            "/v1/metrics/irr_pme",
            "/v1/metrics/twr_vs_index", 
            "/v1/metrics/cashflow_overview",
            "/v1/metrics/net_cf_market",
            "/v1/metrics/pme_progression"
        ]
        
        for endpoint in endpoints:
            payload = {"fund_id": "test123", "start_date": "2020-01-01"}
            key1 = make_cache_key(endpoint, payload)
            key2 = make_cache_key(endpoint, payload)
            
            # Keys should be identical
            assert key1 == key2
            
            # Keys should contain endpoint info
            clean_endpoint = endpoint.replace("/", "_")
            assert clean_endpoint in key1
            
            # Keys should be reasonably short
            assert len(key1) < 100

if __name__ == "__main__":
    # Run a simple test
    print("Testing cache key generation...")
    key = make_cache_key("/v1/metrics/irr_pme", {"fund_id": "test123"})
    print(f"Generated key: {key}")
    print("✅ Cache key generation works!") 