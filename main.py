import os
import sys
import time
from dotenv import load_dotenv

# Add the client-sdk-python directory to the path
sys.path.append(os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'client-sdk-python')
)

# Load environment variables
load_dotenv()

# Get the API key
api_key = os.getenv('VAPI_API_KEY')

# Import VAPI
from vapi_python import Vapi  # noqa: E402

# Language Learning Assistant ID
ASSISTANT_ID = "4df2000e-479b-434e-8373-6ca1809233e2"

def start_session(target_language="German", origin_language="English"):
    """
    Start a session with the Language Learning Assistant
    """
    print(f"Starting {origin_language} to {target_language} learning session...")
    
    try:
        # Initialize VAPI client
        client = Vapi(api_key=api_key)
        
        # Set up assistant configuration
        assistant_config = {
            "variableValues": {
                "language": target_language
            }
        }
        
        # Start call
        client.start(
            assistant_id=ASSISTANT_ID,
            assistant_overrides=assistant_config
        )
        
        print("Connected. Press Ctrl+C to exit.")
        
        # Keep session alive until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Ending session...")
        finally:
            client.stop()
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    start_session()