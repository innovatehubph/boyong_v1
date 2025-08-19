#!/bin/bash

# Pareng Boyong - Enhanced One-Click Installation Script
# Incorporates ALL fixes and improvements discovered during testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Functions
log() { echo -e "${BLUE}[INFO]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
header() { echo -e "${PURPLE}[PARENG BOYONG]${NC} $1"; }

# Configuration
REPO_URL="https://github.com/innovatehubph/boyong_v1.git"
INSTALL_DIR="/opt/pareng-boyong"
PYTHON_MIN_VERSION="3.8"
NODE_MIN_VERSION="18"
SERVICE_NAME="pareng-boyong"
LOG_FILE="/tmp/pareng-boyong-install.log"

# Create log file
exec > >(tee -a "$LOG_FILE")
exec 2>&1

header "🚀 Pareng Boyong Enhanced Installation System"
echo "======================================================"
log "📋 Installation log: $LOG_FILE"
log "📅 Started: $(date)"

# System Detection
detect_system() {
    log "🔍 Detecting system..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            PACKAGE_MANAGER="apt"
            DISTRO="debian"
        elif command -v yum &> /dev/null; then
            PACKAGE_MANAGER="yum"
            DISTRO="redhat"
        elif command -v pacman &> /dev/null; then
            PACKAGE_MANAGER="pacman"
            DISTRO="arch"
        else
            error "Unsupported Linux distribution"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        PACKAGE_MANAGER="brew"
        DISTRO="macos"
    else
        error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    success "System: $DISTRO with $PACKAGE_MANAGER"
}

# Python Version Detection and Compatibility
check_python() {
    log "🐍 Checking Python installation..."
    
    # Find Python executable
    for python_cmd in python3.12 python3.11 python3.10 python3.9 python3.8 python3 python; do
        if command -v "$python_cmd" &> /dev/null; then
            PYTHON_CMD="$python_cmd"
            break
        fi
    done
    
    if [[ -z "$PYTHON_CMD" ]]; then
        error "Python not found. Installing Python..."
        install_python
    fi
    
    # Get Python version
    PYTHON_VERSION=$($PYTHON_CMD --version | grep -oP '\\d+\\.\\d+\\.\\d+')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    log "Found Python $PYTHON_VERSION at $PYTHON_CMD"
    
    # Check version compatibility
    if (( PYTHON_MAJOR < 3 || (PYTHON_MAJOR == 3 && PYTHON_MINOR < 8) )); then
        error "Python $PYTHON_VERSION is too old. Minimum required: 3.8"
        exit 1
    elif (( PYTHON_MAJOR == 3 && PYTHON_MINOR >= 13 )); then
        warn "Python 3.13+ detected - will apply compatibility fixes"
        PYTHON_NEEDS_COMPAT=true
    else
        success "Python $PYTHON_VERSION is compatible"
        PYTHON_NEEDS_COMPAT=false
    fi
}

# Install Python if needed
install_python() {
    log "📦 Installing Python..."
    
    case $PACKAGE_MANAGER in
        apt)
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv python3-dev
            PYTHON_CMD="python3"
            ;;
        yum)
            sudo yum install -y python3 python3-pip python3-devel
            PYTHON_CMD="python3"
            ;;
        brew)
            brew install python@3.12
            PYTHON_CMD="python3.12"
            ;;
        *)
            error "Cannot install Python automatically for $PACKAGE_MANAGER"
            exit 1
            ;;
    esac
}

# Install system dependencies
install_system_deps() {
    log "📦 Installing system dependencies..."
    
    case $PACKAGE_MANAGER in
        apt)
            sudo apt-get update
            sudo apt-get install -y \\
                git curl wget unzip \\
                build-essential \\
                libffi-dev libssl-dev \\
                docker.io docker-compose \\
                nginx \\
                redis-server \\
                ffmpeg \\
                tesseract-ocr \\
                poppler-utils
            ;;
        yum)
            sudo yum groupinstall -y "Development Tools"
            sudo yum install -y \\
                git curl wget unzip \\
                openssl-devel libffi-devel \\
                docker docker-compose \\
                nginx \\
                redis \\
                ffmpeg \\
                tesseract \\
                poppler-utils
            ;;
        brew)
            brew install \\
                git curl wget \\
                docker docker-compose \\
                redis \\
                ffmpeg \\
                tesseract \\
                poppler
            ;;
    esac
    
    success "System dependencies installed"
}

# Install Node.js
install_nodejs() {
    log "📦 Installing Node.js..."
    
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | grep -oP '\\d+\\.\\d+\\.\\d+')
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
        
        if (( NODE_MAJOR >= 18 )); then
            success "Node.js $NODE_VERSION is already installed"
            return
        fi
    fi
    
    # Install Node.js using NodeSource repository
    case $DISTRO in
        debian)
            curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
            sudo apt-get install -y nodejs
            ;;
        redhat)
            curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
            sudo yum install -y nodejs
            ;;
        macos)
            brew install node
            ;;
    esac
    
    success "Node.js installed"
}

# Clone or update repository
setup_repository() {
    log "📁 Setting up repository..."
    
    if [[ -d "$INSTALL_DIR" ]]; then
        log "Repository exists, updating..."
        cd "$INSTALL_DIR"
        git pull origin main
    else
        log "Cloning repository..."
        sudo git clone "$REPO_URL" "$INSTALL_DIR"
        sudo chown -R $USER:$USER "$INSTALL_DIR"
    fi
    
    cd "$INSTALL_DIR"
    success "Repository ready at $INSTALL_DIR"
}

# Create Python virtual environment
setup_venv() {
    log "🐍 Setting up Python virtual environment..."
    
    if [[ ! -d "venv" ]]; then
        $PYTHON_CMD -m venv venv
    fi
    
    source venv/bin/activate
    
    # Upgrade pip and essential tools
    pip install --upgrade pip setuptools wheel
    
    success "Virtual environment ready"
}

# Install Python dependencies with compatibility fixes
install_python_deps() {
    log "📦 Installing Python dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Determine requirements file based on Python version
    if [[ "$PYTHON_NEEDS_COMPAT" == true ]]; then
        PYTHON_SHORT_VERSION="$PYTHON_MAJOR.$PYTHON_MINOR"
        REQ_FILE="config/settings/requirements-py$PYTHON_SHORT_VERSION.txt"
        
        if [[ ! -f "$REQ_FILE" ]]; then
            warn "Creating compatible requirements for Python $PYTHON_SHORT_VERSION..."
            $PYTHON_CMD scripts/setup/validate_dependencies.py --fix
        fi
    else
        REQ_FILE="config/settings/requirements.txt"
    fi
    
    log "Using requirements file: $REQ_FILE"
    
    # Install with retry logic
    MAX_RETRIES=3
    for i in $(seq 1 $MAX_RETRIES); do
        log "Installation attempt $i/$MAX_RETRIES..."
        
        if pip install -r "$REQ_FILE" --timeout=300; then
            success "Python dependencies installed"
            break
        else
            warn "Installation attempt $i failed"
            if [[ $i -eq $MAX_RETRIES ]]; then
                error "All installation attempts failed"
                exit 1
            fi
            sleep 5
        fi
    done
    
    # Install additional discovered dependencies
    log "Installing additional dependencies..."
    pip install crontab inputimeout flaredantic requests openai
    
    success "All Python dependencies installed"
}

# Install Node.js dependencies
install_node_deps() {
    log "📦 Installing Node.js dependencies..."
    
    if [[ -f "webui/package.json" ]]; then
        cd webui
        npm ci --production
        cd ..
        success "Node.js dependencies installed"
    else
        log "No Node.js dependencies found"
    fi
}

# Set up configuration
setup_config() {
    log "⚙️ Setting up configuration..."
    
    # Create config directories
    mkdir -p config/{env,mcp,update,multimedia}
    mkdir -p logs backups temp_update
    mkdir -p pareng_boyong_deliverables/{images,videos,audio}
    
    # Generate default configuration if not exists
    if [[ ! -f "config/env/.env" ]]; then
        cat > config/env/.env << EOF
# Pareng Boyong Configuration
PARENG_BOYONG_ENV=production
LOG_LEVEL=INFO
AUTO_UPDATE_ENABLED=true

# API Keys (set your actual keys)
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here

# Services
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite:///pareng_boyong.db

# Web UI
HOST=0.0.0.0
PORT=8080
DEBUG=false
EOF
        warn "Default configuration created at config/env/.env"
        warn "Please edit config/env/.env with your actual API keys"
    fi
    
    success "Configuration ready"
}

# Set up services
setup_services() {
    log "🐳 Setting up services..."
    
    # Enable and start Docker
    if command -v systemctl &> /dev/null; then
        sudo systemctl enable docker
        sudo systemctl start docker
        sudo usermod -aG docker $USER
    fi
    
    # Start Redis
    if command -v systemctl &> /dev/null; then
        sudo systemctl enable redis-server
        sudo systemctl start redis-server
    elif command -v brew &> /dev/null; then
        brew services start redis
    fi
    
    success "Services configured"
}

# Run validation tests
run_validation() {
    log "🧪 Running installation validation..."
    
    source venv/bin/activate
    
    # Run dependency validation
    $PYTHON_CMD scripts/setup/validate_dependencies.py
    
    # Run installation test
    if [[ -f "scripts/test/test_installation.py" ]]; then
        $PYTHON_CMD scripts/test/test_installation.py
    fi
    
    success "Validation completed"
}

# Create systemd service
create_service() {
    log "🔧 Creating system service..."
    
    if command -v systemctl &> /dev/null; then
        sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=Pareng Boyong AI Assistant
After=network.target redis.service
Wants=redis.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python run_ui.py --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable $SERVICE_NAME
        
        success "System service created: $SERVICE_NAME"
    else
        log "Systemd not available, skipping service creation"
    fi
}

# Set up auto-updates
setup_auto_updates() {
    log "🔄 Setting up automatic updates..."
    
    # Create cron job for auto-updates
    if command -v crontab &> /dev/null; then
        (crontab -l 2>/dev/null || true; echo "0 2 * * * cd $INSTALL_DIR && python scripts/update/auto_update_agent_zero.py --auto") | crontab -
        success "Auto-updates scheduled for 2 AM daily"
    fi
}

# Final setup and start
final_setup() {
    log "🎉 Finalizing installation..."
    
    # Set permissions
    sudo chown -R $USER:$USER "$INSTALL_DIR"
    chmod +x scripts/setup/*.sh
    chmod +x scripts/update/*.py
    chmod +x scripts/test/*.py
    
    # Create desktop shortcut (if GUI available)
    if [[ -n "$DISPLAY" ]] && [[ -d "$HOME/Desktop" ]]; then
        cat > "$HOME/Desktop/Pareng Boyong.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Pareng Boyong
Comment=Advanced AI Assistant
Exec=$INSTALL_DIR/venv/bin/python $INSTALL_DIR/run_ui.py
Icon=$INSTALL_DIR/webui/public/pareng-boyong-favicon.png
Terminal=false
StartupNotify=true
Categories=Development;Office;
EOF
        chmod +x "$HOME/Desktop/Pareng Boyong.desktop"
    fi
    
    success "Installation completed successfully!"
}

# Usage information
show_usage() {
    header "📋 Pareng Boyong Usage Information"
    echo ""
    log "🚀 Start Pareng Boyong:"
    echo "   sudo systemctl start $SERVICE_NAME"
    echo "   OR"
    echo "   cd $INSTALL_DIR && source venv/bin/activate && python run_ui.py"
    echo ""
    log "🌐 Access Web Interface:"
    echo "   http://localhost:8080"
    echo ""
    log "🔧 Manage Service:"
    echo "   sudo systemctl {start|stop|restart|status} $SERVICE_NAME"
    echo ""
    log "📋 View Logs:"
    echo "   sudo journalctl -u $SERVICE_NAME -f"
    echo ""
    log "🔄 Manual Update:"
    echo "   cd $INSTALL_DIR && python scripts/update/auto_update_agent_zero.py"
    echo ""
    log "🧪 Test Installation:"
    echo "   cd $INSTALL_DIR && python scripts/test/test_installation.py"
    echo ""
    log "📖 Configuration:"
    echo "   Edit $INSTALL_DIR/config/env/.env"
}

# Main installation process
main() {
    header "Starting Enhanced Installation Process"
    
    detect_system
    check_python
    install_system_deps
    install_nodejs
    setup_repository
    setup_venv
    install_python_deps
    install_node_deps
    setup_config
    setup_services
    run_validation
    create_service
    setup_auto_updates
    final_setup
    
    echo ""
    success "🎉 Pareng Boyong installation completed successfully!"
    echo ""
    show_usage
    echo ""
    header "Installation log saved to: $LOG_FILE"
    log "📅 Completed: $(date)"
}

# Error handling
trap 'error "Installation failed at line $LINENO. Check $LOG_FILE for details."; exit 1' ERR

# Check if running as root
if [[ $EUID -eq 0 ]]; then
    error "Please do not run this script as root"
    error "Run as a regular user with sudo privileges"
    exit 1
fi

# Check for required commands
for cmd in git curl wget; do
    if ! command -v $cmd &> /dev/null; then
        error "$cmd is required but not installed"
        exit 1
    fi
done

# Run main installation
main "$@"