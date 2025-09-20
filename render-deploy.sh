#!/bin/bash

# Single deployment script for Render
# This starts both FastAPI backend and Streamlit dashboard

echo "🚀 Starting Resume Relevance System on Render..."

# Create uploads directory
mkdir -p app/uploads

# Start FastAPI backend in background on port from environment
uvicorn app.main:app --host 0.0.0.0 --port $PORT &

# Get the backend PID
BACKEND_PID=$!

# Wait for backend to start
sleep 5

echo "✅ Backend started on port $PORT"
echo "🎨 Starting Streamlit dashboard on port $((PORT + 1))..."

# Start Streamlit dashboard on next port
streamlit run app/streamlit_app.py --server.port $((PORT + 1)) --server.address 0.0.0.0 &

# Get the dashboard PID  
DASHBOARD_PID=$!

echo "✅ Dashboard started on port $((PORT + 1))"
echo "🎉 Both services are running!"

# Keep both processes running
wait $BACKEND_PID $DASHBOARD_PID