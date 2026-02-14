#!/usr/bin/env python3
"""
P2P Data Products V2 - Flask Server Launcher
=============================================
Serves app_v2 frontend with modular backend APIs.

Usage:
    python server.py

The server will start on http://localhost:5000
"""

import sys
import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from root .env
load_dotenv()

# Create Flask app serving app_v2 static files
app = Flask(__name__, 
            static_folder='app_v2/static',
            static_url_path='')

CORS(app)

# Initialize facades (Dependency Injection)
from modules.data_products_v2.facade.data_products_facade import DataProductsFacade

# Initialize SQLite facade (pass source_type, not repository object)
app.sqlite_facade_v2 = DataProductsFacade(source_type='sqlite')

# Register backend API blueprints
from modules.data_products_v2.backend import data_products_v2_api
from modules.knowledge_graph_v2.backend import blueprint as knowledge_graph_bp
from modules.ai_assistant.backend import blueprint as ai_assistant_bp
from core.api.frontend_registry import frontend_registry_bp

app.register_blueprint(data_products_v2_api, url_prefix='/api/data-products')
app.register_blueprint(knowledge_graph_bp, url_prefix='/api/knowledge-graph')
app.register_blueprint(ai_assistant_bp, url_prefix='/api/ai-assistant')
app.register_blueprint(frontend_registry_bp)  # No prefix - routes are already defined

# Serve app_v2 index.html at root
@app.route('/')
def serve_index():
    return send_from_directory('app_v2/static', 'index.html')

# Serve module frontend files
@app.route('/modules/<path:path>')
def serve_module_files(path):
    """Serve frontend files from modules directory with no-cache headers"""
    response = send_from_directory('modules', path)
    # Force browser to always reload JavaScript files (no caching)
    if path.endswith('.js'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# Serve app_v2 static files
@app.route('/<path:path>')
def serve_static(path):
    """Serve static files with no-cache headers for JavaScript"""
    response = send_from_directory('app_v2/static', path)
    # Force browser to always reload JavaScript files (no caching)
    if path.endswith('.js'):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    print("=" * 60)
    print("P2P Data Products V2 - Flask Application Server")
    print("=" * 60)
    print()
    print("Starting server...")
    print("Server will be available at: http://localhost:5000")
    print()
    print("Serving frontend from: app_v2/static/")
    print("Backend APIs:")
    print("  - /api/data-products")
    print("  - /api/knowledge-graph")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    print()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)