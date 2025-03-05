import time
import logging
from typing import Callable, Optional

from vapi_python import Vapi
from convolingo.utils.config import (
    config, ASSISTANT_ID, DEFAULT_TARGET_LANGUAGE, 
    DEFAULT_ORIGIN_LANGUAGE, DEFAULT_CHAPTER,
    VOCABULARY_TOOL_ID
)

# Set up logging
logger = logging.getLogger(__name__)


class VapiClient:
    """Client for interacting with the VAPI service"""
    
    def __init__(self):
        """Initialize the VAPI client"""
        self.client = None
        self.is_connected = False
    
    def connect(
        self, 
        target_language: str = DEFAULT_TARGET_LANGUAGE,
        native_language: str = DEFAULT_ORIGIN_LANGUAGE,
        chapter: str = DEFAULT_CHAPTER,
        user_id: Optional[str] = None,
        custom_system_prompt: Optional[str] = None
    ) -> bool:
        """
        Connect to the VAPI service
        
        Args:
            target_language: The language to learn
            native_language: The user's native language
            chapter: The current chapter or module being studied
            user_id: Optional user ID for personalization
            custom_system_prompt: Optional custom system prompt template
                (Used when creating a custom assistant with a dynamic chapter)
            
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
            
            # Check if we're using non-default chapter 
            using_custom_chapter = (chapter != DEFAULT_CHAPTER)
            
            if using_custom_chapter:
                # For custom chapters, we create a completely new assistant
                # with the chapter directly embedded in the system prompt
                # This approach is needed because the default assistant has
                # Chapter 3 hardcoded in its system prompt
                
                # Create the system prompt with the custom chapter
                system_prompt = (
                    "You are a language learning teaching assistant named Emma.\n"
                    "You will begin a lesson plan starting in {native_language} "
                    "and begin role playing speaking in {target_language}.\n\n"
                    "native_language = \"{native_language}\"\n"
                    "target_language = \"{target_language}\"\n\n"
                    f"{chapter}"
                ).format(
                    native_language=native_language,
                    target_language=target_language
                )
                
                # Create a new assistant configuration based on the existing one
                assistant = {
                    "model": {
                        "model": "gpt-3.5-turbo", 
                        "provider": "openai",
                        "temperature": 0.7,
                        "toolIds": [VOCABULARY_TOOL_ID],
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
                    # variableValues are not supported here
                    # Variables are already interpolated into the system prompt directly
                }
                
                # Use the assistant directly
                self.client.start(assistant=assistant)
                logger.info(f"Created custom assistant with chapter: {chapter}")
            else:
                # For the default chapter, use the existing assistant
                assistant_config = {
                    "variableValues": {
                        "native_language": native_language,
                        "target_language": target_language
                    }
                }
                
                # Add user ID if provided
                if user_id:
                    assistant_config["userId"] = user_id
                
                # Use the pre-configured assistant ID with overrides
                self.client.start(
                    assistant_id=ASSISTANT_ID,
                    assistant_overrides=assistant_config
                )
                logger.info(f"Using existing assistant ID: {ASSISTANT_ID}")
            
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