#!/bin/bash

echo "🚀 PME Calculator Quick Start"
echo "============================="

# Step 1: Fix analysis engine
echo "🔧 Step 1: Fixing analysis engine..."
python3 fix_analysis_engine.py

if [ $? -ne 0 ]; then
    echo "❌ Could not fix analysis engine. Stopping."
    exit 1
fi

# Step 2: Check system status
echo ""
echo "🔍 Step 2: Checking system status..."
python3 check_localhost.py

echo ""
echo "🎯 QUICK START COMMANDS:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd pme_calculator/backend && python3 main_minimal.py"
echo ""
echo "Terminal 2 (Frontend):"
echo "  cd pme_calculator/frontend && npm run dev"
echo ""
echo "Then visit: http://localhost:5173" 