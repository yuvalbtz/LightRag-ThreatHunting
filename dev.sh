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
    docker compose -f docker-compose.dev.yml --env-file .env --profile llm up --build
else
    echo "🐳 Running containers..."
    docker compose -f docker-compose.dev.yml --env-file .env --profile llm up
fi

