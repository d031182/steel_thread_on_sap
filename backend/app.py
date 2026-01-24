"""
P2P Data Products Flask Backend
================================
Flask-based REST API for P2P Data Products application.
Provides endpoints for HANA Cloud data products, SQL execution, and connection management.

Author: P2P Development Team
Version: 1.1.0
Date: 2026-01-22
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
import logging
from datetime import datetime, timedelta
from hdbcli import dbapi
import traceback
import sqlite3
import threading
import time
from queue import Queue
import requests
from functools import lru_cache
from csn_urls import get_csn_url, schema_name_to_ord_id, get_all_p2p_products

# SQLite log storage
class SQLiteLogHandler(logging.Handler):
    """Custom log handler that stores logs in SQLite database"""
    def __init__(self, db_path='logs/app_logs.db', retention_days=2):
        super().__init__()
        self.db_path = db_path
        self.retention_days = retention_days
        self.queue = Queue()
        self.lock = threading.Lock()
        
        # Initialize database
        self.init_database()
        
        # Start background writer thread
        self.writer_thread = threading.Thread(target=self._writer_loop, daemon=True)
        self.writer_thread.start()
        
        # Start cleanup thread
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
    
    def init_database(self):
        """Initialize SQLite database with schema"""
        os.makedirs(os.path.dirname(self.db_path) if os.path.dirname(self.db_path) else '.', exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS application_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                level VARCHAR(10) NOT NULL,
                logger VARCHAR(100) NOT NULL,
                message TEXT NOT NULL,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON application_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_level ON application_logs(level)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON application_logs(created_at)')
        
        conn.commit()
        conn.close()
    
    def emit(self, record):
        """Store log record in queue for async writing"""
        try:
            log_entry = {
                'timestamp': datetime.fromtimestamp(record.created).isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': self.format(record)
            }
            self.queue.put(log_entry)
        except Exception:
            self.handleError(record)
    
    def _writer_loop(self):
        """Background thread that writes logs to database"""
        batch = []
        last_write = time.time()
        
        while True:
            try:
                # Collect logs from queue
                timeout = 5.0 - (time.time() - last_write)
                if timeout > 0:
                    try:
                        log_entry = self.queue.get(timeout=timeout)
                        batch.append(log_entry)
                    except:
                        pass
                
                # Write batch if we have logs and either batch is full or timeout
                if batch and (len(batch) >= 100 or time.time() - last_write >= 5.0):
                    self._write_batch(batch)
                    batch = []
                    last_write = time.time()
                
            except Exception as e:
                print(f"Error in log writer thread: {e}")
                time.sleep(1)
    
    def _write_batch(self, batch):
        """Write a batch of logs to database"""
        if not batch:
            return
        
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.executemany('''
                    INSERT INTO application_logs (timestamp, level, logger, message)
                    VALUES (?, ?, ?, ?)
                ''', [(log['timestamp'], log['level'], log['logger'], log['message']) for log in batch])
                
                conn.commit()
            except Exception as e:
                print(f"Error writing logs to database: {e}")
            finally:
                conn.close()
    
    def _cleanup_loop(self):
        """Background thread that cleans up old logs"""
        while True:
            try:
                time.sleep(21600)  # Run every 6 hours
                self.cleanup_old_logs()
            except Exception as e:
                print(f"Error in cleanup thread: {e}")
    
    def cleanup_old_logs(self):
        """Delete logs older than retention period"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                cursor.execute('DELETE FROM application_logs WHERE created_at < ?', 
                             (cutoff_date.isoformat(),))
                deleted = cursor.rowcount
                conn.commit()
                
                # Vacuum if needed
                cursor.execute('PRAGMA page_count')
                page_count = cursor.fetchone()[0]
                cursor.execute('PRAGMA page_size')
                page_size = cursor.fetchone()[0]
                db_size_mb = (page_count * page_size) / (1024 * 1024)
                
                if db_size_mb > 50:
                    cursor.execute('VACUUM')
                    conn.commit()
                
                print(f"Cleaned up {deleted} old logs (retention: {self.retention_days} days)")
                
            except Exception as e:
                print(f"Error cleaning up logs: {e}")
            finally:
                conn.close()
    
    def get_logs(self, level=None, limit=100, offset=0, start_date=None, end_date=None):
        """Retrieve logs from database with filtering"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = 'SELECT * FROM application_logs WHERE 1=1'
            params = []
            
            if level:
                query += ' AND level = ?'
                params.append(level)
            
            if start_date:
                query += ' AND created_at >= ?'
                params.append(start_date)
            
            if end_date:
                query += ' AND created_at <= ?'
                params.append(end_date)
            
            query += ' ORDER BY id DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            logs = [{
                'id': row['id'],
                'timestamp': row['timestamp'],
                'level': row['level'],
                'logger': row['logger'],
                'message': row['message']
            } for row in rows]
            
            conn.close()
            return logs
    
    def get_log_count(self, level=None):
        """Get total count of logs"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if level:
                cursor.execute('SELECT COUNT(*) FROM application_logs WHERE level = ?', (level,))
            else:
                cursor.execute('SELECT COUNT(*) FROM application_logs')
            
            count = cursor.fetchone()[0]
            conn.close()
            return count
    
    def clear_logs(self):
        """Clear all logs"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM application_logs')
            conn.commit()
            conn.close()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add SQLite handler to capture logs
log_db_path = os.getenv('LOG_DB_PATH', 'logs/app_logs.db')
log_retention_days = int(os.getenv('LOG_RETENTION_DAYS', '2'))
sqlite_handler = SQLiteLogHandler(db_path=log_db_path, retention_days=log_retention_days)
sqlite_handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(sqlite_handler)

logger.info(f"SQLite logging initialized: {log_db_path} (retention: {log_retention_days} days)")

# Initialize Flask app
# Calculate static folder path relative to this file's location
import os
import sys
backend_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(backend_dir)
# Use the complete standalone application with HANA + logging features
static_path = os.path.join(project_root, 'web', 'current')

app = Flask(__name__, static_folder=static_path, static_url_path='')
CORS(app)  # Enable CORS for all routes

# Register Feature Manager Blueprint
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'modules'))
try:
    # Import from feature-manager directory (with hyphen, not underscore)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "feature_manager_api", 
        os.path.join(project_root, "modules", "feature-manager", "backend", "api.py")
    )
    feature_manager_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(feature_manager_module)
    
    app.register_blueprint(feature_manager_module.feature_manager_api)
    logger.info("✓ Feature Manager API registered at /api/features")
except FileNotFoundError as e:
    logger.warning(f"⚠️  Feature Manager API not found: {e}")
except ImportError as e:
    logger.warning(f"⚠️  Feature Manager API import error: {e}")
except Exception as e:
    logger.error(f"✗ Failed to register Feature Manager API: {e}")

# Configuration from environment
HANA_HOST = os.getenv('HANA_HOST', '')
HANA_PORT = int(os.getenv('HANA_PORT', '443'))
HANA_USER = os.getenv('HANA_USER', '')
HANA_PASSWORD = os.getenv('HANA_PASSWORD', '')
HANA_SCHEMA = os.getenv('HANA_SCHEMA', 'P2P_SCHEMA')
ENV = os.getenv('ENV', 'development')

# Global connection pool
hana_connections = {}


class HANAConnection:
    """HANA Cloud connection manager"""
    
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.connection = None
    
    def connect(self):
        """Establish connection to HANA Cloud"""
        if self.connection is None:
            try:
                logger.info(f"[HANA] Attempting connection to {self.host}:{self.port} as user '{self.user}'")
                self.connection = dbapi.connect(
                    address=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    encrypt=True,
                    sslValidateCertificate=False
                )
                logger.info(f"[HANA] ✓ Connection established successfully to {self.host}:{self.port}")
                return True
            except dbapi.Error as e:
                # Log HANA-specific errors with detailed context
                error_code = getattr(e, 'errorcode', 'UNKNOWN')
                error_text = str(e)
                logger.error(f"[HANA] ✗ Connection failed to {self.host}:{self.port}")
                logger.error(f"[HANA] Error code: {error_code}")
                logger.error(f"[HANA] Error message: {error_text}")
                logger.error(f"[HANA] User: {self.user}")
                logger.error(f"[HANA] Possible causes:")
                logger.error(f"[HANA]   - IP not in HANA Cloud allowlist (most common)")
                logger.error(f"[HANA]   - Invalid credentials")
                logger.error(f"[HANA]   - HANA instance not running")
                logger.error(f"[HANA]   - Network connectivity issues")
                return False
            except Exception as e:
                # Log non-HANA errors
                logger.error(f"[HANA] ✗ Unexpected connection error: {type(e).__name__}")
                logger.error(f"[HANA] Error details: {str(e)}")
                logger.error(f"[HANA] Traceback:\n{traceback.format_exc()}")
                return False
        return True
    
    def execute_query(self, sql, params=None):
        """Execute SQL query with optional parameters and return results"""
        if not self.connect():
            logger.error("[HANA] Cannot execute query - connection failed")
            raise Exception("Failed to connect to HANA")
        
        cursor = self.connection.cursor()
        start_time = datetime.now()
        
        # Log query execution start
        sql_preview = sql[:200] + '...' if len(sql) > 200 else sql
        if params:
            logger.info(f"[HANA] Executing query with {len(params)} parameters")
        logger.info(f"[HANA] SQL: {sql_preview}")
        
        try:
            # Execute with or without parameters
            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            result = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    # Convert datetime to string
                    if isinstance(value, datetime):
                        value = value.isoformat()
                    row_dict[col] = value
                result.append(row_dict)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            logger.info(f"[HANA] ✓ Query executed successfully: {len(result)} rows, {len(columns)} columns, {execution_time:.2f}ms")
            
            return {
                'success': True,
                'rows': result,
                'rowCount': len(result),
                'columnCount': len(columns),
                'columns': columns,
                'executionTime': round(execution_time, 2)
            }
            
        except dbapi.Error as e:
            # Log HANA SQL errors with detailed context
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            error_code = getattr(e, 'errorcode', 'UNKNOWN')
            error_text = str(e)
            
            logger.error(f"[HANA] ✗ SQL execution failed after {execution_time:.2f}ms")
            logger.error(f"[HANA] Error code: {error_code}")
            logger.error(f"[HANA] Error message: {error_text}")
            logger.error(f"[HANA] SQL: {sql_preview}")
            if params:
                logger.error(f"[HANA] Parameters: {params}")
            logger.error(f"[HANA] Possible causes:")
            logger.error(f"[HANA]   - Invalid SQL syntax")
            logger.error(f"[HANA]   - Table/column does not exist")
            logger.error(f"[HANA]   - Insufficient privileges")
            logger.error(f"[HANA]   - Invalid parameter values")
            
            return {
                'success': False,
                'error': {
                    'message': error_text,
                    'code': 'SQL_ERROR',
                    'errorCode': error_code
                }
            }
        except Exception as e:
            # Log unexpected errors
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"[HANA] ✗ Unexpected query error after {execution_time:.2f}ms: {type(e).__name__}")
            logger.error(f"[HANA] Error details: {str(e)}")
            logger.error(f"[HANA] SQL: {sql_preview}")
            logger.error(f"[HANA] Traceback:\n{traceback.format_exc()}")
            
            return {
                'success': False,
                'error': {
                    'message': str(e),
                    'code': 'SQL_ERROR'
                }
            }
        finally:
            cursor.close()
    
    def close(self):
        """Close connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("HANA connection closed")


# Initialize default HANA connection
if HANA_HOST and HANA_USER and HANA_PASSWORD:
    hana_connections['default'] = HANAConnection(
        HANA_HOST, HANA_PORT, HANA_USER, HANA_PASSWORD
    )
    logger.info("Default HANA connection configured")
else:
    logger.warning("HANA connection not fully configured - check environment variables")


# Request logging middleware
@app.before_request
def log_request():
    """Log all incoming requests"""
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")


@app.after_request
def log_response(response):
    """Log all responses"""
    logger.info(f"{request.method} {request.path} - Status: {response.status_code}")
    return response


# API Routes

@app.route('/')
def index():
    """Serve main application"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/feature-manager')
def feature_manager_ui():
    """Serve Feature Manager Configurator UI"""
    template_path = os.path.join(project_root, 'modules', 'feature-manager', 'templates')
    return send_from_directory(template_path, 'configurator_simple.html')


@app.route('/modules/<path:filepath>')
def serve_module_files(filepath):
    """Serve module frontend files (views, controllers, etc.)"""
    modules_path = os.path.join(project_root, 'modules')
    return send_from_directory(modules_path, filepath)


@app.route('/api/health')
def health():
    """Health check endpoint"""
    hana_status = 'connected' if hana_connections.get('default') else 'not_configured'
    
    # Test HANA connection
    if hana_connections.get('default'):
        try:
            conn = hana_connections['default']
            if conn.connect():
                hana_status = 'healthy'
            else:
                hana_status = 'connection_failed'
        except Exception as e:
            hana_status = 'error'
            logger.error(f"Health check error: {str(e)}")
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.1.0',
        'hana': hana_status
    })


@app.route('/api/data-products', methods=['GET'])
def list_data_products():
    """List all installed data product schemas"""
    try:
        conn = hana_connections.get('default')
        if not conn:
            logger.error("HANA connection not configured")
            return jsonify({
                'success': False,
                'error': {'message': 'HANA connection not configured', 'code': 'NOT_CONFIGURED'}
            }), 500
        
        # Query to find all data product schemas - using parameterized query
        sql = """
        SELECT 
            SCHEMA_NAME,
            SCHEMA_OWNER,
            CREATE_TIME
        FROM SYS.SCHEMAS
        WHERE SCHEMA_NAME LIKE ?
        ORDER BY SCHEMA_NAME
        """
        
        result = conn.execute_query(sql, ('_SAP_DATAPRODUCT%',))
        
        if not result['success']:
            logger.error(f"Failed to list data products: {result.get('error')}")
            return jsonify(result), 500
        
        # Parse schema names to extract metadata
        data_products = []
        for row in result['rows']:
            schema_name = row['SCHEMA_NAME']
            
            # Parse schema name: _SAP_DATAPRODUCT_sap_s4com_dataProduct_ProductName_v1_uuid
            parts = schema_name.split('_')
            
            product_name = 'Unknown'
            version = 'v1'
            namespace = 'sap.s4com'
            
            # Extract namespace
            if len(parts) > 3:
                namespace = parts[3].replace('-', '.')
            
            # Extract product name and version
            if 'dataProduct' in parts:
                dp_index = parts.index('dataProduct')
                if dp_index + 1 < len(parts):
                    product_name = parts[dp_index + 1]
                # Find version
                for part in parts[dp_index+2:]:
                    if part.startswith('v') and part[1:].isdigit():
                        version = part
                        break
            
            data_products.append({
                'schemaName': schema_name,
                'productName': product_name,
                'displayName': product_name.replace('_', ' ').title(),
                'version': version,
                'namespace': namespace,
                'owner': row.get('SCHEMA_OWNER', ''),
                'createTime': row.get('CREATE_TIME', '')
            })
        
        logger.info(f"Found {len(data_products)} data products")
        
        return jsonify({
            'success': True,
            'count': len(data_products),
            'dataProducts': data_products
        })
        
    except Exception as e:
        logger.error(f"Error in list_data_products: {str(e)}\n{traceback.format_exc()}")
        error_message = str(e) if ENV == 'development' else 'Internal server error'
        return jsonify({
            'success': False,
            'error': {
                'message': error_message,
                'code': 'SERVER_ERROR'
            }
        }), 500


@app.route('/api/data-products/<schema_name>/tables', methods=['GET'])
def get_schema_tables(schema_name):
    """Get tables in a data product schema"""
    try:
        # Validate schema name
        if not schema_name.startswith('_SAP_DATAPRODUCT'):
            logger.warning(f"Invalid schema name requested: {schema_name}")
            return jsonify({
                'success': False,
                'error': {'message': 'Invalid schema name', 'code': 'INVALID_INPUT'}
            }), 400
        
        conn = hana_connections.get('default')
        if not conn:
            logger.error("HANA connection not configured")
            return jsonify({
                'success': False,
                'error': {'message': 'HANA connection not configured', 'code': 'NOT_CONFIGURED'}
            }), 500
        
        # Use parameterized query to prevent SQL injection
        sql = """
        SELECT 
            TABLE_NAME,
            TABLE_TYPE
        FROM SYS.TABLES
        WHERE SCHEMA_NAME = ?
        ORDER BY TABLE_NAME
        """
        
        result = conn.execute_query(sql, (schema_name,))
        
        if not result['success']:
            logger.error(f"Failed to get schema tables: {result.get('error')}")
            return jsonify(result), 500
        
        # Get record counts for each table
        tables_with_counts = []
        for table in result['rows']:
            table_name = table['TABLE_NAME']
            try:
                # Get row count for this table
                count_sql = f'SELECT COUNT(*) as RECORD_COUNT FROM "{schema_name}"."{table_name}"'
                count_result = conn.execute_query(count_sql)
                record_count = count_result['rows'][0]['RECORD_COUNT'] if count_result['success'] and count_result['rows'] else 0
                
                tables_with_counts.append({
                    'TABLE_NAME': table_name,
                    'TABLE_TYPE': table['TABLE_TYPE'],
                    'RECORD_COUNT': record_count
                })
            except Exception as e:
                logger.warning(f"Failed to get count for table {table_name}: {str(e)}")
                # Include table even if count fails
                tables_with_counts.append({
                    'TABLE_NAME': table_name,
                    'TABLE_TYPE': table['TABLE_TYPE'],
                    'RECORD_COUNT': 0
                })
        
        logger.info(f"Found {len(tables_with_counts)} tables in schema {schema_name}")
        
        return jsonify({
            'success': True,
            'count': len(tables_with_counts),
            'schemaName': schema_name,
            'tables': tables_with_counts
        })
        
    except Exception as e:
        logger.error(f"Error in get_schema_tables: {str(e)}\n{traceback.format_exc()}")
        error_message = str(e) if ENV == 'development' else 'Internal server error'
        return jsonify({
            'success': False,
            'error': {'message': error_message, 'code': 'SERVER_ERROR'}
        }), 500


@app.route('/api/data-products/<schema_name>/<table_name>/structure', methods=['GET'])
def get_table_structure(schema_name, table_name):
    """Get detailed table structure (columns, types, constraints)"""
    try:
        # Validate schema name
        if not schema_name.startswith('_SAP_DATAPRODUCT'):
            logger.warning(f"Invalid schema name requested: {schema_name}")
            return jsonify({
                'success': False,
                'error': {'message': 'Invalid schema name', 'code': 'INVALID_INPUT'}
            }), 400
        
        # Validate table name
        if not all(c.isalnum() or c in '_.-' for c in table_name):
            logger.warning(f"Invalid table name requested: {table_name}")
            return jsonify({
                'success': False,
                'error': {'message': 'Invalid table name', 'code': 'INVALID_INPUT'}
            }), 400
        
        conn = hana_connections.get('default')
        if not conn:
            logger.error("HANA connection not configured")
            return jsonify({
                'success': False,
                'error': {'message': 'HANA connection not configured', 'code': 'NOT_CONFIGURED'}
            }), 500
        
        # Get table columns with detailed information
        sql = """
        SELECT 
            COLUMN_NAME,
            POSITION,
            DATA_TYPE_NAME,
            LENGTH,
            SCALE,
            IS_NULLABLE,
            DEFAULT_VALUE,
            COMMENTS
        FROM SYS.TABLE_COLUMNS
        WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
        ORDER BY POSITION
        """
        
        result = conn.execute_query(sql, (schema_name, table_name))
        
        if not result['success']:
            logger.error(f"Failed to get table structure: {result.get('error')}")
            return jsonify(result), 500
        
        logger.info(f"Retrieved structure for {schema_name}.{table_name}: {len(result['rows'])} columns")
        
        # Format columns
        columns = []
        for row in result['rows']:
            col_info = {
                'name': row['COLUMN_NAME'],
                'position': row['POSITION'],
                'dataType': row['DATA_TYPE_NAME'],
                'length': row.get('LENGTH'),
                'scale': row.get('SCALE'),
                'nullable': row['IS_NULLABLE'] == 'TRUE',
                'defaultValue': row.get('DEFAULT_VALUE'),
                'comment': row.get('COMMENTS')
            }
            columns.append(col_info)
        
        return jsonify({
            'success': True,
            'schemaName': schema_name,
            'tableName': table_name,
            'columnCount': len(columns),
            'columns': columns
        })
        
    except Exception as e:
        logger.error(f"Error in get_table_structure: {str(e)}\n{traceback.format_exc()}")
        error_message = str(e) if ENV == 'development' else 'Internal server error'
        return jsonify({
            'success': False,
            'error': {'message': error_message, 'code': 'SERVER_ERROR'}
        }), 500


@app.route('/api/data-products/<schema_name>/<table_name>/query', methods=['POST'])
def query_table(schema_name, table_name):
    """Query data from a table"""
    try:
        # Validate schema name
        if not schema_name.startswith('_SAP_DATAPRODUCT'):
            logger.warning(f"Invalid schema name requested: {schema_name}")
            return jsonify({
                'success': False,
                'error': {'message': 'Invalid schema name', 'code': 'INVALID_INPUT'}
            }), 400
        
        # Validate table name (alphanumeric, underscore, dot, hyphen only)
        # HANA table names can contain: letters, numbers, underscores, dots, hyphens
        if not all(c.isalnum() or c in '_.-' for c in table_name):
            logger.warning(f"Invalid table name requested: {table_name}")
            return jsonify({
                'success': False,
                'error': {'message': 'Invalid table name', 'code': 'INVALID_INPUT'}
            }), 400
        
        conn = hana_connections.get('default')
        if not conn:
            logger.error("HANA connection not configured")
            return jsonify({
                'success': False,
                'error': {'message': 'HANA connection not configured', 'code': 'NOT_CONFIGURED'}
            }), 500
        
        # Get query parameters
        data = request.get_json() or {}
        limit = min(int(data.get('limit', 100)), 1000)  # Cap at 1000
        offset = max(int(data.get('offset', 0)), 0)  # Ensure non-negative
        
        # Get table structure to identify key columns
        struct_sql = f"""
        SELECT COLUMN_NAME, POSITION
        FROM SYS.TABLE_COLUMNS
        WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
        ORDER BY POSITION
        """
        
        struct_result = conn.execute_query(struct_sql, (schema_name, table_name))
        
        if struct_result['success'] and struct_result['rows']:
            # Get first 10 columns for preview (essential columns)
            columns = [row['COLUMN_NAME'] for row in struct_result['rows'][:10]]
            column_list = ', '.join([f'"{col}"' for col in columns])
            
            # Add indicator if there are more columns
            total_columns = len(struct_result['rows'])
            if total_columns > 10:
                logger.info(f"Limiting to first 10 of {total_columns} columns for table {table_name}")
        else:
            # Fallback to SELECT * if we can't get structure
            column_list = '*'
        
        # Use parameterized query with proper quoting for identifiers
        sql = f"""
        SELECT {column_list}
        FROM "{schema_name}"."{table_name}"
        LIMIT ? OFFSET ?
        """
        
        result = conn.execute_query(sql, (limit, offset))
        
        if not result['success']:
            logger.error(f"Failed to query table: {result.get('error')}")
            return jsonify(result), 500
        
        logger.info(f"Queried {result['rowCount']} rows from {schema_name}.{table_name}")
        
        # Get total count for pagination
        count_sql = f'SELECT COUNT(*) as TOTAL FROM "{schema_name}"."{table_name}"'
        count_result = conn.execute_query(count_sql)
        total_count = count_result['rows'][0]['TOTAL'] if count_result['success'] and count_result['rows'] else result['rowCount']
        
        return jsonify({
            'success': True,
            'schemaName': schema_name,
            'tableName': table_name,
            'rows': result['rows'],
            'rowCount': result['rowCount'],
            'totalCount': total_count,
            'limit': limit,
            'offset': offset,
            'columns': [{'name': col} for col in result['columns']],
            'executionTime': result['executionTime']
        })
        
    except Exception as e:
        logger.error(f"Error in query_table: {str(e)}\n{traceback.format_exc()}")
        error_message = str(e) if ENV == 'development' else 'Internal server error'
        return jsonify({
            'success': False,
            'error': {'message': error_message, 'code': 'SERVER_ERROR'}
        }), 500


@app.route('/api/execute-sql', methods=['POST'])
def execute_sql():
    """Execute arbitrary SQL query"""
    try:
        conn = hana_connections.get('default')
        if not conn:
            logger.error("HANA connection not configured")
            return jsonify({
                'success': False,
                'error': {'message': 'HANA connection not configured', 'code': 'NOT_CONFIGURED'}
            }), 500
        
        data = request.get_json()
        sql = data.get('sql', '').strip()
        
        # Validate SQL input
        if not sql:
            return jsonify({
                'success': False,
                'error': {'message': 'SQL query is required', 'code': 'MISSING_SQL'}
            }), 400
        
        # Basic length validation (prevent extremely long queries)
        if len(sql) > 50000:
            logger.warning(f"SQL query too long: {len(sql)} characters")
            return jsonify({
                'success': False,
                'error': {'message': 'SQL query too long (max 50000 characters)', 'code': 'QUERY_TOO_LONG'}
            }), 400
        
        logger.info(f"Executing SQL query: {sql[:100]}..." if len(sql) > 100 else f"Executing SQL query: {sql}")
        
        result = conn.execute_query(sql)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error in execute_sql: {str(e)}\n{traceback.format_exc()}")
        error_message = str(e) if ENV == 'development' else 'Internal server error'
        return jsonify({
            'success': False,
            'error': {'message': error_message, 'code': 'SERVER_ERROR'}
        }), 500


@app.route('/api/connections', methods=['GET'])
def list_connections():
    """List HANA connections"""
    return jsonify({
        'success': True,
        'connections': [
            {
                'id': 'default',
                'name': f'{HANA_USER}@{HANA_HOST}',
                'host': HANA_HOST,
                'port': HANA_PORT,
                'user': HANA_USER,
                'schema': HANA_SCHEMA
            }
        ]
    })


@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get application logs from SQLite database"""
    try:
        # Get query parameters
        level = request.args.get('level', None)  # INFO, WARNING, ERROR
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        # Validate level
        if level and level not in ['INFO', 'WARNING', 'ERROR']:
            return jsonify({
                'success': False,
                'error': {'message': 'Invalid log level', 'code': 'INVALID_LEVEL'}
            }), 400
        
        # Get logs from SQLite handler
        logs = sqlite_handler.get_logs(
            level=level, 
            limit=limit, 
            offset=offset,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get total count for pagination
        total_count = sqlite_handler.get_log_count(level=level)
        
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
        total = sqlite_handler.get_log_count()
        info_count = sqlite_handler.get_log_count(level='INFO')
        warning_count = sqlite_handler.get_log_count(level='WARNING')
        error_count = sqlite_handler.get_log_count(level='ERROR')
        
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
    """Clear all stored logs"""
    try:
        sqlite_handler.clear_logs()
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
    """
    Log client-side errors from browser console
    
    This endpoint receives JavaScript errors, warnings, and logs from the frontend
    and stores them in the application log for analysis.
    """
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
        
        # Map client log levels to Python logging levels
        log_func = logger.error
        if level == 'WARNING' or level == 'WARN':
            log_func = logger.warning
        elif level == 'INFO':
            log_func = logger.info
        
        # Log with detailed context
        log_func(f"[CLIENT] {level}: {message}")
        log_func(f"[CLIENT] Location: {url}:{line}:{column}")
        if error_stack:
            log_func(f"[CLIENT] Stack trace:\n{error_stack}")
        log_func(f"[CLIENT] User Agent: {user_agent}")
        log_func(f"[CLIENT] Timestamp: {timestamp}")
        
        return jsonify({
            'success': True,
            'message': 'Client error logged successfully'
        })
        
    except Exception as e:
        logger.error(f"Error logging client error: {str(e)}")
        return jsonify({
            'success': False,
            'error': {'message': str(e), 'code': 'SERVER_ERROR'}
        }), 500


@lru_cache(maxsize=20)
def fetch_csn_from_discovery_api(csn_url):
    """
    Fetch CSN from SAP Discovery API (cached for performance)
    
    Args:
        csn_url: URL to CSN definition
    
    Returns:
        dict: CSN data
    """
    logger.info(f"[Discovery API] Fetching CSN from: {csn_url}")
    
    try:
        response = requests.get(csn_url, timeout=10)
        response.raise_for_status()
        
        csn_data = response.json()
        logger.info(f"[Discovery API] ✓ CSN fetched successfully ({len(str(csn_data))} bytes)")
        
        return csn_data
        
    except requests.exceptions.Timeout:
        logger.error(f"[Discovery API] ✗ Timeout fetching CSN from {csn_url}")
        raise Exception("Timeout fetching CSN from Discovery API")
    except requests.exceptions.RequestException as e:
        logger.error(f"[Discovery API] ✗ HTTP error: {e}")
        raise Exception(f"Failed to fetch CSN: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"[Discovery API] ✗ Invalid JSON response: {e}")
        raise Exception("Invalid CSN format received")


@app.route('/api/data-products/<schema_name>/csn', methods=['GET'])
def get_data_product_csn(schema_name):
    """
    Get CSN (Core Schema Notation) definition for a data product
    
    This endpoint fetches CSN directly from SAP's public Discovery API.
    The CSN URLs are pre-mapped in csn_urls.py for all P2P data products.
    
    Args:
        schema_name: Data product schema name (e.g., 'Supplier', 'sap_s4com_Supplier_v1')
    
    Returns:
        JSON with CSN definition
    """
    try:
        # Validate schema name
        if not schema_name:
            logger.warning("CSN requested with empty schema name")
            return jsonify({
                'success': False,
                'error': {'message': 'Schema name is required', 'code': 'MISSING_SCHEMA_NAME'}
            }), 400
        
        logger.info(f"[CSN Viewer] Fetching CSN definition for: {schema_name}")
        
        # Convert schema name to ORD ID
        ord_id = schema_name_to_ord_id(schema_name)
        
        if not ord_id:
            logger.warning(f"[CSN Viewer] No ORD ID mapping found for: {schema_name}")
            return jsonify({
                'success': False,
                'error': {
                    'message': f'No CSN mapping found for schema: {schema_name}',
                    'code': 'SCHEMA_NOT_MAPPED',
                    'availableProducts': [p['name'] for p in get_all_p2p_products()]
                }
            }), 404
        
        logger.info(f"[CSN Viewer] Mapped to ORD ID: {ord_id}")
        
        # Get CSN URL for this ORD ID
        csn_url = get_csn_url(ord_id)
        
        if not csn_url:
            logger.error(f"[CSN Viewer] No CSN URL found for ORD ID: {ord_id}")
            return jsonify({
                'success': False,
                'error': {
                    'message': f'No CSN URL configured for: {ord_id}',
                    'code': 'CSN_URL_NOT_FOUND'
                }
            }), 404
        
        # Fetch CSN from Discovery API (cached)
        try:
            csn_data = fetch_csn_from_discovery_api(csn_url)
            
            logger.info(f"[CSN Viewer] ✓ Successfully fetched CSN for {schema_name}")
            
            return jsonify({
                'success': True,
                'schemaName': schema_name,
                'ordId': ord_id,
                'csnUrl': csn_url,
                'csn': csn_data
            })
            
        except Exception as fetch_error:
            logger.error(f"[CSN Viewer] Failed to fetch CSN: {str(fetch_error)}")
            return jsonify({
                'success': False,
                'error': {
                    'message': str(fetch_error),
                    'code': 'CSN_FETCH_FAILED',
                    'csnUrl': csn_url
                }
            }), 500
        
    except Exception as e:
        logger.error(f"Error in get_data_product_csn: {str(e)}\n{traceback.format_exc()}")
        error_message = str(e) if ENV == 'development' else 'Internal server error'
        return jsonify({
            'success': False,
            'error': {'message': error_message, 'code': 'SERVER_ERROR'}
        }), 500


# Error handlers

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 Not Found: {request.path}")
    return jsonify({
        'success': False,
        'error': {
            'message': 'Endpoint not found',
            'code': 'NOT_FOUND'
        }
    }), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Internal Server Error: {str(error)}")
    error_message = str(error) if ENV == 'development' else 'Internal server error'
    return jsonify({
        'success': False,
        'error': {
            'message': error_message,
            'code': 'INTERNAL_ERROR'
        }
    }), 500


# Main entry point

if __name__ == '__main__':
    # Check configuration
    if not all([HANA_HOST, HANA_USER, HANA_PASSWORD]):
        logger.warning("⚠️  HANA connection not fully configured")
        logger.warning("Set HANA_HOST, HANA_USER, HANA_PASSWORD environment variables")
    else:
        logger.info(f"✓ HANA configured: {HANA_USER}@{HANA_HOST}:{HANA_PORT}")
    
    # Log environment
    logger.info(f"Environment: {ENV}")
    logger.info(f"Static folder: {app.static_folder}")
    
    # Run Flask app
    logger.info("🚀 Starting Flask server on http://localhost:5000")
    logger.info("📱 Access application at: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=(ENV == 'development'))
