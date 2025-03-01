from flask import Flask, request, jsonify
from http.server import BaseHTTPRequestHandler
import json
import base64
import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import after path is set
import util

app = Flask(__name__)

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get content length
        content_length = int(self.headers['Content-Length'])
        # Get the data
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        # Process the image
        try:
            image_data = data.get('image_data', '')
            if not image_data:
                response = {'error': 'No image data provided'}
                self.send_error(400, 'No image data provided')
                return
                
            results = util.classify_image(image_data)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(results).encode())
        except Exception as e:
            # Log the error
            print(f"Error: {str(e)}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({
            "status": "running",
            "message": "Image Classification API is running! Send POST requests with image_data."
        }).encode())

# Initialize model at module level for cold starts
print("Initializing model...")
try:
    util.load_saved_artifacts()
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {str(e)}")

# Handler for Vercel
def handler(request):
    if request.method == 'POST':
        try:
            # Get the JSON body
            body = json.loads(request.body)
            image_data = body.get('image_data', '')
            
            if not image_data:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "No image data provided"})
                }
                
            results = util.classify_image(image_data)
            
            return {
                "statusCode": 200,
                "body": json.dumps(results),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                }
            }
        except Exception as e:
            print(f"Error: {str(e)}")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)}),
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                }
            }
    else:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "running",
                "message": "Image Classification API is running! Send POST requests with image_data."
            }),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }
