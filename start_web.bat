@echo off
chcp 65001 >nul
echo ============================================================
echo   TRENDOSCOPE - Web UI Launcher
echo ============================================================
echo.

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
echo Starting Trendoscope Web UI...
echo.
echo Browser will open to: http://localhost:8001
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python run.py

pause

