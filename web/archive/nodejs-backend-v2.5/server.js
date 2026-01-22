/**
 * P2P Data Products Backend API Server
 * 
 * Provides real HANA Cloud database connectivity for the frontend application.
 * Uses @sap/hana-client for database operations.
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */

const express = require('express');
const hana = require('@sap/hana-client');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
    next();
});

// HANA Configuration from environment
const hanaConfig = {
    host: process.env.HANA_HOST,
    port: process.env.HANA_PORT || 443,
    user: process.env.HANA_USER,
    password: process.env.HANA_PASSWORD,
    currentSchema: process.env.HANA_SCHEMA || '',
    encrypt: true,
    sslValidateCertificate: false // Set to true in production
};

/**
 * Create and configure HANA connection
 * @returns {Object} HANA connection object
 */
function createConnection() {
    const connection = hana.createConnection();
    return connection;
}

/**
 * Execute SQL query with proper error handling
 * @param {string} sql - SQL query to execute
 * @returns {Promise<Object>} Query result
 */
async function executeQuery(sql) {
    const connection = createConnection();
    const startTime = Date.now();
    
    return new Promise((resolve, reject) => {
        // Connect to HANA
        connection.connect(hanaConfig, (err) => {
            if (err) {
                console.error('Connection error:', err);
                return reject({
                    code: 'CONNECTION_ERROR',
                    message: `Failed to connect to HANA Cloud: ${err.message}`,
                    details: err
                });
            }
            
            console.log('✓ Connected to HANA Cloud');
            
            // Execute SQL
            connection.exec(sql, (err, rows) => {
                const executionTime = Date.now() - startTime;
                
                // Always disconnect
                connection.disconnect();
                
                if (err) {
                    console.error('Query error:', err);
                    return reject({
                        code: err.code || 'EXECUTION_ERROR',
                        message: err.message,
                        details: err,
                        executionTime
                    });
                }
                
                console.log(`✓ Query executed successfully (${executionTime}ms, ${rows.length} rows)`);
                
                // Extract column metadata
                const columns = rows.length > 0 
                    ? Object.keys(rows[0]).map(name => ({
                        name,
                        type: typeof rows[0][name] === 'number' ? 'NUMBER' : 'VARCHAR'
                    }))
                    : [];
                
                resolve({
                    success: true,
                    rowCount: rows.length,
                    columns,
                    rows,
                    executionTime,
                    timestamp: new Date().toISOString()
                });
            });
        });
    });
}

/**
 * Detect SQL query type
 * @param {string} sql - SQL query
 * @returns {string} Query type (SELECT, INSERT, UPDATE, etc.)
 */
function detectQueryType(sql) {
    const cleaned = sql
        .replace(/--[^\n]*/g, '')
        .replace(/\/\*[\s\S]*?\*\//g, '')
        .trim()
        .toUpperCase();
    
    if (cleaned.startsWith('SELECT')) return 'SELECT';
    if (cleaned.startsWith('INSERT')) return 'INSERT';
    if (cleaned.startsWith('UPDATE')) return 'UPDATE';
    if (cleaned.startsWith('DELETE')) return 'DELETE';
    if (cleaned.startsWith('CREATE')) return 'CREATE';
    if (cleaned.startsWith('DROP')) return 'DROP';
    if (cleaned.startsWith('ALTER')) return 'ALTER';
    if (cleaned.startsWith('GRANT')) return 'GRANT';
    if (cleaned.startsWith('REVOKE')) return 'REVOKE';
    if (cleaned.startsWith('CALL')) return 'CALL';
    
    return 'UNKNOWN';
}

// ============================================================================
// API ENDPOINTS
// ============================================================================

/**
 * Health check endpoint
 */
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        version: '1.0.0'
    });
});

/**
 * Test HANA connection endpoint
 */
app.get('/api/test-connection', async (req, res) => {
    const connection = createConnection();
    
    connection.connect(hanaConfig, (err) => {
        if (err) {
            console.error('Connection test failed:', err);
            return res.json({
                success: false,
                message: 'Connection failed',
                error: err.message
            });
        }
        
        connection.exec('SELECT CURRENT_USER, CURRENT_SCHEMA FROM DUMMY', (err, rows) => {
            connection.disconnect();
            
            if (err) {
                return res.json({
                    success: false,
                    message: 'Query failed',
                    error: err.message
                });
            }
            
            res.json({
                success: true,
                message: 'Connection successful',
                data: rows[0]
            });
        });
    });
});

/**
 * Execute SQL query endpoint
 * POST /api/execute-sql
 * Body: { sql: "SELECT * FROM ...", maxRows: 100 }
 */
app.post('/api/execute-sql', async (req, res) => {
    const { sql, maxRows = 1000 } = req.body;
    
    // Validation
    if (!sql || typeof sql !== 'string' || sql.trim() === '') {
        return res.status(400).json({
            success: false,
            error: {
                code: 'INVALID_SQL',
                message: 'SQL query is required and must be a non-empty string'
            }
        });
    }
    
    // Detect query type
    const queryType = detectQueryType(sql);
    
    console.log(`\n=== SQL Execution Request ===`);
    console.log(`Query Type: ${queryType}`);
    console.log(`SQL: ${sql.substring(0, 100)}${sql.length > 100 ? '...' : ''}`);
    console.log(`Max Rows: ${maxRows}`);
    
    try {
        // Execute query
        const result = await executeQuery(sql);
        
        // Limit rows if needed
        if (result.rows.length > maxRows) {
            result.rows = result.rows.slice(0, maxRows);
            result.rowCount = maxRows;
            result.truncated = true;
            result.totalRows = result.rows.length;
        }
        
        // Add query type to result
        result.queryType = queryType;
        
        res.json(result);
        
    } catch (error) {
        console.error('Query execution failed:', error);
        
        res.json({
            success: false,
            queryType,
            error: {
                code: error.code || 'EXECUTION_ERROR',
                message: error.message,
                details: error.details ? error.details.message : null
            },
            executionTime: error.executionTime || 0,
            timestamp: new Date().toISOString()
        });
    }
});

/**
 * Get HANA instance info
 */
app.get('/api/instance-info', async (req, res) => {
    try {
        const result = await executeQuery(`
            SELECT 
                VERSION,
                USAGE
            FROM M_DATABASE
        `);
        
        res.json({
            success: true,
            data: result.rows[0]
        });
    } catch (error) {
        res.json({
            success: false,
            error: error.message
        });
    }
});

// ============================================================================
// DATA PRODUCTS EXPLORER API ENDPOINTS
// ============================================================================

/**
 * List all data product schemas
 * GET /api/data-products
 */
app.get('/api/data-products', async (req, res) => {
    console.log('\n=== Listing Data Products ===');
    
    try {
        const result = await executeQuery(`
            SELECT 
                SCHEMA_NAME,
                SCHEMA_OWNER,
                CREATE_TIME
            FROM SYS.SCHEMAS 
            WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%' 
            ORDER BY CREATE_TIME DESC
        `);
        
        // Parse schema names to extract metadata
        const dataProducts = result.rows.map(row => {
            const schemaName = row.SCHEMA_NAME;
            
            // Parse: _SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3
            const parts = schemaName.split('_');
            let productName = 'Unknown';
            let version = 'v1';
            let namespace = 'sap.s4com';
            
            // Extract product name (e.g., "Supplier", "PurchaseOrder")
            const dataProductIndex = parts.indexOf('dataProduct');
            if (dataProductIndex !== -1 && parts.length > dataProductIndex + 1) {
                // Find product name and version
                for (let i = dataProductIndex + 1; i < parts.length; i++) {
                    if (parts[i].startsWith('v') && /^v\d+$/.test(parts[i])) {
                        version = parts[i];
                        break;
                    } else if (i === dataProductIndex + 1) {
                        productName = parts[i];
                    }
                }
            }
            
            return {
                schemaName,
                productName,
                version,
                namespace,
                owner: row.SCHEMA_OWNER,
                createTime: row.CREATE_TIME
            };
        });
        
        res.json({
            success: true,
            count: dataProducts.length,
            dataProducts,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('Failed to list data products:', error);
        res.status(500).json({
            success: false,
            error: {
                code: error.code || 'LIST_ERROR',
                message: error.message
            }
        });
    }
});

/**
 * Get tables in a data product schema
 * GET /api/data-products/:schemaName/tables
 */
app.get('/api/data-products/:schemaName/tables', async (req, res) => {
    const { schemaName } = req.params;
    
    console.log(`\n=== Getting Tables for Schema: ${schemaName} ===`);
    
    // Validate schema name
    if (!schemaName.startsWith('_SAP_DATAPRODUCT')) {
        return res.status(400).json({
            success: false,
            error: {
                code: 'INVALID_SCHEMA',
                message: 'Schema name must start with _SAP_DATAPRODUCT'
            }
        });
    }
    
    try {
        const result = await executeQuery(`
            SELECT 
                TABLE_NAME,
                TABLE_TYPE
            FROM SYS.TABLES 
            WHERE SCHEMA_NAME = '${schemaName}'
            ORDER BY TABLE_NAME
        `);
        
        res.json({
            success: true,
            schemaName,
            count: result.rows.length,
            tables: result.rows,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('Failed to get tables:', error);
        res.status(500).json({
            success: false,
            error: {
                code: error.code || 'TABLES_ERROR',
                message: error.message
            }
        });
    }
});

/**
 * Get table structure (columns)
 * GET /api/data-products/:schemaName/:tableName/structure
 */
app.get('/api/data-products/:schemaName/:tableName/structure', async (req, res) => {
    const { schemaName, tableName } = req.params;
    
    console.log(`\n=== Getting Structure for ${schemaName}.${tableName} ===`);
    
    // Validate schema name
    if (!schemaName.startsWith('_SAP_DATAPRODUCT')) {
        return res.status(400).json({
            success: false,
            error: {
                code: 'INVALID_SCHEMA',
                message: 'Schema name must start with _SAP_DATAPRODUCT'
            }
        });
    }
    
    try {
        const result = await executeQuery(`
            SELECT 
                COLUMN_NAME,
                DATA_TYPE_NAME,
                LENGTH,
                SCALE,
                IS_NULLABLE,
                DEFAULT_VALUE,
                POSITION,
                COMMENTS
            FROM SYS.TABLE_COLUMNS 
            WHERE SCHEMA_NAME = '${schemaName}'
              AND TABLE_NAME = '${tableName}'
            ORDER BY POSITION
        `);
        
        res.json({
            success: true,
            schemaName,
            tableName,
            columnCount: result.rows.length,
            columns: result.rows,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('Failed to get table structure:', error);
        res.status(500).json({
            success: false,
            error: {
                code: error.code || 'STRUCTURE_ERROR',
                message: error.message
            }
        });
    }
});

/**
 * Query table data
 * POST /api/data-products/:schemaName/:tableName/query
 * Body: { limit, offset, columns, where, orderBy }
 */
app.post('/api/data-products/:schemaName/:tableName/query', async (req, res) => {
    const { schemaName, tableName } = req.params;
    const { 
        limit = 100, 
        offset = 0, 
        columns = ['*'], 
        where = '', 
        orderBy = '' 
    } = req.body;
    
    console.log(`\n=== Querying Data from ${schemaName}.${tableName} ===`);
    console.log(`Limit: ${limit}, Offset: ${offset}`);
    
    // Validate schema name
    if (!schemaName.startsWith('_SAP_DATAPRODUCT')) {
        return res.status(400).json({
            success: false,
            error: {
                code: 'INVALID_SCHEMA',
                message: 'Schema name must start with _SAP_DATAPRODUCT'
            }
        });
    }
    
    // Validate limit
    const maxLimit = 1000;
    const safeLimit = Math.min(Math.max(1, parseInt(limit) || 100), maxLimit);
    const safeOffset = Math.max(0, parseInt(offset) || 0);
    
    // Build column list
    const columnList = Array.isArray(columns) && columns.length > 0 && columns[0] !== '*'
        ? columns.map(c => `"${c}"`).join(', ')
        : '*';
    
    // Build WHERE clause (basic validation)
    let whereClause = '';
    if (where && typeof where === 'string' && where.trim()) {
        // Basic SQL injection prevention - only allow simple conditions
        if (!/[;'"\\]|--/.test(where)) {
            whereClause = `WHERE ${where}`;
        } else {
            return res.status(400).json({
                success: false,
                error: {
                    code: 'INVALID_WHERE',
                    message: 'WHERE clause contains invalid characters'
                }
            });
        }
    }
    
    // Build ORDER BY clause
    let orderByClause = '';
    if (orderBy && typeof orderBy === 'string' && orderBy.trim()) {
        // Basic validation
        if (!/[;'"\\]|--/.test(orderBy)) {
            orderByClause = `ORDER BY ${orderBy}`;
        }
    }
    
    try {
        // Build and execute query
        const sql = `
            SELECT ${columnList}
            FROM "${schemaName}"."${tableName}"
            ${whereClause}
            ${orderByClause}
            LIMIT ${safeLimit} OFFSET ${safeOffset}
        `.trim();
        
        console.log(`SQL: ${sql.substring(0, 200)}...`);
        
        const result = await executeQuery(sql);
        
        // Get total count (without limit)
        let totalCount = result.rowCount;
        if (result.rowCount === safeLimit) {
            try {
                const countSql = `
                    SELECT COUNT(*) as TOTAL_COUNT
                    FROM "${schemaName}"."${tableName}"
                    ${whereClause}
                `;
                const countResult = await executeQuery(countSql);
                totalCount = countResult.rows[0].TOTAL_COUNT;
            } catch (e) {
                console.warn('Could not get total count:', e.message);
            }
        }
        
        res.json({
            success: true,
            schemaName,
            tableName,
            rowCount: result.rowCount,
            totalCount,
            limit: safeLimit,
            offset: safeOffset,
            hasMore: result.rowCount === safeLimit,
            columns: result.columns,
            rows: result.rows,
            executionTime: result.executionTime,
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('Failed to query table data:', error);
        res.status(500).json({
            success: false,
            error: {
                code: error.code || 'QUERY_ERROR',
                message: error.message
            }
        });
    }
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Unhandled error:', err);
    res.status(500).json({
        success: false,
        error: {
            code: 'INTERNAL_ERROR',
            message: err.message
        }
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        success: false,
        error: {
            code: 'NOT_FOUND',
            message: `Endpoint not found: ${req.method} ${req.path}`
        }
    });
});

// Start server
app.listen(PORT, () => {
    console.log('\n===========================================');
    console.log('🚀 P2P Data Products Backend API');
    console.log('===========================================');
    console.log(`Server: http://localhost:${PORT}`);
    console.log(`Health: http://localhost:${PORT}/api/health`);
    console.log(`HANA Host: ${hanaConfig.host}`);
    console.log(`HANA User: ${hanaConfig.user}`);
    console.log(`HANA Schema: ${hanaConfig.currentSchema || '(default)'}`);
    console.log('===========================================\n');
    console.log('Press Ctrl+C to stop\n');
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('\n👋 SIGTERM received, shutting down gracefully...');
    process.exit(0);
});

process.on('SIGINT', () => {
    console.log('\n👋 SIGINT received, shutting down gracefully...');
    process.exit(0);
});
