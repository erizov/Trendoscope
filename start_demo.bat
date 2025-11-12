@echo off
chcp 65001 >nul
echo ============================================================
echo   TRENDOSCOPE - Terminal Demo
echo ============================================================
echo.

echo Checking dependencies...
pip show numpy >nul 2>&1
if errorlevel 1 (
    echo Installing minimal dependencies...
    pip install numpy sentence-transformers --quiet
    echo Done!
) else (
    echo Dependencies OK
)

echo.
echo Running demo with sample posts...
echo This will show executive summaries in the terminal.
echo ============================================================
echo.

python demo.py

echo.
echo ============================================================
echo Demo completed! Check demo_results.json for full output.
echo ============================================================
echo.
pause

