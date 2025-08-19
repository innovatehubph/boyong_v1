# 🤖 Pareng Boyong - Advanced Multimodal AI Assistant

## 🌟 **Complete AI Assistant with Multimedia Generation**

Pareng Boyong is a comprehensive multimodal AI assistant that combines chat capabilities, multimedia generation (images, videos, music, voice), and advanced automation features.

### ✨ **Key Features**

- 🧠 **Advanced AI Chat** - Multiple LLM providers (OpenAI, Anthropic, Local models)
- 🎨 **Image Generation** - FLUX.1, Stable Diffusion, Pollinations.AI
- 🎬 **Video Generation** - 4 cutting-edge models (Wan2.1-VACE-14B, FusioniX, MultiTalk, Wan2GP)
- 🎵 **Music Generation** - AudioCraft, MusicGen 
- 🎤 **Voice Synthesis** - ElevenLabs, Kokoro TTS, ToucanTTS (Filipino)
- 📁 **File Management** - Complete VPS file system access
- 🔧 **Automation** - Code execution, web browsing, API integrations
- 🌐 **Web Interface** - Modern responsive UI with mobile support

---

## 🚀 **Quick Start Installation**

### **Prerequisites**
- Linux VPS with 16GB+ RAM
- Docker and Docker Compose
- 50GB+ available storage
- CUDA-capable GPU (recommended)

### **1. Clone Repository**
```bash
git clone <your-github-repo-url>
cd pareng-boyong
```

### **2. Environment Setup**
```bash
# Copy environment template
cp config/env/.env.example .env

# Edit with your API keys and configurations
nano .env
```

### **3. Required API Keys**
Add these to your `.env` file:
```env
# Required - Chat Models
OPENROUTER_API_KEY=your_openrouter_key
ANTHROPIC_API_KEY=your_anthropic_key

# Optional - Enhanced Features  
ELEVENLABS_API_KEY=your_elevenlabs_key
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key
```

### **4. Install Dependencies**
```bash
# Install Python dependencies
pip install -r config/settings/requirements.txt

# Install Node.js dependencies (for WebUI)
cd webui && npm install && cd ..
```

### **5. Initialize System**
```bash
# Initialize Pareng Boyong
python initialize.py --setup

# Prepare environment
python prepare.py
```

### **6. Start Services**
```bash
# Start all services with Docker
docker-compose up -d

# Or run locally
python run_ui.py --port=80 --host=0.0.0.0
```

### **7. Access Interface**
- **Web Interface**: http://localhost:80
- **API**: http://localhost:80/api/

---

## 📋 **Detailed Installation Guide**

### **System Requirements**

#### **Minimum Requirements**
- OS: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- CPU: 4+ cores
- RAM: 16GB
- Storage: 50GB
- Network: Stable internet connection

#### **Recommended Requirements**
- CPU: 8+ cores
- RAM: 32GB+ 
- Storage: 100GB+ NVMe SSD
- GPU: NVIDIA RTX 3060+ with 12GB VRAM
- Network: High-speed connection (for model downloads)

### **Docker Installation (Recommended)**

#### **1. Install Docker & Docker Compose**
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### **2. Configure Docker**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Enable Docker service
sudo systemctl enable docker
sudo systemctl start docker
```

#### **3. Deploy with Docker**
```bash
# Clone repository
git clone <repo-url>
cd pareng-boyong

# Configure environment
cp config/env/.env.example .env
# Edit .env with your configurations

# Start all services
docker-compose -f config/docker/docker-compose.yml up -d
```

### **Manual Installation**

#### **1. Python Environment**
```bash
# Install Python 3.11+
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r config/settings/requirements.txt
```

#### **2. Node.js for Web UI**
```bash
# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install WebUI dependencies
cd webui
npm install
cd ..
```

#### **3. Optional: GPU Support**
```bash
# Install CUDA (for GPU acceleration)
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda

# Install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### **4. Start Services**
```bash
# Initialize system
python initialize.py

# Start web interface
python run_ui.py --port=80 --host=0.0.0.0

# Or start CLI
python run_cli.py
```

---

## ⚙️ **Configuration**

### **Environment Variables**

#### **Core Configuration**
```env
# Chat Models
CHAT_MODEL_PROVIDER=OPENROUTER
CHAT_MODEL_NAME=anthropic/claude-3.5-sonnet
OPENROUTER_API_KEY=your_key

# TTS Configuration
TTS_PROVIDER=elevenlabs
TTS_ELEVENLABS_ENABLE=true
ELEVENLABS_API_KEY=your_key

# Multimedia Services
ENABLE_IMAGE_GENERATION=true
ENABLE_VIDEO_GENERATION=true
ENABLE_MUSIC_GENERATION=true
```

#### **Advanced Configuration**
```env
# Performance
MAX_CONTEXT_LENGTH=100000
CONCURRENT_REQUESTS=4
CACHE_SIZE=1000

# Security  
AUTH_ENABLED=false
CORS_ORIGINS=*
```

### **Model Configuration**

#### **Default Models** (config/models.yaml)
```yaml
chat_models:
  primary: anthropic/claude-3.5-sonnet
  fallback: openai/gpt-4o-mini
  local: llama3.1:70b

image_models:
  primary: flux.1-schnell
  fallback: stable-diffusion-xl

video_models:
  high_quality: wan2.1-vace-14b
  fast: fusionix
  conversations: multitalk
  accessible: wan2gp
```

---

## 🎨 **Features & Usage**

### **Chat Interface**
- **Web UI**: Modern chat interface with file uploads
- **API**: RESTful API for programmatic access
- **CLI**: Command-line interface for automation

### **Multimedia Generation**

#### **Image Generation**
```bash
# Via web interface
"Create a professional headshot of a businesswoman"

# Via API
curl -X POST http://localhost/api/image_generator \
  -d '{"prompt": "sunset over mountains", "style": "photorealistic"}'
```

#### **Video Generation**
```bash
# High-quality cinematic
"Generate a cinematic video of rain falling on city streets"

# Fast generation
"Create a quick animation of a cat walking"

# Conversations (MultiTalk)
"Make a video of two people discussing AI technology"
```

#### **Voice Synthesis**
```bash
# ElevenLabs (Primary)
"Generate a professional voiceover for this text"

# Filipino TTS
"Gumawa ng boses na nagsasalita ng Tagalog"
```

### **File Management**
- Full VPS file system access
- Upload/download files through web interface
- Automatic organization of generated content
- Version control integration

### **Automation Features**
- Code execution in secure environments
- Web browsing and data extraction
- API integrations with external services
- Scheduled tasks and workflows

---

## 🔧 **Maintenance & Updates**

### **Regular Maintenance**
```bash
# Update dependencies
pip install -r config/settings/requirements.txt --upgrade

# Clean cache
python scripts/maintenance/cleanup_cache.py

# Backup data
python scripts/maintenance/create_backup.py
```

### **Performance Optimization**
```bash
# Clean Python cache
find . -name "__pycache__" -exec rm -rf {} +

# Optimize embeddings
python scripts/maintenance/optimize_embeddings.py

# Monitor resources
python scripts/maintenance/system_monitor.py
```

### **Troubleshooting**

#### **Common Issues**

**1. Port Already in Use**
```bash
# Kill processes on port 80
sudo fuser -k 80/tcp
```

**2. Memory Issues**
```bash
# Clear system cache
sudo sync && echo 3 > /proc/sys/vm/drop_caches
```

**3. GPU Not Detected**
```bash
# Check CUDA installation
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

**4. API Key Issues**
```bash
# Verify environment variables
python -c "import os; print([k for k in os.environ.keys() if 'API' in k])"
```

---

## 📚 **Documentation**

### **API Reference**
- [API Documentation](docs/api/README.md)
- [WebSocket Events](docs/api/websockets.md)  
- [Authentication](docs/api/auth.md)

### **Development Guides**
- [Contributing](docs/CONTRIBUTING.md)
- [Plugin Development](docs/plugins/README.md)
- [Custom Models](docs/models/README.md)

### **Deployment**
- [Production Deployment](docs/deployment/production.md)
- [Docker Configuration](docs/deployment/docker.md)
- [Security Best Practices](docs/security/README.md)

---

## 🤝 **Support & Community**

### **Getting Help**
- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/your-repo/issues)
- 💬 [Discussions](https://github.com/your-repo/discussions)

### **Contributing**
We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 **Acknowledgments**

- Agent Zero Framework
- OpenAI, Anthropic, and other AI providers
- Open source multimedia generation projects
- The amazing open source community

---

**Made with ❤️ by the Pareng Boyong Team**