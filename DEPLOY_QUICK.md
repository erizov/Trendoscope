# 🚀 Quick Deployment Guide

## Choose Your Platform

### 🐳 Docker (1 minute - Local/Any Server)

```bash
docker-compose up -d
```
**Done!** → http://localhost:8003

---

### ☁️ Railway (2 minutes - Cloud)

```bash
# 1. Install CLI
npm install -g @railway/cli

# 2. Login & deploy
railway login
railway up

# 3. Set environment variables
railway variables set OPENAI_API_KEY=sk-your-key
```
**Cost**: $5 credit/month (free trial)

---

### ✈️ Fly.io (3 minutes - Cloud, RECOMMENDED)

```bash
# 1. Install CLI (Windows PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# 2. Login
fly auth login

# 3. Launch app
fly launch
# Choose: app name, region, no database

# 4. Set secrets
fly secrets set OPENAI_API_KEY=sk-your-key
fly secrets set OPENAI_API_BASE=https://api.proxyapi.ru/openai/v1

# 5. Deploy
fly deploy
```
**Cost**: FREE (3 VMs, 256MB each)  
**Best Choice!** ✅

---

### 🌐 Render (5 minutes - Cloud)

```bash
# 1. Go to https://render.com
# 2. New → Web Service
# 3. Connect GitHub repository
# 4. Configure:
#    - Build: pip install -r requirements.txt
#    - Start: python run.py
# 5. Add Environment Variables:
#    - OPENAI_API_KEY
#    - OPENAI_API_BASE
# 6. Click "Create Web Service"
```
**Cost**: FREE (with spin-down)

---

## My Recommendation 🏆

**For Production**: Use **Fly.io**
- ✅ Free forever (3 VMs)
- ✅ Always on (no spin-down)
- ✅ Global CDN
- ✅ Easy CLI
- ✅ 256MB RAM per VM

```bash
fly launch && fly deploy
```

**For Development**: Use **Docker**
- ✅ Instant start
- ✅ Consistent environment
- ✅ Easy debugging

```bash
docker-compose up -d
```

---

## Need More Info?

See **[deploy/README.md](deploy/README.md)** for:
- VPS deployment (systemd + nginx)
- Security configuration
- Scaling strategies
- Troubleshooting

---

**Date**: 2025-11-13  
**Version**: 2.1.0

