#!/usr/bin/env python3
"""
Local development server for N8N webhook integration
Handles CORS and proxies requests to the remote N8N webhook
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import json
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get N8N webhook URL from environment variable
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')
if not N8N_WEBHOOK_URL:
    raise ValueError("N8N_WEBHOOK_URL environment variable is required")

@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "message": "N8N Webhook Proxy Server",
        "timestamp": datetime.now().isoformat(),
        "n8n_webhook": N8N_WEBHOOK_URL
    })

@app.route('/webhook', methods=['GET', 'POST'])
def webhook_proxy():
    """
    Proxy endpoint for N8N webhook
    Accepts both GET and POST requests and forwards to N8N
    """
    try:
        # Log the incoming request
        logger.info(f"Received {request.method} request to /webhook")
        logger.info(f"Headers: {dict(request.headers)}")

        if request.method == 'POST':
            # Get JSON data from the request
            data = request.get_json()
            logger.info(f"POST Data: {data}")

            # Prepare parameters for GET request to N8N
            params = {}
            if data:
                if 'message' in data:
                    params['message'] = data['message']
                if 'user' in data:
                    params['user'] = data['user']
                if 'timestamp' in data:
                    params['timestamp'] = data['timestamp']

            # Forward as GET request to N8N webhook
            logger.info(f"Forwarding to N8N with params: {params}")
            response = requests.get(N8N_WEBHOOK_URL, params=params, timeout=30)

        else:  # GET request
            # Forward GET request with query parameters
            params = dict(request.args)
            logger.info(f"GET Params: {params}")
            logger.info(f"Forwarding to N8N with params: {params}")
            response = requests.get(N8N_WEBHOOK_URL, params=params, timeout=30)

        # Log the N8N response
        logger.info(f"N8N Response Status: {response.status_code}")
        logger.info(f"N8N Response Headers: {dict(response.headers)}")

        # Try to parse JSON response, fallback to text
        try:
            response_data = response.json()
            logger.info(f"N8N Response JSON: {response_data}")
        except json.JSONDecodeError:
            response_data = {
                "message": response.text or "Response received from N8N",
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            logger.info(f"N8N Response Text: {response.text}")

        # Return the response with CORS headers
        return jsonify(response_data), response.status_code

    except requests.exceptions.Timeout:
        error_msg = "Timeout: N8N webhook did not respond within 30 seconds"
        logger.error(error_msg)
        return jsonify({
            "error": error_msg,
            "status": "timeout",
            "timestamp": datetime.now().isoformat()
        }), 408

    except requests.exceptions.RequestException as e:
        error_msg = f"Error connecting to N8N webhook: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "error": error_msg,
            "status": "connection_error",
            "timestamp": datetime.now().isoformat()
        }), 502

    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg)
        return jsonify({
            "error": error_msg,
            "status": "server_error",
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/test')
def test_endpoint():
    """Test endpoint to verify server is working"""
    return jsonify({
        "message": "Test successful! Server is running.",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "GET / - Health check",
            "GET/POST /webhook - N8N webhook proxy",
            "GET /test - This test endpoint"
        ]
    })

@app.route('/webhook/test', methods=['GET', 'POST'])
def webhook_test():
    """Test the webhook with sample data"""
    test_message = request.args.get('message', 'Hello from test endpoint!')

    try:
        # Test the N8N webhook
        params = {
            'message': test_message,
            'user': 'test_user',
            'timestamp': datetime.now().isoformat()
        }

        logger.info(f"Testing N8N webhook with params: {params}")
        response = requests.get(N8N_WEBHOOK_URL, params=params, timeout=30)

        return jsonify({
            "test_status": "success",
            "n8n_status_code": response.status_code,
            "n8n_response": response.text,
            "test_params": params,
            "timestamp": datetime.now().isoformat()
        })

    except Exception as e:
        return jsonify({
            "test_status": "failed",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 Starting N8N Webhook Proxy Server...")
    print(f"📡 N8N Webhook URL: {N8N_WEBHOOK_URL}")
    print("🌐 Server will be available at: http://localhost:8000")
    print("🔧 Endpoints:")
    print("   GET / - Health check")
    print("   GET/POST /webhook - N8N webhook proxy")
    print("   GET /test - Test endpoint")
    print("   GET/POST /webhook/test - Test webhook integration")
    print("\n✨ Use Ctrl+C to stop the server\n")

    app.run(host='0.0.0.0', port=8000, debug=True)