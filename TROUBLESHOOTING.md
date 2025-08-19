# Pareng Boyong - Installation Troubleshooting Guide

## 🔧 Common Installation Issues and Solutions

This guide addresses all issues discovered during comprehensive testing and provides solutions for seamless installation.

---

## 🐍 **Python Version Issues**

### **Problem: Python 3.13+ Compatibility**
**Symptoms:**
- `kokoro>=0.9.2` installation fails
- Build errors with setuptools
- Package version conflicts

**Solution:**
```bash
# Use Python version-specific requirements
pip install -r config/settings/requirements-py3.13.txt

# Or run compatibility fixer
python scripts/setup/validate_dependencies.py --fix
```

### **Problem: Python Too Old**
**Symptoms:**
- Installation fails with "Python 3.x required"
- Import errors for modern packages

**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install python3.11 python3.11-pip python3.11-venv

# macOS with Homebrew
brew install python@3.11

# Update Python command
export PYTHON_CMD=python3.11
```

---

## 📦 **Dependency Issues**

### **Problem: Missing Dependencies**
**Symptoms:**
- `ModuleNotFoundError: No module named 'crontab'`
- `ModuleNotFoundError: No module named 'flaredantic'` 
- `ModuleNotFoundError: No module named 'inputimeout'`

**Solution:**
```bash
# Install missing dependencies automatically
python scripts/setup/validate_dependencies.py --install

# Or install manually
pip install crontab inputimeout flaredantic requests openai
```

### **Problem: Package Build Failures**
**Symptoms:**
- `error: subprocess-exited-with-error`
- Build wheel failures
- setuptools errors

**Solution:**
```bash
# Upgrade build tools first
pip install --upgrade pip setuptools wheel

# For Python 3.13+
pip install "setuptools>=75.0.0"

# Then retry installation
pip install -r config/settings/requirements.txt
```

---

## 🌐 **Web UI Issues**

### **Problem: UI Won't Start**
**Symptoms:**
- `Traceback` errors when running `run_ui.py`
- Missing template errors
- Port binding issues

**Solution:**
```bash
# Check all dependencies
python scripts/setup/validate_dependencies.py

# Test with different port
python run_ui.py --port 8081

# Check logs
tail -f logs/pareng-boyong.log
```

### **Problem: Static Files Missing**
**Symptoms:**
- 404 errors for CSS/JS files
- Broken styling
- Missing images

**Solution:**
```bash
# Check webui directory structure
ls -la webui/

# Restore missing files from backup
cp -r webui-backup/* webui/

# Or re-clone repository
git clone https://github.com/innovatehubph/boyong_v1.git
```

---

## 🐳 **Docker Issues**

### **Problem: Docker Permission Denied**
**Symptoms:**
- `permission denied while trying to connect to Docker daemon`
- Docker commands fail

**Solution:**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Restart shell or logout/login
newgrp docker

# Test Docker access
docker --version
```

### **Problem: Container Build Failures**
**Symptoms:**
- Docker build fails with dependency errors
- Out of space errors

**Solution:**
```bash
# Clean Docker system
docker system prune -a

# Build with no-cache
docker-compose build --no-cache

# Check disk space
df -h
```

---

## 🔄 **Auto-Update Issues**

### **Problem: Update System Not Working**
**Symptoms:**
- Auto-updates not running
- Configuration errors
- Merge conflicts

**Solution:**
```bash
# Check update configuration
cat config/update/update_config.json

# Run manual update
python scripts/update/auto_update_agent_zero.py

# Reset update configuration
rm config/update/update_config.json
python scripts/update/auto_update_agent_zero.py --schedule
```

### **Problem: Customizations Lost After Update**
**Symptoms:**
- Pareng Boyong branding missing
- Multimedia features disabled
- Custom configurations reset

**Solution:**
```bash
# Restore from backup
ls backups/
cp -r backups/pareng_boyong_backup_YYYYMMDD_HHMMSS/* ./

# Check protected files list
grep "pareng_boyong_protected_files" config/update/update_config.json

# Rebuild multimedia services
python scripts/setup/rebuild_multimedia_services.py
```

---

## 💾 **File System Issues**

### **Problem: Permission Errors**
**Symptoms:**
- `PermissionError` when writing files
- Cannot create directories
- Log file access denied

**Solution:**
```bash
# Fix ownership
sudo chown -R $USER:$USER /opt/pareng-boyong

# Fix permissions
chmod +x scripts/setup/*.sh
chmod +x scripts/update/*.py
chmod +x scripts/test/*.py

# Create required directories
mkdir -p logs backups temp_update pareng_boyong_deliverables
```

### **Problem: Path Resolution Issues**
**Symptoms:**
- `/a0/` path errors
- File not found errors
- Working directory issues

**Solution:**
```bash
# Check current directory
pwd

# Should be in repository root
cd /opt/pareng-boyong

# Test path resolution
python -c "from python.helpers.files import get_abs_path; print(get_abs_path('README.md'))"
```

---

## 🔗 **Network Issues**

### **Problem: API Connection Failures**
**Symptoms:**
- OpenAI API errors
- Model loading failures
- Timeout errors

**Solution:**
```bash
# Check internet connection
curl -I https://api.openai.com/v1/models

# Verify API keys
grep -r "API_KEY" config/env/.env

# Test with different endpoints
python -c "import openai; print(openai.__version__)"
```

### **Problem: Tunnel Access Issues**
**Symptoms:**
- External access not working
- Tunnel creation failures
- Port conflicts

**Solution:**
```bash
# Check port availability
netstat -tuln | grep :8080

# Test local access first
curl http://localhost:8080

# Check tunnel configuration
python python/helpers/tunnel_manager.py --test
```

---

## 🧪 **Testing and Validation**

### **Problem: Tests Failing**
**Symptoms:**
- Installation tests report failures
- Import errors during testing
- Missing test files

**Solution:**
```bash
# Run comprehensive test
python scripts/test/comprehensive_test.py

# Check specific test results
cat comprehensive_test_report.json

# Run dependency validation
python scripts/setup/validate_dependencies.py
```

---

## 🚀 **Performance Issues**

### **Problem: Slow Performance**
**Symptoms:**
- Long response times
- High memory usage
- CPU spikes

**Solution:**
```bash
# Check system resources
htop
free -h
df -h

# Optimize Python environment
pip install --upgrade pip setuptools
python -m pip check

# Clear cache
rm -rf __pycache__ */__pycache__ */*/__pycache__
```

---

## 🆘 **Emergency Recovery**

### **Complete Reset Procedure**
If everything fails, use this complete reset:

```bash
# 1. Backup important data
cp -r pareng_boyong_deliverables/ ~/pareng_boyong_backup/
cp config/env/.env ~/pareng_boyong_backup/

# 2. Clean installation
rm -rf /opt/pareng-boyong
git clone https://github.com/innovatehubph/boyong_v1.git /opt/pareng-boyong
cd /opt/pareng-boyong

# 3. Run enhanced installer
chmod +x scripts/setup/enhanced_quick_install.sh
./scripts/setup/enhanced_quick_install.sh

# 4. Restore data
cp -r ~/pareng_boyong_backup/pareng_boyong_deliverables/ ./
cp ~/pareng_boyong_backup/.env config/env/
```

---

## 📞 **Getting Help**

### **Diagnostic Information**
When reporting issues, include:

```bash
# System information
python --version
uname -a
docker --version

# Installation status
python scripts/test/comprehensive_test.py > diagnostic_report.txt

# Configuration
cat config/update/update_config.json
ls -la config/
```

### **Log Files to Check**
- `/tmp/pareng-boyong-install.log` - Installation log
- `logs/pareng-boyong.log` - Application log
- `comprehensive_test_report.json` - Test results
- `validation_report.md` - Dependency validation

### **Support Channels**
1. **GitHub Issues**: https://github.com/innovatehubph/boyong_v1/issues
2. **Documentation**: README.md, INSTALL.md, GITHUB_SETUP.md
3. **Diagnostic Tools**: `scripts/test/comprehensive_test.py`

---

## ✅ **Prevention Tips**

1. **Always use virtual environments**
2. **Keep Python version 3.8-3.12 for best compatibility**
3. **Run validation before and after installation**
4. **Regular backups before updates**
5. **Monitor system resources**
6. **Keep API keys secure and updated**

---

*This troubleshooting guide is updated based on comprehensive testing and real-world installation scenarios.*