#!/bin/bash

echo "🚀 Starting LightRag Threat Hunting in Production..."

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down

# Build and start production environment
echo "🔨 Building and starting production environment..."
docker-compose -f docker-compose.prod.yml up --build

echo "✅ Production environment started!"
echo "📱 Frontend (Vite Dev Server): http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Note: Frontend runs on port 3000 (not 5173) in production mode" 