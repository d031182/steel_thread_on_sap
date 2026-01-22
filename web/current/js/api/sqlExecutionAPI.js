/**
 * SQL Execution API
 * 
 * Provides programmatic access to SQL query execution.
 * This API is UI-independent and fully testable.
 * 
 * Note: In browser mode, this simulates execution with mock data.
 * For real execution, connect to a backend proxy or use BTP deployment.
 * 
 * @module api/sqlExecutionAPI
 */

import { StorageService } from '../services/storageService.js';
import { HanaConnectionAPI } from './hanaConnectionAPI.js';

const HISTORY_KEY = 'queryHistory';
const MAX_HISTORY = 50;

export class SQLExecutionAPI {
    /**
     * Create SQL Execution API
     * @param {StorageService} [storageService] - Storage service instance
     * @param {HanaConnectionAPI} [connectionAPI] - Connection API instance
     */
    constructor(storageService, connectionAPI) {
        this.storage = storageService || new StorageService();
        this.connectionAPI = connectionAPI || new HanaConnectionAPI();
        this._activeQueries = new Map(); // Track running queries
    }

    /**
     * Execute a SQL query
     * @param {string} instanceId - Instance ID to execute against
     * @param {string} sql - SQL query to execute
     * @param {Object} [options] - Execution options
     * @param {number} [options.timeout=30000] - Query timeout in ms
     * @param {number} [options.maxRows=1000] - Maximum rows to return
     * @param {boolean} [options.includeMetadata=true] - Include column metadata
     * @returns {Promise<Object>} Execution result
     */
    async executeQuery(instanceId, sql, options = {}) {
        const startTime = Date.now();
        const queryId = this._generateQueryId();
        
        try {
            // Validate inputs
            if (!instanceId) {
                throw new Error('Instance ID is required');
            }
            if (!sql || sql.trim() === '') {
                throw new Error('SQL query is required');
            }

            // Get instance configuration
            const instance = await this.connectionAPI.getInstance(instanceId);
            if (!instance) {
                throw new Error(`Instance not found: ${instanceId}`);
            }

            // Set defaults
            const timeout = options.timeout || 30000;
            const maxRows = options.maxRows || 1000;
            const includeMetadata = options.includeMetadata !== false;

            // Detect query type
            const queryType = this._detectQueryType(sql);

            // Register active query
            this._activeQueries.set(queryId, {
                sql,
                startTime,
                instanceId
            });

            // Execute query (simulated in browser)
            const result = await this._executeQuerySimulated(
                instance,
                sql,
                queryType,
                { timeout, maxRows, includeMetadata }
            );

            // Calculate execution time
            const executionTime = Date.now() - startTime;

            // Build result object
            const queryResult = {
                success: true,
                queryId,
                instanceId,
                sql,
                queryType,
                executionTime,
                rowCount: result.rows ? result.rows.length : 0,
                columns: result.columns || [],
                rows: result.rows || [],
                metadata: includeMetadata ? result.metadata : undefined,
                timestamp: new Date().toISOString()
            };

            // Save to history
            await this.saveQueryHistory(queryResult);

            return queryResult;

        } catch (error) {
            const executionTime = Date.now() - startTime;
            
            const errorResult = {
                success: false,
                queryId,
                instanceId,
                sql,
                executionTime,
                error: {
                    message: error.message,
                    code: error.code || 'EXECUTION_ERROR',
                    details: error.details || null
                },
                timestamp: new Date().toISOString()
            };

            // Save failed query to history
            await this.saveQueryHistory(errorResult);

            return errorResult;

        } finally {
            // Clean up active query
            this._activeQueries.delete(queryId);
        }
    }

    /**
     * Execute multiple SQL queries in batch
     * @param {string} instanceId - Instance ID
     * @param {string[]} sqlArray - Array of SQL queries
     * @param {Object} [options] - Execution options
     * @returns {Promise<Object[]>} Array of results
     */
    async executeBatch(instanceId, sqlArray, options = {}) {
        if (!Array.isArray(sqlArray)) {
            throw new Error('SQL array must be an array');
        }

        const results = [];
        for (const sql of sqlArray) {
            const result = await this.executeQuery(instanceId, sql, options);
            results.push(result);
            
            // Stop on first error unless continueOnError is true
            if (!result.success && !options.continueOnError) {
                break;
            }
        }

        return results;
    }

    /**
     * Get query history
     * @param {Object} [filter] - Filter options
     * @param {number} [filter.limit=50] - Maximum number of entries
     * @param {string} [filter.instanceId] - Filter by instance
     * @param {boolean} [filter.successOnly=false] - Only successful queries
     * @returns {Promise<Array>} Query history
     */
    async getQueryHistory(filter = {}) {
        let history = this.storage.load(HISTORY_KEY, []);

        // Apply filters
        if (filter.instanceId) {
            history = history.filter(h => h.instanceId === filter.instanceId);
        }
        if (filter.successOnly) {
            history = history.filter(h => h.success);
        }

        // Apply limit
        const limit = filter.limit || MAX_HISTORY;
        return history.slice(0, limit);
    }

    /**
     * Save query to history
     * @param {Object} queryResult - Query result to save
     * @returns {Promise<boolean>} Success status
     */
    async saveQueryHistory(queryResult) {
        try {
            let history = this.storage.load(HISTORY_KEY, []);

            // Add to beginning
            history.unshift({
                queryId: queryResult.queryId,
                instanceId: queryResult.instanceId,
                sql: queryResult.sql,
                queryType: queryResult.queryType,
                success: queryResult.success,
                rowCount: queryResult.rowCount,
                executionTime: queryResult.executionTime,
                timestamp: queryResult.timestamp,
                error: queryResult.error
            });

            // Keep only MAX_HISTORY entries
            if (history.length > MAX_HISTORY) {
                history = history.slice(0, MAX_HISTORY);
            }

            return this.storage.save(HISTORY_KEY, history);
        } catch (error) {
            console.error('Error saving query history:', error);
            return false;
        }
    }

    /**
     * Clear query history
     * @param {string} [instanceId] - Clear for specific instance, or all if not provided
     * @returns {Promise<boolean>} Success status
     */
    async clearHistory(instanceId) {
        if (instanceId) {
            let history = this.storage.load(HISTORY_KEY, []);
            history = history.filter(h => h.instanceId !== instanceId);
            return this.storage.save(HISTORY_KEY, history);
        } else {
            return this.storage.remove(HISTORY_KEY);
        }
    }

    /**
     * Get execution plan for a query (simulated)
     * @param {string} instanceId - Instance ID
     * @param {string} sql - SQL query
     * @returns {Promise<Object>} Execution plan
     */
    async getExecutionPlan(instanceId, sql) {
        const instance = await this.connectionAPI.getInstance(instanceId);
        if (!instance) {
            throw new Error(`Instance not found: ${instanceId}`);
        }

        // Simulated execution plan
        return {
            queryType: this._detectQueryType(sql),
            estimatedCost: Math.floor(Math.random() * 1000),
            estimatedRows: Math.floor(Math.random() * 10000),
            operations: [
                { type: 'TABLE_SCAN', table: 'SAMPLE_TABLE', cost: 100 },
                { type: 'FILTER', condition: 'WHERE clause', cost: 50 },
                { type: 'PROJECTION', columns: ['*'], cost: 10 }
            ],
            warnings: [],
            timestamp: new Date().toISOString()
        };
    }

    /**
     * Cancel a running query
     * @param {string} queryId - Query ID to cancel
     * @returns {Promise<boolean>} True if cancelled
     */
    async cancelQuery(queryId) {
        if (this._activeQueries.has(queryId)) {
            this._activeQueries.delete(queryId);
            return true;
        }
        return false;
    }

    /**
     * Get active queries
     * @returns {Promise<Array>} Array of active query info
     */
    async getActiveQueries() {
        const active = [];
        for (const [queryId, info] of this._activeQueries.entries()) {
            active.push({
                queryId,
                sql: info.sql,
                instanceId: info.instanceId,
                startTime: info.startTime,
                elapsedTime: Date.now() - info.startTime
            });
        }
        return active;
    }

    /**
     * Detect SQL query type
     * @private
     * @param {string} sql - SQL query
     * @returns {string} Query type
     */
    _detectQueryType(sql) {
        // Remove comments and trim
        let cleaned = sql
            .replace(/--[^\n]*/g, '') // Remove line comments
            .replace(/\/\*[\s\S]*?\*\//g, '') // Remove block comments
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

    /**
     * Generate unique query ID
     * @private
     * @returns {string} Query ID
     */
    _generateQueryId() {
        return `query-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Execute query (simulated for browser)
     * In production, this would connect to a backend proxy
     * @private
     * @param {Object} instance - Instance configuration
     * @param {string} sql - SQL query
     * @param {string} queryType - Detected query type
     * @param {Object} options - Execution options
     * @returns {Promise<Object>} Query result
     */
    async _executeQuerySimulated(instance, sql, queryType, options) {
        // Simulate network delay
        await this._delay(500 + Math.random() * 1000);

        // Simulate different query types
        if (queryType === 'SELECT') {
            return this._simulateSelectQuery(sql, options);
        } else if (queryType === 'INSERT') {
            return this._simulateInsertQuery(sql);
        } else if (queryType === 'UPDATE') {
            return this._simulateUpdateQuery(sql);
        } else if (queryType === 'DELETE') {
            return this._simulateDeleteQuery(sql);
        } else {
            return this._simulateOtherQuery(sql, queryType);
        }
    }

    /**
     * Simulate SELECT query
     * @private
     */
    _simulateSelectQuery(sql, options) {
        const rowCount = Math.min(
            Math.floor(Math.random() * 20) + 5,
            options.maxRows
        );

        // Generate sample columns based on common patterns
        const columns = this._generateSampleColumns(sql);
        const rows = this._generateSampleRows(columns, rowCount);

        return {
            columns: columns.map(col => ({
                name: col,
                type: 'NVARCHAR',
                length: 255,
                nullable: true
            })),
            rows,
            metadata: {
                executionPlan: 'Simulated execution plan',
                warnings: []
            }
        };
    }

    /**
     * Simulate INSERT query
     * @private
     */
    _simulateInsertQuery(sql) {
        return {
            columns: [{ name: 'ROWS_AFFECTED', type: 'INTEGER' }],
            rows: [[1]],
            metadata: {
                rowsAffected: 1,
                message: '1 row inserted'
            }
        };
    }

    /**
     * Simulate UPDATE query
     * @private
     */
    _simulateUpdateQuery(sql) {
        const rowsAffected = Math.floor(Math.random() * 10) + 1;
        return {
            columns: [{ name: 'ROWS_AFFECTED', type: 'INTEGER' }],
            rows: [[rowsAffected]],
            metadata: {
                rowsAffected,
                message: `${rowsAffected} row(s) updated`
            }
        };
    }

    /**
     * Simulate DELETE query
     * @private
     */
    _simulateDeleteQuery(sql) {
        const rowsAffected = Math.floor(Math.random() * 5) + 1;
        return {
            columns: [{ name: 'ROWS_AFFECTED', type: 'INTEGER' }],
            rows: [[rowsAffected]],
            metadata: {
                rowsAffected,
                message: `${rowsAffected} row(s) deleted`
            }
        };
    }

    /**
     * Simulate other query types
     * @private
     */
    _simulateOtherQuery(sql, queryType) {
        return {
            columns: [{ name: 'RESULT', type: 'NVARCHAR' }],
            rows: [[`${queryType} executed successfully`]],
            metadata: {
                message: `${queryType} command completed`
            }
        };
    }

    /**
     * Generate sample columns from SQL
     * @private
     */
    _generateSampleColumns(sql) {
        // Try to extract column names from SELECT clause
        const selectMatch = sql.match(/SELECT\s+(.*?)\s+FROM/i);
        if (selectMatch && selectMatch[1] !== '*') {
            const cols = selectMatch[1].split(',').map(c => c.trim().split(/\s+/)[0]);
            if (cols.length > 0 && cols.length < 20) {
                return cols;
            }
        }

        // Default columns
        return ['ID', 'NAME', 'CREATED_AT', 'STATUS'];
    }

    /**
     * Generate sample rows
     * @private
     */
    _generateSampleRows(columns, rowCount) {
        const rows = [];
        for (let i = 0; i < rowCount; i++) {
            const row = [];
            for (const col of columns) {
                row.push(this._generateSampleValue(col, i));
            }
            rows.push(row);
        }
        return rows;
    }

    /**
     * Generate sample value for column
     * @private
     */
    _generateSampleValue(columnName, index) {
        const colUpper = columnName.toUpperCase();
        
        if (colUpper.includes('ID')) {
            return index + 1;
        }
        if (colUpper.includes('NAME')) {
            return `Sample ${index + 1}`;
        }
        if (colUpper.includes('DATE') || colUpper.includes('TIME')) {
            return new Date(Date.now() - Math.random() * 86400000 * 30).toISOString();
        }
        if (colUpper.includes('STATUS')) {
            const statuses = ['Active', 'Inactive', 'Pending', 'Completed'];
            return statuses[Math.floor(Math.random() * statuses.length)];
        }
        if (colUpper.includes('AMOUNT') || colUpper.includes('PRICE')) {
            return (Math.random() * 1000).toFixed(2);
        }
        
        return `Value ${index + 1}`;
    }

    /**
     * Utility: Delay
     * @private
     */
    _delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Default instance (only in browser environment with localStorage)
export const sqlExecutionAPI = typeof localStorage !== 'undefined'
    ? new SQLExecutionAPI()
    : null;
