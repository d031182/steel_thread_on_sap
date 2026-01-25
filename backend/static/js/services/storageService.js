/**
 * Storage Service
 * 
 * Provides an abstraction layer over browser localStorage.
 * This service is testable by injecting a mock storage implementation.
 * 
 * @module services/storageService
 */

export class StorageService {
    /**
     * Create a storage service
     * @param {Storage} [storage] - Storage implementation (default: localStorage in browser, null in Node.js)
     */
    constructor(storage) {
        // Use provided storage or default to localStorage if available (browser)
        this.storage = storage || (typeof localStorage !== 'undefined' ? localStorage : null);
        
        if (!this.storage) {
            throw new Error('Storage implementation required. Pass a storage object to the constructor.');
        }
    }

    /**
     * Save data to storage
     * @param {string} key - Storage key
     * @param {*} data - Data to store (will be JSON stringified)
     * @returns {boolean} Success status
     */
    save(key, data) {
        try {
            const serialized = JSON.stringify(data);
            this.storage.setItem(key, serialized);
            return true;
        } catch (error) {
            console.error(`Error saving to storage (${key}):`, error);
            return false;
        }
    }

    /**
     * Load data from storage
     * @param {string} key - Storage key
     * @param {*} [defaultValue=null] - Default value if key doesn't exist
     * @returns {*} Parsed data or default value
     */
    load(key, defaultValue = null) {
        try {
            const serialized = this.storage.getItem(key);
            if (serialized === null) {
                return defaultValue;
            }
            return JSON.parse(serialized);
        } catch (error) {
            console.error(`Error loading from storage (${key}):`, error);
            return defaultValue;
        }
    }

    /**
     * Remove data from storage
     * @param {string} key - Storage key
     * @returns {boolean} Success status
     */
    remove(key) {
        try {
            this.storage.removeItem(key);
            return true;
        } catch (error) {
            console.error(`Error removing from storage (${key}):`, error);
            return false;
        }
    }

    /**
     * Clear all data from storage
     * @returns {boolean} Success status
     */
    clear() {
        try {
            this.storage.clear();
            return true;
        } catch (error) {
            console.error('Error clearing storage:', error);
            return false;
        }
    }

    /**
     * Check if a key exists in storage
     * @param {string} key - Storage key
     * @returns {boolean} True if key exists
     */
    has(key) {
        return this.storage.getItem(key) !== null;
    }

    /**
     * Get all keys in storage
     * @returns {string[]} Array of storage keys
     */
    keys() {
        const keys = [];
        for (let i = 0; i < this.storage.length; i++) {
            keys.push(this.storage.key(i));
        }
        return keys;
    }
}

// Default instance using browser localStorage (only in browser environment)
export const storageService = typeof localStorage !== 'undefined' 
    ? new StorageService(localStorage) 
    : null;
