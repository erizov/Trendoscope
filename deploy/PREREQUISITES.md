# Prerequisites for Running Docker Move Script

Before running `move-docker-to-d.ps1`, ensure the following prerequisites are met:

## Required

1. **Windows 10/11** with Administrator access
2. **WSL 2** installed and enabled
   - Check: `wsl --status` should show "Default Version: 2"
   - Install if needed: `wsl --install`
3. **Docker Desktop** installed with WSL 2 backend
   - Check: `wsl --list --verbose` should show `docker-desktop` and `docker-desktop-data`
4. **PowerShell 5.1 or later**
   - Check: `$PSVersionTable.PSVersion`
5. **E: drive** with sufficient free space (at least 20GB, recommend 50GB+)
   - Check: `Get-PSDrive E`

## PowerShell Execution Policy

If you get an execution policy error, run:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Or run the script with bypass:

```powershell
powershell -ExecutionPolicy Bypass -File .\move-docker-to-d.ps1
```

## Verification Commands

Run these before the script to verify prerequisites:

```powershell
# Check WSL
wsl --status
wsl --list --verbose

# Check Docker Desktop
Get-Process -Name "Docker Desktop" -ErrorAction SilentlyContinue

# Check disk space
Get-PSDrive E | Select-Object Name, @{Name="Free(GB)";Expression={[math]::Round($_.Free/1GB,2)}}

# Check PowerShell version
$PSVersionTable.PSVersion
```

## Troubleshooting

### "WSL command not found"
- Install WSL: `wsl --install`
- Restart computer after installation

### "docker-desktop-data not found"
- Ensure Docker Desktop is installed
- Ensure Docker Desktop is using WSL 2 backend (Settings → General → Use WSL 2 based engine)
- Start Docker Desktop at least once before running the script

### "Cannot create log directory"
- Check E: drive exists and is accessible
- Ensure you have write permissions on E: drive
- Try creating directory manually: `New-Item -ItemType Directory -Path "E:\Docker" -Force`

### "Execution Policy Error"
- Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- Or use: `powershell -ExecutionPolicy Bypass -File .\move-docker-to-d.ps1`
