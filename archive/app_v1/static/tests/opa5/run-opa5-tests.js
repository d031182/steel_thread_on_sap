#!/usr/bin/env node

/**
 * OPA5 Test Runner (Headless)
 * Runs SAP UI5 OPA5 tests in headless browser using Playwright
 */

const { chromium } = require('@playwright/test');
const path = require('path');

async function runOPA5Tests() {
    console.log('🧪 Running OPA5 Tests (Headless)...\n');
    
    const browser = await chromium.launch();
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Track test results
    const results = {
        passed: 0,
        failed: 0,
        total: 0,
        failures: []
    };
    
    // Listen for console messages from QUnit
    page.on('console', msg => {
        const text = msg.text();
        if (text.includes('✓') || text.includes('passed')) {
            console.log(`  ${text}`);
        } else if (text.includes('✗') || text.includes('failed')) {
            console.error(`  ${text}`);
        }
    });
    
    try {
        // Navigate to OPA5 test page
        const testUrl = `file://${path.resolve(__dirname, 'dataProductsPage.opa5.test.html')}`;
        console.log(`Loading: ${testUrl}\n`);
        
        await page.goto(testUrl, { waitUntil: 'networkidle' });
        
        // Wait for QUnit to finish (check for #qunit-testresult)
        await page.waitForFunction(
            () => {
                const testResult = document.querySelector('#qunit-testresult');
                return testResult && testResult.textContent.includes('completed');
            },
            { timeout: 60000 }
        );
        
        // Extract results
        const qunitResults = await page.evaluate(() => {
            const resultElement = document.querySelector('#qunit-testresult');
            const tests = document.querySelectorAll('#qunit-tests > li');
            
            const failures = [];
            tests.forEach(test => {
                if (test.className.includes('fail')) {
                    const name = test.querySelector('.test-name')?.textContent || 'Unknown';
                    const message = test.querySelector('.fail')?.textContent || 'No details';
                    failures.push({ name, message });
                }
            });
            
            return {
                text: resultElement ? resultElement.textContent : '',
                failures
            };
        });
        
        // Parse results
        const match = qunitResults.text.match(/(\d+) tests? completed in (\d+) milliseconds.*?(\d+) passed, (\d+) failed/);
        if (match) {
            results.total = parseInt(match[1]);
            results.passed = parseInt(match[3]);
            results.failed = parseInt(match[4]);
            results.failures = qunitResults.failures;
        }
        
        console.log('\n' + '='.repeat(60));
        console.log('OPA5 TEST RESULTS');
        console.log('='.repeat(60));
        console.log(`Total:  ${results.total}`);
        console.log(`Passed: ${results.passed} ✓`);
        console.log(`Failed: ${results.failed}${results.failed > 0 ? ' ✗' : ''}`);
        
        if (results.failures.length > 0) {
            console.log('\nFailed Tests:');
            results.failures.forEach(failure => {
                console.log(`\n  ✗ ${failure.name}`);
                console.log(`    ${failure.message}`);
            });
        }
        
        console.log('='.repeat(60) + '\n');
        
    } catch (error) {
        console.error('Error running OPA5 tests:', error);
        results.failed++;
    } finally {
        await browser.close();
    }
    
    // Exit with appropriate code
    process.exit(results.failed > 0 ? 1 : 0);
}

// Run tests
runOPA5Tests().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
});