"""
P2P Data Products Flask Backend
================================
Flask-based REST API for P2P Data Products application.
Provides endpoints for HANA Cloud data products, SQL execution, and connection management.

This version uses modular architecture with dependency injection for:
- Data sources (HANA, SQLite) via DataSource interface
- Logging via ApplicationLogger interface
- Feature management via FeatureFlags service

Author: P2P Development Team
Version: 2.0.0 - Modular Architecture
Date: 2026-01-25
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import sys
import logging
import time
from datetime import datetime

# Add project root to path FIRST
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'modules'))

# Import modular components
from core.services.module_registry import ModuleRegistry
from core.services.module_loader import ModuleLoader
from modules.logger.backend.service import LoggingService

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment from .env file")
except ImportError:
    print("WARNING: python-dotenv not installed. Using system environment variables.")

# Configuration from environment
HANA_HOST = os.getenv('HANA_HOST', '')
HANA_PORT = int(os.getenv('HANA_PORT', '443'))
HANA_USER = os.getenv('HANA_USER', '')
HANA_PASSWORD = os.getenv('HANA_PASSWORD', '')
HANA_SCHEMA = os.getenv('HANA_SCHEMA', 'P2P_SCHEMA')
LOG_DB_PATH = os.getenv('LOG_DB_PATH', 'logs/app_logs.db')

# Industry-standard level-based log retention policy
LOG_RETENTION_POLICY = {
    'ERROR': int(os.getenv('LOG_RETENTION_ERROR', '30')),
    'WARNING': int(os.getenv('LOG_RETENTION_WARNING', '14')),
    'INFO': int(os.getenv('LOG_RETENTION_INFO', '7'))
}

ENV = os.getenv('ENV', 'development')

# Initialize module registry
registry = ModuleRegistry(os.path.join(project_root, 'modules'))
logger_module = logging.getLogger(__name__)
logger_module.info(f"[ModuleRegistry] Discovered {registry.get_module_count()} modules: {', '.join(registry.list_module_names())}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize logging service with retention policy
logging_service = LoggingService(db_path=LOG_DB_PATH, retention_policy=LOG_RETENTION_POLICY)

# Attach SQLite handler to root logger (all module loggers inherit it)
root_logger = logging.getLogger()
sqlite_handler = logging_service.get_handler()
sqlite_handler.setFormatter(logging.Formatter('%(message)s'))
root_logger.addHandler(sqlite_handler)

# Get logger for app.py
logger = logging.getLogger(__name__)
logger.info(f"SQLite logging initialized: {LOG_DB_PATH}")
logger.info(f"Log retention policy: ERROR={LOG_RETENTION_POLICY['ERROR']}d, WARNING={LOG_RETENTION_POLICY['WARNING']}d, INFO={LOG_RETENTION_POLICY['INFO']}d")

# Initialize Flask app
static_path = os.path.join(backend_dir, 'static')
app = Flask(__name__, static_folder=static_path, static_url_path='')
CORS(app)

# Configure session secret key
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Store config in app.config for blueprint access
app.config.update({
    'ENV': ENV,
    'HANA_HOST': HANA_HOST,
    'HANA_PORT': HANA_PORT,
    'HANA_USER': HANA_USER,
    'HANA_SCHEMA': HANA_SCHEMA
})

# Attach logging service to app for blueprint access
app.logging_service = logging_service

# Initialize module loader
module_loader = ModuleLoader(app)

# Load v2 modules only
print(f"\n{'='*60}")
print("Loading v2 Modules...")
print(f"{'='*60}\n")

# Load data_products_v2 module
module_loader.load_blueprint(
    "Data Products v2",
    "modules.data_products_v2.backend",
    "data_products_v2_api",
    "/api/data-products",
    is_critical=False
)

# Load knowledge_graph_v2 module  
module_loader.load_blueprint(
    "Knowledge Graph v2",
    "modules.knowledge_graph_v2.backend",
    "knowledge_graph_v2_api",
    "/api/knowledge-graph",
    is_critical=False
)

# Load logger module
module_loader.load_blueprint(
    "Application Logger",
    "modules.logger.backend",
    "logger_api",
    "/api",
    is_critical=False
)

# Log startup summary
module_loader.log_startup_summary()

# Request/Response logging middleware
@app.before_request
def log_request():
    """Log all incoming requests and track start time"""
    request.start_time = time.time()
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")

@app.after_request
def log_response(response):
    """Log all responses with duration"""
    if hasattr(request, 'start_time'):
        duration_ms = (time.time() - request.start_time) * 1000
        logger.info(f"{request.method} {request.path} - Status: {response.status_code} - Duration: {duration_ms:.2f}ms")
    return response

# Serve frontend
@app.route('/')
def serve_index():
    """Serve the v2 frontend index.html"""
    return send_from_directory(app.static_folder, 'index.html')

# Health check endpoint
@app.route('/api/health')
def health():
    """Health check endpoint with module information"""
    module_count = registry.get_module_count()
    module_names = registry.list_module_names()

    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'architecture': 'v2 (modular)',
        'modules': {
            'count': module_count,
            'names': module_names
        }
    })

# API info endpoint
@app.route('/api/info')
def api_info():
    """API information endpoint"""
    return jsonify({
        'app': 'P2P Data Products',
        'version': '2.0',
        'architecture': 'v2 (modular)',
        'modules': registry.list_module_names()
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({
        'success': False,
        'error': {'message': 'Endpoint not found', 'code': 'NOT_FOUND'}
    }), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Internal Server Error: {str(error)}")
    error_message = str(error) if ENV == 'development' else 'Internal server error'
    return jsonify({
        'success': False,
        'error': {'message': error_message, 'code': 'INTERNAL_ERROR'}
    }), 500

# Main entry point
if __name__ == '__main__':
    logger.info(f"Environment: {ENV}")
    logger.info(f"Static folder: {app.static_folder}")
    logger.info(f"Modules: {len(registry.get_all_modules())}")
    logger.info("Starting Flask server on http://localhost:5000")

    app.run(host='0.0.0.0', port=5000, debug=(ENV == 'development'))