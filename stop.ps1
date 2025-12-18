# Trendoscope Stop Script
# Stops all application processes and services

$ErrorActionPreference = "Continue"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$appDir = Join-Path $scriptDir "app"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Trendoscope - Stopping Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Find and kill processes on port 8004
Write-Host "[1/3] Stopping processes on port 8004..." -ForegroundColor Yellow
$killed = $false

try {
    $connections = Get-NetTCPConnection -LocalPort 8004 -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        $pid = $conn.OwningProcess
        try {
            $proc = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "  Stopping process $pid ($($proc.ProcessName))" -ForegroundColor Gray
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                $killed = $true
            }
        } catch {
            # Process already gone
        }
    }
} catch {
    # No connections found
}

# Step 2: Kill Python processes running run.py or uvicorn
Write-Host "[2/3] Stopping Python application processes..." -ForegroundColor Yellow
try {
    $allPython = Get-Process python -ErrorAction SilentlyContinue
    foreach ($proc in $allPython) {
        try {
            $cmdLine = (Get-CimInstance Win32_Process -Filter "ProcessId = $($proc.Id)").CommandLine
            if ($cmdLine -and (
                $cmdLine -like "*run.py*" -or 
                $cmdLine -like "*uvicorn*" -or
                $cmdLine -like "*trendoscope*" -or
                $cmdLine -like "*app.api.main*" -or
                ($cmdLine -like "*app*" -and $cmdLine -like "*8004*")
            )) {
                Write-Host "  Stopping process $($proc.Id) (Trendoscope)" -ForegroundColor Gray
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                $killed = $true
            }
        } catch {
            # Can't get command line, try killing if working directory matches
            try {
                $procPath = $proc.Path
                if ($procPath -and ($procPath -like "*Trendoscope*" -or $procPath -like "*app*")) {
                    Write-Host "  Stopping process $($proc.Id) (possible Trendoscope)" -ForegroundColor Gray
                    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
                    $killed = $true
                }
            } catch {
                # Skip this process
            }
        }
    }
} catch {
    # No processes found
}

if (-not $killed) {
    Write-Host "  No running processes found" -ForegroundColor Gray
} else {
    Start-Sleep -Seconds 1
}

# Step 3: Stop Redis container if Docker is available
Write-Host "[3/3] Stopping Redis container (if running)..." -ForegroundColor Yellow
try {
    docker info *> $null 2>&1
    if ($LASTEXITCODE -eq 0) {
        $dockerComposeFile = Join-Path $appDir "docker\docker-compose.local.yml"
        if (Test-Path $dockerComposeFile) {
            docker-compose -f $dockerComposeFile down *> $null 2>&1
            Write-Host "  Redis container stopped" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "  Docker not available or Redis not running" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor G