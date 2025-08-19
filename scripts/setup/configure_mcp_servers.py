#!/usr/bin/env python3
"""
Enhanced MCP Servers Configuration Script
Installs and configures multiple useful MCP servers for Pareng Boyong
Including GitHub, Context7, and other popular MCP servers
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import shutil


class MCPServerConfigurator:
    """Configure and install MCP servers for Pareng Boyong"""
    
    def __init__(self):
        self.project_root = Path("/root/projects/pareng-boyong")
        self.mcp_servers_config = {
            "mcpServers": {}
        }
        
        # Available MCP servers to install
        self.available_servers = {
            "github": {
                "package": "@modelcontextprotocol/server-github",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-github"],
                "env_vars": ["GITHUB_PERSONAL_ACCESS_TOKEN"],
                "description": "GitHub integration for repository management",
                "required_setup": self.setup_github_server
            },
            "context7": {
                "package": "@upstash/context7-mcp",
                "command": "npx", 
                "args": ["@upstash/context7-mcp"],
                "env_vars": ["UPSTASH_REDIS_REST_URL", "UPSTASH_REDIS_REST_TOKEN"],
                "description": "Context7 for persistent memory and context management",
                "required_setup": self.setup_context7_server
            },
            "fetch": {
                "package": "@modelcontextprotocol/server-fetch",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-fetch"],
                "env_vars": [],
                "description": "Web fetching capabilities",
                "required_setup": self.setup_fetch_server
            },
            "filesystem": {
                "package": "@modelcontextprotocol/server-filesystem",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-filesystem", "/root/projects/pareng-boyong"],
                "env_vars": [],
                "description": "Local filesystem access",
                "required_setup": self.setup_filesystem_server
            },
            "sqlite": {
                "package": "@modelcontextprotocol/server-sqlite",
                "command": "npx",
                "args": ["@modelcontextprotocol/server-sqlite", "--db-path", "/root/projects/pareng-boyong/data/pareng_boyong.db"],
                "env_vars": [],
                "description": "SQLite database operations",
                "required_setup": self.setup_sqlite_server
            },
            "playwright": {
                "package": "@playwright/mcp",
                "command": "npx",
                "args": ["@playwright/mcp"],
                "env_vars": [],
                "description": "Web automation with Playwright",
                "required_setup": self.setup_playwright_server
            }
        }
    
    def print_status(self, message: str, status: str = "info"):
        """Print colored status messages"""
        colors = {
            "info": "\033[94m",     # Blue
            "success": "\033[92m",  # Green
            "warning": "\033[93m",  # Yellow
            "error": "\033[91m",    # Red
            "reset": "\033[0m"      # Reset
        }
        
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "warning": "⚠️", 
            "error": "❌"
        }
        
        print(f"{colors.get(status, '')}{icons.get(status, '')} {message}{colors['reset']}")
    
    def check_prerequisites(self) -> bool:
        """Check if prerequisites are installed"""
        self.print_status("Checking prerequisites...")
        
        # Check Node.js and npm
        try:
            result = subprocess.run(["node", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.print_status(f"Node.js version: {result.stdout.strip()}", "success")
            else:
                self.print_status("Node.js not found", "error")
                return False
        except FileNotFoundError:
            self.print_status("Node.js not found", "error")
            return False
        
        try:
            result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                self.print_status(f"npm version: {result.stdout.strip()}", "success")
            else:
                self.print_status("npm not found", "error")
                return False
        except FileNotFoundError:
            self.print_status("npm not found", "error")
            return False
        
        # Check Python MCP SDK
        try:
            import mcp
            try:
                version = getattr(mcp, '__version__', 'unknown')
                self.print_status(f"MCP SDK version: {version}", "success")
            except:
                self.print_status("MCP SDK installed (version unknown)", "success")
        except ImportError:
            self.print_status("MCP SDK not found - installing...", "warning")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "mcp"], check=True)
                self.print_status("MCP SDK installed successfully", "success")
            except subprocess.CalledProcessError:
                self.print_status("Failed to install MCP SDK", "error")
                return False
        
        return True
    
    def install_mcp_server(self, server_name: str, server_config: Dict[str, Any]) -> bool:
        """Install a specific MCP server"""
        self.print_status(f"Installing {server_name} MCP server...")
        
        try:
            # Install the package globally to make it available
            install_cmd = ["npm", "install", "-g", server_config["package"]]
            result = subprocess.run(install_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.print_status(f"Successfully installed {server_config['package']}", "success")
                return True
            else:
                self.print_status(f"Failed to install {server_config['package']}: {result.stderr}", "error")
                return False
                
        except Exception as e:
            self.print_status(f"Error installing {server_name}: {str(e)}", "error")
            return False
    
    def setup_github_server(self) -> Dict[str, Any]:
        """Setup GitHub MCP server configuration"""
        self.print_status("Configuring GitHub MCP server...")
        
        # Check if GitHub token exists
        github_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN")
        if not github_token:
            self.print_status("GITHUB_PERSONAL_ACCESS_TOKEN not found in environment", "warning")
            self.print_status("Please set your GitHub Personal Access Token:", "info")
            self.print_status("export GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here", "info")
        
        return {
            "command": "npx",
            "args": ["@modelcontextprotocol/server-github"],
            "env": {
                "GITHUB_PERSONAL_ACCESS_TOKEN": github_token or "${GITHUB_PERSONAL_ACCESS_TOKEN}"
            }
        }
    
    def setup_context7_server(self) -> Dict[str, Any]:
        """Setup Context7 MCP server configuration"""
        self.print_status("Configuring Context7 MCP server...")
        
        # Check for Upstash Redis credentials
        redis_url = os.getenv("UPSTASH_REDIS_REST_URL")
        redis_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
        
        if not redis_url or not redis_token:
            self.print_status("Upstash Redis credentials not found", "warning")
            self.print_status("Please set your Upstash Redis credentials:", "info")
            self.print_status("export UPSTASH_REDIS_REST_URL=your_redis_url", "info")
            self.print_status("export UPSTASH_REDIS_REST_TOKEN=your_redis_token", "info")
        
        return {
            "command": "npx",
            "args": ["@upstash/context7-mcp"],
            "env": {
                "UPSTASH_REDIS_REST_URL": redis_url or "${UPSTASH_REDIS_REST_URL}",
                "UPSTASH_REDIS_REST_TOKEN": redis_token or "${UPSTASH_REDIS_REST_TOKEN}"
            }
        }
    
    def setup_fetch_server(self) -> Dict[str, Any]:
        """Setup Fetch MCP server configuration"""
        self.print_status("Configuring Fetch MCP server...")
        
        return {
            "command": "npx",
            "args": ["@modelcontextprotocol/server-fetch"]
        }
    
    def setup_filesystem_server(self) -> Dict[str, Any]:
        """Setup Filesystem MCP server configuration"""
        self.print_status("Configuring Filesystem MCP server...")
        
        # Create allowed paths for filesystem access
        allowed_paths = [
            str(self.project_root),
            str(self.project_root / "pareng_boyong_deliverables"),
            "/tmp"
        ]
        
        return {
            "command": "npx",
            "args": ["@modelcontextprotocol/server-filesystem"] + allowed_paths
        }
    
    def setup_sqlite_server(self) -> Dict[str, Any]:
        """Setup SQLite MCP server configuration"""
        self.print_status("Configuring SQLite MCP server...")
        
        # Ensure data directory exists
        data_dir = self.project_root / "data"
        data_dir.mkdir(exist_ok=True)
        
        db_path = data_dir / "pareng_boyong.db"
        
        return {
            "command": "npx",
            "args": ["@modelcontextprotocol/server-sqlite", "--db-path", str(db_path)]
        }
    
    def setup_playwright_server(self) -> Dict[str, Any]:
        """Setup Playwright MCP server configuration"""
        self.print_status("Configuring Playwright MCP server...")
        
        return {
            "command": "npx",
            "args": ["@playwright/mcp"]
        }
    
    def configure_servers(self, servers_to_install: List[str]) -> Dict[str, Any]:
        """Configure the specified MCP servers"""
        self.print_status("Configuring MCP servers...")
        
        config = {"mcpServers": {}}
        
        for server_name in servers_to_install:
            if server_name not in self.available_servers:
                self.print_status(f"Unknown server: {server_name}", "warning")
                continue
            
            server_info = self.available_servers[server_name]
            
            # Install the server
            if not self.install_mcp_server(server_name, server_info):
                self.print_status(f"Skipping configuration for {server_name} due to installation failure", "warning")
                continue
            
            # Setup server configuration
            if server_info.get("required_setup"):
                server_config = server_info["required_setup"]()
                config["mcpServers"][server_name] = server_config
                self.print_status(f"Configured {server_name} MCP server", "success")
            else:
                self.print_status(f"No specific configuration needed for {server_name}", "info")
        
        return config
    
    def save_configuration(self, config: Dict[str, Any]):
        """Save the MCP configuration"""
        self.print_status("Saving MCP configuration...")
        
        # Create a configuration file for reference
        config_file = self.project_root / "mcp_servers_config.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            
            self.print_status(f"Configuration saved to {config_file}", "success")
            
            # Print the configuration for manual setting in UI
            self.print_status("MCP Servers Configuration JSON:", "info")
            print(json.dumps(config, indent=2))
            
        except Exception as e:
            self.print_status(f"Failed to save configuration: {str(e)}", "error")
    
    def show_setup_instructions(self):
        """Show post-installation setup instructions"""
        self.print_status("MCP Servers Setup Complete!", "success")
        
        print("\n" + "="*60)
        print("📋 SETUP INSTRUCTIONS")
        print("="*60)
        
        print("\n1. 🔑 Required Environment Variables:")
        print("   Add these to your .env file if not already present:")
        print("   ")
        print("   # GitHub MCP Server")
        print("   GITHUB_PERSONAL_ACCESS_TOKEN=your_github_token_here")
        print("   ")
        print("   # Context7 MCP Server (optional)")
        print("   UPSTASH_REDIS_REST_URL=your_redis_url")
        print("   UPSTASH_REDIS_REST_TOKEN=your_redis_token")
        
        print("\n2. 🔧 Manual Configuration:")
        print("   - Copy the JSON configuration above")
        print("   - Go to Pareng Boyong Settings > MCP Servers")
        print("   - Paste the configuration in the MCP Servers field")
        print("   - Save the settings")
        
        print("\n3. 🧪 Test the Setup:")
        print("   Ask Pareng Boyong:")
        print("   - 'List my GitHub repositories'")
        print("   - 'Fetch content from a website'")
        print("   - 'Show files in the current directory'")
        
        print("\n4. 📚 Available MCP Tools:")
        for name, info in self.available_servers.items():
            print(f"   • {name}: {info['description']}")
        
        print("\n" + "="*60)
    
    def run_configuration(self, servers: Optional[List[str]] = None):
        """Run the complete MCP server configuration"""
        self.print_status("Starting MCP Servers Configuration", "info")
        
        # Use all servers if none specified
        if servers is None:
            servers = list(self.available_servers.keys())
        
        # Check prerequisites
        if not self.check_prerequisites():
            self.print_status("Prerequisites check failed. Aborting.", "error")
            return False
        
        # Configure servers
        config = self.configure_servers(servers)
        
        # Save configuration
        if config["mcpServers"]:
            self.save_configuration(config)
            self.show_setup_instructions()
            return True
        else:
            self.print_status("No servers were successfully configured", "error")
            return False


def main():
    """Main configuration script"""
    configurator = MCPServerConfigurator()
    
    # Parse command line arguments for specific servers
    if len(sys.argv) > 1:
        servers_to_install = sys.argv[1:]
        print(f"Installing specific servers: {', '.join(servers_to_install)}")
    else:
        # Install recommended servers by default
        servers_to_install = ["github", "context7", "fetch", "filesystem"]
        print("Installing recommended MCP servers...")
    
    success = configurator.run_configuration(servers_to_install)
    
    if success:
        print("\n🎉 MCP Servers configuration completed successfully!")
        return 0
    else:
        print("\n❌ MCP Servers configuration failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())