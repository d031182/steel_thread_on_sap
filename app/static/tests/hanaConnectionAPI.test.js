/**
 * Unit Tests for HANA Connection API
 * 
 * These tests demonstrate that the API is fully testable without any UI.
 * Run with: node tests/hanaConnectionAPI.test.js (requires Node.js test runner)
 * Or use a test framework like Jest, Vitest, or Mocha
 */

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

// Test Suite
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
    
    async run() {
        console.log('\n🧪 Running HANA Connection API Tests\n');
        
        // Test 1: Create Instance
        await this.test('should create a new instance', async () => {
            const storage = new MockStorageService();
            const api = new HanaConnectionAPI(storage);
            
            const config = {
                name: 'Test Instance',
                host: 'test.hana.ondemand.com',
                port: '443',
                user: 'TEST_USER',
                schema: 'TEST_SCHEMA'
            };
            
            const instance = await api.createInstance(config);
            
            this.assert(instance.id, 'Instance should have an ID');
            this.assertEquals(instance.name, 'Test Instance', 'Instance name should match');
            this.assertEquals(instance.host, 'test.hana.ondemand.com', 'Host should match');
            this.assertEquals(instance.isDefault, true, 'First instance should be default');
        });
        
        // Test 2: Get All Instances
        await this.test('should get all instances', async () => {
            const storage = new MockStorageService();
            const api = new HanaConnectionAPI(storage);
            
            await api.createInstance({
                name: 'Instance 1',
                host: 'host1.com',
                user: 'user1'
            });
            
            await api.createInstance({
                name: 'Instance 2',
                host: 'host2.com',
                user: 'user2'
            });
            
            const instances = await api.getInstances();
            this.assertEquals(instances.length, 2, 'Should have 2 instances');
        });
        
        // Test 3: Get Instance by ID
        await this.test('should get instance by ID', async () => {
            const storage = new MockStorageService();
            const api = new HanaConnectionAPI(storage);
            
            const created = await api.createInstance({
                name: 'Test Instance',
                host: 'test.com',
                user: 'test'
            });
            
            const retrieved = await api.getInstance(created.id);
            this.assertEquals(retrieved.name, 'Test Instance', 'Retrieved instance should match');
        });
        
        // Test 4: Update Instance
        await this.test('should update an instance', async () => {
            const storage = new MockStorageService();
            const api = new HanaConnectionAPI(storage);
            
            const created = await api.createInstance({
                name: 'Original Name',
                host: 'test.com',
                user: 'test'
            });
            
            const updated = await api.updateInstance(created.id, {
                name: 'Updated Name',
                description: 'New description'
            });
            
            this.assertEquals(updated.name, 'Updated Name', 'Name should be updated');
            this.assertEquals(updated.description, 'New description', 'Description should be updated');
        });
        
        // Test 5: Delete Instance
        await this.test('should delete an instance', async () => {
            const storage = new MockStorageService();
            const api = new HanaConnectionAPI(storage);
            
            // Create two instances (so we can delete non-default)
            const instance1 = await api.createInstance({
                name: 'Instance 1',
                host: 'host1.com',
                user: 'user1'
            });
            
            const instance2 = await api.createInstance({
                name: 'Instance 2',
                host: 'host2.com',
                user: 'user2'
            });
            
            const deleted = await api.deleteInstance(instance2.id);
            this.assertEquals(deleted, true, 'Should return true when deleted');
            
            const instances = await api.getInstances();
            this.assertEquals(instances.length, 1, 'Should have 1 instance left');
        });
        
        // Test 6: Set Default Instance
        await this.test('should set default instance', async () => {
            const storage = new MockStorageService();
            const api = new HanaConnectionAPI(storage);
            
            const instance1 = await api.createInstance({
                name: 'Instance 1',
                host: 'host1.com',
                user: 'user1'
            });
            
            const instance2 = await api.createInstance({
                name: 'Instance 2',
                host: 'host2.com',
                user: 'user2'
            });
            
            await api.setDefaultInstance(instance2.id);
            
            const defaultInstance = await api.getDefaultInstance();
            this.assertEquals(defaultInstance.id, instance2.id, 'Instance 2 should be default');
        });
        
        // Test 7: Validation
        await this.test('should throw error for missing required fields', async () => {
            const storage = new MockStorageService();
            const api = new HanaConnectionAPI(storage);
            
            try {
                await api.createInstance({
                    name: 'Test'
                    // Missing host and user
                });
                throw new Error('Should have thrown validation error');
            } catch (error) {
                this.assert(
                    error.message.includes('Missing required fields'),
                    'Should throw validation error'
                );
            }
        });
        
        // Test 8: Test Connection
        await this.test('should test connection (simulated)', async () => {
            const storage = new MockStorageService();
            const api = new HanaConnectionAPI(storage);
            
            const instance = await api.createInstance({
                name: 'Test Instance',
                host: 'test.com',
                user: 'test'
            });
            
            const result = await api.testConnection(instance.id);
            this.assertEquals(result.success, true, 'Connection test should succeed');
        });
        
        // Test 9: Get Connection String
        await this.test('should generate connection string', async () => {
            const storage = new MockStorageService();
            const api = new HanaConnectionAPI(storage);
            
            const instance = await api.createInstance({
                name: 'Test Instance',
                host: 'test.hana.com',
                port: '443',
                user: 'test',
                ssl: true
            });
            
            const connStr = await api.getConnectionString(instance.id);
            this.assertEquals(connStr, 'https://test.hana.com:443', 'Connection string should be correct');
        });
        
        // Test 10: Export Instances
        await this.test('should export instances', async () => {
            const storage = new MockStorageService();
            const api = new HanaConnectionAPI(storage);
            
            await api.createInstance({
                name: 'Instance 1',
                host: 'host1.com',
                user: 'user1',
                password: 'secret'
            });
            
            const exported = await api.exportInstances(false);
            const data = JSON.parse(exported);
            
            this.assertEquals(data.length, 1, 'Should export 1 instance');
            this.assert(!data[0].password, 'Password should not be included');
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
