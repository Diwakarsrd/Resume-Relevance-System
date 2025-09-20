#!/bin/bash

# Resume Relevance Check System - Startup Script
# This script sets up and starts the complete system

echo "=============================================="
echo "Resume Relevance Check System - Setup & Start"
echo "=============================================="
echo

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ ERROR: Python is not installed or not in PATH"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

echo "✅ Python found: $(python --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo
    echo "⚠️  WARNING: .env file not found!"
    echo "Please create a .env file with your GEMINI_API_KEY"
    echo "Example: GEMINI_API_KEY=your_api_key_here"
    echo
    read -p "Press Enter to continue or Ctrl+C to exit..."
fi

# Start the backend server in background
echo
echo "🚀 Starting FastAPI backend server..."
uvicorn app.main:app --host 0.0.0.0 --port 8003 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Start the Streamlit dashboard
echo "🎨 Starting Streamlit dashboard..."
streamlit run app/streamlit_app.py --server.port 8505 &
DASHBOARD_PID=$!

echo
echo "=============================================="
echo "🎉 System is running!"
echo
echo "📡 API Server: http://localhost:8003"
echo "📚 API Docs: http://localhost:8003/docs"
echo "🎨 Dashboard: http://localhost:8505"
echo
echo "To stop the system:"
echo "kill $BACKEND_PID $DASHBOARD_PID"
echo "=============================================="

# Keep script running
wait