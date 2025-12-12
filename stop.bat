@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ============================================================
echo   TRENDOSCOPE - Stopping Application
echo ============================================================
echo.

set FOUND=0

REM Find process using port 8003
echo Checking for process on port 8003...
for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8003" ^| findstr "LISTENING"') do (
    set PID=%%a
    set FOUND=1
    goto :found
)

REM Alternative: find Python process running run.py
if !FOUND! equ 0 (
    echo Checking for Python process running run.py...
    for /f "tokens=2" %%a in ('wmic process where "name='python.exe' and commandline like '%%run.py%%'" get processid /format:value 2^>nul ^| findstr "ProcessId"') do (
        set PID=%%a
        set FOUND=1
        goto :found
    )
)

if !FOUND! equ 0 (
    echo [INFO] No running Trendoscope process found.
    echo.
    if "%1" neq "/nopause" pause
    exit /b 0
)

:found
if !FOUND! equ 1 (
    echo Found process with PID: !PID!
    echo Attempting to stop process...
    taskkill /PID !PID! /F >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to stop process !PID!
        echo You may need to run this script as Administrator
    ) else (
        echo [SUCCESS] Process !PID! stopped successfully
        timeout /t 2 >nul
        REM Verify it's stopped
        netstat -ano 2>nul | findstr ":8003" >nul 2>&1
        if errorlevel 1 (
            echo [SUCCESS] Port 8003 is now free
        ) else (
            echo [WARNING] Port 8003 may still be in use
        )
    )
) else (
    echo [INFO] No process found to stop
)

echo.
if "%1" neq "/nopause" pause

