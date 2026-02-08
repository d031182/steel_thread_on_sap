/**
 * NoOpLogger (Null Object Pattern)
 * 
 * Purpose: Silent logger fallback when log_manager module is disabled
 * Pattern: Null Object Pattern (safe default implementation)
 * 
 * Behavior:
 * - Implements ILogger interface completely
 * - All methods are safe no-ops (no errors thrown)
 * - Optionally logs to console in development mode
 * 
 * Usage:
 *   DependencyContainer.register('ILogger', () => new NoOpLogger());
 *   const logger = DependencyContainer.get('ILogger');
 *   logger.log('Test');  // Silent (or console.debug in dev mode)
 * 
 * Why This Matters:
 * - Modules can always call logger.log() without checking if logger exists
 * - Code works unchanged whether log_manager enabled or disabled
 * - Graceful degradation (feature missing = silent, not error)
 * 
 * Architecture: Fallback adapter for ILogger interface
 */
class NoOpLogger extends ILogger {
    /**
     * Create a NoOpLogger
     * 
     * @param {boolean} logToConsole - If true, log to console.debug (dev mode)
     */
    constructor(logToConsole = false) {
        super();
        this._logToConsole = logToConsole;
    }
    
    /**
     * Log a message (silent or console.debug)
     * 
     * @param {string} message - Log message
     * @param {string} level - Severity level
     * @param {Object} context - Additional context
     * 
     * @example
     * logger.log('Graph refreshed', 'INFO');  // Silent (no backend logging)
     */
    log(message, level = 'INFO', context = null) {
        if (this._logToConsole) {
            const timestamp = new Date().toISOString();
            console.debug(
                `[NoOpLogger] ${timestamp} [${level}] ${message}`,
                context ? context : ''
            );
        }
        // Otherwise: completely silent (no console spam)
    }
    
    /**
     * Log an info message (shorthand for log with INFO level)
     */
    info(message, context = null) {
        this.log(message, 'INFO', context);
    }
    
    /**
     * Log a warning message (shorthand for log with WARNING level)
     */
    warn(message, context = null) {
        this.log(message, 'WARNING', context);
    }
    
    /**
     * Log an error message (shorthand for log with ERROR level)
     */
    error(message, context = null) {
        this.log(message, 'ERROR', context);
    }
    
    /**
     * Log a debug message (shorthand for log with DEBUG level)
     */
    debug(message, context = null) {
        this.log(message, 'DEBUG', context);
    }
    
    /**
     * Show log UI (no-op)
     * 
     * Does nothing since no log_manager module available
     * Could optionally show a "Log Manager not enabled" toast
     */
    showUI() {
        if (this._logToConsole) {
            console.debug('[NoOpLogger] showUI() called but log_manager module disabled');
        }
        // No-op: Don't throw error, just do nothing
    }
    
    /**
     * Get recent logs (returns empty array)
     * 
     * @returns {Promise<Array>} Empty array (no logs available)
     */
    async getRecentLogs(count = 50, level = null) {
        return [];  // No logs available
    }
}

// Export for module systems (ES6)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NoOpLogger;
}

// Export for browser global
if (typeof window !== 'undefined') {
    window.NoOpLogger = NoOpLogger;
}