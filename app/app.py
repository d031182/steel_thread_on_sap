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
import traceback
import requests
from functools import lru_cache

# Add project root to path FIRST
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'modules'))

# Import modular components
from core.services.module_registry import ModuleRegistry
from core.services.module_loader import ModuleLoader
from core.interfaces.data_source import DataSource
from core.interfaces.logger import ApplicationLogger
from modules.hana_connection.backend import HANADataSource
from modules.sqlite_connection.backend import SQLiteDataSource
from modules.log_manager.backend import SQLiteLogHandler, LoggingService
from modules.log_manager.backend.logging_modes import logging_mode_manager, LoggingMode

# Import CSN utilities
from csn_urls import get_csn_url, schema_name_to_ord_id, get_all_p2p_products

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
# ERROR: 30 days (critical for debugging, low volume)
# WARNING: 14 days (important patterns, medium volume)
# INFO: 7 days (recent context, high volume)
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

# Configure logging with SQLite handler
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize logging service with level-based retention policy
logging_service = LoggingService(db_path=LOG_DB_PATH, retention_policy=LOG_RETENTION_POLICY)
sqlite_handler = logging_service.get_handler()
sqlite_handler.setFormatter(logging.Formatter('%(message)s'))

# CRITICAL: Add SQLite handler to ROOT logger so ALL module loggers inherit it
root_logger = logging.getLogger()
root_logger.addHandler(sqlite_handler)

# Get logger for app.py
logger = logging.getLogger(__name__)
logger.info(f"SQLite logging initialized: {LOG_DB_PATH}")
logger.info(f"Log retention policy: ERROR={LOG_RETENTION_POLICY['ERROR']}d, WARNING={LOG_RETENTION_POLICY['WARNING']}d, INFO={LOG_RETENTION_POLICY['INFO']}d")

# Log initial logging mode
logger.info(f"Logging mode: {logging_mode_manager.mode.value}")

# Initialize Flask app  
static_path = os.path.join(backend_dir, 'static')
app = Flask(__name__, static_folder=static_path, static_url_path='')
CORS(app)

# Configure session secret key for login_manager
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Store config in app.config for blueprint access
app.config.update({
    'ENV': ENV,
    'HANA_HOST': HANA_HOST,
    'HANA_PORT': HANA_PORT,
    'HANA_USER': HANA_USER,
    'HANA_SCHEMA': HANA_SCHEMA
})

# Initialize data sources (dependency injection)
hana_data_source: DataSource = None
# Use the correct database path for SQLite data products
sqlite_db_path = os.path.join(backend_dir, 'database', 'p2p_data_products.db')
sqlite_data_source: DataSource = SQLiteDataSource(db_path=sqlite_db_path)

if HANA_HOST and HANA_USER and HANA_PASSWORD:
    hana_data_source = HANADataSource(HANA_HOST, HANA_PORT, HANA_USER, HANA_PASSWORD)
    logger.info("HANA data source initialized")
else:
    logger.warning("WARNING: HANA not configured - only SQLite source available")

# Attach data sources to app for blueprint access
app.hana_data_source = hana_data_source
app.sqlite_data_source = sqlite_data_source

# Register Module Blueprints using centralized loader
# Benefits: Consistent error handling, detailed logging, startup diagnostics
module_loader = ModuleLoader(app)

# Load modules with try-catch-log pattern
# Critical=False: Application continues if module fails (graceful degradation)
# Critical=True: Application stops if module fails (essential infrastructure)

module_loader.load_blueprint(
    "Feature Manager",
    "modules.feature_manager.backend",
    "feature_manager_api",
    "/api/features",
    is_critical=False
)

module_loader.load_blueprint(
    "Data Products",
    "modules.data_products.backend",
    "data_products_api",
    "/api/data-products",
    is_critical=False  # Core feature but app can run without it
)

module_loader.load_blueprint(
    "SQL Execution",
    "modules.sql_execution.backend",
    "sql_execution_api",
    "/api/sql",
    is_critical=False
)

module_loader.load_blueprint(
    "CSN Validation",
    "modules.csn_validation.backend",
    "csn_validation_api",
    "/api/csn",
    is_critical=False
)

module_loader.load_blueprint(
    "API Playground",
    "modules.api_playground.backend",
    "api_playground_api",
    "/api/playground",
    is_critical=False
)

module_loader.load_blueprint(
    "Knowledge Graph",
    "modules.knowledge_graph.backend",
    "knowledge_graph_api",
    "/api/knowledge-graph",
    is_critical=False
)

module_loader.load_blueprint(
    "Login Manager",
    "modules.login_manager.backend",
    "login_manager_api",
    "/api/login-manager",
    is_critical=True  # Essential for user authentication
)

module_loader.load_blueprint(
    "AI Assistant",
    "modules.ai_assistant.backend",
    "bp",
    "/api/ai-assistant",
    is_critical=False
)

# Log startup summary with all module loading results
module_loader.log_startup_summary()

# Register logging API extensions (dual-mode support)
from logging_api_extensions import register_logging_extensions
register_logging_extensions(app, logging_mode_manager, LoggingMode)


# Helper function to get appropriate data source
def get_data_source(source_name: str) -> DataSource:
    """
    Get data source by name
    
    Args:
        source_name: 'hana' or 'sqlite'
    
    Returns:
        DataSource instance
    
    Raises:
        ValueError: If source is invalid or not configured
    """
    if source_name == 'sqlite':
        return sqlite_data_source
    elif source_name == 'hana':
        if not hana_data_source:
            raise ValueError("HANA data source not configured")
        return hana_data_source
    else:
        raise ValueError(f"Invalid data source: {source_name}")


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
        
        # Create log record with duration
        log_record = logger.makeRecord(
            logger.name,
            logging.INFO,
            __file__,
            0,
            f"{request.method} {request.path} - Status: {response.status_code} - Duration: {duration_ms:.2f}ms",
            (),
            None
        )
        log_record.duration_ms = duration_ms
        logger.handle(log_record)
    else:
        logger.info(f"{request.method} {request.path} - Status: {response.status_code}")
    
    return response


# Static file routes
@app.route('/')
def index():
    """Serve SAP UI5 version (default)"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/app')
def data_products_app():
    """Serve Data Products application"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/alpine')
def alpine_app():
    """Serve Alpine.js + Tailwind version of the application"""
    return send_from_directory(app.static_folder, 'alpine-app.html')


@app.route('/alpine-fiori')
def alpine_fiori_app():
    """Serve Alpine.js + Fiori Design version of the application"""
    return send_from_directory(app.static_folder, 'alpine-fiori.html')


@app.route('/vanilla')
def vanilla_app():
    """Serve Vanilla JS + Fiori Design version of the application"""
    return send_from_directory(app.static_folder, 'vanilla-fiori.html')


@app.route('/choose')
def ux_selector():
    """Serve UX selector page"""
    return send_from_directory(app.static_folder, 'ux-selector.html')


@app.route('/api-playground')
def api_playground():
    """Serve simple API Playground (Swagger-like)"""
    return send_from_directory(app.static_folder, 'api-playground.html')


@app.route('/feature_manager')
def feature_manager_ui():
    """Serve Feature Manager Configurator UI"""
    template_path = os.path.join(project_root, 'modules', 'feature_manager', 'templates')
    return send_from_directory(template_path, 'configurator_simple.html')


@app.route('/feature_manager/test')
def feature_manager_test():
    """Serve Feature Manager Test UI"""
    template_path = os.path.join(project_root, 'modules', 'feature_manager', 'templates')
    return send_from_directory(template_path, 'configurator_test.html')


@app.route('/feature_manager/enhanced')
def feature_manager_enhanced():
    """Serve Feature Manager Enhanced UI"""
    template_path = os.path.join(project_root, 'modules', 'feature_manager', 'templates')
    return send_from_directory(template_path, 'configurator_enhanced.html')


@app.route('/feature_manager/production')
def feature_manager_production():
    """Serve Feature Manager Production UI"""
    template_path = os.path.join(project_root, 'modules', 'feature_manager', 'templates')
    return send_from_directory(template_path, 'configurator_production.html')


@app.route('/modules/<path:filepath>')
def serve_module_files(filepath):
    """Serve module frontend files"""
    modules_path = os.path.join(project_root, 'modules')
    return send_from_directory(modules_path, filepath)


# API Routes - Modules
@app.route('/api/modules', methods=['GET'])
def list_modules():
    """
    List all discovered modules with metadata
    
    Returns:
        JSON with module list, categorized and with full metadata
    """
    try:
        all_modules = registry.get_all_modules()
        module_list = []
        
        for name, config in all_modules.items():
            module_info = {
                'name': name,
                'displayName': config.get('displayName', name),
                'version': config.get('version', 'unknown'),
                'category': config.get('category', 'Uncategorized'),
                'enabled': config.get('enabled', True),
                'description': config.get('description', ''),
                'requiresHana': config.get('requiresHana', False),
                'path': str(registry.get_module_path(name))
            }
            module_list.append(module_info)
        
        # Group by category
        by_category = {}
        for module in module_list:
            category = module['category']
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(module)
        
        return jsonify({
            'success': True,
            'count': len(module_list),
            'modules': module_list,
            'byCategory': by_category,
            'categories': list(by_category.keys())
        })
        
    except Exception as e:
        logger.error(f"Error in list_modules: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'code': 'SERVER_ERROR'}
        }), 500


# API Routes - Health Check
@app.route('/api/health')
def health():
    """Health check endpoint with module information"""
    hana_status = 'not_configured'
    
    if hana_data_source:
        try:
            # Test connection by querying data products
            products = hana_data_source.get_data_products()
            hana_status = 'healthy' if products is not None else 'connection_failed'
        except Exception as e:
            hana_status = 'error'
            logger.error(f"Health check error: {str(e)}")
    
    # Get module summary
    module_count = registry.get_module_count()
    module_names = registry.list_module_names()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'architecture': 'modular',
        'hana': hana_status,
        'modules': {
            'count': module_count,
            'names': module_names
        }
    })


# NOTE: Modular API Routes
# - Data Products: modules/data_products/backend/api.py → /api/data-products/*
# - SQL Execution: modules/sql_execution/backend/api.py → /api/sql/*
# - CSN Validation: modules/csn_validation/backend/api.py → /api/csn/*

# NOTE: Knowledge Graph API moved to modules/knowledge_graph/backend/api.py → /api/knowledge-graph/*

# API Routes - Logging
@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get application logs"""
    try:
        level = request.args.get('level', None)
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        if level and level not in ['INFO', 'WARNING', 'ERROR']:
            return jsonify({
                'success': False,
                'error': {'message': 'Invalid log level', 'code': 'INVALID_LEVEL'}
            }), 400
        
        logs = logging_service.get_logs(level, limit, offset, start_date, end_date)
        total_count = logging_service.get_log_count(level)
        
        return jsonify({
            'success': True,
            'count': len(logs),
            'totalCount': total_count,
            'logs': logs,
            'filters': {
                'level': level,
                'limit': limit,
                'offset': offset,
                'start_date': start_date,
                'end_date': end_date
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'code': 'SERVER_ERROR'}
        }), 500


@app.route('/api/logs/stats', methods=['GET'])
def get_log_stats():
    """Get log statistics"""
    try:
        total = logging_service.get_log_count()
        info_count = logging_service.get_log_count(level='INFO')
        warning_count = logging_service.get_log_count(level='WARNING')
        error_count = logging_service.get_log_count(level='ERROR')
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total,
                'info': info_count,
                'warning': warning_count,
                'error': error_count
            }
        })
    except Exception as e:
        logger.error(f"Error getting log stats: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'code': 'SERVER_ERROR'}
        }), 500


@app.route('/api/logs/clear', methods=['POST'])
def clear_logs():
    """Clear all logs"""
    try:
        logging_service.clear_logs()
        logger.info("Logs cleared by user request")
        return jsonify({
            'success': True,
            'message': 'Logs cleared successfully'
        })
    except Exception as e:
        logger.error(f"Error clearing logs: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'code': 'SERVER_ERROR'}
        }), 500


@app.route('/api/logs/client', methods=['POST'])
def log_client_error():
    """Log client-side errors"""
    try:
        data = request.get_json()
        
        level = data.get('level', 'ERROR').upper()
        message = data.get('message', 'No message')
        url = data.get('url', 'unknown')
        line = data.get('line', 0)
        column = data.get('column', 0)
        error_stack = data.get('stack', '')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        user_agent = request.headers.get('User-Agent', 'unknown')
        
        log_func = logger.error if level == 'ERROR' else (logger.warning if level == 'WARNING' else logger.info)
        
        log_func(f"[CLIENT] {level}: {message}")
        log_func(f"[CLIENT] Location: {url}:{line}:{column}")
        if error_stack:
            log_func(f"[CLIENT] Stack:\n{error_stack}")
        log_func(f"[CLIENT] User Agent: {user_agent}")
        
        return jsonify({
            'success': True,
            'message': 'Client error logged'
        })
        
    except Exception as e:
        logger.error(f"Error logging client error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'code': 'SERVER_ERROR'}
        }), 500


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
    
    if hana_data_source:
        logger.info(f"HANA: {HANA_USER}@{HANA_HOST}:{HANA_PORT}")
    else:
        logger.warning("WARNING: HANA not configured")
    
    logger.info("Starting Flask server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=(ENV == 'development'))