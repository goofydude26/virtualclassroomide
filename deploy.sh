#!/bin/bash

# Virtual Classroom - Quick Deploy Script
# This script helps you deploy to Render or run locally

echo "🎓 Virtual Classroom - Deployment Helper"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker is not installed on this system."
    echo ""
    echo "📋 Deployment Options:"
    echo ""
    echo "Option 1: Deploy directly to Render (Recommended)"
    echo "  1. Create MongoDB Atlas account (free): https://www.mongodb.com/cloud/atlas"
    echo "  2. Get your connection string"
    echo "  3. Push code to GitHub:"
    echo "     git init"
    echo "     git add ."
    echo "     git commit -m 'Initial commit'"
    echo "     git remote add origin YOUR_REPO_URL"
    echo "     git push -u origin main"
    echo "  4. Go to Render: https://dashboard.render.com/"
    echo "  5. New Web Service → Connect your repo"
    echo "  6. Render auto-detects render.yaml"
    echo "  7. Add environment variables:"
    echo "     - MONGO_URL: your MongoDB Atlas connection string"
    echo "     - ADMIN_SECRET_KEY: a secure password for admin signup"
    echo ""
    echo "Option 2: Install Docker locally"
    echo "  macOS: https://docs.docker.com/desktop/install/mac-install/"
    echo "  Then run: ./deploy.sh"
    echo ""
    exit 0
fi

# Docker is installed, proceed with build
echo "✅ Docker found!"
echo ""
echo "Building Docker image..."
docker build -t virtual-classroom:latest .

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "🚀 Next steps:"
    echo ""
    echo "To run locally:"
    echo "  docker-compose up"
    echo ""
    echo "To deploy to Render:"
    echo "  1. Push to GitHub"
    echo "  2. Follow instructions in README.md"
    echo ""
else
    echo ""
    echo "❌ Build failed. Check the errors above."
    exit 1
fi
