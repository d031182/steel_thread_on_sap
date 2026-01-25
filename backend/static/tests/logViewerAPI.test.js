/**
 * Log Viewer API - Unit Tests
 * ============================
 * Tests for Log Viewer API business logic.
 * Runs in Node.js without browser dependencies.
 */

// Import the API (works in Node.js)
const { LogViewerAPI } = require('../js/api/logViewerAPI.js');

/**
 * Simple test runner
 */
class TestRunner {
    constructor() {
        this.passed = 0;
        this.failed = 0;
        this.tests = [];
    }

    async test(name, fn) {
        try {
            await fn();
            this.passed++;
            console.log(`✅ ${name}`);
            this.tests.push({ name, status: 'passed' });
        } catch (error) {
            this.failed++;
            console.error(`❌ ${name}`);
            console.error(`   Error: ${error.message}`);
            this.tests.push({ name, status: 'failed', error: error.message });
        }
    }

    printResults() {
        console.log('\n📊 Test Results:');
        console.log(`   Total: ${this.passed + this.failed}`);
        console.log(`   ✅ Passed: ${this.passed}`);
        console.log(`   ❌ Failed: ${this.failed}`);
        
        if (this.failed === 0) {
            console.log('\n🎉 ALL TESTS PASSED!');
        }
    }
}

/**
 * Mock fetch for testing
 */
function createMockFetch(mockResponse) {
    return async (url, options = {}) => {
        return {
            json: async () => mockResponse
        };
    };
}

/**
 * Run all tests
 */
async function runTests() {
    console.log('🧪 Log Viewer API Tests\n');

    const runner = new TestRunner();

    // Test 1: Constructor with default URL
    await runner.test('Constructor initializes with default baseURL', async () => {
        const api = new LogViewerAPI();
        if (api.baseURL !== 'http://localhost:5000') {
            throw new Error(`Expected baseURL to be 'http://localhost:5000', got '${api.baseURL}'`);
        }
        if (api.cacheTTL !== 10000) {
            throw new Error(`Expected cacheTTL to be 10000, got ${api.cacheTTL}`);
        }
    });

    // Test 2: Constructor with custom URL
    await runner.test('Constructor accepts custom baseURL', async () => {
        const api = new LogViewerAPI('http://custom:8080');
        if (api.baseURL !== 'http://custom:8080') {
            throw new Error(`Expected baseURL to be 'http://custom:8080', got '${api.baseURL}'`);
        }
    });

    // Test 3: Cache validation - non-existent key
    await runner.test('_isCacheValid returns false for non-existent key', async () => {
        const api = new LogViewerAPI();
        if (api._isCacheValid('nonexistent')) {
            throw new Error('Expected _isCacheValid to return false for non-existent key');
        }
    });

    // Test 4: Cache validation - fresh data
    await runner.test('_isCacheValid returns true for fresh data', async () => {
        const api = new LogViewerAPI();
        api._setCached('test', { data: 'test' });
        if (!api._isCacheValid('test')) {
            throw new Error('Expected _isCacheValid to return true for fresh data');
        }
    });

    // Test 5: Get cached data - valid
    await runner.test('_getCached returns cached data when valid', async () => {
        const api = new LogViewerAPI();
        const testData = { logs: [{ id: 1, message: 'test' }] };
        api._setCached('test', testData);
        const cached = api._getCached('test');
        if (JSON.stringify(cached) !== JSON.stringify(testData)) {
            throw new Error('Expected _getCached to return cached data');
        }
    });

    // Test 6: Get cached data - missing key
    await runner.test('_getCached returns null for missing key', async () => {
        const api = new LogViewerAPI();
        const cached = api._getCached('missing');
        if (cached !== null) {
            throw new Error('Expected _getCached to return null for missing key');
        }
    });

    // Test 7: Clear cache
    await runner.test('clearCache removes all cached data', async () => {
        const api = new LogViewerAPI();
        api._setCached('test1', { data: 'test1' });
        api._setCached('test2', { data: 'test2' });
        api.clearCache();
        if (Object.keys(api.cache).length !== 0) {
            throw new Error('Expected cache to be empty after clearCache');
        }
    });

    // Test 8: Cache statistics
    await runner.test('getCacheStats returns correct statistics', async () => {
        const api = new LogViewerAPI();
        api._setCached('test1', { data: 'test1' });
        api._setCached('test2', { data: 'test2' });
        const stats = api.getCacheStats();
        if (stats.size !== 2) {
            throw new Error(`Expected cache size 2, got ${stats.size}`);
        }
        if (stats.keys.length !== 2) {
            throw new Error(`Expected 2 cache keys, got ${stats.keys.length}`);
        }
    });

    // Test 9: Export to CSV - empty logs
    await runner.test('_exportToCSV throws error for empty logs', async () => {
        const api = new LogViewerAPI();
        try {
            api._exportToCSV([]);
            throw new Error('Expected _exportToCSV to throw error for empty logs');
        } catch (error) {
            if (error.message !== 'No logs to export') {
                throw error;
            }
        }
    });

    // Test 10: Export to CSV - valid logs
    await runner.test('_exportToCSV creates valid CSV', async () => {
        const api = new LogViewerAPI();
        const logs = [
            { id: 1, timestamp: '2026-01-22T11:00:00Z', level: 'INFO', logger: 'test', message: 'Test message' }
        ];
        const blob = api._exportToCSV(logs);
        if (!(blob instanceof Blob)) {
            throw new Error('Expected _exportToCSV to return Blob');
        }
        if (blob.type !== 'text/csv;charset=utf-8;') {
            throw new Error(`Expected CSV mime type, got ${blob.type}`);
        }
    });

    // Test 11: Export to JSON
    await runner.test('_exportToJSON creates valid JSON', async () => {
        const api = new LogViewerAPI();
        const logs = [
            { id: 1, timestamp: '2026-01-22T11:00:00Z', level: 'INFO', logger: 'test', message: 'Test' }
        ];
        const blob = api._exportToJSON(logs);
        if (!(blob instanceof Blob)) {
            throw new Error('Expected _exportToJSON to return Blob');
        }
        if (blob.type !== 'application/json') {
            throw new Error(`Expected JSON mime type, got ${blob.type}`);
        }
    });

    // Test 12: Search logs - client-side filtering
    await runner.test('searchLogs filters by search term', async () => {
        const api = new LogViewerAPI();
        
        // Mock fetch to return sample logs
        global.fetch = createMockFetch({
            success: true,
            logs: [
                { id: 1, message: 'Test message one' },
                { id: 2, message: 'Another test' },
                { id: 3, message: 'No match here' }
            ],
            totalCount: 3
        });

        const result = await api.searchLogs('test');
        if (result.count !== 2) {
            throw new Error(`Expected 2 matching logs, got ${result.count}`);
        }
        if (result.searchTerm !== 'test') {
            throw new Error(`Expected searchTerm 'test', got '${result.searchTerm}'`);
        }
    });

    // Test 13: Get logs by level
    await runner.test('getLogsByLevel fetches all three levels', async () => {
        const api = new LogViewerAPI();
        
        let callCount = 0;
        global.fetch = createMockFetch({
            success: true,
            logs: [],
            totalCount: callCount++
        });

        const result = await api.getLogsByLevel(10);
        if (!result.info || !result.warning || !result.error) {
            throw new Error('Expected result to have info, warning, and error properties');
        }
        if (!result.counts) {
            throw new Error('Expected result to have counts property');
        }
    });

    // Test 14: Get recent errors
    await runner.test('getRecentErrors fetches ERROR level logs', async () => {
        const api = new LogViewerAPI();
        
        global.fetch = createMockFetch({
            success: true,
            logs: [
                { id: 1, level: 'ERROR', message: 'Error 1' },
                { id: 2, level: 'ERROR', message: 'Error 2' }
            ],
            totalCount: 2
        });

        const errors = await api.getRecentErrors(10);
        if (errors.length !== 2) {
            throw new Error(`Expected 2 errors, got ${errors.length}`);
        }
    });

    // Test 15: Test connection
    await runner.test('testConnection returns boolean', async () => {
        const api = new LogViewerAPI();
        
        global.fetch = createMockFetch({
            status: 'healthy'
        });

        const result = await api.testConnection();
        if (typeof result !== 'boolean') {
            throw new Error(`Expected boolean, got ${typeof result}`);
        }
    });

    runner.printResults();
    
    // Exit with appropriate code
    process.exit(runner.failed > 0 ? 1 : 0);
}

// Run tests
runTests().catch(error => {
    console.error('Fatal test error:', error);
    process.exit(1);
});
