/**
 * IDataSource Interface
 * 
 * Purpose: Contract for data source services (Repository Pattern abstraction)
 * Pattern: Interface Segregation Principle (focused contract)
 * 
 * Implementations:
 * - DataProductsAdapter: Real data products API (if data_products module enabled)
 * - MockDataSource: Mock data for testing/offline (fallback)
 * - HanaDataSource: Direct HANA Cloud queries (future)
 * 
 * Usage:
 *   const dataSource = DependencyContainer.get('IDataSource');
 *   const tables = await dataSource.getTables();
 *   const data = await dataSource.query('SELECT * FROM Supplier');
 * 
 * Architecture: Core interface for optional data_products module dependency
 */
class IDataSource {
    /**
     * Execute a SQL query
     * 
     * @param {string} sql - SQL query string
     * @param {Array} params - Query parameters (for parameterized queries)
     * @returns {Promise<Array>} Query results
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * const results = await dataSource.query(
     *     'SELECT * FROM Supplier WHERE Country = ?',
     *     ['Germany']
     * );
     */
    async query(sql, params = []) {
        throw new Error('IDataSource.query() must be implemented by subclass');
    }
    
    /**
     * Get list of available tables
     * 
     * @returns {Promise<Array<string>>} Array of table names
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * const tables = await dataSource.getTables();
     * console.log('Available tables:', tables.join(', '));
     */
    async getTables() {
        throw new Error('IDataSource.getTables() must be implemented by subclass');
    }
    
    /**
     * Get schema for a table
     * 
     * @param {string} tableName - Table name
     * @returns {Promise<Object>} Table schema with columns and types
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * const schema = await dataSource.getTableSchema('Supplier');
     * // { columns: ['ID', 'Name', 'Country'], types: ['TEXT', 'TEXT', 'TEXT'] }
     */
    async getTableSchema(tableName) {
        throw new Error('IDataSource.getTableSchema() must be implemented by subclass');
    }
    
    /**
     * Get data source type (sqlite, hana, etc.)
     * 
     * @returns {string} Data source type identifier
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * const type = dataSource.getType();  // 'sqlite' or 'hana'
     */
    getType() {
        throw new Error('IDataSource.getType() must be implemented by subclass');
    }
    
    /**
     * Test connection (health check)
     * 
     * @returns {Promise<boolean>} True if connection healthy
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * const isHealthy = await dataSource.testConnection();
     * if (!isHealthy) {
     *     console.error('Data source unavailable');
     * }
     */
    async testConnection() {
        throw new Error('IDataSource.testConnection() must be implemented by subclass');
    }
}

// Export for module systems (ES6)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = IDataSource;
}

// Export for browser global
if (typeof window !== 'undefined') {
    window.IDataSource = IDataSource;
}