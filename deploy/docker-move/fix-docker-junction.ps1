# PowerShell script to fix Docker Desktop junction after moving data to E:\Docker\wsl
# Run as Administrator

$ErrorActionPreference = "Stop"
$LogFile = "E:\Docker\fix-junction-log-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"

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
Write-Log "Docker Junction Fix Script" "INFO"
Write-Log "================================================" "INFO"

if (-not (Test-Administrator)) {
    Write-Log "ERROR: Must run as Administrator!" "ERROR"
    exit 1
}

$OldPath = "$env:LOCALAPPDATA\Docker\wsl"
$NewPath = "E:\Docker\wsl"

try {
    # Step 1: Stop Docker Desktop
    Write-Log "Step 1: Stopping Docker Desktop..." "INFO"
    $DockerProcess = Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue
    if ($DockerProcess) {
        Stop-Process -Name "Docker Desktop" -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 5
        Write-Log "Docker Desktop stopped" "INFO"
    }

    # Step 2: Shutdown WSL
    Write-Log "Step 2: Shutting down WSL..." "INFO"
    wsl --shutdown 2>&1 | Out-Null
    Start-Sleep -Seconds 3

    # Step 3: Verify new location exists
    Write-Log "Step 3: Verifying new location..." "INFO"
    if (-not (Test-Path $NewPath)) {
        Write-Log "ERROR: New location does not exist: $NewPath" "ERROR"
        throw "New location not found"
    }
    Write-Log "New location exists: $NewPath" "INFO"

    # Step 4: Check current state of old path
    Write-Log "Step 4: Checking current state of old path..." "INFO"
    if (Test-Path $OldPath) {
        $Item = Get-Item $OldPath
        $IsJunction = ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)
        
        if ($IsJunction) {
            Write-Log "Junction already exists at: $OldPath" "INFO"
            $Target = (Get-Item $OldPath).Target
            Write-Log "Current junction target: $Target" "INFO"
            
            if ($Target -ne $NewPath) {
                Write-Log "Junction points to wrong location, removing..." "WARN"
                Remove-Item $OldPath -Force
            } else {
                Write-Log "Junction is correct, but Docker may need restart" "INFO"
            }
        } else {
            Write-Log "Old path exists but is NOT a junction (real folder)" "WARN"
            Write-Log "Checking if it's empty or has data..." "INFO"
            
            $Items = Get-ChildItem $OldPath -ErrorAction SilentlyContinue
            if ($Items.Count -eq 0) {
                Write-Log "Old folder is empty, removing..." "INFO"
                Remove-Item $OldPath -Force
            } else {
                Write-Log "WARNING: Old folder has $($Items.Count) items" "WARN"
                Write-Log "Backing up old folder..." "INFO"
                $BackupPath = "${OldPath}_backup_$(Get-Date -Format 'yyyyMMdd-HHmmss')"
                Rename-Item $OldPath $BackupPath -Force
                Write-Log "Backed up to: $BackupPath" "INFO"
            }
        }
    }

    # Step 5: Create/verify junction
    Write-Log "Step 5: Creating junction..." "INFO"
    if (-not (Test-Path $OldPath)) {
        # Create parent directory if needed
        $Parent = Split-Path -Parent $OldPath
        if (-not (Test-Path $Parent)) {
            New-Item -ItemType Directory -Path $Parent -Force | Out-Null
        }
        
        # Create junction using cmd mklink (more reliable than PowerShell)
        $MklinkCmd = "cmd /c mklink /J `"$OldPath`" `"$NewPath`""
        Write-Log "Running: $MklinkCmd" "INFO"
        $Result = Invoke-Expression $MklinkCmd 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Junction created successfully" "INFO"
        } else {
            Write-Log "ERROR: Failed to create junction: $Result" "ERROR"
            throw "Junction creation failed"
        }
    }

    # Step 6: Verify junction
    Write-Log "Step 6: Verifying junction..." "INFO"
    if (Test-Path $OldPath) {
        $Item = Get-Item $OldPath
        $IsJunction = ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)
        
        if ($IsJunction) {
            Write-Log "SUCCESS: Junction verified" "INFO"
            Write-Log "Junction: $OldPath -> $NewPath" "INFO"
            
            # Test access through junction
            $TestFile = Get-ChildItem "$OldPath\disk" -ErrorAction SilentlyContinue | Select-Object -First 1
            if ($TestFile) {
                Write-Log "SUCCESS: Can access files through junction" "INFO"
            } else {
                Write-Log "WARNING: Junction exists but cannot access files" "WARN"
            }
        } else {
            Write-Log "ERROR: Path exists but is not a junction!" "ERROR"
            throw "Junction verification failed"
        }
    } else {
        Write-Log "ERROR: Junction was not created!" "ERROR"
        throw "Junction does not exist"
    }

    # Step 7: Check Docker Desktop settings
    Write-Log "Step 7: Checking Docker Desktop settings..." "INFO"
    $SettingsPath = "$env:APPDATA\Docker\settings.json"
    if (Test-Path $SettingsPath) {
        try {
            $Settings = Get-Content $SettingsPath | ConvertFrom-Json
            Write-Log "Docker settings file found" "INFO"
            Write-Log "wslEngineEnabled: $($Settings.wslEngineEnabled)" "INFO"
        } catch {
            Write-Log "Could not read settings file" "WARN"
        }
    }

    # Step 8: Summary
    Write-Log "================================================" "INFO"
    Write-Log "Fix completed!" "INFO"
    Write-Log "Next steps:" "INFO"
    Write-Log "1. Start Docker Desktop" "INFO"
    Write-Log "2. Wait for full initialization (2-3 minutes)" "INFO"
    Write-Log "3. Verify: docker info" "INFO"
    Write-Log "4. Check: docker images" "INFO"
    Write-Log "================================================" "INFO"
    Write-Log "Log file: $LogFile" "INFO"

} catch {
    Write-Log "================================================" "ERROR"
    Write-Log "ERROR: Fix failed!" "ERROR"
    Write-Log "Error: $($_.Exception.Message)" "ERROR"
    Write-Log "================================================" "ERROR"
    exit 1
}
