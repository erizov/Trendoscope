# TTS Testing Script
# Автоматический запуск и тестирование TTS функциональности

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TTS Testing Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuration
$API_URL = "http://localhost:8004"
$API_TIMEOUT = 60

# Function to check if API is running
function Test-API {
    try {
        $response = Invoke-WebRequest -Uri "$API_URL/health" -TimeoutSec 5 -UseBasicParsing
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

# Function to wait for API
function Wait-ForAPI {
    Write-Host "Waiting for API to be ready..." -ForegroundColor Yellow
    $maxWait = 60
    $waited = 0
    
    while ($waited -lt $maxWait) {
        if (Test-API) {
            Write-Host "✓ API is ready!" -ForegroundColor Green
            return $true
        }
        Start-Sleep -Seconds 2
        $waited += 2
        Write-Host "  Waiting... ($waited/$maxWait seconds)" -ForegroundColor Gray
    }
    
    Write-Host "✗ API is not available after $maxWait seconds" -ForegroundColor Red
    return $false
}

# Step 1: Check if API is running
Write-Host "Step 1: Checking API..." -ForegroundColor Cyan
if (-not (Test-API)) {
    Write-Host "  API is not running." -ForegroundColor Yellow
    Write-Host ""
    
    # Ask user if they want to start API automatically
    $start = Read-Host "Start API automatically? (y/n)"
    if ($start -eq "y" -or $start -eq "Y") {
        Write-Host "  Starting API in background..." -ForegroundColor Gray
        
        # Check if run.py exists
        $API_SCRIPT = "run.py"
        if (-not (Test-Path $API_SCRIPT)) {
            Write-Host "  ✗ $API_SCRIPT not found!" -ForegroundColor Red
            Write-Host "  Please run API manually: python run.py" -ForegroundColor Yellow
            exit 1
        }
        
        # Start API in background
        $apiProcess = Start-Process python -ArgumentList $API_SCRIPT -PassThru -WindowStyle Hidden
        
        Write-Host "  Waiting for API to start..." -ForegroundColor Gray
        if (-not (Wait-ForAPI)) {
            Write-Host ""
            Write-Host "✗ API failed to start" -ForegroundColor Red
            Stop-Process -Id $apiProcess.Id -Force -ErrorAction SilentlyContinue
            Write-Host "  Start API manually: python run.py" -ForegroundColor Yellow
            exit 1
        }
        
        Write-Host "  ✓ API started (PID: $($apiProcess.Id))" -ForegroundColor Green
        Write-Host "  Note: API will continue running after tests" -ForegroundColor Gray
    } else {
        Write-Host "  Please run API manually: python run.py" -ForegroundColor Yellow
        Write-Host ""
        
        # Ask user if they want to wait
        $wait = Read-Host "Wait for API to start? (y/n)"
        if ($wait -eq "y" -or $wait -eq "Y") {
            if (-not (Wait-ForAPI)) {
                Write-Host ""
                Write-Host "✗ Cannot proceed without API" -ForegroundColor Red
                Write-Host "  Start API manually: python run.py" -ForegroundColor Yellow
                exit 1
            }
        } else {
            Write-Host "  Skipping API check. Make sure API is running!" -ForegroundColor Yellow
            exit 1
        }
    }
} else {
    Write-Host "  ✓ API is running" -ForegroundColor Green
}

Write-Host ""

# Step 2: Quick API Tests
Write-Host "Step 2: Quick API Tests..." -ForegroundColor Cyan

try {
    # Test 1: Generate TTS (Russian)
    Write-Host "  Test 1: Generate TTS (Russian)..." -ForegroundColor Gray
    $response = Invoke-RestMethod -Uri "$API_URL/api/tts/generate" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{"text": "Привет, это тест.", "language": "ru", "voice_gender": "female"}' `
        -ErrorAction Stop
    
    Write-Host "    ✓ TTS generated" -ForegroundColor Green
    Write-Host "      Audio ID: $($response.audio_id)" -ForegroundColor Gray
    Write-Host "      Language: $($response.language)" -ForegroundColor Gray
    Write-Host "      Provider: $($response.provider)" -ForegroundColor Gray
    
    $audioId = $response.audio_id
    
    # Test 2: Get audio file
    Write-Host "  Test 2: Get audio file..." -ForegroundColor Gray
    $audioResponse = Invoke-WebRequest -Uri "$API_URL/api/tts/audio/$audioId" `
        -OutFile "test_audio.mp3" `
        -ErrorAction Stop
    
    if (Test-Path "test_audio.mp3") {
        $fileSize = (Get-Item "test_audio.mp3").Length
        Write-Host "    ✓ Audio file downloaded ($([math]::Round($fileSize / 1KB, 2)) KB)" -ForegroundColor Green
    }
    
    # Test 3: Statistics
    Write-Host "  Test 3: Get statistics..." -ForegroundColor Gray
    $stats = Invoke-RestMethod -Uri "$API_URL/api/tts/stats" -ErrorAction Stop
    Write-Host "    ✓ Statistics retrieved" -ForegroundColor Green
    Write-Host "      Cache files: $($stats.cache_files)" -ForegroundColor Gray
    Write-Host "      Cache size: $([math]::Round($stats.cache_size_bytes / 1MB, 2)) MB" -ForegroundColor Gray
    
    Write-Host ""
    Write-Host "  ✓ All quick tests passed!" -ForegroundColor Green
    
} catch {
    Write-Host "  ✗ Quick tests failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

Write-Host ""

# Step 3: Run E2E Tests
Write-Host "Step 3: Running E2E Tests..." -ForegroundColor Cyan
Write-Host ""

# Check if pytest is available
try {
    $pytestVersion = python -m pytest --version 2>&1
    Write-Host "  Using: $pytestVersion" -ForegroundColor Gray
} catch {
    Write-Host "  ✗ pytest not found. Install with: pip install pytest pytest-asyncio" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Run pytest
$testFile = "tests/e2e/test_tts.py"
if (Test-Path $testFile) {
    Write-Host "  Running: pytest $testFile -v" -ForegroundColor Gray
    Write-Host ""
    
    python -m pytest $testFile -v --tb=short
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "  ✓ All E2E tests passed!" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "  ⚠ Some tests failed or were skipped" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ Test file not found: $testFile" -ForegroundColor Red
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Testing Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Cleanup
if (Test-Path "test_audio.mp3") {
    Write-Host "Test audio file saved: test_audio.mp3" -ForegroundColor Gray
    Write-Host "  Play it to verify audio quality" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Open browser: start http://localhost:8004" -ForegroundColor Gray
Write-Host "  2. Click '🔊 Читать вслух' on any news article" -ForegroundColor Gray
Write-Host "  3. Test avatar and audio playback" -ForegroundColor Gray
Write-Host ""
