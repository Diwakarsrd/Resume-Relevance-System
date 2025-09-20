#!/bin/bash

echo "🚀 Starting Resume Relevance System - FastAPI + Streamlit"
echo "========================================================="

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start FastAPI backend in background
echo "📡 Starting FastAPI backend server on port 8080..."
cd app && python -m uvicorn main:app --host 0.0.0.0 --port 8080 &
FASTAPI_PID=$!

# Wait a moment for FastAPI to start
sleep 3

# Start Streamlit frontend
echo "🎨 Starting Streamlit UI on port 8501..."
echo "🌐 Dashboard: http://localhost:8501"
echo "📚 API Docs: http://localhost:8080/docs"
echo "⏹️  Press Ctrl+C to stop the servers"
echo ""

# Function to handle cleanup
cleanup() {
    echo "\nShutting down servers..."
    kill $FASTAPI_PID 2>/dev/null
    exit 0
}

# Set trap to call cleanup function on script exit
trap cleanup SIGINT SIGTERM

# Run Streamlit (this will keep the script running)
streamlit run streamlit_app.py --server.port 8501

# If we get here, cleanup
cleanup