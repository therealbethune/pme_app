#!/bin/bash

echo "🚀 Applying upload fix for PMEAnalysisEngine..."

# Step 1: Kill existing server
echo "🧹 Killing existing server on port 8000..."
lsof -ti :8000 | xargs -r kill -9 2>/dev/null || true
sleep 2

# Step 2: Navigate to backend directory
cd pme_calculator/backend

# Step 3: Test the fix
echo "🔍 Testing upload fix..."
python3 ../test_upload_fix.py

if [ $? -eq 0 ]; then
    echo "✅ Upload fix test passed!"
    
    # Step 4: Test server startup
    echo "🚀 Testing server startup..."
    timeout 10s python3 main_minimal.py &
    SERVER_PID=$!
    
    sleep 5
    
    # Check if server is running
    if curl -s http://localhost:8000/api/health > /dev/null; then
        echo "✅ Server started successfully!"
        echo "🎉 Upload fix applied and tested successfully!"
        echo ""
        echo "📋 Next steps:"
        echo "   1. Frontend: http://localhost:5173/"
        echo "   2. Backend: http://localhost:8000/"
        echo "   3. API Docs: http://localhost:8000/api/docs"
        echo "   4. Try uploading a file to test the fix!"
        
        # Keep server running
        wait $SERVER_PID
    else
        echo "⚠️  Server may not have started properly"
        kill $SERVER_PID 2>/dev/null
        exit 1
    fi
else
    echo "❌ Upload fix test failed"
    exit 1
fi 