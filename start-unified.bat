@echo off
echo Starting Resume Relevance System
echo ================================

REM Set environment variables
set PYTHONPATH=%PYTHONPATH%;%CD%

echo Starting Streamlit application...
echo Dashboard will be available at: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.

REM Run Streamlit app
streamlit run streamlit_app.py --server.port 8501