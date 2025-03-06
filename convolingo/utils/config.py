import os
from pathlib import Path
from dotenv import load_dotenv

# Constants
DEFAULT_TARGET_LANGUAGE = "German"
DEFAULT_ORIGIN_LANGUAGE = "English"
DEFAULT_CHAPTER = "Chapter 3 - Ordering a donner (cost, cash/card, getting change, what sides they have)"
# ASSISTANT_ID = "4df2000e-479b-434e-8373-6ca1809233e2"
# VOCABULARY_TOOL_ID = "b7bf97bf-c4cb-4d41-9db2-038460f17870"
WEBHOOK_PORT = 5000

# Default system prompt template
# Note: This template is for documentation purposes only.
# The assistant configuration shows that the system prompt is set in the 
# model.messages array rather than directly as systemPrompt.
DEFAULT_SYSTEM_PROMPT = """
You are a language learning teaching assistant named Emma.
You will begin a lesson plan starting in {native_language} and begin role playing speaking in {target_language}.

native_language = "{native_language}"
target_language = "{target_language}"

{chapter}
"""


class Config:
    """Configuration manager for the application"""
    
    def __init__(self):
        """Initialize configuration by loading environment variables"""
        # Determine the repository root directory
        self.root_dir = Path(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))))
        
        # Explicitly load .env from the repository root
        env_path = self.root_dir / ".env"
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
        else:
            print(f"Warning: .env file not found at {env_path}")
            load_dotenv()  # Fallback to default behavior
        
        # Get API key
        self.api_key = os.getenv('VAPI_API_KEY')
        if not self.api_key:
            raise ValueError("VAPI_API_KEY environment variable not set")
            
        # API settings
        self.api_base = os.getenv('VAPI_API_BASE', 'https://api.vapi.ai')
        
        # History directory
        self.history_dir = self.root_dir / "conversation_history"
        
        # Ensure history directory exists
        self.history_dir.mkdir(exist_ok=True)


# Create singleton instance
config = Config() 