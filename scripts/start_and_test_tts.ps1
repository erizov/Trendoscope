# Start API and Run TTS Tests
# Запускает API в фоне и запускает тесты

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Start API and Test TTS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$API_URL = "http://localhost:8004"
$API_SCRIPT = "run_test.py"  # Use test script without reload
if (-not (Test-Path $API_SCRIPT)) {
    $API_SCRIPT = "run.py"  # Fallback to regular script
}

# Check if API is already running
function Test-API {
    try {
        $response = Invoke-WebRequest -Uri "$API_URL/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Step 1: Check if API is running
Write-Host "Step 1: Checking if API is running..." -ForegroundColor Cyan
if (Test-API) {
    Write-Host "  ✓ API is already running" -ForegroundColor Green
    $apiRunning = $true
} else {
    Write-Host "  API is not running. Starting..." -ForegroundColor Yellow
    
    # Check if run.py exists
    if (-not (Test-Path $API_SCRIPT)) {
        Write-Host "  ✗ $API_SCRIPT not found!" -ForegroundColor Red
        exit 1
    }
    
    # Start API in background
    Write-Host "  Starting API in background..." -ForegroundColor Gray
    
    # Create log file for API output
    $logFile = "api_startup.log"
    $logPath = Join-Path $PWD $logFile
    
    # Start API process with output redirection
    $apiProcess = Start-Process python -ArgumentList $API_SCRIPT `
        -PassThru `
        -WindowStyle Hidden `
        -RedirectStandardOutput $logPath `
        -RedirectStandardError $logPath
    
    Write-Host "  API process started (PID: $($apiProcess.Id))" -ForegroundColor Gray
    Write-Host "  Log file: $logPath" -ForegroundColor Gray
    Write-Host "  Waiting for API to start..." -ForegroundColor Gray
    
    $maxWait = 60
    $waited = 0
    $apiRunning = $false
    
    while ($waited -lt $maxWait) {
        Start-Sleep -Seconds 2
        $waited += 2
        
        # Check if process is still running
        try {
            $proc = Get-Process -Id $apiProcess.Id -ErrorAction Stop
        } catch {
            Write-Host "  ✗ API process died unexpectedly!" -ForegroundColor Red
            if (Test-Path $logPath) {
                Write-Host "  Last log entries:" -ForegroundColor Yellow
                Get-Content $logPath -Tail 10 | ForEach-Object {
                    Write-Host "    $_" -ForegroundColor Gray
                }
            }
            exit 1
        }
        
        if (Test-API) {
            Write-Host "  ✓ API started successfully!" -ForegroundColor Green
            $apiRunning = $true
            break
        }
        
        Write-Host "    Waiting... ($waited/$maxWait seconds)" -ForegroundColor Gray
    }
    
    if (-not $apiRunning) {
        Write-Host "  ✗ API failed to start after $maxWait seconds" -ForegroundColor Red
        Write-Host "  Checking process status..." -ForegroundColor Yellow
        
        try {
            $proc = Get-Process -Id $apiProcess.Id -ErrorAction Stop
            Write-Host "  Process is running but API not responding" -ForegroundColor Yellow
            if (Test-Path $logPath) {
                Write-Host "  Last log entries:" -ForegroundColor Yellow
                Get-Content $logPath -Tail 15 | ForEach-Object {
                    Write-Host "    $_" -ForegroundColor Gray
                }
            }
        } catch {
            Write-Host "  Process is not running" -ForegroundColor Yellow
            if (Test-Path $logPath) {
                Write-Host "  Error log:" -ForegroundColor Yellow
                Get-Content $logPath -Tail 20 | ForEach-Object {
                    Write-Host "    $_" -ForegroundColor Gray
                }
            }
        }
        
        Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host ""
        Write-Host "  Try running manually to see errors:" -ForegroundColor Yellow
        Write-Host "    python run.py" -ForegroundColor Gray
        exit 1
    }
}

Write-Host ""

# Step 2: Run tests
Write-Host "Step 2: Running TTS tests..." -ForegroundColor Cyan
Write-Host ""

# Run the test script
$testScript = Join-Path $PSScriptRoot "test_tts.ps1"
if (Test-Path $testScript) {
    & $testScript
} else {
    # Fallback: run pytest directly
    Write-Host "  Running pytest directly..." -ForegroundColor Gray
    python -m pytest tests/e2e/test_tts.py -v --tb=short
}

Write-Host ""

# Step 3: Cleanup (optional)
if ($apiProcess) {
    Write-Host "Step 3: Cleanup..." -ForegroundColor Cyan
    $keepRunning = Read-Host "Keep API running? (y/n)"
    if ($keepRunning -ne "y" -and $keepRunning -ne "Y") {
        Write-Host "  Stopping API..." -ForegroundColor Gray
        Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ API stopped" -ForegroundColor Green
    } else {
        Write-Host "  API is still running (PID: $($apiProcess.Id))" -ForegroundColor Gray
        Write-Host "  Stop manually if needed" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Done!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
