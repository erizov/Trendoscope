# Moving Docker Desktop VHDX Files (Alternative Method)

## When to Use This Method

Use `move-docker-vhdx-to-e.ps1` when:
- `docker-desktop-data` WSL distribution doesn't exist
- Docker Desktop is using VHDX files directly (newer versions)
- You found VHDX files at `C:\Users\<user>\AppData\Local\Docker\wsl\disk\docker_data.vhdx`

## What This Script Does

1. Stops Docker Desktop
2. Shuts down WSL
3. Moves the entire `wsl` directory from `C:\Users\<user>\AppData\Local\Docker\wsl` to `E:\Docker\wsl`
4. Creates a junction/symlink from old location to new location
5. Docker Desktop will continue to work using the junction

## Prerequisites

- Administrator access
- Docker Desktop stopped
- E: drive with sufficient space (at least 1.2x your Docker data size)
- Robocopy available (built into Windows)

## Usage

```powershell
# Run as Administrator
cd E:\Python\FastAPI\Trendoscope\deploy
.\move-docker-vhdx-to-e.ps1
```

### Parameters

- `-SourcePath`: Source path (default: `$env:LOCALAPPDATA\Docker\wsl`)
- `-DestPath`: Destination path (default: `E:\Docker\wsl`)
- `-SkipBackup`: Not used in this script (robocopy handles it)

## How It Works

1. **Robocopy** moves files reliably (handles large files, retries on errors)
2. **Junction point** is created so Docker Desktop still sees the old path
3. **No Docker settings changes needed** - the junction makes it transparent

## After Running

1. **Start Docker Desktop**
2. **Verify everything works:**
   ```powershell
   docker info
   docker images
   ```

3. **Check actual location:**
   ```powershell
   # Should show junction pointing to E:\Docker\wsl
   dir "$env:LOCALAPPDATA\Docker\wsl"
   ```

## Advantages

- ✅ Works even when `docker-desktop-data` WSL distribution doesn't exist
- ✅ Moves all Docker data (VHDX files, configs, etc.)
- ✅ Creates junction so Docker Desktop doesn't need reconfiguration
- ✅ Uses robocopy for reliable large file moves
- ✅ Detailed logging

## Disadvantages

- ⚠️ Requires Administrator access
- ⚠️ Takes longer (moves entire directory structure)
- ⚠️ Junction points can be confusing if you forget they exist

## Troubleshooting

### Junction Creation Fails

If the junction can't be created:
1. Manually create it: `mklink /J "$env:LOCALAPPDATA\Docker\wsl" "E:\Docker\wsl"`
2. Or update Docker Desktop settings to point to new location (if possible)

### Docker Desktop Won't Start

1. Check junction exists: `dir "$env:LOCALAPPDATA\Docker\wsl"`
2. Verify data exists at destination: `dir E:\Docker\wsl`
3. Check robocopy log for errors

### Not Enough Space

- Ensure E: drive has at least 1.2x your Docker data size free
- Check: `Get-PSDrive E | Select-Object Free`

## Verification

After move, verify:

```powershell
# Check junction
dir "$env:LOCALAPPDATA\Docker\wsl" | Select-Object LinkType, Target

# Check actual location
Get-ChildItem "E:\Docker\wsl" -Recurse | Measure-Object -Property Length -Sum

# Test Docker
docker info
docker images
```
