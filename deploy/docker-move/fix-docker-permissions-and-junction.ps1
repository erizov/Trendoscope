# PowerShell script to fix Docker Desktop junction and permissions
# Run as Administrator

$ErrorActionPreference = "Stop"
$LogFile = "E:\Docker\fix-docker-complete-log-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"

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
Write-Log "Docker Complete Fix Script" "INFO"
Write-Log "================================================" "INFO"

if (-not (Test-Administrator)) {
    Write-Log "ERROR: Must run as Administrator!" "ERROR"
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Red
    exit 1
}

$OldPath = "$env:LOCALAPPDATA\Docker\wsl"
$NewPath = "E:\Docker\wsl"
$UserName = $env:USERNAME

try {
    # Step 1: Stop Docker Desktop
    Write-Log "Step 1: Stopping Docker Desktop..." "INFO"
    $DockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
    if ($DockerProcess) {
        Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 5
        Write-Log "Docker Desktop stopped" "INFO"
    } else {
        Write-Log "Docker Desktop is not running" "INFO"
    }

    # Step 2: Shutdown WSL
    Write-Log "Step 2: Shutting down WSL..." "INFO"
    wsl --shutdown 2>&1 | Out-Null
    Start-Sleep -Seconds 5

    # Step 3: Verify new location exists
    Write-Log "Step 3: Verifying new location..." "INFO"
    if (-not (Test-Path $NewPath)) {
        Write-Log "ERROR: New location does not exist: $NewPath" "ERROR"
        throw "New location not found"
    }
    Write-Log "New location exists: $NewPath" "INFO"
    
    # Check for key files
    $VhdxFile = Join-Path $NewPath "disk\docker_data.vhdx"
    if (Test-Path $VhdxFile) {
        $SizeGB = [math]::Round((Get-Item $VhdxFile).Length / 1GB, 2)
        Write-Log "Found docker_data.vhdx: $SizeGB GB" "INFO"
    } else {
        Write-Log "WARNING: docker_data.vhdx not found at expected location" "WARN"
    }

    # Step 4: Set permissions on E:\Docker\wsl
    Write-Log "Step 4: Setting permissions on E:\Docker\wsl..." "INFO"
    try {
        # Grant full control to current user
        $PermResult = icacls "E:\Docker\wsl" /grant "${UserName}:(OI)(CI)F" /T 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Permissions set successfully" "INFO"
        } else {
            Write-Log "WARNING: Permission setting returned code: $LASTEXITCODE" "WARN"
            Write-Log "Output: $PermResult" "WARN"
        }
        
        # Also grant to SYSTEM and Administrators
        icacls "E:\Docker\wsl" /grant "SYSTEM:(OI)(CI)F" /T 2>&1 | Out-Null
        icacls "E:\Docker\wsl" /grant "Administrators:(OI)(CI)F" /T 2>&1 | Out-Null
        Write-Log "Additional permissions set" "INFO"
    } catch {
        Write-Log "WARNING: Could not set permissions: $_" "WARN"
    }

    # Step 5: Check and fix old path
    Write-Log "Step 5: Checking old path..." "INFO"
    if (Test-Path $OldPath) {
        $Item = Get-Item $OldPath -Force
        $IsJunction = ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)
        
        if ($IsJunction) {
            Write-Log "Junction exists, checking target..." "INFO"
            try {
                $Target = (Get-Item $OldPath).Target
                Write-Log "Current junction target: $Target" "INFO"
                
                if ($Target -ne $NewPath) {
                    Write-Log "Junction points to wrong location, removing..." "WARN"
                    Remove-Item $OldPath -Force
                } else {
                    Write-Log "Junction is correct" "INFO"
                }
            } catch {
                Write-Log "Could not read junction target, removing..." "WARN"
                Remove-Item $OldPath -Force
            }
        } else {
            Write-Log "Old path is a REAL folder, not a junction" "WARN"
            
            # Check if it has data
            $Items = Get-ChildItem $OldPath -ErrorAction SilentlyContinue
            if ($Items.Count -gt 0) {
                Write-Log "WARNING: Old folder has $($Items.Count) items" "WARN"
                Write-Log "Checking if it's Docker data or empty..." "INFO"
                
                # Check if it has docker_data.vhdx
                $OldVhdx = Join-Path $OldPath "disk\docker_data.vhdx"
                if (Test-Path $OldVhdx) {
                    Write-Log "ERROR: Old folder still has docker_data.vhdx!" "ERROR"
                    Write-Log "Data may not have been fully moved" "ERROR"
                    Write-Log "Please verify data is at: $NewPath" "ERROR"
                } else {
                    Write-Log "Old folder appears to be empty or recreated by Docker" "INFO"
                }
            }
            
            # Backup and remove
            Write-Log "Backing up old folder..." "INFO"
            $BackupPath = "${OldPath}_backup_$(Get-Date -Format 'yyyyMMdd-HHmmss')"
            if (Test-Path $BackupPath) {
                Remove-Item $BackupPath -Recurse -Force -ErrorAction SilentlyContinue
            }
            Rename-Item $OldPath $BackupPath -Force -ErrorAction SilentlyContinue
            Write-Log "Backed up to: $BackupPath" "INFO"
        }
    }

    # Step 6: Create junction
    Write-Log "Step 6: Creating junction..." "INFO"
    if (-not (Test-Path $OldPath)) {
        # Ensure parent directory exists
        $Parent = Split-Path -Parent $OldPath
        if (-not (Test-Path $Parent)) {
            New-Item -ItemType Directory -Path $Parent -Force | Out-Null
            Write-Log "Created parent directory: $Parent" "INFO"
        }
        
        # Create junction using cmd mklink
        Write-Log "Creating junction: $OldPath -> $NewPath" "INFO"
        $Result = cmd /c mklink /J `"$OldPath`" `"$NewPath`" 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Junction created successfully" "INFO"
            Write-Log "Output: $Result" "INFO"
        } else {
            Write-Log "ERROR: Failed to create junction" "ERROR"
            Write-Log "Exit code: $LASTEXITCODE" "ERROR"
            Write-Log "Output: $Result" "ERROR"
            throw "Junction creation failed"
        }
    } else {
        Write-Log "Junction already exists" "INFO"
    }

    # Step 7: Verify junction
    Write-Log "Step 7: Verifying junction..." "INFO"
    if (Test-Path $OldPath) {
        $Item = Get-Item $OldPath -Force
        $IsJunction = ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)
        
        if ($IsJunction) {
            Write-Log "SUCCESS: Junction verified" "INFO"
            
            # Test access through junction
            $TestPath = Join-Path $OldPath "disk"
            if (Test-Path $TestPath) {
                $TestFiles = Get-ChildItem $TestPath -ErrorAction SilentlyContinue
                Write-Log "SUCCESS: Can access files through junction ($($TestFiles.Count) items in disk folder)" "INFO"
            } else {
                Write-Log "WARNING: Cannot access disk folder through junction" "WARN"
            }
        } else {
            Write-Log "ERROR: Path exists but is not a junction!" "ERROR"
            throw "Junction verification failed"
        }
    } else {
        Write-Log "ERROR: Junction was not created!" "ERROR"
        throw "Junction does not exist"
    }

    # Step 8: Final verification
    Write-Log "Step 8: Final verification..." "INFO"
    Write-Log "Old path (junction): $OldPath" "INFO"
    Write-Log "New path (actual): $NewPath" "INFO"
    Write-Log "Junction status: OK" "INFO"
    
    # Check directory listing through junction
    $JunctionContents = Get-ChildItem $OldPath -ErrorAction SilentlyContinue
    Write-Log "Contents accessible through junction: $($JunctionContents.Count) items" "INFO"

    # Step 9: Summary
    Write-Log "================================================" "INFO"
    Write-Log "Fix completed successfully!" "INFO"
    Write-Log "" "INFO"
    Write-Log "Next steps:" "INFO"
    Write-Log "1. Start Docker Desktop" "INFO"
    Write-Log "2. Wait 2-3 minutes for full initialization" "INFO"
    Write-Log "3. Verify: docker info" "INFO"
    Write-Log "4. Check: docker images" "INFO"
    Write-Log "" "INFO"
    Write-Log "If Docker engine still stops:" "INFO"
    Write-Log "- Check Docker Desktop logs (Troubleshoot > View logs)" "INFO"
    Write-Log "- Try: Docker Desktop Settings > Troubleshoot > Reset to factory defaults" "INFO"
    Write-Log "  (This won't delete your data if junction is correct)" "INFO"
    Write-Log "================================================" "INFO"
    Write-Log "Log file: $LogFile" "INFO"

} catch {
    Write-Log "================================================" "ERROR"
    Write-Log "ERROR: Fix failed!" "ERROR"
    Write-Log "Error: $($_.Exception.Message)" "ERROR"
    Write-Log "Stack: $($_.Exception.StackTrace)" "ERROR"
    Write-Log "================================================" "ERROR"
    Write-Log "Log file: $LogFile" "ERROR"
    exit 1
}
