/**
 * ILogger Interface
 * 
 * Purpose: Contract for logging services (Dependency Inversion Principle)
 * Pattern: Interface Segregation Principle (focused contract)
 * 
 * Implementations:
 * - LogManagerAdapter: Full logging to backend (if log_manager module enabled)
 * - NoOpLogger: Silent logging (fallback when log_manager disabled)
 * - ConsoleLogger: Console logging for development
 * 
 * Usage:
 *   const logger = DependencyContainer.get('ILogger');
 *   logger.log('Graph refreshed', 'INFO');
 *   logger.showUI();  // Opens log viewer (if available)
 * 
 * Architecture: Core interface for optional log_manager module dependency
 */
class ILogger {
    /**
     * Log a message with severity level
     * 
     * @param {string} message - Log message
     * @param {string} level - Severity level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
     * @param {Object} context - Additional context (optional)
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * logger.log('User logged in', 'INFO', { userId: 123 });
     */
    log(message, level = 'INFO', context = null) {
        throw new Error('ILogger.log() must be implemented by subclass');
    }
    
    /**
     * Show log viewer UI (if available)
     * 
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * logger.showUI();  // Opens log manager dialog
     */
    showUI() {
        throw new Error('ILogger.showUI() must be implemented by subclass');
    }
    
    /**
     * Get recent logs (if available)
     * 
     * @param {number} count - Number of recent logs (default: 50)
     * @param {string} level - Filter by level (optional)
     * @returns {Promise<Array>} Array of log entries
     * @throws {Error} Must be implemented by subclass
     * 
     * @example
     * const logs = await logger.getRecentLogs(10, 'ERROR');
     */
    async getRecentLogs(count = 50, level = null) {
        throw new Error('ILogger.getRecentLogs() must be implemented by subclass');
    }
}

// Export for module systems (ES6)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ILogger;
}

// Export for browser global
if (typeof window !== 'undefined') {
    window.ILogger = ILogger;
}