# Python code equivalent to the provided JavaScript code
# Running on port 3001

from flask import Flask, request, jsonify
import requests
import os
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time

app = Flask(__name__)

# Environment variables
OPENWEBUI_BASE_URL = os.environ.get('OPENWEBUI_BASE_URL')
OPENWEBUI_API_KEY = os.environ.get('OPENWEBUI_API_KEY')
API_KEY = os.environ.get('API_KEY')


# Configure retry strategy
retry_strategy = Retry(
    total=3,  # number of retries
    backoff_factor=1,  # wait 1, 2, 4 seconds between retries
    status_forcelist=[500, 502, 503, 504]  # retry on these status codes
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)

@app.route('/v1/chat/completions', methods=['POST'])
@app.route('/v1/models', methods=['GET', 'POST'])
def handle_request():
    
    # Check authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header or auth_header != f'Bearer {API_KEY}':
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        # Determine API URL based on endpoint
        path = request.path
        if path == '/v1/chat/completions':
            print("chat/completions, method: ", request.method)
            api_url = f"{OPENWEBUI_BASE_URL}/api/chat/completions"
            request_body = request.get_json()
            if not request_body:
                return jsonify({'error': 'Invalid JSON body'}), 400
            print(f"Request body: {request_body}")
            
            # Handle streaming response
            if request_body.get('stream', False):
                try:
                    custom_response = session.post(
                        api_url,
                        headers={
                            'Content-Type': 'application/json',
                            'Authorization': f'Bearer {OPENWEBUI_API_KEY}'
                        },
                        json=request_body,
                        stream=True,
                        timeout=(30, 300)  # (connect timeout, read timeout)
                    )
                    custom_response.raise_for_status()
                except requests.exceptions.Timeout:
                    return jsonify({'error': 'Request timed out'}), 504
                except requests.exceptions.RequestException as e:
                    return jsonify({'error': f'Request failed: {str(e)}'}), 500

                def generate():
                    try:
                        for line in custom_response.iter_lines():
                            if line:
                                line_str = line.decode('utf-8')
                                if line_str.startswith('data: '):
                                    line_str = line_str[6:]
                                yield f"data: {line_str}\n\n"
                    except Exception as e:
                        print(f"Streaming error: {e}")
                        yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
                
                return app.response_class(
                    generate(),
                    mimetype='text/event-stream',
                    headers={
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                    }
                )
                
        elif path == '/v1/models':
            print("models")
            api_url = f"{OPENWEBUI_BASE_URL}/api/models"
            if request.method == 'GET':
                try:
                    custom_response = session.get(
                        api_url,
                        headers={'Authorization': f'Bearer {OPENWEBUI_API_KEY}'},
                        timeout=(10, 30)
                    )
                    custom_response.raise_for_status()
                    return jsonify(custom_response.json())
                except requests.exceptions.Timeout:
                    return jsonify({'error': 'Request timed out'}), 504
                except requests.exceptions.RequestException as e:
                    return jsonify({'error': f'Request failed: {str(e)}'}), 500
        else:
            print("Not Found")
            return jsonify({'error': 'Not Found'}), 404
        
        # Forward the request to the appropriate API
        try:
            custom_response = session.post(
                api_url,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {OPENWEBUI_API_KEY}'
                },
                json=request_body,
                timeout=(30, 300)  # (connect timeout, read timeout)
            )
            custom_response.raise_for_status()
            return jsonify(custom_response.json())
        except requests.exceptions.Timeout:
            return jsonify({'error': 'Request timed out'}), 504
        except requests.exceptions.RequestException as e:
            return jsonify({'error': f'Request failed: {str(e)}'}), 500
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/<path:path>', methods=['PUT', 'DELETE'])
def catch_all(path):
    print(f"catch_all: {path}")
    print(f"catch_all: {path}, {request.method}")
    return jsonify({'error': 'Not Found'}), 404

if __name__ == '__main__':
    print("Starting server on port 3001")
    app.run(host='0.0.0.0', port=3001)