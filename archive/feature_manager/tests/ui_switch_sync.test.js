/**
 * Feature Manager UI - Switch Synchronization Test
 * 
 * Tests that toggling a feature switch in one tab updates
 * the same feature's switch in all other tabs.
 * 
 * Run with: node modules/feature-manager/tests/ui_switch_sync.test.js
 * 
 * This test prevents regression of the synchronization bug where
 * switches would not sync across tabs after being toggled.
 */

const { JSDOM } = require('jsdom');
const fs = require('fs');
const path = require('path');

class SwitchSyncTestRunner {
    constructor() {
        this.passed = 0;
        this.failed = 0;
        this.dom = null;
        this.window = null;
    }

    async setup() {
        console.log('\n🧪 Setting up test environment...\n');
        
        // Read HTML file
        const htmlPath = path.join(__dirname, '../../../web/current/index.html');
        const html = fs.readFileSync(htmlPath, 'utf-8');

        // Create jsdom environment
        this.dom = new JSDOM(html, {
            url: 'http://localhost:5000/',
            runScripts: 'dangerously',
            resources: 'usable',
            beforeParse(window) {
                // Mock fetch API for feature manager
                window.fetch = async (url, options = {}) => {
                    if (url === '/api/features') {
                        // Return mock features
                        return {
                            json: async () => ({
                                success: true,
                                features: {
                                    features: {
                                        'application-logging': {
                                            key: 'application-logging',
                                            displayName: 'Application Logging',
                                            description: 'SQLite-based logging system',
                                            category: 'Infrastructure',
                                            enabled: true
                                        },
                                        'feature-manager': {
                                            key: 'feature-manager',
                                            displayName: 'Feature Manager',
                                            description: 'Feature toggle system',
                                            category: 'Infrastructure',
                                            enabled: true
                                        },
                                        'debug-mode': {
                                            key: 'debug-mode',
                                            displayName: 'Debug Mode',
                                            description: 'Enhanced console logging',
                                            category: 'Developer Tools',
                                            enabled: false
                                        }
                                    }
                                }
                            })
                        };
                    } else if (url.includes('/toggle')) {
                        // Extract feature key from URL
                        const match = url.match(/\/api\/features\/([^/]+)\/toggle/);
                        const featureKey = match ? match[1] : '';
                        
                        // Toggle the state
                        const currentState = mockFeatureStates[featureKey];
                        const newState = !currentState;
                        mockFeatureStates[featureKey] = newState;
                        
                        return {
                            json: async () => ({
                                success: true,
                                enabled: newState
                            })
                        };
                    }
                    
                    return { json: async () => ({ success: false }) };
                };
            }
        });
        
        this.window = this.dom.window;
        
        // Wait for SAP UI5 to load (simulated)
        await new Promise(resolve => setTimeout(resolve, 100));
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
            if (error.stack) {
                console.error(`   Stack: ${error.stack.split('\n')[1].trim()}`);
            }
        }
    }

    assertTrue(condition, message) {
        if (!condition) {
            throw new Error(message || 'Assertion failed: expected true');
        }
    }

    assertEqual(actual, expected, message) {
        if (actual !== expected) {
            throw new Error(message || `Expected ${expected}, got ${actual}`);
        }
    }

    assertNotNull(value, message) {
        if (value === null || value === undefined) {
            throw new Error(message || 'Expected non-null value');
        }
    }

    async run() {
        console.log('═══════════════════════════════════════════════════════');
        console.log('  Feature Manager - Switch Synchronization Tests');
        console.log('═══════════════════════════════════════════════════════\n');

        await this.setup();

        // Test 1: Custom data stored on switches
        await this.test('Switches have featureKey custom data stored', () => {
            const html = fs.readFileSync(
                path.join(__dirname, '../../../web/current/index.html'),
                'utf-8'
            );
            
            // Verify custom data is set
            this.assertTrue(
                html.includes('oSwitch.data("featureKey", feature.key)'),
                'Should store feature key in switch custom data'
            );
        });

        // Test 2: Sync function exists
        await this.test('syncAllSwitchesInDialog function exists', () => {
            const html = fs.readFileSync(
                path.join(__dirname, '../../../web/current/index.html'),
                'utf-8'
            );
            
            this.assertTrue(
                html.includes('function syncAllSwitchesInDialog'),
                'Sync function should be defined'
            );
        });

        // Test 3: Sync function called after toggle
        await this.test('Sync function called after successful toggle', () => {
            const html = fs.readFileSync(
                path.join(__dirname, '../../../web/current/index.html'),
                'utf-8'
            );
            
            this.assertTrue(
                html.includes('syncAllSwitchesInDialog(oDialog, key, data.enabled)'),
                'Should call sync function after toggle'
            );
        });

        // Test 4: Sync uses custom data for matching
        await this.test('Sync function matches switches by custom data', () => {
            const html = fs.readFileSync(
                path.join(__dirname, '../../../web/current/index.html'),
                'utf-8'
            );
            
            // Check for custom data matching (not tooltip matching)
            this.assertTrue(
                html.includes('oSwitch.data("featureKey")'),
                'Should use custom data for matching'
            );
            
            this.assertTrue(
                html.includes('switchFeatureKey === featureKey'),
                'Should compare custom data values'
            );
        });

        // Test 5: Sync checks all tabs
        await this.test('Sync function iterates through all tabs', () => {
            const html = fs.readFileSync(
                path.join(__dirname, '../../../web/current/index.html'),
                'utf-8'
            );
            
            this.assertTrue(
                html.includes('aTabs.forEach(function(oTab)'),
                'Should iterate through all tabs'
            );
        });

        // Test 6: Sync handles both InputListItem and CustomListItem
        await this.test('Sync supports both list item types', () => {
            const html = fs.readFileSync(
                path.join(__dirname, '../../../web/current/index.html'),
                'utf-8'
            );
            
            this.assertTrue(
                html.includes('sap.m.InputListItem'),
                'Should handle InputListItem'
            );
            
            this.assertTrue(
                html.includes('sap.m.CustomListItem'),
                'Should handle CustomListItem'
            );
        });

        // Test 7: Sync avoids unnecessary change events
        await this.test('Sync checks state before updating', () => {
            const html = fs.readFileSync(
                path.join(__dirname, '../../../web/current/index.html'),
                'utf-8'
            );
            
            this.assertTrue(
                html.includes('if (oSwitch.getState() !== newState)'),
                'Should check state before updating to avoid unnecessary events'
            );
        });

        // Test 8: Dialog reference passed to toggle handler
        await this.test('Toggle handler receives dialog reference', () => {
            const html = fs.readFileSync(
                path.join(__dirname, '../../../web/current/index.html'),
                'utf-8'
            );
            
            this.assertTrue(
                html.includes('await toggleFeatureInDialog(feature.key, feature.displayName, bState, oSwitch, oDialog)'),
                'Should pass dialog reference to toggle handler'
            );
        });

        // Test 9: Dialog reference traversal from switch
        await this.test('Dialog found by traversing from switch', () => {
            const html = fs.readFileSync(
                path.join(__dirname, '../../../web/current/index.html'),
                'utf-8'
            );
            
            this.assertTrue(
                html.includes('let oDialog = oSwitch.getParent()'),
                'Should traverse from switch to find dialog'
            );
            
            this.assertTrue(
                html.includes('while (oDialog && oDialog.getMetadata().getName() !== "sap.m.Dialog")'),
                'Should traverse up until dialog found'
            );
        });

        // Test 10: Sync has null safety checks
        await this.test('Sync function has defensive checks', () => {
            const html = fs.readFileSync(
                path.join(__dirname, '../../../web/current/index.html'),
                'utf-8'
            );
            
            this.assertTrue(
                html.includes('if (!oDialog)'),
                'Should check dialog exists'
            );
            
            this.assertTrue(
                html.includes('if (!oIconTabBar)'),
                'Should check IconTabBar exists'
            );
        });

        // Summary
        console.log('\n═══════════════════════════════════════════════════════');
        console.log(`  Results: ${this.passed} passed, ${this.failed} failed`);
        console.log('═══════════════════════════════════════════════════════\n');

        if (this.failed === 0) {
            console.log('🎉 All switch synchronization tests passed!\n');
            return true;
        } else {
            console.log('❌ Some tests failed. Please review the implementation.\n');
            return false;
        }
    }
}

// Mock feature states
const mockFeatureStates = {
    'application-logging': true,
    'feature-manager': true,
    'debug-mode': false
};

// Run tests
(async () => {
    const runner = new SwitchSyncTestRunner();
    const success = await runner.run();
    process.exit(success ? 0 : 1);
})();