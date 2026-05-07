#!/bin/bash

# OmniBot Quick Start Script
# This script sets up and runs the entire project

echo "🤖 OmniBot - Quick Start Setup"
echo "================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Python and Node.js found!"
echo ""

# Setup Backend
echo "📦 Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f "../.env" ]; then
    echo "Creating .env file..."
    cp ../.env.example ../.env
    echo "⚠️  Please edit .env file with your API keys before running bots!"
fi

# Initialize database
echo "Initializing database..."
python -c "from app.models.database import init_db; import asyncio; asyncio.run(init_db())"

echo "✅ Backend setup complete!"
echo ""

# Setup Frontend
echo "📦 Setting up frontend..."
cd ../frontend

# Install dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
fi

echo "✅ Frontend setup complete!"
echo ""

# Instructions
echo "🎉 Setup Complete!"
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "Terminal 3 (Optional) - Telegram Bot:"
echo "  cd bots/telegram"
echo "  python bot.py"
echo ""
echo "🌐 Web Interface: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Happy coding! 🚀"
