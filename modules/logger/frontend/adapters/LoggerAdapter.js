/**
 * Logger Adapter
 * ==============
 * API client for the Logger module backend endpoints.
 * 
 * @module LoggerAdapter
 */

/**
 * Logger API Client
 * 
 * Handles communication with the Logger backend API.
 */
class LoggerAdapter {
    constructor() {
        this.baseUrl = '/api/logger';
    }
    
    /**
     * Get current logging mode
     * 
     * @returns {Promise<Object>} Response with mode data
     * @example
     * const response = await adapter.getMode();
     * // { status: 'success', data: { mode: 'default', ... } }
     */
    async getMode() {
        try {
            const response = await fetch(`${this.baseUrl}/mode`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to get logging mode:', error);
            throw error;
        }
    }
    
    /**
     * Set logging mode
     * 
     * @param {string} mode - Mode to set ('default' or 'flight_recorder')
     * @returns {Promise<Object>} Response with updated mode data
     * @example
     * const response = await adapter.setMode('flight_recorder');
     * // { status: 'success', message: '...', data: { mode: 'flight_recorder', ... } }
     */
    async setMode(mode) {
        try {
            const response = await fetch(`${this.baseUrl}/mode`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ mode })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.message || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to set logging mode:', error);
            throw error;
        }
    }
    
    /**
     * Submit a log entry to the backend
     * 
     * Uses sendBeacon for non-blocking submission (doesn't wait for response).
     * Falls back to fetch if sendBeacon is not available.
     * 
     * @param {Object} logEntry - Log entry object
     * @param {string} logEntry.level - Log level ('INFO', 'WARN', 'ERROR')
     * @param {string} logEntry.category - Log category ('CLICK', 'API', 'CONSOLE', 'ERROR', 'SAPUI5')
     * @param {string} logEntry.message - Log message
     * @param {Object} [logEntry.details] - Additional details
     * @returns {Promise<void>}
     * @example
     * await adapter.submitLog({
     *     level: 'INFO',
     *     category: 'CLICK',
     *     message: 'User clicked button',
     *     details: { element: 'Button#submit', x: 450, y: 300 }
     * });
     */
    async submitLog(logEntry) {
        const url = `${this.baseUrl}/client`;
        const data = JSON.stringify(logEntry);
        
        try {
            // Use sendBeacon for non-blocking submission (preferred)
            if (navigator.sendBeacon) {
                const blob = new Blob([data], { type: 'application/json' });
                const success = navigator.sendBeacon(url, blob);
                
                if (!success) {
                    // sendBeacon failed, fall back to fetch
                    await this._submitLogViaFetch(url, logEntry);
                }
            } else {
                // sendBeacon not available, use fetch
                await this._submitLogViaFetch(url, logEntry);
            }
        } catch (error) {
            // Silently fail - don't want logging errors to break the app
            console.error('Failed to submit log:', error);
        }
    }
    
    /**
     * Submit log via fetch (fallback method)
     * @private
     */
    async _submitLogViaFetch(url, logEntry) {
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(logEntry)
            });
            
            if (!response.ok) {
                console.warn(`Log submission failed: HTTP ${response.status}`);
            }
        } catch (error) {
            console.error('Fetch submission failed:', error);
        }
    }
    
    /**
     * Retrieve logs from backend (paginated)
     * 
     * @param {Object} options - Query options
     * @param {string} [options.level] - Filter by level ('INFO', 'WARN', 'ERROR')
     * @param {string} [options.category] - Filter by category
     * @param {number} [options.limit=100] - Max results
     * @param {number} [options.offset=0] - Pagination offset
     * @returns {Promise<Object>} Response with logs array
     * @example
     * const response = await adapter.getLogs({ level: 'ERROR', limit: 50 });
     * // { status: 'success', data: { logs: [...], total: 123, limit: 50, offset: 0 } }
     */
    async getLogs(options = {}) {
        try {
            const params = new URLSearchParams();
            
            if (options.level) params.append('level', options.level);
            if (options.category) params.append('category', options.category);
            if (options.limit) params.append('limit', options.limit.toString());
            if (options.offset) params.append('offset', options.offset.toString());
            
            const url = `${this.baseUrl}/logs?${params.toString()}`;
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Failed to retrieve logs:', error);
            throw error;
        }
    }
    
    /**
     * Health check
     * 
     * @returns {Promise<Object>} Health status
     * @example
     * const response = await adapter.healthCheck();
     * // { status: 'healthy', module: 'logger', version: '1.0.0', ... }
     */
    async healthCheck() {
        try {
            const response = await fetch(`${this.baseUrl}/health`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Health check failed:', error);
            throw error;
        }
    }
}

export default LoggerAdapter;