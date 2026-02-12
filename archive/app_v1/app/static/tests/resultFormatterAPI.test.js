/**
 * Unit Tests for Result Formatter API
 * 
 * These tests demonstrate that the formatting API is fully testable without any UI.
 * Run with: node tests/resultFormatterAPI.test.js
 */

import { ResultFormatterAPI } from '../js/api/resultFormatterAPI.js';

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
    
    assertContains(str, substr, message) {
        if (!str.includes(substr)) {
            throw new Error(message || `Expected "${str}" to contain "${substr}"`);
        }
    }
    
    assertDefined(value, message) {
        if (value === undefined || value === null) {
            throw new Error(message || 'Value should be defined');
        }
    }
    
    async run() {
        console.log('\n🧪 Running Result Formatter API Tests\n');
        
        // Create mock query result
        const mockResult = {
            success: true,
            queryType: 'SELECT',
            executionTime: 1234,
            rowCount: 3,
            columns: [
                { name: 'ID', type: 'INTEGER' },
                { name: 'NAME', type: 'NVARCHAR' },
                { name: 'CREATED_AT', type: 'TIMESTAMP' }
            ],
            rows: [
                [1, 'Alice', '2024-01-01T10:00:00Z'],
                [2, 'Bob', '2024-01-02T11:00:00Z'],
                [3, 'Charlie', '2024-01-03T12:00:00Z']
            ],
            timestamp: '2024-01-15T10:30:00Z'
        };
        
        // Test 1: Format as table
        await this.test('should format results as table', () => {
            const formatter = new ResultFormatterAPI();
            const formatted = formatter.formatResults(mockResult, 'table');
            
            this.assertEquals(formatted.format, 'table', 'Format should be table');
            this.assert(formatted.headers.length === 3, 'Should have 3 headers');
            this.assert(formatted.data.length === 3, 'Should have 3 data rows');
            this.assertDefined(formatted.metadata, 'Should have metadata');
        });
        
        // Test 2: Format as JSON
        await this.test('should format results as JSON', () => {
            const formatter = new ResultFormatterAPI();
            const formatted = formatter.formatResults(mockResult, 'json');
            
            this.assertEquals(formatted.format, 'json', 'Format should be json');
            this.assert(Array.isArray(formatted.data), 'Data should be array');
            this.assert(formatted.data.length === 3, 'Should have 3 objects');
            this.assertDefined(formatted.data[0].ID, 'Should have ID property');
            this.assertDefined(formatted.data[0].NAME, 'Should have NAME property');
        });
        
        // Test 3: Format as CSV
        await this.test('should format results as CSV', () => {
            const formatter = new ResultFormatterAPI();
            const formatted = formatter.formatResults(mockResult, 'csv');
            
            this.assertEquals(formatted.format, 'csv', 'Format should be csv');
            this.assert(typeof formatted.data === 'string', 'Data should be string');
            this.assertContains(formatted.data, 'ID,NAME,CREATED_AT', 'Should have headers');
            this.assertContains(formatted.data, 'Alice', 'Should have data');
        });
        
        // Test 4: Format error
        await this.test('should format error correctly', () => {
            const formatter = new ResultFormatterAPI();
            const error = {
                code: 'SYNTAX_ERROR',
                message: 'Invalid SQL syntax'
            };
            
            const formatted = formatter.formatError(error);
            
            this.assertEquals(formatted.type, 'error', 'Type should be error');
            this.assertEquals(formatted.severity, 'error', 'Severity should be error');
            this.assertContains(formatted.title, 'Syntax', 'Title should mention syntax');
            this.assertEquals(formatted.message, 'Invalid SQL syntax', 'Message should match');
            this.assert(formatted.suggestions.length > 0, 'Should have suggestions');
        });
        
        // Test 5: Format metadata
        await this.test('should format metadata correctly', () => {
            const formatter = new ResultFormatterAPI();
            const metadata = formatter.formatMetadata(mockResult);
            
            this.assertEquals(metadata.queryType, 'SELECT', 'Query type should match');
            this.assertContains(metadata.executionTime, 's', 'Execution time should be formatted');
            this.assertEquals(metadata.rowCount, '3', 'Row count should be formatted');
            this.assertEquals(metadata.columnCount, 3, 'Column count should match');
        });
        
        // Test 6: Export to CSV
        await this.test('should export array to CSV', () => {
            const formatter = new ResultFormatterAPI();
            const data = [
                { id: 1, name: 'Alice' },
                { id: 2, name: 'Bob' }
            ];
            
            const csv = formatter.exportResults(data, 'csv');
            
            this.assertContains(csv, 'id,name', 'Should have headers');
            this.assertContains(csv, '1,Alice', 'Should have first row');
            this.assertContains(csv, '2,Bob', 'Should have second row');
        });
        
        // Test 7: Export to JSON
        await this.test('should export array to JSON', () => {
            const formatter = new ResultFormatterAPI();
            const data = [
                { id: 1, name: 'Alice' },
                { id: 2, name: 'Bob' }
            ];
            
            const json = formatter.exportResults(data, 'json');
            
            this.assert(typeof json === 'string', 'Should be string');
            const parsed = JSON.parse(json);
            this.assert(Array.isArray(parsed), 'Should parse to array');
            this.assertEquals(parsed.length, 2, 'Should have 2 items');
        });
        
        // Test 8: Format execution time
        await this.test('should format execution time correctly', () => {
            const formatter = new ResultFormatterAPI();
            
            const result1 = { ...mockResult, executionTime: 500 };
            const meta1 = formatter.formatMetadata(result1);
            this.assertContains(meta1.executionTime, 'ms', 'Should format ms');
            
            const result2 = { ...mockResult, executionTime: 5000 };
            const meta2 = formatter.formatMetadata(result2);
            this.assertContains(meta2.executionTime, 's', 'Should format seconds');
            
            const result3 = { ...mockResult, executionTime: 125000 };
            const meta3 = formatter.formatMetadata(result3);
            this.assertContains(meta3.executionTime, 'm', 'Should format minutes');
        });
        
        // Test 9: Format summary
        await this.test('should format query summary', () => {
            const formatter = new ResultFormatterAPI();
            const summary = formatter.formatSummary(mockResult);
            
            this.assertContains(summary, 'Retrieved', 'Should mention retrieval');
            this.assertContains(summary, '3 row(s)', 'Should mention row count');
            this.assertContains(summary, 's', 'Should include time');
        });
        
        // Test 10: Format columns
        await this.test('should format column metadata', () => {
            const formatter = new ResultFormatterAPI();
            const columns = formatter.formatColumns(mockResult.columns);
            
            this.assertEquals(columns.length, 3, 'Should have 3 columns');
            this.assertEquals(columns[0].name, 'ID', 'First column should be ID');
            this.assertDefined(columns[0].displayType, 'Should have display type');
            this.assertDefined(columns[0].icon, 'Should have icon');
        });
        
        // Test 11: Handle CSV special characters
        await this.test('should escape CSV special characters', () => {
            const formatter = new ResultFormatterAPI();
            const data = [
                { text: 'Hello, World' },
                { text: 'Quote: "test"' },
                { text: 'Line\nbreak' }
            ];
            
            const csv = formatter.exportResults(data, 'csv');
            
            this.assertContains(csv, '"Hello, World"', 'Should quote comma');
            this.assertContains(csv, '""test""', 'Should escape quotes');
        });
        
        // Test 12: Handle NULL values
        await this.test('should handle NULL values correctly', () => {
            const formatter = new ResultFormatterAPI();
            const result = {
                ...mockResult,
                rows: [[1, null, undefined]]
            };
            
            const formatted = formatter.formatResults(result, 'table');
            const firstRow = formatted.data[0];
            
            this.assertEquals(firstRow.NAME, 'NULL', 'Should format null as NULL');
            this.assertEquals(firstRow.CREATED_AT, 'NULL', 'Should format undefined as NULL');
        });
        
        // Test 13: Error suggestions
        await this.test('should provide helpful error suggestions', () => {
            const formatter = new ResultFormatterAPI();
            
            const errors = [
                { code: 'SYNTAX_ERROR', expectedSuggestion: 'syntax' },
                { code: 'PERMISSION_DENIED', expectedSuggestion: 'privileges' },
                { code: 'QUERY_TIMEOUT', expectedSuggestion: 'WHERE' },
                { code: 'CONNECTION_ERROR', expectedSuggestion: 'running' }
            ];
            
            for (const { code, expectedSuggestion } of errors) {
                const formatted = formatter.formatError({ code, message: 'Error' });
                const hasRelevantSuggestion = formatted.suggestions.some(s => 
                    s.toLowerCase().includes(expectedSuggestion.toLowerCase())
                );
                this.assert(
                    hasRelevantSuggestion,
                    `Should have suggestion about ${expectedSuggestion} for ${code}`
                );
            }
        });
        
        // Test 14: Format failed query result
        await this.test('should format failed query result', () => {
            const formatter = new ResultFormatterAPI();
            const failedResult = {
                success: false,
                error: {
                    code: 'EXECUTION_ERROR',
                    message: 'Query failed'
                }
            };
            
            const formatted = formatter.formatResults(failedResult, 'table');
            
            this.assertEquals(formatted.type, 'error', 'Should be error type');
            this.assertDefined(formatted.message, 'Should have message');
        });
        
        // Test 15: Export to Excel format
        await this.test('should export to Excel format with BOM', () => {
            const formatter = new ResultFormatterAPI();
            const data = [{ id: 1, name: 'Test' }];
            
            const excel = formatter.exportResults(data, 'excel');
            
            this.assert(excel.charCodeAt(0) === 0xFEFF, 'Should have BOM');
            this.assertContains(excel, 'id,name', 'Should have CSV content');
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
