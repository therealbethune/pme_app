#!/bin/bash

echo "🔍 Verifying PME Calculator Startup"
echo "==================================="

# Apply quick fixes first
echo "🔧 Applying quick fixes..."
python3 quick_fix_loading.py

echo ""
echo "🧪 Running comprehensive tests..."
python3 test_loading_issues.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 All tests passed! Ready to start."
    echo ""
    echo "🚀 STARTUP COMMANDS:"
    echo ""
    echo "Terminal 1 (Backend):"
    echo "  cd pme_calculator/backend"
    echo "  python3 main_minimal.py"
    echo ""
    echo "Terminal 2 (Frontend):"
    echo "  cd pme_calculator/frontend"
    echo "  npm run dev"
    echo ""
    echo "Then visit: http://localhost:5173"
    echo ""
    echo "Expected behavior:"
    echo "  - File upload forms should appear"
    echo "  - No 'Loading...' stuck states"
    echo "  - Backend API accessible at http://localhost:8000/api/docs"
else
    echo ""
    echo "❌ Some tests failed. Check output above."
    exit 1
fi 