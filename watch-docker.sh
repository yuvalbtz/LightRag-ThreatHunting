#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda activate lightrag_env

echo "🐳 Starting Docker Compose with hot reload..."
echo "✅ Development environment started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Note: Frontend runs on port 3000 (not 5173) in development mode" 

# Global variable for server PID
SERVER_PID=""

# Function to start uvicorn server
start_server() {
    echo "Starting uvicorn server..."
    uvicorn api:app --host 0.0.0.0 --port 8000 --log-level info --log-config /dev/null &
    SERVER_PID=$!
    echo "Server started with PID: $SERVER_PID"
}

# Function to stop server
stop_server() {
    if [ ! -z "$SERVER_PID" ]; then
        echo "Stopping server with PID: $SERVER_PID"
        kill $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
    fi
}

# Function to check for file changes
check_changes() {
    find /app -name "*.py" -newer /tmp/last_check 2>/dev/null | head -1
}

# Signal handler for graceful shutdown
cleanup() {
    echo "Received shutdown signal, cleaning up..."
    stop_server
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Start the server
start_server

# Create initial timestamp
touch /tmp/last_check

# Main loop for file watching
while true; do
    sleep 2
    
    # Check for changes
    if [ ! -z "$(check_changes)" ]; then
        echo "File changes detected, restarting server..."
        stop_server
        start_server
        touch /tmp/last_check
    fi
done 