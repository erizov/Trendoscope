# Navigate to the trendoscope2 directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$trendoscope2Dir = Split-Path -Parent $scriptDir
Set-Location $trendoscope2Dir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Trendoscope2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is available
$dockerAvailable = $false
try {
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerAvailable = $true
    }
} catch {
    $dockerAvailable = $false
}

if ($dockerAvailable) {
    Write-Host "Starting Redis container for Trendoscope2..." -ForegroundColor Yellow
    docker-compose -f docker/docker-compose.local.yml up -d redis 2>&1 | Out-Null
    
    # Wait for Redis to be healthy
    Write-Host "Waiting for Redis to be healthy..." -ForegroundColor Yellow
    $maxRetries = 30
    $retryCount = 0
    $redisHealthy = $false
    
    do {
        try {
            $status = docker inspect --format='{{.State.Health.Status}}' trendoscope2_redis 2>$null
            if ($status -eq 'healthy') {
                Write-Host "✓ Redis is healthy." -ForegroundColor Green
                $redisHealthy = $true
                break
            }
            Write-Host "Redis status: $($status -replace '\s+', '') (Attempt $($retryCount+1)/$maxRetries)" -ForegroundColor Gray
        } catch {
            Write-Host "Redis container not found, starting..." -ForegroundColor Yellow
        }
        Start-Sleep -Seconds 2
        $retryCount++
    } while ($retryCount -lt $maxRetries)
    
    if (-not $redisHealthy) {
        Write-Host "⚠ Warning: Redis did not become healthy in time. Continuing without Redis..." -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ Docker not available. Running without Redis (degraded mode)." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Starting Trendoscope2 FastAPI application..." -ForegroundColor Yellow
Write-Host "API will be available at: http://localhost:8004" -ForegroundColor Cyan
Write-Host "Frontend will be available at: http://localhost:8004" -ForegroundColor Cyan
Write-Host "API docs: http://localhost:8004/docs" -ForegroundColor Cyan
Write-Host ""

# Start the FastAPI app in a new terminal window
$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    $pythonPath = "python"
}

Start-Process powershell -ArgumentList "-NoExit -Command `"cd '$trendoscope2Dir'; `$env:PYTHONPATH='.'; python run.py`""

Write-Host "✓ Trendoscope2 API is starting in a new window." -ForegroundColor Green
Write-Host "  Check the new PowerShell window for logs." -ForegroundColor Gray
Write-Host ""
Write-Host "To stop: .\scripts\stop.ps1" -ForegroundColor Gray
Write-Host "To restart: .\scripts\restart.ps1" -ForegroundColor Gray
