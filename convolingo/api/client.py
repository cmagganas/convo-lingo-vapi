import time
import logging
import requests
from typing import Callable, Optional

from vapi_python import Vapi
from convolingo.utils.config import (
    config, DEFAULT_TARGET_LANGUAGE, 
    DEFAULT_ORIGIN_LANGUAGE, DEFAULT_CHAPTER
)

# Set up logging
logger = logging.getLogger(__name__)

# Constants for vocabulary tool creation
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


class VapiClient:
    """Client for interacting with the VAPI service"""
    
    def __init__(self):
        """Initialize the VAPI client"""
        self.client = None
        self.is_connected = False
        self.vocabulary_tool_id = None
    
    def _create_vocabulary_tool(self) -> Optional[str]:
        """
        Create a new vocabulary tool in VAPI
        
        Returns:
            str: Tool ID if successful, None otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json"
            }
            
            # Create the tool - note the correct endpoint is /tool (singular)
            payload = {
                "type": "function",  # Specify the type as function
                "function": {
                    "name": TOOL_NAME,
                    "description": TOOL_DESCRIPTION,
                    "parameters": TOOL_PARAMETERS
                }
            }
            
            response = requests.post(
                f"{config.api_base}/tool",  # Fixed endpoint from /tools to /tool
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
                # Continue without the tool if creation fails
                return None
        except Exception as e:
            logger.error(f"Error creating vocabulary tool: {e}")
            # Continue without the tool if an exception occurs
            return None
    
    def connect(
        self, 
        target_language: str = DEFAULT_TARGET_LANGUAGE,
        native_language: str = DEFAULT_ORIGIN_LANGUAGE,
        chapter: str = DEFAULT_CHAPTER,
        user_id: Optional[str] = None,
    ) -> bool:
        """
        Connect to the VAPI service
        
        Args:
            target_language: The language to learn
            native_language: The user's native language
            chapter: The current chapter or module being studied
            user_id: Optional user ID for personalization
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Initialize VAPI client
            self.client = Vapi(api_key=config.api_key)
            
            # Log the configuration being sent
            logger.info(
                f"Connecting with: target={target_language}, "
                f"native={native_language}, chapter='{chapter[:30]}...'"
            )
            
            # Create the system prompt with the dynamic variables
            system_prompt = (
                "You are a language learning teaching assistant named Emma.\n"
                "You will begin a lesson plan starting in {native_language} "
                "and begin role playing speaking in {target_language}.\n\n"
                "native_language = \"{native_language}\"\n"
                "target_language = \"{target_language}\"\n\n"
                "{chapter}"
            ).format(
                native_language=native_language,
                target_language=target_language,
                chapter=chapter
            )
            
            # Create a custom assistant configuration
            assistant = {
                "model": {
                    "model": "gpt-3.5-turbo", 
                    "provider": "openai",
                    "temperature": 0.7,
                    "messages": [
                        {
                            "role": "system",
                            "content": system_prompt
                        }
                    ]
                },
                "voice": {
                    "model": "eleven_multilingual_v2",
                    "voiceId": "S9EGwlCtMF7VXtENq79v",
                    "provider": "11labs",
                    "stability": 0.5,
                    "similarityBoost": 0.75
                },
                "transcriber": {
                    "model": "nova-3",
                    "language": "en-US",
                    "provider": "deepgram"
                }
            }
            
            # Add user ID if provided
            if user_id:
                assistant["userId"] = user_id
            
            # Use the assistant directly
            self.client.start(assistant=assistant)
            logger.info(f"Created custom assistant with chapter: {chapter}")
            
            self.is_connected = True
            logger.info(
                f"Connected to VAPI assistant for {target_language} learning"
            )
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to VAPI: {e}")
            self.is_connected = False
            return False
    
    def disconnect(self) -> None:
        """Disconnect from the VAPI service"""
        if self.client and self.is_connected:
            try:
                self.client.stop()
                logger.info("Disconnected from VAPI assistant")
            except Exception as e:
                logger.error(f"Error disconnecting from VAPI: {e}")
            finally:
                self.is_connected = False
                self.client = None
    
    def send_message(self, text: str) -> bool:
        """
        Send a message to the assistant
        
        Args:
            text: The message text
            
        Returns:
            bool: True if message sent successfully, False otherwise
        """
        if not self.client or not self.is_connected:
            logger.error("Cannot send message: Not connected to VAPI")
            return False
            
        try:
            # VAPI SDK method to send text
            # The exact method name may vary based on the SDK version
            # Try different methods that might be available
            if hasattr(self.client, 'send_text'):
                self.client.send_text(text)
            elif hasattr(self.client, 'user_message'):
                self.client.user_message(text)
            else:
                # Fallback - this might be the most recent one
                self.client.message(text)
            return True
        except Exception as e:
            logger.error(f"Error sending message to VAPI: {e}")
            return False
    
    def maintain_connection(self, should_continue: Callable[[], bool]) -> None:
        """
        Keep the connection alive until should_continue returns False
        
        Args:
            should_continue: Function that returns False when connection 
                             should end
        """
        try:
            while should_continue() and self.is_connected:
                time.sleep(0.5)
        except Exception as e:
            logger.error(f"Error maintaining connection: {e}")
        finally:
            self.disconnect()