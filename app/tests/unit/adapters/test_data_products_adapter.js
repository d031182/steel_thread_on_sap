/**
 * Unit Tests: DataProductsAdapter
 * 
 * Test Framework: Gu Wu (顾武) Frontend Testing
 * Pattern: AAA (Arrange-Act-Assert)
 * Coverage Target: 100% (all 5 IDataSource methods + retry logic)
 */

// Mock fetch for testing
global.fetch = jest.fn();
global.performance = {
    now: jest.fn(() => Date.now())
};

// Import adapter
const DataProductsAdapter = require('../../../static/js/adapters/DataProductsAdapter.js');

// Mock IDataSource base class
class IDataSource {
    async query(sql, params = []) {
        throw new Error('Not implemented');
    }
    async getTables() {
        throw new Error('Not implemented');
    }
    async getTableSchema(tableName) {
        throw new Error('Not implemented');
    }
    getType() {
        throw new Error('Not implemented');
    }
    async testConnection() {
        throw new Error('Not implemented');
    }
}
global.IDataSource = IDataSource;

describe('DataProductsAdapter - IDataSource Implementation', () => {
    let adapter;
    let mockCache;
    
    beforeEach(() => {
        // Reset fetch mock
        global.fetch.mockClear();
        
        // Create mock cache
        mockCache = {
            _store: {},
            get: jest.fn(async (key) => mockCache._store[key] || null),
            set: jest.fn(async (key, value) => { mockCache._store[key] = value; }),
            has: jest.fn(async (key) => !!mockCache._store[key]),
            clear: jest.fn(async () => { mockCache._store = {}; })
        };
        
        // Create adapter with mock cache
        adapter = new DataProductsAdapter({
            baseUrl: '/api/data_products',
            source: 'sqlite',
            timeout: 5000,
            maxRetries: 2,
            cache: mockCache
        });
    });
    
    // ===== Test 1: query() method =====
    describe('query()', () => {
        test('executes SQL query successfully', async () => {
            // ARRANGE
            const sql = 'SELECT * FROM Supplier';
            const mockResponse = {
                success: true,
                rows: [
                    { ID: '1', Name: 'Supplier A' },
                    { ID: '2', Name: 'Supplier B' }
                ]
            };
            
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockResponse
            });
            
            // ACT
            const result = await adapter.query(sql);
            
            // ASSERT
            expect(result).toEqual(mockResponse.rows);
            expect(global.fetch).toHaveBeenCalledWith(
                '/api/data_products/execute-sql',
                expect.objectContaining({
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ sql })
                })
            );
        });
        
        test('caches successful query results', async () => {
            // ARRANGE
            const sql = 'SELECT * FROM Supplier';
            const mockResponse = {
                success: true,
                rows: [{ ID: '1', Name: 'Test' }]
            };
            
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockResponse
            });
            
            // ACT
            await adapter.query(sql);
            
            // ASSERT
            expect(mockCache.set).toHaveBeenCalledWith(
                `query:sqlite:${sql}`,
                mockResponse.rows,
                300 // 5 min TTL
            );
        });
        
        test('returns cached results on second call', async () => {
            // ARRANGE
            const sql = 'SELECT * FROM Supplier';
            const cachedData = [{ ID: '1', Name: 'Cached' }];
            mockCache._store[`query:sqlite:${sql}`] = cachedData;
            
            // ACT
            const result = await adapter.query(sql);
            
            // ASSERT
            expect(result).toEqual(cachedData);
            expect(global.fetch).not.toHaveBeenCalled(); // No network call
            expect(mockCache.get).toHaveBeenCalled();
        });
        
        test('throws error for empty SQL', async () => {
            // ACT & ASSERT
            await expect(adapter.query('')).rejects.toThrow('SQL query cannot be empty');
            await expect(adapter.query('   ')).rejects.toThrow('SQL query cannot be empty');
        });
        
        test('throws error for backend failure', async () => {
            // ARRANGE
            const sql = 'SELECT * FROM NonExistent';
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    success: false,
                    error: { message: 'Table not found' }
                })
            });
            
            // ACT & ASSERT
            await expect(adapter.query(sql)).rejects.toThrow('Table not found');
        });
    });
    
    // ===== Test 2: getTables() method =====
    describe('getTables()', () => {
        test('returns list of tables', async () => {
            // ARRANGE
            const mockResponse = {
                success: true,
                data_products: [
                    {
                        schema: 'P2P_SCHEMA',
                        tables: [
                            { name: 'Supplier' },
                            { name: 'Purchase_Order' }
                        ]
                    }
                ]
            };
            
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockResponse
            });
            
            // ACT
            const result = await adapter.getTables();
            
            // ASSERT
            expect(result).toEqual(['Supplier', 'Purchase_Order']);
            expect(global.fetch).toHaveBeenCalledWith(
                '/api/data_products/?source=sqlite',
                undefined
            );
        });
        
        test('caches table list', async () => {
            // ARRANGE
            const mockResponse = {
                success: true,
                data_products: [
                    { schema: 'P2P_SCHEMA', tables: [{ name: 'Test' }] }
                ]
            };
            
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockResponse
            });
            
            // ACT
            await adapter.getTables();
            
            // ASSERT
            expect(mockCache.set).toHaveBeenCalledWith(
                'tables:sqlite',
                ['Test'],
                600 // 10 min TTL
            );
        });
        
        test('returns empty array if no tables', async () => {
            // ARRANGE
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ success: true, data_products: [] })
            });
            
            // ACT
            const result = await adapter.getTables();
            
            // ASSERT
            expect(result).toEqual([]);
        });
    });
    
    // ===== Test 3: getTableSchema() method =====
    describe('getTableSchema()', () => {
        test('returns table schema', async () => {
            // ARRANGE
            const mockResponse = {
                success: true,
                columns: [
                    { name: 'ID', type: 'TEXT' },
                    { name: 'Name', type: 'TEXT' }
                ]
            };
            
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockResponse
            });
            
            // ACT
            const result = await adapter.getTableSchema('Supplier');
            
            // ASSERT
            expect(result.tableName).toBe('Supplier');
            expect(result.columns).toEqual(['ID', 'Name']);
            expect(result.types).toEqual(['TEXT', 'TEXT']);
            expect(result.columnDetails).toEqual(mockResponse.columns);
        });
        
        test('caches schema results', async () => {
            // ARRANGE
            const mockResponse = {
                success: true,
                columns: [{ name: 'ID', type: 'TEXT' }]
            };
            
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => mockResponse
            });
            
            // ACT
            await adapter.getTableSchema('Supplier');
            
            // ASSERT
            expect(mockCache.set).toHaveBeenCalledWith(
                'schema:sqlite:Supplier',
                expect.objectContaining({ tableName: 'Supplier' }),
                600 // 10 min TTL
            );
        });
        
        test('throws error for missing table name', async () => {
            // ACT & ASSERT
            await expect(adapter.getTableSchema('')).rejects.toThrow('Table name is required');
            await expect(adapter.getTableSchema(null)).rejects.toThrow('Table name is required');
        });
        
        test('throws error if table not found', async () => {
            // ARRANGE
            global.fetch.mockResolvedValue({
                ok: true,
                json: async () => ({ success: false })
            });
            
            // ACT & ASSERT
            await expect(adapter.getTableSchema('NonExistent'))
                .rejects.toThrow("Table 'NonExistent' not found");
        });
    });
    
    // ===== Test 4: getType() method =====
    describe('getType()', () => {
        test('returns configured source type', () => {
            // ACT
            const type = adapter.getType();
            
            // ASSERT
            expect(type).toBe('sqlite');
        });
        
        test('defaults to hana if not specified', () => {
            // ARRANGE
            const defaultAdapter = new DataProductsAdapter();
            
            // ACT
            const type = defaultAdapter.getType();
            
            // ASSERT
            expect(type).toBe('hana');
        });
    });
    
    // ===== Test 5: testConnection() method =====
    describe('testConnection()', () => {
        test('returns true for healthy connection', async () => {
            // ARRANGE
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({ success: true })
            });
            
            // ACT
            const result = await adapter.testConnection();
            
            // ASSERT
            expect(result).toBe(true);
        });
        
        test('returns false for unhealthy connection', async () => {
            // ARRANGE
            global.fetch.mockRejectedValueOnce(new Error('Network error'));
            
            // ACT
            const result = await adapter.testConnection();
            
            // ASSERT
            expect(result).toBe(false);
        });
        
        test('uses only 1 retry for health checks', async () => {
            // ARRANGE
            global.fetch
                .mockRejectedValueOnce(new Error('First attempt fails'))
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ success: true })
                });
            
            // ACT
            const result = await adapter.testConnection();
            
            // ASSERT
            expect(result).toBe(true);
            expect(global.fetch).toHaveBeenCalledTimes(2); // Initial + 1 retry
        });
    });
    
    // ===== Test 6: Retry Logic =====
    describe('Retry Logic', () => {
        test('retries on network failure', async () => {
            // ARRANGE
            const sql = 'SELECT * FROM Supplier';
            global.fetch
                .mockRejectedValueOnce(new Error('Network error'))
                .mockRejectedValueOnce(new Error('Network error'))
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ success: true, rows: [] })
                });
            
            // ACT
            const result = await adapter.query(sql);
            
            // ASSERT
            expect(result).toEqual([]);
            expect(global.fetch).toHaveBeenCalledTimes(3); // Initial + 2 retries
            
            const stats = adapter.getStats();
            expect(stats.retries).toBe(2);
        });
        
        test('retries on 500 server error', async () => {
            // ARRANGE
            const sql = 'SELECT * FROM Supplier';
            global.fetch
                .mockResolvedValueOnce({
                    ok: false,
                    status: 500,
                    statusText: 'Internal Server Error',
                    text: async () => 'Server error'
                })
                .mockResolvedValueOnce({
                    ok: true,
                    json: async () => ({ success: true, rows: [] })
                });
            
            // ACT
            const result = await adapter.query(sql);
            
            // ASSERT
            expect(result).toEqual([]);
            expect(global.fetch).toHaveBeenCalledTimes(2);
        });
        
        test('does NOT retry on 400 client error', async () => {
            // ARRANGE
            const sql = 'INVALID SQL';
            global.fetch.mockResolvedValueOnce({
                ok: false,
                status: 400,
                statusText: 'Bad Request',
                text: async () => 'Invalid SQL syntax'
            });
            
            // ACT & ASSERT
            await expect(adapter.query(sql)).rejects.toThrow('HTTP 400');
            expect(global.fetch).toHaveBeenCalledTimes(1); // No retry
        });
        
        test('throws after max retries exceeded', async () => {
            // ARRANGE
            const sql = 'SELECT * FROM Supplier';
            global.fetch.mockRejectedValue(new Error('Network error'));
            
            // ACT & ASSERT
            await expect(adapter.query(sql)).rejects.toThrow('Network error');
            expect(global.fetch).toHaveBeenCalledTimes(3); // Initial + 2 retries
        });
    });
    
    // ===== Test 7: Statistics Tracking =====
    describe('Statistics', () => {
        test('tracks successful requests', async () => {
            // ARRANGE
            global.fetch.mockResolvedValue({
                ok: true,
                json: async () => ({ success: true, rows: [] })
            });
            
            // ACT
            await adapter.query('SELECT 1');
            await adapter.query('SELECT 2');
            
            // ASSERT
            const stats = adapter.getStats();
            expect(stats.requests).toBe(2);
            expect(stats.successes).toBe(2);
            expect(stats.failures).toBe(0);
        });
        
        test('tracks failed requests', async () => {
            // ARRANGE
            global.fetch.mockRejectedValue(new Error('Network error'));
            
            // ACT
            try {
                await adapter.query('SELECT 1');
            } catch (e) {
                // Expected
            }
            
            // ASSERT
            const stats = adapter.getStats();
            expect(stats.requests).toBe(3); // Initial + 2 retries
            expect(stats.successes).toBe(0);
            expect(stats.failures).toBe(1);
            expect(stats.retries).toBe(2);
        });
        
        test('tracks cache hits and misses', async () => {
            // ARRANGE
            const sql = 'SELECT * FROM Supplier';
            global.fetch.mockResolvedValue({
                ok: true,
                json: async () => ({ success: true, rows: [{ ID: '1' }] })
            });
            
            // ACT
            await adapter.query(sql); // Cache miss + set
            await adapter.query(sql); // Cache hit
            await adapter.query(sql); // Cache hit
            
            // ASSERT
            const stats = adapter.getStats();
            expect(stats.cacheHits).toBe(2);
            expect(stats.cacheMisses).toBe(1);
            expect(stats.cacheHitRate).toBeCloseTo(0.667, 2);
        });
        
        test('tracks average response time', async () => {
            // ARRANGE
            let callCount = 0;
            global.performance.now.mockImplementation(() => {
                callCount++;
                return callCount * 100; // 0ms, 100ms, 200ms, 300ms...
            });
            
            global.fetch.mockResolvedValue({
                ok: true,
                json: async () => ({ success: true, rows: [] })
            });
            
            // ACT
            await adapter.query('SELECT 1'); // 100ms
            await adapter.query('SELECT 2'); // 100ms
            
            // ASSERT
            const stats = adapter.getStats();
            expect(stats.avgResponseTime).toBe(100);
        });
        
        test('clearStats() resets all counters', async () => {
            // ARRANGE
            global.fetch.mockResolvedValue({
                ok: true,
                json: async () => ({ success: true, rows: [] })
            });
            await adapter.query('SELECT 1');
            
            // ACT
            adapter.clearStats();
            
            // ASSERT
            const stats = adapter.getStats();
            expect(stats.requests).toBe(0);
            expect(stats.successes).toBe(0);
            expect(stats.failures).toBe(0);
        });
    });
    
    // ===== Test 8: Error Handling =====
    describe('Error Handling', () => {
        test('handles timeout gracefully', async () => {
            // ARRANGE
            const sql = 'SELECT * FROM Supplier';
            global.fetch.mockImplementation(() => 
                new Promise((resolve, reject) => {
                    const error = new Error('Aborted');
                    error.name = 'AbortError';
                    reject(error);
                })
            );
            
            // ACT & ASSERT
            await expect(adapter.query(sql)).rejects.toThrow('Request timeout');
        });
        
        test('provides user-friendly error messages', async () => {
            // ARRANGE
            const sql = 'SELECT * FROM Supplier';
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: async () => ({
                    success: false,
                    error: { message: 'Connection to HANA failed', code: 'DB_ERROR' }
                })
            });
            
            // ACT & ASSERT
            await expect(adapter.query(sql)).rejects.toThrow('Connection to HANA failed');
        });
    });
    
    // ===== Test 9: Configuration =====
    describe('Configuration', () => {
        test('uses default configuration', () => {
            // ARRANGE
            const defaultAdapter = new DataProductsAdapter();
            
            // ACT
            const stats = defaultAdapter.getStats();
            
            // ASSERT
            expect(stats.source).toBe('hana'); // Default
            expect(stats.timeout).toBe(30000); // 30s default
            expect(stats.maxRetries).toBe(3); // 3 retries default
        });
        
        test('accepts custom configuration', () => {
            // ARRANGE
            const customAdapter = new DataProductsAdapter({
                baseUrl: '/custom/api',
                source: 'sqlite',
                timeout: 10000,
                maxRetries: 5
            });
            
            // ACT
            const stats = customAdapter.getStats();
            
            // ASSERT
            expect(stats.source).toBe('sqlite');
            expect(stats.timeout).toBe(10000);
            expect(stats.maxRetries).toBe(5);
        });
    });
    
    // ===== Test 10: Cache Integration =====
    describe('Cache Integration', () => {
        test('works without cache (cache = null)', async () => {
            // ARRANGE
            const noCacheAdapter = new DataProductsAdapter({
                cache: null
            });
            
            global.fetch.mockResolvedValue({
                ok: true,
                json: async () => ({ success: true, rows: [] })
            });
            
            // ACT & ASSERT (should not throw)
            await expect(noCacheAdapter.query('SELECT 1')).resolves.toEqual([]);
        });
        
        test('setCache() updates cache instance', () => {
            // ARRANGE
            const newCache = { get: jest.fn(), set: jest.fn() };
            
            // ACT
            adapter.setCache(newCache);
            
            // ASSERT
            expect(adapter.getCache()).toBe(newCache);
        });
    });
});