# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Start the N8N Webhook Proxy Server
```bash
python server.py
```

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Test the Webhook Integration
```bash
# Test the server health
curl http://localhost:8000/

# Test the webhook endpoint
curl "http://localhost:8000/webhook/test?message=Hello from test"
```

## Architecture

### Matrix Terminal Interface
- **Frontend**: HTML/CSS/JavaScript Matrix-style terminal interface
- **Backend**: Python Flask server acting as webhook proxy
- **Integration**: N8N webhook for chatbot functionality

### Files Structure
- `index.html` - Main terminal interface
- `styles.css` - Matrix terminal styling
- `script.js` - Terminal functionality and N8N integration
- `server.py` - Python Flask proxy server for N8N webhook
- `requirements.txt` - Python dependencies
- `blue-matrix-terminal.html` - Alternative blue-themed terminal

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the proxy server:
   ```bash
   python server.py
   ```

3. Open `index.html` in your browser

4. The terminal will connect to the N8N webhook through the local proxy server at `http://localhost:8000/webhook`

### N8N Webhook Configuration
- **Remote Webhook**: `https://miran-jc.app.n8n.cloud/webhook-test/1106d72c-36b7-4ee6-8a81-f21be25dc3ea`
- **Local Proxy**: `http://localhost:8000/webhook`
- **Method**: POST (frontend) → GET (to N8N)