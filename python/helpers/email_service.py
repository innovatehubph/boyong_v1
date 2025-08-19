"""
Pareng Boyong Email Service
Professional email sending capabilities using Nodemailer
"""

import asyncio
import subprocess
import json
import os
import tempfile
import shutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from python.helpers.log import Log
from python.helpers.print_style import PrintStyle

@dataclass
class EmailRecipient:
    """Email recipient information"""
    email: str
    name: Optional[str] = None

@dataclass
class EmailAttachment:
    """Email attachment information"""
    filename: str
    path: str
    content_type: Optional[str] = None

@dataclass
class EmailTemplate:
    """Email template data"""
    subject: str
    html_content: str
    variables: Dict[str, Any]

@dataclass
class EmailResult:
    """Result of email sending operation"""
    success: bool
    message_id: Optional[str]
    recipients: List[str]
    error_message: Optional[str] = None
    send_time: float = 0.0

class ParengBoyongEmailService:
    """Professional email service for Pareng Boyong"""
    
    def __init__(self, logger: Optional[Log] = None):
        self.logger = logger or Log()
        
        # Email configuration
        self.smtp_config = {
            'host': 'smtp.hostinger.com',
            'port': 465,
            'secure': True,
            'auth': {
                'user': 'admin@innovatehub.ph',
                'pass': 'Bossmarc@747'
            }
        }
        
        # Template configuration
        self.template_config = {
            'logo_path': '/root/logo/Innologo 2 Background Removed.png',
            'company_name': 'InnovateHub Philippines',
            'company_color': '#57317A',
            'button_color': '#28a745',
            'website_url': 'https://innovatehub.ph'
        }
        
        # Ensure Nodemailer is installed
        self._ensure_nodemailer_installed()
        
    def _ensure_nodemailer_installed(self):
        """Ensure Nodemailer and dependencies are installed"""
        
        try:
            # Check if node_modules exists
            node_modules_path = Path("/root/projects/pareng-boyong/node_modules")
            
            if not node_modules_path.exists():
                PrintStyle(font_color="yellow").print("📦 Installing Nodemailer dependencies...")
                
                # Create package.json if it doesn't exist
                package_json_path = Path("/root/projects/pareng-boyong/package.json")
                if not package_json_path.exists():
                    package_json = {
                        "name": "pareng-boyong-email",
                        "version": "1.0.0",
                        "description": "Email service for Pareng Boyong",
                        "dependencies": {
                            "nodemailer": "^6.9.8",
                            "handlebars": "^4.7.8"
                        }
                    }
                    package_json_path.write_text(json.dumps(package_json, indent=2))
                
                # Install dependencies
                result = subprocess.run(
                    "npm install",
                    shell=True,
                    cwd="/root/projects/pareng-boyong",
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    PrintStyle(font_color="green").print("✅ Nodemailer installed successfully")
                else:
                    PrintStyle(font_color="red").print(f"❌ Failed to install Nodemailer: {result.stderr}")
                    
        except Exception as e:
            self.logger.log(f"Error installing Nodemailer: {e}")
    
    def create_standard_template(
        self, 
        subject: str,
        recipient_name: str,
        content_html: str,
        button_text: Optional[str] = None,
        button_url: Optional[str] = None,
        note_text: Optional[str] = None
    ) -> str:
        """Create email using the standard InnovateHub template"""
        
        # Build button HTML if provided
        button_html = ""
        if button_text and button_url:
            button_html = f'''
            <div style="text-align: center; margin: 30px 0;">
                <a href="{button_url}" class="button">{button_text}</a>
            </div>
            '''
        
        # Build note HTML if provided
        note_html = ""
        if note_text:
            note_html = f'''
            <div class="note">
                <p><strong>Note:</strong> {note_text}</p>
            </div>
            '''
        
        # Standard email template
        template_html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{subject}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, Helvetica, sans-serif;
            background-color: #f7f7f7;
            color: #333333;
        }}
        .container {{
            max-width: 600px;
            margin: 20px auto;
            background-color: #ffffff;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            overflow: hidden;
            padding: 20px;
        }}
        .header {{
            background-color: {self.template_config['company_color']};
            color: #ffffff;
            text-align: center;
            padding: 30px 20px;
            border-radius: 12px 12px 0 0;
        }}
        .header img {{
            width: 150px;
            height: auto;
            margin-bottom: 20px;
        }}
        .content {{
            padding: 10px 10px 20px 10px;
            font-size: 16px;
            line-height: 1.6;
        }}
        .button {{
            display: inline-block;
            background-color: {self.template_config['button_color']};
            color: #ffffff;
            padding: 12px 24px;
            text-align: center;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
        }}
        .note {{
            background-color: #f3e5f5;
            padding: 15px 20px;
            border-left: 4px solid {self.template_config['company_color']};
            margin-top: 30px;
        }}
        .footer {{
            background-color: {self.template_config['company_color']};
            color: #ffffff;
            text-align: center;
            font-size: 12px;
            padding: 20px;
            border-radius: 0 0 12px 12px;
        }}
        @media only screen and (max-width: 480px) {{
            .container {{
                margin: 10px;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
            }}
            .button {{
                width: 100%;
                display: block;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="cid:logo" alt="InnovateHub Logo" />
            <h1>{subject}</h1>
        </div>
        <div class="content">
            <p>Hello {recipient_name},</p>
            {content_html}
            {button_html}
            {note_html}
        </div>
        <div class="footer">
            <p>Best regards,<br><strong>Pareng Boyong AI Assistant</strong></p>
            <p>This is an automated message. Please do not reply directly to this email.</p>
            <p>&copy; 2025 {self.template_config['company_name']}. All rights reserved.</p>
        </div>
    </div>
</body>
</html>'''
        
        return template_html
    
    async def send_email(
        self,
        to: List[EmailRecipient],
        subject: str,
        html_content: str,
        attachments: Optional[List[EmailAttachment]] = None,
        cc: Optional[List[EmailRecipient]] = None,
        bcc: Optional[List[EmailRecipient]] = None
    ) -> EmailResult:
        """Send email using Nodemailer"""
        
        start_time = datetime.now()
        
        try:
            # Create temporary Node.js script for sending email
            email_script = self._create_email_script(
                to, subject, html_content, attachments, cc, bcc
            )
            
            # Execute the email script
            result = subprocess.run(
                f"node {email_script}",
                shell=True,
                cwd="/root/projects/pareng-boyong",
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Parse result
            if result.returncode == 0:
                try:
                    response_data = json.loads(result.stdout)
                    
                    send_time = (datetime.now() - start_time).total_seconds()
                    
                    return EmailResult(
                        success=True,
                        message_id=response_data.get('messageId'),
                        recipients=[r.email for r in to],
                        send_time=send_time
                    )
                    
                except json.JSONDecodeError:
                    return EmailResult(
                        success=True,
                        message_id=None,
                        recipients=[r.email for r in to],
                        send_time=(datetime.now() - start_time).total_seconds()
                    )
            else:
                return EmailResult(
                    success=False,
                    message_id=None,
                    recipients=[r.email for r in to],
                    error_message=result.stderr,
                    send_time=(datetime.now() - start_time).total_seconds()
                )
                
        except subprocess.TimeoutExpired:
            return EmailResult(
                success=False,
                message_id=None,
                recipients=[r.email for r in to],
                error_message="Email sending timeout",
                send_time=(datetime.now() - start_time).total_seconds()
            )
        except Exception as e:
            return EmailResult(
                success=False,
                message_id=None,
                recipients=[r.email for r in to],
                error_message=str(e),
                send_time=(datetime.now() - start_time).total_seconds()
            )
        finally:
            # Cleanup temporary script
            if 'email_script' in locals() and os.path.exists(email_script):
                os.unlink(email_script)
    
    def _create_email_script(
        self,
        to: List[EmailRecipient],
        subject: str,
        html_content: str,
        attachments: Optional[List[EmailAttachment]] = None,
        cc: Optional[List[EmailRecipient]] = None,
        bcc: Optional[List[EmailRecipient]] = None
    ) -> str:
        """Create temporary Node.js script for sending email"""
        
        # Prepare recipient lists
        to_list = [{"address": r.email, "name": r.name or r.email} for r in to]
        cc_list = [{"address": r.email, "name": r.name or r.email} for r in (cc or [])]
        bcc_list = [{"address": r.email, "name": r.name or r.email} for r in (bcc or [])]
        
        # Prepare attachments
        attachment_list = []
        
        # Always include logo as inline attachment
        logo_path = self.template_config['logo_path']
        if os.path.exists(logo_path):
            attachment_list.append({
                "filename": "logo.png",
                "path": logo_path,
                "cid": "logo"
            })
        
        # Add custom attachments
        if attachments:
            for att in attachments:
                attachment_list.append({
                    "filename": att.filename,
                    "path": att.path,
                    "contentType": att.content_type
                })
        
        # Create Node.js email script
        script_content = f'''
const nodemailer = require('nodemailer');

async function sendEmail() {{
    try {{
        // Create transporter
        const transporter = nodemailer.createTransporter({{
            host: '{self.smtp_config['host']}',
            port: {self.smtp_config['port']},
            secure: {str(self.smtp_config['secure']).lower()},
            auth: {{
                user: '{self.smtp_config['auth']['user']}',
                pass: '{self.smtp_config['auth']['pass']}'
            }}
        }});
        
        // Verify connection
        await transporter.verify();
        
        // Email options
        const mailOptions = {{
            from: {{
                name: 'Pareng Boyong AI Assistant',
                address: '{self.smtp_config['auth']['user']}'
            }},
            to: {json.dumps(to_list)},
            cc: {json.dumps(cc_list)},
            bcc: {json.dumps(bcc_list)},
            subject: `{subject}`,
            html: `{html_content.replace('`', '\\`').replace('${', '\\${')}`,
            attachments: {json.dumps(attachment_list)}
        }};
        
        // Send email
        const info = await transporter.sendEmail(mailOptions);
        
        // Return success response
        console.log(JSON.stringify({{
            success: true,
            messageId: info.messageId,
            response: info.response
        }}));
        
    }} catch (error) {{
        console.error(JSON.stringify({{
            success: false,
            error: error.message
        }}));
        process.exit(1);
    }}
}}

sendEmail();
'''
        
        # Write script to temporary file
        temp_script = tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.js',
            delete=False,
            dir='/tmp'
        )
        
        temp_script.write(script_content)
        temp_script.close()
        
        return temp_script.name
    
    async def send_standard_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        content_html: str,
        button_text: Optional[str] = None,
        button_url: Optional[str] = None,
        note_text: Optional[str] = None,
        cc_emails: Optional[List[str]] = None
    ) -> EmailResult:
        """Send email using standard InnovateHub template"""
        
        # Create recipients
        recipients = [EmailRecipient(email=to_email, name=to_name)]
        cc_recipients = [EmailRecipient(email=email) for email in (cc_emails or [])]
        
        # Generate HTML using standard template
        html_content = self.create_standard_template(
            subject=subject,
            recipient_name=to_name,
            content_html=content_html,
            button_text=button_text,
            button_url=button_url,
            note_text=note_text
        )
        
        # Send email
        return await self.send_email(
            to=recipients,
            subject=subject,
            html_content=html_content,
            cc=cc_recipients
        )
    
    async def send_notification_email(
        self,
        to_email: str,
        to_name: str,
        notification_type: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> EmailResult:
        """Send notification email"""
        
        subject = f"Pareng Boyong Notification: {notification_type}"
        
        content_html = f"<p>{message}</p>"
        
        if details:
            content_html += "<h3>Details:</h3><ul>"
            for key, value in details.items():
                content_html += f"<li><strong>{key}:</strong> {value}</li>"
            content_html += "</ul>"
        
        return await self.send_standard_email(
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            content_html=content_html,
            note_text="This is an automated notification from Pareng Boyong AI Assistant."
        )
    
    async def send_webapp_deployment_notification(
        self,
        to_email: str,
        to_name: str,
        webapp_name: str,
        webapp_url: str,
        deployment_service: str,
        webapp_type: str = "webapp",
        deployment_time: float = 0.0
    ) -> EmailResult:
        """Send webapp deployment notification with VPS-specific details"""
        
        subject = f"🚀 Your {webapp_name} is now live!"
        
        # Enhanced content for VPS deployments
        if deployment_service.lower() == "vps":
            content_html = f'''
            <p>🎉 <strong>Excellent news!</strong> Your {webapp_type} webapp <strong>{webapp_name}</strong> has been successfully deployed to your VPS and is now accessible to users worldwide.</p>
            
            <h3>🏠 VPS Deployment Details:</h3>
            <ul>
                <li><strong>Webapp Name:</strong> {webapp_name}</li>
                <li><strong>App Type:</strong> {webapp_type.title()}</li>
                <li><strong>Hosting:</strong> InnovateHub VPS (projects.innovatehub.ph)</li>
                <li><strong>Deployment Method:</strong> Path-based routing</li>
                <li><strong>Status:</strong> ✅ Live and accessible</li>
                <li><strong>Deploy Time:</strong> {deployment_time:.1f} seconds</li>
            </ul>
            
            <h3>🌐 Access Your Webapp:</h3>
            <p>Your webapp is available at: <strong>{webapp_url}</strong></p>
            <p>All sub-pages and resources are automatically accessible through wildcard routing:</p>
            <ul>
                <li>📍 Main app: <code>{webapp_url}</code></li>
                <li>📍 Any sub-path: <code>{webapp_url}[your-path]</code></li>
                <li>📍 API endpoints: <code>{webapp_url}api/[endpoint]</code></li>
            </ul>
            
            <h3>🔧 Technical Features:</h3>
            <ul>
                <li>✅ SSL/TLS encryption enabled</li>
                <li>✅ Asset compression and caching</li>
                <li>✅ Mobile-responsive serving</li>
                <li>✅ High-performance nginx routing</li>
                <li>✅ Process management {'(PM2)' if webapp_type == 'node' else '(systemd)' if webapp_type == 'python' else ''}</li>
            </ul>
            
            <p><strong>🎯 Your webapp is now live and ready for users!</strong> You can share this URL with anyone, and they'll be able to access your webapp from any device, anywhere in the world.</p>
            '''
            
            note_text = f"Your webapp is hosted on InnovateHub's VPS with enterprise-grade infrastructure. The URL {webapp_url} is your permanent address!"
            
        else:
            # Standard deployment notification for external services
            content_html = f'''
            <p>Great news! Your webapp <strong>{webapp_name}</strong> has been successfully deployed and is now accessible to users worldwide.</p>
            
            <h3>Deployment Details:</h3>
            <ul>
                <li><strong>Webapp Name:</strong> {webapp_name}</li>
                <li><strong>Hosting Service:</strong> {deployment_service.title()}</li>
                <li><strong>Status:</strong> Live and accessible</li>
                <li><strong>Deploy Time:</strong> {deployment_time:.1f} seconds</li>
            </ul>
            
            <p>You can now share this URL with anyone, and they'll be able to access your webapp from any device.</p>
            '''
            
            note_text = "Keep this URL safe - it's your webapp's permanent address!"
        
        return await self.send_standard_email(
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            content_html=content_html,
            button_text="🌐 Open Your Webapp",
            button_url=webapp_url,
            note_text=note_text
        )
    
    def get_email_stats(self) -> Dict[str, Any]:
        """Get email service statistics"""
        
        return {
            'smtp_host': self.smtp_config['host'],
            'smtp_port': self.smtp_config['port'],
            'from_email': self.smtp_config['auth']['user'],
            'template_logo': os.path.exists(self.template_config['logo_path']),
            'nodemailer_available': shutil.which('node') is not None,
            'company_name': self.template_config['company_name'],
            'website_url': self.template_config['website_url']
        }

# Global email service instance
_email_service = None

def get_email_service(logger: Optional[Log] = None) -> ParengBoyongEmailService:
    """Get or create global email service"""
    global _email_service
    
    if _email_service is None:
        _email_service = ParengBoyongEmailService(logger)
        
    return _email_service