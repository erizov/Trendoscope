# Quick Pre-Run Checklist

Before running `move-docker-to-d.ps1`, quickly verify:

## ✅ Quick Checks (30 seconds)

```powershell
# 1. Check WSL is available
wsl --list --verbose
# Should show: docker-desktop and docker-desktop-data

# 2. Check E: drive has space
Get-PSDrive E | Select-Object Name, @{Name="Free(GB)";Expression={[math]::Round($_.Free/1GB,2)}}
# Should show at least 20GB free

# 3. Check you're ready to run
# - Docker Desktop is stopped (or will be stopped by script)
# - You have Administrator access
# - E: drive exists and is accessible
```

## 🚀 Ready to Run?

If all checks pass:

```powershell
# Open PowerShell as Administrator
# Navigate to script directory
cd E:\Python\FastAPI\Trendoscope\deploy

# Run the script
.\move-docker-to-d.ps1
```

## ⚠️ If Something Fails

See `PREREQUISITES.md` for detailed troubleshooting.
