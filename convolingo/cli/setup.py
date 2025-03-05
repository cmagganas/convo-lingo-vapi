import logging
import sys
import json
import requests
import time
import signal
import os
from typing import Dict, Any, Optional

from convolingo.utils.config import config
from convolingo.utils.ngrok_helper import NgrokTunnel
from convolingo.api.server import WebhookServer

# Set up logging
logger = logging.getLogger(__name__)

# Constants
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
        "language": {
            "type": "string",
            "description": "The language the word is in"
        },
        "translation": {
            "type": "string",
            "description": "The translation of the word"
        },
        "notes": {
            "type": "string",
            "description": "Additional notes about the word"
        }
    }
}


class SetupTool:
    """Tool for setting up and configuring the vocabulary tool with VAPI"""
    
    def __init__(self):
        """Initialize the setup tool"""
        self.api_key = config.api_key
        self.api_base = config.api_base
        self.server = None
        self.server_process = None
        self.ngrok = NgrokTunnel()
    
    def check_api_key(self) -> bool:
        """
        Check if the API key is valid
        
        Returns:
            bool: True if API key is valid, False otherwise
        """
        try:
            # Make a simple API call to validate the key
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            response = requests.get(
                f"{self.api_base}/assistants",
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info("API key is valid")
                return True
            else:
                logger.error(
                    f"API key validation failed: {response.status_code} {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error checking API key: {e}")
            return False
    
    def create_vocabulary_tool(self) -> Optional[str]:
        """
        Create the vocabulary tool in VAPI
        
        Returns:
            str: Tool ID if successful, None otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Create the tool
            payload = {
                "name": TOOL_NAME,
                "description": TOOL_DESCRIPTION,
                "input_schema": TOOL_PARAMETERS
            }
            
            response = requests.post(
                f"{self.api_base}/tools",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                data = response.json()
                tool_id = data.get("id")
                logger.info(f"Vocabulary tool created with ID: {tool_id}")
                return tool_id
            else:
                logger.error(
                    f"Failed to create tool: {response.status_code} {response.text}"
                )
                return None
        except Exception as e:
            logger.error(f"Error creating vocabulary tool: {e}")
            return None
    
    def update_server_url(self, tool_id: str, server_url: str) -> bool:
        """
        Update the server URL for the tool
        
        Args:
            tool_id: The tool ID
            server_url: The server URL
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Update the tool
            payload = {
                "server_url": server_url
            }
            
            response = requests.patch(
                f"{self.api_base}/tools/{tool_id}",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Server URL updated to: {server_url}")
                return True
            else:
                logger.error(
                    f"Failed to update server URL: {response.status_code} {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error updating server URL: {e}")
            return False
    
    def assign_tool_to_assistant(self, tool_id: str) -> bool:
        """
        Assign the tool to the assistant
        
        Args:
            tool_id: The tool ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from convolingo.utils.config import ASSISTANT_ID
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Get current assistant tools
            response = requests.get(
                f"{self.api_base}/assistants/{ASSISTANT_ID}",
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(
                    f"Failed to get assistant: {response.status_code} {response.text}"
                )
                return False
            
            assistant_data = response.json()
            current_tools = assistant_data.get("tools", [])
            
            # Check if tool is already assigned
            for tool in current_tools:
                if tool.get("id") == tool_id:
                    logger.info("Tool already assigned to assistant")
                    return True
            
            # Add the new tool
            current_tools.append({"id": tool_id})
            
            # Update the assistant
            payload = {
                "tools": current_tools
            }
            
            response = requests.patch(
                f"{self.api_base}/assistants/{ASSISTANT_ID}",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                logger.info(f"Tool assigned to assistant {ASSISTANT_ID}")
                return True
            else:
                logger.error(
                    f"Failed to assign tool: {response.status_code} {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Error assigning tool to assistant: {e}")
            return False
    
    def run_setup(self, run_server: bool = True, tool_id: str = None) -> None:
        """
        Run the complete setup process
        
        Args:
            run_server: Whether to run the webhook server
            tool_id: Optional tool ID (if not provided, will create a new tool)
        """
        # Check API key
        if not self.check_api_key():
            logger.error("API key is invalid. Please check your .env file.")
            return

        # Start webhook server if requested
        if run_server:
            # Start ngrok tunnel
            server_url = self.ngrok.start()
            if not server_url:
                logger.error("Failed to start ngrok tunnel. Exiting.")
                return
                
            # Add API path to URL
            webhook_url = self.ngrok.get_api_url("api/vocabulary")
            
            # Create server
            self.server = WebhookServer()
            
            # Start server in a thread
            import threading
            server_thread = threading.Thread(
                target=self.server.run,
                kwargs={"debug": False},
                daemon=True
            )
            server_thread.start()
            
            logger.info(f"Webhook server running at {webhook_url}")
            
            # Create or update tool
            if not tool_id:
                tool_id = self.create_vocabulary_tool()
                if not tool_id:
                    logger.error("Failed to create vocabulary tool. Exiting.")
                    self.ngrok.stop()
                    return
            
            # Update server URL
            if not self.update_server_url(tool_id, webhook_url):
                logger.error("Failed to update server URL. Exiting.")
                self.ngrok.stop()
                return
            
            # Assign tool to assistant
            if not self.assign_tool_to_assistant(tool_id):
                logger.error("Failed to assign tool to assistant. Exiting.")
                self.ngrok.stop()
                return
            
            # Setup complete
            logger.info("Setup complete! The webhook server is running.")
            logger.info("Press Ctrl+C to stop.")
            
            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopping webhook server...")
            finally:
                self.ngrok.stop()
        else:
            # Just create and configure the tool without running the server
            if not tool_id:
                tool_id = self.create_vocabulary_tool()
                if not tool_id:
                    logger.error("Failed to create vocabulary tool. Exiting.")
                    return
            
            # Assign tool to assistant
            if not self.assign_tool_to_assistant(tool_id):
                logger.error("Failed to assign tool to assistant. Exiting.")
                return
            
            logger.info("Tool setup complete!") 