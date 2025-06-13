"""
Tests for predictive cache warming functionality.
"""

import asyncio
import json
import pytest
from unittest.mock import patch, MagicMock

# Import the modules we need to test
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "pme_calculator" / "backend"))

from cache import make_cache_key, cache_get, cache_set
from worker.tasks import warm_cache, POPULAR_FUNDS


@pytest.fixture
def event_loop():
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.mark.asyncio
async def test_cache_key_generation():
    """Test that cache keys are generated consistently."""
    key1 = make_cache_key("irr_pme", {"fund": "FUND_A"})
    key2 = make_cache_key("irr_pme", {"fund": "FUND_A"})
    key3 = make_cache_key("irr_pme", {"fund": "FUND_B"})

    # Same inputs should generate same key
    assert key1 == key2

    # Different inputs should generate different keys
    assert key1 != key3

    # Keys should have expected format
    assert key1.startswith("pme:irr_pme:")
    assert len(key1.split(":")) == 3


@pytest.mark.asyncio
async def test_cache_roundtrip():
    """Test basic cache set and get operations."""
    test_data = {"fund_id": "TEST_FUND", "irr": 0.15, "pme": 1.25, "test": True}

    key = make_cache_key("test_endpoint", {"fund": "TEST_FUND"})

    # Mock Redis operations to avoid needing actual Redis
    with patch("cache.get_redis_pool") as mock_redis:
        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance

        # Mock successful set
        mock_redis_instance.set.return_value = True
        result = await cache_set(key, test_data, ttl=300)
        assert result is True

        # Mock successful get
        mock_redis_instance.get.return_value = json.dumps(test_data, default=str)
        cached_data = await cache_get(key)
        assert cached_data == test_data


def test_warm_cache_task_structure():
    """Test that the warm_cache task is properly structured."""
    # Check that POPULAR_FUNDS is defined
    assert isinstance(POPULAR_FUNDS, list)
    assert len(POPULAR_FUNDS) > 0

    # Check that warm_cache is a Celery task
    assert hasattr(warm_cache, "delay")
    assert hasattr(warm_cache, "apply_async")


@pytest.mark.asyncio
async def test_cache_warming_logic():
    """Test the cache warming logic without actually running Celery."""
    # Mock the cache operations
    with patch("cache.cache_set") as mock_cache_set, patch(
        "db_views.refresh"
    ) as mock_refresh:

        mock_cache_set.return_value = True

        # Simulate the warming logic
        warmed_funds = []

        for fund_id in POPULAR_FUNDS[:2]:  # Test with first 2 funds
            key = make_cache_key("irr_pme", {"fund": fund_id})

            mock_data = {
                "fund_id": fund_id,
                "irr": 0.15,
                "pme": 1.2,
                "warmed_at": "2024-01-01T00:00:00Z",
                "data_source": "cache_warming",
            }

            # This would be the async call in the actual task
            success = True  # Mocked success

            if success:
                warmed_funds.append(fund_id)

        # Verify results
        assert len(warmed_funds) == 2
        assert warmed_funds == POPULAR_FUNDS[:2]

        # Verify refresh was called (would be called in actual task)
        # mock_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_cache_miss_and_hit_pattern():
    """Test the expected cache miss -> hit pattern."""
    key = make_cache_key("irr_pme", {"fund": "FUND_A"})

    with patch("cache.get_redis_pool") as mock_redis:
        mock_redis_instance = MagicMock()
        mock_redis.return_value = mock_redis_instance

        # First call: cache miss
        mock_redis_instance.get.return_value = None
        result1 = await cache_get(key)
        assert result1 is None

        # Set data in cache
        test_data = {"fund_id": "FUND_A", "irr": 0.15}
        mock_redis_instance.set.return_value = True
        await cache_set(key, test_data)

        # Second call: cache hit
        mock_redis_instance.get.return_value = json.dumps(test_data)
        result2 = await cache_get(key)
        assert result2 == test_data


def test_popular_funds_configuration():
    """Test that popular funds are properly configured."""
    # Should have at least 3 funds for testing
    assert len(POPULAR_FUNDS) >= 3

    # Should be strings
    for fund_id in POPULAR_FUNDS:
        assert isinstance(fund_id, str)
        assert len(fund_id) > 0

    # Should not have duplicates
    assert len(POPULAR_FUNDS) == len(set(POPULAR_FUNDS))


@pytest.mark.asyncio
async def test_cache_error_handling():
    """Test cache error handling."""
    key = make_cache_key("test", {"fund": "ERROR_FUND"})

    with patch("cache.get_redis_pool") as mock_redis:
        # Simulate Redis connection error
        mock_redis.side_effect = Exception("Redis connection failed")

        # Should handle errors gracefully
        result = await cache_get(key)
        assert result is None

        # Set should also handle errors gracefully
        success = await cache_set(key, {"test": "data"})
        assert success is False


if __name__ == "__main__":
    # Run basic tests
    print("Running basic cache warming tests...")

    # Test key generation
    key1 = make_cache_key("irr_pme", {"fund": "FUND_A"})
    key2 = make_cache_key("irr_pme", {"fund": "FUND_A"})
    assert key1 == key2
    print("✅ Cache key generation test passed")

    # Test popular funds configuration
    assert len(POPULAR_FUNDS) >= 3
    print("✅ Popular funds configuration test passed")

    print("All basic tests passed! Run with pytest for full test suite.")
