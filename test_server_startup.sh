#!/bin/bash

echo "🚀 Testing server startup with fixed PMEAnalysisEngine..."

# Kill any processes on port 8000
echo "🧹 Cleaning up port 8000..."
lsof -ti :8000 | xargs -r kill -9 2>/dev/null || true
sleep 2

# Test the import first
cd pme_calculator/backend
echo "🔍 Testing import..."
python3 -c "
from analysis_engine import PMEAnalysisEngine
engine = PMEAnalysisEngine()
print('✅ PMEAnalysisEngine import successful')

# Test the methods
import tempfile
import pandas as pd

# Test load_fund_data
test_data = pd.DataFrame({
    'Date': ['2020-01-01', '2020-06-01'],
    'Contributions': [-100, -50],
    'Distributions': [0, 10],
    'NAV': [100, 140]
})

with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
    test_data.to_csv(f.name, index=False)
    result = engine.load_fund_data(f.name)
    print(f'✅ load_fund_data successful: {result}')
    import os
    os.unlink(f.name)

print('🎉 All method tests passed!')
"

if [ $? -eq 0 ]; then
    echo "✅ Import and method tests passed!"
    
    # Try to start the server
    echo "🚀 Starting server..."
    timeout 10s python3 main_minimal.py &
    SERVER_PID=$!
    
    sleep 5
    
    # Check if server is running
    if curl -s http://localhost:8000/api/health > /dev/null; then
        echo "✅ Server started successfully!"
        kill $SERVER_PID 2>/dev/null
    else
        echo "⚠️  Server may not have started properly"
        kill $SERVER_PID 2>/dev/null
    fi
else
    echo "❌ Import/method tests failed"
fi

echo "🎉 Server startup test complete!" 