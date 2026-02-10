/**
 * Unit Tests for Debug Logger Service
 * 
 * Tests the debug logging utility that provides conditional
 * logging for troubleshooting purposes.
 * 
 * Run with: node web/current/tests/debugLogger.test.js
 */

import { DebugLogger } from '../js/utils/debugLogger.js';

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
            console.error(`   ${error.message}`);
            this.tests.push({ name, status: 'failed', error: error.message });
        }
    }
    
    assertEquals(actual, expected, message) {
        if (actual !== expected) {
            throw new Error(`${message}\n  Expected: ${expected}\n  Actual: ${actual}`);
        }
    }
    
    assertTrue(condition, message) {
        if (!condition) {
            throw new Error(message);
        }
    }
    
    assertFalse(condition, message) {
        if (condition) {
            throw new Error(message);
        }
    }
    
    summary() {
        console.log('\n' + '='.repeat(50));
        console.log('Test Summary');
        console.log('='.repeat(50));
        console.log(`Total: ${this.tests.length}`);
        console.log(`Passed: ${this.passed} ✅`);
        console.log(`Failed: ${this.failed} ❌`);
        console.log(`Success Rate: ${((this.passed / this.tests.length) * 100).toFixed(1)}%`);
        console.log('='.repeat(50));
        return this.failed === 0;
    }
}

// Mock localStorage for Node.js environment
class MockLocalStorage {
    constructor() {
        this.data = new Map();
    }
    
    getItem(key) {
        return this.data.get(key) || null;
    }
    
    setItem(key, value) {
        this.data.set(key, value);
    }
    
    clear() {
        this.data.clear();
    }
}

// Mock console for testing
class MockConsole {
    constructor() {
        this.logs = [];
    }
    
    log(...args) {
        this.logs.push({ type: 'log', args });
    }
    
    error(...args) {
        this.logs.push({ type: 'error', args });
    }
    
    group(...args) {
        this.logs.push({ type: 'group', args });
    }
    
    groupEnd() {
        this.logs.push({ type: 'groupEnd' });
    }
    
    table(...args) {
        this.logs.push({ type: 'table', args });
    }
    
    clear() {
        this.logs = [];
    }
    
    getLastLog() {
        return this.logs[this.logs.length - 1];
    }
    
    hasLogWithText(text) {
        return this.logs.some(log => 
            log.args && log.args.some(arg => 
                typeof arg === 'string' && arg.includes(text)
            )
        );
    }
}

// Test Suite
async function runTests() {
    const runner = new TestRunner();
    
    console.log('Debug Logger Service - Unit Tests');
    console.log('='.repeat(50));
    console.log('Testing conditional debug logging utility\n');
    
    // Set up mocks
    global.localStorage = new MockLocalStorage();
    const originalConsole = global.console;
    
    // Test 1: Singleton pattern
    await runner.test('Should return same instance (singleton)', () => {
        const instance1 = DebugLogger.getInstance();
        const instance2 = DebugLogger.getInstance();
        runner.assertTrue(instance1 === instance2, 'Should return same instance');
    });
    
    // Test 2: Initial state (disabled by default)
    await runner.test('Should be disabled by default', () => {
        global.localStorage.clear();
        const logger = new DebugLogger();
        runner.assertFalse(logger.isEnabled(), 'Should be disabled initially');
    });
    
    // Test 3: Enable functionality
    await runner.test('Should enable debug mode', () => {
        global.localStorage.clear();
        global.console = new MockConsole();
        const logger = new DebugLogger();
        
        logger.enable();
        
        runner.assertTrue(logger.isEnabled(), 'Should be enabled');
        runner.assertEquals(
            global.localStorage.getItem('debugMode'),
            'true',
            'Should persist to localStorage'
        );
        runner.assertTrue(
            global.console.hasLogWithText('Debug Mode ENABLED'),
            'Should log enable message'
        );
        
        global.console = originalConsole;
    });
    
    // Test 4: Disable functionality
    await runner.test('Should disable debug mode', () => {
        global.localStorage.clear();
        global.console = new MockConsole();
        const logger = new DebugLogger();
        
        logger.enable();
        logger.disable();
        
        runner.assertFalse(logger.isEnabled(), 'Should be disabled');
        runner.assertEquals(
            global.localStorage.getItem('debugMode'),
            'false',
            'Should persist to localStorage'
        );
        runner.assertTrue(
            global.console.hasLogWithText('Debug Mode DISABLED'),
            'Should log disable message'
        );
        
        global.console = originalConsole;
    });
    
    // Test 5: Toggle functionality
    await runner.test('Should toggle debug mode', () => {
        global.localStorage.clear();
        global.console = new MockConsole();
        const logger = new DebugLogger();
        
        const initialState = logger.isEnabled();
        const newState = logger.toggle();
        
        runner.assertEquals(newState, !initialState, 'Should toggle to opposite state');
        runner.assertEquals(logger.isEnabled(), newState, 'Should update internal state');
        
        global.console = originalConsole;
    });
    
    // Test 6: localStorage persistence
    await runner.test('Should restore state from localStorage', () => {
        global.localStorage.clear();
        global.localStorage.setItem('debugMode', 'true');
        
        const logger = new DebugLogger();
        runner.assertTrue(logger.isEnabled(), 'Should restore enabled state from localStorage');
        
        global.localStorage.setItem('debugMode', 'false');
        const logger2 = new DebugLogger();
        runner.assertFalse(logger2.isEnabled(), 'Should restore disabled state from localStorage');
    });
    
    // Test 7: Conditional logging (disabled)
    await runner.test('Should NOT log when disabled', () => {
        global.localStorage.clear();
        global.console = new MockConsole();
        const logger = new DebugLogger();
        
        logger.disable();
        logger.log('Test message', { data: 'test' });
        
        // Should only have disable message, not the test log
        runner.assertFalse(
            global.console.hasLogWithText('Test message'),
            'Should not log when disabled'
        );
        
        global.console = originalConsole;
    });
    
    // Test 8: Conditional logging (enabled)
    await runner.test('Should log when enabled', () => {
        global.localStorage.clear();
        global.console = new MockConsole();
        const logger = new DebugLogger();
        
        logger.enable();
        global.console.clear(); // Clear enable message
        logger.log('Test message', { data: 'test' });
        
        runner.assertTrue(
            global.console.hasLogWithText('Test message'),
            'Should log when enabled'
        );
        
        global.console = originalConsole;
    });
    
    // Test 9: Entry/exit logging
    await runner.test('Should log function entry and exit with timing', () => {
        global.localStorage.clear();
        global.console = new MockConsole();
        const logger = new DebugLogger();
        
        logger.enable();
        global.console.clear();
        
        const startTime = logger.entry('testFunction', { param1: 'value1' });
        runner.assertTrue(typeof startTime === 'number', 'Should return start time');
        runner.assertTrue(
            global.console.hasLogWithText('ENTRY: testFunction'),
            'Should log entry'
        );
        
        // Simulate work
        const workStart = Date.now();
        while (Date.now() - workStart < 10) {} // Wait ~10ms
        
        logger.exit('testFunction', { result: 'success' }, startTime);
        runner.assertTrue(
            global.console.hasLogWithText('EXIT: testFunction'),
            'Should log exit'
        );
        runner.assertTrue(
            global.console.hasLogWithText('Duration:'),
            'Should log duration'
        );
        
        global.console = originalConsole;
    });
    
    // Test 10: Error logging
    await runner.test('Should log errors with stack traces', () => {
        global.localStorage.clear();
        global.console = new MockConsole();
        const logger = new DebugLogger();
        
        logger.enable();
        global.console.clear();
        
        const testError = new Error('Test error message');
        logger.error('testFunction', testError);
        
        runner.assertTrue(
            global.console.hasLogWithText('ERROR in testFunction'),
            'Should log error function name'
        );
        runner.assertTrue(
            global.console.hasLogWithText('Test error message'),
            'Should log error message'
        );
        
        global.console = originalConsole;
    });
    
    // Test 11: Performance timing
    await runner.test('Should measure and log performance timing', () => {
        global.localStorage.clear();
        global.console = new MockConsole();
        const logger = new DebugLogger();
        
        logger.enable();
        global.console.clear();
        
        const startTime = logger.startTimer();
        runner.assertTrue(typeof startTime === 'number', 'Should return start time');
        
        // Simulate work
        const workStart = Date.now();
        while (Date.now() - workStart < 10) {} // Wait ~10ms
        
        logger.endTimer('Test operation', startTime);
        runner.assertTrue(
            global.console.hasLogWithText('Test operation:'),
            'Should log timer label'
        );
        runner.assertTrue(
            global.console.hasLogWithText('ms'),
            'Should log duration in ms'
        );
        
        global.console = originalConsole;
    });
    
    // Test 12: Object inspection
    await runner.test('Should inspect objects and log details', () => {
        global.localStorage.clear();
        global.console = new MockConsole();
        const logger = new DebugLogger();
        
        logger.enable();
        global.console.clear();
        
        const testObj = { name: 'test', value: 123 };
        logger.inspect('Test Object', testObj);
        
        runner.assertTrue(
            global.console.hasLogWithText('Inspecting: Test Object'),
            'Should log inspection label'
        );
        runner.assertTrue(
            global.console.logs.some(log => log.type === 'table'),
            'Should use console.table'
        );
        
        global.console = originalConsole;
    });
    
    // Test 13: Table logging
    await runner.test('Should log data in table format', () => {
        global.localStorage.clear();
        global.console = new MockConsole();
        const logger = new DebugLogger();
        
        logger.enable();
        global.console.clear();
        
        const testData = [
            { id: 1, name: 'Item 1' },
            { id: 2, name: 'Item 2' }
        ];
        logger.table('Test Data', testData);
        
        runner.assertTrue(
            global.console.hasLogWithText('Test Data'),
            'Should log table label'
        );
        runner.assertTrue(
            global.console.logs.some(log => log.type === 'table'),
            'Should use console.table'
        );
        
        global.console = originalConsole;
    });
    
    // Test 14: Group logging
    await runner.test('Should support grouped logs', () => {
        global.localStorage.clear();
        global.console = new MockConsole();
        const logger = new DebugLogger();
        
        logger.enable();
        global.console.clear();
        
        logger.group('Test Group');
        runner.assertTrue(
            global.console.logs.some(log => log.type === 'group'),
            'Should create log group'
        );
        
        logger.groupEnd();
        runner.assertTrue(
            global.console.logs.some(log => log.type === 'groupEnd'),
            'Should end log group'
        );
        
        global.console = originalConsole;
    });
    
    // Test 15: No-op when disabled
    await runner.test('Should be no-op for all methods when disabled', () => {
        global.localStorage.clear();
        global.console = new MockConsole();
        const logger = new DebugLogger();
        
        logger.disable();
        global.console.clear();
        
        // Try all logging methods
        logger.log('message');
        logger.entry('func');
        logger.exit('func');
        logger.error('func', new Error('test'));
        logger.endTimer('timer', Date.now());
        logger.inspect('obj', {});
        logger.table('data', []);
        logger.group('group');
        logger.groupEnd();
        
        // Should have no logs (all disabled)
        runner.assertEquals(
            global.console.logs.length,
            0,
            'Should not log anything when disabled'
        );
        
        global.console = originalConsole;
    });
    
    return runner.summary();
}

// Run tests
runTests().then(success => {
    process.exit(success ? 0 : 1);
}).catch(error => {
    console.error('Test suite error:', error);
    process.exit(1);
});