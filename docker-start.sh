#!/bin/bash

# Docker startup script for Resume Relevance System

echo "🚀 Starting Resume Relevance Check System in Docker..."

# Start FastAPI backend in background
uvicorn app.main:app --host 0.0.0.0 --port 8003 &

# Wait for backend to start
sleep 5

# Start Streamlit dashboard
streamlit run app/streamlit_app.py --server.port 8505 --server.address 0.0.0.0