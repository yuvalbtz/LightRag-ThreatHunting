#!/bin/bash

# Production startup script with .env support
echo "🚀 Starting ThreatHunting Production Environment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ Created .env from env.example"
        echo "📝 Please edit .env with your production configuration values"
        echo "⚠️  Remember to set DEBUG=false and use production secrets!"
    else
        echo "❌ env.example not found. Please create a .env file manually."
        exit 1
    fi
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start production environment with .env file
echo "🔨 Building and starting production environment..."
docker-compose -f docker-compose.prod.yml --env-file .env up --build -d

echo "✅ Production environment started!"
echo "🌐 Frontend: http://localhost"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Note: Frontend runs on port 3000 (not 5173) in production mode" 