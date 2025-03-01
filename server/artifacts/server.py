from flask import Flask, Response, request, jsonify
from waitress import serve
import util
import os
import json

app = Flask(__name__)

@app.route('/api/classify_image', methods=['POST'])
def classify_image():
    image_data = request.form['image_data']
    result = util.classify_image(image_data)
    response = jsonify(result)
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/', methods=['GET'])
def home():
    return "Image Classification API is running! Send POST requests to /api/classify_image"

# For local testing
if __name__ == "__main__":
    print("Starting Python Flask Server For Sports Celebrity Image Classification")
    util.load_saved_artifacts()
    app.run(port=5000)

# For Vercel
util.load_saved_artifacts()

# Add handler for Vercel
def handler(request, **kwargs):
    return app(request.environ, start_response)
