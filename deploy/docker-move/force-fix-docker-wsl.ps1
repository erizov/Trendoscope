# PowerShell script to force fix Docker Desktop WSL distribution issue
# Run as Administrator

$ErrorActionPreference = "Stop"
$LogFile = "E:\Docker\force-fix-log-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage -ErrorAction SilentlyContinue
}

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

Write-Log "================================================" "INFO"
Write-Log "Force Fix Docker Desktop WSL Distribution" "INFO"
Write-Log "================================================" "INFO"

if (-not (Test-Administrator)) {
    Write-Log "ERROR: Must run as Administrator!" "ERROR"
    exit 1
}

$OldPath = "$env:LOCALAPPDATA\Docker\wsl"
$NewPath = "E:\Docker\wsl"

try {
    # Step 1: Stop ALL processes that might lock files
    Write-Log "Step 1: Stopping all Docker and WSL processes..." "INFO"
    
    # Stop Docker Desktop
    Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue | Stop-Process -Force
    Start-Sleep -Seconds 3
    
    # Stop docker processes
    Get-Process -Name "docker" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process -Name "dockerd" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process -Name "com.docker.backend" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Start-Sleep -Seconds 3
    
    # Force shutdown WSL
    Write-Log "Forcing WSL shutdown..." "INFO"
    wsl --shutdown 2>&1 | Out-Null
    Start-Sleep -Seconds 5
    
    # Kill any remaining WSL processes
    Get-Process -Name "wsl" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process -Name "wslhost" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Start-Sleep -Seconds 3
    Write-Log "All processes stopped" "INFO"

    # Step 2: Check for file locks
    Write-Log "Step 2: Checking for file locks..." "INFO"
    
    # Use handle.exe if available, or check manually
    $LockedFiles = @()
    try {
        $VhdxFile = Join-Path $NewPath "disk\docker_data.vhdx"
        if (Test-Path $VhdxFile) {
            # Try to open file exclusively to check if locked
            try {
                $FileStream = [System.IO.File]::Open($VhdxFile, 'Open', 'ReadWrite', 'None')
                $FileStream.Close()
                Write-Log "File is not locked: $VhdxFile" "INFO"
            } catch {
                Write-Log "WARNING: File may be locked: $VhdxFile" "WARN"
                Write-Log "Error: $_" "WARN"
            }
        }
    } catch {
        Write-Log "Could not check file locks: $_" "WARN"
    }

    # Step 3: Verify data location
    Write-Log "Step 3: Verifying data location..." "INFO"
    if (-not (Test-Path $NewPath)) {
        Write-Log "ERROR: New location does not exist: $NewPath" "ERROR"
        throw "New location not found"
    }
    Write-Log "Data exists at: $NewPath" "INFO"

    # Step 4: Check current junction state
    Write-Log "Step 4: Checking junction state..." "INFO"
    if (Test-Path $OldPath) {
        $Item = Get-Item $OldPath -Force -ErrorAction SilentlyContinue
        if ($Item) {
            $IsJunction = ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)
            
            if ($IsJunction) {
                Write-Log "Junction exists, removing to recreate..." "INFO"
                Remove-Item $OldPath -Force
                Start-Sleep -Seconds 2
            } else {
                Write-Log "Old path is a real folder, backing up and removing..." "WARN"
                $Backup = "${OldPath}_backup_$(Get-Date -Format 'yyyyMMdd-HHmmss')"
                if (Test-Path $Backup) {
                    Remove-Item $Backup -Recurse -Force -ErrorAction SilentlyContinue
                }
                Rename-Item $OldPath $Backup -Force -ErrorAction SilentlyContinue
                Write-Log "Backed up to: $Backup" "INFO"
                Start-Sleep -Seconds 2
            }
        }
    }

    # Step 5: Create fresh junction
    Write-Log "Step 5: Creating fresh junction..." "INFO"
    
    # Ensure parent exists
    $Parent = Split-Path -Parent $OldPath
    if (-not (Test-Path $Parent)) {
        New-Item -ItemType Directory -Path $Parent -Force | Out-Null
    }
    
    # Create junction
    $Result = cmd /c mklink /J `"$OldPath`" `"$NewPath`" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Junction created successfully" "INFO"
    } else {
        Write-Log "ERROR: Failed to create junction: $Result" "ERROR"
        throw "Junction creation failed"
    }

    # Step 6: Verify junction works
    Write-Log "Step 6: Verifying junction..." "INFO"
    if (Test-Path $OldPath) {
        $Item = Get-Item $OldPath -Force
        $IsJunction = ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)
        
        if ($IsJunction) {
            Write-Log "SUCCESS: Junction verified" "INFO"
            
            # Test access
            $TestPath = Join-Path $OldPath "disk\docker_data.vhdx"
            if (Test-Path $TestPath) {
                Write-Log "SUCCESS: Can access docker_data.vhdx through junction" "INFO"
            } else {
                Write-Log "WARNING: Cannot access docker_data.vhdx through junction" "WARN"
            }
        }
    }

    # Step 7: Additional WSL cleanup
    Write-Log "Step 7: Performing WSL cleanup..." "INFO"
    
    # List WSL distributions
    $WslList = wsl --list --verbose 2>&1
    Write-Log "Current WSL distributions:" "INFO"
    Write-Log $WslList "INFO"
    
    # Ensure docker-desktop is stopped
    wsl -d docker-desktop --terminate 2>&1 | Out-Null
    
    # Final shutdown
    wsl --shutdown 2>&1 | Out-Null
    Start-Sleep -Seconds 5

    # Step 8: Summary
    Write-Log "================================================" "INFO"
    Write-Log "Fix completed!" "INFO"
    Write-Log "" "INFO"
    Write-Log "IMPORTANT: Before starting Docker Desktop:" "INFO"
    Write-Log "1. Wait 10 seconds for all processes to fully stop" "INFO"
    Write-Log "2. Start Docker Desktop" "INFO"
    Write-Log "3. If you still get the error, try:" "INFO"
    Write-Log "   - Restart your computer" "INFO"
    Write-Log "   - Then start Docker Desktop" "INFO"
    Write-Log "" "INFO"
    Write-Log "Alternative if junction doesn't work:" "INFO"
    Write-Log "Docker Desktop may need the data at the original location." "INFO"
    Write-Log "You may need to move data back to C: drive or use a different method." "INFO"
    Write-Log "================================================" "INFO"
    Write-Log "Log file: $LogFile" "INFO"

} catch {
    Write-Log "================================================" "ERROR"
    Write-Log "ERROR: Fix failed!" "ERROR"
    Write-Log "Error: $($_.Exception.Message)" "ERROR"
    Write-Log "================================================" "ERROR"
    exit 1
}
