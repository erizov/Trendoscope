# 🚀 Deployment Guide - Trendoscope

## Deployment Options

### 1. 🐳 Docker (Recommended)
### 2. ☁️ Railway
### 3. 🌐 Render
### 4. ✈️ Fly.io
### 5. 🔧 Manual VPS

---

## 1. 🐳 Docker Deployment

### Quick Start

```bash
# 1. Build and run
docker-compose up -d

# 2. Check logs
docker-compose logs -f

# 3. Stop
docker-compose down
```

### Configuration

Create `.env` file:
```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_API_BASE=https://api.proxyapi.ru/openai/v1
```

### Access
- **URL**: http://localhost:8003
- **Health check**: http://localhost:8003/docs

---

## 2. ☁️ Railway Deployment

Railway is a Platform-as-a-Service with automatic deployments.

### Steps:

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Initialize project**
   ```bash
   railway init
   ```

3. **Add environment variables**
   ```bash
   railway variables set OPENAI_API_KEY=sk-your-key
   railway variables set OPENAI_API_BASE=https://api.proxyapi.ru/openai/v1
   ```

4. **Deploy**
   ```bash
   railway up
   ```

### Configuration

See `deploy/railway.json` for Railway-specific config.

### Pricing
- **Free tier**: 500 hours/month, $5 credit
- **Starter**: $5/month

---

## 3. 🌐 Render Deployment

Render offers free tier for web services.

### Steps:

1. **Connect GitHub repo**
   - Go to https://render.com
   - New → Web Service
   - Connect GitHub repository

2. **Configure**
   - **Name**: trendoscope
   - **Region**: Choose closest
   - **Branch**: master
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python run.py`

3. **Environment Variables**
   ```
   OPENAI_API_KEY=sk-your-key
   OPENAI_API_BASE=https://api.proxyapi.ru/openai/v1
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (~5 minutes)

### Configuration

See `deploy/render.yaml` for infrastructure-as-code.

### Pricing
- **Free tier**: Yes (spins down after inactivity)
- **Starter**: $7/month (always on)

---

## 4. ✈️ Fly.io Deployment

Fly.io runs Docker containers globally.

### Steps:

1. **Install Fly CLI**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   fly auth login
   ```

3. **Launch app**
   ```bash
   fly launch
   # Answer prompts:
   # - App name: trendoscope
   # - Region: choose closest
   # - Database: No
   ```

4. **Set secrets**
   ```bash
   fly secrets set OPENAI_API_KEY=sk-your-key
   fly secrets set OPENAI_API_BASE=https://api.proxyapi.ru/openai/v1
   ```

5. **Deploy**
   ```bash
   fly deploy
   ```

### Configuration

See `deploy/fly.toml` for Fly.io config.

### Pricing
- **Free tier**: 3 shared VMs, 256MB RAM each
- **Paid**: ~$2/month for 1GB RAM

---

## 5. 🔧 Manual VPS Deployment

Deploy on your own VPS (DigitalOcean, AWS, etc.)

### Prerequisites

- Ubuntu 20.04+ or similar
- Root/sudo access
- Domain name (optional)

### Steps:

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip -y

# 3. Clone repository
git clone https://github.com/YOUR_USERNAME/trendoscope.git
cd trendoscope

# 4. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Configure environment
cp .env.example .env
nano .env  # Edit with your keys

# 7. Run with systemd (optional)
sudo cp deploy/trendoscope.service /etc/systemd/system/
sudo systemctl enable trendoscope
sudo systemctl start trendoscope

# 8. Setup Nginx reverse proxy (optional)
sudo apt install nginx -y
sudo cp deploy/nginx.conf /etc/nginx/sites-available/trendoscope
sudo ln -s /etc/nginx/sites-available/trendoscope /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### Systemd Service

See `deploy/trendoscope.service`

### Nginx Configuration

See `deploy/nginx.conf`

---

## 📊 Comparison Table

| Platform | Free Tier | Always On | Docker | RAM | Deploy Time | Best For |
|----------|-----------|-----------|--------|-----|-------------|----------|
| **Docker** | ✅ | ✅ | ✅ | Unlimited | 1 min | Local development |
| **Railway** | $5 credit | ✅ | ✅ | 512 MB | 2 min | Quick start |
| **Render** | ✅ | ❌ | ✅ | 512 MB | 5 min | Free hosting |
| **Fly.io** | ✅ | ✅ | ✅ | 256 MB | 3 min | Global CDN |
| **VPS** | ❌ | ✅ | ✅ | Custom | 10 min | Full control |

---

## 🔐 Security Considerations

### Environment Variables

**Never commit these**:
- `OPENAI_API_KEY`
- `OPENAI_API_BASE`
- Database credentials
- Secret keys

### Best Practices

1. **Use secrets management**
   - Railway: `railway variables`
   - Render: Environment Variables tab
   - Fly.io: `fly secrets`
   - Docker: `.env` file (gitignored)

2. **Enable HTTPS**
   - Railway/Render/Fly: Automatic
   - VPS: Use Let's Encrypt + Nginx

3. **Rate limiting**
   - Consider adding rate limiting middleware
   - Use API key quotas

4. **Monitoring**
   - Enable health checks
   - Set up logging
   - Monitor API usage

---

## 🚀 Recommended Deployment

### For Development
**Docker** - Easy, fast, consistent

```bash
docker-compose up -d
```

### For Production (Free)
**Fly.io** - Always on, good free tier, global

```bash
fly launch
fly deploy
```

### For Production (Paid)
**Railway** - Simple, reliable, good support

```bash
railway up
```

### For Custom Requirements
**VPS** - Full control, customizable

---

## 🐛 Troubleshooting

### Container won't start
```bash
docker-compose logs
# Check for missing dependencies or env vars
```

### Port already in use
```bash
# Change port in docker-compose.yml:
ports:
  - "8004:8003"  # Use 8004 instead
```

### Memory issues
- Reduce RAG size
- Use smaller model
- Increase container memory limit

### API key errors
```bash
# Verify environment variables
docker-compose exec trendoscope env | grep OPENAI
```

---

## 📞 Support

- **Documentation**: See `/documents` folder
- **Issues**: Check logs first
- **Railway**: https://railway.app/help
- **Render**: https://render.com/docs
- **Fly.io**: https://fly.io/docs

---

## ✅ Deployment Checklist

- [ ] Environment variables set
- [ ] Database/RAG data backed up
- [ ] Health checks configured
- [ ] Logging enabled
- [ ] HTTPS configured
- [ ] Domain name (if needed)
- [ ] Monitoring setup
- [ ] Backup strategy
- [ ] Scaling plan
- [ ] Security review

---

**Ready to deploy!** Choose your platform and follow the guide above. 🚀

**Date**: 2025-11-13  
**Version**: 2.1.0  
**Status**: Production Ready ✅

