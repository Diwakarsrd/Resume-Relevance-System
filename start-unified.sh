#!/bin/bash

echo "🚀 Starting Resume Relevance System - Single Host Mode"
echo "=============================================="

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start the unified application
echo "📡 Starting unified FastAPI + Dashboard server..."
echo "🌐 Dashboard will be available at: http://localhost:8000"
echo "📚 API Documentation: http://localhost:8000/docs"
echo "⏹️  Press Ctrl+C to stop the server"
echo ""

# Run the FastAPI app with uvicorn
cd app && uvicorn main:app --host 0.0.0.0 --port 8000 --reload