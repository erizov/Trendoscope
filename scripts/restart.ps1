# Navigate to the trendoscope2 directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$trendoscope2Dir = Split-Path -Parent $scriptDir
Set-Location $trendoscope2Dir

Write-Host "========================================"
Write-Host "Restarting Trendoscope2"
Write-Host "========================================"
Write-Host ""

Write-Host "Stopping services..."
& "$scriptDir\\stop.ps1"

Write-Host ""
Write-Host "Waiting 5 seconds..."
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "Starting services..."
& "$scriptDir\\start.ps1"

Write-Host ""
Write-Host "Trendoscope2 services restarted."

