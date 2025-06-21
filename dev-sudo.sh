#!/bin/bash

echo "🚀 Starting LightRag Threat Hunting with Hot Reload (with sudo)..."

# Stop any existing containers
echo "🛑 Stopping existing containers..."
sudo docker-compose down

# Build and start development environment
echo "🔨 Building and starting development environment..."
sudo docker-compose -f docker-compose.dev.yml up --build

echo "✅ Development environment started!"
echo "📱 Frontend (Vite Dev Server): http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Note: Frontend runs on port 3000 (not 5173) in development mode"
echo "🔄 Backend hot reload is now working with uvicorn --reload!" 