@echo off
echo 🚀 Starting Resume Relevance System - FastAPI + Streamlit
echo =========================================================

REM Set environment variables
set PYTHONPATH=%PYTHONPATH%;%CD%

REM Start FastAPI backend in background
echo 📡 Starting FastAPI backend server on port 8080...
start /B python -m uvicorn app.main:app --host 0.0.0.0 --port 8080

REM Wait a moment for FastAPI to start
timeout /t 3 /nobreak >nul

REM Start Streamlit frontend
echo 🎨 Starting Streamlit UI on port 8501...
echo 🌐 Dashboard: http://localhost:8501
echo 📚 API Docs: http://localhost:8080/docs
echo ⏹️  Press Ctrl+C to stop the servers
echo.

REM Run Streamlit
cd app && streamlit run streamlit_app.py --server.port 8501