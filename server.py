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

# ============================================================================
# DEPENDENCY INJECTION CONTAINER for data_products_v2
# ============================================================================
# This section acts as the DI container/composition root.
# It creates repositories, injects them into facades, and injects facades into API.

def configure_data_products_v2(app):
    """
    Configure data_products_v2 module with proper Dependency Injection
    
    Architecture:
        Repository (leaf) → Facade (middle) → API (top)
    
    Benefits:
    - No Service Locator anti-pattern
    - Easy to test (inject mocks)
    - Clear dependencies
    """
    from modules.data_products_v2.repositories.sqlite_data_product_repository import SQLiteDataProductRepository
    from modules.data_products_v2.repositories.hana_data_product_repository import HANADataProductRepository
    from modules.data_products_v2.facade.data_products_facade import DataProductsFacade
    from modules.data_products_v2.backend.api import DataProductsV2API, create_blueprint
    
    # 1. Create repositories (leaf dependencies)
    sqlite_repo = SQLiteDataProductRepository(db_path=None)  # Uses default path
    
    hana_repo = None
    hana_host = os.getenv('HANA_HOST')
    hana_port = int(os.getenv('HANA_PORT', 443))
    hana_user = os.getenv('HANA_USER')
    hana_password = os.getenv('HANA_PASSWORD')
    hana_database = os.getenv('HANA_DATABASE', 'P2P')
    hana_schema = os.getenv('HANA_SCHEMA', 'P2P_SCHEMA')
    
    if all([hana_host, hana_user, hana_password]):
        try:
            hana_repo = HANADataProductRepository(
                host=hana_host,
                port=hana_port,
                user=hana_user,
                password=hana_password,
                database=hana_database,
                schema=hana_schema
            )
            print(f"✅ HANA repository initialized: {hana_host}:{hana_port}")
        except Exception as e:
            print(f"⚠️  Failed to initialize HANA repository: {e}")
    else:
        print("⚠️  HANA credentials not found in .env - HANA data source disabled")
    
    # 2. Create facades (middle layer) with injected repositories
    sqlite_facade = DataProductsFacade(repository=sqlite_repo)
    hana_facade = DataProductsFacade(repository=hana_repo) if hana_repo else None
    
    # 3. Create API instance (top layer) with injected facades
    api_instance = DataProductsV2API(
        sqlite_facade=sqlite_facade,
        hana_facade=hana_facade
    )
    
    # 4. Create and register blueprint
    blueprint = create_blueprint(api_instance)
    app.register_blueprint(blueprint, url_prefix='/api/data-products')
    
    print("✅ data_products_v2 module configured with Dependency Injection")
    return api_instance

# Configure data_products_v2 with DI
configure_data_products_v2(app)

# Register other backend API blueprints
from modules.knowledge_graph_v2.backend import blueprint as knowledge_graph_bp
from modules.ai_assistant.backend import blueprint as ai_assistant_bp
from core.api.frontend_registry import frontend_registry_bp

app.register_blueprint(knowledge_graph_bp)  # No prefix - blueprint defines url_prefix='/api/knowledge-graph-v2'
app.register_blueprint(ai_assistant_bp)  # No prefix - blueprint defines url_prefix='/api/ai-assistant'
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