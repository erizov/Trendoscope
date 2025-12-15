# Navigate to the trendoscope2 directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$trendoscope2Dir = Split-Path -Parent $scriptDir
Set-Location $trendoscope2Dir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Restarting Trendoscope2" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stop existing services
Write-Host "Stopping services..." -ForegroundColor Yellow
& "$scriptDir\stop.ps1"

# Give some time for containers to shut down
Write-Host ""
Write-Host "Waiting 5 seconds..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# Start services
Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow
& "$scriptDir\start.ps1"

Write-Host ""
Write-Host "✓ Trendoscope2 services restarted." -ForegroundColor Green
