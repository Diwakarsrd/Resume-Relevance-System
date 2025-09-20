@echo off
REM Resume Relevance Check System - Windows Startup Script

echo ==============================================
echo Resume Relevance Check System - Setup ^& Start
echo ==============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Create virtual environment if needed
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate environment and install dependencies
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check for .env file
if not exist ".env" (
    echo.
    echo ⚠️  WARNING: .env file missing!
    echo Create .env with: GEMINI_API_KEY=your_key
    echo.
    pause
)

REM Start services
echo.
echo 🚀 Starting FastAPI backend...
start "Resume API Server" cmd /k "call venv\Scripts\activate.bat && uvicorn app.main:app --host 0.0.0.0 --port 8003"

timeout /t 5 /nobreak >nul

echo 🎨 Starting Streamlit dashboard...
start "Resume Dashboard" cmd /k "call venv\Scripts\activate.bat && streamlit run app\streamlit_app.py --server.port 8505"

echo.
echo ==============================================
echo 🎉 System is running!
echo.
echo 📡 API Server: http://localhost:8003
echo 📚 API Docs: http://localhost:8003/docs  
echo 🎨 Dashboard: http://localhost:8505
echo.
echo Both services are running in separate windows.
echo Close those windows to stop the services.
echo ==============================================
echo.

pause