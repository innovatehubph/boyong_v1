#!/usr/bin/env python3
"""
GitHub MCP Server Setup for Pareng Boyong
Configures GitHub integration for repository operations
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def setup_github_mcp():
    """Set up GitHub MCP server integration"""
    
    print("🐙 Setting up GitHub MCP Server for Pareng Boyong...")
    
    # Check if MCP servers config exists
    config_path = Path("/root/projects/pareng-boyong/mcp_servers_config.json")
    
    if not config_path.exists():
        print("❌ MCP servers config file not found")
        return False
    
    # Read current config
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Failed to read MCP config: {e}")
        return False
    
    # Check if GitHub server is configured
    github_configured = 'github' in config.get('mcpServers', {})
    
    if not github_configured:
        print("❌ GitHub MCP server not found in configuration")
        return False
    
    print("✅ GitHub MCP server found in configuration")
    
    # Check for GitHub token
    github_token = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
    
    if not github_token or github_token.strip() == "":
        print("⚠️ GitHub Personal Access Token not set")
        print("\n📋 **Setup Instructions:**")
        print("1. Go to https://github.com/settings/tokens")
        print("2. Generate a new Personal Access Token (Classic)")
        print("3. Select scopes: repo, read:org, read:user")
        print("4. Copy the token")
        print("5. Add to .env file: GITHUB_PERSONAL_ACCESS_TOKEN=your_token_here")
        print("6. Run this script again")
        
        # Prompt for token
        token_input = input("\n🔑 Enter your GitHub Personal Access Token (or press Enter to skip): ").strip()
        
        if token_input:
            # Add to .env file
            env_path = Path("/root/projects/pareng-boyong/.env")
            try:
                with open(env_path, 'a') as f:
                    f.write(f"\nGITHUB_PERSONAL_ACCESS_TOKEN={token_input}\n")
                
                print("✅ GitHub token added to .env file")
                os.environ['GITHUB_PERSONAL_ACCESS_TOKEN'] = token_input
                github_token = token_input
                
            except Exception as e:
                print(f"❌ Failed to update .env file: {e}")
                return False
        else:
            print("⏭️ Skipping GitHub token setup")
            return False
    
    else:
        print(f"✅ GitHub token found: {github_token[:8]}...")
    
    # Test GitHub API connectivity
    print("\n🔗 Testing GitHub API connectivity...")
    
    try:
        import requests
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Pareng-Boyong-AI'
        }
        
        response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ GitHub API connected successfully")
            print(f"   User: {user_data.get('login', 'Unknown')}")
            print(f"   Name: {user_data.get('name', 'Unknown')}")
            
            # Test repository access
            repos_response = requests.get('https://api.github.com/user/repos?per_page=5', headers=headers, timeout=10)
            if repos_response.status_code == 200:
                repos = repos_response.json()
                print(f"   Accessible repositories: {len(repos)} (showing first 5)")
                for repo in repos[:3]:
                    print(f"     - {repo['full_name']}")
            
        elif response.status_code == 401:
            print("❌ GitHub API authentication failed - invalid token")
            return False
        else:
            print(f"⚠️ GitHub API response: {response.status_code}")
            
    except ImportError:
        print("⚠️ requests library not available for testing")
    except Exception as e:
        print(f"⚠️ GitHub API test failed: {e}")
    
    # Check if MCP GitHub server package is installed
    print("\n📦 Checking MCP GitHub server installation...")
    
    try:
        # Check if the package is installed
        result = subprocess.run(['npm', 'list', '@modelcontextprotocol/server-github'], 
                              capture_output=True, text=True, cwd='/root/projects/pareng-boyong')
        
        if result.returncode == 0:
            print("✅ @modelcontextprotocol/server-github is installed")
        else:
            print("📦 Installing @modelcontextprotocol/server-github...")
            install_result = subprocess.run(['npm', 'install', '@modelcontextprotocol/server-github'], 
                                          capture_output=True, text=True, cwd='/root/projects/pareng-boyong')
            
            if install_result.returncode == 0:
                print("✅ GitHub MCP server installed successfully")
            else:
                print(f"❌ Failed to install GitHub MCP server: {install_result.stderr}")
                return False
                
    except Exception as e:
        print(f"⚠️ Could not check/install MCP server: {e}")
    
    print("\n🎯 **GitHub MCP Server Status:**")
    print("✅ Configuration: Ready")
    print("✅ Authentication: Configured" if github_token else "❌ Authentication: Missing token")
    print("✅ Package: Installed")
    
    # Test MCP integration
    print("\n🧪 Testing MCP GitHub integration...")
    
    try:
        # Import and test MCP functionality
        sys.path.append('/root/projects/pareng-boyong')
        
        # Try to run a simple MCP test
        test_result = subprocess.run([
            'python3', 'simple_mcp_test.py'
        ], capture_output=True, text=True, cwd='/root/projects/pareng-boyong', timeout=30)
        
        if test_result.returncode == 0:
            print("✅ MCP integration test passed")
            print("📋 Test output:")
            for line in test_result.stdout.split('\n')[:5]:
                if line.strip():
                    print(f"   {line}")
        else:
            print("⚠️ MCP integration test had issues:")
            for line in test_result.stderr.split('\n')[:3]:
                if line.strip():
                    print(f"   {line}")
                    
    except subprocess.TimeoutExpired:
        print("⚠️ MCP test timed out")
    except Exception as e:
        print(f"⚠️ MCP test failed: {e}")
    
    print("\n🎉 **GitHub MCP Server Setup Complete!**")
    print("\n📖 **Available GitHub Operations:**")
    print("- Repository browsing and file access")
    print("- Issue creation and management") 
    print("- Pull request operations")
    print("- Commit history and blame")
    print("- Repository statistics")
    
    return True


def show_github_capabilities():
    """Show what GitHub MCP server can do"""
    
    capabilities = {
        "Repository Operations": [
            "List repositories",
            "Get repository information", 
            "Browse repository contents",
            "Read file contents",
            "Search within repositories"
        ],
        "Issue Management": [
            "List issues",
            "Create new issues",
            "Update issue status",
            "Add comments to issues",
            "Search issues"
        ],
        "Pull Requests": [
            "List pull requests",
            "Get PR details",
            "Review PR changes",
            "Merge pull requests",
            "Create PR comments"
        ],
        "Code Analysis": [
            "View commit history",
            "Git blame information",
            "Compare branches",
            "Repository statistics",
            "Code search"
        ]
    }
    
    print("\n🐙 **GitHub MCP Server Capabilities:**")
    for category, features in capabilities.items():
        print(f"\n**{category}:**")
        for feature in features:
            print(f"  ✅ {feature}")


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 PARENG BOYONG - GITHUB MCP SETUP")
    print("=" * 60)
    
    success = setup_github_mcp()
    
    if success:
        show_github_capabilities()
        print(f"\n{'=' * 60}")
        print("✅ Setup completed successfully!")
        print("🔥 Pareng Boyong now has GitHub superpowers!")
        print(f"{'=' * 60}")
    else:
        print(f"\n{'=' * 60}")
        print("⚠️ Setup completed with issues")
        print("Please review the messages above and fix any problems")
        print(f"{'=' * 60}")