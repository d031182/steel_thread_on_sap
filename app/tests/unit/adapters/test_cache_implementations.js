/**
 * Unit Tests: Cache Implementations (InMemoryCache + LocalStorageCache)
 * 
 * Test Framework: Gu Wu (顾武) Frontend Testing
 * Pattern: AAA (Arrange-Act-Assert)
 * Coverage Target: 100% (all 7 ICache methods)
 */

// Mock localStorage for testing (since Node.js doesn't have it)
class MockLocalStorage {
    constructor() {
        this._store = {};
    }
    
    getItem(key) {
        return this._store[key] || null;
    }
    
    setItem(key, value) {
        this._store[key] = String(value);
    }
    
    removeItem(key) {
        delete this._store[key];
    }
    
    clear() {
        this._store = {};
    }
    
    get length() {
        return Object.keys(this._store).length;
    }
    
    key(index) {
        const keys = Object.keys(this._store);
        return keys[index] || null;
    }
}

// Setup global localStorage mock
global.localStorage = new MockLocalStorage();

// Import implementations
const InMemoryCache = require('../../../static/js/adapters/InMemoryCache.js');
const LocalStorageCache = require('../../../static/js/adapters/LocalStorageCache.js');

/**
 * Shared test suite for both cache implementations
 * (DRY principle - test same behavior across implementations)
 */
function runCacheTests(CacheClass, cacheName) {
    describe(`${cacheName} - ICache Implementation`, () => {
        let cache;
        
        beforeEach(() => {
            cache = new CacheClass();
            
            // Clear localStorage between tests
            if (cacheName === 'LocalStorageCache') {
                global.localStorage.clear();
            }
        });
        
        afterEach(async () => {
            await cache.clear();
        });
        
        // ===== Test 1: get() method =====
        describe('get()', () => {
            test('returns null for non-existent key', async () => {
                // ARRANGE (cache is empty)
                
                // ACT
                const result = await cache.get('nonexistent');
                
                // ASSERT
                expect(result).toBeNull();
            });
            
            test('returns value for existing key', async () => {
                // ARRANGE
                await cache.set('test_key', 'test_value');
                
                // ACT
                const result = await cache.get('test_key');
                
                // ASSERT
                expect(result).toBe('test_value');
            });
            
            test('returns null for expired key', async () => {
                // ARRANGE
                await cache.set('expired_key', 'value', 0.1); // 100ms TTL
                await new Promise(resolve => setTimeout(resolve, 150)); // Wait 150ms
                
                // ACT
                const result = await cache.get('expired_key');
                
                // ASSERT
                expect(result).toBeNull();
            });
            
            test('handles complex objects', async () => {
                // ARRANGE
                const complexObj = {
                    id: 123,
                    name: 'Test',
                    nested: { a: 1, b: [1, 2, 3] }
                };
                await cache.set('complex', complexObj);
                
                // ACT
                const result = await cache.get('complex');
                
                // ASSERT
                expect(result).toEqual(complexObj);
            });
        });
        
        // ===== Test 2: set() method =====
        describe('set()', () => {
            test('stores value without TTL', async () => {
                // ACT
                await cache.set('persistent', 'value');
                
                // ASSERT
                const result = await cache.get('persistent');
                expect(result).toBe('value');
            });
            
            test('stores value with TTL', async () => {
                // ACT
                await cache.set('temporary', 'value', 60); // 60 seconds
                
                // ASSERT (should exist immediately)
                const result = await cache.get('temporary');
                expect(result).toBe('value');
            });
            
            test('overwrites existing key', async () => {
                // ARRANGE
                await cache.set('key', 'old_value');
                
                // ACT
                await cache.set('key', 'new_value');
                
                // ASSERT
                const result = await cache.get('key');
                expect(result).toBe('new_value');
            });
        });
        
        // ===== Test 3: delete() method =====
        describe('delete()', () => {
            test('returns true for existing key', async () => {
                // ARRANGE
                await cache.set('to_delete', 'value');
                
                // ACT
                const result = await cache.delete('to_delete');
                
                // ASSERT
                expect(result).toBe(true);
                expect(await cache.get('to_delete')).toBeNull();
            });
            
            test('returns false for non-existent key', async () => {
                // ACT
                const result = await cache.delete('nonexistent');
                
                // ASSERT
                expect(result).toBe(false);
            });
        });
        
        // ===== Test 4: has() method =====
        describe('has()', () => {
            test('returns true for existing key', async () => {
                // ARRANGE
                await cache.set('exists', 'value');
                
                // ACT
                const result = await cache.has('exists');
                
                // ASSERT
                expect(result).toBe(true);
            });
            
            test('returns false for non-existent key', async () => {
                // ACT
                const result = await cache.has('nonexistent');
                
                // ASSERT
                expect(result).toBe(false);
            });
            
            test('returns false for expired key', async () => {
                // ARRANGE
                await cache.set('expired', 'value', 0.1); // 100ms TTL
                await new Promise(resolve => setTimeout(resolve, 150)); // Wait 150ms
                
                // ACT
                const result = await cache.has('expired');
                
                // ASSERT
                expect(result).toBe(false);
            });
        });
        
        // ===== Test 5: clear() method =====
        describe('clear()', () => {
            test('removes all entries', async () => {
                // ARRANGE
                await cache.set('key1', 'value1');
                await cache.set('key2', 'value2');
                await cache.set('key3', 'value3');
                
                // ACT
                await cache.clear();
                
                // ASSERT
                expect(await cache.has('key1')).toBe(false);
                expect(await cache.has('key2')).toBe(false);
                expect(await cache.has('key3')).toBe(false);
                
                const keys = await cache.getKeys();
                expect(keys.length).toBe(0);
            });
        });
        
        // ===== Test 6: getKeys() method =====
        describe('getKeys()', () => {
            test('returns empty array when cache is empty', async () => {
                // ACT
                const keys = await cache.getKeys();
                
                // ASSERT
                expect(keys).toEqual([]);
            });
            
            test('returns all valid keys', async () => {
                // ARRANGE
                await cache.set('key1', 'value1');
                await cache.set('key2', 'value2');
                await cache.set('key3', 'value3');
                
                // ACT
                const keys = await cache.getKeys();
                
                // ASSERT
                expect(keys.sort()).toEqual(['key1', 'key2', 'key3'].sort());
            });
            
            test('excludes expired keys', async () => {
                // ARRANGE
                await cache.set('valid', 'value', 60); // 60s TTL
                await cache.set('expired', 'value', 0.1); // 100ms TTL
                await new Promise(resolve => setTimeout(resolve, 150)); // Wait 150ms
                
                // ACT
                const keys = await cache.getKeys();
                
                // ASSERT
                expect(keys).toEqual(['valid']);
            });
        });
        
        // ===== Test 7: getStats() method =====
        describe('getStats()', () => {
            test('tracks hit rate correctly', async () => {
                // ARRANGE
                await cache.set('key', 'value');
                await cache.get('key'); // Hit
                await cache.get('nonexistent'); // Miss
                await cache.get('key'); // Hit
                
                // ACT
                const stats = await cache.getStats();
                
                // ASSERT
                expect(stats.hits).toBe(2);
                expect(stats.misses).toBe(1);
                expect(stats.hitRate).toBeCloseTo(0.667, 2);
                expect(stats.type).toBe(cacheName);
            });
            
            test('tracks operations correctly', async () => {
                // ARRANGE & ACT
                await cache.set('key1', 'value1');
                await cache.set('key2', 'value2');
                await cache.delete('key1');
                await cache.clear();
                
                // ASSERT
                const stats = await cache.getStats();
                expect(stats.sets).toBe(2);
                expect(stats.deletes).toBe(1);
                expect(stats.clears).toBe(1);
            });
            
            test('reports entry count and size', async () => {
                // ARRANGE
                await cache.set('key1', 'small');
                await cache.set('key2', { large: 'x'.repeat(1000) });
                
                // ACT
                const stats = await cache.getStats();
                
                // ASSERT
                expect(stats.entries).toBe(2);
                expect(stats.sizeKB).toBeGreaterThan(0);
            });
        });
    });
}

// ===== Run tests for both implementations =====
runCacheTests(InMemoryCache, 'InMemoryCache');
runCacheTests(LocalStorageCache, 'LocalStorageCache');

// ===== Implementation-specific tests =====
describe('LocalStorageCache - Specific Behavior', () => {
    let cache;
    
    beforeEach(() => {
        global.localStorage.clear();
        cache = new LocalStorageCache();
    });
    
    test('uses namespace prefix to avoid collisions', async () => {
        // ARRANGE
        await cache.set('test', 'value');
        
        // ACT
        const rawKey = 'app_v2_cache_test'; // Default prefix
        const stored = global.localStorage.getItem(rawKey);
        
        // ASSERT
        expect(stored).not.toBeNull();
        expect(JSON.parse(stored).value).toBe('value');
    });
    
    test('handles localStorage unavailable gracefully', async () => {
        // ARRANGE
        const originalLocalStorage = global.localStorage;
        global.localStorage = null;
        const unavailableCache = new LocalStorageCache();
        
        // ACT & ASSERT (should not throw)
        await expect(unavailableCache.set('key', 'value')).resolves.toBeUndefined();
        await expect(unavailableCache.get('key')).resolves.toBeNull();
        await expect(unavailableCache.has('key')).resolves.toBe(false);
        
        // CLEANUP
        global.localStorage = originalLocalStorage;
    });
    
    test('stats persist across cache instances', async () => {
        // ARRANGE
        const cache1 = new LocalStorageCache();
        await cache1.set('key', 'value');
        await cache1.get('key');
        
        // ACT
        const cache2 = new LocalStorageCache(); // New instance
        const stats = await cache2.getStats();
        
        // ASSERT
        expect(stats.sets).toBe(1);
        expect(stats.hits).toBe(1);
    });
});

describe('InMemoryCache - Specific Behavior', () => {
    test('stats do NOT persist across instances', async () => {
        // ARRANGE
        const cache1 = new InMemoryCache();
        await cache1.set('key', 'value');
        await cache1.get('key');
        
        // ACT
        const cache2 = new InMemoryCache(); // New instance
        const stats = await cache2.getStats();
        
        // ASSERT
        expect(stats.sets).toBe(0); // Fresh instance, no history
        expect(stats.hits).toBe(0);
    });
    
    test('cache data does NOT persist across instances', async () => {
        // ARRANGE
        const cache1 = new InMemoryCache();
        await cache1.set('key', 'value');
        
        // ACT
        const cache2 = new InMemoryCache();
        const result = await cache2.get('key');
        
        // ASSERT
        expect(result).toBeNull(); // Different instance = different Map
    });
});