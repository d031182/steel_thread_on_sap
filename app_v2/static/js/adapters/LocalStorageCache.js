/**
 * LocalStorageCache - Browser-persistent cache implementation
 * 
 * Purpose: Persistent caching using browser localStorage API
 * Pattern: Adapter Pattern (implements ICache interface)
 * 
 * Characteristics:
 * - ✅ Persistent: Survives page reloads
 * - ✅ Cross-tab: Shared across all tabs/windows
 * - ✅ Simple: Built-in browser API
 * - ❌ Size limit: ~5-10MB per domain
 * - ❌ Slower: Serialization overhead (JSON.stringify/parse)
 * 
 * Use Cases:
 * - User preferences (theme, language)
 * - Long-term data (frequently accessed, rarely changes)
 * - Cross-session data (authentication tokens, user settings)
 * 
 * NOT for:
 * - Large datasets (>1MB) - use InMemoryCache
 * - Frequently changing data - use InMemoryCache
 * - Sensitive data - use secure backend storage
 * 
 * @implements {ICache}
 */
class LocalStorageCache {
    constructor(prefix = 'app_v2_cache_') {
        // Namespace prefix to avoid collisions
        this._prefix = prefix;
        
        // Check if localStorage is available
        this._available = this._checkAvailability();
        
        // Statistics tracking (stored in localStorage)
        this._statsKey = `${this._prefix}__stats__`;
        this._initializeStats();
    }
    
    /**
     * Check if localStorage is available
     * (May be disabled in private browsing mode)
     */
    _checkAvailability() {
        try {
            const testKey = '__localStorage_test__';
            localStorage.setItem(testKey, 'test');
            localStorage.removeItem(testKey);
            return true;
        } catch (e) {
            console.warn('LocalStorage not available:', e.message);
            return false;
        }
    }
    
    /**
     * Initialize or load statistics
     */
    _initializeStats() {
        if (!this._available) return;
        
        try {
            const stored = localStorage.getItem(this._statsKey);
            this._stats = stored ? JSON.parse(stored) : {
                hits: 0,
                misses: 0,
                sets: 0,
                deletes: 0,
                clears: 0
            };
        } catch (e) {
            this._stats = {
                hits: 0,
                misses: 0,
                sets: 0,
                deletes: 0,
                clears: 0
            };
        }
    }
    
    /**
     * Save statistics to localStorage
     */
    _saveStats() {
        if (!this._available) return;
        
        try {
            localStorage.setItem(this._statsKey, JSON.stringify(this._stats));
        } catch (e) {
            // Quota exceeded or other error - silently fail
        }
    }
    
    /**
     * Build full key with prefix
     */
    _buildKey(key) {
        return `${this._prefix}${key}`;
    }
    
    /**
     * Get value from cache
     * 
     * @param {string} key - Cache key
     * @returns {Promise<*>} Value or null if not found/expired
     */
    async get(key) {
        if (!this._available) {
            return null;
        }
        
        try {
            const fullKey = this._buildKey(key);
            const stored = localStorage.getItem(fullKey);
            
            if (!stored) {
                this._stats.misses++;
                this._saveStats();
                return null;
            }
            
            const entry = JSON.parse(stored);
            
            // Check expiry
            if (entry.expiry && Date.now() > entry.expiry) {
                localStorage.removeItem(fullKey);
                this._stats.misses++;
                this._saveStats();
                return null;
            }
            
            this._stats.hits++;
            this._saveStats();
            return entry.value;
            
        } catch (e) {
            console.error('LocalStorageCache.get error:', e);
            this._stats.misses++;
            this._saveStats();
            return null;
        }
    }
    
    /**
     * Set value in cache with optional TTL
     * 
     * @param {string} key - Cache key
     * @param {*} value - Value to cache (will be JSON serialized)
     * @param {number} ttlSeconds - Time-to-live in seconds (null = no expiry)
     * @returns {Promise<void>}
     */
    async set(key, value, ttlSeconds = null) {
        if (!this._available) {
            return;
        }
        
        try {
            const fullKey = this._buildKey(key);
            const entry = {
                value: value,
                expiry: ttlSeconds ? Date.now() + (ttlSeconds * 1000) : null,
                created: Date.now()
            };
            
            localStorage.setItem(fullKey, JSON.stringify(entry));
            this._stats.sets++;
            this._saveStats();
            
        } catch (e) {
            // Quota exceeded or serialization error
            if (e.name === 'QuotaExceededError') {
                console.warn('LocalStorage quota exceeded, clearing old entries...');
                await this._clearOldEntries();
                
                // Try again after clearing
                try {
                    const fullKey = this._buildKey(key);
                    const entry = {
                        value: value,
                        expiry: ttlSeconds ? Date.now() + (ttlSeconds * 1000) : null,
                        created: Date.now()
                    };
                    localStorage.setItem(fullKey, JSON.stringify(entry));
                    this._stats.sets++;
                    this._saveStats();
                } catch (retryError) {
                    console.error('LocalStorageCache.set failed after clearing:', retryError);
                }
            } else {
                console.error('LocalStorageCache.set error:', e);
            }
        }
    }
    
    /**
     * Clear old entries (LRU eviction)
     * Removes 25% of oldest entries when quota exceeded
     */
    async _clearOldEntries() {
        const keys = await this.getKeys();
        if (keys.length === 0) return;
        
        // Get all entries with timestamps
        const entries = [];
        for (const key of keys) {
            try {
                const fullKey = this._buildKey(key);
                const stored = localStorage.getItem(fullKey);
                const entry = JSON.parse(stored);
                entries.push({
                    key: key,
                    created: entry.created || 0
                });
            } catch (e) {
                // Malformed entry, will be removed
            }
        }
        
        // Sort by creation time (oldest first)
        entries.sort((a, b) => a.created - b.created);
        
        // Remove oldest 25%
        const removeCount = Math.ceil(entries.length * 0.25);
        for (let i = 0; i < removeCount; i++) {
            await this.delete(entries[i].key);
        }
    }
    
    /**
     * Delete value from cache
     * 
     * @param {string} key - Cache key
     * @returns {Promise<boolean>} True if key existed
     */
    async delete(key) {
        if (!this._available) {
            return false;
        }
        
        const fullKey = this._buildKey(key);
        const existed = localStorage.getItem(fullKey) !== null;
        
        if (existed) {
            localStorage.removeItem(fullKey);
            this._stats.deletes++;
            this._saveStats();
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
        if (!this._available) {
            return false;
        }
        
        try {
            const fullKey = this._buildKey(key);
            const stored = localStorage.getItem(fullKey);
            
            if (!stored) {
                return false;
            }
            
            const entry = JSON.parse(stored);
            
            // Check expiry
            if (entry.expiry && Date.now() > entry.expiry) {
                localStorage.removeItem(fullKey);
                return false;
            }
            
            return true;
            
        } catch (e) {
            return false;
        }
    }
    
    /**
     * Clear all cache entries (preserves stats)
     * 
     * @returns {Promise<void>}
     */
    async clear() {
        if (!this._available) {
            return;
        }
        
        const keys = await this.getKeys();
        for (const key of keys) {
            const fullKey = this._buildKey(key);
            localStorage.removeItem(fullKey);
        }
        
        this._stats.clears++;
        this._stats.hits = 0;
        this._stats.misses = 0;
        this._stats.sets = 0;
        this._stats.deletes = 0;
        this._saveStats();
    }
    
    /**
     * Get all cache keys
     * 
     * @returns {Promise<Array<string>>}
     */
    async getKeys() {
        if (!this._available) {
            return [];
        }
        
        const keys = [];
        const prefixLen = this._prefix.length;
        
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            
            // Skip stats key and non-prefixed keys
            if (key === this._statsKey) continue;
            if (!key.startsWith(this._prefix)) continue;
            
            // Remove prefix
            const cleanKey = key.substring(prefixLen);
            
            // Check if expired
            try {
                const stored = localStorage.getItem(key);
                const entry = JSON.parse(stored);
                
                if (!entry.expiry || Date.now() <= entry.expiry) {
                    keys.push(cleanKey);
                } else {
                    // Remove expired entry
                    localStorage.removeItem(key);
                }
            } catch (e) {
                // Malformed entry, skip
            }
        }
        
        return keys;
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
        
        // Calculate actual localStorage usage
        let sizeBytes = 0;
        const keys = await this.getKeys();
        
        for (const key of keys) {
            try {
                const fullKey = this._buildKey(key);
                const stored = localStorage.getItem(fullKey);
                sizeBytes += stored.length * 2; // UTF-16 = 2 bytes per char
            } catch (e) {
                // Skip
            }
        }
        
        return {
            hits: this._stats.hits,
            misses: this._stats.misses,
            sets: this._stats.sets,
            deletes: this._stats.deletes,
            clears: this._stats.clears,
            hitRate: hitRate,
            entries: keys.length,
            sizeKB: Math.round(sizeBytes / 1024),
            type: 'LocalStorageCache',
            available: this._available
        };
    }
}

// Export for module systems (ES6)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = LocalStorageCache;
}

// Export for browser global (App V2 pattern)
if (typeof window !== 'undefined') {
    window.LocalStorageCache = LocalStorageCache;
}