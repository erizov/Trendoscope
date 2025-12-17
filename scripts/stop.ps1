# Navigate to the trendoscope2 directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$trendoscope2Dir = Split-Path -Parent $scriptDir
Set-Location $trendoscope2Dir

Write-Host "========================================"
Write-Host "Stopping Trendoscope2"
Write-Host "========================================"
Write-Host ""

# Stop Redis if Docker is available
$dockerAvailable = $false
try {
    docker info *> $null
    if ($LASTEXITCODE -eq 0) { $dockerAvailable = $true }
} catch {
    $dockerAvailable = $false
}

if ($dockerAvailable) {
    Write-Host "Stopping Redis container..."
    docker-compose -f docker/docker-compose.local.yml down *> $null
    Write-Host "Redis container stopped."
} else {
    Write-Host "Docker not available, skipping Redis stop."
}

Write-Host ""
Write-Host "Note: Stop the FastAPI window manually (Ctrl+C or close window)."
Write-Host "Stop script completed."

