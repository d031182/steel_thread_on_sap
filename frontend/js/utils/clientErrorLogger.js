/**
 * Client-Side Error Logger
 * 
 * Captures JavaScript errors, warnings, and console messages from the browser
 * and sends them to the backend for centralized logging and analysis.
 * 
 * This helps diagnose issues that occur in the browser but aren't visible
 * in the backend logs.
 */

class ClientErrorLogger {
    constructor(endpoint = '/api/logs/client') {
        this.endpoint = endpoint;
        this.enabled = true;
        this.maxRetries = 3;
        this.logQueue = [];
        this.isSending = false;
        
        // Initialize error capturing
        this.init();
    }
    
    init() {
        // Capture unhandled errors
        window.addEventListener('error', (event) => {
            this.logError({
                level: 'ERROR',
                message: event.message || 'Uncaught error',
                url: event.filename || window.location.href,
                line: event.lineno || 0,
                column: event.colno || 0,
                stack: event.error ? event.error.stack : '',
                timestamp: new Date().toISOString()
            });
        });
        
        // Capture unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.logError({
                level: 'ERROR',
                message: `Unhandled Promise Rejection: ${event.reason}`,
                url: window.location.href,
                line: 0,
                column: 0,
                stack: event.reason && event.reason.stack ? event.reason.stack : '',
                timestamp: new Date().toISOString()
            });
        });
        
        // Intercept console.error
        const originalConsoleError = console.error;
        console.error = (...args) => {
            // Call original console.error
            originalConsoleError.apply(console, args);
            
            // Log to backend
            const message = args.map(arg => 
                typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
            ).join(' ');
            
            this.logError({
                level: 'ERROR',
                message: `Console Error: ${message}`,
                url: window.location.href,
                line: 0,
                column: 0,
                stack: new Error().stack || '',
                timestamp: new Date().toISOString()
            });
        };
        
        // Intercept console.warn
        const originalConsoleWarn = console.warn;
        console.warn = (...args) => {
            // Call original console.warn
            originalConsoleWarn.apply(console, args);
            
            // Log to backend
            const message = args.map(arg => 
                typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
            ).join(' ');
            
            this.logError({
                level: 'WARNING',
                message: `Console Warning: ${message}`,
                url: window.location.href,
                line: 0,
                column: 0,
                stack: '',
                timestamp: new Date().toISOString()
            });
        };
        
        console.log('[ClientErrorLogger] Error logging initialized');
    }
    
    logError(errorInfo) {
        if (!this.enabled) {
            return;
        }
        
        // Add to queue
        this.logQueue.push(errorInfo);
        
        // Send if not already sending
        if (!this.isSending) {
            this.sendLogs();
        }
    }
    
    async sendLogs() {
        if (this.logQueue.length === 0 || this.isSending) {
            return;
        }
        
        this.isSending = true;
        
        // Take first log from queue
        const errorInfo = this.logQueue.shift();
        
        try {
            const response = await fetch(this.endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(errorInfo)
            });
            
            if (!response.ok) {
                console.warn('[ClientErrorLogger] Failed to send error log:', response.status);
            }
        } catch (error) {
            // Failed to send - don't log this recursively!
            console.warn('[ClientErrorLogger] Network error sending log:', error.message);
        } finally {
            this.isSending = false;
            
            // Send next log if any
            if (this.logQueue.length > 0) {
                setTimeout(() => this.sendLogs(), 100);
            }
        }
    }
    
    enable() {
        this.enabled = true;
        console.log('[ClientErrorLogger] Error logging enabled');
    }
    
    disable() {
        this.enabled = false;
        console.log('[ClientErrorLogger] Error logging disabled');
    }
}

// Create global instance
window.clientErrorLogger = new ClientErrorLogger();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ClientErrorLogger;
}
