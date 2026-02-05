"""
Test Server for Feature Manager Module

Quick server to test Feature Manager API endpoints.

Run with: python test_feature_manager.py

Then test with:
- GET  http://localhost:5001/api/features
- POST http://localhost:5001/api/features/application-logging/toggle
- GET  http://localhost:5001/api/features/export
"""

from flask import Flask
from flask_cors import CORS
import sys
from pathlib import Path
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import Feature Manager API
from modules.feature_manager.backend.api import api as feature_manager_api

# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for testing

# Register Feature Manager blueprint
app.register_blueprint(feature_manager_api)


@app.route('/')
def home():
    """Home page with API documentation."""
    return """
    <html>
    <head>
        <title>Feature Manager Test Server</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #0070f2; }
            .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-left: 4px solid #0070f2; }
            .method { color: #0070f2; font-weight: bold; }
            code { background: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
            button { background: #0070f2; color: white; border: none; padding: 10px 20px; 
                     cursor: pointer; border-radius: 5px; margin: 5px; }
            button:hover { background: #0056b3; }
            #output { background: #f5f5f5; padding: 15px; margin: 20px 0; 
                      border: 1px solid #ddd; min-height: 100px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <h1>🎯 Feature Manager Test Server</h1>
        <p>Server running on <strong>http://localhost:5001</strong></p>
        
        <h2>Available Endpoints:</h2>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/features</code><br>
            Get all features<br>
            <button onclick="testEndpoint('GET', '/api/features')">Test</button>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/features/&lt;name&gt;</code><br>
            Get specific feature<br>
            <button onclick="testEndpoint('GET', '/api/features/feature-manager')">Test (feature-manager)</button>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <code>/api/features/&lt;name&gt;/enable</code><br>
            Enable a feature<br>
            <button onclick="testEndpoint('POST', '/api/features/application-logging/enable')">Test (enable logging)</button>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <code>/api/features/&lt;name&gt;/disable</code><br>
            Disable a feature<br>
            <button onclick="testEndpoint('POST', '/api/features/application-logging/disable')">Test (disable logging)</button>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <code>/api/features/&lt;name&gt;/toggle</code><br>
            Toggle a feature on/off<br>
            <button onclick="testEndpoint('POST', '/api/features/application-logging/toggle')">Test (toggle logging)</button>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/features/export</code><br>
            Export configuration<br>
            <button onclick="testEndpoint('GET', '/api/features/export')">Test</button>
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> <code>/api/features/reset</code><br>
            Reset to defaults<br>
            <button onclick="testEndpoint('POST', '/api/features/reset')">Test</button>
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <code>/api/features/categories</code><br>
            Get all categories<br>
            <button onclick="testEndpoint('GET', '/api/features/categories')">Test</button>
        </div>
        
        <h2>Test Output:</h2>
        <div id="output">Click a Test button above to see the API response...</div>
        
        <script>
            async function testEndpoint(method, url) {
                const output = document.getElementById('output');
                output.textContent = 'Loading...';
                
                try {
                    const response = await fetch(url, { method: method });
                    const data = await response.json();
                    
                    output.textContent = method + ' ' + url + '\\n\\n' + 
                                       'Status: ' + response.status + '\\n\\n' +
                                       JSON.stringify(data, null, 2);
                } catch (error) {
                    output.textContent = 'Error: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    """


if __name__ == '__main__':
    print("=" * 60)
    print("🎯 FEATURE MANAGER TEST SERVER")
    print("=" * 60)
    print("\n✅ Server starting...")
    print("\n📍 Open in browser: http://localhost:5001")
    print("\n🔧 API Endpoints:")
    print("   GET  http://localhost:5001/api/features")
    print("   POST http://localhost:5001/api/features/<name>/toggle")
    print("   GET  http://localhost:5001/api/features/export")
    print("\n⏹️  Press CTRL+C to stop\n")
    print("=" * 60 + "\n")
    
    # Run server
    app.run(debug=True, port=5001, host='0.0.0.0')