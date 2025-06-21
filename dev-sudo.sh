#!/bin/bash

# Development startup script with sudo and .env support
echo "🚀 Starting ThreatHunting Development Environment with sudo..."

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

# Stop any existing containers
echo "🛑 Stopping existing containers..."
sudo docker-compose down

# Build and start development environment with .env file
echo "🔨 Building and starting development environment..."
sudo docker-compose -f docker-compose.dev.yml --env-file .env up --build

echo "✅ Development environment started!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Note: Frontend runs on port 3000 (not 5173) in development mode"
echo "🔄 Backend hot reload is now working with uvicorn --reload!" 