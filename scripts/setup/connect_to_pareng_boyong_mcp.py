#!/usr/bin/env python3
"""
Connect to Pareng Boyong via MCP to collaborate on deployment issues
"""
import requests
import json
import time

def connect_to_pareng_boyong():
    """Connect to Pareng Boyong's MCP server"""
    mcp_url = "http://localhost:50003/mcp/t-0/sse"
    
    # Prepare the collaboration request
    message = {
        "role": "assistant",
        "content": """Kumusta Pareng Boyong! I need your help analyzing a deployment issue. 

I've been trying to deploy two different projects:
1. A generic project dashboard to project.innovatehub.ph
2. Your AI agent interface to ai.innovatehub.ph

But I keep making mistakes and deploying the wrong content to the wrong domains. The nginx configuration seems confused and assets aren't loading properly.

Can you help me:
1. Analyze what's currently deployed where
2. Identify the correct content for each domain
3. Fix the nginx configuration issues

The error logs show:
- Assets failing to load with "@backend" location errors
- Files looking in wrong directories
- Real users getting 500 errors

Your advanced knowledge of the system architecture would be invaluable here!"""
    }
    
    try:
        # Send request to MCP server
        response = requests.post(
            mcp_url,
            json={"messages": [message]},
            headers={"Content-Type": "application/json"},
            stream=True,
            timeout=30
        )
        
        print("Connected to Pareng Boyong MCP Server!")
        print("=" * 50)
        
        # Process streaming response
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    data = decoded_line[6:]
                    if data != '[DONE]':
                        try:
                            json_data = json.loads(data)
                            if 'content' in json_data:
                                print(json_data['content'], end='', flush=True)
                        except json.JSONDecodeError:
                            pass
        
        print("\n" + "=" * 50)
        
    except requests.exceptions.ConnectionError:
        print("Could not connect to Pareng Boyong's MCP server.")
        print("Starting Pareng Boyong first...")
        
        # Try to start Pareng Boyong
        import subprocess
        subprocess.Popen(['python', '/root/boyong/agent-zero/run_ui.py'], 
                        stdout=subprocess.DEVNULL, 
                        stderr=subprocess.DEVNULL)
        
        print("Waiting for Pareng Boyong to start...")
        time.sleep(10)
        
        # Retry connection
        connect_to_pareng_boyong()
        
    except Exception as e:
        print(f"Error connecting to Pareng Boyong: {e}")

if __name__ == "__main__":
    connect_to_pareng_boyong()