/**
 * Log Viewer API
 * ===============
 * Business logic for log viewing, filtering, and analysis.
 * Zero UI dependencies - can be used in Node.js, browser, or CLI.
 * 
 * @module logViewerAPI
 * @version 1.0.0
 */

export class LogViewerAPI {
    /**
     * Create a new Log Viewer API instance
     * @param {string} baseURL - Base URL for API (default: http://localhost:5000)
     */
    constructor(baseURL = 'http://localhost:5000') {
        this.baseURL = baseURL;
        this.cache = {};
        this.cacheTTL = 10000; // 10 seconds for log cache
    }

    /**
     * Get application logs with filtering
     * @param {Object} options - Query options
     * @param {string} options.level - Filter by level (INFO, WARNING, ERROR)
     * @param {number} options.limit - Number of logs to retrieve (default: 100)
     * @param {number} options.offset - Pagination offset (default: 0)
     * @param {string} options.start_date - Filter from date (ISO format)
     * @param {string} options.end_date - Filter to date (ISO format)
     * @returns {Promise<Object>} Log data with pagination info
     */
    async getLogs(options = {}) {
        const {
            level = null,
            limit = 100,
            offset = 0,
            start_date = null,
            end_date = null
        } = options;

        const params = new URLSearchParams();
        if (level) params.append('level', level);
        params.append('limit', limit);
        params.append('offset', offset);
        if (start_date) params.append('start_date', start_date);
        if (end_date) params.append('end_date', end_date);

        const url = `${this.baseURL}/api/logs?${params.toString()}`;

        try {
            const response = await fetch(url);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error?.message || 'Failed to get logs');
            }

            return data;
        } catch (error) {
            console.error('Error fetching logs:', error);
            throw error;
        }
    }

    /**
     * Get log statistics (counts by level)
     * @returns {Promise<Object>} Statistics object with counts
     */
    async getLogStats() {
        const cacheKey = 'log_stats';
        
        // Check cache
        const cached = this._getCached(cacheKey);
        if (cached) return cached;

        const url = `${this.baseURL}/api/logs/stats`;

        try {
            const response = await fetch(url);
            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error?.message || 'Failed to get log statistics');
            }

            // Cache stats
            this._setCached(cacheKey, data);

            return data;
        } catch (error) {
            console.error('Error fetching log stats:', error);
            throw error;
        }
    }

    /**
     * Clear all logs
     * @returns {Promise<Object>} Success response
     */
    async clearLogs() {
        const url = `${this.baseURL}/api/logs/clear`;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error?.message || 'Failed to clear logs');
            }

            // Clear cache
            this.clearCache();

            return data;
        } catch (error) {
            console.error('Error clearing logs:', error);
            throw error;
        }
    }

    /**
     * Get logs grouped by level
     * @param {number} limit - Logs per level (default: 20)
     * @returns {Promise<Object>} Logs grouped by level
     */
    async getLogsByLevel(limit = 20) {
        try {
            const [infoLogs, warningLogs, errorLogs] = await Promise.all([
                this.getLogs({ level: 'INFO', limit }),
                this.getLogs({ level: 'WARNING', limit }),
                this.getLogs({ level: 'ERROR', limit })
            ]);

            return {
                info: infoLogs.logs,
                warning: warningLogs.logs,
                error: errorLogs.logs,
                counts: {
                    info: infoLogs.totalCount,
                    warning: warningLogs.totalCount,
                    error: errorLogs.totalCount,
                    total: infoLogs.totalCount + warningLogs.totalCount + errorLogs.totalCount
                }
            };
        } catch (error) {
            console.error('Error fetching logs by level:', error);
            throw error;
        }
    }

    /**
     * Get recent errors (last N errors)
     * @param {number} limit - Number of errors to retrieve (default: 10)
     * @returns {Promise<Array>} Recent error logs
     */
    async getRecentErrors(limit = 10) {
        try {
            const result = await this.getLogs({ level: 'ERROR', limit });
            return result.logs;
        } catch (error) {
            console.error('Error fetching recent errors:', error);
            throw error;
        }
    }

    /**
     * Search logs by message content
     * @param {string} searchTerm - Search term to find in log messages
     * @param {Object} options - Additional filter options
     * @returns {Promise<Array>} Matching logs
     */
    async searchLogs(searchTerm, options = {}) {
        try {
            const result = await this.getLogs({
                ...options,
                limit: options.limit || 100
            });

            // Client-side filtering by search term
            const filtered = result.logs.filter(log =>
                log.message.toLowerCase().includes(searchTerm.toLowerCase())
            );

            return {
                logs: filtered,
                count: filtered.length,
                totalCount: result.totalCount,
                searchTerm
            };
        } catch (error) {
            console.error('Error searching logs:', error);
            throw error;
        }
    }

    /**
     * Get logs for a specific time range
     * @param {Date} startDate - Start date
     * @param {Date} endDate - End date
     * @param {Object} options - Additional options
     * @returns {Promise<Object>} Logs in time range
     */
    async getLogsByTimeRange(startDate, endDate, options = {}) {
        try {
            return await this.getLogs({
                ...options,
                start_date: startDate.toISOString(),
                end_date: endDate.toISOString()
            });
        } catch (error) {
            console.error('Error fetching logs by time range:', error);
            throw error;
        }
    }

    /**
     * Export logs to specified format
     * @param {string} format - Export format (csv, json)
     * @param {Object} filters - Filter options
     * @returns {Promise<Blob>} Exported data
     */
    async exportLogs(format = 'csv', filters = {}) {
        try {
            // Get all matching logs (no limit for export)
            const result = await this.getLogs({
                ...filters,
                limit: 10000 // Max export size
            });

            if (format === 'csv') {
                return this._exportToCSV(result.logs);
            } else if (format === 'json') {
                return this._exportToJSON(result.logs);
            } else {
                throw new Error(`Unsupported export format: ${format}`);
            }
        } catch (error) {
            console.error('Error exporting logs:', error);
            throw error;
        }
    }

    /**
     * Test backend connection
     * @returns {Promise<boolean>} Connection status
     */
    async testConnection() {
        try {
            const response = await fetch(`${this.baseURL}/api/health`);
            const data = await response.json();
            return data.status === 'healthy';
        } catch (error) {
            return false;
        }
    }

    // Private methods

    /**
     * Export logs to CSV format
     * @private
     */
    _exportToCSV(logs) {
        if (!logs || logs.length === 0) {
            throw new Error('No logs to export');
        }

        // CSV header
        const headers = ['ID', 'Timestamp', 'Level', 'Logger', 'Message'];
        let csv = headers.join(',') + '\n';

        // CSV rows
        logs.forEach(log => {
            const row = [
                log.id,
                log.timestamp,
                log.level,
                log.logger,
                `"${log.message.replace(/"/g, '""')}"` // Escape quotes
            ];
            csv += row.join(',') + '\n';
        });

        // Create Blob with UTF-8 BOM for Excel compatibility
        const BOM = '\uFEFF';
        return new Blob([BOM + csv], { type: 'text/csv;charset=utf-8;' });
    }

    /**
     * Export logs to JSON format
     * @private
     */
    _exportToJSON(logs) {
        const json = JSON.stringify(logs, null, 2);
        return new Blob([json], { type: 'application/json' });
    }

    /**
     * Trigger browser download
     * @private
     */
    triggerDownload(blob, filename) {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
    }

    /**
     * Check if cached data is still valid
     * @private
     */
    _isCacheValid(key) {
        const cached = this.cache[key];
        if (!cached) return false;
        return Date.now() - cached.timestamp < this.cacheTTL;
    }

    /**
     * Get cached data if valid
     * @private
     */
    _getCached(key) {
        if (this._isCacheValid(key)) {
            return this.cache[key].data;
        }
        return null;
    }

    /**
     * Store data in cache
     * @private
     */
    _setCached(key, data) {
        this.cache[key] = {
            data,
            timestamp: Date.now()
        };
    }

    /**
     * Clear all cached data
     */
    clearCache() {
        this.cache = {};
    }

    /**
     * Get cache statistics
     * @returns {Object} Cache stats
     */
    getCacheStats() {
        const keys = Object.keys(this.cache);
        return {
            size: keys.length,
            keys: keys,
            ttl: this.cacheTTL
        };
    }

    /**
     * Format timestamp for display
     * @param {string} timestamp - ISO timestamp string
     * @returns {string} Formatted timestamp
     */
    formatTimestamp(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleString();
        } catch (error) {
            return timestamp;
        }
    }

    /**
     * Format log level with color info
     * @param {string} level - Log level (INFO, WARNING, ERROR)
     * @returns {Object} Format info with color and icon
     */
    formatLogLevel(level) {
        const formats = {
            'INFO': { color: '#0070f2', icon: 'ℹ️', label: 'INFO', state: 'Information' },
            'WARNING': { color: '#e9730c', icon: '⚠️', label: 'WARNING', state: 'Warning' },
            'ERROR': { color: '#b00', icon: '❌', label: 'ERROR', state: 'Error' }
        };
        return formats[level] || { color: '#666', icon: '●', label: level, state: 'None' };
    }
}

// Export for use in browser and Node.js
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { LogViewerAPI };
}
