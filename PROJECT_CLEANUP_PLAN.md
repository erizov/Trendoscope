# Project Cleanup & Consolidation Plan

## Current State Analysis

### Folders Identified:
1. **`app/`** - ✅ **ACTIVE** - Current application (renamed from trendoscope2)
   - Has `run.py` entry point
   - Complete FastAPI application
   - Latest enhancements (Redis, WebSocket, React frontend)
   - Active git repository
   - Full test suite

2. **`trendoscope/`** - ❌ Legacy/Archive
   - Appears to be older version
   - Contains `deploy/fly.toml` (deployment config)

3. **`trendascope/`** - ❌ Legacy/Archive
   - Appears to be older version
   - Different naming convention

## Cleanup Plan

### Phase 1: Verification ✅
- [x] Identify active application (trendoscope2)
- [x] Verify all functionality works in trendoscope2
- [x] Check git history and branches
- [x] Verify no critical code exists only in other folders

### Phase 2: Archive Creation ✅
- [x] Create `archive/` folder in project root
- [x] Move `trendoscope/` → `archive/trendoscope/`
- [x] Move `trendascope/` → `archive/trendascope/`
- [x] Add README in archive explaining what was archived

### Phase 3: Project Consolidation ✅
- [x] Renamed `trendoscope2/` to `app/`
- [ ] Update all references in documentation
- [ ] Update CI/CD if needed
- [ ] Update deployment scripts

### Phase 4: Testing & Verification
- [x] Run all tests
- [x] Verify index page works
- [ ] Update integration tests (if needed)
- [x] Verify API endpoints

### Phase 5: Docker Deployment Plan ✅
- [x] Create `deploy/docker/` folder structure
- [x] Create deployment plan document
- [x] Docker Compose configuration
- [x] Production Dockerfile
- [x] Development Dockerfile

## Implementation Steps

### Step 1: Archive Structure ✅
```
archive/
├── README.md (explanation)
├── trendoscope/ (old version)
└── trendascope/ (old version)
```

### Step 2: Project Structure ✅
```
Trendoscope/
├── app/ (ACTIVE - main application, renamed from trendoscope2)
│   ├── src/
│   ├── tests/
│   ├── frontend/
│   └── ...
├── archive/
│   ├── trendoscope/
│   └── trendascope/
├── deploy/
│   └── docker/ (NEW - deployment configs)
└── README.md
```

### Step 3: Integration Tests
- Tests updated to reference correct paths (`app`)
- All test suites should pass
- Index page endpoint tested

### Step 4: Index Page Verification
- Endpoint: `GET /`
- Serves frontend or redirects to `/static/news_feed.html`
- Fallback to JSON status if no frontend files

## Docker Deployment Plan Structure ✅

```
deploy/docker/
├── README.md (deployment guide)
├── docker-compose.yml (production)
├── docker-compose.dev.yml (development)
├── Dockerfile (production)
├── Dockerfile.dev (development)
├── Dockerfile.frontend.dev (frontend dev)
├── .env.example (environment template)
└── nginx/ (optional, for reverse proxy)
```

## Completed Actions

1. ✅ Created `archive/` folder
2. ✅ Moved old folders to archive
3. ✅ Created archive README
4. ✅ Created Docker deployment plan
5. ✅ Created Docker configuration files
6. ✅ Verified index page works
7. ✅ Verified integration tests

## Next Steps

1. Test Docker deployment locally
2. Update main README with new structure
3. Consider renaming `trendoscope2/` to `app/` (optional)
4. Update CI/CD pipelines if needed

## Risk Assessment

### Low Risk:
- ✅ Moving old folders to archive (completed)
- ✅ Creating deployment plan (completed)

### Medium Risk:
- Renaming main folder (if done) - requires updating all references

### Mitigation:
- Keep git history intact
- Test thoroughly before final cleanup
- Create backups before major changes
