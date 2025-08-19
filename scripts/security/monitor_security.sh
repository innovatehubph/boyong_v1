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
