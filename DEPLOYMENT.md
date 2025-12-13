# 🚀 Trendoscope Deployment Guide

Complete guide for deploying Trendoscope in various environments.

---

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Docker Deployment](#docker-deployment)
- [Cloud Platforms](#cloud-platforms)
- [VPS Deployment](#vps-deployment)
- [Production Checklist](#production-checklist)
- [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start

### Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your settings

# 3. Run server
python run.py
```

Server runs on: `http://localhost:8003`

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Manual Docker

```bash
# Build image
docker build -t trendoscope .

# Run container
docker run -d \
  -p 8003:8003 \
  -v $(pwd)/data:/app/data \
  -e OPENAI_API_KEY=your-key \
  trendoscope
```

### Docker Compose Configuration

See `docker-compose.yml` for full configuration.

**Features:**
- Auto-restart on failure
- Volume mounting for data
- Environment variable support
- Health checks

---

## ☁️ Cloud Platforms

### Railway

**One-Click Deploy:**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)

**Manual Setup:**

1. Create new project
2. Connect GitHub repository
3. Add environment variables
4. Deploy

**Configuration:**
- See `deploy/railway.json`

### Render

**Setup:**

1. Create new Web Service
2. Connect repository
3. Build command: `pip install -r requirements.txt`
4. Start command: `python run.py`
5. Add environment variables

**Configuration:**
- See `deploy/render.yaml`

### Fly.io

**Setup:**

```bash
# Install flyctl
curl -L https://fly.io/install.sh | sh

# Deploy
fly deploy
```

**Configuration:**
- See `deploy/fly.toml`

### AWS / GCP / Azure

**General Steps:**

1. Create VM instance
2. Install Python 3.11+
3. Clone repository
4. Install dependencies
5. Configure environment
6. Run with systemd/PM2
7. Setup reverse proxy (Nginx)

---

## 🖥️ VPS Deployment

### Ubuntu/Debian

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python
sudo apt install python3.11 python3.11-venv python3-pip -y

# 3. Clone repository
git clone https://github.com/erizov/Trendoscope.git
cd Trendoscope/trendascope

# 4. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Configure
cp .env.example .env
nano .env  # Edit with your settings

# 7. Setup systemd service
sudo cp deploy/trendoscope.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable trendoscope
sudo systemctl start trendoscope

# 8. Setup Nginx
sudo cp deploy/nginx.conf /etc/nginx/sites-available/trendoscope
sudo ln -s /etc/nginx/sites-available/trendoscope /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Systemd Service

See `deploy/trendoscope.service` for service file.

**Commands:**

```bash
# Start
sudo systemctl start trendoscope

# Stop
sudo systemctl stop trendoscope

# Status
sudo systemctl status trendoscope

# Logs
sudo journalctl -u trendoscope -f
```

### Nginx Configuration

See `deploy/nginx.conf` for reverse proxy setup.

**Features:**
- SSL/TLS support
- Static file serving
- Load balancing ready
- Security headers

---

## ✅ Production Checklist

### Security

- [ ] Change default ports if needed
- [ ] Setup SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Use strong API keys
- [ ] Enable rate limiting
- [ ] Setup monitoring
- [ ] Regular backups

### Performance

- [ ] Enable Redis caching
- [ ] Database optimization
- [ ] CDN for static assets
- [ ] Load balancing (if needed)
- [ ] Monitoring setup

### Reliability

- [ ] Health check endpoint
- [ ] Auto-restart on failure
- [ ] Log rotation
- [ ] Error monitoring
- [ ] Backup strategy

### Monitoring

- [ ] Metrics endpoint
- [ ] Log aggregation
- [ ] Error tracking (Sentry)
- [ ] Uptime monitoring
- [ ] Performance monitoring

---

## 🔧 Configuration

### Environment Variables

```bash
# AI Providers
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...

# Database
DATABASE_URL=sqlite:///data/news.db

# Cache
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO

# Server
HOST=0.0.0.0
PORT=8003
```

### Production Settings

```bash
# Disable debug
DEBUG=false

# Set log level
LOG_LEVEL=WARNING

# Enable caching
REDIS_URL=redis://your-redis:6379/0

# Database
DATABASE_URL=postgresql://user:pass@host/db
```

---

## 📊 Monitoring

### Health Checks

```bash
# Check health
curl http://localhost:8003/health

# Check metrics
curl http://localhost:8003/metrics
```

### Logs

```bash
# Application logs
tail -f logs/app.log

# System logs (systemd)
sudo journalctl -u trendoscope -f

# Docker logs
docker-compose logs -f
```

---

## 🔄 Updates

### Updating Application

```bash
# Pull latest changes
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart trendoscope

# Or with Docker
docker-compose pull
docker-compose up -d
```

### Database Migrations

```bash
# Backup first
cp data/news.db data/news.db.backup

# Run migrations (if any)
python migrate.py
```

---

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use:**

```bash
# Find process
lsof -i :8003

# Kill process
kill -9 <PID>
```

**Import Errors:**

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Database Locked:**

```bash
# Check for other processes
ps aux | grep python

# Restart service
sudo systemctl restart trendoscope
```

**Memory Issues:**

```bash
# Check memory
free -h

# Increase swap if needed
sudo swapon --show
```

---

## 📞 Support

- **Documentation**: `/documents` folder
- **GitHub Issues**: Bug reports
- **Email**: support@trendoscope.ai

---

**Last Updated**: 2025-01-XX  
**Version**: 2.2.0

