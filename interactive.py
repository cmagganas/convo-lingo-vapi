import os
import sys
import time
import threading
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
from tool import mock_tool_call  # noqa: E402

# Assistant ID
ASSISTANT_ID = "4df2000e-479b-434e-8373-6ca1809233e2"

def interactive_session(target_language="German", origin_language="English"):
    """
    Interactive session with the Language Learning Assistant
    """
    print(f"Starting {origin_language} to {target_language} learning session...")
    
    # Initialize VAPI client
    client = None
    running = True
    
    try:
        # Initialize client
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
        
        print("Connected. Type 'exit' to quit.")
        
        # Start input thread
        input_thread = threading.Thread(
            target=handle_text_input,
            args=(client, lambda: running)
        )
        input_thread.daemon = True
        input_thread.start()
        
        # Keep main thread alive
        while running:
            time.sleep(1)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if client:
            client.stop()
            print("Session ended.")

def handle_text_input(client, is_running):
    """
    Handle text input from user
    """
    while is_running():
        text = input("\nType message or 'exit': ").strip()
        
        if text.lower() == 'exit':
            # Signal to stop
            return
            
        elif text:
            # Check for vocabulary keywords
            vocab_keywords = ["vocabulary", "word", "meaning", "translate"]
            if any(keyword in text.lower() for keyword in vocab_keywords):
                mock_tool_call(text)
                
            # Send message to assistant
            try:
                client.add_message("user", text)  # noqa: E1101
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    interactive_session() 