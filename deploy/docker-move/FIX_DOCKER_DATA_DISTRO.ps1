# Script to help create or locate docker-desktop-data distribution
# Run as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Docker Desktop Data Distribution Fix" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check current state
Write-Host "Current WSL distributions:" -ForegroundColor Yellow
wsl --list --verbose
Write-Host ""

# Check if docker-desktop-data exists but might be hidden or in different location
Write-Host "Checking for docker-desktop-data in WSL registry..." -ForegroundColor Yellow

# Try to get more detailed WSL info
$WslListAll = wsl --list --all --verbose 2>&1
Write-Host $WslListAll
Write-Host ""

# Check Docker Desktop data locations
Write-Host "Checking Docker Desktop data locations..." -ForegroundColor Yellow

$PossibleDataPaths = @(
    "$env:LOCALAPPDATA\Docker\wsl\data",
    "$env:LOCALAPPDATA\Docker\wsl",
    "$env:ProgramData\DockerDesktop",
    "$env:USERPROFILE\.docker"
)

foreach ($Path in $PossibleDataPaths) {
    if (Test-Path $Path) {
        $Size = (Get-ChildItem $Path -Recurse -ErrorAction SilentlyContinue | 
                 Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
        $SizeGB = [math]::Round($Size / 1GB, 2)
        Write-Host "  Found: $Path ($SizeGB GB)" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SOLUTION ATTEMPTS:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Solution 1: Try to trigger docker-desktop-data creation
Write-Host "Solution 1: Force Docker Desktop to create docker-desktop-data" -ForegroundColor Yellow
Write-Host ""
Write-Host "Steps to try:" -ForegroundColor White
Write-Host "1. Quit Docker Desktop completely" -ForegroundColor White
Write-Host "2. Run: wsl --shutdown" -ForegroundColor White
Write-Host "3. Start Docker Desktop again" -ForegroundColor White
Write-Host "4. Wait 2-3 minutes for full initialization" -ForegroundColor White
Write-Host "5. Check: wsl --list --verbose" -ForegroundColor White
Write-Host ""

# Solution 2: Check Docker Desktop Resources > WSL Integration
Write-Host "Solution 2: Verify WSL Integration Settings" -ForegroundColor Yellow
Write-Host ""
Write-Host "In Docker Desktop:" -ForegroundColor White
Write-Host "1. Settings > Resources > WSL Integration" -ForegroundColor White
Write-Host "2. Enable integration with your default WSL distro" -ForegroundColor White
Write-Host "3. Enable integration for Ubuntu-20.04, Ubuntu-22.04, etc." -ForegroundColor White
Write-Host "4. Click Apply & Restart" -ForegroundColor White
Write-Host "5. Wait for full restart" -ForegroundColor White
Write-Host ""

# Solution 3: Check if we can manually create it
Write-Host "Solution 3: Check Docker Desktop version compatibility" -ForegroundColor Yellow
Write-Host ""
$DockerVersion = docker --version 2>&1
Write-Host "Docker version: $DockerVersion" -ForegroundColor Cyan
Write-Host ""
Write-Host "Note: Some Docker Desktop versions may store data differently." -ForegroundColor Yellow
Write-Host "If docker-desktop-data never appears, Docker may be using" -ForegroundColor Yellow
Write-Host "a different storage mechanism (e.g., VHDX file directly)." -ForegroundColor Yellow
Write-Host ""

# Solution 4: Alternative - find actual Docker data location
Write-Host "Solution 4: Locate actual Docker data storage" -ForegroundColor Yellow
Write-Host ""
Write-Host "Checking for Docker VHDX files..." -ForegroundColor White

$VhdxPaths = @(
    "$env:LOCALAPPDATA\Docker\wsl\data\ext4.vhdx",
    "$env:LOCALAPPDATA\Docker\wsl\distro\ext4.vhdx"
)

foreach ($VhdxPath in $VhdxPaths) {
    $ParentDir = Split-Path -Parent $VhdxPath
    if (Test-Path $ParentDir) {
        $VhdxFiles = Get-ChildItem -Path $ParentDir -Filter "*.vhdx" -Recurse -ErrorAction SilentlyContinue
        if ($VhdxFiles) {
            foreach ($File in $VhdxFiles) {
                $SizeGB = [math]::Round($File.Length / 1GB, 2)
                Write-Host "  Found VHDX: $($File.FullName) ($SizeGB GB)" -ForegroundColor Green
            }
        }
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "If docker-desktop-data still doesn't appear after trying" -ForegroundColor Yellow
Write-Host "Solutions 1-2, you may need to:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Reinstall Docker Desktop (keep data if prompted)" -ForegroundColor White
Write-Host "2. Or contact Docker support if this is a known issue" -ForegroundColor White
Write-Host "3. Or check Docker Desktop release notes for your version" -ForegroundColor White
Write-Host ""
