from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import os

app = Flask(__name__)
cors = CORS(app, resource={r"/*": {"origins": "*"}})

# Load configurations from environment variables
# CORS(app)

# Define your routes directly in this file or assume they are defined in the imported controllers
@app.route('/')
def home():
    return "Hi Hello"

# Main entry point to run the Flask application
if __name__ == '__main__':
    app.run(port=5099,debug=True)
