/**
 * ICache Interface
 * 
 * Purpose: Contract for caching services (performance optimization)
 * Pattern: Interface Segregation Principle (focused contract)
 * 
 * Implementations:
 * - LocalStorageCache: Browser localStorage (fallback, always available)
 * - SessionStorageCache: Browser sessionStorage (temporary)
 * - RedisCache: Redis backend (future, high-performance)
 * - InMemoryCache: JavaScript Map (fast, not persistent)
 * 
 * Usage:
 *   const cache = DependencyContainer.get('ICache');
 *   await cache.set('graph_data', graphData, 300);  // TTL 5 minutes
 *   const data = await cache.get('graph_data');
 * 
 * Architecture: Core interface for optional caching capabilities
 */
class ICache {
    /**
     * Get a value from cache
     * 
     * @param {string} key - Cache key
     * @returns {Promise<*>} Cached value or null if not found/expired
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * const data = await cache.get('graph_schema');
     * if (data) {
     *     console.log('Cache hit!');
     * } else {
     *     console.log('Cache miss, fetching...');
     * }
     */
    async get(key) {
        throw new Error('ICache.get() must be implemented by subclass');
    }
    
    /**
     * Set a value in cache with optional TTL
     * 
     * @param {string} key - Cache key
     * @param {*} value - Value to cache (will be JSON serialized)
     * @param {number} ttlSeconds - Time-to-live in seconds (optional, null = no expiry)
     * @returns {Promise<void>}
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * // Cache for 5 minutes
     * await cache.set('graph_data', graphData, 300);
     * 
     * // Cache indefinitely
     * await cache.set('user_preferences', prefs);
     */
    async set(key, value, ttlSeconds = null) {
        throw new Error('ICache.set() must be implemented by subclass');
    }
    
    /**
     * Delete a value from cache
     * 
     * @param {string} key - Cache key
     * @returns {Promise<boolean>} True if key existed and was deleted
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * await cache.delete('graph_data');
     */
    async delete(key) {
        throw new Error('ICache.delete() must be implemented by subclass');
    }
    
    /**
     * Check if a key exists in cache (and not expired)
     * 
     * @param {string} key - Cache key
     * @returns {Promise<boolean>} True if key exists and not expired
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * if (await cache.has('graph_data')) {
     *     const data = await cache.get('graph_data');
     * }
     */
    async has(key) {
        throw new Error('ICache.has() must be implemented by subclass');
    }
    
    /**
     * Clear all cache entries
     * 
     * @returns {Promise<void>}
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * await cache.clear();  // Useful for "Clear Cache" button
     */
    async clear() {
        throw new Error('ICache.clear() must be implemented by subclass');
    }
    
    /**
     * Get all cache keys
     * 
     * @returns {Promise<Array<string>>} Array of cache keys
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * const keys = await cache.getKeys();
     * console.log('Cached items:', keys.join(', '));
     */
    async getKeys() {
        throw new Error('ICache.getKeys() must be implemented by subclass');
    }
    
    /**
     * Get cache statistics (for debugging)
     * 
     * @returns {Promise<Object>} Cache stats (hits, misses, size, etc.)
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * const stats = await cache.getStats();
     * // { hits: 42, misses: 8, hitRate: 0.84, sizeKB: 125 }
     */
    async getStats() {
        throw new Error('ICache.getStats() must be implemented by subclass');
    }
}

// Export for module systems (ES6)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ICache;
}

// Export for browser global
if (typeof window !== 'undefined') {
    window.ICache = ICache;
}