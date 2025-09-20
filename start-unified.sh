#!/bin/bash

echo "Starting Resume Relevance System"
echo "================================"

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "Starting Streamlit application..."
echo "Dashboard will be available at: http://localhost:8501"
echo "Press Ctrl+C to stop the server"
echo ""

# Run Streamlit app
streamlit run streamlit_app.py --server.port 8501