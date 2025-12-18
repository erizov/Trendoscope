# Quick API Check Script
# Быстрая проверка состояния API

$API_URL = "http://localhost:8004"

Write-Host "Checking API at $API_URL..." -ForegroundColor Cyan
Write-Host ""

# Check health endpoint
try {
    $response = Invoke-WebRequest -Uri "$API_URL/health" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ API is running!" -ForegroundColor Green
        Write-Host "  Status: $($response.StatusCode)" -ForegroundColor Gray
        exit 0
    }
} catch {
    Write-Host "✗ API is not responding" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Start API with:" -ForegroundColor Cyan
    Write-Host "  python run.py" -ForegroundColor Gray
    exit 1
}
