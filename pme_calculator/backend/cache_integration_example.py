#!/usr/bin/env python3
"""
Example of how to integrate Redis cache with the PME calculator.
"""

import asyncio
from cache import cached, cache, init_cache

# Example: Cache expensive PME calculations
@cached(ttl=1800, key_prefix="pme_calculation")  # 30 minutes
async def calculate_pme_cached(fund_data, index_data, calculation_params):
    """
    Cached PME calculation function.
    
    This would replace expensive PME calculations with cached results.
    """
    # Simulate expensive calculation
    await asyncio.sleep(0.1)  # Simulate computation time
    
    # In real implementation, this would call the actual PME calculation
    result = {
        "pme_ratio": 1.25,
        "irr": 0.15,
        "multiple": 2.1,
        "calculation_time": "cached" if await cache.exists(
            cache._generate_key("pme_calculation", fund_data, index_data, calculation_params)
        ) else "computed"
    }
    
    return result

# Example: Cache analysis results
@cached(ttl=3600, key_prefix="analysis_result")  # 1 hour
async def get_analysis_results_cached(analysis_id):
    """
    Cached analysis results retrieval.
    """
    # Simulate database/computation
    await asyncio.sleep(0.05)
    
    return {
        "analysis_id": analysis_id,
        "status": "completed",
        "results": {
            "funds_analyzed": 10,
            "total_pme": 1.18,
            "avg_irr": 0.12
        }
    }

async def demo_cache_usage():
    """Demonstrate cache usage."""
    print("🚀 Cache Integration Demo")
    
    # Initialize cache
    await init_cache()
    
    # First call - will compute and cache
    print("\n📊 First PME calculation (will be computed)...")
    result1 = await calculate_pme_cached("fund_a", "sp500", {"method": "ks_pme"})
    print(f"Result: {result1}")
    
    # Second call - will use cache
    print("\n📊 Second PME calculation (should be cached)...")
    result2 = await calculate_pme_cached("fund_a", "sp500", {"method": "ks_pme"})
    print(f"Result: {result2}")
    
    # Analysis results demo
    print("\n📈 Analysis results (first call)...")
    analysis1 = await get_analysis_results_cached("analysis_123")
    print(f"Analysis: {analysis1}")
    
    print("\n📈 Analysis results (second call - cached)...")
    analysis2 = await get_analysis_results_cached("analysis_123")
    print(f"Analysis: {analysis2}")
    
    # Manual cache operations
    print("\n🔧 Manual cache operations...")
    await cache.set("manual_key", {"data": "manual_value"}, ttl=60)
    manual_result = await cache.get("manual_key")
    print(f"Manual cache result: {manual_result}")
    
    # Close cache connection
    await cache.close()
    print("\n✅ Cache demo completed!")

if __name__ == "__main__":
    asyncio.run(demo_cache_usage()) 