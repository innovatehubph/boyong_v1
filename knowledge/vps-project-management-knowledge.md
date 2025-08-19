# VPS Project Management Knowledge for Pareng Boyong

## 🏗️ Complete VPS Project Structure

Pareng Boyong now has comprehensive access to all VPS projects and applications through the enhanced file system integration.

## 📂 Project Directory Structure

### **Main Web Projects (/a0/vps-www/)**

#### **1. InnovateHub Projects Platform**
**Location**: `/a0/vps-www/projects.innovatehub.ph/`

**Structure**:
```
projects.innovatehub.ph/
├── frontend/              # Next.js React application
│   ├── app/              # Next.js 13+ app directory
│   ├── lib/              # Utility libraries
│   ├── public/           # Static assets
│   ├── package.json      # Dependencies
│   └── next.config.mjs   # Next.js configuration
├── backend/              # GraphQL API server
│   ├── src/              # Source code
│   ├── models/           # Database models
│   ├── resolvers/        # GraphQL resolvers
│   ├── schema/           # GraphQL schema
│   └── package.json      # Dependencies
└── api/                  # Python API service
    └── projects_api.py   # API server
```

**Key Files to Know**:
- Frontend: Next.js with TypeScript, TailwindCSS
- Backend: Node.js with GraphQL, MongoDB
- API: Python with FastAPI
- Domain: projects.innovatehub.ph

#### **2. Pareng Boyong Applications**
**Location**: `/a0/vps-www/pareng-boyong-apps/`

**Current Applications**:

##### **Espresso Depot** - Coffee Shop Management System
**Location**: `/a0/vps-www/pareng-boyong-apps/espresso-depot/`

**Structure**:
```
espresso-depot/
├── backend/              # Node.js Express API
│   ├── controllers/      # API controllers
│   ├── models/           # Database models
│   ├── routes/           # API routes
│   ├── middleware/       # Auth & validation
│   ├── config/           # Database config
│   ├── app.js           # Main server file
│   └── package.json     # Dependencies
└── frontend/            # React application
    ├── src/
    │   ├── components/   # React components
    │   ├── App.js       # Main app component
    │   └── index.js     # Entry point
    ├── public/          # Static assets
    └── package.json     # Dependencies
```

**Features**:
- Customer relationship management (CRM)
- Inventory management
- Order processing
- Employee scheduling
- Dashboard analytics
- PostgreSQL database integration

**Key Technologies**:
- Backend: Node.js, Express, PostgreSQL
- Frontend: React, JavaScript
- Authentication: JWT tokens
- Database: PostgreSQL with Sequelize ORM

#### **3. Default Web Root**
**Location**: `/a0/vps-www/html/`
- Standard nginx default web directory
- Contains basic HTML files
- Used for testing and fallback content

## 🛠️ Project Management Capabilities

### **File Operations Pareng Boyong Can Perform**

#### **Code Analysis & Review**
```bash
# View project structure
ls -la /a0/vps-www/projects.innovatehub.ph/frontend/

# Read configuration files
cat /a0/vps-www/pareng-boyong-apps/espresso-depot/backend/package.json

# Search for specific code patterns
grep -r "import" /a0/vps-www/projects.innovatehub.ph/frontend/src/
```

#### **Configuration Management**
```bash
# Update environment variables
nano /a0/vps-www/pareng-boyong-apps/espresso-depot/backend/.env

# Modify package.json dependencies
vim /a0/vps-www/projects.innovatehub.ph/frontend/package.json

# Update database configurations
cat /a0/vps-www/pareng-boyong-apps/espresso-depot/backend/config/database.js
```

#### **Log Analysis & Debugging**
```bash
# View application logs
tail -f /a0/vps-www/projects.innovatehub.ph/backend/logs/combined.log

# Check error logs
cat /a0/vps-www/projects.innovatehub.ph/backend/logs/error.log

# Monitor system logs
journalctl -f -u nginx
```

### **Development Workflow Integration**

#### **NPM/Node.js Projects**
Pareng Boyong can:
- Install dependencies: `npm install` in project directories
- Run development servers: `npm run dev`
- Build production versions: `npm run build`
- Run tests: `npm test`
- Update packages: `npm update`

#### **Database Management**
Access to database operations:
- PostgreSQL connections for Espresso Depot
- MongoDB operations for InnovateHub projects
- Database migrations and seeding
- Query execution and data analysis

#### **Web Server Configuration**
- Nginx configuration access
- SSL certificate management
- Domain routing and proxy settings
- Static file serving optimization

## 🔧 Common Project Tasks

### **1. Project Health Checks**
```bash
# Check if services are running
systemctl status nginx
systemctl status postgresql

# Verify project dependencies
cd /a0/vps-www/projects.innovatehub.ph/frontend && npm audit
cd /a0/vps-www/pareng-boyong-apps/espresso-depot/backend && npm audit
```

### **2. Deployment Operations**
```bash
# Build and deploy frontend
cd /a0/vps-www/projects.innovatehub.ph/frontend
npm run build
```

### **3. Database Operations**
```bash
# Connect to PostgreSQL for Espresso Depot
psql -h localhost -U espresso_dep_user -d espresso_dep_dev

# Run database migrations
cd /a0/vps-www/pareng-boyong-apps/espresso-depot/backend
npm run migrate
```

### **4. Performance Monitoring**
```bash
# Check disk usage
df -h /var/www

# Monitor memory usage
free -h

# Check active connections
netstat -tuln
```

## 🚨 Important Guidelines

### **File Modification Safety**
1. **Always backup** before making major changes
2. **Check file permissions** before editing
3. **Test changes** in development first
4. **Use version control** when available
5. **Verify dependencies** after modifications

### **Security Considerations**
1. **Never expose** sensitive configuration files
2. **Validate file permissions** for security
3. **Monitor access logs** for unusual activity
4. **Keep dependencies updated** for security patches
5. **Use environment variables** for secrets

### **Performance Best Practices**
1. **Monitor resource usage** during operations
2. **Optimize file operations** for large projects
3. **Use caching** where appropriate
4. **Implement proper logging** for debugging
5. **Regular maintenance** of temporary files

## 📊 Project Status Monitoring

### **Health Check Commands**
```bash
# Overall VPS status
docker ps -a
systemctl status nginx postgresql

# Project-specific checks
cd /a0/vps-www/projects.innovatehub.ph && npm run health-check
cd /a0/vps-www/pareng-boyong-apps/espresso-depot && npm run status

# Database connectivity
psql -h localhost -U espresso_dep_user -d espresso_dep_dev -c "SELECT version();"
```

### **Performance Metrics**
```bash
# Disk usage by project
du -sh /a0/vps-www/*/

# Memory usage monitoring
ps aux --sort=-%mem | head -10

# Network connections
ss -tuln | grep -E "(80|443|5432|3000|8000)"
```

This comprehensive project management system ensures Pareng Boyong can effectively maintain, develop, and troubleshoot all VPS applications while maintaining security and performance standards.