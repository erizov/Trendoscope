# Script to check Docker Desktop WSL 2 configuration
# Run this to diagnose Docker Desktop setup

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker Desktop WSL 2 Diagnostic Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker Desktop version
Write-Host "1. Checking Docker Desktop version..." -ForegroundColor Yellow
$DockerVersion = docker --version 2>&1
if ($DockerVersion) {
    Write-Host "   Docker version: $DockerVersion" -ForegroundColor Green
} else {
    Write-Host "   Docker command not found" -ForegroundColor Red
}

# Check WSL distributions
Write-Host ""
Write-Host "2. Checking WSL distributions..." -ForegroundColor Yellow
$WslList = wsl --list --verbose 2>&1
Write-Host $WslList

$HasDocker = $WslList -match "docker-desktop"
$HasDockerData = $WslList -match "docker-desktop-data"

Write-Host ""
if ($HasDocker) {
    Write-Host "   ✓ docker-desktop found" -ForegroundColor Green
} else {
    Write-Host "   ✗ docker-desktop NOT found" -ForegroundColor Red
}

if ($HasDockerData) {
    Write-Host "   ✓ docker-desktop-data found" -ForegroundColor Green
} else {
    Write-Host "   ✗ docker-desktop-data NOT found" -ForegroundColor Red
}

# Check Docker Desktop process
Write-Host ""
Write-Host "3. Checking Docker Desktop process..." -ForegroundColor Yellow
$DockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
if ($DockerProcess) {
    Write-Host "   Docker Desktop is running (PID: $($DockerProcess.Id))" -ForegroundColor Green
} else {
    Write-Host "   Docker Desktop is NOT running" -ForegroundColor Yellow
}

# Check Docker context/info
Write-Host ""
Write-Host "4. Checking Docker system info..." -ForegroundColor Yellow
try {
    $DockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   Docker is responding" -ForegroundColor Green
        
        # Check for WSL in docker info
        if ($DockerInfo -match "WSL") {
            Write-Host "   WSL mentioned in docker info" -ForegroundColor Green
        }
        
        # Check for Operating System
        $OSLine = $DockerInfo | Select-String "Operating System"
        if ($OSLine) {
            Write-Host "   $OSLine" -ForegroundColor Cyan
        }
    } else {
        Write-Host "   Docker is not responding: $DockerInfo" -ForegroundColor Red
    }
} catch {
    Write-Host "   Could not get Docker info: $_" -ForegroundColor Red
}

# Check Docker Desktop settings file location
Write-Host ""
Write-Host "5. Checking Docker Desktop settings location..." -ForegroundColor Yellow
$SettingsPath = "$env:APPDATA\Docker\settings.json"
if (Test-Path $SettingsPath) {
    Write-Host "   Settings file found: $SettingsPath" -ForegroundColor Green
    try {
        $Settings = Get-Content $SettingsPath | ConvertFrom-Json
        if ($Settings.wslEngineEnabled) {
            Write-Host "   wslEngineEnabled: $($Settings.wslEngineEnabled)" -ForegroundColor Green
        } else {
            Write-Host "   wslEngineEnabled: Not set (may default to true)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   Could not read settings file" -ForegroundColor Red
    }
} else {
    Write-Host "   Settings file not found at: $SettingsPath" -ForegroundColor Yellow
}

# Check WSL version
Write-Host ""
Write-Host "6. Checking WSL version..." -ForegroundColor Yellow
$WslVersion = wsl --version 2>&1
if ($WslVersion) {
    Write-Host $WslVersion
} else {
    Write-Host "   Could not get WSL version" -ForegroundColor Yellow
}

# Recommendations
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RECOMMENDATIONS:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if (-not $HasDockerData) {
    Write-Host ""
    Write-Host "docker-desktop-data is missing. Try these steps:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1. Make sure Docker Desktop is fully started" -ForegroundColor White
    Write-Host "2. In Docker Desktop Settings, check:" -ForegroundColor White
    Write-Host "   - Resources > WSL Integration" -ForegroundColor White
    Write-Host "   - Make sure 'Enable integration with my default WSL distro' is checked" -ForegroundColor White
    Write-Host "3. Try restarting Docker Desktop completely:" -ForegroundColor White
    Write-Host "   - Right-click system tray icon > Quit Docker Desktop" -ForegroundColor White
    Write-Host "   - Wait 10 seconds" -ForegroundColor White
    Write-Host "   - Start Docker Desktop again" -ForegroundColor White
    Write-Host "   - Wait for full initialization (1-2 minutes)" -ForegroundColor White
    Write-Host "4. Check again: wsl --list --verbose" -ForegroundColor White
}

Write-Host ""
