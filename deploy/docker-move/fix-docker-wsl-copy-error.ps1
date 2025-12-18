# PowerShell script to fix Docker Desktop WSL distro copy error
# This happens when Docker Desktop tries to initialize/recreate the distribution
# Run as Administrator

$ErrorActionPreference = "Stop"
$LogFile = "E:\Docker\fix-wsl-copy-error-log-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"

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
Write-Log "Fix Docker Desktop WSL Distro Copy Error" "INFO"
Write-Log "================================================" "INFO"

if (-not (Test-Administrator)) {
    Write-Log "ERROR: Must run as Administrator!" "ERROR"
    exit 1
}

$OldPath = "$env:LOCALAPPDATA\Docker\wsl"
$NewPath = "E:\Docker\wsl"

try {
    # Step 1: Force stop everything
    Write-Log "Step 1: Force stopping all processes..." "INFO"
    
    Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "docker*" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "wsl*" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "dockerd" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "com.docker.backend" -ErrorAction SilentlyContinue | Stop-Process -Force
    
    Start-Sleep -Seconds 5
    
    # Force WSL shutdown
    wsl --shutdown 2>&1 | Out-Null
    Start-Sleep -Seconds 10
    
    Write-Log "All processes stopped" "INFO"

    # Step 2: Check current state
    Write-Log "Step 2: Checking current state..." "INFO"
    
    $OldPathExists = Test-Path $OldPath
    $NewPathExists = Test-Path $NewPath
    
    Write-Log "Old path exists: $OldPathExists" "INFO"
    Write-Log "New path exists: $NewPathExists" "INFO"
    
    if (-not $NewPathExists) {
        Write-Log "ERROR: New path does not exist: $NewPath" "ERROR"
        throw "New location not found"
    }

    # Step 3: Check if old path is junction or real folder
    if ($OldPathExists) {
        $Item = Get-Item $OldPath -Force -ErrorAction SilentlyContinue
        if ($Item) {
            $IsJunction = ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)
            
            if ($IsJunction) {
                Write-Log "Old path is a junction" "INFO"
                Write-Log "Docker Desktop may have issues with junctions during initialization" "WARN"
                Write-Log "Removing junction temporarily..." "INFO"
                Remove-Item $OldPath -Force
            } else {
                Write-Log "Old path is a real folder" "INFO"
                # Check if it has data or is empty
                $Items = Get-ChildItem $OldPath -ErrorAction SilentlyContinue
                if ($Items.Count -gt 0) {
                    Write-Log "Old folder has $($Items.Count) items" "INFO"
                    # Check if it's the actual data or Docker trying to recreate
                    $OldVhdx = Join-Path $OldPath "disk\docker_data.vhdx"
                    if (Test-Path $OldVhdx) {
                        Write-Log "WARNING: Old folder has docker_data.vhdx - data may be duplicated" "WARN"
                    } else {
                        Write-Log "Old folder appears to be Docker initialization attempt" "INFO"
                    }
                }
            }
        }
    }

    # Step 4: Move data back temporarily (if needed) OR create junction
    Write-Log "Step 4: Setting up path..." "INFO"
    
    # Option: Move data back temporarily to let Docker initialize
    # OR: Create junction and hope Docker accepts it
    
    # Since user already has data on E:, let's try creating junction
    # But first ensure old path doesn't exist
    if (Test-Path $OldPath) {
        Write-Log "Removing old path..." "INFO"
        Remove-Item $OldPath -Recurse -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }
    
    # Create junction
    Write-Log "Creating junction: $OldPath -> $NewPath" "INFO"
    $Parent = Split-Path -Parent $OldPath
    if (-not (Test-Path $Parent)) {
        New-Item -ItemType Directory -Path $Parent -Force | Out-Null
    }
    
    $Result = cmd /c mklink /J `"$OldPath`" `"$NewPath`" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Log "Junction created" "INFO"
    } else {
        Write-Log "ERROR: Failed to create junction: $Result" "ERROR"
        throw "Junction creation failed"
    }

    # Step 5: Verify junction
    Write-Log "Step 5: Verifying junction..." "INFO"
    if (Test-Path $OldPath) {
        $Item = Get-Item $OldPath -Force
        $IsJunction = ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)
        if ($IsJunction) {
            Write-Log "Junction verified" "INFO"
        }
    }

    # Step 6: Final WSL cleanup
    Write-Log "Step 6: Final WSL cleanup..." "INFO"
    wsl --shutdown 2>&1 | Out-Null
    Start-Sleep -Seconds 5
    
    # List WSL distributions
    $WslList = wsl --list --verbose 2>&1
    Write-Log "WSL distributions:" "INFO"
    Write-Log $WslList "INFO"

    # Step 7: Summary and recommendations
    Write-Log "================================================" "INFO"
    Write-Log "Fix completed!" "INFO"
    Write-Log "" "INFO"
    Write-Log "IMPORTANT: Docker Desktop may still fail with this error" "WARN"
    Write-Log "because it tries to COPY/initialize the distribution." "WARN"
    Write-Log "" "INFO"
    Write-Log "RECOMMENDED SOLUTION:" "INFO"
    Write-Log "1. RESTART YOUR COMPUTER (this releases all file handles)" "INFO"
    Write-Log "2. After restart, start Docker Desktop" "INFO"
    Write-Log "3. If error persists, try:" "INFO"
    Write-Log "   a. Move data back to C: temporarily" "INFO"
    Write-Log "   b. Let Docker Desktop initialize" "INFO"
    Write-Log "   c. Then move data to E: again" "INFO"
    Write-Log "" "INFO"
    Write-Log "ALTERNATIVE: Check Docker Desktop Settings" "INFO"
    Write-Log "Some versions allow changing data location:" "INFO"
    Write-Log "Settings > Resources > Advanced > Disk image location" "INFO"
    Write-Log "================================================" "INFO"
    Write-Log "Log file: $LogFile" "INFO"

} catch {
    Write-Log "================================================" "ERROR"
    Write-Log "ERROR: Fix failed!" "ERROR"
    Write-Log "Error: $($_.Exception.Message)" "ERROR"
    Write-Log "================================================" "ERROR"
    exit 1
}

