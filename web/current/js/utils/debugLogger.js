/**
 * Debug Logger Service
 * 
 * Provides conditional debug logging for troubleshooting.
 * Logs are only output when debug mode is enabled.
 * State persists across page reloads via localStorage.
 * 
 * @class DebugLogger
 * @singleton
 */
export class DebugLogger {
    static instance = null;
    static STORAGE_KEY = 'debugMode';
    
    /**
     * Get singleton instance
     * @returns {DebugLogger}
     */
    static getInstance() {
        if (!DebugLogger.instance) {
            DebugLogger.instance = new DebugLogger();
        }
        return DebugLogger.instance;
    }
    
    constructor() {
        // Load state from localStorage
        const stored = localStorage.getItem(DebugLogger.STORAGE_KEY);
        this.enabled = stored === 'true';
        
        // Log initial state
        if (this.enabled) {
            console.log('%c[DEBUG] Debug Mode is ENABLED', 'color: green; font-weight: bold');
        }
    }
    
    /**
     * Check if debug mode is enabled
     * @returns {boolean}
     */
    isEnabled() {
        return this.enabled;
    }
    
    /**
     * Enable debug mode
     */
    enable() {
        this.enabled = true;
        localStorage.setItem(DebugLogger.STORAGE_KEY, 'true');
        console.log('%c[DEBUG] Debug Mode ENABLED', 'color: green; font-weight: bold');
        console.log('%c[DEBUG] All function calls will now be logged', 'color: green');
    }
    
    /**
     * Disable debug mode
     */
    disable() {
        console.log('%c[DEBUG] Debug Mode DISABLED', 'color: gray; font-weight: bold');
        this.enabled = false;
        localStorage.setItem(DebugLogger.STORAGE_KEY, 'false');
    }
    
    /**
     * Toggle debug mode
     * @returns {boolean} New state
     */
    toggle() {
        if (this.enabled) {
            this.disable();
        } else {
            this.enable();
        }
        return this.enabled;
    }
    
    /**
     * Log a debug message (only if enabled)
     * @param {string} message - Message to log
     * @param {*} data - Optional data to log
     */
    log(message, data = null) {
        if (!this.enabled) return;
        
        const timestamp = new Date().toISOString();
        console.log(
            `%c[DEBUG] ${timestamp}`,
            'color: blue; font-weight: bold',
            message,
            data !== null ? data : ''
        );
    }
    
    /**
     * Log function entry (only if enabled)
     * @param {string} functionName - Name of function
     * @param {Object} params - Function parameters
     * @returns {number} Start time for performance tracking
     */
    entry(functionName, params = {}) {
        if (!this.enabled) return Date.now();
        
        const timestamp = new Date().toISOString();
        const startTime = Date.now();
        
        console.group(`%c[DEBUG] ENTRY: ${functionName}()`, 'color: green; font-weight: bold');
        console.log(`%c  Timestamp:`, 'color: gray', timestamp);
        console.log(`%c  Parameters:`, 'color: gray', params);
        console.groupEnd();
        
        return startTime;
    }
    
    /**
     * Log function exit (only if enabled)
     * @param {string} functionName - Name of function
     * @param {*} result - Function result
     * @param {number} startTime - Start time from entry()
     */
    exit(functionName, result = null, startTime = null) {
        if (!this.enabled) return;
        
        const timestamp = new Date().toISOString();
        const duration = startTime ? Date.now() - startTime : 0;
        
        console.group(`%c[DEBUG] EXIT: ${functionName}()`, 'color: blue; font-weight: bold');
        console.log(`%c  Timestamp:`, 'color: gray', timestamp);
        console.log(`%c  Duration:`, 'color: gray', `${duration}ms`);
        if (result !== null) {
            console.log(`%c  Result:`, 'color: gray', result);
        }
        console.groupEnd();
    }
    
    /**
     * Log an error (only if enabled)
     * @param {string} functionName - Name of function where error occurred
     * @param {Error} error - Error object
     */
    error(functionName, error) {
        if (!this.enabled) return;
        
        const timestamp = new Date().toISOString();
        
        console.group(`%c[DEBUG] ERROR in ${functionName}()`, 'color: red; font-weight: bold');
        console.log(`%c  Timestamp:`, 'color: gray', timestamp);
        console.log(`%c  Error:`, 'color: gray', error);
        console.log(`%c  Message:`, 'color: gray', error.message);
        if (error.stack) {
            console.log(`%c  Stack:`, 'color: gray', error.stack);
        }
        console.groupEnd();
    }
    
    /**
     * Start a performance timer
     * @returns {number} Start time
     */
    startTimer() {
        return Date.now();
    }
    
    /**
     * End a performance timer and log result (only if enabled)
     * @param {string} label - Timer label
     * @param {number} startTime - Start time from startTimer()
     */
    endTimer(label, startTime) {
        if (!this.enabled) return;
        
        const duration = Date.now() - startTime;
        console.log(
            `%c[DEBUG] ⏱️ ${label}:`,
            'color: purple; font-weight: bold',
            `${duration}ms`
        );
    }
    
    /**
     * Log object properties (only if enabled)
     * @param {string} label - Object label
     * @param {Object} obj - Object to inspect
     */
    inspect(label, obj) {
        if (!this.enabled) return;
        
        console.group(`%c[DEBUG] 🔍 Inspecting: ${label}`, 'color: orange; font-weight: bold');
        console.log(`%c  Type:`, 'color: gray', typeof obj);
        console.log(`%c  Value:`, 'color: gray', obj);
        if (obj && typeof obj === 'object') {
            console.log(`%c  Keys:`, 'color: gray', Object.keys(obj));
            console.table(obj);
        }
        console.groupEnd();
    }
    
    /**
     * Log a table of data (only if enabled)
     * @param {string} label - Table label
     * @param {Array|Object} data - Data to display in table
     */
    table(label, data) {
        if (!this.enabled) return;
        
        console.log(`%c[DEBUG] 📊 ${label}`, 'color: teal; font-weight: bold');
        console.table(data);
    }
    
    /**
     * Group debug logs together (only if enabled)
     * @param {string} groupName - Group name
     */
    group(groupName) {
        if (!this.enabled) return;
        console.group(`%c[DEBUG] 📦 ${groupName}`, 'color: purple; font-weight: bold');
    }
    
    /**
     * End a debug log group (only if enabled)
     */
    groupEnd() {
        if (!this.enabled) return;
        console.groupEnd();
    }
}

// Export singleton instance
export const debugLogger = DebugLogger.getInstance();