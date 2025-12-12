@echo off
chcp 65001 >nul
setlocal

echo ============================================================
echo   TRENDOSCOPE - Restarting Application
echo ============================================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo Step 1: Stopping existing instance...
call stop.bat /nopause

echo.
echo Step 2: Waiting 3 seconds before restart...
timeout /t 3 /nobreak >nul

echo.
echo Step 3: Starting application...
REM Start in new window to avoid blocking
start "Trendoscope" cmd /c "cd /d %~dp0 && python run.py"

echo.
echo [SUCCESS] Application restart initiated
echo Check the new window for server status
echo.
timeout /t 2 /nobreak >nul

