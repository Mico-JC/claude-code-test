"""
Vercel serverless function for N8N webhook integration
Handles CORS and proxies requests to the remote N8N webhook
"""

from http.server import BaseHTTPRequestHandler
import requests
import json
import os
from datetime import datetime
from urllib.parse import urlparse, parse_qs

# Get N8N webhook URL from environment variable
N8N_WEBHOOK_URL = os.getenv('N8N_WEBHOOK_URL', 'https://miran-jc.app.n8n.cloud/webhook/1106d72c-36b7-4ee6-8a81-f21be25dc3ea')

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        # Handle CORS preflight request
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.send_header('Access-Control-Max-Age', '3600')
        self.end_headers()

    def do_GET(self):
        self._handle_request()

    def do_POST(self):
        self._handle_request()

    def _handle_request(self):
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            if self.command == 'POST':
                # Get JSON data from POST request
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)

                try:
                    data = json.loads(post_data.decode('utf-8')) if post_data else {}
                except json.JSONDecodeError:
                    data = {}

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
                # Parse query parameters
                parsed_url = urlparse(self.path)
                params = {k: v[0] for k, v in parse_qs(parsed_url.query).items()}

                # Forward GET request to N8N webhook
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

            # Send response
            self.wfile.write(json.dumps(response_data).encode('utf-8'))

        except requests.exceptions.Timeout:
            self._send_error_response({
                "error": "Timeout: N8N webhook did not respond within 30 seconds",
                "status": "timeout",
                "timestamp": datetime.now().isoformat()
            }, 408)

        except requests.exceptions.RequestException as e:
            self._send_error_response({
                "error": f"Error connecting to N8N webhook: {str(e)}",
                "status": "connection_error",
                "timestamp": datetime.now().isoformat()
            }, 502)

        except Exception as e:
            self._send_error_response({
                "error": f"Unexpected error: {str(e)}",
                "status": "server_error",
                "timestamp": datetime.now().isoformat()
            }, 500)

    def _send_error_response(self, error_data, status_code):
        self.send_response(status_code)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(error_data).encode('utf-8'))