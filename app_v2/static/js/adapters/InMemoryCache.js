/**
 * InMemoryCache - Fast in-memory cache implementation
 * 
 * Purpose: High-performance caching using JavaScript Map
 * Pattern: Adapter Pattern (implements ICache interface)
 * 
 * Characteristics:
 * - ✅ Fastest: Direct memory access (no serialization)
 * - ✅ Simple: No external dependencies
 * - ❌ Volatile: Lost on page reload
 * - ❌ No sharing: Each tab has separate cache
 * 
 * Use Cases:
 * - Session data (doesn't need persistence)
 * - Temporary results (API responses during single session)
 * - Performance-critical caching (graph layouts, computed values)
 * 
 * NOT for:
 * - User preferences (use LocalStorageCache)
 * - Long-term data (use LocalStorageCache)
 * - Cross-tab data (use LocalStorageCache)
 * 
 * @implements {ICache}
 */
class InMemoryCache {
    constructor() {
        // Storage: Map<key, {value, expiry}>
        this._cache = new Map();
        
        // Statistics tracking
        this._stats = {
            hits: 0,
            misses: 0,
            sets: 0,
            deletes: 0,
            clears: 0
        };
    }
    
    /**
     * Get value from cache
     * 
     * @param {string} key - Cache key
     * @returns {Promise<*>} Value or null if not found/expired
     */
    async get(key) {
        const entry = this._cache.get(key);
        
        if (!entry) {
            this._stats.misses++;
            return null;
        }
        
        // Check expiry
        if (entry.expiry && Date.now() > entry.expiry) {
            this._cache.delete(key);
            this._stats.misses++;
            return null;
        }
        
        this._stats.hits++;
        return entry.value;
    }
    
    /**
     * Set value in cache with optional TTL
     * 
     * @param {string} key - Cache key
     * @param {*} value - Value to cache
     * @param {number} ttlSeconds - Time-to-live in seconds (null = no expiry)
     * @returns {Promise<void>}
     */
    async set(key, value, ttlSeconds = null) {
        const entry = {
            value: value,
            expiry: ttlSeconds ? Date.now() + (ttlSeconds * 1000) : null
        };
        
        this._cache.set(key, entry);
        this._stats.sets++;
    }
    
    /**
     * Delete value from cache
     * 
     * @param {string} key - Cache key
     * @returns {Promise<boolean>} True if key existed
     */
    async delete(key) {
        const existed = this._cache.has(key);
        if (existed) {
            this._cache.delete(key);
            this._stats.deletes++;
        }
        return existed;
    }
    
    /**
     * Check if key exists (and not expired)
     * 
     * @param {string} key - Cache key
     * @returns {Promise<boolean>}
     */
    async has(key) {
        const entry = this._cache.get(key);
        
        if (!entry) {
            return false;
        }
        
        // Check expiry
        if (entry.expiry && Date.now() > entry.expiry) {
            this._cache.delete(key);
            return false;
        }
        
        return true;
    }
    
    /**
     * Clear all cache entries
     * 
     * @returns {Promise<void>}
     */
    async clear() {
        this._cache.clear();
        this._stats.clears++;
        
        // Reset hit/miss counters (but preserve clears count)
        this._stats.hits = 0;
        this._stats.misses = 0;
        this._stats.sets = 0;
        this._stats.deletes = 0;
    }
    
    /**
     * Get all cache keys
     * 
     * @returns {Promise<Array<string>>}
     */
    async getKeys() {
        // Filter out expired keys
        const validKeys = [];
        
        for (const [key, entry] of this._cache.entries()) {
            if (!entry.expiry || Date.now() <= entry.expiry) {
                validKeys.push(key);
            }
        }
        
        return validKeys;
    }
    
    /**
     * Get cache statistics
     * 
     * @returns {Promise<Object>}
     */
    async getStats() {
        const totalRequests = this._stats.hits + this._stats.misses;
        const hitRate = totalRequests > 0 
            ? (this._stats.hits / totalRequests) 
            : 0;
        
        // Calculate approximate memory size
        let sizeBytes = 0;
        for (const entry of this._cache.values()) {
            // Rough estimate: JSON size
            try {
                sizeBytes += JSON.stringify(entry.value).length;
            } catch (e) {
                // Non-serializable value, skip
            }
        }
        
        return {
            hits: this._stats.hits,
            misses: this._stats.misses,
            sets: this._stats.sets,
            deletes: this._stats.deletes,
            clears: this._stats.clears,
            hitRate: hitRate,
            entries: this._cache.size,
            sizeKB: Math.round(sizeBytes / 1024),
            type: 'InMemoryCache'
        };
    }
}

// Export for module systems (ES6)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InMemoryCache;
}

// Export for browser global (App V2 pattern)
if (typeof window !== 'undefined') {
    window.InMemoryCache = InMemoryCache;
}