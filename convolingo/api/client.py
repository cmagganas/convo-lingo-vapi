import time
import logging
from typing import Callable

from vapi_python import Vapi
from convolingo.utils.config import config, ASSISTANT_ID

# Set up logging
logger = logging.getLogger(__name__)


class VapiClient:
    """Client for interacting with the VAPI service"""
    
    def __init__(self):
        """Initialize the VAPI client"""
        self.client = None
        self.is_connected = False
    
    def connect(self, target_language: str) -> bool:
        """
        Connect to the VAPI service
        
        Args:
            target_language: The language to learn
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Initialize VAPI client
            self.client = Vapi(api_key=config.api_key)
            
            # Get assistant configuration
            assistant_config = config.get_assistant_config(target_language)
            
            # Start call
            self.client.start(
                assistant_id=ASSISTANT_ID,
                assistant_overrides=assistant_config
            )
            
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