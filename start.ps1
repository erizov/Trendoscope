# Trendoscope Start Script
# Starts the application and all required services

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$appDir = Join-Path $scriptDir "app"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Trendoscope - Starting Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Kill all existing processes
Write-Host "[1/5] Stopping existing processes..." -ForegroundColor Yellow
& "$scriptDir\scripts\stop.ps1" 2>$null
Start-Sleep -Seconds 2

# Kill any remaining Python processes on port 8004
Write-Host "[2/5] Checking for processes on port 8004..." -ForegroundColor Yellow
try {
    $processes = Get-NetTCPConnection -LocalPort 8004 -ErrorAction SilentlyContinue | 
        Select-Object -ExpandProperty OwningProcess -Unique
    
    foreach ($pid in $processes) {
        try {
            $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($proc -and $proc.ProcessName -like "*python*") {
                Write-Host "  Killing process $pid ($($proc.ProcessName))" -ForegroundColor Gray
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            }
        } catch {
            # Process already gone
        }
    }
    Start-Sleep -Seconds 1
} catch {
    Write-Host "  No processes found on port 8004" -ForegroundColor Gray
}

# Step 2: Start Redis if Docker is available
Write-Host "[3/5] Starting Redis (if available)..." -ForegroundColor Yellow
$dockerAvailable = $false
try {
    docker info *> $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerAvailable = $true
        $dockerComposeFile = Join-Path $appDir "docker\docker-compose.local.yml"
        if (Test-Path $dockerComposeFile) {
            docker-compose -f $dockerComposeFile up -d redis *> $null 2>&1
            Write-Host "  Redis container started" -ForegroundColor Green
            
            # Wait for Redis to be ready
            $maxRetries = 15
            $retryCount = 0
            $redisReady = $false
            
            while ($retryCount -lt $maxRetries) {
                try {
                    $status = docker inspect --format="{{.State.Health.Status}}" trendoscope-redis 2>$null
                    if ($status -eq "healthy" -or $status -eq "running") {
                        $redisReady = $true
                        break
                    }
                } catch {
                    # Container might not have health check
                    try {
                        docker exec trendoscope-redis redis-cli ping *> $null 2>&1
                        if ($LASTEXITCODE -eq 0) {
                            $redisReady = $true
                            break
                        }
                    } catch {
                        # Not ready yet
                    }
                }
                Start-Sleep -Seconds 1
                $retryCount++
            }
            
            if ($redisReady) {
                Write-Host "  Redis is ready" -ForegroundColor Green
            } else {
                Write-Host "  Redis not ready, continuing anyway" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  Docker Compose file not found, skipping Redis" -ForegroundColor Yellow
        }
    }
} catch {
    Write-Host "  Docker not available, using in-memory cache" -ForegroundColor Yellow
}

# Step 3: Start the FastAPI application
Write-Host "[4/5] Starting FastAPI application..." -ForegroundColor Yellow
Set-Location $appDir

$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) {
    $pythonPath = (Get-Command python3 -ErrorAction SilentlyContinue).Source
}
if (-not $pythonPath) {
    Write-Host "  ERROR: Python not found!" -ForegroundColor Red
    exit 1
}

# Create log directory
$logDir = Join-Path $appDir "logs"
if (-not (Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

# Start the application in background
$logFile = Join-Path $logDir "app_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
Write-Host "  Log file: $logFile" -ForegroundColor Gray
Write-Host "  Starting on http://localhost:8004" -ForegroundColor Gray

$process = Start-Process -FilePath $pythonPath -ArgumentList "run.py" -WorkingDirectory $appDir -PassThru -NoNewWindow -RedirectStandardOutput $logFile -RedirectStandardError $logFile

# Wait a bit for the server to start
Start-Sleep -Seconds 3

# Step 4: Verify the application is running
Write-Host "[5/5] Verifying application health..." -ForegroundColor Yellow
$maxRetries = 10
$retryCount = 0
$apiReady = $false

while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8004/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $apiReady = $true
            $healthData = $response.Content | ConvertFrom-Json
            Write-Host "  API is running!" -ForegroundColor Green
            Write-Host "  Status: $($healthData.status)" -ForegroundColor Gray
            Write-Host "  Redis: $($healthData.redis)" -ForegroundColor Gray
            Write-Host "  Database: $($healthData.database)" -ForegroundColor Gray
            break
        }
    } catch {
        # Not ready yet
    }
    Start-Sleep -Seconds 1
    $retryCount++
}

if (-not $apiReady) {
    Write-Host "  WARNING: API did not respond in time" -ForegroundColor Yellow
    Write-Host "  Check logs: $logFile" -ForegroundColor Yellow
    Write-Host "  Process ID: $($process.Id)" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Trendoscope is running!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  API:      http://localhost:8004" -ForegroundColor Cyan
    Write-Host "  Docs:     http://localhost:8004/docs" -ForegroundColor Cyan
    Write-Host "  Health:   http://localhost:8004/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  Process ID: $($process.Id)" -ForegroundColor Gray
    Write-Host "  Log file:   $logFile" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To stop:   .\stop.ps1" -ForegroundColor Yellow
    Write-Host "To restart: .\restart.ps1" -ForegroundColor Yellow
    Write-Host ""
}

Set-Location $scriptDir
