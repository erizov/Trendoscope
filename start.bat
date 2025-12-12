@echo off
chcp 65001 >nul
setlocal

echo ============================================================
echo   TRENDOSCOPE - Starting Application
echo ============================================================
echo.

REM Check if already running
netstat -ano | findstr ":8003" >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Application appears to be already running on port 8003
    echo Use stop.bat to stop it first, or restart.bat to restart
    echo.
    pause
    exit /b 1
)

REM Change to script directory
cd /d "%~dp0"

echo Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing minimal dependencies...
    pip install fastapi uvicorn numpy sentence-transformers --quiet
    echo Done!
) else (
    echo Dependencies OK
)

echo.
echo Starting Trendoscope...
echo.
echo API will be available at:
echo   http://localhost:8003
echo.
echo API Documentation:
echo   http://localhost:8003/docs
echo.
echo Web UI:
echo   http://localhost:8003
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

REM Start the application
python run.py

pause

