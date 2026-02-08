/**
 * DataProductsAdapter - Backend API Client
 * 
 * Purpose: Connects frontend to Flask data_products backend API
 * Pattern: Adapter Pattern (implements IDataSource interface)
 * 
 * Architecture:
 * - Browser (App V2) → HTTP → Flask Backend → Repository → HANA/SQLite
 * - This adapter is the "Browser → HTTP" layer
 * 
 * Features:
 * - ✅ Implements all 5 IDataSource methods
 * - ✅ Retry logic for transient failures (3 attempts, exponential backoff)
 * - ✅ Error handling with user-friendly messages
 * - ✅ Caching support (optional, via ICache)
 * - ✅ Request timeout (30s default)
 * - ✅ Health check via testConnection()
 * 
 * Usage:
 *   const adapter = new DataProductsAdapter({ baseUrl: '/api/data_products' });
 *   const tables = await adapter.getTables();
 *   const results = await adapter.query('SELECT * FROM Supplier');
 * 
 * @implements {IDataSource}
 */
class DataProductsAdapter extends IDataSource {
    /**
     * Create adapter instance
     * 
     * @param {Object} config - Configuration
     * @param {string} config.baseUrl - Base API URL (default: '/api/data_products')
     * @param {string} config.source - Data source ('hana' or 'sqlite', default: 'hana')
     * @param {number} config.timeout - Request timeout in ms (default: 30000)
     * @param {number} config.maxRetries - Max retry attempts (default: 3)
     * @param {ICache} config.cache - Optional cache instance
     */
    constructor(config = {}) {
        super();
        
        this._baseUrl = config.baseUrl || '/api/data_products';
        this._source = config.source || 'hana';
        this._timeout = config.timeout || 30000;
        this._maxRetries = config.maxRetries || 3;
        this._cache = config.cache || null;
        
        // Statistics
        this._stats = {
            requests: 0,
            successes: 0,
            failures: 0,
            retries: 0,
            cacheHits: 0,
            cacheMisses: 0,
            totalTime: 0
        };
    }
    
    /**
     * Execute SQL query
     * 
     * @param {string} sql - SQL query string
     * @param {Array} params - Query parameters (not yet supported by backend)
     * @returns {Promise<Array>} Query results
     */
    async query(sql, params = []) {
        if (!sql || typeof sql !== 'string') {
            throw new Error('SQL query must be a non-empty string');
        }
        
        if (sql.trim().length === 0) {
            throw new Error('SQL query cannot be empty');
        }
        
        // Check cache (if available)
        const cacheKey = `query:${this._source}:${sql}`;
        if (this._cache) {
            const cached = await this._cache.get(cacheKey);
            if (cached) {
                this._stats.cacheHits++;
                return cached;
            }
            this._stats.cacheMisses++;
        }
        
        // Execute query via backend API
        const startTime = performance.now();
        
        try {
            const response = await this._fetchWithRetry(
                `${this._baseUrl}/execute-sql`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sql })
                }
            );
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error?.message || 'Query execution failed');
            }
            
            const rows = result.rows || [];
            
            // Cache successful results (5 min TTL)
            if (this._cache && rows.length > 0) {
                await this._cache.set(cacheKey, rows, 300);
            }
            
            this._stats.successes++;
            this._stats.totalTime += (performance.now() - startTime);
            
            return rows;
            
        } catch (error) {
            this._stats.failures++;
            this._stats.totalTime += (performance.now() - startTime);
            throw new Error(`Query failed: ${error.message}`);
        }
    }
    
    /**
     * Get list of available tables
     * 
     * @returns {Promise<Array<string>>} Array of table names
     */
    async getTables() {
        // Check cache (if available)
        const cacheKey = `tables:${this._source}`;
        if (this._cache) {
            const cached = await this._cache.get(cacheKey);
            if (cached) {
                this._stats.cacheHits++;
                return cached;
            }
            this._stats.cacheMisses++;
        }
        
        const startTime = performance.now();
        
        try {
            // Get all data products (schemas)
            const response = await this._fetchWithRetry(
                `${this._baseUrl}/?source=${this._source}`
            );
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.error?.message || 'Failed to fetch data products');
            }
            
            // Extract all table names from all schemas
            const tables = [];
            for (const schema of result.data_products || []) {
                if (schema.tables) {
                    tables.push(...schema.tables.map(t => t.name));
                }
            }
            
            // Cache results (10 min TTL)
            if (this._cache) {
                await this._cache.set(cacheKey, tables, 600);
            }
            
            this._stats.successes++;
            this._stats.totalTime += (performance.now() - startTime);
            
            return tables;
            
        } catch (error) {
            this._stats.failures++;
            this._stats.totalTime += (performance.now() - startTime);
            throw new Error(`Failed to get tables: ${error.message}`);
        }
    }
    
    /**
     * Get schema for a table
     * 
     * @param {string} tableName - Table name
     * @returns {Promise<Object>} Table schema with columns and types
     */
    async getTableSchema(tableName) {
        if (!tableName) {
            throw new Error('Table name is required');
        }
        
        // Check cache (if available)
        const cacheKey = `schema:${this._source}:${tableName}`;
        if (this._cache) {
            const cached = await this._cache.get(cacheKey);
            if (cached) {
                this._stats.cacheHits++;
                return cached;
            }
            this._stats.cacheMisses++;
        }
        
        const startTime = performance.now();
        
        try {
            // We need to find which schema contains this table
            // For now, we'll try common schemas
            const commonSchemas = ['P2P_SCHEMA', 'PUBLIC'];
            
            for (const schemaName of commonSchemas) {
                try {
                    const response = await this._fetchWithRetry(
                        `${this._baseUrl}/${schemaName}/${tableName}/structure?source=${this._source}`
                    );
                    
                    const result = await response.json();
                    
                    if (result.success) {
                        const schema = {
                            tableName: tableName,
                            schemaName: schemaName,
                            columns: result.columns.map(c => c.name),
                            types: result.columns.map(c => c.type),
                            columnDetails: result.columns
                        };
                        
                        // Cache results (10 min TTL)
                        if (this._cache) {
                            await this._cache.set(cacheKey, schema, 600);
                        }
                        
                        this._stats.successes++;
                        this._stats.totalTime += (performance.now() - startTime);
                        
                        return schema;
                    }
                } catch (e) {
                    // Try next schema
                    continue;
                }
            }
            
            throw new Error(`Table '${tableName}' not found in any schema`);
            
        } catch (error) {
            this._stats.failures++;
            this._stats.totalTime += (performance.now() - startTime);
            throw new Error(`Failed to get table schema: ${error.message}`);
        }
    }
    
    /**
     * Get data source type
     * 
     * @returns {string} Data source type identifier
     */
    getType() {
        return this._source; // 'hana' or 'sqlite'
    }
    
    /**
     * Test connection (health check)
     * 
     * @returns {Promise<boolean>} True if connection healthy
     */
    async testConnection() {
        const startTime = performance.now();
        
        try {
            // Try to list data products (lightweight operation)
            const response = await this._fetchWithRetry(
                `${this._baseUrl}/?source=${this._source}`,
                { method: 'GET' },
                { maxRetries: 1 } // Only 1 retry for health checks
            );
            
            const result = await response.json();
            
            this._stats.totalTime += (performance.now() - startTime);
            
            return result.success === true;
            
        } catch (error) {
            this._stats.totalTime += (performance.now() - startTime);
            return false;
        }
    }
    
    /**
     * Fetch with retry logic (exponential backoff)
     * 
     * @private
     * @param {string} url - Request URL
     * @param {Object} options - Fetch options
     * @param {Object} retryConfig - Retry configuration override
     * @returns {Promise<Response>}
     */
    async _fetchWithRetry(url, options = {}, retryConfig = {}) {
        const maxRetries = retryConfig.maxRetries !== undefined 
            ? retryConfig.maxRetries 
            : this._maxRetries;
        
        let lastError = null;
        
        for (let attempt = 0; attempt <= maxRetries; attempt++) {
            try {
                this._stats.requests++;
                
                // Add timeout to request
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this._timeout);
                
                const response = await fetch(url, {
                    ...options,
                    signal: controller.signal
                });
                
                clearTimeout(timeoutId);
                
                // Check HTTP status
                if (!response.ok) {
                    const errorText = await response.text();
                    throw new Error(
                        `HTTP ${response.status}: ${response.statusText}\n${errorText}`
                    );
                }
                
                return response;
                
            } catch (error) {
                lastError = error;
                
                // Don't retry on client errors (4xx)
                if (error.message.includes('HTTP 4')) {
                    throw error;
                }
                
                // Don't retry on timeout abort
                if (error.name === 'AbortError') {
                    throw new Error(`Request timeout after ${this._timeout}ms`);
                }
                
                // Retry on network errors or 5xx
                if (attempt < maxRetries) {
                    this._stats.retries++;
                    
                    // Exponential backoff: 1s, 2s, 4s, 8s...
                    const delay = Math.pow(2, attempt) * 1000;
                    await new Promise(resolve => setTimeout(resolve, delay));
                    
                    console.warn(
                        `[DataProductsAdapter] Retry ${attempt + 1}/${maxRetries} ` +
                        `after ${delay}ms: ${error.message}`
                    );
                } else {
                    throw error;
                }
            }
        }
        
        throw lastError;
    }
    
    /**
     * Get adapter statistics
     * 
     * @returns {Object} Statistics object
     */
    getStats() {
        const avgTime = this._stats.requests > 0 
            ? this._stats.totalTime / this._stats.requests 
            : 0;
        
        const successRate = this._stats.requests > 0
            ? this._stats.successes / this._stats.requests
            : 0;
        
        const cacheHitRate = (this._stats.cacheHits + this._stats.cacheMisses) > 0
            ? this._stats.cacheHits / (this._stats.cacheHits + this._stats.cacheMisses)
            : 0;
        
        return {
            requests: this._stats.requests,
            successes: this._stats.successes,
            failures: this._stats.failures,
            retries: this._stats.retries,
            successRate: successRate,
            avgResponseTime: Math.round(avgTime),
            cacheHitRate: cacheHitRate,
            cacheHits: this._stats.cacheHits,
            cacheMisses: this._stats.cacheMisses,
            type: 'DataProductsAdapter',
            source: this._source,
            timeout: this._timeout,
            maxRetries: this._maxRetries
        };
    }
    
    /**
     * Clear statistics
     */
    clearStats() {
        this._stats = {
            requests: 0,
            successes: 0,
            failures: 0,
            retries: 0,
            cacheHits: 0,
            cacheMisses: 0,
            totalTime: 0
        };
    }
    
    /**
     * Set cache instance
     * 
     * @param {ICache} cache - Cache instance
     */
    setCache(cache) {
        this._cache = cache;
    }
    
    /**
     * Get cache instance
     * 
     * @returns {ICache|null}
     */
    getCache() {
        return this._cache;
    }
}

// Export for module systems (ES6)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataProductsAdapter;
}

// Export for browser global (App V2 pattern)
if (typeof window !== 'undefined') {
    window.DataProductsAdapter = DataProductsAdapter;
}