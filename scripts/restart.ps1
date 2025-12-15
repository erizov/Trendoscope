# Trendoscope2 Restart Script
Write-Host "Restarting Trendoscope2..." -ForegroundColor Yellow

# Stop
& "$PSScriptRoot\stop.ps1"

Start-Sleep -Seconds 2

# Start
& "$PSScriptRoot\start.ps1"

