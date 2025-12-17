# Navigate to the trendoscope2 directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$trendoscope2Dir = Split-Path -Parent $scriptDir
Set-Location $trendoscope2Dir

Write-Host "========================================"
Write-Host "Starting Trendoscope2"
Write-Host "========================================"
Write-Host ""

# Check if Docker is available
$dockerAvailable = $false
try {
    docker info *> $null
    if ($LASTEXITCODE -eq 0) {
        $dockerAvailable = $true
    }
} catch {
    $dockerAvailable = $false
}

if ($dockerAvailable) {
    Write-Host "Starting Redis container for Trendoscope2..."
    docker-compose -f docker/docker-compose.local.yml up -d redis *> $null

    Write-Host "Waiting for Redis to be healthy..."
    $maxRetries = 30
    $retryCount = 0
    $redisHealthy = $false

    while ($retryCount -lt $maxRetries) {
        try {
            $status = docker inspect --format="{{.State.Health.Status}}" trendoscope2_redis 2>$null
            if ($status -eq "healthy") {
                Write-Host "Redis is healthy."
                $redisHealthy = $true
                break
            } else {
                Write-Host "Redis status: $status (Attempt $($retryCount+1)/$maxRetries)"
            }
        } catch {
            Write-Host "Redis container not found yet..."
        }
        Start-Sleep -Seconds 2
        $retryCount++
    }

    if (-not $redisHealthy) {
        Write-Host "Warning: Redis did not become healthy in time. Continuing without Redis..."
    }
} else {
    Write-Host "Docker not available. Running without Redis (degraded mode)."
}

Write-Host ""
Write-Host "Starting Trendoscope2 FastAPI application..."
Write-Host "API: http://localhost:8004"
Write-Host "Frontend: http://localhost:8004"
Write-Host "Docs: http://localhost:8004/docs"
Write-Host ""

$pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonPath) { $pythonPath = "python" }

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-Command",
    "cd '$trendoscope2Dir'; `$env:PYTHONPATH='.'; $pythonPath run.py"
)

Write-Host "Trendoscope2 API is starting in a new window."
Write-Host "Check the new PowerShell window for logs."
Write-Host ""
Write-Host "To stop: .\\scripts\\stop.ps1"
Write-Host "To restart: .\\scripts\\restart.ps1"

