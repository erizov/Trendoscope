# Fix: Docker Engine Stopped / WSL Distribution Copy Error

## Error Message

```
An unexpected error occurred while copying the Docker Desktop WSL distro.
Either shut down WSL with wsl --shutdown and reopen Docker Desktop, 
or reboot your machine. If the issue persists, collect diagnostics and submit an issue.

installing main distribution: copying distribution: 
The process cannot access the file because it is being used by another process.
```

## Root Cause

Docker Desktop is trying to recreate/initialize the WSL distribution but files are locked because:
1. WSL instances are still running
2. Docker Desktop processes are still active
3. File handles are not released
4. Junction may be causing access issues

## Solution Steps

### Step 1: Run Force Fix Script (as Administrator)

```powershell
cd E:\Python\FastAPI\Trendoscope\deploy
.\force-fix-docker-wsl.ps1
```

This script will:
- Force stop all Docker and WSL processes
- Shutdown WSL completely
- Recreate the junction properly
- Clean up any locks

### Step 2: If Script Doesn't Work, Manual Steps

**Run these commands as Administrator:**

```powershell
# 1. Stop everything
Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name "docker*" -ErrorAction SilentlyContinue | Stop-Process -Force
wsl --shutdown
Start-Sleep -Seconds 10

# 2. Kill any remaining processes
Get-Process | Where-Object {$_.ProcessName -like "*docker*" -or $_.ProcessName -like "*wsl*"} | Stop-Process -Force -ErrorAction SilentlyContinue

# 3. Verify junction
$OldPath = "$env:LOCALAPPDATA\Docker\wsl"
if (Test-Path $OldPath) {
    $Item = Get-Item $OldPath -Force
    $IsJunction = ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)
    if (-not $IsJunction) {
        Write-Host "Removing non-junction folder..." -ForegroundColor Yellow
        Remove-Item $OldPath -Recurse -Force
        cmd /c mklink /J "$OldPath" "E:\Docker\wsl"
    }
}

# 4. Final WSL shutdown
wsl --shutdown
Start-Sleep -Seconds 5
```

### Step 3: Restart Computer (Recommended)

After running the fix script:

1. **Restart your computer** (this ensures all file handles are released)
2. **Start Docker Desktop** after restart
3. **Wait 2-3 minutes** for full initialization

### Step 4: If Still Fails - Move Data Back Temporarily

**The issue**: Docker Desktop is trying to COPY/initialize the WSL distribution, and junctions may interfere with this process.

**Solution**: Move data back to C: temporarily, let Docker initialize, then move again.

**Run this script as Administrator:**

```powershell
cd E:\Python\FastAPI\Trendoscope\deploy
.\move-back-to-c-temp.ps1
```

This will:
1. Stop all Docker/WSL processes
2. Remove junction
3. Move data back to `C:\Users\<user>\AppData\Local\Docker\wsl`
4. Let Docker Desktop initialize properly

**After Docker Desktop works on C: drive:**
- You can try moving to E: again using WSL export/import method
- Or keep it on C: if space allows

**Option B: Use Docker Desktop's built-in data location setting**
- Some Docker Desktop versions allow changing data location
- Check: Docker Desktop Settings → Resources → Advanced → Disk image location
- If available, set it to `E:\Docker` directly (no junction needed)

## Verification After Fix

```powershell
# 1. Check junction
dir "$env:LOCALAPPDATA\Docker\wsl" | Select Name, Attributes
# Should show <JUNCTION>

# 2. Test access
dir "$env:LOCALAPPDATA\Docker\wsl\disk"
# Should show docker_data.vhdx

# 3. Start Docker Desktop and test
docker info
docker images
```

## Prevention

To avoid this issue in the future:
1. Always stop Docker Desktop completely before moving data
2. Use `wsl --shutdown` before any WSL-related operations
3. Wait 10-15 seconds after stopping processes before moving files
4. Consider restarting computer after major Docker data moves
