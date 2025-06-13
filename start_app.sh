#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "🚀 Starting PME Calculator Web Application..."
echo "Project root is: $SCRIPT_DIR"

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🧹 Cleaning up processes..."
    # Use pkill with the -f flag to match the full command string
    pkill -f "uvicorn.*main_minimal:app"
    pkill -f "vite.*--port 5173"
    pkill -f "node.*vite"
    echo "✅ Cleanup complete"
    exit 0
}

# Set up signal handlers to call cleanup function on exit
trap cleanup SIGINT SIGTERM

echo "🧹 Cleaning up any old processes..."
pkill -f "uvicorn.*main_minimal:app" 2>/dev/null
pkill -f "vite.*--port 5173" 2>/dev/null
pkill -f "node.*vite" 2>/dev/null
sleep 1

# Define backend and frontend directories relative to the script
BACKEND_DIR="$SCRIPT_DIR/pme_calculator/backend"
FRONTEND_DIR="$SCRIPT_DIR/pme_calculator/frontend"

# Check if directories exist
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Error: Backend directory not found at $BACKEND_DIR"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "⚠️  Warning: Frontend directory not found at $FRONTEND_DIR. Running backend only."
    FRONTEND_AVAILABLE=false
else
    FRONTEND_AVAILABLE=true
fi

# Start backend
echo "🔧 Starting backend in $BACKEND_DIR..."
cd "$BACKEND_DIR"
python3 main_minimal.py &
BACKEND_PID=$!

# Wait for backend to start and check if it's running
echo "⏳ Waiting for backend to initialize..."
sleep 4 # Increased wait time
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start. Check backend logs."
    exit 1
fi
echo "✅ Backend started with PID $BACKEND_PID"

# Start frontend if available
if [ "$FRONTEND_AVAILABLE" = true ]; then
    echo "🎨 Starting frontend in $FRONTEND_DIR..."
    cd "$FRONTEND_DIR"
    
    if [ ! -d "node_modules" ]; then
        echo "📦 node_modules not found. Running npm install..."
        npm install
    fi
    
    npm run dev &
    FRONTEND_PID=$!
    echo "✅ Frontend started with PID $FRONTEND_PID"
    
    echo "🚀 Application is running!"
    echo "   - 🖥️  Frontend: http://localhost:5173"
    echo "   - 📊 Backend:  http://localhost:8000/api/docs"
    
    # Wait for either process to exit, then trigger cleanup
    wait -n $BACKEND_PID $FRONTEND_PID
    cleanup
else
    echo "🚀 Backend is running!"
    echo "   - 📊 Backend: http://localhost:8000/api/docs"
    wait $BACKEND_PID
    cleanup
fi 