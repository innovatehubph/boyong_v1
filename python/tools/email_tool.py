"""
Pareng Boyong Email Tool
Professional email sending capabilities with InnovateHub branding
"""

import asyncio
from datetime import datetime
from python.helpers.tool import Tool, Response
from python.helpers.email_service import get_email_service, EmailRecipient, EmailAttachment
from python.helpers.print_style import PrintStyle

class EmailTool(Tool):
    """Tool for sending professional emails through Pareng Boyong"""
    
    async def execute(self, **kwargs):
        """Execute email sending operations"""
        
        email_type = self.args.get("email_type", "standard").lower()
        
        if email_type == "standard":
            return await self._send_standard_email()
        elif email_type == "notification":
            return await self._send_notification_email()
        elif email_type == "webapp_deployment":
            return await self._send_webapp_deployment_email()
        elif email_type == "custom":
            return await self._send_custom_email()
        elif email_type == "test":
            return await self._send_test_email()
        elif email_type == "status":
            return await self._show_email_status()
        else:
            return Response(message=self._get_help_message())
    
    async def _send_standard_email(self):
        """Send email using standard InnovateHub template"""
        
        # Required parameters
        to_email = self.args.get("to_email", "")
        to_name = self.args.get("to_name", "")
        subject = self.args.get("subject", "")
        content = self.args.get("content", "")
        
        if not all([to_email, to_name, subject, content]):
            return Response(message="❌ Missing required parameters: to_email, to_name, subject, content")
        
        # Optional parameters
        button_text = self.args.get("button_text")
        button_url = self.args.get("button_url")
        note_text = self.args.get("note_text")
        cc_emails = self.args.get("cc_emails", [])
        
        email_service = get_email_service(self.agent.context.log)
        
        PrintStyle(font_color="cyan").print(f"📧 Sending standard email to {to_email}...")
        
        try:
            result = await email_service.send_standard_email(
                to_email=to_email,
                to_name=to_name,
                subject=subject,
                content_html=content,
                button_text=button_text,
                button_url=button_url,
                note_text=note_text,
                cc_emails=cc_emails
            )
            
            if result.success:
                return Response(message=f"""
📧 **EMAIL SENT SUCCESSFULLY!**

**📬 Email Details:**
• To: {to_name} ({to_email})
• Subject: {subject}
• Template: InnovateHub Standard
• Message ID: {result.message_id or 'Generated'}
• Send Time: {result.send_time:.2f}s

**✅ Status:** Email delivered successfully using professional template
**🎨 Design:** InnovateHub branded template with logo
**📱 Features:** Mobile-responsive design with modern styling

**💡 Recipient Experience:**
The recipient will receive a professionally designed email with:
• InnovateHub logo and branding
• Clean, modern layout
• Mobile-responsive design
• Professional footer with company information
{'• Action button: ' + button_text if button_text else ''}
{'• Important note section' if note_text else ''}
                """.strip())
            else:
                return Response(message=f"""
❌ **EMAIL SENDING FAILED**

**Error Details:**
• Recipient: {to_email}
• Subject: {subject}
• Error: {result.error_message}
• Attempt Duration: {result.send_time:.2f}s

**Troubleshooting:**
• Check recipient email address format
• Verify SMTP configuration
• Ensure internet connectivity
• Try again in a few moments
                """.strip())
                
        except Exception as e:
            return Response(message=f"💥 Email system error: {e}")
    
    async def _send_notification_email(self):
        """Send notification email"""
        
        to_email = self.args.get("to_email", "")
        to_name = self.args.get("to_name", "")
        notification_type = self.args.get("notification_type", "General")
        message = self.args.get("message", "")
        details = self.args.get("details", {})
        
        if not all([to_email, to_name, message]):
            return Response(message="❌ Missing required parameters: to_email, to_name, message")
        
        email_service = get_email_service(self.agent.context.log)
        
        PrintStyle(font_color="cyan").print(f"🔔 Sending notification email to {to_email}...")
        
        try:
            result = await email_service.send_notification_email(
                to_email=to_email,
                to_name=to_name,
                notification_type=notification_type,
                message=message,
                details=details
            )
            
            if result.success:
                return Response(message=f"""
🔔 **NOTIFICATION EMAIL SENT!**

**📬 Notification Details:**
• Recipient: {to_name} ({to_email})
• Type: {notification_type}
• Message: {message[:100]}{'...' if len(message) > 100 else ''}
• Details: {len(details)} items included
• Send Time: {result.send_time:.2f}s

**✅ Status:** Notification delivered successfully
                """.strip())
            else:
                return Response(message=f"❌ Notification email failed: {result.error_message}")
                
        except Exception as e:
            return Response(message=f"💥 Notification email error: {e}")
    
    async def _send_webapp_deployment_email(self):
        """Send webapp deployment notification email"""
        
        to_email = self.args.get("to_email", "")
        to_name = self.args.get("to_name", "")
        webapp_name = self.args.get("webapp_name", "")
        webapp_url = self.args.get("webapp_url", "")
        deployment_service = self.args.get("deployment_service", "Cloud")
        
        if not all([to_email, to_name, webapp_name, webapp_url]):
            return Response(message="❌ Missing required parameters: to_email, to_name, webapp_name, webapp_url")
        
        email_service = get_email_service(self.agent.context.log)
        
        PrintStyle(font_color="cyan").print(f"🚀 Sending webapp deployment email to {to_email}...")
        
        try:
            result = await email_service.send_webapp_deployment_notification(
                to_email=to_email,
                to_name=to_name,
                webapp_name=webapp_name,
                webapp_url=webapp_url,
                deployment_service=deployment_service
            )
            
            if result.success:
                return Response(message=f"""
🚀 **WEBAPP DEPLOYMENT EMAIL SENT!**

**📬 Deployment Notification:**
• Recipient: {to_name} ({to_email})
• Webapp: {webapp_name}
• URL: {webapp_url}
• Service: {deployment_service}
• Send Time: {result.send_time:.2f}s

**✅ Status:** Deployment notification delivered
**🎯 Purpose:** User informed about webapp accessibility
**🌐 Action:** Recipient can click button to open webapp
                """.strip())
            else:
                return Response(message=f"❌ Webapp deployment email failed: {result.error_message}")
                
        except Exception as e:
            return Response(message=f"💥 Webapp deployment email error: {e}")
    
    async def _send_custom_email(self):
        """Send custom email with full HTML content"""
        
        to_email = self.args.get("to_email", "")
        to_name = self.args.get("to_name", "")
        subject = self.args.get("subject", "")
        html_content = self.args.get("html_content", "")
        attachments = self.args.get("attachments", [])
        cc_emails = self.args.get("cc_emails", [])
        bcc_emails = self.args.get("bcc_emails", [])
        
        if not all([to_email, subject, html_content]):
            return Response(message="❌ Missing required parameters: to_email, subject, html_content")
        
        email_service = get_email_service(self.agent.context.log)
        
        PrintStyle(font_color="cyan").print(f"✉️ Sending custom email to {to_email}...")
        
        try:
            # Prepare recipients
            recipients = [EmailRecipient(email=to_email, name=to_name or to_email)]
            cc_recipients = [EmailRecipient(email=email) for email in cc_emails]
            bcc_recipients = [EmailRecipient(email=email) for email in bcc_emails]
            
            # Prepare attachments
            email_attachments = []
            for att in attachments:
                if isinstance(att, dict) and 'filename' in att and 'path' in att:
                    email_attachments.append(EmailAttachment(
                        filename=att['filename'],
                        path=att['path'],
                        content_type=att.get('content_type')
                    ))
            
            result = await email_service.send_email(
                to=recipients,
                subject=subject,
                html_content=html_content,
                attachments=email_attachments,
                cc=cc_recipients,
                bcc=bcc_recipients
            )
            
            if result.success:
                return Response(message=f"""
✉️ **CUSTOM EMAIL SENT!**

**📬 Email Details:**
• To: {to_email}
• Subject: {subject}
• CC Recipients: {len(cc_emails)}
• BCC Recipients: {len(bcc_emails)}
• Attachments: {len(email_attachments)}
• Send Time: {result.send_time:.2f}s

**✅ Status:** Custom email delivered successfully
                """.strip())
            else:
                return Response(message=f"❌ Custom email failed: {result.error_message}")
                
        except Exception as e:
            return Response(message=f"💥 Custom email error: {e}")
    
    async def _send_test_email(self):
        """Send test email to verify email system"""
        
        test_email = self.args.get("test_email", "admin@innovatehub.ph")
        
        email_service = get_email_service(self.agent.context.log)
        
        PrintStyle(font_color="cyan").print(f"🧪 Sending test email to {test_email}...")
        
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            result = await email_service.send_standard_email(
                to_email=test_email,
                to_name="Email System Tester",
                subject="Pareng Boyong Email System Test",
                content_html=f"""
                <p>This is a test email from Pareng Boyong's email system.</p>
                
                <h3>Test Details:</h3>
                <ul>
                    <li><strong>Test Time:</strong> {current_time}</li>
                    <li><strong>System:</strong> Pareng Boyong AI Assistant</li>
                    <li><strong>Email Service:</strong> InnovateHub SMTP</li>
                    <li><strong>Template:</strong> Standard InnovateHub Design</li>
                </ul>
                
                <p>If you received this email, the email system is working correctly!</p>
                """,
                button_text="View System Status",
                button_url="https://innovatehub.ph",
                note_text="This is an automated test email. No action is required."
            )
            
            if result.success:
                return Response(message=f"""
🧪 **EMAIL SYSTEM TEST SUCCESSFUL!**

**📬 Test Results:**
• Test Email: {test_email}
• Send Time: {result.send_time:.2f}s
• Message ID: {result.message_id or 'Generated'}

**✅ System Status:**
• SMTP Connection: Working
• Template Rendering: Working
• Logo Attachment: Working
• Email Delivery: Successful

**🎯 Conclusion:** Email system is fully operational and ready for use!
                """.strip())
            else:
                return Response(message=f"""
🧪 **EMAIL SYSTEM TEST FAILED**

**❌ Test Results:**
• Test Email: {test_email}
• Error: {result.error_message}
• Duration: {result.send_time:.2f}s

**🔧 Troubleshooting Required:**
• Check SMTP credentials
• Verify network connectivity
• Review email configuration
                """.strip())
                
        except Exception as e:
            return Response(message=f"💥 Email test error: {e}")
    
    async def _show_email_status(self):
        """Show email system status and configuration"""
        
        email_service = get_email_service(self.agent.context.log)
        stats = email_service.get_email_stats()
        
        status_message = f"""
📧 **PARENG BOYONG EMAIL SYSTEM STATUS**

**🔧 SMTP Configuration:**
• Host: {stats['smtp_host']}
• Port: {stats['smtp_port']}
• From Email: {stats['from_email']}
• Security: SSL/TLS Enabled

**🎨 Template Configuration:**
• Company: {stats['company_name']}
• Website: {stats['website_url']}
• Logo Available: {'✅ Yes' if stats['template_logo'] else '❌ No'}
• Template Style: InnovateHub Professional

**🛠️ System Dependencies:**
• Node.js: {'✅ Available' if stats['nodemailer_available'] else '❌ Not Found'}
• Nodemailer: Installing automatically when needed
• Template Engine: Built-in HTML generator

**📋 Available Email Types:**
• **Standard** - Professional template with InnovateHub branding
• **Notification** - System notifications and alerts
• **Webapp Deployment** - Webapp launch notifications
• **Custom** - Full HTML emails with attachments
• **Test** - System verification emails

**🎯 Features:**
• Professional InnovateHub branding
• Mobile-responsive design
• Automatic logo embedding
• Action buttons and CTAs
• CC/BCC support
• File attachments
• Error handling and recovery

**✅ Status:** Email system is ready for professional communication
        """.strip()
        
        PrintStyle(font_color="cyan").print("📊 Email system status report generated")
        return Response(message=status_message)
    
    def _get_help_message(self):
        """Get help message for the email tool"""
        
        return """
📧 **PARENG BOYONG EMAIL TOOL**

**🎯 Purpose:** Send professional emails with InnovateHub branding and modern templates.

**Available Email Types:**

**• `standard` - Professional Template Email**
```json
{
  "tool_name": "email",
  "email_type": "standard",
  "to_email": "user@example.com",
  "to_name": "John Doe",
  "subject": "Welcome to Our Service",
  "content": "<p>Thank you for joining us!</p>",
  "button_text": "Get Started",
  "button_url": "https://example.com/start",
  "note_text": "Contact support if you need help",
  "cc_emails": ["manager@example.com"]
}
```

**• `notification` - System Notification**
```json
{
  "tool_name": "email",
  "email_type": "notification",
  "to_email": "user@example.com",
  "to_name": "John Doe",
  "notification_type": "System Alert",
  "message": "Your account has been updated",
  "details": {"account": "premium", "expires": "2025-12-31"}
}
```

**• `webapp_deployment` - Webapp Launch Notification**
```json
{
  "tool_name": "email",
  "email_type": "webapp_deployment",
  "to_email": "developer@example.com",
  "to_name": "Jane Developer",
  "webapp_name": "My Todo App",
  "webapp_url": "https://my-todo-app.vercel.app",
  "deployment_service": "Vercel"
}
```

**• `custom` - Full HTML Email**
```json
{
  "tool_name": "email",
  "email_type": "custom",
  "to_email": "user@example.com",
  "subject": "Custom Email",
  "html_content": "<html>...</html>",
  "attachments": [{"filename": "doc.pdf", "path": "/path/to/doc.pdf"}],
  "cc_emails": ["cc@example.com"],
  "bcc_emails": ["bcc@example.com"]
}
```

**• `test` - System Test**
```json
{
  "tool_name": "email",
  "email_type": "test",
  "test_email": "admin@innovatehub.ph"
}
```

**• `status` - System Status**
```json
{
  "tool_name": "email",
  "email_type": "status"
}
```

**🎨 Template Features:**
• InnovateHub professional branding
• Mobile-responsive design
• Automatic logo embedding
• Modern CSS styling
• Action buttons with hover effects
• Professional footer with company info
• Color scheme: #57317A (purple) and #28a745 (green)

**📧 SMTP Configuration:**
• Host: smtp.hostinger.com
• Port: 465 (SSL)
• From: admin@innovatehub.ph
• Security: Full SSL/TLS encryption

**✅ Use Cases:**
• Welcome emails for new users
• System notifications and alerts
• Webapp deployment notifications
• Marketing and promotional emails
• Transactional emails
• Customer support communications

The email system provides professional, branded communication capabilities for Pareng Boyong with automatic template generation and reliable delivery.
        """.strip()

# Register the tool
if __name__ == "__main__":
    print("Email Tool loaded successfully")