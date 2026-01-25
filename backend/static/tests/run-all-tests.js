/**
 * Master Test Runner
 * 
 * Runs all test suites and provides combined results.
 * Run with: node tests/run-all-tests.js
 */

import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

class MasterTestRunner {
    constructor() {
        this.testFiles = [
            'hanaConnectionAPI.test.js',
            'sqlExecutionAPI.test.js',
            'resultFormatterAPI.test.js'
        ];
        this.results = [];
    }

    async runTest(testFile) {
        return new Promise((resolve) => {
            console.log(`\n${'='.repeat(60)}`);
            console.log(`Running: ${testFile}`);
            console.log('='.repeat(60));

            const testPath = join(__dirname, testFile);
            const child = spawn('node', [testPath], {
                stdio: 'inherit',
                shell: true
            });

            child.on('close', (code) => {
                resolve({
                    file: testFile,
                    success: code === 0
                });
            });

            child.on('error', (error) => {
                console.error(`Error running ${testFile}:`, error);
                resolve({
                    file: testFile,
                    success: false,
                    error: error.message
                });
            });
        });
    }

    async runAll() {
        console.log('\n🧪 MASTER TEST RUNNER');
        console.log('='.repeat(60));
        console.log(`Running ${this.testFiles.length} test suites...\n`);

        for (const testFile of this.testFiles) {
            const result = await this.runTest(testFile);
            this.results.push(result);
        }

        // Print summary
        this.printSummary();

        // Return exit code
        return this.results.every(r => r.success) ? 0 : 1;
    }

    printSummary() {
        console.log('\n' + '='.repeat(60));
        console.log('📊 OVERALL TEST RESULTS');
        console.log('='.repeat(60));

        const passed = this.results.filter(r => r.success).length;
        const failed = this.results.filter(r => !r.success).length;

        console.log('\nTest Suites:');
        this.results.forEach(result => {
            const status = result.success ? '✅' : '❌';
            console.log(`   ${status} ${result.file}`);
        });

        console.log('\nSummary:');
        console.log(`   ✅ Passed: ${passed} suite(s)`);
        console.log(`   ❌ Failed: ${failed} suite(s)`);
        console.log(`   📈 Total: ${this.results.length} suite(s)`);

        if (failed === 0) {
            console.log('\n🎉 ALL TESTS PASSED!');
        } else {
            console.log('\n⚠️  SOME TESTS FAILED');
        }

        console.log('='.repeat(60) + '\n');
    }
}

// Run all tests
const runner = new MasterTestRunner();
runner.runAll().then(exitCode => {
    process.exit(exitCode);
}).catch(error => {
    console.error('Master test runner error:', error);
    process.exit(1);
});
