# CI/CD Pipeline Plan for Trendoscope2

## 📋 Overview

This document outlines the CI/CD strategy for Trendoscope2, focusing on:
- **Development Flow**: Feature development in `trendoscope2/` → Promotion to `deploy/`
- **Deployment Pipeline**: Local environment → Production-ready deployment folder
- **Services**: FastAPI, Redis, PostgreSQL, Prometheus, Grafana
- **Security & Monitoring**: Integrated into deployment pipeline

---

## 🏗️ Architecture Overview

### Directory Structure

```
Trendoscope/
├── trendoscope2/          # Development environment
│   ├── src/               # Source code
│   ├── tests/             # Test suite
│   ├── scripts/           # Development scripts
│   └── docker/            # Development Docker configs
│
└── deploy/                # Production deployment (to be created)
    ├── src/               # Production code (copied from trendoscope2)
    ├── docker/            # Production Docker Compose
    ├── monitoring/        # Prometheus & Grafana configs
    ├── security/          # Security configs & secrets management
    ├── scripts/           # Deployment scripts
    └── docs/              # Deployment documentation
```

---

## 🔄 Development Workflow

### Phase 1: Feature Development (trendoscope2/)

**Location**: `trendoscope2/`

**Process**:
1. **Create Feature Branch**
   ```bash
   cd trendoscope2
   git checkout -b feature/new-feature-name
   ```

2. **Develop & Test Locally**
   - Write code in `trendoscope2/src/`
   - Add tests in `trendoscope2/tests/`
   - Run local tests: `pytest tests/`
   - Test manually: `.\scripts\start.ps1`

3. **Local Validation Checklist**
   - [ ] All unit tests pass
   - [ ] E2E tests pass
   - [ ] Code follows PEP 8
   - [ ] No linter errors
   - [ ] Manual testing successful
   - [ ] Documentation updated

4. **Commit & Push**
   ```bash
   git add .
   git commit -m "feat: Add new feature"
   git push origin feature/new-feature-name
   ```

### Phase 2: CI Validation (Automated)

**Trigger**: Push to `trendoscope2/` repository

**CI Pipeline Steps**:

1. **Code Quality Checks**
   ```yaml
   - Run linter (flake8, black, mypy)
   - Check code coverage (pytest-cov)
   - Validate imports and dependencies
   ```

2. **Unit Tests**
   ```yaml
   - Run pytest with coverage
   - Minimum coverage: 80%
   - Fail if any test fails
   ```

3. **E2E Tests**
   ```yaml
   - Start test environment (Docker Compose)
   - Run E2E test suite
   - Validate all endpoints
   - Check service health
   ```

4. **Integration Tests**
   ```yaml
   - Test with Redis
   - Test with PostgreSQL (optional)
   - Test async processing
   - Test background tasks
   ```

5. **Security Scan**
   ```yaml
   - Dependency vulnerability scan (safety, pip-audit)
   - Code security scan (bandit)
   - Docker image scan (trivy)
   ```

6. **Build Validation**
   ```yaml
   - Validate Docker images build
   - Check configuration files
   - Validate environment variables
   ```

**CI Tools**:
- **GitHub Actions** (recommended for local setup)
- **GitLab CI** (alternative)
- **Jenkins** (if preferred)

### Phase 3: Promotion to Deploy (Manual/Approved)

**Trigger**: Feature branch merged to `main` in `trendoscope2/`

**Promotion Process**:

1. **Automated Promotion Script**
   ```powershell
   # scripts/promote-to-deploy.ps1
   - Validate all tests pass
   - Copy code from trendoscope2/ to deploy/
   - Update version numbers
   - Generate deployment configs
   - Create deployment commit
   ```

2. **Deployment Preparation**
   - Update `deploy/docker/docker-compose.prod.yml`
   - Update `deploy/monitoring/prometheus.yml`
   - Update `deploy/security/secrets.example`
   - Generate production requirements

3. **Deployment Validation**
   - Build production Docker images
   - Run production E2E tests
   - Validate all services start correctly

---

## 🚀 Deployment Pipeline

### Deployment Folder Structure

```
deploy/
├── docker/
│   ├── docker-compose.prod.yml      # Production services
│   ├── Dockerfile.fastapi           # FastAPI production image
│   └── .env.prod.example            # Production env template
│
├── monitoring/
│   ├── prometheus/
│   │   ├── prometheus.yml           # Prometheus config
│   │   └── alerts.yml               # Alert rules
│   └── grafana/
│       ├── dashboards/              # Grafana dashboards
│       └── provisioning/            # Auto-provisioning
│
├── security/
│   ├── nginx/                       # Nginx reverse proxy
│   │   └── nginx.conf
│   ├── ssl/                         # SSL certificates (gitignored)
│   └── secrets/                     # Secrets management
│       └── .env.prod                # Production secrets (gitignored)
│
├── scripts/
│   ├── deploy.ps1                   # Main deployment script
│   ├── rollback.ps1                 # Rollback script
│   ├── health-check.ps1             # Health check script
│   └── backup.ps1                   # Backup script
│
└── docs/
    ├── DEPLOYMENT.md                # Deployment guide
    ├── MONITORING.md                # Monitoring setup
    └── SECURITY.md                  # Security guide
```

### Services in Deployment

**From LOCAL_INFRASTRUCTURE_PLAN.md (lines 509-513)**:
- ✅ **FastAPI** (localhost:8004 → production port)
- ✅ **Redis** (localhost:6379)
- ✅ **PostgreSQL** (localhost:5432)
- ✅ **Prometheus** (localhost:9090)
- ✅ **Grafana** (localhost:3000)

**Additional Production Services**:
- **Nginx** (reverse proxy, SSL termination)
- **Backup Service** (automated database backups)
- **Log Aggregation** (optional: ELK stack)

### Deployment Steps

#### Step 1: Pre-Deployment Validation

```powershell
# scripts/pre-deploy-check.ps1
- Validate all services configured
- Check secrets are set
- Validate SSL certificates
- Check disk space
- Validate network connectivity
```

#### Step 2: Build Production Images

```powershell
# Build FastAPI image
docker build -f docker/Dockerfile.fastapi -t trendoscope2-api:latest .

# Build other service images if needed
docker-compose -f docker/docker-compose.prod.yml build
```

#### Step 3: Database Migration

```powershell
# Run migrations if using PostgreSQL
python scripts/migrate.py --env production
```

#### Step 4: Deploy Services

```powershell
# Start all services
docker-compose -f docker/docker-compose.prod.yml up -d

# Wait for health checks
.\scripts\health-check.ps1 -timeout 300
```

#### Step 5: Post-Deployment Validation

```powershell
# Run smoke tests
pytest tests/e2e/test_production.py

# Check service health
.\scripts\health-check.ps1

# Validate monitoring
curl http://localhost:9090/api/v1/targets  # Prometheus
curl http://localhost:3000/api/health      # Grafana
```

#### Step 6: Rollback (if needed)

```powershell
# Rollback to previous version
.\scripts\rollback.ps1 -version <previous-version>
```

---

## 🔧 CI/CD Configuration

### GitHub Actions Workflow

**File**: `.github/workflows/ci-cd.yml`

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
    paths:
      - 'trendoscope2/**'
  pull_request:
    branches: [main]
    paths:
      - 'trendoscope2/**'

jobs:
  # Development Validation
  validate:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          cd trendoscope2
          pip install -r requirements-minimal.txt
          pip install pytest pytest-cov flake8 black mypy
      
      - name: Lint
        run: |
          cd trendoscope2
          flake8 src/ tests/
          black --check src/ tests/
          mypy src/
      
      - name: Test
        run: |
          cd trendoscope2
          pytest tests/ --cov=src --cov-report=xml
      
      - name: E2E Tests
        run: |
          cd trendoscope2
          # Start services
          docker-compose -f docker/docker-compose.local.yml up -d redis
          # Run E2E tests
          pytest tests/e2e/ -v
      
      - name: Security Scan
        run: |
          cd trendoscope2
          pip install safety bandit
          safety check
          bandit -r src/
  
  # Promotion to Deploy
  promote:
    needs: validate
    runs-on: windows-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v3
      
      - name: Promote to Deploy
        run: |
          cd trendoscope2
          .\scripts\promote-to-deploy.ps1
      
      - name: Create Deployment PR
        uses: peter-evans/create-pull-request@v5
        with:
          title: "Deploy: Promote changes to production"
          body: "Automated promotion from trendoscope2 to deploy/"
          branch: deploy/promote-$(date +%s)
  
  # Deployment Validation
  deploy-validate:
    needs: promote
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Validate Deployment
        run: |
          cd deploy
          docker-compose -f docker/docker-compose.prod.yml config
          docker-compose -f docker/docker-compose.prod.yml build
```

---

## 🐛 Bug Fix Workflow

### Process for Bug Fixes

1. **Identify Bug** (in `trendoscope2/` or `deploy/`)
   - Create issue with reproduction steps
   - Label: `bug`, `critical` (if production)

2. **Fix in Development** (`trendoscope2/`)
   ```bash
   git checkout -b fix/bug-description
   # Fix bug
   # Add test case
   # Run tests
   ```

3. **CI Validation**
   - All tests must pass
   - Bug fix test case included
   - No regressions

4. **Hotfix Process** (if critical production bug)
   ```bash
   # Fix directly in deploy/ (temporary)
   # Then backport to trendoscope2/
   # Then promote properly
   ```

5. **Promotion**
   - Same promotion process as features
   - Faster approval for bug fixes

---

## 🔒 Security Pipeline

### Security Checks

1. **Dependency Scanning**
   - Check for known vulnerabilities
   - Update dependencies regularly
   - Use `requirements-security.txt` for production

2. **Code Security**
   - Static analysis (bandit)
   - Secret scanning (truffleHog, git-secrets)
   - SQL injection checks
   - XSS prevention validation

3. **Container Security**
   - Scan Docker images (trivy, snyk)
   - Use minimal base images
   - No secrets in images

4. **Secrets Management**
   - Use environment variables
   - Never commit secrets
   - Rotate secrets regularly
   - Use `.env.prod` (gitignored)

### Security in Deployment

```yaml
# deploy/security/nginx.conf
- SSL/TLS termination
- Rate limiting
- CORS configuration
- Security headers
- DDoS protection
```

---

## 📊 Monitoring Pipeline

### Prometheus Configuration

**File**: `deploy/monitoring/prometheus/prometheus.yml`

```yaml
scrape_configs:
  - job_name: 'trendoscope2-api'
    static_configs:
      - targets: ['fastapi:8004']
  
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
  
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
```

### Grafana Dashboards

- **API Metrics**: Request rate, latency, errors
- **Database Metrics**: Query performance, connections
- **System Metrics**: CPU, RAM, disk usage
- **Business Metrics**: News items processed, translations

### Alerting Rules

**File**: `deploy/monitoring/prometheus/alerts.yml`

```yaml
groups:
  - name: trendoscope2_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
      
      - alert: DatabaseDown
        expr: up{job="postgres"} == 0
```

---

## 📝 Feature Development Checklist

### Before Starting

- [ ] Create feature branch from `main`
- [ ] Review existing code structure
- [ ] Check for similar features
- [ ] Plan API changes (if any)

### During Development

- [ ] Write code following PEP 8
- [ ] Add type hints
- [ ] Write unit tests
- [ ] Write E2E tests (if applicable)
- [ ] Update documentation
- [ ] Test locally

### Before Promotion

- [ ] All tests pass
- [ ] Code reviewed (self-review minimum)
- [ ] No linter errors
- [ ] Documentation updated
- [ ] Migration scripts (if database changes)
- [ ] Backward compatibility checked

### Promotion Process

- [ ] Merge to `main` in `trendoscope2/`
- [ ] CI pipeline passes
- [ ] Run promotion script
- [ ] Validate deployment configs
- [ ] Create deployment PR
- [ ] Manual testing in deploy environment
- [ ] Approve and merge deployment PR

---

## 🚨 Rollback Strategy

### Automatic Rollback Triggers

- Health check failures > 3 consecutive
- Error rate > 10% for 5 minutes
- Database connection failures
- Critical service down

### Manual Rollback

```powershell
# Rollback to previous version
.\scripts\rollback.ps1 -version <version> -reason "Bug in latest release"

# Rollback steps:
# 1. Stop current services
# 2. Restore previous Docker images
# 3. Restore database backup (if needed)
# 4. Start previous version
# 5. Validate health
```

---

## 📈 Metrics & KPIs

### CI/CD Metrics

- **Build Time**: Target < 10 minutes
- **Test Coverage**: Target > 80%
- **Deployment Frequency**: As needed
- **Mean Time to Recovery**: Target < 15 minutes
- **Change Failure Rate**: Target < 5%

### Deployment Metrics

- **Deployment Success Rate**: Target > 95%
- **Zero-Downtime Deployments**: Target 100%
- **Rollback Frequency**: Target < 2% of deployments

---

## 🎯 Implementation Phases

### Phase 1: Basic CI (Week 1-2)

- [ ] Set up GitHub Actions
- [ ] Basic linting and testing
- [ ] E2E test automation
- [ ] Create `deploy/` folder structure

### Phase 2: Promotion Pipeline (Week 3-4)

- [ ] Create promotion script
- [ ] Automated code copying
- [ ] Deployment config generation
- [ ] Basic deployment validation

### Phase 3: Full Deployment (Week 5-6)

- [ ] Production Docker Compose
- [ ] Monitoring setup (Prometheus/Grafana)
- [ ] Security hardening
- [ ] Backup automation

### Phase 4: Advanced Features (Week 7-8)

- [ ] Automated rollback
- [ ] Blue-green deployments
- [ ] Canary releases
- [ ] Performance testing

---

## 📚 Documentation Requirements

### Required Documentation

1. **CI/CD Guide**: How to use the pipeline
2. **Deployment Guide**: Step-by-step deployment
3. **Monitoring Guide**: How to use Prometheus/Grafana
4. **Security Guide**: Security best practices
5. **Troubleshooting Guide**: Common issues and solutions

### Documentation Location

- Development docs: `trendoscope2/docs/`
- Deployment docs: `deploy/docs/`
- API docs: Auto-generated at `/docs`

---

## ✅ Success Criteria

### CI/CD Pipeline is Successful When:

1. ✅ All tests pass automatically on every commit
2. ✅ Code quality is maintained (linting, coverage)
3. ✅ Security vulnerabilities are caught early
4. ✅ Deployment is automated and reliable
5. ✅ Rollback is quick and safe
6. ✅ Monitoring provides visibility
7. ✅ Documentation is up-to-date

---

## 🔄 Continuous Improvement

### Regular Reviews

- **Weekly**: Review CI/CD metrics
- **Monthly**: Review and update pipeline
- **Quarterly**: Major pipeline improvements

### Feedback Loop

- Collect deployment metrics
- Analyze failure patterns
- Improve automation
- Update documentation

---

## 📞 Support & Escalation

### Issues During CI/CD

1. **CI Failures**: Check logs, fix issues, re-run
2. **Deployment Failures**: Use rollback script
3. **Production Issues**: Follow incident response plan

### Emergency Contacts

- **CI/CD Issues**: Development team
- **Production Issues**: On-call engineer
- **Security Issues**: Security team

---

## 🎉 Next Steps

1. **Review this plan** with the team
2. **Set up basic CI** (GitHub Actions)
3. **Create `deploy/` folder** structure
4. **Implement promotion script**
5. **Test end-to-end** workflow
6. **Iterate and improve**

---

**Last Updated**: 2025-12-15
**Version**: 1.0.0
**Status**: Planning Phase

