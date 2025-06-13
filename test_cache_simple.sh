#!/bin/bash

echo "🧪 Testing Redis cache implementation..."

cd pme_calculator/backend

# Run the verification script
echo "📋 Running cache verification test..."
python3 test_cache_verification.py

if [ $? -eq 0 ]; then
    echo "✅ Cache verification passed"
else
    echo "❌ Cache verification failed"
    exit 1
fi

# Run pytest on cache tests
echo "📋 Running pytest cache tests..."
python3 -m pytest tests/test_cache.py -v

if [ $? -eq 0 ]; then
    echo "✅ All cache tests passed"
else
    echo "❌ Some cache tests failed"
    exit 1
fi

echo "🎉 All cache tests completed successfully!" 