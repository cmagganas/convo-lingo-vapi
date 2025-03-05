# Setting Up Server URL for VAPI Tool Integration

This guide explains how to configure a server URL for receiving tool calls from VAPI.

## Prerequisites

- ngrok installed
- Flask server running (ngrok_server.py)
- VAPI API key

## Steps

### 1. Start the Flask Server

Run the webhook server locally:

```
python ngrok_server.py
```

This starts a Flask server on port 5000 that can receive callbacks from VAPI.

### 2. Start ngrok

In a new terminal, run:

```
ngrok http 5000
```

This creates a secure tunnel to your local server. You'll see a forwarding URL like:
```
Forwarding https://12345.ngrok.io -> http://localhost:5000
```

Copy this HTTPS URL.

### 3. Set Server URL in VAPI

There are two ways to set the server URL:

#### Option 1: Use the VAPI Dashboard

1. Go to the VAPI dashboard
2. Navigate to Settings > Server URL
3. Enter your ngrok URL + "/api/vocabulary" (e.g., `https://12345.ngrok.io/api/vocabulary`)
4. Save the settings

#### Option 2: Use the VAPI API

Make a POST request to update the server URL:

```bash
curl -X POST \
  https://api.vapi.ai/server-url \
  -H "Authorization: Bearer $VAPI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://12345.ngrok.io/api/vocabulary"
  }'
```

Replace `12345.ngrok.io` with your actual ngrok URL.

### 4. Testing the Integration

Once the server URL is set up, you can test the integration by:

1. Making a call using the Language Learning Assistant
2. Using vocabulary-related keywords in your conversation
3. Checking the Flask server logs for webhook events

## Important Notes

- The server now supports three endpoints:
  - `/api/vocabulary` - Primary endpoint for vocabulary tool calls
  - `/callbacks` - General webhook callback endpoint
  - `/` - Root endpoint (can handle both GET and POST requests)

- The ngrok URL changes every time you restart ngrok, unless you have a paid account
- Server URL calls have a timeout limit, so your webhook should respond quickly
- The call can continue even if the tool call fails, but vocabulary won't be saved 