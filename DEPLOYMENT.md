# 🚀 OmniAgent AI - Production Deployment Guide

Iss document me **OmniAgent AI Multi-Agent Platform** ko local machine, VPS (DigitalOcean/AWS EC2), Docker, ya Cloud Platforms (Render / Railway) par deploy karne ke complete step-by-step instructions diye gaye hain.

---

## 📁 Created Deployment Files

1. [`Dockerfile`](file:///c:/Users/mspaw/Downloads/ITR/Final%20project/Multi/Dockerfile) - Production multi-stage Docker build container.
2. [`docker-compose.yml`](file:///c:/Users/mspaw/Downloads/ITR/Final%20project/Multi/docker-compose.yml) - Docker Compose container orchestrator.
3. [`Procfile`](file:///c:/Users/mspaw/Downloads/ITR/Final%20project/Multi/Procfile) - Render / Railway / Heroku process runner.
4. [`render.yaml`](file:///c:/Users/mspaw/Downloads/ITR/Final%20project/Multi/render.yaml) - Render.com Cloud Infrastructure blueprint.
5. [`nginx.conf`](file:///c:/Users/mspaw/Downloads/ITR/Final%20project/Multi/nginx.conf) - Nginx reverse proxy configuration for Linux VPS.
6. [`.env.example`](file:///c:/Users/mspaw/Downloads/ITR/Final%20project/Multi/.env.example) - Production environment variables template.

---

## Option 1: Docker Compose Deployment (Recommended for Local / VPS)

Sabse simple tarika poori application ko single command se deploy karne ka:

```bash
# 1. Build and run containers in background
docker compose up --build -d

# 2. Check container status
docker compose ps

# 3. View live logs
docker compose logs -f
```

Application URL: `http://localhost:8000` ya `http://YOUR_SERVER_IP:8000`

---

## Option 2: Render.com Cloud Deployment (Free Cloud Hosting)

1. Apne GitHub repository ko Render.com se connect karein.
2. **New Web Service** select karein.
3. Configuration set karein:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`
4. **Environment Variables** add karein:
   - `ENVIRONMENT` = `production`
   - `SECRET_KEY` = `YOUR_PRODUCTION_SECRET_KEY`
5. Click **Deploy Web Service**!

---

## Option 3: VPS Linux Server Deployment (DigitalOcean / AWS EC2 / Hetzner)

```bash
# 1. Server updates & install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv nginx git tesseract-ocr

# 2. Clone Repository
git clone <YOUR_GIT_REPO_URL> /var/www/omniagent
cd /var/www/omniagent

# 3. Create virtualenv and install requirements
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Systemd Background Service Setup
sudo nano /etc/systemd/system/omniagent.service
```

Paste systemd config:
```ini
[Unit]
Description=OmniAgent AI FastAPI Production Server
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/omniagent
ExecStart=/var/www/omniagent/venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable & start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable omniagent
sudo systemctl start omniagent
```

Configure Nginx reverse proxy:
```bash
sudo cp nginx.conf /etc/nginx/sites-available/omniagent
sudo ln -s /etc/nginx/sites-available/omniagent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 🎯 Verification Checklist

- [x] FastAPI REST Endpoints (`/api/v1`)
- [x] ChromaDB Vector Database Persistence (`./backend/chroma_db`)
- [x] Local Ollama Connection (`http://localhost:11434`)
- [x] Pure HTML, CSS, JS Single Page App Frontend
