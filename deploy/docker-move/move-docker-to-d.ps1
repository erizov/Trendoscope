# PowerShell script to move Docker Desktop data from C:\Docker to E:\Docker
# Run as Administrator

param(
    [string]$SourcePath = "C:\Docker",
    [string]$DestPath = "E:\Docker",
    [switch]$SkipBackup = $false
)

$ErrorActionPreference = "Stop"
$LogFile = "E:\Docker\move-docker-log-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"

# Function to write log messages
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage -ErrorAction SilentlyContinue
}

# Function to check if running as Administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Start logging
Write-Log "================================================" "INFO"
Write-Log "Docker Move Script Started" "INFO"
Write-Log "Source: $SourcePath" "INFO"
Write-Log "Destination: $DestPath" "INFO"
Write-Log "================================================" "INFO"

# Check if running as Administrator
if (-not (Test-Administrator)) {
    Write-Log "ERROR: This script must be run as Administrator!" "ERROR"
    Write-Log "Right-click PowerShell and select 'Run as Administrator'" "ERROR"
    exit 1
}

# Create log directory if it doesn't exist (before any logging)
$LogDir = Split-Path -Path $LogFile -Parent
if (-not (Test-Path $LogDir)) {
    try {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
        Write-Log "Created log directory: $LogDir" "INFO"
    } catch {
        Write-Host "WARNING: Could not create log directory: $LogDir" -ForegroundColor Yellow
        Write-Host "Logging to console only" -ForegroundColor Yellow
    }
}

try {
    # Pre-flight checks
    Write-Log "Pre-flight checks..." "INFO"
    
    # Check if WSL is available
    $WslAvailable = Get-Command wsl -ErrorAction SilentlyContinue
    if (-not $WslAvailable) {
        Write-Log "ERROR: WSL command not found. WSL must be installed." "ERROR"
        Write-Log "Install WSL: wsl --install" "ERROR"
        throw "WSL not available"
    }
    Write-Log "WSL command found" "INFO"
    
    # Check if Docker Desktop is installed (check for docker-desktop process or WSL distro)
    Write-Log "Checking Docker Desktop installation..." "INFO"
    
    # Step 1: Check if Docker Desktop is running
    Write-Log "Step 1: Checking Docker Desktop status..." "INFO"
    $DockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
    if ($DockerProcess) {
        Write-Log "WARNING: Docker Desktop is running. Attempting to stop..." "WARN"
        Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 5
        Write-Log "Docker Desktop stopped" "INFO"
    } else {
        Write-Log "Docker Desktop is not running" "INFO"
    }

    # Step 2: Shut down WSL
    Write-Log "Step 2: Shutting down WSL instances..." "INFO"
    wsl --shutdown 2>&1 | Out-Null
    Start-Sleep -Seconds 3
    Write-Log "WSL shutdown complete" "INFO"

    # Step 3: List WSL distributions
    Write-Log "Step 3: Checking WSL distributions..." "INFO"
    $WslList = wsl --list --verbose 2>&1
    Write-Log "WSL Distributions:" "INFO"
    Write-Log $WslList "INFO"

    $HasDockerData = $WslList -match "docker-desktop-data"
    $HasDocker = $WslList -match "docker-desktop"

    if (-not $HasDockerData) {
        Write-Log "WARNING: docker-desktop-data distribution not found in WSL list" "WARN"
        Write-Log "This usually means Docker Desktop hasn't fully initialized yet" "WARN"
        Write-Log "" "WARN"
        Write-Log "DIAGNOSTIC INFORMATION:" "INFO"
        Write-Log "Found docker-desktop: $HasDocker" "INFO"
        Write-Log "Found docker-desktop-data: $HasDockerData" "INFO"
        Write-Log "" "INFO"
        Write-Log "SOLUTION STEPS:" "INFO"
        Write-Log "Since WSL 2 is already enabled, try these steps:" "INFO"
        Write-Log "" "INFO"
        Write-Log "1. In Docker Desktop Settings > Resources > WSL Integration:" "INFO"
        Write-Log "   - Enable integration with your default WSL distro" "INFO"
        Write-Log "   - Enable integration for Ubuntu-20.04, Ubuntu-22.04, etc." "INFO"
        Write-Log "   - Click 'Apply & Restart'" "INFO"
        Write-Log "" "INFO"
        Write-Log "2. Fully restart Docker Desktop:" "INFO"
        Write-Log "   - Right-click system tray icon > Quit Docker Desktop" "INFO"
        Write-Log "   - Wait 15 seconds" "INFO"
        Write-Log "   - Start Docker Desktop again" "INFO"
        Write-Log "   - Wait 2-3 minutes for full initialization" "INFO"
        Write-Log "" "INFO"
        Write-Log "3. Update WSL and restart:" "INFO"
        Write-Log "   - Run: wsl --update" "INFO"
        Write-Log "   - Restart Docker Desktop" "INFO"
        Write-Log "" "INFO"
        Write-Log "4. Verify with: wsl --list --verbose" "INFO"
        Write-Log "   Should show both docker-desktop and docker-desktop-data" "INFO"
        Write-Log "" "INFO"
        Write-Host "NOTE: Some Docker Desktop versions may not create docker-desktop-data" -ForegroundColor Yellow
        Write-Host "automatically. If it still doesn't appear, you may need to" -ForegroundColor Yellow
        Write-Host "reinstall Docker Desktop or check Docker Desktop release notes." -ForegroundColor Yellow
        Write-Log "" "INFO"
        throw "docker-desktop-data distribution not found. Please initialize Docker Desktop with WSL 2 backend first."
    }
    
    if ($HasDockerData) {
        Write-Log "Found docker-desktop-data distribution" "INFO"
    } else {
        Write-Log "WARNING: Proceeding without docker-desktop-data in WSL list" "WARN"
        Write-Log "The script will attempt to work with docker-desktop only" "WARN"
    }

    # Step 4: Create destination directory
    Write-Log "Step 4: Creating destination directory..." "INFO"
    if (-not (Test-Path $DestPath)) {
        New-Item -ItemType Directory -Path $DestPath -Force | Out-Null
        Write-Log "Created directory: $DestPath" "INFO"
    } else {
        Write-Log "Destination directory already exists: $DestPath" "INFO"
    }

    # Step 5: Check disk space
    Write-Log "Step 5: Checking disk space..." "INFO"
    $DestDrive = (Split-Path -Qualifier $DestPath).TrimEnd(':')
    $DestDriveInfo = Get-PSDrive -Name $DestDrive -ErrorAction SilentlyContinue
    if ($DestDriveInfo) {
        $FreeSpaceGB = [math]::Round($DestDriveInfo.Free / 1GB, 2)
        Write-Log "Free space on $DestDrive`: $FreeSpaceGB GB" "INFO"
        if ($FreeSpaceGB -lt 20) {
            Write-Log "WARNING: Less than 20GB free space on destination drive" "WARN"
        }
    }

    # Step 6: Export docker-desktop-data
    $ExportFile = Join-Path $DestPath "docker-desktop-data-export.tar"
    
    if ($HasDockerData) {
        Write-Log "Step 6: Exporting docker-desktop-data..." "INFO"
        
        Write-Log "Exporting to: $ExportFile" "INFO"
        Write-Log "This may take several minutes depending on data size..." "INFO"
        
        $ExportStart = Get-Date
        $ExportResult = wsl --export docker-desktop-data $ExportFile 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            $ExportDuration = (Get-Date) - $ExportStart
            Write-Log "Export completed successfully in $($ExportDuration.TotalMinutes) minutes" "INFO"
            
            # Check export file size
            if (Test-Path $ExportFile) {
                $ExportSizeGB = [math]::Round((Get-Item $ExportFile).Length / 1GB, 2)
                Write-Log "Export file size: $ExportSizeGB GB" "INFO"
            }
        } else {
            Write-Log "ERROR: Export failed!" "ERROR"
            Write-Log $ExportResult "ERROR"
            throw "Export failed with exit code $LASTEXITCODE"
        }
    } else {
        Write-Log "Step 6: docker-desktop-data not found in WSL distributions" "WARN"
        Write-Log "This may mean Docker Desktop hasn't been fully initialized" "WARN"
        Write-Log "SOLUTION: Start Docker Desktop, ensure WSL 2 backend is enabled" "WARN"
        Write-Log "  Settings > General > Use WSL 2 based engine" "WARN"
        Write-Log "  Then restart Docker Desktop and run this script again" "WARN"
        throw "docker-desktop-data distribution not found. Please initialize Docker Desktop with WSL 2 backend first."
    }

    # Step 7: Unregister docker-desktop-data
    if ($HasDockerData) {
        Write-Log "Step 7: Unregistering docker-desktop-data..." "INFO"
        $UnregisterResult = wsl --unregister docker-desktop-data 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "docker-desktop-data unregistered successfully" "INFO"
        } else {
            Write-Log "WARNING: Unregister may have failed (exit code: $LASTEXITCODE)" "WARN"
            Write-Log $UnregisterResult "WARN"
        }
    }

    # Step 8: Import docker-desktop-data to new location
    if ($HasDockerData -and (Test-Path $ExportFile)) {
        Write-Log "Step 8: Importing docker-desktop-data to new location..." "INFO"
        $ImportPath = Join-Path $DestPath "docker-desktop-data"
        
        Write-Log "Importing to: $ImportPath" "INFO"
        Write-Log "This may take several minutes..." "INFO"
        
        $ImportStart = Get-Date
        $ImportResult = wsl --import docker-desktop-data $ImportPath $ExportFile --version 2 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            $ImportDuration = (Get-Date) - $ImportStart
            Write-Log "Import completed successfully in $($ImportDuration.TotalMinutes) minutes" "INFO"
        } else {
            Write-Log "ERROR: Import failed!" "ERROR"
            Write-Log $ImportResult "ERROR"
            throw "Import failed with exit code $LASTEXITCODE"
        }
    }

    # Step 9: Verify new location
    Write-Log "Step 9: Verifying new location..." "INFO"
    $WslListAfter = wsl --list --verbose 2>&1
    Write-Log "WSL Distributions after move:" "INFO"
    Write-Log $WslListAfter "INFO"
    
    if ($WslListAfter -match "docker-desktop-data") {
        Write-Log "SUCCESS: docker-desktop-data found in WSL list" "INFO"
    } else {
        Write-Log "WARNING: docker-desktop-data not found in WSL list" "WARN"
    }

    # Step 10: Clean up export file (optional)
    if ($HasDockerData -and (Test-Path $ExportFile) -and -not $SkipBackup) {
        Write-Log "Step 10: Keeping export file as backup: $ExportFile" "INFO"
        Write-Log "To remove it later, run: Remove-Item '$ExportFile'" "INFO"
    } elseif ($HasDockerData -and (Test-Path $ExportFile) -and $SkipBackup) {
        Write-Log "Step 10: Removing export file..." "INFO"
        Remove-Item $ExportFile -Force
        Write-Log "Export file removed" "INFO"
    }

    # Step 11: Summary
    Write-Log "================================================" "INFO"
    Write-Log "Move operation completed!" "INFO"
    Write-Log "Next steps:" "INFO"
    Write-Log "1. Start Docker Desktop" "INFO"
    Write-Log "2. Verify with: docker info" "INFO"
    Write-Log "3. Check images: docker images" "INFO"
    Write-Log "4. Verify location: wsl --list --verbose" "INFO"
    Write-Log "================================================" "INFO"
    Write-Log "Log file saved to: $LogFile" "INFO"

} catch {
    Write-Log "================================================" "ERROR"
    Write-Log "ERROR: Move operation failed!" "ERROR"
    Write-Log "Error message: $($_.Exception.Message)" "ERROR"
    Write-Log "Error details: $($_.Exception)" "ERROR"
    Write-Log "================================================" "ERROR"
    Write-Log "Log file saved to: $LogFile" "ERROR"
    Write-Log "Please review the log file for details" "ERROR"
    exit 1
}
