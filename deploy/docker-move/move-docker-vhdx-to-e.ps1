# PowerShell script to move Docker Desktop VHDX files from C: to E:
# Alternative approach when docker-desktop-data WSL distribution doesn't exist
# Run as Administrator

param(
    [string]$SourcePath = "$env:LOCALAPPDATA\Docker\wsl",
    [string]$DestPath = "E:\Docker\wsl",
    [switch]$SkipBackup = $false
)

$ErrorActionPreference = "Stop"
$LogFile = "E:\Docker\move-docker-vhdx-log-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"

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
Write-Log "Docker VHDX Move Script Started" "INFO"
Write-Log "Source: $SourcePath" "INFO"
Write-Log "Destination: $DestPath" "INFO"
Write-Log "================================================" "INFO"

# Check if running as Administrator
if (-not (Test-Administrator)) {
    Write-Log "ERROR: This script must be run as Administrator!" "ERROR"
    Write-Log "Right-click PowerShell and select 'Run as Administrator'" "ERROR"
    exit 1
}

# Create log directory if it doesn't exist
$LogDir = Split-Path -Path $LogFile -Parent
if (-not (Test-Path $LogDir)) {
    try {
        New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
        Write-Log "Created log directory: $LogDir" "INFO"
    } catch {
        Write-Host "WARNING: Could not create log directory: $LogDir" -ForegroundColor Yellow
    }
}

try {
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

    # Step 3: Verify source path exists
    Write-Log "Step 3: Verifying source path..." "INFO"
    if (-not (Test-Path $SourcePath)) {
        Write-Log "ERROR: Source path does not exist: $SourcePath" "ERROR"
        throw "Source path not found"
    }
    Write-Log "Source path exists: $SourcePath" "INFO"

    # Step 4: Check for VHDX files
    Write-Log "Step 4: Checking for Docker VHDX files..." "INFO"
    $VhdxFiles = Get-ChildItem -Path $SourcePath -Filter "*.vhdx" -Recurse -ErrorAction SilentlyContinue
    if ($VhdxFiles.Count -eq 0) {
        Write-Log "WARNING: No VHDX files found in source path" "WARN"
        Write-Log "Checking for alternative Docker data locations..." "INFO"
    } else {
        Write-Log "Found $($VhdxFiles.Count) VHDX file(s):" "INFO"
        foreach ($File in $VhdxFiles) {
            $SizeGB = [math]::Round($File.Length / 1GB, 2)
            Write-Log "  - $($File.FullName) ($SizeGB GB)" "INFO"
        }
    }

    # Step 5: Calculate total size
    Write-Log "Step 5: Calculating total data size..." "INFO"
    $TotalSize = (Get-ChildItem -Path $SourcePath -Recurse -ErrorAction SilentlyContinue | 
                  Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
    $TotalSizeGB = [math]::Round($TotalSize / 1GB, 2)
    Write-Log "Total size to move: $TotalSizeGB GB" "INFO"

    # Step 6: Check disk space
    Write-Log "Step 6: Checking destination disk space..." "INFO"
    $DestDrive = (Split-Path -Qualifier $DestPath).TrimEnd(':')
    $DestDriveInfo = Get-PSDrive -Name $DestDrive -ErrorAction SilentlyContinue
    if ($DestDriveInfo) {
        $FreeSpaceGB = [math]::Round($DestDriveInfo.Free / 1GB, 2)
        Write-Log "Free space on $DestDrive`: $FreeSpaceGB GB" "INFO"
        if ($FreeSpaceGB -lt ($TotalSizeGB * 1.2)) {
            Write-Log "WARNING: May not have enough free space (need ~$([math]::Round($TotalSizeGB * 1.2, 2)) GB)" "WARN"
        }
    }

    # Step 7: Create destination directory structure
    Write-Log "Step 7: Creating destination directory structure..." "INFO"
    $DestParent = Split-Path -Parent $DestPath
    if (-not (Test-Path $DestParent)) {
        New-Item -ItemType Directory -Path $DestParent -Force | Out-Null
        Write-Log "Created directory: $DestParent" "INFO"
    }

    # Step 8: Move the entire wsl directory
    Write-Log "Step 8: Moving Docker wsl directory..." "INFO"
    Write-Log "This may take 10-30 minutes depending on data size..." "INFO"
    
    $MoveStart = Get-Date
    
    # Use robocopy for reliable large file moves
    $RobocopyLog = Join-Path $DestPath "robocopy-log.txt"
    $RobocopyResult = & robocopy $SourcePath $DestPath /E /MOVE /R:3 /W:5 /LOG:$RobocopyLog /NP /NDL /NFL
    
    $MoveDuration = (Get-Date) - $MoveStart
    Write-Log "Move operation completed in $($MoveDuration.TotalMinutes) minutes" "INFO"
    
    # Check robocopy exit codes (0-7 are success)
    if ($RobocopyResult -le 7) {
        Write-Log "Files moved successfully" "INFO"
    } else {
        Write-Log "WARNING: Robocopy returned exit code: $RobocopyResult" "WARN"
        Write-Log "Check robocopy log: $RobocopyLog" "WARN"
    }

    # Step 9: Create junction/symlink from old location to new location
    Write-Log "Step 9: Creating symbolic link from old to new location..." "INFO"
    
    # Remove old directory if empty or only has junction
    if (Test-Path $SourcePath) {
        $RemainingItems = Get-ChildItem -Path $SourcePath -ErrorAction SilentlyContinue
        if ($RemainingItems.Count -eq 0) {
            Remove-Item -Path $SourcePath -Force -ErrorAction SilentlyContinue
            Write-Log "Removed empty source directory" "INFO"
        }
    }
    
    # Create junction point
    try {
        $JunctionResult = cmd /c mklink /J $SourcePath $DestPath 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Symbolic link created successfully" "INFO"
            Write-Log "Old path now points to: $DestPath" "INFO"
        } else {
            Write-Log "WARNING: Could not create junction: $JunctionResult" "WARN"
            Write-Log "You may need to manually create a junction or update Docker settings" "WARN"
        }
    } catch {
        Write-Log "WARNING: Junction creation failed: $_" "WARN"
    }

    # Step 10: Verify move
    Write-Log "Step 10: Verifying move..." "INFO"
    if (Test-Path $DestPath) {
        $DestSize = (Get-ChildItem -Path $DestPath -Recurse -ErrorAction SilentlyContinue | 
                     Measure-Object -Property Length -Sum -ErrorAction SilentlyContinue).Sum
        $DestSizeGB = [math]::Round($DestSize / 1GB, 2)
        Write-Log "Destination size: $DestSizeGB GB" "INFO"
        
        if ($DestSizeGB -ge ($TotalSizeGB * 0.95)) {
            Write-Log "SUCCESS: Data appears to have moved successfully" "INFO"
        } else {
            Write-Log "WARNING: Destination size is less than expected" "WARN"
        }
    } else {
        Write-Log "ERROR: Destination path does not exist after move!" "ERROR"
        throw "Move verification failed"
    }

    # Step 11: Summary
    Write-Log "================================================" "INFO"
    Write-Log "Move operation completed!" "INFO"
    Write-Log "Next steps:" "INFO"
    Write-Log "1. Start Docker Desktop" "INFO"
    Write-Log "2. Verify with: docker info" "INFO"
    Write-Log "3. Check images: docker images" "INFO"
    Write-Log "4. Verify data location: Check Docker Desktop Settings" "INFO"
    Write-Log "================================================" "INFO"
    Write-Log "Log file saved to: $LogFile" "INFO"
    Write-Log "Robocopy log saved to: $RobocopyLog" "INFO"

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
