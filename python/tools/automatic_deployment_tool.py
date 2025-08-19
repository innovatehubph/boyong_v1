"""
Pareng Boyong Automatic Deployment Management Tool
Ensures every webapp created is immediately accessible to users
Solves the critical UX problem of local-only deployments
"""

import asyncio
import os
from datetime import datetime
from python.helpers.tool import Tool, Response
from python.helpers.automatic_deployment_system import get_deployment_system
from python.helpers.print_style import PrintStyle

class AutomaticDeploymentTool(Tool):
    """Tool for managing automatic webapp deployment system"""
    
    async def execute(self, **kwargs):
        """Execute automatic deployment management commands"""
        
        command = self.args.get("command", "status").lower()
        
        if command == "status":
            return await self._show_deployment_status()
        elif command == "start_monitoring":
            return await self._start_monitoring()
        elif command == "stop_monitoring":
            return await self._stop_monitoring()
        elif command == "deploy_webapp":
            return await self._deploy_specific_webapp()
        elif command == "list_accessible":
            return await self._list_accessible_webapps()
        elif command == "test_webapp":
            return await self._test_webapp_access()
        elif command == "deployment_history":
            return await self._show_deployment_history()
        elif command == "force_redeploy":
            return await self._force_redeploy()
        else:
            return Response(message=self._get_help_message())
    
    async def _show_deployment_status(self):
        """Show comprehensive deployment system status"""
        
        deployment_system = get_deployment_system(self.agent.context.log)
        status = deployment_system.get_deployment_status()
        
        status_message = f"""
🚀 **AUTOMATIC WEBAPP DEPLOYMENT SYSTEM STATUS**

**🛡️ System State:**
• Monitoring: {'🟢 ACTIVE' if status['monitoring'] else '🔴 INACTIVE'}
• Total Webapps Deployed: {status['total_webapps_deployed']}
• Deployment Success Rate: {status['success_rate']:.1%}
• Total Deployments: {status['deployment_history_count']}

**🌐 Currently Accessible Webapps ({len(status['active_webapps'])}):**
"""
        
        if status['active_webapps']:
            for webapp in status['active_webapps']:
                status_emoji = {
                    'deployed': '🟢',
                    'deploying': '🟡',
                    'failed': '🔴'
                }.get(webapp['status'], '❓')
                
                status_message += f"""
• {status_emoji} **{webapp['name']}**
  📱 URL: {webapp['url']}
  ☁️ Service: {webapp['service'].title()}
  📊 Status: {webapp['status'].title()}
"""
        else:
            status_message += "\n• No webapps currently deployed\n"
        
        status_message += f"""
**🎯 System Purpose:**
• Automatically detect newly created webapps
• Deploy them to public cloud services (Vercel, Netlify, Surge)
• Provide users with immediately accessible URLs
• Eliminate the frustration of local-only deployments

**⚙️ Deployment Services Available:**
• Vercel (React, Vue, Node.js, Static)
• Netlify (React, Vue, Static)
• Surge.sh (Static sites)
• Ngrok Tunnel (Fallback for any app)
• Railway (Coming soon)
• Render (Coming soon)

**📊 Performance:**
"""
        
        if status['success_rate'] > 0.8:
            status_message += "🟢 **EXCELLENT** - High deployment success rate"
        elif status['success_rate'] > 0.6:
            status_message += "🟡 **GOOD** - Most deployments successful"
        elif status['success_rate'] > 0.3:
            status_message += "🟠 **FAIR** - Some deployment issues"
        else:
            status_message += "🔴 **POOR** - Deployment system needs attention"
        
        PrintStyle(font_color="cyan").print("📊 Deployment system status report generated")
        return Response(message=status_message.strip())
    
    async def _start_monitoring(self):
        """Start automatic webapp monitoring and deployment"""
        
        deployment_system = get_deployment_system(self.agent.context.log)
        
        if deployment_system.monitoring:
            return Response(message="✅ Automatic deployment monitoring is already active")
        
        try:
            # Start monitoring in background
            asyncio.create_task(deployment_system.start_monitoring())
            
            return Response(message="""
🚀 **AUTOMATIC DEPLOYMENT MONITORING STARTED**

The system is now actively monitoring for new webapps and will automatically deploy them for user access.

**🔍 What's Being Monitored:**
• `/root/projects/pareng-boyong/pareng_boyong_deliverables/webapps/`
• `/root/projects/pareng-boyong/work_dir/`
• `/tmp/webapp_projects/`
• `/root/webapp_projects/`

**🤖 Automatic Actions:**
• Detect newly created webapps (React, Vue, Node.js, Python, Static)
• Analyze webapp type and framework
• Deploy to best available cloud service
• Test accessibility and provide public URLs
• Monitor deployment success

**☁️ Deployment Targets:**
• **Vercel** - React, Vue, Node.js apps (Priority 1)
• **Netlify** - Static sites and SPAs (Priority 2)
• **Surge.sh** - Simple static hosting (Priority 3)
• **Ngrok Tunnel** - Fallback for any webapp

**✅ Status:** Monitoring active - new webapps will be automatically deployed!

**💡 User Benefit:** When you create a webapp, users will immediately get a working URL they can access from anywhere.
            """.strip())
            
        except Exception as e:
            return Response(message=f"❌ Failed to start monitoring: {e}")
    
    async def _stop_monitoring(self):
        """Stop automatic webapp monitoring"""
        
        deployment_system = get_deployment_system(self.agent.context.log)
        
        if not deployment_system.monitoring:
            return Response(message="ℹ️ Automatic deployment monitoring is already stopped")
        
        try:
            deployment_system.stop_monitoring()
            
            return Response(message="""
⚠️ **AUTOMATIC DEPLOYMENT MONITORING STOPPED**

Webapp monitoring has been disabled.

**🔴 No Longer Active:**
• New webapp detection: DISABLED
• Automatic deployment: STOPPED
• Public URL generation: INACTIVE

**⚠️ Impact:**
• New webapps will remain local-only
• Users won't be able to access created webapps
• Manual deployment will be required

**💡 Recommendation:** Re-enable monitoring with command="start_monitoring" to ensure user accessibility.
            """.strip())
            
        except Exception as e:
            return Response(message=f"❌ Failed to stop monitoring: {e}")
    
    async def _deploy_specific_webapp(self):
        """Deploy a specific webapp manually"""
        
        webapp_path = self.args.get("webapp_path", "")
        webapp_name = self.args.get("webapp_name", "")
        
        if not webapp_path:
            return Response(message="❌ Please provide webapp_path parameter")
        
        if not os.path.exists(webapp_path):
            return Response(message=f"❌ Webapp path does not exist: {webapp_path}")
        
        deployment_system = get_deployment_system(self.agent.context.log)
        
        PrintStyle(font_color="cyan").print(f"🚀 Deploying webapp: {webapp_path}")
        
        try:
            public_url = await deployment_system.deploy_specific_webapp(webapp_path, webapp_name)
            
            if public_url:
                return Response(message=f"""
🎉 **WEBAPP DEPLOYED SUCCESSFULLY!**

**📱 Webapp Details:**
• Path: {webapp_path}
• Name: {webapp_name or os.path.basename(webapp_path)}

**🌐 Public Access:**
• **URL: {public_url}**
• Status: Deployed and accessible
• Users can now access this webapp from anywhere

**✅ Next Steps:**
• Share the URL with users
• Test all webapp functionality
• Monitor usage and performance

**🎯 User Benefit:** The webapp is now publicly accessible and ready for use!
                """.strip())
            else:
                return Response(message=f"""
❌ **DEPLOYMENT FAILED**

Could not deploy webapp at: {webapp_path}

**Possible Issues:**
• Webapp type not recognized (React, Vue, Node.js, Python, Static)
• Build errors in the webapp
• No available deployment services
• Network connectivity issues

**💡 Troubleshooting:**
• Check webapp structure and package.json
• Ensure all dependencies are installed
• Try command="deployment_history" to see error details
• Use command="status" to check system health
                """.strip())
                
        except Exception as e:
            return Response(message=f"💥 Deployment error: {e}")
    
    async def _list_accessible_webapps(self):
        """List all webapps that users can currently access"""
        
        deployment_system = get_deployment_system(self.agent.context.log)
        accessible_webapps = deployment_system.get_user_accessible_webapps()
        
        if not accessible_webapps:
            return Response(message="""
📱 **NO ACCESSIBLE WEBAPPS**

Currently, there are no webapps deployed and accessible to users.

**💡 To Deploy Webapps:**
• Create a webapp in a monitored directory
• Use command="deploy_webapp" with webapp_path
• Start monitoring with command="start_monitoring"

**🔍 Monitored Directories:**
• `/root/projects/pareng-boyong/pareng_boyong_deliverables/webapps/`
• `/root/projects/pareng-boyong/work_dir/`
• `/tmp/webapp_projects/`
• `/root/webapp_projects/`
            """.strip())
        
        webapp_list = f"""
🌐 **USER-ACCESSIBLE WEBAPPS ({len(accessible_webapps)})**

"""
        
        for i, webapp in enumerate(accessible_webapps, 1):
            created_date = datetime.fromisoformat(webapp['created_at']).strftime("%Y-%m-%d %H:%M")
            
            webapp_list += f"""
**{i}. {webapp['name']}**
• 🌐 **URL:** {webapp['url']}
• 📱 Type: {webapp['type'].title()} ({webapp['framework']})
• ☁️ Hosted on: {webapp['deployed_on'].title()}
• 📅 Created: {created_date}

"""
        
        webapp_list += f"""
**🎯 User Instructions:**
Copy any URL above and open it in a browser to access the webapp.

**📊 Summary:**
• Total accessible webapps: {len(accessible_webapps)}
• All URLs are publicly accessible
• No local setup required for users
        """
        
        return Response(message=webapp_list.strip())
    
    async def _test_webapp_access(self):
        """Test accessibility of a specific webapp"""
        
        webapp_url = self.args.get("webapp_url", "")
        
        if not webapp_url:
            return Response(message="❌ Please provide webapp_url parameter")
        
        PrintStyle(font_color="cyan").print(f"🧪 Testing webapp accessibility: {webapp_url}")
        
        try:
            import requests
            
            # Test HTTP request
            response = requests.get(webapp_url, timeout=30)
            
            test_result = f"""
🧪 **WEBAPP ACCESSIBILITY TEST**

**🌐 URL Tested:** {webapp_url}
**📊 Response Status:** {response.status_code}
**⏱️ Response Time:** {response.elapsed.total_seconds():.2f}s
**📏 Content Length:** {len(response.content)} bytes

"""
            
            if response.status_code == 200:
                test_result += "✅ **RESULT: ACCESSIBLE**\n"
                test_result += "The webapp is responding and accessible to users.\n\n"
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                if 'text/html' in content_type:
                    test_result += "📄 Content Type: HTML (Webapp)\n"
                elif 'application/json' in content_type:
                    test_result += "📄 Content Type: JSON (API)\n"
                else:
                    test_result += f"📄 Content Type: {content_type}\n"
                
                # Basic content analysis
                content = response.text.lower()
                if any(keyword in content for keyword in ['<html', '<body', '<div']):
                    test_result += "✅ HTML content detected - webapp appears to be working\n"
                
                if any(framework in content for framework in ['react', 'vue', 'angular']):
                    test_result += "⚛️ Frontend framework detected in content\n"
                
            elif response.status_code in [301, 302, 307, 308]:
                test_result += "🔄 **RESULT: REDIRECTING**\n"
                redirect_url = response.headers.get('location', 'Unknown')
                test_result += f"The webapp is redirecting to: {redirect_url}\n"
                
            elif response.status_code == 404:
                test_result += "❌ **RESULT: NOT FOUND**\n"
                test_result += "The webapp URL returns 404 - may not be deployed or URL is incorrect.\n"
                
            elif response.status_code >= 500:
                test_result += "💥 **RESULT: SERVER ERROR**\n"
                test_result += "The webapp has server-side issues and needs fixing.\n"
                
            else:
                test_result += f"⚠️ **RESULT: UNEXPECTED STATUS ({response.status_code})**\n"
                test_result += "The webapp returned an unexpected status code.\n"
            
            test_result += f"\n**🎯 User Impact:** "
            if response.status_code == 200:
                test_result += "Users can successfully access and use this webapp."
            else:
                test_result += "Users will encounter issues accessing this webapp."
            
            return Response(message=test_result.strip())
            
        except requests.exceptions.Timeout:
            return Response(message=f"""
⏰ **ACCESSIBILITY TEST: TIMEOUT**

**🌐 URL:** {webapp_url}
**❌ Result:** Request timed out after 30 seconds

**Possible Issues:**
• Webapp is not responding
• Server is overloaded
• Network connectivity problems
• Webapp is not actually deployed

**🎯 User Impact:** Users will not be able to access this webapp.
            """.strip())
            
        except requests.exceptions.ConnectionError:
            return Response(message=f"""
🔌 **ACCESSIBILITY TEST: CONNECTION ERROR**

**🌐 URL:** {webapp_url}
**❌ Result:** Could not connect to webapp

**Possible Issues:**
• Webapp is not deployed
• URL is incorrect
• Hosting service is down
• DNS resolution issues

**🎯 User Impact:** Users will not be able to access this webapp.
            """.strip())
            
        except Exception as e:
            return Response(message=f"💥 Accessibility test error: {e}")
    
    async def _show_deployment_history(self):
        """Show deployment history and statistics"""
        
        deployment_system = get_deployment_system(self.agent.context.log)
        
        if not deployment_system.deployment_history:
            return Response(message="📝 No deployment history available yet.")
        
        recent_deployments = deployment_system.deployment_history[-10:]  # Last 10 deployments
        
        history_message = f"""
📚 **DEPLOYMENT HISTORY**

**Recent Deployments ({len(recent_deployments)}):**

"""
        
        for i, deployment in enumerate(recent_deployments, 1):
            timestamp = datetime.fromisoformat(deployment['timestamp']).strftime("%Y-%m-%d %H:%M")
            success_emoji = "✅" if deployment['success'] else "❌"
            
            history_message += f"""
**{i}. {success_emoji} {deployment['webapp_name']}**
• Service: {deployment['service'].title()}
• Time: {timestamp}
• Duration: {deployment['deploy_time']:.1f}s
"""
            
            if deployment['success']:
                history_message += f"• URL: {deployment['public_url']}\n"
            else:
                history_message += f"• Error: {deployment.get('error', 'Unknown error')}\n"
            
            history_message += "\n"
        
        # Overall statistics
        total_deployments = len(deployment_system.deployment_history)
        successful_deployments = sum(1 for d in deployment_system.deployment_history if d['success'])
        success_rate = successful_deployments / total_deployments if total_deployments > 0 else 0
        
        # Service statistics
        service_stats = {}
        for deployment in deployment_system.deployment_history:
            service = deployment['service']
            if service not in service_stats:
                service_stats[service] = {'total': 0, 'successful': 0}
            service_stats[service]['total'] += 1
            if deployment['success']:
                service_stats[service]['successful'] += 1
        
        history_message += f"""
**📊 Overall Statistics:**
• Total Deployments: {total_deployments}
• Successful: {successful_deployments}
• Failed: {total_deployments - successful_deployments}
• Success Rate: {success_rate:.1%}

**☁️ Service Performance:**
"""
        
        for service, stats in service_stats.items():
            service_success_rate = stats['successful'] / stats['total'] if stats['total'] > 0 else 0
            history_message += f"• {service.title()}: {service_success_rate:.1%} ({stats['successful']}/{stats['total']})\n"
        
        return Response(message=history_message.strip())
    
    async def _force_redeploy(self):
        """Force redeploy a specific webapp"""
        
        webapp_name = self.args.get("webapp_name", "")
        
        if not webapp_name:
            return Response(message="❌ Please provide webapp_name parameter")
        
        deployment_system = get_deployment_system(self.agent.context.log)
        
        # Find the webapp
        if webapp_name not in deployment_system.deployed_webapps:
            return Response(message=f"❌ Webapp '{webapp_name}' not found in deployed webapps")
        
        webapp = deployment_system.deployed_webapps[webapp_name]
        
        PrintStyle(font_color="cyan").print(f"🔄 Force redeploying: {webapp_name}")
        
        try:
            # Reset status and redeploy
            webapp.deployment_status = "created"
            webapp.public_url = None
            
            await deployment_system._deploy_webapp_automatically(webapp)
            
            if webapp.deployment_status == "deployed":
                return Response(message=f"""
🎉 **WEBAPP REDEPLOYED SUCCESSFULLY!**

**📱 Webapp:** {webapp_name}
**🌐 New URL:** {webapp.public_url}
**☁️ Service:** {webapp.deployment_service.title()}
**📊 Status:** Deployed and accessible

**✅ Result:** The webapp has been redeployed and is ready for users.
                """.strip())
            else:
                return Response(message=f"""
❌ **REDEPLOYMENT FAILED**

**📱 Webapp:** {webapp_name}
**📊 Status:** {webapp.deployment_status}

Check deployment_history for error details.
                """.strip())
                
        except Exception as e:
            return Response(message=f"💥 Redeployment error: {e}")
    
    def _get_help_message(self):
        """Get help message for the tool"""
        
        return """
🚀 **AUTOMATIC WEBAPP DEPLOYMENT TOOL**

**🎯 Purpose:** Ensure every webapp created is immediately accessible to users, eliminating the frustration of local-only deployments.

**Available Commands:**

• `status` - Show deployment system status and active webapps
• `start_monitoring` - Start automatic webapp detection and deployment
• `stop_monitoring` - Stop automatic deployment monitoring
• `deploy_webapp` - Deploy a specific webapp manually
• `list_accessible` - List all webapps users can currently access
• `test_webapp` - Test accessibility of a specific webapp URL
• `deployment_history` - Show deployment history and statistics
• `force_redeploy` - Force redeploy a specific webapp

**Examples:**

```json
{
  "tool_name": "automatic_deployment",
  "command": "status"
}
```

```json
{
  "tool_name": "automatic_deployment",
  "command": "deploy_webapp",
  "webapp_path": "/path/to/webapp",
  "webapp_name": "my-awesome-app"
}
```

```json
{
  "tool_name": "automatic_deployment",
  "command": "test_webapp",
  "webapp_url": "https://my-app.vercel.app"
}
```

**🛡️ Supported Webapp Types:**
• **React** (create-react-app, Next.js)
• **Vue** (Vue CLI, Nuxt.js)
• **Node.js** (Express, Fastify)
• **Python** (Flask, Django)
• **Static HTML** (Plain HTML/CSS/JS)

**☁️ Deployment Services:**
• **Vercel** - React, Vue, Node.js (Priority 1)
• **Netlify** - Static sites and SPAs (Priority 2)  
• **Surge.sh** - Simple static hosting (Priority 3)
• **Ngrok Tunnel** - Fallback for any webapp

**🔍 Monitoring Directories:**
• `/root/projects/pareng-boyong/pareng_boyong_deliverables/webapps/`
• `/root/projects/pareng-boyong/work_dir/`
• `/tmp/webapp_projects/`
• `/root/webapp_projects/`

**🎉 User Benefits:**
• **No Setup Required** - Users get working URLs immediately
• **Universal Access** - Works from any device/browser
• **Zero Frustration** - No "it only works locally" problems
• **Professional URLs** - Proper hosting with HTTPS
• **Instant Sharing** - URLs can be shared immediately

The automatic deployment system solves the critical UX problem where users ask for webapps but can't access them because they're only deployed locally.
        """.strip()

# Register the tool
if __name__ == "__main__":
    print("Automatic Deployment Management Tool loaded successfully")