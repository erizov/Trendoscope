# Trendoscope Management Scripts

## Overview

Management scripts for starting, stopping, and restarting the Trendoscope application.

## Scripts

### `start.ps1`
Starts the Trendoscope application and all required services.

**Features:**
- Stops any existing processes on port 8004
- Starts Redis container (if Docker is available)
- Starts FastAPI application in a new window
- Verifies application health
- Provides status information

**Usage:**
```powershell
.\start.ps1
```

**What it does:**
1. Stops existing processes
2. Checks for processes on port 8004
3. Starts Redis (if available)
4. Starts FastAPI application
5. Verifies health endpoint

### `stop.ps1`
Stops all Trendoscope processes and services.

**Features:**
- Finds and kills processes on port 8004
- Kills Python processes running Trendoscope
- Stops Redis container (if running)

**Usage:**
```powershell
.\stop.ps1
```

**What it does:**
1. Stops processes on port 8004
2. Stops Python application processes
3. Stops Redis container

### `restart.ps1`
Restarts all Trendoscope services.

**Features:**
- Calls stop script
- Waits for cleanup
- Calls start script

**Usage:**
```powershell
.\restart.ps1
```

### `test_scripts.ps1`
Comprehensive test script for all management scripts.

**Usage:**
```powershell
.\test_scripts.ps1
```

**Tests:**
1. Stop functionality
2. Start functionality
3. Health endpoint verification
4. Root endpoint verification
5. Restart functionality
6. Pytest health tests

## Health Check

The scripts verify application health by checking:
- `http://localhost:8004/health` - Health endpoint
- Response status code 200
- Health data (status, redis, database)

## Logs

Application logs are stored in:
- `app/logs/app_YYYYMMDD_HHMMSS.log` - Application output
- `app/logs/app_YYYYMMDD_HHMMSS_error.log` - Error output

## Process Management

The scripts identify Trendoscope processes by:
- Port 8004 connections
- Python processes with command line containing:
  - `run.py`
  - `uvicorn`
  - `trendoscope`
  - `app.api.main`

## Troubleshooting

### API not starting
1. Check if port 8004 is already in use:
   ```powershell
   Get-NetTCPConnection -LocalPort 8004
   ```
2. Check application logs:
   ```powershell
   Get-Content app\logs\app_*.log -Tail 50
   ```
3. Verify Python is installed:
   ```powershell
   python --version
   ```

### Processes not stopping
1. Manually kill processes:
   ```powershell
   Get-Process python | Stop-Process -Force
   ```
2. Check for processes on port 8004:
   ```powershell
   Get-NetTCPConnection -LocalPort 8004 | Stop-Process -Id {OwningProcess} -Force
   ```

### Redis not starting
- Docker may not be available
- Application will run with in-memory cache
- Check Docker status:
  ```powershell
  docker info
  ```

## Integration with Existing Scripts

The root scripts (`start.ps1`, `stop.ps1`, `restart.ps1`) integrate with scripts in the `scripts/` folder:
- Uses `scripts/stop.ps1` for initial cleanup
- Maintains compatibility with existing workflow

## Testing

Run comprehensive tests:
```powershell
.\test_scripts.ps1
```

Or test manually:
```powershell
# Start
.\start.ps1

# Wait and check
Start-Sleep -Seconds 10
.\scripts\check_api.ps1

# Run pytest
cd app
python -m pytest tests/integration/test_all_endpoints.py::TestHealthEndpoints -v

# Stop
cd ..
.\stop.ps1
```
