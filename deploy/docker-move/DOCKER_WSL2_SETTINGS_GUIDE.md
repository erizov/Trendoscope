# Docker Desktop WSL 2 Settings Guide

## If "Use WSL 2 based engine" Checkbox is Missing

In newer versions of Docker Desktop (4.0+), the "Use WSL 2 based engine" checkbox may not appear because:
- WSL 2 is now the **default** backend
- The setting has been moved to a different location
- Your system may not support Hyper-V (so WSL 2 is the only option)

## Where to Check WSL 2 Settings

### Method 1: Resources > WSL Integration (Most Common)

1. Open Docker Desktop
2. Click **Settings** (gear icon)
3. Go to **Resources > WSL Integration**
4. Check:
   - ✅ "Enable integration with my default WSL distro"
   - ✅ Enable for specific distros (Ubuntu-20.04, Ubuntu-22.04, etc.)
5. Click **Apply & Restart**

### Method 2: Check Docker Desktop Version

Run this to check your Docker Desktop version:

```powershell
docker --version
docker version
```

**Docker Desktop 4.0+**: WSL 2 is default, no checkbox needed
**Docker Desktop 3.x**: May have the checkbox in General tab

### Method 3: Verify WSL 2 is Actually Being Used

Run the diagnostic script:

```powershell
cd E:\Python\FastAPI\Trendoscope\deploy
.\CHECK_DOCKER_WSL2.ps1
```

This will show:
- Whether docker-desktop-data exists
- Docker Desktop version
- WSL integration status

## Creating docker-desktop-data Distribution

If `docker-desktop-data` is missing, try these steps:

### Step 1: Ensure WSL Integration is Enabled

1. Docker Desktop Settings > **Resources > WSL Integration**
2. Enable integration with your WSL distros
3. Click **Apply & Restart**

### Step 2: Fully Restart Docker Desktop

1. **Quit Docker Desktop completely:**
   - Right-click Docker icon in system tray
   - Select **"Quit Docker Desktop"**
   - Wait 10-15 seconds

2. **Start Docker Desktop again:**
   - Launch from Start menu
   - **Wait 2-3 minutes** for full initialization
   - Check system tray - whale icon should be steady (not animating)

### Step 3: Verify Distribution Created

```powershell
wsl --list --verbose
```

You should now see:
```
docker-desktop       Stopped         2
docker-desktop-data  Stopped         2
```

## Alternative: Force WSL 2 via Settings File

If the GUI doesn't work, you can manually edit Docker Desktop settings:

1. **Quit Docker Desktop**

2. **Edit settings file:**
   ```powershell
   notepad "$env:APPDATA\Docker\settings.json"
   ```

3. **Look for and ensure:**
   ```json
   "wslEngineEnabled": true
   ```

4. **Save and restart Docker Desktop**

## Still Not Working?

If `docker-desktop-data` still doesn't appear after following these steps:

1. **Run diagnostic script:**
   ```powershell
   .\CHECK_DOCKER_WSL2.ps1
   ```

2. **Check WSL version:**
   ```powershell
   wsl --version
   wsl --status
   ```

3. **Update WSL:**
   ```powershell
   wsl --update
   ```

4. **Restart Docker Desktop** and wait for full initialization

5. **Check again:**
   ```powershell
   wsl --list --verbose
   ```

## Quick Test

After Docker Desktop is running, test if it's using WSL 2:

```powershell
# Should work if Docker is using WSL 2
docker info | Select-String -Pattern "WSL|Operating System"
```

If you see WSL mentioned, Docker is likely using WSL 2 backend.
