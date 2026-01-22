/**
 * HANA Connection API
 * 
 * Provides programmatic access to HANA instance management.
 * This API is UI-independent and fully testable.
 * 
 * @module api/hanaConnectionAPI
 */

import { StorageService } from '../services/storageService.js';

const STORAGE_KEY = 'hanaInstances';

export class HanaConnectionAPI {
    /**
     * Create HANA Connection API
     * @param {StorageService} [storageService] - Storage service instance
     */
    constructor(storageService = new StorageService()) {
        this.storage = storageService;
        this._instances = null;
    }

    /**
     * Generate unique ID for instance
     * @private
     * @returns {string} Unique instance ID
     */
    _generateId() {
        return `instance-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Load instances from storage
     * @private
     */
    _loadInstances() {
        if (this._instances === null) {
            this._instances = this.storage.load(STORAGE_KEY, []);
        }
        return this._instances;
    }

    /**
     * Save instances to storage
     * @private
     */
    _saveInstances() {
        return this.storage.save(STORAGE_KEY, this._instances);
    }

    /**
     * Get all HANA instances
     * @returns {Promise<Array>} Array of instance configurations
     */
    async getInstances() {
        return Promise.resolve(this._loadInstances());
    }

    /**
     * Get a specific instance by ID
     * @param {string} id - Instance ID
     * @returns {Promise<Object|null>} Instance configuration or null if not found
     */
    async getInstance(id) {
        const instances = this._loadInstances();
        const instance = instances.find(i => i.id === id);
        return Promise.resolve(instance || null);
    }

    /**
     * Create a new HANA instance configuration
     * @param {Object} config - Instance configuration
     * @param {string} config.name - Instance name
     * @param {string} config.host - HANA host
     * @param {string} [config.port='443'] - HANA port
     * @param {string} config.user - Database user
     * @param {string} [config.password] - Database password (optional)
     * @param {string} [config.schema] - Default schema
     * @param {string} [config.description] - Instance description
     * @param {boolean} [config.ssl=true] - Use SSL connection
     * @returns {Promise<Object>} Created instance with generated ID
     * @throws {Error} If required fields are missing
     */
    async createInstance(config) {
        // Validation
        if (!config.name || !config.host || !config.user) {
            throw new Error('Missing required fields: name, host, user');
        }

        const instances = this._loadInstances();
        
        const newInstance = {
            id: this._generateId(),
            name: config.name,
            host: config.host,
            port: config.port || '443',
            user: config.user,
            password: config.password || '',
            schema: config.schema || '',
            description: config.description || '',
            ssl: config.ssl !== false,
            isDefault: instances.length === 0, // First instance is default
            createdAt: new Date().toISOString(),
            status: 'unknown'
        };

        instances.push(newInstance);
        this._saveInstances();

        return Promise.resolve(newInstance);
    }

    /**
     * Update an existing instance
     * @param {string} id - Instance ID
     * @param {Object} updates - Fields to update
     * @returns {Promise<Object|null>} Updated instance or null if not found
     */
    async updateInstance(id, updates) {
        const instances = this._loadInstances();
        const index = instances.findIndex(i => i.id === id);
        
        if (index === -1) {
            return Promise.resolve(null);
        }

        // Merge updates (excluding id and isDefault)
        const { id: _, isDefault: __, ...allowedUpdates } = updates;
        instances[index] = {
            ...instances[index],
            ...allowedUpdates,
            updatedAt: new Date().toISOString()
        };

        this._saveInstances();
        return Promise.resolve(instances[index]);
    }

    /**
     * Delete an instance
     * @param {string} id - Instance ID
     * @returns {Promise<boolean>} True if deleted, false if not found
     */
    async deleteInstance(id) {
        const instances = this._loadInstances();
        const index = instances.findIndex(i => i.id === id);
        
        if (index === -1) {
            return Promise.resolve(false);
        }

        // Cannot delete default instance if there are others
        if (instances[index].isDefault && instances.length > 1) {
            throw new Error('Cannot delete default instance. Set another instance as default first.');
        }

        instances.splice(index, 1);
        this._saveInstances();
        return Promise.resolve(true);
    }

    /**
     * Set an instance as default
     * @param {string} id - Instance ID
     * @returns {Promise<boolean>} True if successful
     */
    async setDefaultInstance(id) {
        const instances = this._loadInstances();
        const instance = instances.find(i => i.id === id);
        
        if (!instance) {
            return Promise.resolve(false);
        }

        // Remove default from all instances
        instances.forEach(i => i.isDefault = false);
        // Set new default
        instance.isDefault = true;

        this._saveInstances();
        return Promise.resolve(true);
    }

    /**
     * Get the default instance
     * @returns {Promise<Object|null>} Default instance or null if none
     */
    async getDefaultInstance() {
        const instances = this._loadInstances();
        const defaultInstance = instances.find(i => i.isDefault);
        return Promise.resolve(defaultInstance || (instances.length > 0 ? instances[0] : null));
    }

    /**
     * Test connection to an instance (simulated)
     * In a real implementation, this would attempt a database connection
     * @param {string} id - Instance ID
     * @returns {Promise<Object>} Connection test result
     */
    async testConnection(id) {
        const instance = await this.getInstance(id);
        
        if (!instance) {
            return Promise.resolve({
                success: false,
                error: 'Instance not found'
            });
        }

        // Simulate connection test
        // In a real implementation, this would use a backend API
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    success: true,
                    message: `Connection test successful for ${instance.name}`,
                    timestamp: new Date().toISOString()
                });
            }, 1500);
        });
    }

    /**
     * Update instance status
     * @param {string} id - Instance ID
     * @param {string} status - New status (e.g., 'connected', 'error', 'unknown')
     * @returns {Promise<boolean>} True if successful
     */
    async updateStatus(id, status) {
        return this.updateInstance(id, { status });
    }

    /**
     * Get connection string for an instance
     * @param {string} id - Instance ID
     * @returns {Promise<string|null>} Connection string or null
     */
    async getConnectionString(id) {
        const instance = await this.getInstance(id);
        
        if (!instance) {
            return Promise.resolve(null);
        }

        const protocol = instance.ssl ? 'https' : 'http';
        return Promise.resolve(`${protocol}://${instance.host}:${instance.port}`);
    }

    /**
     * Export instances configuration (without passwords)
     * @param {boolean} [includePasswords=false] - Include passwords in export
     * @returns {Promise<string>} JSON string of configurations
     */
    async exportInstances(includePasswords = false) {
        const instances = this._loadInstances();
        
        const exportData = instances.map(instance => {
            const exported = { ...instance };
            if (!includePasswords) {
                delete exported.password;
            }
            return exported;
        });

        return Promise.resolve(JSON.stringify(exportData, null, 2));
    }

    /**
     * Import instances configuration
     * @param {string} jsonData - JSON string of instances
     * @param {boolean} [merge=false] - Merge with existing or replace
     * @returns {Promise<number>} Number of instances imported
     */
    async importInstances(jsonData, merge = false) {
        try {
            const imported = JSON.parse(jsonData);
            
            if (!Array.isArray(imported)) {
                throw new Error('Invalid import data format');
            }

            if (!merge) {
                this._instances = imported;
            } else {
                const instances = this._loadInstances();
                imported.forEach(imp => {
                    // Check if instance exists (by host + user)
                    const exists = instances.find(i => 
                        i.host === imp.host && i.user === imp.user
                    );
                    if (!exists) {
                        instances.push({
                            ...imp,
                            id: this._generateId() // Generate new ID
                        });
                    }
                });
            }

            this._saveInstances();
            return Promise.resolve(imported.length);
        } catch (error) {
            throw new Error(`Import failed: ${error.message}`);
        }
    }

    /**
     * Clear all instances (use with caution)
     * @returns {Promise<boolean>} True if successful
     */
    async clearAllInstances() {
        this._instances = [];
        return Promise.resolve(this._saveInstances());
    }
}

// Default instance (only in browser environment with localStorage)
export const hanaConnectionAPI = typeof localStorage !== 'undefined'
    ? new HanaConnectionAPI()
    : null;
