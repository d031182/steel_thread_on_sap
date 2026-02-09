/**
 * DataProductsV2Adapter - Specialized Adapter for Data Products V2 API
 * =====================================================================
 * 
 * Purpose: Adapter specifically for Data Products V2 backend API
 * 
 * Key Methods (used by frontend):
 * - query('data_products', {}) → GET /api/v2/data-products/
 * - getTables(productName) → GET /api/v2/data-products/{productName}/tables
 * - getTableStructure(productName, tableName) → GET /api/v2/data-products/{productName}/{tableName}/structure
 * - queryTable(productName, tableName, limit, offset) → POST /api/v2/data-products/{productName}/{tableName}/query
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */
class DataProductsV2Adapter {
    /**
     * Create adapter
     * 
     * @param {Object} config - Configuration
     * @param {string} config.baseUrl - Base API URL (default: '/api/v2/data-products')
     * @param {string} config.source - Data source ('hana' or 'sqlite', default: 'sqlite')
     * @param {number} config.timeout - Request timeout in ms (default: 30000)
     */
    constructor(config = {}) {
        this._baseUrl = config.baseUrl || '/api/v2/data-products';
        this._source = config.source || 'sqlite';
        this._timeout = config.timeout || 30000;
    }

    /**
     * Query data products (special method for initial load)
     * 
     * @param {string} resource - Resource type ('data_products')
     * @param {Object} options - Query options
     * @returns {Promise<Array>} Array of data products
     */
    async query(resource, options = {}) {
        if (resource === 'data_products' && options.operation === 'list') {
            // Fetch data products list
            const response = await fetch(
                `${this._baseUrl}/?source=${this._source}`,
                { 
                    method: 'GET',
                    signal: AbortSignal.timeout(this._timeout)
                }
            );

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();

            if (!result.success) {
                throw new Error(result.error || 'Failed to fetch data products');
            }

            return result.data_products || [];
        }

        throw new Error(`Unsupported query: ${resource} / ${options.operation}`);
    }

    /**
     * Get tables in a data product
     * 
     * @param {string} productName - Data product name
     * @returns {Promise<Array>} Array of tables
     */
    async getTables(productName) {
        const response = await fetch(
            `${this._baseUrl}/${productName}/tables?source=${this._source}`,
            {
                method: 'GET',
                signal: AbortSignal.timeout(this._timeout)
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Failed to fetch tables');
        }

        return result.tables || [];
    }

    /**
     * Get table structure (columns)
     * 
     * @param {string} productName - Data product name
     * @param {string} tableName - Table name
     * @returns {Promise<Array>} Array of columns
     */
    async getTableStructure(productName, tableName) {
        const response = await fetch(
            `${this._baseUrl}/${productName}/${tableName}/structure?source=${this._source}`,
            {
                method: 'GET',
                signal: AbortSignal.timeout(this._timeout)
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Failed to fetch table structure');
        }

        return result.columns || [];
    }

    /**
     * Query table data
     * 
     * @param {string} productName - Data product name
     * @param {string} tableName - Table name
     * @param {number} limit - Row limit
     * @param {number} offset - Row offset
     * @returns {Promise<Object>} Query result with rows and columns
     */
    async queryTable(productName, tableName, limit = 100, offset = 0) {
        const response = await fetch(
            `${this._baseUrl}/${productName}/${tableName}/query?source=${this._source}`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ limit, offset }),
                signal: AbortSignal.timeout(this._timeout)
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const result = await response.json();

        if (!result.success) {
            throw new Error(result.error || 'Failed to query table');
        }

        return {
            rows: result.rows || [],
            columns: result.columns || [],
            totalCount: result.totalCount || 0
        };
    }

    /**
     * Get data source type
     * 
     * @returns {string} Data source type
     */
    getType() {
        return this._source;
    }
}

// Export for browser global
if (typeof window !== 'undefined') {
    window.DataProductsV2Adapter = DataProductsV2Adapter;
}

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DataProductsV2Adapter;
}