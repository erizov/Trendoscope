# Moving Docker Desktop Data from C: to E: Drive

This guide explains how to move Docker Desktop's data directory (images, containers, volumes) from C: to E: drive on Windows.

## Prerequisites

- Administrator access
- Docker Desktop installed
- E: drive with sufficient space (recommend at least 50GB free)

## Steps

### 1. Stop Docker Desktop

- Right-click the Docker icon in the system tray
- Select **"Quit Docker Desktop"**
- Wait until Docker Desktop fully closes

### 2. Open PowerShell as Administrator

- Press `Win + X`
- Select **"Windows PowerShell (Admin)"** or **"Terminal (Admin)"**

### 3. Check WSL Distributions

Verify Docker Desktop WSL distributions exist:

```powershell
wsl --list --verbose
```

You should see:
- `docker-desktop`
- `docker-desktop-data`

### 4. Shut Down All WSL Instances

```powershell
wsl --shutdown
```

Wait a few seconds for WSL to fully shut down.

### 5. Create Destination Directory on E: Drive

```powershell
New-Item -ItemType Directory -Path "E:\DockerData" -Force
```

### 6. Export Docker Data

Export the `docker-desktop-data` distribution to a tar file:

```powershell
wsl --export docker-desktop-data E:\DockerData\docker-desktop-data.tar
```

**Note**: This may take several minutes depending on the size of your Docker data.

### 7. Unregister Current Docker Data Distribution

```powershell
wsl --unregister docker-desktop-data
```

**Warning**: This removes the old distribution, but your data is safely exported in the tar file.

### 8. Import Docker Data to New Location

Import the data to the new location on E: drive:

```powershell
wsl --import docker-desktop-data E:\DockerData E:\DockerData\docker-desktop-data.tar --version 2
```

**Note**: This may also take several minutes.

### 9. Clean Up Temporary Export File (Optional)

After verifying everything works, you can delete the tar file:

```powershell
Remove-Item E:\DockerData\docker-desktop-data.tar
```

### 10. Start Docker Desktop

- Launch Docker Desktop from the Start menu
- Wait for it to fully start
- Verify it's working: `docker info`

### 11. Verify New Location

Check that Docker is using the new location:

```powershell
wsl --list --verbose
```

The `docker-desktop-data` should show location `E:\DockerData`.

## Verification

After moving, verify everything works:

```powershell
# Check Docker is running
docker info

# List images (should show your existing images)
docker images

# Check volumes
docker volume ls
```

## Troubleshooting

### If Docker Desktop Won't Start

1. Ensure WSL 2 is enabled:
   ```powershell
   wsl --set-default-version 2
   ```

2. Restart Docker Desktop

3. Check WSL distributions:
   ```powershell
   wsl --list --verbose
   ```

### If Images/Containers Are Missing

- The export/import process should preserve everything
- If something is missing, check the export tar file still exists
- You may need to re-import: `wsl --import docker-desktop-data E:\DockerData E:\DockerData\docker-desktop-data.tar --version 2`

### Disk Space Issues

- Ensure E: drive has enough space (at least 2x your current Docker data size)
- Check space: `Get-PSDrive E`

## Alternative: Move Only Docker Images/Volumes

If you only want to move specific data (not everything), you can:

1. Use Docker's data-root configuration (more complex)
2. Use symlinks (not recommended)
3. Use the WSL method above (recommended - moves everything)

## Notes

- **Backup**: Consider backing up important containers/images before moving
- **Time**: The export/import process can take 10-30 minutes depending on data size
- **Space**: Ensure E: drive has sufficient free space (check with `Get-PSDrive E`)
- **Future**: All new Docker data will automatically be stored on E: drive

## References

- Docker Desktop WSL 2 backend: https://docs.docker.com/desktop/wsl/
- WSL commands: https://docs.microsoft.com/en-us/windows/wsl/basic-commands
