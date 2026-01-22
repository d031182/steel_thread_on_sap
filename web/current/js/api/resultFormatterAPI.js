/**
 * Result Formatter API
 * 
 * Provides formatting and export capabilities for SQL query results.
 * This API is UI-independent and fully testable.
 * 
 * @module api/resultFormatterAPI
 */

export class ResultFormatterAPI {
    /**
     * Create Result Formatter API
     */
    constructor() {
        // No dependencies needed
    }

    /**
     * Format query results for display
     * @param {Object} rawResult - Raw query result from SQLExecutionAPI
     * @param {string} [format='table'] - Output format: 'table', 'json', 'csv'
     * @returns {Object} Formatted result
     */
    formatResults(rawResult, format = 'table') {
        if (!rawResult) {
            throw new Error('Raw result is required');
        }

        if (!rawResult.success) {
            return this.formatError(rawResult.error);
        }

        switch (format.toLowerCase()) {
            case 'table':
                return this._formatAsTable(rawResult);
            case 'json':
                return this._formatAsJSON(rawResult);
            case 'csv':
                return this._formatAsCSV(rawResult);
            default:
                throw new Error(`Unsupported format: ${format}`);
        }
    }

    /**
     * Format error for display
     * @param {Object} error - Error object
     * @returns {Object} Formatted error
     */
    formatError(error) {
        if (!error) {
            return {
                type: 'error',
                severity: 'error',
                title: 'Unknown Error',
                message: 'An unknown error occurred',
                details: null
            };
        }

        return {
            type: 'error',
            severity: this._determineSeverity(error),
            title: this._getErrorTitle(error),
            message: error.message || 'An error occurred',
            code: error.code || 'UNKNOWN_ERROR',
            details: error.details || null,
            suggestions: this._getSuggestions(error)
        };
    }

    /**
     * Format metadata for display
     * @param {Object} result - Query result with metadata
     * @returns {Object} Formatted metadata
     */
    formatMetadata(result) {
        if (!result) {
            return {};
        }

        return {
            queryType: result.queryType || 'UNKNOWN',
            executionTime: this._formatExecutionTime(result.executionTime),
            rowCount: this._formatRowCount(result.rowCount),
            columnCount: result.columns ? result.columns.length : 0,
            timestamp: this._formatTimestamp(result.timestamp),
            instanceInfo: result.instanceId ? { instanceId: result.instanceId } : null,
            additionalMetadata: result.metadata || {}
        };
    }

    /**
     * Export results to specified format
     * @param {Array} data - Array of result objects
     * @param {string} format - Export format: 'csv', 'json', 'excel'
     * @returns {string|Blob} Exported data
     */
    exportResults(data, format) {
        if (!Array.isArray(data)) {
            throw new Error('Data must be an array');
        }

        if (data.length === 0) {
            throw new Error('No data to export');
        }

        switch (format.toLowerCase()) {
            case 'csv':
                return this._exportToCSV(data);
            case 'json':
                return this._exportToJSON(data);
            case 'excel':
                return this._exportToExcel(data);
            default:
                throw new Error(`Unsupported export format: ${format}`);
        }
    }

    /**
     * Format as table structure
     * @private
     */
    _formatAsTable(result) {
        const headers = result.columns.map(col => ({
            key: col.name,
            label: col.name,
            type: col.type,
            sortable: true,
            filterable: true
        }));

        const data = result.rows.map((row, index) => {
            const rowObj = { _index: index + 1 };
            result.columns.forEach((col, colIndex) => {
                rowObj[col.name] = this._formatValue(row[colIndex], col.type);
            });
            return rowObj;
        });

        return {
            format: 'table',
            headers,
            data,
            totalRows: result.rowCount,
            metadata: this.formatMetadata(result)
        };
    }

    /**
     * Format as JSON
     * @private
     */
    _formatAsJSON(result) {
        const data = result.rows.map(row => {
            const obj = {};
            result.columns.forEach((col, index) => {
                obj[col.name] = row[index];
            });
            return obj;
        });

        return {
            format: 'json',
            data,
            metadata: this.formatMetadata(result)
        };
    }

    /**
     * Format as CSV
     * @private
     */
    _formatAsCSV(result) {
        const headers = result.columns.map(col => col.name).join(',');
        const rows = result.rows.map(row => 
            row.map(cell => this._escapeCsvValue(cell)).join(',')
        );

        return {
            format: 'csv',
            data: [headers, ...rows].join('\n'),
            metadata: this.formatMetadata(result)
        };
    }

    /**
     * Export to CSV format
     * @private
     */
    _exportToCSV(data) {
        if (data.length === 0) {
            return '';
        }

        // Get headers from first object
        const headers = Object.keys(data[0]);
        const headerRow = headers.join(',');

        // Convert data rows
        const dataRows = data.map(obj => 
            headers.map(header => this._escapeCsvValue(obj[header])).join(',')
        );

        return [headerRow, ...dataRows].join('\n');
    }

    /**
     * Export to JSON format
     * @private
     */
    _exportToJSON(data) {
        return JSON.stringify(data, null, 2);
    }

    /**
     * Export to Excel format (CSV with BOM for Excel)
     * @private
     */
    _exportToExcel(data) {
        const csv = this._exportToCSV(data);
        // Add BOM for Excel UTF-8 support
        return '\uFEFF' + csv;
    }

    /**
     * Format execution time
     * @private
     */
    _formatExecutionTime(ms) {
        if (!ms && ms !== 0) return 'N/A';
        
        if (ms < 1000) {
            return `${ms}ms`;
        } else if (ms < 60000) {
            return `${(ms / 1000).toFixed(2)}s`;
        } else {
            const minutes = Math.floor(ms / 60000);
            const seconds = ((ms % 60000) / 1000).toFixed(0);
            return `${minutes}m ${seconds}s`;
        }
    }

    /**
     * Format row count
     * @private
     */
    _formatRowCount(count) {
        if (!count && count !== 0) return 'N/A';
        
        if (count < 1000) {
            return count.toString();
        } else if (count < 1000000) {
            return `${(count / 1000).toFixed(1)}K`;
        } else {
            return `${(count / 1000000).toFixed(1)}M`;
        }
    }

    /**
     * Format timestamp
     * @private
     */
    _formatTimestamp(timestamp) {
        if (!timestamp) return 'N/A';
        
        try {
            const date = new Date(timestamp);
            return date.toLocaleString();
        } catch (error) {
            return timestamp;
        }
    }

    /**
     * Format value based on type
     * @private
     */
    _formatValue(value, type) {
        if (value === null || value === undefined) {
            return 'NULL';
        }

        if (type && type.includes('DATE') || type && type.includes('TIME')) {
            try {
                const date = new Date(value);
                if (!isNaN(date.getTime())) {
                    return date.toLocaleString();
                }
            } catch (error) {
                // Fall through to return as-is
            }
        }

        if (typeof value === 'number') {
            // Format numbers with appropriate precision
            if (type && (type.includes('DECIMAL') || type.includes('FLOAT'))) {
                return value.toFixed(2);
            }
            return value.toString();
        }

        return value.toString();
    }

    /**
     * Escape CSV value
     * @private
     */
    _escapeCsvValue(value) {
        if (value === null || value === undefined) {
            return '';
        }

        const stringValue = value.toString();
        
        // If contains comma, quote, or newline, wrap in quotes and escape quotes
        if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
            return `"${stringValue.replace(/"/g, '""')}"`;
        }

        return stringValue;
    }

    /**
     * Determine error severity
     * @private
     */
    _determineSeverity(error) {
        if (!error.code) return 'error';

        const code = error.code.toUpperCase();
        
        if (code.includes('WARN')) return 'warning';
        if (code.includes('INFO')) return 'information';
        if (code.includes('SYNTAX')) return 'error';
        if (code.includes('PERMISSION')) return 'error';
        if (code.includes('TIMEOUT')) return 'warning';
        
        return 'error';
    }

    /**
     * Get error title
     * @private
     */
    _getErrorTitle(error) {
        if (!error.code) return 'Query Error';

        const code = error.code.toUpperCase();
        
        if (code.includes('SYNTAX')) return 'SQL Syntax Error';
        if (code.includes('PERMISSION')) return 'Permission Denied';
        if (code.includes('TIMEOUT')) return 'Query Timeout';
        if (code.includes('CONNECTION')) return 'Connection Error';
        if (code.includes('EXECUTION')) return 'Execution Error';
        
        return 'Query Error';
    }

    /**
     * Get error suggestions
     * @private
     */
    _getSuggestions(error) {
        if (!error.code) return [];

        const code = error.code.toUpperCase();
        const suggestions = [];
        
        if (code.includes('SYNTAX')) {
            suggestions.push('Check your SQL syntax');
            suggestions.push('Verify table and column names');
            suggestions.push('Ensure keywords are spelled correctly');
        }
        
        if (code.includes('PERMISSION')) {
            suggestions.push('Check user privileges');
            suggestions.push('Contact database administrator');
            suggestions.push('Verify schema access');
        }
        
        if (code.includes('TIMEOUT')) {
            suggestions.push('Try adding WHERE clause to limit results');
            suggestions.push('Consider adding indexes');
            suggestions.push('Break query into smaller parts');
        }
        
        if (code.includes('CONNECTION')) {
            suggestions.push('Verify instance is running');
            suggestions.push('Check network connectivity');
            suggestions.push('Test connection in HANA Connection tab');
        }
        
        return suggestions;
    }

    /**
     * Create download link for export
     * @param {string} content - Content to download
     * @param {string} filename - Filename
     * @param {string} mimeType - MIME type
     * @returns {string} Data URL
     */
    createDownloadLink(content, filename, mimeType) {
        const blob = new Blob([content], { type: mimeType });
        return URL.createObjectURL(blob);
    }

    /**
     * Trigger browser download
     * @param {string} content - Content to download
     * @param {string} filename - Filename
     * @param {string} mimeType - MIME type
     */
    triggerDownload(content, filename, mimeType) {
        const url = this.createDownloadLink(content, filename, mimeType);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }

    /**
     * Format results summary
     * @param {Object} result - Query result
     * @returns {string} Human-readable summary
     */
    formatSummary(result) {
        if (!result.success) {
            return `Query failed: ${result.error.message}`;
        }

        const parts = [];
        
        if (result.queryType === 'SELECT') {
            parts.push(`Retrieved ${result.rowCount} row(s)`);
        } else if (result.queryType === 'INSERT') {
            parts.push(`Inserted ${result.rowCount} row(s)`);
        } else if (result.queryType === 'UPDATE') {
            parts.push(`Updated ${result.rowCount} row(s)`);
        } else if (result.queryType === 'DELETE') {
            parts.push(`Deleted ${result.rowCount} row(s)`);
        } else {
            parts.push(`${result.queryType} executed successfully`);
        }

        parts.push(`in ${this._formatExecutionTime(result.executionTime)}`);

        return parts.join(' ');
    }

    /**
     * Format column metadata for display
     * @param {Array} columns - Column metadata array
     * @returns {Array} Formatted column info
     */
    formatColumns(columns) {
        if (!Array.isArray(columns)) {
            return [];
        }

        return columns.map(col => ({
            name: col.name,
            type: col.type,
            displayType: this._getDisplayType(col.type),
            length: col.length,
            nullable: col.nullable !== false,
            icon: this._getTypeIcon(col.type)
        }));
    }

    /**
     * Get display type name
     * @private
     */
    _getDisplayType(type) {
        if (!type) return 'Unknown';
        
        const typeUpper = type.toUpperCase();
        
        if (typeUpper.includes('VARCHAR') || typeUpper.includes('CHAR')) {
            return 'Text';
        }
        if (typeUpper.includes('INT')) {
            return 'Integer';
        }
        if (typeUpper.includes('DECIMAL') || typeUpper.includes('NUMERIC')) {
            return 'Number';
        }
        if (typeUpper.includes('DATE')) {
            return 'Date';
        }
        if (typeUpper.includes('TIME')) {
            return 'DateTime';
        }
        if (typeUpper.includes('BOOL')) {
            return 'Boolean';
        }
        
        return type;
    }

    /**
     * Get type icon
     * @private
     */
    _getTypeIcon(type) {
        if (!type) return '📝';
        
        const typeUpper = type.toUpperCase();
        
        if (typeUpper.includes('VARCHAR') || typeUpper.includes('CHAR')) {
            return '📝';
        }
        if (typeUpper.includes('INT') || typeUpper.includes('NUMERIC')) {
            return '🔢';
        }
        if (typeUpper.includes('DATE') || typeUpper.includes('TIME')) {
            return '📅';
        }
        if (typeUpper.includes('BOOL')) {
            return '☑️';
        }
        
        return '📊';
    }
}

// Default instance
export const resultFormatterAPI = new ResultFormatterAPI();
