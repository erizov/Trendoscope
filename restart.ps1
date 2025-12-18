# Trendoscope Restart Script
# Stops all services, waits, then starts them again

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Trendoscope - Restarting Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stop services
Write-Host "Stopping services..." -ForegroundColor Yellow
& "$scriptDir\stop.ps1"

Write-Host ""
Write-Host "Waiting 3 seconds for cleanup..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start services
Write-Host ""
Write-Host "Starting services..." -ForegroundColor Yellow
& "$scriptDir\start.ps1"

Write-Host ""
Write-Host "Restart complete!" -ForegroundColor Green
