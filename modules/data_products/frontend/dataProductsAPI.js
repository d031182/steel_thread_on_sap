/**
 * Data Products API Client
 * 
 * Provides methods to interact with HANA Cloud data products through the backend API.
 * Handles listing data products, exploring tables, and querying data.
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */

export class DataProductsAPI {
    /**
     * Create a new DataProductsAPI instance
     * @param {string} baseURL - Base URL of the backend API
     */
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
        this.cache = new Map();
        this.cacheTTL = 60000; // 1 minute cache
    }

    /**
     * Check if cached data is still valid
     * @private
     */
    _isCacheValid(cacheKey) {
        const cached = this.cache.get(cacheKey);
        if (!cached) return false;
        
        const age = Date.now() - cached.timestamp;
        return age < this.cacheTTL;
    }

    /**
     * Get cached data if valid
     * @private
     */
    _getCached(cacheKey) {
        if (this._isCacheValid(cacheKey)) {
            console.log(`📦 Cache hit: ${cacheKey}`);
            return this.cache.get(cacheKey).data;
        }
        return null;
    }

    /**
     * Set cache data
     * @private
     */
    _setCache(cacheKey, data) {
        this.cache.set(cacheKey, {
            data,
            timestamp: Date.now()
        });
    }

    /**
     * Make HTTP request with error handling
     * @private
     */
    async _request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        
        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error?.message || `HTTP ${response.status}`);
            }
            
            return data;
            
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw {
                code: 'API_ERROR',
                message: error.message,
                endpoint
            };
        }
    }

    /**
     * List all installed data product schemas
     * @returns {Promise<Object>} Data products list
     */
    async listDataProducts() {
        const cacheKey = 'data-products-list';
        const cached = this._getCached(cacheKey);
        if (cached) return cached;
        
        console.log('🔍 Fetching data products list from HANA...');
        
        const result = await this._request('/api/data-products');
        
        if (result.success) {
            this._setCache(cacheKey, result);
            console.log(`✓ Found ${result.count} data products`);
        }
        
        return result;
    }

    /**
     * Get tables in a data product schema
     * @param {string} schemaName - Full schema name
     * @returns {Promise<Object>} Tables list
     */
    async getTables(schemaName) {
        if (!schemaName) {
            throw new Error('Schema name is required');
        }
        
        const cacheKey = `tables-${schemaName}`;
        const cached = this._getCached(cacheKey);
        if (cached) return cached;
        
        console.log(`🔍 Fetching tables for ${schemaName}...`);
        
        const result = await this._request(`/api/data-products/${encodeURIComponent(schemaName)}/tables`);
        
        if (result.success) {
            this._setCache(cacheKey, result);
            console.log(`✓ Found ${result.count} tables`);
        }
        
        return result;
    }

    /**
     * Get table structure (column definitions)
     * @param {string} schemaName - Full schema name
     * @param {string} tableName - Table name
     * @returns {Promise<Object>} Table structure
     */
    async getTableStructure(schemaName, tableName) {
        if (!schemaName || !tableName) {
            throw new Error('Schema name and table name are required');
        }
        
        const cacheKey = `structure-${schemaName}-${tableName}`;
        const cached = this._getCached(cacheKey);
        if (cached) return cached;
        
        console.log(`🔍 Fetching structure for ${schemaName}.${tableName}...`);
        
        const result = await this._request(
            `/api/data-products/${encodeURIComponent(schemaName)}/${encodeURIComponent(tableName)}/structure`
        );
        
        if (result.success) {
            this._setCache(cacheKey, result);
            console.log(`✓ Found ${result.columnCount} columns`);
        }
        
        return result;
    }

    /**
     * Query table data
     * @param {string} schemaName - Full schema name
     * @param {string} tableName - Table name
     * @param {Object} options - Query options
     * @param {number} options.limit - Maximum rows to return (default: 100)
     * @param {number} options.offset - Number of rows to skip (default: 0)
     * @param {string[]} options.columns - Columns to select (default: all)
     * @param {string} options.where - WHERE clause conditions (optional)
     * @param {string} options.orderBy - ORDER BY clause (optional)
     * @returns {Promise<Object>} Query results
     */
    async queryTable(schemaName, tableName, options = {}) {
        if (!schemaName || !tableName) {
            throw new Error('Schema name and table name are required');
        }
        
        const {
            limit = 100,
            offset = 0,
            columns = ['*'],
            where = '',
            orderBy = ''
        } = options;
        
        console.log(`🔍 Querying ${schemaName}.${tableName}...`);
        console.log(`   Limit: ${limit}, Offset: ${offset}`);
        
        const result = await this._request(
            `/api/data-products/${encodeURIComponent(schemaName)}/${encodeURIComponent(tableName)}/query`,
            {
                method: 'POST',
                body: JSON.stringify({
                    limit,
                    offset,
                    columns,
                    where,
                    orderBy
                })
            }
        );
        
        if (result.success) {
            console.log(`✓ Retrieved ${result.rowCount} rows (${result.executionTime}ms)`);
        }
        
        return result;
    }

    /**
     * Get data product metadata from schema name
     * Parses schema name to extract product information
     * @param {string} schemaName - Full schema name
     * @returns {Object} Metadata object
     */
    getDataProductMetadata(schemaName) {
        // Parse: _SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3
        const parts = schemaName.split('_');
        
        let productName = 'Unknown';
        let version = 'v1';
        let namespace = 'sap.s4com';
        let uuid = '';
        
        // Extract namespace
        if (parts.length > 3) {
            namespace = parts[3].replace(/-/g, '.');
        }
        
        // Extract product name and version
        const dataProductIndex = parts.indexOf('dataProduct');
        if (dataProductIndex !== -1) {
            for (let i = dataProductIndex + 1; i < parts.length; i++) {
                if (parts[i].startsWith('v') && /^v\d+$/.test(parts[i])) {
                    version = parts[i];
                } else if (i === dataProductIndex + 1) {
                    productName = parts[i];
                } else if (parts[i].includes('-')) {
                    // UUID found
                    uuid = parts[i];
                }
            }
        }
        
        return {
            schemaName,
            productName,
            displayName: this._formatProductName(productName),
            version,
            namespace,
            uuid,
            fullName: `${namespace}:${productName}:${version}`
        };
    }

    /**
     * Format product name for display
     * Converts "PurchaseOrder" to "Purchase Order"
     * @private
     */
    _formatProductName(name) {
        // Insert spaces before capital letters
        return name.replace(/([A-Z])/g, ' $1').trim();
    }

    /**
     * Clear all cached data
     */
    clearCache() {
        this.cache.clear();
        console.log('🗑️ Cache cleared');
    }

    /**
     * Get cache statistics
     * @returns {Object} Cache stats
     */
    getCacheStats() {
        return {
            size: this.cache.size,
            keys: Array.from(this.cache.keys()),
            ttl: this.cacheTTL
        };
    }

    /**
     * Test backend connection
     * @returns {Promise<boolean>} Connection status
     */
    async testConnection() {
        try {
            const result = await this._request('/api/health');
            return result.status === 'healthy';
        } catch (error) {
            console.error('Connection test failed:', error);
            return false;
        }
    }

    /**
     * Parse CSN and extract entity information
     * 
     * Extracts all entities from a CSN definition and returns structured information
     * about each entity including field count.
     * 
     * @param {Object} csn - CSN definition object with 'definitions' property
     * @returns {Array<Object>} Array of entity information objects
     * @example
     * const entities = api.parseCSNEntities(csnData);
     * // Returns: [
     * //   { name: 'supplier.Supplier', elements: {...}, fieldCount: 120 },
     * //   { name: 'supplier.SupplierCompanyCode', elements: {...}, fieldCount: 25 }
     * // ]
     */
    parseCSNEntities(csn) {
        if (!csn || !csn.definitions || typeof csn.definitions !== 'object') {
            console.warn('Invalid CSN structure - missing definitions');
            return [];
        }

        const entities = [];
        
        for (const [entityName, entityDef] of Object.entries(csn.definitions)) {
            // Only include definitions that have elements (actual entities, not types)
            if (entityDef && entityDef.elements && typeof entityDef.elements === 'object') {
                const fieldCount = Object.keys(entityDef.elements).length;
                
                entities.push({
                    name: entityName,
                    elements: entityDef.elements,
                    fieldCount: fieldCount,
                    kind: entityDef.kind || 'entity'
                });
                
                console.log(`  Entity: ${entityName} (${fieldCount} fields)`);
            }
        }

        console.log(`📦 Parsed ${entities.length} entities from CSN`);
        return entities;
    }

    /**
     * Format CSN field for display
     * 
     * Extracts and formats field metadata for UI display, including type information,
     * constraints, and annotations.
     * 
     * @param {string} fieldName - Field name
     * @param {Object} fieldDef - Field definition from CSN
     * @returns {Object} Formatted field information
     * @example
     * const field = api.formatCSNField('Supplier', fieldDefinition);
     * // Returns: {
     * //   name: 'Supplier',
     * //   type: 'cds.String',
     * //   length: 10,
     * //   key: true,
     * //   nullable: false,
     * //   description: 'Account Number of Supplier',
     * //   annotations: { '@EndUserText.quickInfo': '...' }
     * // }
     */
    formatCSNField(fieldName, fieldDef) {
        if (!fieldDef || typeof fieldDef !== 'object') {
            return {
                name: fieldName,
                type: 'unknown',
                length: null,
                key: false,
                nullable: true,
                description: '',
                annotations: {}
            };
        }

        // Extract type information
        const type = fieldDef.type || 'unknown';
        const length = fieldDef.length || null;
        const scale = fieldDef.scale || null;
        const precision = fieldDef.precision || null;

        // Extract constraints
        const key = fieldDef.key === true;
        const nullable = fieldDef.notNull !== true; // notNull=true means NOT nullable

        // Extract description from annotations
        const description = fieldDef['@EndUserText.quickInfo'] || 
                          fieldDef['@EndUserText.label'] || 
                          fieldDef['@title'] ||
                          '';

        // Extract all annotations
        const annotations = this._extractAnnotations(fieldDef);

        return {
            name: fieldName,
            type: type,
            length: length,
            scale: scale,
            precision: precision,
            key: key,
            nullable: nullable,
            description: description,
            annotations: annotations
        };
    }

    /**
     * Extract all annotations from field definition
     * 
     * @private
     * @param {Object} fieldDef - Field definition object
     * @returns {Object} Object containing all annotations (keys starting with @)
     */
    _extractAnnotations(fieldDef) {
        const annotations = {};
        
        for (const [key, value] of Object.entries(fieldDef)) {
            if (key.startsWith('@')) {
                annotations[key] = value;
            }
        }
        
        return annotations;
    }

    /**
     * Get CSN (Core Schema Notation) definition for a data product
     * 
     * Retrieves the authoritative CSN schema definition from the backend,
     * which loads it from local files or BDC MCP server.
     * 
     * @param {string} schemaName - Data product schema name (e.g., 'sap_s4com_Supplier_v1')
     * @returns {Promise<Object>} Result object with CSN data or error
     * @example
     * const result = await api.getCSNDefinition('sap_s4com_Supplier_v1');
     * if (result.success) {
     *   console.log('CSN:', result.csn);
     *   console.log('Source:', result.source); // 'local_file' or 'bdc_mcp'
     *   console.log('ORD ID:', result.ordId);
     * }
     */
    async getCSNDefinition(schemaName) {
        if (!schemaName) {
            throw {
                code: 'MISSING_PARAMETER',
                message: 'Schema name is required'
            };
        }

        // Normalize schema name (remove _SAP_DATAPRODUCT prefix if present)
        let normalizedName = schemaName;
        if (schemaName.startsWith('_SAP_DATAPRODUCT_')) {
            // Extract: _SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_uuid
            // To: sap_s4com_Supplier_v1
            const parts = schemaName.split('_');
            const dpIndex = parts.indexOf('dataProduct');
            if (dpIndex !== -1 && dpIndex + 1 < parts.length) {
                const vendor = parts[3] || 'sap';
                const product = parts[4] || 's4com';
                const productName = parts[dpIndex + 1];
                // Find version
                let version = 'v1';
                for (let i = dpIndex + 2; i < parts.length; i++) {
                    if (parts[i].startsWith('v') && parts[i][1] && /^\d/.test(parts[i][1])) {
                        version = parts[i];
                        break;
                    }
                }
                normalizedName = `${vendor}_${product}_${productName}_${version}`;
            }
        }

        console.log(`🔍 Fetching CSN definition for ${normalizedName}...`);

        try {
            const result = await this._request(
                `/api/data-products/${encodeURIComponent(normalizedName)}/csn`
            );

            if (result.success) {
                console.log(`✓ CSN retrieved successfully`);
                console.log(`  Source: ${result.source}`);
                console.log(`  ORD ID: ${result.ordId}`);
                if (result.csn && result.csn.definitions) {
                    const entityCount = Object.keys(result.csn.definitions).length;
                    console.log(`  Entities: ${entityCount}`);
                }
            }

            return result;

        } catch (error) {
            console.error(`❌ Failed to retrieve CSN for ${normalizedName}:`, error);
            return {
                success: false,
                error: {
                    code: error.code || 'CSN_ERROR',
                    message: error.message || 'Failed to retrieve CSN definition'
                }
            };
        }
    }
}

// Export singleton instance
export const dataProductsAPI = new DataProductsAPI();
