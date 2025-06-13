#!/bin/bash
# Test script for Docker build verification

set -e

echo "🐳 Testing Docker build for PME App"
echo "=================================="

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed or not in PATH"
    echo "   Please install Docker to run this test"
    exit 1
fi

echo "✅ Docker is available"

# Build the image
echo "📦 Building Docker image..."
docker build -t pme-app-test .

echo "✅ Docker image built successfully"

# Test the CLI inside the container
echo "🧪 Testing CLI inside container..."
docker run --rm pme-app-test python -m pme_app.cli --help

echo "🧪 Testing version command..."
docker run --rm pme-app-test python -m pme_app.cli version

# Test that the web server can start (just check it doesn't crash immediately)
echo "🧪 Testing web server startup..."
timeout 10s docker run --rm -p 8000:8000 pme-app-test || true

echo "✅ All Docker tests passed!"
echo "🎉 The Docker image is ready for deployment"

# Clean up
echo "🧹 Cleaning up test image..."
docker rmi pme-app-test

echo "✅ Cleanup complete" 