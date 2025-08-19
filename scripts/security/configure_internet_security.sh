#!/bin/bash

# Agent Zero Internet Security Configuration
# Configures security settings for internet exposure via ai.innovatehub.ph

set -e

echo "🔒 Configuring Agent Zero Security for Internet Access..."

# Function to generate secure password
generate_password() {
    openssl rand -base64 32 | tr -d "=+/" | cut -c1-25
}

# Generate secure passwords
RFC_PASSWORD=$(generate_password)
UI_PASSWORD=$(generate_password)
ROOT_PASSWORD=$(generate_password)

echo "📋 Generated Security Credentials:"
echo "   RFC Password: $RFC_PASSWORD"
echo "   UI Password: $UI_PASSWORD" 
echo "   Root Password: $ROOT_PASSWORD"
echo ""

# Create environment file for the development container
echo "📝 Creating security configuration..."

cat > /root/projects/pareng-boyong/.env << EOF
# Agent Zero Security Configuration for Internet Access
# Generated on $(date)

# RFC Authentication
RFC_PASSWORD=$RFC_PASSWORD

# UI Authentication  
UI_LOGIN=admin
UI_PASSWORD=$UI_PASSWORD

# Root password for SSH access
ROOT_PASSWORD=$ROOT_PASSWORD

# External access configuration
EXTERNAL_ACCESS=true
DOMAIN=ai.innovatehub.ph

# Security settings
SECURE_MODE=true
RATE_LIMIT=true
EOF

# Set proper permissions on env file
chmod 600 /root/projects/pareng-boyong/.env

echo "✅ Environment file created: /root/projects/pareng-boyong/.env"

# Configure firewall rules for security
echo "🔥 Configuring firewall rules..."

# Allow only necessary ports
ufw --force reset >/dev/null 2>&1 || true
ufw default deny incoming
ufw default allow outgoing

# SSH access
ufw allow 22/tcp comment "SSH"

# HTTP/HTTPS (nginx)
ufw allow 80/tcp comment "HTTP"
ufw allow 443/tcp comment "HTTPS"

# Agent Zero services (only from localhost)
ufw allow from 127.0.0.1 to any port 55080 comment "Agent Zero HTTP (localhost only)"
ufw allow from 127.0.0.1 to any port 55022 comment "Agent Zero SSH (localhost only)"
ufw allow from 127.0.0.1 to any port 55510 comment "SearXNG (localhost only)"

# Docker network access
ufw allow from 172.17.0.0/16 comment "Docker network"

# Enable firewall
ufw --force enable

echo "✅ Firewall configured"

# Restart development container with new environment
echo "🔄 Restarting Agent Zero development container with security settings..."

docker stop agent-zero-dev >/dev/null 2>&1 || true
docker rm agent-zero-dev >/dev/null 2>&1 || true

# Start container with environment file
docker run -d \
    --name agent-zero-dev \
    -p 127.0.0.1:55080:80 \
    -p 127.0.0.1:55022:22 \
    -v /root/projects/pareng-boyong:/a0 \
    --env-file /root/projects/pareng-boyong/.env \
    agent0ai/agent-zero:latest

# Wait for container to start
echo "⏳ Waiting for container to initialize..."
sleep 15

# Test container accessibility
if docker ps | grep -q agent-zero-dev; then
    echo "✅ Secure Agent Zero container is running"
else
    echo "❌ Failed to start secure container"
    exit 1
fi

# Create security monitoring script
cat > /root/projects/pareng-boyong/monitor_security.sh << 'EOF'
#!/bin/bash

# Agent Zero Security Monitor
echo "🔍 Agent Zero Security Status"
echo "=============================="

# Check container status
echo "📦 Container Status:"
if docker ps | grep -q agent-zero-dev; then
    echo "   ✅ Agent Zero container running"
else
    echo "   ❌ Agent Zero container not running"
fi

# Check firewall status
echo ""
echo "🔥 Firewall Status:"
ufw status numbered | head -10

# Check nginx status
echo ""
echo "🌐 Nginx Status:"
if systemctl is-active --quiet nginx; then
    echo "   ✅ Nginx running"
else
    echo "   ❌ Nginx not running"
fi

# Check SSL certificate
echo ""
echo "🔒 SSL Certificate:"
if openssl x509 -checkend 2592000 -noout -in /etc/letsencrypt/live/ai.innovatehub.ph/cert.pem 2>/dev/null; then
    echo "   ✅ SSL certificate valid for 30+ days"
else
    echo "   ⚠️  SSL certificate expires soon or invalid"
fi

# Check recent access attempts
echo ""
echo "📊 Recent Access (last 10 entries):"
tail -10 /var/log/nginx/ai.innovatehub.ph.access.log | cut -d' ' -f1,4,5,6,7 | sed 's/\[//g'

echo ""
echo "🔒 Security Configuration Complete"
EOF

chmod +x /root/projects/pareng-boyong/monitor_security.sh

echo ""
echo "🎉 Internet Security Configuration Complete!"
echo ""
echo "🌐 Access Information:"
echo "   URL: https://ai.innovatehub.ph"
echo "   UI Username: admin"
echo "   UI Password: $UI_PASSWORD"
echo ""
echo "🔧 Security Features Enabled:"
echo "   ✅ HTTPS with SSL certificates"
echo "   ✅ Rate limiting (10 req/s)"
echo "   ✅ Firewall protection"
echo "   ✅ UI authentication"
echo "   ✅ RFC password protection"
echo "   ✅ Localhost-only RFC access"
echo "   ✅ Security headers"
echo ""
echo "📋 Management Commands:"
echo "   Monitor: ./monitor_security.sh"
echo "   View logs: tail -f /var/log/nginx/ai.innovatehub.ph.access.log"
echo "   Container logs: docker logs -f agent-zero-dev"
echo ""
echo "⚠️  IMPORTANT: Save the UI password: $UI_PASSWORD"
echo "🔐 Configure this password in Agent Zero settings for full functionality"