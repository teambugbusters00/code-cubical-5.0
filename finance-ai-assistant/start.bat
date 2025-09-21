@echo off
REM Finance AI Assistant Startup Script for Windows
REM This script starts all components of the Finance AI Assistant

echo 🚀 Starting Finance AI Assistant...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if requirements.txt is newer than last install
if not exist ".requirements_installed" (
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
    echo. > .requirements_installed
)

REM Create necessary directories
echo 📁 Creating directories...
if not exist "logs" mkdir logs
if not exist "data" mkdir data

REM Function to start a service
set "start_service=start_service"

goto :start_services

:start_service
set "service_name=%~1"
set "command=%~2"
set "log_file=%~3"

echo ▶️ Starting %service_name%...
start "FinanceAI - %service_name%" cmd /c "%command% > %log_file% 2>&1"
echo    Log: %log_file%
goto :eof

:start_services

REM Start Pathway Data Processing (in background)
call :start_service "Pathway Data Processing" "cd data_processing && python financial_pipeline.py" "logs\pathway.log"

REM Wait a moment for Pathway to initialize
timeout /t 3 /nobreak > nul

REM Start FastAPI Backend
call :start_service "FastAPI Backend" "cd backend && python app.py" "logs\backend.log"

REM Wait a moment for backend to initialize
timeout /t 5 /nobreak > nul

REM Start Streamlit Frontend
call :start_service "Streamlit Frontend" "cd frontend && streamlit run app.py --server.headless true --server.address 0.0.0.0" "logs\frontend.log"

echo.
echo ✅ All services started successfully!
echo.
echo 🌐 Access points:
echo    • Frontend Dashboard: http://localhost:8501
echo    • Backend API: http://localhost:8000
echo    • API Documentation: http://localhost:8000/docs
echo    • Pathway Service: http://localhost:8765
echo.
echo 📊 To check service status:
echo    • Backend health: curl http://localhost:8000/health
echo    • View logs: type logs\*.log
echo.
echo 🛑 To stop all services:
echo    • Close this window or press Ctrl+C
echo    • Or run: taskkill /FI "WINDOWTITLE eq FinanceAI*"
echo.
echo 📝 Services are running in the background.
pause