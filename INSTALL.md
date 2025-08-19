# 📦 Pareng Boyong Installation Guide

## 🚀 **One-Command Installation**

```bash
curl -fsSL https://raw.githubusercontent.com/your-repo/pareng-boyong/main/scripts/setup/quick_install.sh | bash
```

## 📋 **Step-by-Step Installation**

### **1. System Preparation**

#### **Update System**
```bash
sudo apt update && sudo apt upgrade -y
```

#### **Install Dependencies**
```bash
# Essential packages
sudo apt install -y git curl wget python3.11 python3.11-pip python3.11-venv nodejs npm docker.io docker-compose

# GPU support (optional)
sudo apt install -y nvidia-docker2
```

### **2. Repository Setup**

#### **Clone Repository**
```bash
git clone <your-github-repo-url>
cd pareng-boyong
```

#### **Make Scripts Executable**
```bash
chmod +x scripts/**/*.sh
```

### **3. Environment Configuration**

#### **Create Environment File**
```bash
cp config/env/.env.example .env
```

#### **Configure API Keys** (Edit `.env` file)
```env
# Required - Chat Models
OPENROUTER_API_KEY=sk-or-v1-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here

# Optional - Multimedia
ELEVENLABS_API_KEY=sk-your-elevenlabs-key
OPENAI_API_KEY=sk-your-openai-key

# Database (optional)
DATABASE_URL=sqlite:///pareng_boyong.db
```

### **4. Dependencies Installation**

#### **Python Dependencies**
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python packages
pip install -r config/settings/requirements.txt
```

#### **Node.js Dependencies** 
```bash
# Install WebUI dependencies
cd webui
npm install
cd ..
```

### **5. System Initialize**

#### **Run Setup Script**
```bash
python scripts/setup/initialize_system.py
```

#### **Setup Services**
```bash
# Setup multimodal services
python scripts/setup/setup_multimedia.py

# Setup TTS services
python scripts/setup/setup_tts.py

# Setup local AI models (optional)
python scripts/setup/setup_local_models.py
```

### **6. Start Services**

#### **Docker Method (Recommended)**
```bash
docker-compose up -d
```

#### **Manual Method**
```bash
# Start in background
python run_ui.py --port=80 --host=0.0.0.0 --daemonize

# Or start in foreground
python run_ui.py --port=80 --host=0.0.0.0
```

### **7. Verification**

#### **Check Services**
```bash
# Check web interface
curl -I http://localhost:80

# Check API endpoint
curl http://localhost:80/api/health

# Check system status
python scripts/maintenance/system_check.py
```

---

## 🔧 **Advanced Installation Options**

### **Custom Installation Directory**
```bash
git clone <repo-url> /opt/pareng-boyong
cd /opt/pareng-boyong
# Continue with installation steps
```

### **Production Installation**
```bash
# Use production configuration
cp config/env/.env.production .env

# Install with production optimizations
python scripts/deployment/production_install.py

# Setup systemd service
sudo python scripts/deployment/setup_systemd.py
```

### **Development Installation**
```bash
# Install development dependencies
pip install -r config/settings/requirements-dev.txt

# Setup pre-commit hooks
pre-commit install

# Start in development mode
python run_ui.py --debug --reload
```

---

## 🐳 **Docker Installation**

### **Docker Compose (Easiest)**
```bash
# Clone repository
git clone <repo-url>
cd pareng-boyong

# Configure environment
cp config/env/.env.example .env
# Edit .env with your API keys

# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

### **Manual Docker**
```bash
# Build image
docker build -t pareng-boyong .

# Run container
docker run -d \
  --name pareng-boyong \
  -p 80:80 \
  -e OPENROUTER_API_KEY=your_key \
  -v $(pwd):/app \
  pareng-boyong
```

---

## 🌐 **Web Server Installation**

### **Nginx Reverse Proxy**
```bash
# Install Nginx
sudo apt install nginx

# Configure virtual host
sudo tee /etc/nginx/sites-available/pareng-boyong << EOF
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/pareng-boyong /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### **SSL Certificate (Let's Encrypt)**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

---

## 🎯 **Service Configuration**

### **Systemd Service**
```bash
# Create service file
sudo tee /etc/systemd/system/pareng-boyong.service << EOF
[Unit]
Description=Pareng Boyong AI Assistant
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/pareng-boyong
Environment=PATH=/opt/pareng-boyong/venv/bin
ExecStart=/opt/pareng-boyong/venv/bin/python run_ui.py --port=8080 --host=0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable pareng-boyong
sudo systemctl start pareng-boyong
sudo systemctl status pareng-boyong
```

### **Log Configuration**
```bash
# Configure log rotation
sudo tee /etc/logrotate.d/pareng-boyong << EOF
/var/log/pareng-boyong/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        systemctl reload pareng-boyong
    endscript
}
EOF
```

---

## 🔍 **Installation Verification**

### **System Check Script**
```bash
python scripts/maintenance/installation_check.py
```

### **Manual Verification**
```bash
# Check Python environment
python --version
pip list | grep -E "(torch|transformers|flask)"

# Check Node.js environment
node --version
npm list | grep -E "(react|next)"

# Check services
curl -s http://localhost:80/api/health | jq

# Check GPU (if available)
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
```

---

## ❗ **Troubleshooting Common Issues**

### **Permission Denied**
```bash
# Fix ownership
sudo chown -R $(whoami):$(whoami) /opt/pareng-boyong

# Fix permissions
chmod +x scripts/**/*.sh
```

### **Port Already in Use**
```bash
# Find process using port
sudo lsof -i :80
sudo fuser -k 80/tcp

# Or use different port
python run_ui.py --port=8080
```

### **Out of Memory**
```bash
# Increase swap
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Add to /etc/fstab for persistence
echo '/swapfile swap swap defaults 0 0' | sudo tee -a /etc/fstab
```

### **API Key Issues**
```bash
# Test API keys
python scripts/setup/test_api_keys.py

# Verify environment variables
echo $OPENROUTER_API_KEY
```

### **Docker Issues**
```bash
# Check Docker status
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Clean Docker cache
docker system prune -a
```

---

## 📞 **Getting Help**

If you encounter issues:

1. **Check logs**: `tail -f data/logs/latest.log`
2. **Run diagnostics**: `python scripts/maintenance/diagnose.py`
3. **Check documentation**: [docs/](docs/)
4. **Open an issue**: [GitHub Issues](https://github.com/your-repo/issues)

---

**Installation complete! 🎉**

Access your Pareng Boyong instance at: http://localhost:80