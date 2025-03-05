from flask import Flask, request, jsonify
import json
from tool import mock_tool_call

app = Flask(__name__)

@app.route('/callbacks', methods=['POST'])
def handle_callback():
    """
    Handle webhook callbacks from VAPI
    
    This endpoint would receive event data when the vocabulary tool is called
    """
    try:
        # Get the JSON data from the request
        data = request.json
        
        # Log the received data
        print("\n--- Webhook Callback Received ---")
        print(f"Event Type: {data.get('type', 'unknown')}")
        
        # If this is a tool call event, process it
        if data.get('type') == 'tool-call':
            tool_id = data.get('toolId')
            tool_input = data.get('input', {})
            
            print(f"Tool ID: {tool_id}")
            print(f"Tool Input: {json.dumps(tool_input, indent=2)}")
            
            # Process the tool call (mock implementation)
            result = mock_tool_call(str(tool_input))
            
            # Return a response that VAPI would use
            return jsonify({
                "success": True,
                "result": result
            })
        
        # For any other event type, just acknowledge receipt
        return jsonify({"success": True})
        
    except Exception as e:
        print(f"Error processing webhook: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/vocabulary', methods=['POST'])
def handle_vocabulary():
    """
    Handle vocabulary tool calls from VAPI
    
    This endpoint receives tool calls specifically for the vocabulary tool
    """
    try:
        # Get the JSON data from the request
        data = request.json
        
        # Log the received data
        print("\n--- Vocabulary Tool Call Received ---")
        print(f"Request Data: {json.dumps(data, indent=2)}")
        
        # Extract text to process if available
        text_to_process = ""
        if isinstance(data, dict):
            text_to_process = data.get('text', '')
        
        # Process the tool call (mock implementation)
        result = mock_tool_call(text_to_process)
        
        # Return a response that VAPI would use
        return jsonify({
            "success": True,
            "result": result
        })
        
    except Exception as e:
        print(f"Error processing vocabulary tool call: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Simple home page to verify the server is running
    """
    if request.method == 'POST':
        try:
            data = request.json
            print("\n--- POST Request to Root Endpoint ---")
            print(f"Request Data: {json.dumps(data, indent=2)}")
            return jsonify({"success": True})
        except Exception as e:
            print(f"Error processing root POST: {e}")
            return jsonify({"success": False, "error": str(e)}), 500
    
    return """
    <html>
        <body>
            <h1>VAPI Webhook Server</h1>
            <p>This server is ready to receive callbacks from VAPI.</p>
            <p>Use ngrok to expose this server to the internet.</p>
        </body>
    </html>
    """

if __name__ == '__main__':
    print("Starting webhook server on port 5000...")
    print("To expose this server, run: ngrok http 5000")
    print("Then use the ngrok URL + '/api/vocabulary' as your server URL in VAPI.")
    app.run(debug=True, port=5000) 