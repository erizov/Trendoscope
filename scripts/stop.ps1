# Navigate to the trendoscope2 directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$trendoscope2Dir = Split-Path -Parent $scriptDir
Set-Location $trendoscope2Dir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stopping Trendoscope2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stop Redis if Docker is available
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
    Write-Host "Stopping Redis container..." -ForegroundColor Yellow
    docker-compose -f docker/docker-compose.local.yml down 2>&1 | Out-Null
    Write-Host "✓ Redis container stopped." -ForegroundColor Green
} else {
    Write-Host "⚠ Docker not available, skipping Redis stop." -ForegroundColor Yellow
}

# Note: FastAPI process must be stopped manually (Ctrl+C in the window)
Write-Host ""
Write-Host "⚠ Note: FastAPI process must be stopped manually." -ForegroundColor Yellow
Write-Host "  Press Ctrl+C in the FastAPI window, or close it." -ForegroundColor Gray
Write-Host ""
Write-Host "✓ Stop script completed." -ForegroundColor Green
