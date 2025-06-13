#!/bin/bash

echo "🚀 Running comprehensive loading issue tests..."

# Kill any processes on port 8000
echo "🧹 Cleaning up port 8000..."
lsof -ti :8000 | xargs -r kill -9 2>/dev/null || true

# Run the test
cd pme_calculator/backend
python3 test_loading_issues_comprehensive.py

echo "🎉 Loading tests complete!" 