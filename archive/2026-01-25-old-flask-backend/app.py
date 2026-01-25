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
app = Flask(__name__, static_folder='..', static_url_path='')
CORS(app)  # Enable CORS for all routes

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
                logger.info(f"Connecting to HANA: {self.user}@{self.host}:{self.port}")
                self.connection = dbapi.connect(
                    address=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    encrypt=True,
                    sslValidateCertificate=False
                )
                logger.info("HANA connection established successfully")
                return True
            except Exception as e:
                logger.error(f"HANA connection error: {str(e)}")
                return False
        return True
    
    def execute_query(self, sql, params=None):
        """Execute SQL query with optional parameters and return results"""
        if not self.connect():
            raise Exception("Failed to connect to HANA")
        
        cursor = self.connection.cursor()
        start_time = datetime.now()
        
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
            
            logger.info(f"Query executed successfully: {len(result)} rows, {execution_time:.2f}ms")
            
            return {
                'success': True,
                'rows': result,
                'rowCount': len(result),
                'columnCount': len(columns),
                'columns': columns,
                'executionTime': round(execution_time, 2)
            }
            
        except Exception as e:
            logger.error(f"SQL execution error: {str(e)}")
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
    return send_from_directory(os.path.join(app.static_folder, 'webapp'), 'p2p-fiori-proper.html')


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


@app.route('/api/data-products/<schema_name>/csn', methods=['GET'])
def get_data_product_csn(schema_name):
    """
    Get CSN (Core Schema Notation) definition for a data product via BDC MCP
    
    This endpoint retrieves the authoritative CSN schema from SAP Business Data Cloud
    using the MCP (Model Context Protocol) server connection.
    
    Args:
        schema_name: Data product schema name (e.g., 'sap_s4com_Supplier_v1')
    
    Returns:
        JSON with CSN definition or error
    """
    try:
        # Validate schema name
        if not schema_name:
            logger.warning("CSN requested with empty schema name")
            return jsonify({
                'success': False,
                'error': {'message': 'Schema name is required', 'code': 'MISSING_SCHEMA_NAME'}
            }), 400
        
        logger.info(f"Fetching CSN definition for schema: {schema_name}")
        
        # Convert schema name to ORD ID format
        # Example: sap_s4com_Supplier_v1 -> sap.s4com:apiResource:Supplier:v1
        parts = schema_name.split('_')
        
        if len(parts) < 4:
            logger.warning(f"Invalid schema name format: {schema_name}")
            return jsonify({
                'success': False,
                'error': {'message': 'Invalid schema name format', 'code': 'INVALID_SCHEMA_FORMAT'}
            }), 400
        
        # Extract components
        vendor = parts[0]  # sap
        product = parts[1]  # s4com
        # Find version (starts with 'v' and followed by digit)
        version = 'v1'  # default
        product_name_parts = []
        
        for i, part in enumerate(parts[2:], start=2):
            if part.startswith('v') and len(part) > 1 and part[1:].split('_')[0].isdigit():
                version = part.split('_')[0]  # Handle v1_xxx format
                break
            else:
                product_name_parts.append(part)
        
        product_name = '_'.join(product_name_parts) if product_name_parts else parts[2]
        
        # Construct ORD ID
        ord_id = f"{vendor}.{product}:apiResource:{product_name}:{version}"
        
        logger.info(f"Converted schema name to ORD ID: {ord_id}")
        
        # TODO: In production, this would call the BDC MCP server
        # For now, return a helpful message with instructions
        
        # Check if we have local CSN file as fallback
        local_csn_path = f"data-products/{vendor}-{product}-{product_name}-{version}.en.json"
        local_csn_path_alt = f"data-products/{vendor}-{product}-{product_name}-{version}.en-complete.json"
        
        import os
        if os.path.exists(local_csn_path):
            logger.info(f"Loading CSN from local file: {local_csn_path}")
            with open(local_csn_path, 'r', encoding='utf-8') as f:
                csn_data = json.load(f)
            
            return jsonify({
                'success': True,
                'source': 'local_file',
                'schemaName': schema_name,
                'ordId': ord_id,
                'csn': csn_data,
                'message': 'CSN loaded from local file (BDC MCP integration pending)'
            })
        elif os.path.exists(local_csn_path_alt):
            logger.info(f"Loading CSN from local file: {local_csn_path_alt}")
            with open(local_csn_path_alt, 'r', encoding='utf-8') as f:
                csn_data = json.load(f)
            
            return jsonify({
                'success': True,
                'source': 'local_file',
                'schemaName': schema_name,
                'ordId': ord_id,
                'csn': csn_data,
                'message': 'CSN loaded from local file (BDC MCP integration pending)'
            })
        else:
            logger.warning(f"CSN file not found locally: {local_csn_path}")
            return jsonify({
                'success': False,
                'error': {
                    'message': 'CSN not available locally. BDC MCP integration required.',
                    'code': 'CSN_NOT_FOUND',
                    'ordId': ord_id,
                    'hint': 'Use BDC MCP csnSchema tool to retrieve from SAP Business Data Cloud'
                }
            }), 404
        
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
