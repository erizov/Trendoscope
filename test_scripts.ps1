# Test Script for Start/Stop/Restart Scripts
# Tests the scripts and verifies API functionality

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Testing Trendoscope Scripts" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Stop any running instances
Write-Host "[Test 1] Stopping any running instances..." -ForegroundColor Yellow
& "$scriptDir\stop.ps1"
Start-Sleep -Seconds 2

# Verify nothing is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8004/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
    Write-Host "  FAIL: API is still running!" -ForegroundColor Red
    exit 1
} catch {
    Write-Host "  PASS: API is stopped" -ForegroundColor Green
}

# Test 2: Start the application
Write-Host ""
Write-Host "[Test 2] Starting application..." -ForegroundColor Yellow
& "$scriptDir\start.ps1"
Start-Sleep -Seconds 8

# Test 3: Verify API is running
Write-Host ""
Write-Host "[Test 3] Verifying API health..." -ForegroundColor Yellow
$maxRetries = 15
$retryCount = 0
$apiReady = $false

while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8004/health" -TimeoutSec 3 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            $healthData = $response.Content | ConvertFrom-Json
            Write-Host "  PASS: API is running!" -ForegroundColor Green
            Write-Host "    Status: $($healthData.status)" -ForegroundColor Gray
            Write-Host "    Redis: $($healthData.redis)" -ForegroundColor Gray
            Write-Host "    Database: $($healthData.database)" -ForegroundColor Gray
            $apiReady = $true
            break
        }
    } catch {
        # Not ready yet
    }
    Start-Sleep -Seconds 1
    $retryCount++
}

if (-not $apiReady) {
    Write-Host "  FAIL: API did not start in time" -ForegroundColor Red
    exit 1
}

# Test 4: Test root endpoint
Write-Host ""
Write-Host "[Test 4] Testing root endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8004/" -TimeoutSec 3 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "  PASS: Root endpoint responding" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: Root endpoint returned $($response.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  FAIL: Root endpoint error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 5: Test restart
Write-Host ""
Write-Host "[Test 5] Testing restart..." -ForegroundColor Yellow
& "$scriptDir\restart.ps1"
Start-Sleep -Seconds 10

# Verify API is still running after restart
Write-Host ""
Write-Host "[Test 6] Verifying API after restart..." -ForegroundColor Yellow
$retryCount = 0
$apiReady = $false

while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8004/health" -TimeoutSec 3 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "  PASS: API is running after restart!" -ForegroundColor Green
            $apiReady = $true
            break
        }
    } catch {
        # Not ready yet
    }
    Start-Sleep -Seconds 1
    $retryCount++
}

if (-not $apiReady) {
    Write-Host "  FAIL: API did not restart properly" -ForegroundColor Red
    exit 1
}

# Test 7: Run pytest health tests
Write-Host ""
Write-Host "[Test 7] Running pytest health tests..." -ForegroundColor Yellow
Set-Location "$scriptDir\app"
$testResult = python -m pytest tests/integration/test_all_endpoints.py::TestHealthEndpoints -v --tb=short -q 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  PASS: All health tests passed" -ForegroundColor Green
} else {
    Write-Host "  FAIL: Health tests failed" -ForegroundColor Red
    Write-Host $testResult
    exit 1
}

# Cleanup
Write-Host ""
Write-Host "[Cleanup] Stopping application..." -ForegroundColor Yellow
Set-Location $scriptDir
& "$scriptDir\stop.ps1"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  All Tests Passed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
