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
from core.backend.module_registry import ModuleRegistry
from core.interfaces.data_source import DataSource
from core.interfaces.logger import ApplicationLogger
from modules.hana_connection.backend import HANADataSource
from modules.sqlite_connection.backend import SQLiteDataSource
from modules.application_logging.backend import SQLiteLogHandler, LoggingService

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
LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', '2'))
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
logger = logging.getLogger(__name__)

# Initialize logging service (dependency injection)
logging_service = LoggingService(db_path=LOG_DB_PATH, retention_days=LOG_RETENTION_DAYS)
sqlite_handler = logging_service.get_handler()
sqlite_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(sqlite_handler)

logger.info(f"SQLite logging initialized: {LOG_DB_PATH} (retention: {LOG_RETENTION_DAYS} days)")

# Initialize Flask app  
static_path = os.path.join(backend_dir, 'static')
app = Flask(__name__, static_folder=static_path, static_url_path='')
CORS(app)

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
sqlite_data_source: DataSource = SQLiteDataSource()

if HANA_HOST and HANA_USER and HANA_PASSWORD:
    hana_data_source = HANADataSource(HANA_HOST, HANA_PORT, HANA_USER, HANA_PASSWORD)
    logger.info("HANA data source initialized")
else:
    logger.warning("WARNING: HANA not configured - only SQLite source available")

# Attach data sources to app for blueprint access
app.hana_data_source = hana_data_source
app.sqlite_data_source = sqlite_data_source

# Register Module Blueprints
try:
    # Feature Manager Blueprint
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "feature_manager_api",
        os.path.join(project_root, "modules", "feature_manager", "backend", "api.py")
    )
    feature_manager_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(feature_manager_module)
    
    app.register_blueprint(feature_manager_module.feature_manager_api)
    logger.info("Feature Manager API registered at /api/features")
except Exception as e:
    logger.warning(f"WARNING: Feature Manager API not registered: {e}")

try:
    # Data Products Blueprint
    from modules.data_products.backend import data_products_api
    app.register_blueprint(data_products_api)
    logger.info("Data Products API registered at /api/data-products")
except Exception as e:
    logger.warning(f"WARNING: Data Products API not registered: {e}")

try:
    # SQL Execution Blueprint
    from modules.sql_execution.backend import sql_execution_api
    app.register_blueprint(sql_execution_api)
    logger.info("SQL Execution API registered at /api/sql")
except Exception as e:
    logger.warning(f"WARNING: SQL Execution API not registered: {e}")

try:
    # CSN Validation Blueprint
    from modules.csn_validation.backend import csn_validation_api
    app.register_blueprint(csn_validation_api)
    logger.info("CSN Validation API registered at /api/csn")
except Exception as e:
    logger.warning(f"WARNING: CSN Validation API not registered: {e}")


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
    """Log all incoming requests"""
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")


@app.after_request
def log_response(response):
    """Log all responses"""
    logger.info(f"{request.method} {request.path} - Status: {response.status_code}")
    return response


# Static file routes
@app.route('/')
def index():
    """Serve P2P Application with ShellBar"""
    return send_from_directory(app.static_folder, 'app.html')


@app.route('/app')
def data_products_app():
    """Serve Data Products application"""
    return send_from_directory(app.static_folder, 'index.html')


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