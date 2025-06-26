#!/bin/bash

echo "🐳 Starting Ollama server..."
ollama serve &

# Give the server a few seconds to start
sleep 3

echo "⬇️ Pulling models..."
ollama pull qwen2.5:1.5b
ollama pull nomic-embed-text:latest

echo "✅ Ollama server and models are ready."

# Keep the container running
tail -f /dev/null
