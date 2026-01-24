/**
 * Unit Tests for Data Products API
 * 
 * Tests the Data Products API in a pure Node.js environment
 * without any browser dependencies.
 * 
 * Run with: node tests/dataProductsAPI.test.js
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */

import { DataProductsAPI } from '../js/api/dataProductsAPI.js';

/**
 * Simple test runner for Node.js
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
            return true;
        } catch (error) {
            this.failed++;
            console.error(`❌ ${name}`);
            console.error(`   ${error.message}`);
            if (error.stack) {
                console.error(`   ${error.stack.split('\n')[1]}`);
            }
            return false;
        }
    }

    assert(condition, message) {
        if (!condition) {
            throw new Error(message || 'Assertion failed');
        }
    }

    assertEqual(actual, expected, message) {
        if (actual !== expected) {
            throw new Error(message || `Expected ${expected}, got ${actual}`);
        }
    }

    assertNotNull(value, message) {
        if (value === null || value === undefined) {
            throw new Error(message || 'Value should not be null');
        }
    }

    async run() {
        console.log('\n🧪 Data Products API Tests\n');
        console.log('=' .repeat(50));
        
        const startTime = Date.now();

        // Test 1: Constructor
        await this.test('Constructor initializes with default baseURL', () => {
            const api = new DataProductsAPI();
            this.assertEqual(api.baseURL, 'http://localhost:3000');
            this.assertNotNull(api.cache);
            this.assertEqual(api.cacheTTL, 60000);
        });

        // Test 2: Constructor with custom URL
        await this.test('Constructor accepts custom baseURL', () => {
            const customURL = 'https://api.example.com';
            const api = new DataProductsAPI(customURL);
            this.assertEqual(api.baseURL, customURL);
        });

        // Test 3: Cache validation
        await this.test('_isCacheValid returns false for non-existent key', () => {
            const api = new DataProductsAPI();
            const result = api._isCacheValid('non-existent-key');
            this.assertEqual(result, false);
        });

        // Test 4: Cache validation with fresh data
        await this.test('_isCacheValid returns true for fresh data', () => {
            const api = new DataProductsAPI();
            api._setCache('test-key', { data: 'test' });
            const result = api._isCacheValid('test-key');
            this.assertEqual(result, true);
        });

        // Test 5: Cache retrieval
        await this.test('_getCached returns cached data when valid', () => {
            const api = new DataProductsAPI();
            const testData = { test: 'value' };
            api._setCache('test-key', testData);
            const result = api._getCached('test-key');
            this.assertNotNull(result);
            this.assertEqual(result.test, 'value');
        });

        // Test 6: Cache retrieval for missing key
        await this.test('_getCached returns null for missing key', () => {
            const api = new DataProductsAPI();
            const result = api._getCached('missing-key');
            this.assertEqual(result, null);
        });

        // Test 7: Cache clearing
        await this.test('clearCache removes all cached data', () => {
            const api = new DataProductsAPI();
            api._setCache('key1', 'value1');
            api._setCache('key2', 'value2');
            api.clearCache();
            this.assertEqual(api.cache.size, 0);
        });

        // Test 8: Cache statistics
        await this.test('getCacheStats returns correct statistics', () => {
            const api = new DataProductsAPI();
            api._setCache('key1', 'value1');
            api._setCache('key2', 'value2');
            const stats = api.getCacheStats();
            this.assertEqual(stats.size, 2);
            this.assertEqual(stats.keys.length, 2);
            this.assertEqual(stats.ttl, 60000);
        });

        // Test 9: Metadata parsing
        await this.test('getDataProductMetadata parses schema names correctly', () => {
            const api = new DataProductsAPI();
            const schemaName = '_SAP_DATAPRODUCT_sap_s4com_dataProduct_Supplier_v1_c8f5c255-6ddd-444a-8f90-01baa10b87d3';
            const metadata = api.getDataProductMetadata(schemaName);
            
            this.assertEqual(metadata.schemaName, schemaName);
            this.assertEqual(metadata.productName, 'Supplier');
            this.assertEqual(metadata.version, 'v1');
            this.assertNotNull(metadata.displayName);
        });

        // Test 10: Product name formatting
        await this.test('_formatProductName formats names correctly', () => {
            const api = new DataProductsAPI();
            this.assertEqual(api._formatProductName('PurchaseOrder'), 'Purchase Order');
            this.assertEqual(api._formatProductName('Supplier'), 'Supplier');
            this.assertEqual(api._formatProductName('ServiceEntrySheet'), 'Service Entry Sheet');
        });

        // Test 11: Error handling in listDataProducts (mock fetch)
        await this.test('listDataProducts handles fetch errors gracefully', async () => {
            const api = new DataProductsAPI();
            // Override _request to simulate error
            api._request = async () => {
                throw new Error('Network error');
            };
            
            try {
                await api.listDataProducts();
                throw new Error('Should have thrown an error');
            } catch (error) {
                this.assert(error.message.includes('Network error') || error.code === 'API_ERROR');
            }
        });

        // Test 12: Cache usage in listDataProducts
        await this.test('listDataProducts uses cache on second call', async () => {
            const api = new DataProductsAPI();
            const mockData = {
                success: true,
                count: 2,
                dataProducts: [
                    { schemaName: 'test1', productName: 'Test1' },
                    { schemaName: 'test2', productName: 'Test2' }
                ]
            };
            
            // Mock _request
            let callCount = 0;
            api._request = async () => {
                callCount++;
                return mockData;
            };
            
            // First call
            await api.listDataProducts();
            this.assertEqual(callCount, 1);
            
            // Second call should use cache
            await api.listDataProducts();
            this.assertEqual(callCount, 1); // Still 1, used cache
        });

        // Test 13: getTables parameter validation
        await this.test('getTables throws error for missing schemaName', async () => {
            const api = new DataProductsAPI();
            
            try {
                await api.getTables();
                throw new Error('Should have thrown an error');
            } catch (error) {
                this.assert(error.message.includes('required'));
            }
        });

        // Test 14: getTableStructure parameter validation
        await this.test('getTableStructure throws error for missing parameters', async () => {
            const api = new DataProductsAPI();
            
            try {
                await api.getTableStructure('schema');
                throw new Error('Should have thrown an error');
            } catch (error) {
                this.assert(error.message.includes('required'));
            }
        });

        // Test 15: queryTable parameter validation
        await this.test('queryTable throws error for missing parameters', async () => {
            const api = new DataProductsAPI();
            
            try {
                await api.queryTable();
                throw new Error('Should have thrown an error');
            } catch (error) {
                this.assert(error.message.includes('required'));
            }
        });

        // Test 16: queryTable with default options
        await this.test('queryTable applies default options correctly', async () => {
            const api = new DataProductsAPI();
            let capturedOptions;
            
            api._request = async (endpoint, options) => {
                if (options && options.body) {
                    capturedOptions = JSON.parse(options.body);
                }
                return { success: true, rows: [] };
            };
            
            await api.queryTable('schema', 'table');
            
            this.assertEqual(capturedOptions.limit, 100);
            this.assertEqual(capturedOptions.offset, 0);
        });

        // Test 17: queryTable with custom options
        await this.test('queryTable respects custom options', async () => {
            const api = new DataProductsAPI();
            let capturedOptions;
            
            api._request = async (endpoint, options) => {
                if (options && options.body) {
                    capturedOptions = JSON.parse(options.body);
                }
                return { success: true, rows: [] };
            };
            
            await api.queryTable('schema', 'table', {
                limit: 50,
                offset: 100,
                where: "Country='US'"
            });
            
            this.assertEqual(capturedOptions.limit, 50);
            this.assertEqual(capturedOptions.offset, 100);
            this.assertEqual(capturedOptions.where, "Country='US'");
        });

        // Summary
        const duration = Date.now() - startTime;
        console.log('=' .repeat(50));
        console.log(`\n📊 Test Results:`);
        console.log(`   Total: ${this.passed + this.failed}`);
        console.log(`   ✅ Passed: ${this.passed}`);
        console.log(`   ❌ Failed: ${this.failed}`);
        console.log(`   ⏱️  Duration: ${duration}ms`);
        console.log(`   📈 Coverage: ${Math.round((this.passed / (this.passed + this.failed)) * 100)}%\n`);

        return this.failed === 0;
    }
}

// Run tests
const runner = new TestRunner();
runner.run().then(success => {
    process.exit(success ? 0 : 1);
}).catch(error => {
    console.error('Test runner error:', error);
    process.exit(1);
});
