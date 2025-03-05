import threading
import logging
import sys
from typing import Callable, Dict, Any, Optional

from convolingo.api.client import VapiClient
from convolingo.tools.vocabulary import VocabularyTool
from convolingo.utils.config import (
    DEFAULT_TARGET_LANGUAGE, DEFAULT_ORIGIN_LANGUAGE, DEFAULT_CHAPTER
)

# Set up logging
logger = logging.getLogger(__name__)


class InteractiveSession:
    """Interactive language learning session with text input"""
    
    def __init__(self):
        """Initialize the interactive session"""
        self.client = VapiClient()
        self.vocabulary_tool = VocabularyTool()
        self.running = False
    
    def start(
        self, 
        target_language: str = DEFAULT_TARGET_LANGUAGE,
        origin_language: str = DEFAULT_ORIGIN_LANGUAGE,
        chapter: str = DEFAULT_CHAPTER,
        user_id: Optional[str] = None
    ) -> None:
        """
        Start an interactive session
        
        Args:
            target_language: The language to learn
            origin_language: The user's native language
            chapter: The current chapter or module being studied
            user_id: Optional user ID for personalization
        """
        self.running = True
        
        logger.info(f"Starting {origin_language} to {target_language} "
                  f"learning session...")
        
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
        
        if chapter != DEFAULT_CHAPTER:
            print(f"Note: If the assistant still discusses {DEFAULT_CHAPTER.split(':')[0]}, ")
            print("it might not be using the 'chapter' variable in its system prompt.")
        
        print("Type 'exit' to quit, 'help' for commands.")
        
        # Start input thread
        input_thread = threading.Thread(
            target=self._handle_input,
            daemon=True
        )
        input_thread.start()
        
        # Maintain connection in main thread
        try:
            self.client.maintain_connection(lambda: self.running)
        except KeyboardInterrupt:
            logger.info("Session interrupted by user")
        finally:
            self.running = False
            print("Session ended.")
    
    def _handle_input(self) -> None:
        """Handle user input in a separate thread"""
        while self.running:
            try:
                text = input("\nType message or 'exit': ").strip()
                
                if not text:
                    continue
                    
                if text.lower() == 'exit':
                    self.running = False
                    return
                
                if text.lower() == 'help':
                    self._show_help()
                    continue
                
                # Check for vocabulary commands
                if text.lower().startswith('vocab '):
                    self._handle_vocabulary_command(text[6:])
                    continue
                
                # Send message to assistant
                self.client.send_message(text)
                
            except EOFError:
                self.running = False
                return
            except Exception as e:
                logger.error(f"Error handling input: {e}")
    
    def _show_help(self) -> None:
        """Show help information"""
        print("\nAvailable commands:")
        print("  exit            - Exit the session")
        print("  help            - Show this help information")
        print("  vocab add       - Add a new vocabulary word")
        print("  vocab list      - List all vocabulary words")
        print("  vocab search    - Search for a vocabulary word")
    
    def _handle_vocabulary_command(self, command: str) -> None:
        """
        Handle vocabulary-related commands
        
        Args:
            command: The vocabulary command without the 'vocab ' prefix
        """
        parts = command.split()
        if not parts:
            print("Invalid vocabulary command. Type 'help' for usage.")
            return
            
        action = parts[0].lower()
        
        if action == 'add' and len(parts) >= 3:
            # Format: vocab add word translation [notes]
            word = parts[1]
            translation = parts[2]
            notes = " ".join(parts[3:]) if len(parts) > 3 else None
            
            result = self.vocabulary_tool.add_word(
                DEFAULT_TARGET_LANGUAGE, word, translation, notes
            )
            print(result["message"])
            
        elif action == 'list':
            result = self.vocabulary_tool.list_words(DEFAULT_TARGET_LANGUAGE)
            print(result["message"])
            
            if result["words"]:
                for word in result["words"]:
                    print(f"  {word['word']} - {word['translation']}")
            
        elif action == 'search' and len(parts) >= 2:
            query = " ".join(parts[1:])
            result = self.vocabulary_tool.search_word(
                DEFAULT_TARGET_LANGUAGE, query
            )
            print(result["message"])
            
            if result["results"]:
                for word in result["results"]:
                    print(f"  {word['word']} - {word['translation']}")
        
        else:
            print("Invalid vocabulary command. Type 'help' for usage.") 