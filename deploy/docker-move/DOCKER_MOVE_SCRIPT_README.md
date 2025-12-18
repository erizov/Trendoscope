# Docker Move Script Usage

## Quick Start

1. **Open PowerShell as Administrator**
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

2. **Navigate to script directory**
   ```powershell
   cd E:\Python\FastAPI\Trendoscope\deploy
   ```

3. **Run the script**
   ```powershell
   .\move-docker-to-d.ps1
   ```

## Script Parameters

- `-SourcePath`: Source path (default: `C:\Docker`)
- `-DestPath`: Destination path (default: `E:\Docker`)
- `-SkipBackup`: Remove export file after import (default: keep as backup)

## Examples

### Basic usage (C:\Docker → E:\Docker)
```powershell
.\move-docker-to-d.ps1
```

### Custom paths
```powershell
.\move-docker-to-d.ps1 -SourcePath "C:\Docker" -DestPath "D:\Docker"
```

### Remove backup file after move
```powershell
.\move-docker-to-d.ps1 -SkipBackup
```

## What the Script Does

1. ✅ Checks if running as Administrator
2. ✅ Stops Docker Desktop if running
3. ✅ Shuts down WSL instances
4. ✅ Lists WSL distributions
5. ✅ Creates destination directory
6. ✅ Checks disk space
7. ✅ Exports docker-desktop-data to tar file
8. ✅ Unregisters old docker-desktop-data
9. ✅ Imports docker-desktop-data to new location
10. ✅ Verifies new location
11. ✅ Creates detailed log file

## Log File

The script creates a detailed log file at:
```
E:\Docker\move-docker-log-YYYYMMDD-HHMMSS.txt
```

## After Running the Script

1. **Start Docker Desktop**
   - Launch from Start menu
   - Wait for it to fully start

2. **Verify everything works**
   ```powershell
   docker info
   docker images
   docker volume ls
   ```

3. **Verify new location**
   ```powershell
   wsl --list --verbose
   ```
   Should show `docker-desktop-data` at `E:\Docker\docker-desktop-data`

## Troubleshooting

### Script fails with "must be run as Administrator"
- Right-click PowerShell
- Select "Run as Administrator"

### Docker Desktop won't start after move
- Check WSL distributions: `wsl --list --verbose`
- Ensure WSL 2 is default: `wsl --set-default-version 2`
- Restart Docker Desktop

### Images/containers missing
- Check if export file still exists: `E:\Docker\docker-desktop-data-export.tar`
- Re-import if needed (see script log for exact command)

### Not enough disk space
- Check free space: `Get-PSDrive E`
- Need at least 20GB free (more is better)

## Safety Features

- ✅ Creates backup export file before unregistering
- ✅ Detailed logging of all operations
- ✅ Error handling with rollback information
- ✅ Verifies each step before proceeding

## Notes

- **Time**: Export/import can take 10-30 minutes depending on Docker data size
- **Backup**: Export file is kept by default (can be removed with `-SkipBackup`)
- **Space**: Ensure destination drive has sufficient free space
- **Future**: All new Docker data will be stored at the new location
