#!/bin/bash

echo "🚀 Building Docker image..."
docker build -t virtual-classroom:latest .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo ""
    echo "📦 To run locally with Docker:"
    echo "   docker-compose up"
    echo ""
    echo "🌐 To deploy to Render:"
    echo "   1. Push to GitHub"
    echo "   2. Connect repo in Render dashboard"
    echo "   3. Set environment variables (MONGO_URL, ADMIN_SECRET_KEY)"
    echo ""
else
    echo "❌ Docker build failed!"
    exit 1
fi
