#!/usr/bin/env python
import os
import requests
import json
import subprocess
import time
import signal
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
VAPI_API_KEY = os.getenv('VAPI_API_KEY')
VAPI_API_BASE = 'https://api.vapi.ai'
TOOL_NAME = 'vocabularyTool'
TOOL_DESCRIPTION = 'Tool to add, review and search vocabulary words'
TOOL_PARAMETERS = {
    "type": "object",
    "required": ["action"],
    "properties": {
        "word": {
            "type": "string",
            "description": "The vocabulary word to add or search for"
        },
        "action": {
            "type": "string",
            "description": "The action to perform (add, list, search)"
        },
        "definition": {
            "type": "string",
            "description": "The definition of the word being added"
        }
    }
}
ASSISTANT_ID = "4df2000e-479b-434e-8373-6ca1809233e2"  # Language Learning Assistant ID

# Headers for API requests
headers = {
    'Authorization': f'Bearer {VAPI_API_KEY}',
    'Content-Type': 'application/json'
}

def check_api_key():
    """Verify the API key is valid"""
    if not VAPI_API_KEY:
        print("Error: VAPI_API_KEY not found in .env file")
        return False
    
    # Test the API key with a simple request
    try:
        response = requests.get(
            f'{VAPI_API_BASE}/assistants/{ASSISTANT_ID}',
            headers=headers
        )
        if response.status_code == 200:
            print("✅ API key is valid")
            return True
        else:
            print(f"❌ API key validation failed: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"❌ API key validation error: {e}")
        return False

def create_vocabulary_tool():
    """Create the vocabulary tool in VAPI"""
    print("\nCreating vocabulary tool...")
    
    tool_data = {
        "type": "function",
        "function": {
            "name": TOOL_NAME,
            "description": TOOL_DESCRIPTION,
            "parameters": TOOL_PARAMETERS,
            "async": False
        }
    }
    
    try:
        response = requests.post(
            f'{VAPI_API_BASE}/tools',
            headers=headers,
            json=tool_data
        )
        
        if response.status_code in [200, 201]:
            tool_id = response.json().get('id')
            print(f"✅ Tool created successfully with ID: {tool_id}")
            return tool_id
        else:
            print(f"❌ Tool creation failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"❌ Tool creation error: {e}")
        return None

def update_server_url(tool_id, server_url):
    """Update the server URL for the tool"""
    print(f"\nUpdating server URL to: {server_url}")
    
    update_data = {
        "server": {
            "url": server_url,
            "timeoutSeconds": 30
        }
    }
    
    try:
        response = requests.patch(
            f'{VAPI_API_BASE}/tools/{tool_id}',
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            print("✅ Server URL updated successfully")
            return True
        else:
            print(f"❌ Server URL update failed: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"❌ Server URL update error: {e}")
        return False

def assign_tool_to_assistant(tool_id):
    """Assign the tool to the Language Learning Assistant"""
    print(f"\nAssigning tool to assistant {ASSISTANT_ID}...")
    
    # First get current assistant config
    try:
        response = requests.get(
            f'{VAPI_API_BASE}/assistants/{ASSISTANT_ID}',
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Failed to get assistant: {response.status_code} {response.text}")
            return False
        
        assistant_data = response.json()
        
        # Update the tool IDs list
        model_config = assistant_data.get('model', {})
        tool_ids = model_config.get('toolIds', [])
        
        # Skip if tool is already assigned
        if tool_id in tool_ids:
            print("✅ Tool is already assigned to the assistant")
            return True
        
        # Add the new tool ID
        tool_ids.append(tool_id)
        
        # Update the assistant
        update_data = {
            "model": {
                "toolIds": tool_ids
            }
        }
        
        response = requests.patch(
            f'{VAPI_API_BASE}/assistants/{ASSISTANT_ID}',
            headers=headers,
            json=update_data
        )
        
        if response.status_code == 200:
            print("✅ Tool assigned to assistant successfully")
            return True
        else:
            print(f"❌ Tool assignment failed: {response.status_code} {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Tool assignment error: {e}")
        return False

def start_flask_server():
    """Start the Flask server in a subprocess"""
    print("\nStarting Flask server...")
    try:
        # Start the flask server
        server_process = subprocess.Popen(
            ["python", "ngrok_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        if server_process.poll() is None:
            print("✅ Flask server started successfully")
            return server_process
        else:
            stdout, stderr = server_process.communicate()
            print(f"❌ Flask server failed to start: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Flask server error: {e}")
        return None

def start_ngrok(port=5000):
    """Start ngrok and get the public URL"""
    print("\nStarting ngrok...")
    try:
        # Check if ngrok is installed
        subprocess.run(["ngrok", "--version"], 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE, 
                       check=True)
        
        # Start ngrok
        ngrok_process = subprocess.Popen(
            ["ngrok", "http", str(port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Give it a moment to start
        time.sleep(2)
        
        if ngrok_process.poll() is None:
            # Get the ngrok URL
            try:
                response = requests.get("http://localhost:4040/api/tunnels")
                tunnels = response.json()["tunnels"]
                if tunnels:
                    ngrok_url = tunnels[0]["public_url"]
                    print(f"✅ ngrok started successfully at: {ngrok_url}")
                    return ngrok_process, ngrok_url
                else:
                    print("❌ No ngrok tunnels found")
                    return ngrok_process, None
            except Exception as e:
                print(f"❌ Failed to get ngrok URL: {e}")
                return ngrok_process, None
        else:
            stdout, stderr = ngrok_process.communicate()
            print(f"❌ ngrok failed to start: {stderr}")
            return None, None
    except subprocess.CalledProcessError:
        print("❌ ngrok is not installed. Please install it first.")
        print("   Mac: brew install ngrok")
        print("   Windows: choco install ngrok")
        print("   Or download from: https://ngrok.com/download")
        return None, None
    except Exception as e:
        print(f"❌ ngrok error: {e}")
        return None, None

def cleanup(server_process, ngrok_process):
    """Clean up processes on exit"""
    if server_process and server_process.poll() is None:
        server_process.terminate()
        print("Flask server stopped")
    
    if ngrok_process and ngrok_process.poll() is None:
        ngrok_process.terminate()
        print("ngrok stopped")

def main():
    """Main function to set up the vocabulary tool integration"""
    print("=== VAPI Vocabulary Tool Setup ===\n")
    
    # Set up signal handlers for clean exit
    def signal_handler(sig, frame):
        print("\nExiting...")
        if 'server_process' in locals() and server_process:
            cleanup(server_process, ngrok_process)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Step 1: Validate API key
    if not check_api_key():
        return
    
    # Step 2: Start Flask server
    server_process = start_flask_server()
    if not server_process:
        return
    
    # Step 3: Start ngrok
    ngrok_process, ngrok_url = start_ngrok()
    if not ngrok_url:
        cleanup(server_process, None)
        return
    
    # Step 4: Construct the complete webhook URL
    webhook_url = f"{ngrok_url}/api/vocabulary"
    
    # Step 5: Create the vocabulary tool
    tool_id = create_vocabulary_tool()
    if not tool_id:
        cleanup(server_process, ngrok_process)
        return
    
    # Step 6: Update the server URL
    if not update_server_url(tool_id, webhook_url):
        cleanup(server_process, ngrok_process)
        return
    
    # Step 7: Assign the tool to the assistant
    if not assign_tool_to_assistant(tool_id):
        cleanup(server_process, ngrok_process)
        return
    
    # All done!
    print("\n✅ Setup complete! The vocabulary tool is now ready to use.")
    print(f"Tool ID: {tool_id}")
    print(f"Webhook URL: {webhook_url}")
    print("\nPress Ctrl+C to stop the server and ngrok")
    
    # Keep the script running to maintain the server and ngrok
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        cleanup(server_process, ngrok_process)

if __name__ == "__main__":
    main() 