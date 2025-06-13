#!/bin/bash

echo "🛑 Stopping PME Calculator Web Application..."

# Function to kill processes matching a pattern.
# The `|| true` prevents the script from exiting if no processes are found.
kill_process() {
    local pattern=$1
    echo "🔎 Searching for processes matching '${pattern}'..."
    if pgrep -f "${pattern}" > /dev/null; then
        echo "⛔ Killing processes matching '${pattern}'..."
        pkill -9 -f "${pattern}"
    else
        echo "✅ No running processes found for '${pattern}'."
    fi
}

# Kill backend and frontend processes using specific patterns
kill_process "uvicorn.*main_minimal:app"
kill_process "vite.*--port 5173"
kill_process "node.*vite"

echo "⏳ Waiting a moment for processes to terminate..."
sleep 1

echo "🔍 Final check..."
if pgrep -f "main_minimal" > /dev/null || pgrep -f "vite" > /dev/null; then
    echo "⚠️  Some processes survived. Retrying with broader patterns."
    kill_process "main_minimal"
    kill_process "vite"
    echo "🛑 Final cleanup sweep complete."
else
    echo "🎉 All application processes stopped cleanly."
fi

# Exit with success code to allow command chaining
exit 0 