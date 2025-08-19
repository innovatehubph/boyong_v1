#!/bin/bash

# Pareng Boyong - Quick Installation Script
# Automated installation for Ubuntu/Debian systems

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log() { echo -e "${BLUE}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

# Configuration
REPO_URL="https://github.com/your-username/pareng-boyong.git"
INSTALL_DIR="/opt/pareng-boyong"
PYTHON_VERSION="3.11"
NODE_VERSION="18"

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   warn "This script should not be run as root for security reasons"
   warn "Please run as a regular user with sudo privileges"
   exit 1
fi

log "🚀 Starting Pareng Boyong installation..."

# System check
log "📋 Checking system requirements..."
if ! command -v sudo &> /dev/null; then
    error "sudo is required but not installed"
    exit 1
fi

# Check OS
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    error "This script only supports Linux systems"
    exit 1
fi

# Update system
log "⏫ Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install essential packages
log "📦 Installing essential packages..."
sudo apt install -y curl wget git software-properties-common apt-transport-https ca-certificates gnupg lsb-release

# Install Python 3.11
log "🐍 Installing Python ${PYTHON_VERSION}..."
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-pip python${PYTHON_VERSION}-venv python${PYTHON_VERSION}-dev

# Install Node.js
log "📦 Installing Node.js ${NODE_VERSION}..."
curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install Docker
log "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
else
    log "Docker already installed"
fi

# Install Docker Compose
log "🔧 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
else
    log "Docker Compose already installed"
fi

# Create installation directory
log "📁 Creating installation directory..."
if [[ -d "$INSTALL_DIR" ]]; then
    warn "Installation directory exists. Backing up..."
    sudo mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%s)"
fi

# Clone repository
log "📥 Cloning Pareng Boyong repository..."
sudo git clone "$REPO_URL" "$INSTALL_DIR"
sudo chown -R $USER:$USER "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Create virtual environment
log "🐍 Creating Python virtual environment..."
python${PYTHON_VERSION} -m venv venv
source venv/bin/activate

# Install Python dependencies
log "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r config/settings/requirements.txt

# Install Node.js dependencies
log "📦 Installing Node.js dependencies..."
cd webui
npm install
cd ..

# Setup environment file
log "⚙️ Setting up environment configuration..."
if [[ ! -f .env ]]; then
    cp config/env/.env.example .env
    warn "Please edit .env file with your API keys before starting services"
    warn "Required: OPENROUTER_API_KEY, ANTHROPIC_API_KEY"
    warn "Optional: ELEVENLABS_API_KEY, OPENAI_API_KEY"
fi

# Initialize system
log "🔧 Initializing system..."
python initialize.py --setup 2>/dev/null || true

# Setup systemd service (optional)
if [[ "$1" == "--service" ]]; then
    log "🔧 Setting up systemd service..."
    sudo tee /etc/systemd/system/pareng-boyong.service << EOF
[Unit]
Description=Pareng Boyong AI Assistant
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python run_ui.py --port=8080 --host=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable pareng-boyong
fi

# Setup Nginx (optional)
if [[ "$1" == "--nginx" ]] || [[ "$2" == "--nginx" ]]; then
    log "🌐 Setting up Nginx reverse proxy..."
    sudo apt install -y nginx
    
    sudo tee /etc/nginx/sites-available/pareng-boyong << EOF
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_buffering off;
    }

    location /ws {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/pareng-boyong /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t && sudo systemctl reload nginx
fi

# Create desktop shortcut (optional)
if command -v desktop-file-install &> /dev/null; then
    log "🖥️ Creating desktop shortcut..."
    cat > ~/.local/share/applications/pareng-boyong.desktop << EOF
[Desktop Entry]
Name=Pareng Boyong
Comment=Advanced AI Assistant
Exec=xdg-open http://localhost:8080
Icon=applications-internet
Type=Application
Categories=Network;Office;
StartupNotify=true
EOF
fi

success "🎉 Installation completed successfully!"
echo
log "📋 Next steps:"
echo "  1. Edit the configuration file: nano $INSTALL_DIR/.env"
echo "  2. Add your API keys (OPENROUTER_API_KEY, ANTHROPIC_API_KEY, etc.)"
echo "  3. Start the services:"
echo
echo "     # Docker method (recommended):"
echo "     cd $INSTALL_DIR && docker-compose up -d"
echo
echo "     # Manual method:"
echo "     cd $INSTALL_DIR && source venv/bin/activate && python run_ui.py"
echo
echo "     # Systemd service method (if installed):"
echo "     sudo systemctl start pareng-boyong"
echo
log "🌐 Access your Pareng Boyong instance at:"
if [[ "$1" == "--nginx" ]] || [[ "$2" == "--nginx" ]]; then
    echo "     http://your-server-ip/"
else
    echo "     http://localhost:8080/"
fi
echo
warn "⚠️ Important: Don't forget to configure your API keys in .env file!"
success "Happy AI chatting! 🤖"