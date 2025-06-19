#!/bin/bash
# Local development script to run all checks (mirrors CI)

set -e

echo "🧹 Running code formatting..."
black .
ruff check --fix .

echo "🔍 Running type checking..."
tox -e typecheck

echo "🧪 Running root tests..."
tox -e test-root

echo "🧪 Running backend tests..."
tox -e test-backend

echo "📊 Generating coverage report..."
tox -e coverage-report

echo "✅ All checks passed! Ready for CI." 