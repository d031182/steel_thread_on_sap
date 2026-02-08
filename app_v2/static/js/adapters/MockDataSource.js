/**
 * MockDataSource (Null Object Pattern)
 * 
 * Purpose: Mock data source fallback when data_products module is disabled
 * Pattern: Null Object Pattern (safe default implementation with sample data)
 * 
 * Behavior:
 * - Implements IDataSource interface completely
 * - Returns mock data (sample schema + empty results)
 * - All methods are safe (no errors thrown)
 * - Useful for offline development and testing
 * 
 * Usage:
 *   DependencyContainer.register('IDataSource', () => new MockDataSource());
 *   const dataSource = DependencyContainer.get('IDataSource');
 *   const tables = await dataSource.getTables();  // ['Supplier', 'PurchaseOrder']
 * 
 * Why This Matters:
 * - Modules can always query data without checking if data_products exists
 * - Code works unchanged whether data_products enabled or disabled
 * - Graceful degradation (returns empty data, not errors)
 * 
 * Architecture: Fallback adapter for IDataSource interface
 */
class MockDataSource extends IDataSource {
    /**
     * Create a MockDataSource with optional sample data
     */
    constructor() {
        super();
        
        // Mock schema for common P2P tables
        this._mockSchema = {
            'Supplier': {
                columns: ['ID', 'Name', 'Country', 'Rating'],
                types: ['TEXT', 'TEXT', 'TEXT', 'INTEGER']
            },
            'PurchaseOrder': {
                columns: ['PONumber', 'SupplierID', 'OrderDate', 'TotalAmount'],
                types: ['TEXT', 'TEXT', 'TEXT', 'REAL']
            },
            'Invoice': {
                columns: ['InvoiceNumber', 'PONumber', 'InvoiceDate', 'Amount'],
                types: ['TEXT', 'TEXT', 'TEXT', 'REAL']
            }
        };
    }
    
    /**
     * Execute a SQL query (returns empty results)
     * 
     * @param {string} sql - SQL query string
     * @param {Array} params - Query parameters
     * @returns {Promise<Array>} Empty array (mock data)
     * 
     * @example
     * const results = await dataSource.query('SELECT * FROM Supplier');
     * // Returns: []
     */
    async query(sql, params = []) {
        console.debug('[MockDataSource] query() called (data_products module disabled)');
        console.debug('SQL:', sql);
        
        // Return empty results
        return [];
    }
    
    /**
     * Get list of available tables (mock schema)
     * 
     * @returns {Promise<Array<string>>} Array of mock table names
     * 
     * @example
     * const tables = await dataSource.getTables();
     * // Returns: ['Supplier', 'PurchaseOrder', 'Invoice']
     */
    async getTables() {
        return Object.keys(this._mockSchema);
    }
    
    /**
     * Get schema for a table (mock schema)
     * 
     * @param {string} tableName - Table name
     * @returns {Promise<Object>} Mock table schema
     * 
     * @example
     * const schema = await dataSource.getTableSchema('Supplier');
     * // Returns: { columns: ['ID', 'Name', ...], types: ['TEXT', 'TEXT', ...] }
     */
    async getTableSchema(tableName) {
        const schema = this._mockSchema[tableName];
        
        if (!schema) {
            // Return generic schema for unknown tables
            return {
                columns: ['ID', 'Name'],
                types: ['TEXT', 'TEXT']
            };
        }
        
        return schema;
    }
    
    /**
     * Get data source type
     * 
     * @returns {string} 'mock' type identifier
     * 
     * @example
     * const type = dataSource.getType();  // 'mock'
     */
    getType() {
        return 'mock';
    }
    
    /**
     * Test connection (always healthy for mock)
     * 
     * @returns {Promise<boolean>} Always true (mock is always available)
     * 
     * @example
     * const isHealthy = await dataSource.testConnection();  // true
     */
    async testConnection() {
        return true;  // Mock data source is always "healthy"
    }
}

// Export for module systems (ES6)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MockDataSource;
}

// Export for browser global
if (typeof window !== 'undefined') {
    window.MockDataSource = MockDataSource;
}