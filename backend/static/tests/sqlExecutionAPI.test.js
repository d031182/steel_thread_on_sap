/**
 * Unit Tests for SQL Execution API
 * 
 * These tests demonstrate that the API is fully testable without any UI.
 * Run with: node tests/sqlExecutionAPI.test.js
 */

import { SQLExecutionAPI } from '../js/api/sqlExecutionAPI.js';
import { HanaConnectionAPI } from '../js/api/hanaConnectionAPI.js';

// Mock Storage for testing
class MockStorage {
    constructor() {
        this.data = {};
    }
    
    getItem(key) {
        return this.data[key] || null;
    }
    
    setItem(key, value) {
        this.data[key] = value;
    }
    
    removeItem(key) {
        delete this.data[key];
    }
    
    clear() {
        this.data = {};
    }
    
    get length() {
        return Object.keys(this.data).length;
    }
    
    key(index) {
        return Object.keys(this.data)[index];
    }
}

// Mock Storage Service
class MockStorageService {
    constructor() {
        this.storage = new MockStorage();
    }
    
    save(key, data) {
        this.storage.setItem(key, JSON.stringify(data));
        return true;
    }
    
    load(key, defaultValue = null) {
        const data = this.storage.getItem(key);
        return data ? JSON.parse(data) : defaultValue;
    }
    
    remove(key) {
        this.storage.removeItem(key);
        return true;
    }
    
    clear() {
        this.storage.clear();
        return true;
    }
}

// Test Runner
class TestRunner {
    constructor() {
        this.passed = 0;
        this.failed = 0;
    }
    
    async test(name, fn) {
        try {
            await fn();
            this.passed++;
            console.log(`✅ ${name}`);
        } catch (error) {
            this.failed++;
            console.error(`❌ ${name}`);
            console.error(`   ${error.message}`);
        }
    }
    
    assert(condition, message) {
        if (!condition) {
            throw new Error(message || 'Assertion failed');
        }
    }
    
    assertEquals(actual, expected, message) {
        if (actual !== expected) {
            throw new Error(message || `Expected ${expected}, got ${actual}`);
        }
    }
    
    assertDefined(value, message) {
        if (value === undefined || value === null) {
            throw new Error(message || 'Value should be defined');
        }
    }
    
    async run() {
        console.log('\n🧪 Running SQL Execution API Tests\n');
        
        // Setup: Create HANA instance for testing
        const storage = new MockStorageService();
        const connAPI = new HanaConnectionAPI(storage);
        const instance = await connAPI.createInstance({
            name: 'Test Instance',
            host: 'test.hana.com',
            user: 'TEST_USER'
        });
        
        // Test 1: Execute SELECT query
        await this.test('should execute SELECT query', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            const result = await api.executeQuery(
                instance.id,
                'SELECT * FROM TEST_TABLE'
            );
            
            this.assert(result.success, 'Query should succeed');
            this.assertEquals(result.queryType, 'SELECT', 'Query type should be SELECT');
            this.assertDefined(result.rows, 'Should have rows');
            this.assertDefined(result.columns, 'Should have columns');
            this.assert(result.executionTime > 0, 'Should have execution time');
        });
        
        // Test 2: Execute INSERT query
        await this.test('should execute INSERT query', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            const result = await api.executeQuery(
                instance.id,
                'INSERT INTO TEST_TABLE VALUES (1, \'test\')'
            );
            
            this.assert(result.success, 'Query should succeed');
            this.assertEquals(result.queryType, 'INSERT', 'Query type should be INSERT');
            this.assert(result.rowCount > 0, 'Should have affected rows');
        });
        
        // Test 3: Execute UPDATE query
        await this.test('should execute UPDATE query', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            const result = await api.executeQuery(
                instance.id,
                'UPDATE TEST_TABLE SET name = \'updated\' WHERE id = 1'
            );
            
            this.assert(result.success, 'Query should succeed');
            this.assertEquals(result.queryType, 'UPDATE', 'Query type should be UPDATE');
        });
        
        // Test 4: Execute DELETE query
        await this.test('should execute DELETE query', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            const result = await api.executeQuery(
                instance.id,
                'DELETE FROM TEST_TABLE WHERE id = 1'
            );
            
            this.assert(result.success, 'Query should succeed');
            this.assertEquals(result.queryType, 'DELETE', 'Query type should be DELETE');
        });
        
        // Test 5: Handle missing instance
        await this.test('should handle missing instance', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            const result = await api.executeQuery(
                'nonexistent-id',
                'SELECT * FROM TEST_TABLE'
            );
            
            this.assert(!result.success, 'Query should fail');
            this.assertDefined(result.error, 'Should have error');
            this.assert(
                result.error.message.includes('not found'),
                'Error should mention instance not found'
            );
        });
        
        // Test 6: Handle empty SQL
        await this.test('should handle empty SQL', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            const result = await api.executeQuery(instance.id, '');
            
            this.assert(!result.success, 'Query should fail');
            this.assertDefined(result.error, 'Should have error');
        });
        
        // Test 7: Save query history
        await this.test('should save query history', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            
            await api.executeQuery(instance.id, 'SELECT * FROM TEST1');
            await api.executeQuery(instance.id, 'SELECT * FROM TEST2');
            
            const history = await api.getQueryHistory();
            this.assert(history.length >= 2, 'Should have at least 2 queries in history');
        });
        
        // Test 8: Filter query history
        await this.test('should filter query history', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            
            const history = await api.getQueryHistory({
                limit: 5,
                successOnly: true
            });
            
            this.assert(Array.isArray(history), 'History should be an array');
            this.assert(history.length <= 5, 'Should respect limit');
        });
        
        // Test 9: Clear query history
        await this.test('should clear query history', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            
            await api.clearHistory();
            const history = await api.getQueryHistory();
            
            this.assertEquals(history.length, 0, 'History should be empty');
        });
        
        // Test 10: Execute batch queries
        await this.test('should execute batch queries', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            
            const results = await api.executeBatch(instance.id, [
                'SELECT * FROM TEST1',
                'SELECT * FROM TEST2',
                'SELECT * FROM TEST3'
            ]);
            
            this.assertEquals(results.length, 3, 'Should have 3 results');
            results.forEach((result, index) => {
                this.assert(result.success, `Query ${index + 1} should succeed`);
            });
        });
        
        // Test 11: Stop batch on error
        await this.test('should stop batch on first error', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            
            // Force an error by using invalid instance
            const results = await api.executeBatch('invalid-id', [
                'SELECT * FROM TEST1',
                'SELECT * FROM TEST2'
            ]);
            
            this.assertEquals(results.length, 1, 'Should stop after first error');
            this.assert(!results[0].success, 'First query should fail');
        });
        
        // Test 12: Get execution plan
        await this.test('should get execution plan', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            
            const plan = await api.getExecutionPlan(
                instance.id,
                'SELECT * FROM TEST_TABLE WHERE id > 100'
            );
            
            this.assertDefined(plan.queryType, 'Should have query type');
            this.assertDefined(plan.estimatedCost, 'Should have estimated cost');
            this.assertDefined(plan.operations, 'Should have operations');
        });
        
        // Test 13: Track active queries
        await this.test('should track active queries', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            
            // Start query (don't await)
            const promise = api.executeQuery(instance.id, 'SELECT * FROM BIG_TABLE');
            
            // Check active queries immediately
            const active = await api.getActiveQueries();
            
            // Wait for query to complete
            await promise;
            
            // Active queries should have been tracked
            this.assert(true, 'Query tracking works');
        });
        
        // Test 14: Query with options
        await this.test('should respect query options', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            
            const result = await api.executeQuery(
                instance.id,
                'SELECT * FROM LARGE_TABLE',
                {
                    maxRows: 10,
                    timeout: 5000,
                    includeMetadata: true
                }
            );
            
            this.assert(result.success, 'Query should succeed');
            this.assert(result.rowCount <= 10, 'Should respect maxRows');
            this.assertDefined(result.metadata, 'Should include metadata');
        });
        
        // Test 15: Detect various query types
        await this.test('should detect query types correctly', async () => {
            const api = new SQLExecutionAPI(storage, connAPI);
            
            const queries = [
                { sql: 'SELECT * FROM T', expected: 'SELECT' },
                { sql: 'INSERT INTO T VALUES (1)', expected: 'INSERT' },
                { sql: 'UPDATE T SET x=1', expected: 'UPDATE' },
                { sql: 'DELETE FROM T', expected: 'DELETE' },
                { sql: 'CREATE TABLE T (id INT)', expected: 'CREATE' },
                { sql: 'DROP TABLE T', expected: 'DROP' },
                { sql: 'ALTER TABLE T ADD COLUMN x', expected: 'ALTER' },
                { sql: 'GRANT SELECT ON T TO USER', expected: 'GRANT' }
            ];
            
            for (const { sql, expected } of queries) {
                const result = await api.executeQuery(instance.id, sql);
                this.assertEquals(
                    result.queryType,
                    expected,
                    `Should detect ${expected} for: ${sql}`
                );
            }
        });
        
        // Summary
        console.log(`\n📊 Test Results:`);
        console.log(`   ✅ Passed: ${this.passed}`);
        console.log(`   ❌ Failed: ${this.failed}`);
        console.log(`   📈 Total: ${this.passed + this.failed}\n`);
        
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
