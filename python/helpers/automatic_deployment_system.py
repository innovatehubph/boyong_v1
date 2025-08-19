"""
Pareng Boyong Automatic Public Deployment System
Ensures every webapp created is immediately accessible to users
Solves the critical UX problem of local-only deployments
"""

import asyncio
import json
import subprocess
import requests
import os
import time
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import zipfile
import tempfile

from python.helpers.log import Log
from python.helpers.print_style import PrintStyle

@dataclass
class WebappInfo:
    """Information about a created webapp"""
    name: str
    local_path: str
    local_port: int
    webapp_type: str  # "static", "react", "vue", "node", "python", "php"
    framework: str    # "create-react-app", "vue-cli", "express", "flask", "django"
    build_command: Optional[str]
    start_command: Optional[str]
    public_url: Optional[str] = None
    deployment_status: str = "created"  # "created", "deploying", "deployed", "failed"
    deployment_service: Optional[str] = None
    created_at: str = ""

@dataclass
class DeploymentResult:
    """Result of a deployment attempt"""
    success: bool
    public_url: Optional[str]
    deployment_service: str
    deployment_time_seconds: float
    error_message: Optional[str] = None
    logs: List[str] = None

class WebappDetector:
    """Detects when webapps are created and gathers information"""
    
    def __init__(self, logger: Log):
        self.logger = logger
        self.monitored_directories = [
            "/root/projects/pareng-boyong/pareng_boyong_deliverables/webapps/",
            "/root/projects/pareng-boyong/work_dir/",
            "/tmp/webapp_projects/",
            "/root/webapp_projects/"
        ]
        
    def detect_new_webapps(self) -> List[WebappInfo]:
        """Detect newly created webapps that need deployment"""
        
        detected_webapps = []
        
        for directory in self.monitored_directories:
            if not os.path.exists(directory):
                continue
                
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                
                if os.path.isdir(item_path):
                    webapp_info = self._analyze_webapp_directory(item_path, item)
                    if webapp_info:
                        detected_webapps.append(webapp_info)
        
        return detected_webapps
    
    def _analyze_webapp_directory(self, path: str, name: str) -> Optional[WebappInfo]:
        """Analyze a directory to determine if it's a webapp and what type"""
        
        files = os.listdir(path)
        
        # React App Detection
        if "package.json" in files:
            try:
                package_json = json.loads(open(os.path.join(path, "package.json")).read())
                
                # React detection
                if ("react" in str(package_json.get("dependencies", {})) or 
                    "react" in str(package_json.get("devDependencies", {}))):
                    
                    return WebappInfo(
                        name=name,
                        local_path=path,
                        local_port=3000,
                        webapp_type="react",
                        framework="create-react-app",
                        build_command="npm run build",
                        start_command="npm start",
                        created_at=datetime.now().isoformat()
                    )
                
                # Vue detection
                elif ("vue" in str(package_json.get("dependencies", {})) or
                      "@vue/cli" in str(package_json.get("devDependencies", {}))):
                    
                    return WebappInfo(
                        name=name,
                        local_path=path,
                        local_port=8080,
                        webapp_type="vue",
                        framework="vue-cli",
                        build_command="npm run build",
                        start_command="npm run serve",
                        created_at=datetime.now().isoformat()
                    )
                
                # Node.js/Express detection
                elif ("express" in str(package_json.get("dependencies", {})) or
                      "scripts" in package_json and "start" in package_json["scripts"]):
                    
                    return WebappInfo(
                        name=name,
                        local_path=path,
                        local_port=3000,
                        webapp_type="node",
                        framework="express",
                        build_command=None,
                        start_command="npm start",
                        created_at=datetime.now().isoformat()
                    )
                    
            except:
                pass
        
        # Python Flask/Django Detection
        if any(f in files for f in ["app.py", "main.py", "server.py"]):
            # Flask detection
            for py_file in ["app.py", "main.py", "server.py"]:
                if py_file in files:
                    try:
                        content = open(os.path.join(path, py_file)).read()
                        if "flask" in content.lower() or "Flask" in content:
                            return WebappInfo(
                                name=name,
                                local_path=path,
                                local_port=5000,
                                webapp_type="python",
                                framework="flask",
                                build_command=None,
                                start_command=f"python {py_file}",
                                created_at=datetime.now().isoformat()
                            )
                    except:
                        pass
        
        # Django detection
        if "manage.py" in files:
            return WebappInfo(
                name=name,
                local_path=path,
                local_port=8000,
                webapp_type="python",
                framework="django",
                build_command=None,
                start_command="python manage.py runserver",
                created_at=datetime.now().isoformat()
            )
        
        # Static HTML detection
        if "index.html" in files:
            return WebappInfo(
                name=name,
                local_path=path,
                local_port=8080,
                webapp_type="static",
                framework="html",
                build_command=None,
                start_command=None,
                created_at=datetime.now().isoformat()
            )
        
        return None

class VPSDeploymentService:
    """Handles deployment to local VPS with projects.innovatehub.ph/{projectname}/ structure"""
    
    def __init__(self, logger: Log):
        self.logger = logger
        self.vps_config = {
            'domain': 'projects.innovatehub.ph',
            'web_root': '/var/www/projects.innovatehub.ph',
            'nginx_sites': '/etc/nginx/sites-available',
            'nginx_enabled': '/etc/nginx/sites-enabled',
            'pm2_apps': '/root/.pm2'
        }
        
        # Ensure directories exist
        self._ensure_vps_directories()
    
    def _ensure_vps_directories(self):
        """Ensure required VPS directories exist"""
        try:
            os.makedirs(self.vps_config['web_root'], exist_ok=True)
            os.makedirs(self.vps_config['nginx_sites'], exist_ok=True)
            os.makedirs(self.vps_config['nginx_enabled'], exist_ok=True)
            
            # Set proper permissions
            subprocess.run(f"chown -R www-data:www-data {self.vps_config['web_root']}", shell=True)
            subprocess.run(f"chmod -R 755 {self.vps_config['web_root']}", shell=True)
            
        except Exception as e:
            self.logger.log(f"Error ensuring VPS directories: {e}")
    
    async def deploy_webapp(self, webapp: WebappInfo) -> DeploymentResult:
        """Deploy webapp to VPS with path-based routing"""
        
        start_time = time.time()
        
        try:
            PrintStyle(font_color="cyan").print(f"🏠 Deploying to VPS: projects.innovatehub.ph/{webapp.name}/")
            
            # Create project directory
            project_path = os.path.join(self.vps_config['web_root'], webapp.name)
            os.makedirs(project_path, exist_ok=True)
            
            # Deploy based on webapp type
            if webapp.webapp_type in ['react', 'vue']:
                return await self._deploy_spa_to_vps(webapp, project_path, start_time)
            elif webapp.webapp_type == 'node':
                return await self._deploy_node_to_vps(webapp, project_path, start_time)
            elif webapp.webapp_type == 'python':
                return await self._deploy_python_to_vps(webapp, project_path, start_time)
            elif webapp.webapp_type == 'static':
                return await self._deploy_static_to_vps(webapp, project_path, start_time)
            else:
                return DeploymentResult(
                    success=False,
                    public_url=None,
                    deployment_service="vps",
                    deployment_time_seconds=time.time() - start_time,
                    error_message=f"Unsupported webapp type for VPS: {webapp.webapp_type}"
                )
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="vps",
                deployment_time_seconds=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _deploy_spa_to_vps(self, webapp: WebappInfo, project_path: str, start_time: float) -> DeploymentResult:
        """Deploy Single Page Application (React/Vue) to VPS"""
        
        try:
            # Copy source files
            shutil.copytree(webapp.local_path, project_path, dirs_exist_ok=True)
            
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            try:
                # Install dependencies
                PrintStyle(font_color="white").print("   Installing dependencies...")
                install_result = subprocess.run("npm install", shell=True, 
                                              capture_output=True, text=True, timeout=300)
                
                if install_result.returncode != 0:
                    return DeploymentResult(
                        success=False,
                        public_url=None,
                        deployment_service="vps",
                        deployment_time_seconds=time.time() - start_time,
                        error_message=f"npm install failed: {install_result.stderr}"
                    )
                
                # Build the project
                PrintStyle(font_color="white").print("   Building project...")
                build_result = subprocess.run("npm run build", shell=True,
                                            capture_output=True, text=True, timeout=600)
                
                if build_result.returncode != 0:
                    return DeploymentResult(
                        success=False,
                        public_url=None,
                        deployment_service="vps",
                        deployment_time_seconds=time.time() - start_time,
                        error_message=f"Build failed: {build_result.stderr}"
                    )
                
                # Determine build directory
                if os.path.exists("build"):
                    build_dir = "build"
                elif os.path.exists("dist"):
                    build_dir = "dist"
                else:
                    return DeploymentResult(
                        success=False,
                        public_url=None,
                        deployment_service="vps",
                        deployment_time_seconds=time.time() - start_time,
                        error_message="No build directory found (build/ or dist/)"
                    )
                
                # Copy built files to web root
                web_dir = os.path.join(project_path, "web")
                if os.path.exists(web_dir):
                    shutil.rmtree(web_dir)
                shutil.copytree(build_dir, web_dir)
                
                # Create nginx configuration
                await self._create_spa_nginx_config(webapp.name, web_dir)
                
                # Test and reload nginx
                nginx_test = subprocess.run("nginx -t", shell=True, capture_output=True, text=True)
                if nginx_test.returncode == 0:
                    subprocess.run("systemctl reload nginx", shell=True)
                    
                    public_url = f"https://{self.vps_config['domain']}/{webapp.name}/"
                    
                    return DeploymentResult(
                        success=True,
                        public_url=public_url,
                        deployment_service="vps",
                        deployment_time_seconds=time.time() - start_time,
                        logs=[f"SPA deployed to {public_url}"]
                    )
                else:
                    return DeploymentResult(
                        success=False,
                        public_url=None,
                        deployment_service="vps",
                        deployment_time_seconds=time.time() - start_time,
                        error_message=f"Nginx configuration test failed: {nginx_test.stderr}"
                    )
                    
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="vps",
                deployment_time_seconds=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _deploy_static_to_vps(self, webapp: WebappInfo, project_path: str, start_time: float) -> DeploymentResult:
        """Deploy static HTML website to VPS"""
        
        try:
            # Copy static files directly
            web_dir = os.path.join(project_path, "web")
            if os.path.exists(web_dir):
                shutil.rmtree(web_dir)
            shutil.copytree(webapp.local_path, web_dir)
            
            # Create nginx configuration
            await self._create_static_nginx_config(webapp.name, web_dir)
            
            # Test and reload nginx
            nginx_test = subprocess.run("nginx -t", shell=True, capture_output=True, text=True)
            if nginx_test.returncode == 0:
                subprocess.run("systemctl reload nginx", shell=True)
                
                public_url = f"https://{self.vps_config['domain']}/{webapp.name}/"
                
                return DeploymentResult(
                    success=True,
                    public_url=public_url,
                    deployment_service="vps",
                    deployment_time_seconds=time.time() - start_time,
                    logs=[f"Static site deployed to {public_url}"]
                )
            else:
                return DeploymentResult(
                    success=False,
                    public_url=None,
                    deployment_service="vps",
                    deployment_time_seconds=time.time() - start_time,
                    error_message=f"Nginx configuration test failed: {nginx_test.stderr}"
                )
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="vps",
                deployment_time_seconds=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _deploy_node_to_vps(self, webapp: WebappInfo, project_path: str, start_time: float) -> DeploymentResult:
        """Deploy Node.js application to VPS with PM2"""
        
        try:
            # Copy source files
            shutil.copytree(webapp.local_path, project_path, dirs_exist_ok=True)
            
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            try:
                # Install dependencies
                PrintStyle(font_color="white").print("   Installing dependencies...")
                install_result = subprocess.run("npm install --production", shell=True,
                                              capture_output=True, text=True, timeout=300)
                
                if install_result.returncode != 0:
                    return DeploymentResult(
                        success=False,
                        public_url=None,
                        deployment_service="vps",
                        deployment_time_seconds=time.time() - start_time,
                        error_message=f"npm install failed: {install_result.stderr}"
                    )
                
                # Find available port
                port = await self._find_available_port()
                
                # Create PM2 ecosystem file
                ecosystem_config = {
                    "apps": [{
                        "name": f"pareng-boyong-{webapp.name}",
                        "script": webapp.start_command.split()[-1] if webapp.start_command else "server.js",
                        "cwd": project_path,
                        "env": {
                            "PORT": str(port),
                            "NODE_ENV": "production"
                        },
                        "instances": 1,
                        "exec_mode": "fork",
                        "watch": False,
                        "max_memory_restart": "500M",
                        "error_file": f"/var/log/pm2/{webapp.name}-error.log",
                        "out_file": f"/var/log/pm2/{webapp.name}-out.log",
                        "log_file": f"/var/log/pm2/{webapp.name}-combined.log"
                    }]
                }
                
                with open("ecosystem.config.json", "w") as f:
                    json.dump(ecosystem_config, f, indent=2)
                
                # Stop existing PM2 process if it exists
                subprocess.run(f"pm2 delete pareng-boyong-{webapp.name}", shell=True, 
                             capture_output=True, text=True)
                
                # Start with PM2
                PrintStyle(font_color="white").print(f"   Starting Node.js app on port {port}...")
                pm2_result = subprocess.run("pm2 start ecosystem.config.json", shell=True,
                                          capture_output=True, text=True, timeout=60)
                
                if pm2_result.returncode != 0:
                    return DeploymentResult(
                        success=False,
                        public_url=None,
                        deployment_service="vps",
                        deployment_time_seconds=time.time() - start_time,
                        error_message=f"PM2 start failed: {pm2_result.stderr}"
                    )
                
                # Save PM2 configuration
                subprocess.run("pm2 save", shell=True)
                
                # Create nginx configuration for Node.js app
                await self._create_node_nginx_config(webapp.name, port)
                
                # Test and reload nginx
                nginx_test = subprocess.run("nginx -t", shell=True, capture_output=True, text=True)
                if nginx_test.returncode == 0:
                    subprocess.run("systemctl reload nginx", shell=True)
                    
                    public_url = f"https://{self.vps_config['domain']}/{webapp.name}/"
                    
                    return DeploymentResult(
                        success=True,
                        public_url=public_url,
                        deployment_service="vps",
                        deployment_time_seconds=time.time() - start_time,
                        logs=[f"Node.js app deployed to {public_url} (port {port})"]
                    )
                else:
                    return DeploymentResult(
                        success=False,
                        public_url=None,
                        deployment_service="vps",
                        deployment_time_seconds=time.time() - start_time,
                        error_message=f"Nginx configuration test failed: {nginx_test.stderr}"
                    )
                    
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="vps",
                deployment_time_seconds=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _deploy_python_to_vps(self, webapp: WebappInfo, project_path: str, start_time: float) -> DeploymentResult:
        """Deploy Python application to VPS"""
        
        try:
            # Copy source files
            shutil.copytree(webapp.local_path, project_path, dirs_exist_ok=True)
            
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            try:
                # Create virtual environment
                PrintStyle(font_color="white").print("   Creating Python virtual environment...")
                venv_result = subprocess.run("python3 -m venv venv", shell=True,
                                           capture_output=True, text=True, timeout=120)
                
                if venv_result.returncode != 0:
                    return DeploymentResult(
                        success=False,
                        public_url=None,
                        deployment_service="vps",
                        deployment_time_seconds=time.time() - start_time,
                        error_message=f"Virtual environment creation failed: {venv_result.stderr}"
                    )
                
                # Install dependencies
                if os.path.exists("requirements.txt"):
                    PrintStyle(font_color="white").print("   Installing Python dependencies...")
                    pip_result = subprocess.run("./venv/bin/pip install -r requirements.txt", shell=True,
                                              capture_output=True, text=True, timeout=300)
                    
                    if pip_result.returncode != 0:
                        return DeploymentResult(
                            success=False,
                            public_url=None,
                            deployment_service="vps",
                            deployment_time_seconds=time.time() - start_time,
                            error_message=f"pip install failed: {pip_result.stderr}"
                        )
                
                # Find available port
                port = await self._find_available_port()
                
                # Create systemd service for Python app
                service_name = f"pareng-boyong-{webapp.name}"
                await self._create_python_systemd_service(webapp, project_path, port, service_name)
                
                # Start the service
                PrintStyle(font_color="white").print(f"   Starting Python app on port {port}...")
                systemctl_result = subprocess.run(f"systemctl start {service_name}", shell=True,
                                                capture_output=True, text=True)
                
                if systemctl_result.returncode != 0:
                    return DeploymentResult(
                        success=False,
                        public_url=None,
                        deployment_service="vps",
                        deployment_time_seconds=time.time() - start_time,
                        error_message=f"Service start failed: {systemctl_result.stderr}"
                    )
                
                # Enable service to start on boot
                subprocess.run(f"systemctl enable {service_name}", shell=True)
                
                # Create nginx configuration for Python app
                await self._create_python_nginx_config(webapp.name, port)
                
                # Test and reload nginx
                nginx_test = subprocess.run("nginx -t", shell=True, capture_output=True, text=True)
                if nginx_test.returncode == 0:
                    subprocess.run("systemctl reload nginx", shell=True)
                    
                    public_url = f"https://{self.vps_config['domain']}/{webapp.name}/"
                    
                    return DeploymentResult(
                        success=True,
                        public_url=public_url,
                        deployment_service="vps",
                        deployment_time_seconds=time.time() - start_time,
                        logs=[f"Python app deployed to {public_url} (port {port})"]
                    )
                else:
                    return DeploymentResult(
                        success=False,
                        public_url=None,
                        deployment_service="vps",
                        deployment_time_seconds=time.time() - start_time,
                        error_message=f"Nginx configuration test failed: {nginx_test.stderr}"
                    )
                    
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="vps",
                deployment_time_seconds=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _find_available_port(self) -> int:
        """Find an available port for the application"""
        import socket
        
        for port in range(3000, 4000):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    return port
            except OSError:
                continue
        
        return 3000  # fallback
    
    async def _create_spa_nginx_config(self, project_name: str, web_dir: str):
        """Create nginx configuration for Single Page Application"""
        
        config_content = f'''# {project_name} - Single Page Application
location /{project_name}/ {{
    alias {web_dir}/;
    index index.html index.htm;
    
    # Handle client-side routing for SPAs
    try_files $uri $uri/ @{project_name}_fallback;
    
    # Cache static assets
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}

location @{project_name}_fallback {{
    rewrite ^/{project_name}/(.*)$ /{project_name}/index.html last;
}}
'''
        
        await self._update_main_nginx_config(project_name, config_content)
    
    async def _create_static_nginx_config(self, project_name: str, web_dir: str):
        """Create nginx configuration for static website"""
        
        config_content = f'''# {project_name} - Static Website
location /{project_name}/ {{
    alias {web_dir}/;
    index index.html index.htm;
    
    # Cache static assets
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}
'''
        
        await self._update_main_nginx_config(project_name, config_content)
    
    async def _create_node_nginx_config(self, project_name: str, port: int):
        """Create nginx configuration for Node.js application"""
        
        config_content = f'''# {project_name} - Node.js Application
location /{project_name}/ {{
    proxy_pass http://localhost:{port}/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
    
    # Handle paths without trailing slash
    rewrite ^/{project_name}$ /{project_name}/ permanent;
}}
'''
        
        await self._update_main_nginx_config(project_name, config_content)
    
    async def _create_python_nginx_config(self, project_name: str, port: int):
        """Create nginx configuration for Python application"""
        
        config_content = f'''# {project_name} - Python Application
location /{project_name}/ {{
    proxy_pass http://localhost:{port}/;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 300s;
    proxy_connect_timeout 75s;
    
    # Handle paths without trailing slash
    rewrite ^/{project_name}$ /{project_name}/ permanent;
}}
'''
        
        await self._update_main_nginx_config(project_name, config_content)
    
    async def _update_main_nginx_config(self, project_name: str, location_config: str):
        """Update the main projects.innovatehub.ph nginx configuration"""
        
        config_file = os.path.join(self.vps_config['nginx_sites'], 'projects.innovatehub.ph')
        
        try:
            # Read existing configuration
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    content = f.read()
            else:
                # Create base configuration if it doesn't exist
                content = self._get_base_nginx_config()
            
            # Remove existing location block for this project
            lines = content.split('\n')
            filtered_lines = []
            skip_block = False
            
            for line in lines:
                if f'# {project_name} -' in line:
                    skip_block = True
                elif skip_block and line.strip().startswith('}') and not line.strip().startswith('location'):
                    skip_block = False
                    continue
                elif not skip_block:
                    filtered_lines.append(line)
            
            # Find the correct insertion point (before the last closing brace of server block)
            insert_index = -1
            brace_count = 0
            
            for i in range(len(filtered_lines) - 1, -1, -1):
                line = filtered_lines[i].strip()
                if line == '}':
                    brace_count += 1
                elif line == '{' or line.startswith('server {'):
                    brace_count -= 1
                
                # Insert before the final server block closing brace
                if brace_count == 1 and line == '}' and i > 0:
                    # Check if this is the server block closing brace
                    prev_lines = filtered_lines[max(0, i-10):i]
                    has_server_content = any('server_name' in l or 'listen' in l or 'location' in l for l in prev_lines)
                    if has_server_content:
                        insert_index = i
                        break
            
            if insert_index > 0:
                # Insert the new location block with proper indentation
                new_lines = filtered_lines[:insert_index]
                new_lines.append('')  # Empty line for readability
                
                # Add each line of the location config with proper indentation
                for line in location_config.strip().split('\n'):
                    if line.strip():
                        new_lines.append('    ' + line)
                    else:
                        new_lines.append('')
                
                new_lines.append('')  # Empty line after location block
                new_lines.extend(filtered_lines[insert_index:])
                
                # Write updated configuration
                with open(config_file, 'w') as f:
                    f.write('\n'.join(new_lines))
                
                # Enable the site
                enabled_file = os.path.join(self.vps_config['nginx_enabled'], 'projects.innovatehub.ph')
                if not os.path.exists(enabled_file):
                    os.symlink(config_file, enabled_file)
                    
        except Exception as e:
            self.logger.log(f"Error updating nginx config: {e}")
            raise
    
    def _get_base_nginx_config(self) -> str:
        """Get base nginx configuration for projects.innovatehub.ph"""
        
        return f'''server {{
    listen 80;
    listen 443 ssl http2;
    server_name {self.vps_config['domain']};
    
    # SSL configuration (if certificates exist)
    ssl_certificate /etc/letsencrypt/live/{self.vps_config['domain']}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{self.vps_config['domain']}/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private auth;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
    
    # Default root location
    location / {{
        root {self.vps_config['web_root']};
        index index.html index.htm;
        try_files $uri $uri/ =404;
    }}
    
    # Health check endpoint
    location /health {{
        return 200 "OK";
        add_header Content-Type text/plain;
    }}
    
    # Projects will be added here automatically
    
    # Error pages
    error_page 502 503 504 /50x.html;
    location = /50x.html {{
        root /usr/share/nginx/html;
    }}
    
    # Logging
    access_log /var/log/nginx/{self.vps_config['domain']}.access.log;
    error_log /var/log/nginx/{self.vps_config['domain']}.error.log;
}}'''
    
    async def _create_python_systemd_service(self, webapp: WebappInfo, project_path: str, port: int, service_name: str):
        """Create systemd service for Python application"""
        
        # Determine the main Python file
        main_file = "app.py"
        if webapp.start_command:
            # Extract filename from start command like "python app.py" or "python main.py"
            parts = webapp.start_command.split()
            if len(parts) > 1:
                main_file = parts[-1]
        elif os.path.exists(os.path.join(project_path, "main.py")):
            main_file = "main.py"
        elif os.path.exists(os.path.join(project_path, "server.py")):
            main_file = "server.py"
        
        service_content = f'''[Unit]
Description=Pareng Boyong {webapp.name} Python Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory={project_path}
Environment="PORT={port}"
Environment="PYTHONPATH={project_path}"
ExecStart={project_path}/venv/bin/python {main_file}
Restart=always
RestartSec=3
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
'''
        
        service_file = f"/etc/systemd/system/{service_name}.service"
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        # Reload systemd
        subprocess.run("systemctl daemon-reload", shell=True)

class CloudDeploymentService:
    """Handles deployment to various cloud services and VPS"""
    
    def __init__(self, logger: Log):
        self.logger = logger
        self.vps_deployer = VPSDeploymentService(logger)
        self.deployment_services = {
            'vps': {'priority': 0, 'supports': ['react', 'vue', 'node', 'python', 'static']},  # Highest priority
            'vercel': {'priority': 1, 'supports': ['react', 'vue', 'node', 'static']},
            'netlify': {'priority': 2, 'supports': ['react', 'vue', 'static']},
            'heroku': {'priority': 3, 'supports': ['node', 'python']},
            'railway': {'priority': 4, 'supports': ['node', 'python', 'react', 'vue']},
            'render': {'priority': 5, 'supports': ['node', 'python', 'static']},
            'surge': {'priority': 6, 'supports': ['static', 'react', 'vue']}
        }
    
    async def deploy_webapp(self, webapp: WebappInfo) -> DeploymentResult:
        """Deploy webapp to the best available cloud service"""
        
        # Find best deployment service for this webapp type
        compatible_services = []
        for service, config in self.deployment_services.items():
            if webapp.webapp_type in config['supports']:
                compatible_services.append((service, config['priority']))
        
        # Sort by priority (lower number = higher priority)
        compatible_services.sort(key=lambda x: x[1])
        
        for service_name, _ in compatible_services:
            try:
                PrintStyle(font_color="cyan").print(f"🚀 Attempting deployment to {service_name.title()}...")
                
                if service_name == 'vps':
                    result = await self.vps_deployer.deploy_webapp(webapp)
                elif service_name == 'vercel':
                    result = await self._deploy_to_vercel(webapp)
                elif service_name == 'netlify':
                    result = await self._deploy_to_netlify(webapp)
                elif service_name == 'surge':
                    result = await self._deploy_to_surge(webapp)
                elif service_name == 'railway':
                    result = await self._deploy_to_railway(webapp)
                elif service_name == 'render':
                    result = await self._deploy_to_render(webapp)
                else:
                    continue
                
                if result.success:
                    PrintStyle(font_color="green").print(f"✅ Successfully deployed to {service_name.title()}")
                    return result
                else:
                    PrintStyle(font_color="yellow").print(f"⚠️ {service_name.title()} deployment failed: {result.error_message}")
                    
            except Exception as e:
                PrintStyle(font_color="red").print(f"❌ {service_name.title()} deployment error: {e}")
                continue
        
        # If all cloud services fail, try local tunnel as fallback
        return await self._deploy_with_tunnel(webapp)
    
    async def _deploy_to_vercel(self, webapp: WebappInfo) -> DeploymentResult:
        """Deploy to Vercel (best for React/Vue/Node.js)"""
        
        start_time = time.time()
        
        try:
            # Install Vercel CLI if not available
            await self._ensure_vercel_cli()
            
            # Change to webapp directory
            original_dir = os.getcwd()
            os.chdir(webapp.local_path)
            
            try:
                # Build the project if needed
                if webapp.build_command:
                    PrintStyle(font_color="white").print(f"   Building: {webapp.build_command}")
                    build_result = subprocess.run(webapp.build_command, shell=True, 
                                                capture_output=True, text=True, timeout=300)
                    
                    if build_result.returncode != 0:
                        return DeploymentResult(
                            success=False,
                            public_url=None,
                            deployment_service="vercel",
                            deployment_time_seconds=time.time() - start_time,
                            error_message=f"Build failed: {build_result.stderr}",
                            logs=[build_result.stdout, build_result.stderr]
                        )
                
                # Deploy to Vercel
                deploy_cmd = "vercel --prod --yes --token $VERCEL_TOKEN" if os.getenv('VERCEL_TOKEN') else "vercel --prod --yes"
                
                PrintStyle(font_color="white").print("   Deploying to Vercel...")
                deploy_result = subprocess.run(deploy_cmd, shell=True,
                                             capture_output=True, text=True, timeout=180)
                
                if deploy_result.returncode == 0:
                    # Extract URL from output
                    output_lines = deploy_result.stdout.split('\n')
                    public_url = None
                    
                    for line in output_lines:
                        if 'https://' in line and '.vercel.app' in line:
                            public_url = line.strip()
                            break
                    
                    if not public_url:
                        # Try to get from stderr
                        for line in deploy_result.stderr.split('\n'):
                            if 'https://' in line and '.vercel.app' in line:
                                public_url = line.strip()
                                break
                    
                    return DeploymentResult(
                        success=True,
                        public_url=public_url,
                        deployment_service="vercel",
                        deployment_time_seconds=time.time() - start_time,
                        logs=[deploy_result.stdout]
                    )
                else:
                    return DeploymentResult(
                        success=False,
                        public_url=None,
                        deployment_service="vercel",
                        deployment_time_seconds=time.time() - start_time,
                        error_message=f"Deployment failed: {deploy_result.stderr}",
                        logs=[deploy_result.stdout, deploy_result.stderr]
                    )
                    
            finally:
                os.chdir(original_dir)
                
        except subprocess.TimeoutExpired:
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="vercel",
                deployment_time_seconds=time.time() - start_time,
                error_message="Deployment timeout"
            )
        except Exception as e:
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="vercel",
                deployment_time_seconds=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _deploy_to_netlify(self, webapp: WebappInfo) -> DeploymentResult:
        """Deploy to Netlify (best for static sites)"""
        
        start_time = time.time()
        
        try:
            # Install Netlify CLI if not available
            await self._ensure_netlify_cli()
            
            # Change to webapp directory
            original_dir = os.getcwd()
            os.chdir(webapp.local_path)
            
            try:
                # Build the project if needed
                build_dir = "build"
                if webapp.build_command:
                    PrintStyle(font_color="white").print(f"   Building: {webapp.build_command}")
                    build_result = subprocess.run(webapp.build_command, shell=True,
                                                capture_output=True, text=True, timeout=300)
                    
                    if build_result.returncode != 0:
                        return DeploymentResult(
                            success=False,
                            public_url=None,
                            deployment_service="netlify",
                            deployment_time_seconds=time.time() - start_time,
                            error_message=f"Build failed: {build_result.stderr}"
                        )
                
                # Determine build directory
                if os.path.exists("build"):
                    build_dir = "build"
                elif os.path.exists("dist"):
                    build_dir = "dist"
                elif os.path.exists("public"):
                    build_dir = "public"
                else:
                    build_dir = "."
                
                # Deploy to Netlify
                deploy_cmd = f"netlify deploy --prod --dir {build_dir}"
                
                PrintStyle(font_color="white").print("   Deploying to Netlify...")
                deploy_result = subprocess.run(deploy_cmd, shell=True,
                                             capture_output=True, text=True, timeout=180)
                
                if deploy_result.returncode == 0:
                    # Extract URL from output
                    public_url = None
                    for line in deploy_result.stdout.split('\n'):
                        if 'Website URL:' in line:
                            public_url = line.split('Website URL:')[1].strip()
                            break
                        elif 'https://' in line and '.netlify.app' in line:
                            public_url = line.strip()
                            break
                    
                    return DeploymentResult(
                        success=True,
                        public_url=public_url,
                        deployment_service="netlify",
                        deployment_time_seconds=time.time() - start_time,
                        logs=[deploy_result.stdout]
                    )
                else:
                    return DeploymentResult(
                        success=False,
                        public_url=None,
                        deployment_service="netlify",
                        deployment_time_seconds=time.time() - start_time,
                        error_message=f"Deployment failed: {deploy_result.stderr}"
                    )
                    
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="netlify",
                deployment_time_seconds=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _deploy_to_surge(self, webapp: WebappInfo) -> DeploymentResult:
        """Deploy to Surge.sh (simple static hosting)"""
        
        start_time = time.time()
        
        try:
            # Install Surge CLI if not available
            await self._ensure_surge_cli()
            
            # Change to webapp directory
            original_dir = os.getcwd()
            os.chdir(webapp.local_path)
            
            try:
                # Build the project if needed
                build_dir = "."
                if webapp.build_command:
                    PrintStyle(font_color="white").print(f"   Building: {webapp.build_command}")
                    build_result = subprocess.run(webapp.build_command, shell=True,
                                                capture_output=True, text=True, timeout=300)
                    
                    if build_result.returncode != 0:
                        return DeploymentResult(
                            success=False,
                            public_url=None,
                            deployment_service="surge",
                            deployment_time_seconds=time.time() - start_time,
                            error_message=f"Build failed: {build_result.stderr}"
                        )
                    
                    # Use build directory
                    if os.path.exists("build"):
                        build_dir = "build"
                    elif os.path.exists("dist"):
                        build_dir = "dist"
                
                # Generate unique domain
                domain_name = f"{webapp.name.lower().replace('_', '-')}-{int(time.time())}.surge.sh"
                
                # Deploy to Surge
                deploy_cmd = f"surge {build_dir} {domain_name}"
                
                PrintStyle(font_color="white").print("   Deploying to Surge...")
                deploy_result = subprocess.run(deploy_cmd, shell=True,
                                             capture_output=True, text=True, timeout=120)
                
                if deploy_result.returncode == 0:
                    public_url = f"https://{domain_name}"
                    
                    return DeploymentResult(
                        success=True,
                        public_url=public_url,
                        deployment_service="surge",
                        deployment_time_seconds=time.time() - start_time,
                        logs=[deploy_result.stdout]
                    )
                else:
                    return DeploymentResult(
                        success=False,
                        public_url=None,
                        deployment_service="surge",
                        deployment_time_seconds=time.time() - start_time,
                        error_message=f"Deployment failed: {deploy_result.stderr}"
                    )
                    
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="surge",
                deployment_time_seconds=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _deploy_to_railway(self, webapp: WebappInfo) -> DeploymentResult:
        """Deploy to Railway (good for full-stack apps)"""
        
        start_time = time.time()
        
        try:
            # This would need Railway CLI setup
            # For now, return a placeholder implementation
            
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="railway",
                deployment_time_seconds=time.time() - start_time,
                error_message="Railway deployment not yet implemented - requires CLI setup"
            )
            
        except Exception as e:
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="railway",
                deployment_time_seconds=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _deploy_to_render(self, webapp: WebappInfo) -> DeploymentResult:
        """Deploy to Render (good for full-stack apps)"""
        
        start_time = time.time()
        
        try:
            # This would need Render API setup
            # For now, return a placeholder implementation
            
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="render",
                deployment_time_seconds=time.time() - start_time,
                error_message="Render deployment not yet implemented - requires API setup"
            )
            
        except Exception as e:
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="render",
                deployment_time_seconds=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _deploy_with_tunnel(self, webapp: WebappInfo) -> DeploymentResult:
        """Deploy using ngrok tunnel as fallback"""
        
        start_time = time.time()
        
        try:
            # Start the webapp locally first
            if webapp.start_command:
                PrintStyle(font_color="white").print(f"   Starting local server: {webapp.start_command}")
                
                # Start the webapp in background
                process = subprocess.Popen(
                    webapp.start_command,
                    shell=True,
                    cwd=webapp.local_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Wait a moment for the server to start
                await asyncio.sleep(5)
                
                # Check if process is still running
                if process.poll() is None:
                    # Server is running, create ngrok tunnel
                    tunnel_result = await self._create_ngrok_tunnel(webapp.local_port)
                    
                    if tunnel_result:
                        return DeploymentResult(
                            success=True,
                            public_url=tunnel_result,
                            deployment_service="ngrok_tunnel",
                            deployment_time_seconds=time.time() - start_time,
                            logs=[f"Local server started on port {webapp.local_port}"]
                        )
                
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="ngrok_tunnel",
                deployment_time_seconds=time.time() - start_time,
                error_message="Failed to start local server or create tunnel"
            )
            
        except Exception as e:
            return DeploymentResult(
                success=False,
                public_url=None,
                deployment_service="ngrok_tunnel",
                deployment_time_seconds=time.time() - start_time,
                error_message=str(e)
            )
    
    async def _create_ngrok_tunnel(self, port: int) -> Optional[str]:
        """Create ngrok tunnel for local port"""
        
        try:
            # Install ngrok if not available
            if not shutil.which("ngrok"):
                PrintStyle(font_color="yellow").print("   Installing ngrok...")
                subprocess.run("curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null", shell=True)
                subprocess.run("echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | sudo tee /etc/apt/sources.list.d/ngrok.list", shell=True)
                subprocess.run("sudo apt update && sudo apt install ngrok", shell=True)
            
            # Start ngrok tunnel
            PrintStyle(font_color="white").print(f"   Creating ngrok tunnel for port {port}...")
            
            tunnel_process = subprocess.Popen(
                f"ngrok http {port} --log=stdout",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for tunnel to establish and extract URL
            start_time = time.time()
            while time.time() - start_time < 30:  # 30 second timeout
                try:
                    # Check ngrok API for tunnel info
                    response = requests.get("http://localhost:4040/api/tunnels", timeout=2)
                    if response.status_code == 200:
                        tunnels = response.json().get("tunnels", [])
                        for tunnel in tunnels:
                            if tunnel.get("proto") == "https":
                                public_url = tunnel.get("public_url")
                                if public_url:
                                    PrintStyle(font_color="green").print(f"   ✅ Tunnel created: {public_url}")
                                    return public_url
                except:
                    pass
                
                await asyncio.sleep(2)
            
            return None
            
        except Exception as e:
            PrintStyle(font_color="red").print(f"   ❌ Ngrok tunnel failed: {e}")
            return None
    
    async def _ensure_vercel_cli(self):
        """Ensure Vercel CLI is installed"""
        if not shutil.which("vercel"):
            PrintStyle(font_color="white").print("   Installing Vercel CLI...")
            subprocess.run("npm install -g vercel", shell=True, check=True)
    
    async def _ensure_netlify_cli(self):
        """Ensure Netlify CLI is installed"""
        if not shutil.which("netlify"):
            PrintStyle(font_color="white").print("   Installing Netlify CLI...")
            subprocess.run("npm install -g netlify-cli", shell=True, check=True)
    
    async def _ensure_surge_cli(self):
        """Ensure Surge CLI is installed"""
        if not shutil.which("surge"):
            PrintStyle(font_color="white").print("   Installing Surge CLI...")
            subprocess.run("npm install -g surge", shell=True, check=True)

class AutomaticDeploymentSystem:
    """Main system that automatically deploys webapps for user accessibility"""
    
    def __init__(self, logger: Optional[Log] = None):
        self.logger = logger or Log()
        self.detector = WebappDetector(self.logger)
        self.cloud_deployer = CloudDeploymentService(self.logger)
        
        self.deployed_webapps = {}  # Track deployed webapps
        self.monitoring = False
        self.deployment_history = []
        
    async def start_monitoring(self):
        """Start monitoring for new webapps that need deployment"""
        
        self.monitoring = True
        PrintStyle(font_color="green").print("🚀 Automatic Deployment System: STARTED")
        PrintStyle(font_color="cyan").print("   Monitoring for webapps that need public deployment...")
        
        while self.monitoring:
            try:
                # Detect new webapps
                detected_webapps = self.detector.detect_new_webapps()
                
                for webapp in detected_webapps:
                    # Check if already deployed
                    if webapp.name not in self.deployed_webapps:
                        PrintStyle(font_color="yellow").print(f"🔍 New webapp detected: {webapp.name}")
                        
                        # Automatically deploy
                        await self._deploy_webapp_automatically(webapp)
                
                # Check every 30 seconds for new webapps
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.log(f"Deployment monitoring error: {e}")
                await asyncio.sleep(60)
    
    def stop_monitoring(self):
        """Stop webapp monitoring"""
        self.monitoring = False
        PrintStyle(font_color="yellow").print("🚀 Automatic Deployment System: STOPPED")
    
    async def _deploy_webapp_automatically(self, webapp: WebappInfo):
        """Automatically deploy a webapp and make it publicly accessible"""
        
        PrintStyle(font_color="cyan").print(f"🚀 Auto-deploying webapp: {webapp.name}")
        PrintStyle(font_color="white").print(f"   Type: {webapp.webapp_type} ({webapp.framework})")
        PrintStyle(font_color="white").print(f"   Path: {webapp.local_path}")
        
        try:
            webapp.deployment_status = "deploying"
            self.deployed_webapps[webapp.name] = webapp
            
            # Deploy to cloud service
            deployment_result = await self.cloud_deployer.deploy_webapp(webapp)
            
            if deployment_result.success:
                webapp.public_url = deployment_result.public_url
                webapp.deployment_status = "deployed"
                webapp.deployment_service = deployment_result.deployment_service
                
                PrintStyle(font_color="green").print(f"🎉 WEBAPP DEPLOYED SUCCESSFULLY!")
                PrintStyle(font_color="green").print(f"   📱 Webapp: {webapp.name}")
                PrintStyle(font_color="green").print(f"   🌐 Public URL: {webapp.public_url}")
                PrintStyle(font_color="green").print(f"   ☁️ Service: {deployment_result.deployment_service.title()}")
                PrintStyle(font_color="green").print(f"   ⏱️ Deploy Time: {deployment_result.deployment_time_seconds:.1f}s")
                
                # Record deployment
                self.deployment_history.append({
                    'webapp_name': webapp.name,
                    'public_url': webapp.public_url,
                    'service': deployment_result.deployment_service,
                    'timestamp': datetime.now().isoformat(),
                    'deploy_time': deployment_result.deployment_time_seconds,
                    'success': True
                })
                
                # Auto-test the deployed webapp
                await self._test_deployed_webapp(webapp)
                
                # Send email notification for VPS deployments
                if deployment_result.deployment_service == "vps":
                    await self._send_vps_deployment_email(webapp, deployment_result)
                
            else:
                webapp.deployment_status = "failed"
                
                PrintStyle(font_color="red").print(f"❌ Deployment failed for: {webapp.name}")
                PrintStyle(font_color="red").print(f"   Error: {deployment_result.error_message}")
                
                # Record failed deployment
                self.deployment_history.append({
                    'webapp_name': webapp.name,
                    'public_url': None,
                    'service': deployment_result.deployment_service,
                    'timestamp': datetime.now().isoformat(),
                    'deploy_time': deployment_result.deployment_time_seconds,
                    'success': False,
                    'error': deployment_result.error_message
                })
                
        except Exception as e:
            webapp.deployment_status = "failed"
            PrintStyle(font_color="red").print(f"💥 Deployment system error: {e}")
            self.logger.log(f"Deployment error for {webapp.name}: {e}")
    
    async def _test_deployed_webapp(self, webapp: WebappInfo):
        """Test that the deployed webapp is actually accessible"""
        
        if not webapp.public_url:
            return
        
        try:
            PrintStyle(font_color="cyan").print("🧪 Testing webapp accessibility...")
            
            # Test HTTP request to the deployed URL
            response = requests.get(webapp.public_url, timeout=30)
            
            if response.status_code == 200:
                PrintStyle(font_color="green").print("✅ Webapp is accessible and responding!")
                
                # Test if it's actually a webapp (not just a placeholder)
                content = response.text.lower()
                
                if any(keyword in content for keyword in ['<html', '<body', '<div', 'react', 'vue', 'app']):
                    PrintStyle(font_color="green").print("✅ Webapp content verified - ready for users!")
                else:
                    PrintStyle(font_color="yellow").print("⚠️ Webapp accessible but content may not be fully loaded")
            else:
                PrintStyle(font_color="yellow").print(f"⚠️ Webapp returned status code: {response.status_code}")
                
        except Exception as e:
            PrintStyle(font_color="red").print(f"❌ Webapp accessibility test failed: {e}")
    
    async def _send_vps_deployment_email(self, webapp: WebappInfo, deployment_result: DeploymentResult):
        """Send email notification for VPS deployment success"""
        
        try:
            # Import email service here to avoid circular imports
            from python.helpers.email_service import get_email_service
            
            email_service = get_email_service(self.logger)
            
            # Use a default email - in production this would come from user context
            user_email = "admin@innovatehub.ph"  # TODO: Get actual user email from context
            user_name = "Developer"  # TODO: Get actual user name from context
            
            PrintStyle(font_color="cyan").print("📧 Sending VPS deployment notification email...")
            
            email_result = await email_service.send_webapp_deployment_notification(
                to_email=user_email,
                to_name=user_name,
                webapp_name=webapp.name,
                webapp_url=deployment_result.public_url,
                deployment_service=deployment_result.deployment_service,
                webapp_type=webapp.webapp_type,
                deployment_time=deployment_result.deployment_time_seconds
            )
            
            if email_result.success:
                PrintStyle(font_color="green").print("✅ VPS deployment email sent successfully!")
                PrintStyle(font_color="white").print(f"   📧 Notified: {user_email}")
                PrintStyle(font_color="white").print(f"   📱 Webapp: {webapp.name}")
                PrintStyle(font_color="white").print(f"   🌐 URL: {deployment_result.public_url}")
            else:
                PrintStyle(font_color="yellow").print(f"⚠️ Email notification failed: {email_result.error_message}")
                
        except Exception as e:
            PrintStyle(font_color="red").print(f"❌ Error sending deployment email: {e}")
            self.logger.log(f"VPS deployment email error: {e}")
    
    async def deploy_specific_webapp(self, webapp_path: str, webapp_name: str = None) -> Optional[str]:
        """Deploy a specific webapp and return the public URL"""
        
        if not webapp_name:
            webapp_name = os.path.basename(webapp_path)
        
        # Analyze the webapp
        webapp_info = self.detector._analyze_webapp_directory(webapp_path, webapp_name)
        
        if not webapp_info:
            PrintStyle(font_color="red").print(f"❌ Could not detect webapp type at: {webapp_path}")
            return None
        
        # Deploy it
        await self._deploy_webapp_automatically(webapp_info)
        
        return webapp_info.public_url
    
    def get_deployment_status(self) -> Dict[str, Any]:
        """Get current deployment system status"""
        
        total_deployments = len(self.deployment_history)
        successful_deployments = sum(1 for d in self.deployment_history if d['success'])
        
        return {
            'monitoring': self.monitoring,
            'total_webapps_deployed': len(self.deployed_webapps),
            'deployment_history_count': total_deployments,
            'successful_deployments': successful_deployments,
            'success_rate': successful_deployments / total_deployments if total_deployments > 0 else 0,
            'active_webapps': [
                {
                    'name': webapp.name,
                    'url': webapp.public_url,
                    'service': webapp.deployment_service,
                    'status': webapp.deployment_status
                }
                for webapp in self.deployed_webapps.values()
                if webapp.deployment_status == 'deployed'
            ]
        }
    
    def get_user_accessible_webapps(self) -> List[Dict[str, str]]:
        """Get list of webapps that users can actually access"""
        
        accessible_webapps = []
        
        for webapp in self.deployed_webapps.values():
            if webapp.deployment_status == "deployed" and webapp.public_url:
                accessible_webapps.append({
                    'name': webapp.name,
                    'url': webapp.public_url,
                    'type': webapp.webapp_type,
                    'framework': webapp.framework,
                    'deployed_on': webapp.deployment_service,
                    'created_at': webapp.created_at
                })
        
        return accessible_webapps

# Global deployment system instance
_deployment_system = None

def get_deployment_system(logger: Optional[Log] = None) -> AutomaticDeploymentSystem:
    """Get or create global deployment system"""
    global _deployment_system
    
    if _deployment_system is None:
        _deployment_system = AutomaticDeploymentSystem(logger)
        
    return _deployment_system

async def start_automatic_deployment_monitoring():
    """Start automatic deployment monitoring"""
    deployment_system = get_deployment_system()
    await deployment_system.start_monitoring()

def deploy_webapp_now(webapp_path: str, webapp_name: str = None) -> str:
    """Immediately deploy a webapp and return public URL"""
    deployment_system = get_deployment_system()
    return asyncio.run(deployment_system.deploy_specific_webapp(webapp_path, webapp_name))