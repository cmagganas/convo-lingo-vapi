# Language Learning Assistant

A minimal Python application using VAPI's Language Learning Assistant.

## Setup

1. Install dependencies:
```
brew install portaudio
pip install -r requirements.txt
```

2. Create a `.env` file with your VAPI API key:
```
VAPI_API_KEY=your_api_key_here
```

## Usage

### Basic Session
```
python main.py
```

### Interactive Session with Text Input
```
python interactive.py
```

## Tool Integration

### Automated Setup with setup_tool.py

To automatically set up the vocabulary tool integration:

```
python setup_tool.py
```

This script will:
1. Validate your VAPI API key
2. Start the Flask webhook server
3. Start ngrok to expose your local server
4. Create the vocabulary tool in VAPI
5. Configure the server URL
6. Assign the tool to the Language Learning Assistant

The script will keep running to maintain the ngrok tunnel. Press Ctrl+C to stop.

### Manual Setup

To manually test the vocabulary tool integration:

1. Start the webhook server:
```
python ngrok_server.py
```

2. Expose your local server using ngrok:
```
ngrok http 5000
```

3. Copy the ngrok URL (e.g. `https://12345.ngrok.io/api/vocabulary`) and use it as your server URL in VAPI.

## Development Notes

- Assistant ID: 4df2000e-479b-434e-8373-6ca1809233e2
- Vocabulary Tool ID: b7bf97bf-c4cb-4d41-9db2-038460f17870

Both scripts default to English-to-German learning. To use a different language, modify the function call arguments. 