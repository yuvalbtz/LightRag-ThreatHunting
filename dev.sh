#!/bin/bash

# Development startup script with .env support
echo "🚀 Starting ThreatHunting Development Environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ Created .env from env.example"
        echo "📝 Please edit .env with your configuration values"
    else
        echo "❌ env.example not found. Please create a .env file manually."
        exit 1
    fi
fi

## check if docker should build the containers or only run the containers   
if [ "$1" == "build" ]; then
    echo "🔨 Building containers..."
    print_logs
    docker-compose -f docker-compose.dev.yml --env-file .env up --build
else
    echo "🐳 Running containers..."
    print_logs
    docker-compose -f docker-compose.dev.yml --env-file .env up
fi



# function to print the logs of the containers
function print_logs() {
    echo "🐳 Starting Docker Compose with hot reload..."
    echo "✅ Development environment started!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
    echo "📚 API Docs: http://localhost:8000/docs"
    echo ""
    echo "💡 Note: Frontend runs on port 3000 (not 5173) in development mode" 
}


