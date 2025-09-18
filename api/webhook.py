"""
Vercel serverless function for N8N webhook integration
Handles CORS and proxies requests to the remote N8N webhook
"""

from flask import Flask, request, jsonify
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

# Get N8N webhook URL from environment variable
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL')
if not N8N_WEBHOOK_URL:
    raise ValueError("N8N_WEBHOOK_URL environment variable is required")

def handler(request):
    """
    Vercel serverless function handler
    """
    # Handle CORS preflight request
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization',
            'Access-Control-Max-Age': '3600'
        }
        return ('', 200, headers)

    # Set CORS headers for all responses
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
        'Content-Type': 'application/json'
    }

    try:
        if request.method == 'POST':
            # Get JSON data from the request
            data = request.get_json() or {}

            # Prepare parameters for GET request to N8N
            params = {}
            if 'message' in data:
                params['message'] = data['message']
            if 'user' in data:
                params['user'] = data['user']
            if 'timestamp' in data:
                params['timestamp'] = data['timestamp']

            # Forward as GET request to N8N webhook
            response = requests.get(N8N_WEBHOOK_URL, params=params, timeout=30)

        else:  # GET request
            # Forward GET request with query parameters
            params = dict(request.args)
            response = requests.get(N8N_WEBHOOK_URL, params=params, timeout=30)

        # Try to parse JSON response, fallback to text
        try:
            response_data = response.json()
        except json.JSONDecodeError:
            response_data = {
                "message": response.text or "Response received from N8N",
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }

        return (json.dumps(response_data), response.status_code, headers)

    except requests.exceptions.Timeout:
        error_response = {
            "error": "Timeout: N8N webhook did not respond within 30 seconds",
            "status": "timeout",
            "timestamp": datetime.now().isoformat()
        }
        return (json.dumps(error_response), 408, headers)

    except requests.exceptions.RequestException as e:
        error_response = {
            "error": f"Error connecting to N8N webhook: {str(e)}",
            "status": "connection_error",
            "timestamp": datetime.now().isoformat()
        }
        return (json.dumps(error_response), 502, headers)

    except Exception as e:
        error_response = {
            "error": f"Unexpected error: {str(e)}",
            "status": "server_error",
            "timestamp": datetime.now().isoformat()
        }
        return (json.dumps(error_response), 500, headers)

# Export the handler for Vercel
def main(request):
    return handler(request)