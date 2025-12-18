# PowerShell script to temporarily move Docker data back to C: drive
# This lets Docker Desktop initialize properly, then you can move it again
# Run as Administrator

$ErrorActionPreference = "Stop"
$LogFile = "E:\Docker\move-back-to-c-log-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"

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
Write-Log "Move Docker Data Back to C: (Temporary)" "INFO"
Write-Log "================================================" "INFO"

if (-not (Test-Administrator)) {
    Write-Log "ERROR: Must run as Administrator!" "ERROR"
    exit 1
}

$OldPath = "$env:LOCALAPPDATA\Docker\wsl"
$NewPath = "E:\Docker\wsl"

try {
    # Step 1: Stop everything
    Write-Log "Step 1: Stopping all processes..." "INFO"
    Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue | Stop-Process -Force
    Get-Process -Name "docker*" -ErrorAction SilentlyContinue | Stop-Process -Force
    wsl --shutdown 2>&1 | Out-Null
    Start-Sleep -Seconds 10

    # Step 2: Remove junction if exists
    Write-Log "Step 2: Removing junction..." "INFO"
    if (Test-Path $OldPath) {
        $Item = Get-Item $OldPath -Force -ErrorAction SilentlyContinue
        if ($Item) {
            $IsJunction = ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)
            if ($IsJunction) {
                Remove-Item $OldPath -Force
                Write-Log "Junction removed" "INFO"
            } else {
                Write-Log "Old path is a real folder, backing up..." "INFO"
                $Backup = "${OldPath}_backup_$(Get-Date -Format 'yyyyMMdd-HHmmss')"
                Rename-Item $OldPath $Backup -Force
                Write-Log "Backed up to: $Backup" "INFO"
            }
        }
    }

    # Step 3: Move data back to C:
    Write-Log "Step 3: Moving data back to C:..." "INFO"
    Write-Log "This may take 15-30 minutes for 86GB..." "INFO"
    
    if (Test-Path $NewPath) {
        $MoveStart = Get-Date
        robocopy $NewPath $OldPath /E /MOVE /R:3 /W:5 /NP /NDL /NFL
        
        $MoveDuration = (Get-Date) - $MoveStart
        Write-Log "Move completed in $($MoveDuration.TotalMinutes) minutes" "INFO"
        
        # Verify
        if (Test-Path (Join-Path $OldPath "disk\docker_data.vhdx")) {
            Write-Log "SUCCESS: Data moved back to C:" "INFO"
        } else {
            Write-Log "WARNING: docker_data.vhdx not found at C: location" "WARN"
        }
    } else {
        Write-Log "ERROR: Source path does not exist: $NewPath" "ERROR"
        throw "Source not found"
    }

    # Step 4: Summary
    Write-Log "================================================" "INFO"
    Write-Log "Data moved back to C: drive" "INFO"
    Write-Log "" "INFO"
    Write-Log "Next steps:" "INFO"
    Write-Log "1. Start Docker Desktop" "INFO"
    Write-Log "2. Wait for full initialization (2-3 minutes)" "INFO"
    Write-Log "3. Verify: docker info" "INFO"
    Write-Log "4. Once Docker works, you can try moving to E: again" "INFO"
    Write-Log "   using the WSL export/import method" "INFO"
    Write-Log "================================================" "INFO"

} catch {
    Write-Log "================================================" "ERROR"
    Write-Log "ERROR: Move failed!" "ERROR"
    Write-Log "Error: $($_.Exception.Message)" "ERROR"
    Write-Log "================================================" "ERROR"
    exit 1
}

