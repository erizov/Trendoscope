# Troubleshooting: docker-desktop-data Not Found

## Problem

The script reports:
```
ERROR: docker-desktop-data distribution not found
```

But you see `docker-desktop` in the WSL list.

## Why This Happens

The `docker-desktop-data` WSL distribution is created automatically when Docker Desktop starts for the first time with WSL 2 backend enabled. If it's missing, it usually means:

1. Docker Desktop hasn't been started yet, OR
2. Docker Desktop is using Hyper-V backend instead of WSL 2, OR
3. Docker Desktop was installed but never fully initialized

## Solution

### Step 1: Verify Docker Desktop Settings

**Note**: In newer Docker Desktop versions, the "Use WSL 2 based engine" checkbox may not appear in General tab because WSL 2 is the default.

1. **Start Docker Desktop** (if not running)
2. **Open Settings** (gear icon in Docker Desktop)

**Check these locations:**

**Option A: General Tab (older versions)**
- ✅ "Use WSL 2 based engine" should be **checked** (if this option exists)

**Option B: Resources > WSL Integration (newer versions)**
- Go to **Resources > WSL Integration**
- ✅ "Enable integration with my default WSL distro" should be **checked**
- ✅ Enable integration for specific distros (Ubuntu, etc.) if needed

**Option C: Advanced Settings**
- Some versions have WSL settings under **Resources > Advanced**
- Check if WSL 2 is mentioned or configured there

3. **Click "Apply & Restart"** if you changed anything

### Step 2: Wait for Full Initialization

- Wait for Docker Desktop to fully start (whale icon in system tray should be steady)
- This can take 1-2 minutes on first start

### Step 3: Verify WSL Distribution Exists

Open PowerShell and run:

```powershell
wsl --list --verbose
```

You should see BOTH:
- `docker-desktop` (Stopped or Running)
- `docker-desktop-data` (Stopped or Running)

### Step 4: If Still Missing

Try these commands:

```powershell
# Update WSL
wsl --update

# Restart Docker Desktop
# (Right-click system tray icon > Quit, then start again)

# Check again
wsl --list --verbose
```

### Step 5: Nuclear Option (if nothing works)

If `docker-desktop-data` still doesn't appear:

1. **Uninstall Docker Desktop** (keep data if prompted)
2. **Reinstall Docker Desktop**
3. **During installation**, ensure WSL 2 is selected
4. **Start Docker Desktop** and wait for full initialization
5. **Verify** with `wsl --list --verbose`

## Verification Commands

After fixing, verify everything is ready:

```powershell
# Should show both distributions
wsl --list --verbose

# Should work
docker info

# Should show images (if any)
docker images
```

## Common Issues

### "docker-desktop exists but docker-desktop-data doesn't"

- **Cause**: Docker Desktop started but didn't create data distribution
- **Fix**: Restart Docker Desktop, ensure WSL 2 backend is enabled

### "Neither distribution exists"

- **Cause**: Docker Desktop not installed or WSL 2 not enabled
- **Fix**: Install Docker Desktop with WSL 2 backend

### "WSL command not found"

- **Cause**: WSL not installed
- **Fix**: Run `wsl --install` and restart computer

## After Fixing

Once `docker-desktop-data` appears in `wsl --list --verbose`, you can run the move script again:

```powershell
.\move-docker-to-d.ps1
```
