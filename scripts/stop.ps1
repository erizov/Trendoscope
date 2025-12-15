# Trendoscope2 Stop Script
Write-Host "Stopping Trendoscope2..." -ForegroundColor Yellow

# Stop Redis container
Write-Host "Stopping Redis container..." -ForegroundColor Cyan
Set-Location "$PSScriptRoot\.."
docker-compose -f docker/docker-compose.local.yml stop redis

Write-Host "Trendoscope2 stopped." -ForegroundColor Green

