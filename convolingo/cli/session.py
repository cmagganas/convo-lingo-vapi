import logging
import sys
import time
from typing import Optional

from convolingo.api.client import VapiClient
from convolingo.utils.config import (
    DEFAULT_TARGET_LANGUAGE, DEFAULT_ORIGIN_LANGUAGE, DEFAULT_CHAPTER
)

# Set up logging
logger = logging.getLogger(__name__)


class Session:
    """Basic language learning session with VAPI"""
    
    def __init__(self):
        """Initialize the basic session"""
        self.client = VapiClient()
        self.running = False
    
    def start(
        self, 
        target_language: str = DEFAULT_TARGET_LANGUAGE,
        origin_language: str = DEFAULT_ORIGIN_LANGUAGE,
        chapter: str = DEFAULT_CHAPTER,
        user_id: Optional[str] = None,
        duration: Optional[int] = None
    ) -> None:
        """
        Start a basic session
        
        Args:
            target_language: The language to learn
            origin_language: The user's native language
            chapter: The current chapter or module being studied
            user_id: Optional user ID for personalization
            duration: Optional duration in seconds (None for indefinite)
        """
        self.running = True
        
        logger.info(f"Starting {origin_language} to {target_language} learning session...")
        
        # Connect to VAPI with all parameters
        if not self.client.connect(
            target_language=target_language,
            native_language=origin_language,
            chapter=chapter,
            user_id=user_id
        ):
            logger.error("Failed to connect to VAPI. Exiting.")
            return
        
        print(f"Connected. Learning {target_language} from {origin_language}.")
        print(f"Current chapter: {chapter}")
        
        print("Press Ctrl+C to exit.")
        
        # If duration is specified, run for that time
        if duration:
            print(f"Session will run for {duration} seconds.")
            try:
                time.sleep(duration)
            except KeyboardInterrupt:
                logger.info("Session interrupted by user")
            finally:
                self.running = False
                self.client.disconnect()
                print("Session ended.")
        else:
            # Otherwise, maintain connection until interrupted
            try:
                self.client.maintain_connection(lambda: self.running)
            except KeyboardInterrupt:
                logger.info("Session interrupted by user")
            finally:
                self.running = False
                print("Session ended.")