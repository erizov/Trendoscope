# Trendoscope2 Start Script
Write-Host "Starting Trendoscope2..." -ForegroundColor Green

# Check if Docker is running
$dockerRunning = docker info 2>$null
if (-not $dockerRunning) {
    Write-Host "Docker is not running. Starting Docker Desktop..." -ForegroundColor Yellow
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    Start-Sleep -Seconds 10
}

# Start Redis
Write-Host "Starting Redis container..." -ForegroundColor Cyan
Set-Location "$PSScriptRoot\.."
docker-compose -f docker/docker-compose.local.yml up -d redis

# Wait for Redis to be ready
Write-Host "Waiting for Redis to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 3

# Check Redis health
$redisHealth = docker exec trendoscope2-redis redis-cli ping 2>$null
if ($redisHealth -eq "PONG") {
    Write-Host "Redis is ready!" -ForegroundColor Green
} else {
    Write-Host "Warning: Redis may not be ready yet" -ForegroundColor Yellow
}

# Start FastAPI app
Write-Host "Starting FastAPI application..." -ForegroundColor Cyan
Set-Location "$PSScriptRoot\.."
python run.py

