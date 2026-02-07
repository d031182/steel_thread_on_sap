/**
 * Dual-Mode Logging System - Frontend
 * ====================================
 * Manages logging behavior based on mode:
 * - DEFAULT: Business-level only, no automatic logging
 * - FLIGHT_RECORDER: Full tracing + backend sync
 * 
 * Automatically detects mode from backend and initializes appropriate behavior.
 * 
 * Usage:
 *   1. Include in HTML: <script src="js/logging-modes.js"></script>
 *   2. Mode switches automatically based on backend setting
 *   3. Manual control: window.LoggingMode.switchMode('flight_recorder')
 * 
 * Author: P2P Development Team
 * Version: 1.0.0
 * Date: 2026-02-07
 */

(function() {
    'use strict';

    class LoggingModeManager {
        constructor() {
            this.mode = 'default';  // Will be fetched from backend
            this.sessionId = this.generateSessionId();
            this.initialized = false;
            this.batchQueue = [];
            this.batchSize = 10;  // Send logs in batches of 10
            this.batchTimeout = 5000;  // Or after 5 seconds
            this.batchTimer = null;
            
            // Initialize asynchronously
            this.initialize();
        }

        generateSessionId() {
            return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }

        async initialize() {
            try {
                // Fetch current mode from backend
                const response = await fetch('/api/logging/mode');
                const data = await response.json();
                
                if (data.success) {
                    this.mode = data.status.mode;
                    console.log(`%c[LOGGING MODE] ${this.mode.toUpperCase()}`, 
                        this.mode === 'flight_recorder' 
                            ? 'background: #ff6600; color: white; font-weight: bold; padding: 4px;'
                            : 'background: #4CAF50; color: white; font-weight: bold; padding: 4px;'
                    );
                    
                    if (this.isFlightRecorder()) {
                        this.initializeFlightRecorder();
                    }
                    
                    this.initialized = true;
                } else {
                    console.error('[LOGGING MODE] Failed to fetch mode from backend');
                    this.mode = 'default';  // Safe fallback
                }
            } catch (error) {
                console.error('[LOGGING MODE] Error initializing:', error);
                this.mode = 'default';  // Safe fallback
            }
        }

        isFlightRecorder() {
            return this.mode === 'flight_recorder';
        }

        isDefault() {
            return this.mode === 'default';
        }

        initializeFlightRecorder() {
            console.log('%c[FLIGHT RECORDER] Capturing all activities...', 
                'background: #ff6600; color: white; font-weight: bold; padding: 4px;');
            
            // Capture everything and send to backend
            this.captureClicks();
            this.captureConsole();
            this.captureNetworkRequests();
            this.captureErrors();
            this.captureSAPUI5Events();
            
            // Log initialization
            this.sendToBackend('SYSTEM', 'Flight Recorder initialized', {
                sessionId: this.sessionId,
                url: window.location.href,
                timestamp: new Date().toISOString()
            });
        }

        // Send log to backend (with batching for performance)
        sendToBackend(category, action, details = {}) {
            if (!this.initialized) {
                // Queue until initialized
                setTimeout(() => this.sendToBackend(category, action, details), 100);
                return;
            }
            
            const logEntry = {
                level: this.determineLevelFromCategory(category),
                category: category,
                message: `[${category}] ${action}`,
                details: {
                    ...details,
                    sessionId: this.sessionId,
                    timestamp: new Date().toISOString(),
                    url: window.location.href
                }
            };

            // Add to batch queue
            this.batchQueue.push(logEntry);
            
            // Send if batch size reached
            if (this.batchQueue.length >= this.batchSize) {
                this.flushBatch();
            } else {
                // Reset batch timer
                if (this.batchTimer) {
                    clearTimeout(this.batchTimer);
                }
                this.batchTimer = setTimeout(() => this.flushBatch(), this.batchTimeout);
            }
        }

        flushBatch() {
            if (this.batchQueue.length === 0) return;
            
            const batch = [...this.batchQueue];
            this.batchQueue = [];
            
            if (this.batchTimer) {
                clearTimeout(this.batchTimer);
                this.batchTimer = null;
            }
            
            // Send batch (for now, send individually - can be optimized later)
            batch.forEach(logEntry => {
                const blob = new Blob([JSON.stringify(logEntry)], { type: 'application/json' });
                navigator.sendBeacon('/api/logs/client', blob);
            });
        }

        determineLevelFromCategory(category) {
            const levelMap = {
                'ERROR': 'ERROR',
                'CONSOLE_ERROR': 'ERROR',
                'API_ERROR': 'ERROR',
                'CLICK': 'INFO',
                'API': 'INFO',
                'CONSOLE': 'INFO',
                'SAPUI5': 'INFO',
                'PERFORMANCE': 'INFO',
                'SYSTEM': 'INFO'
            };
            return levelMap[category] || 'INFO';
        }

        // Capture Methods

        captureClicks() {
            const self = this;
            document.addEventListener('click', function(e) {
                const element = e.target;
                
                // Get SAPUI5 control info if available
                let controlInfo = null;
                if (typeof sap !== 'undefined' && sap.ui && sap.ui.getCore) {
                    const control = sap.ui.getCore().byId(element.id);
                    if (control) {
                        controlInfo = control.getMetadata().getName();
                    }
                }
                
                self.sendToBackend('CLICK', 'User clicked element', {
                    tagName: element.tagName,
                    id: element.id || null,
                    className: element.className || null,
                    text: element.textContent ? element.textContent.substring(0, 50) : null,
                    coordinates: { x: e.clientX, y: e.clientY },
                    sapui5Control: controlInfo
                });
            }, true);
        }

        captureConsole() {
            const originalLog = console.log;
            const originalWarn = console.warn;
            const originalError = console.error;
            const self = this;

            console.log = function(...args) {
                self.sendToBackend('CONSOLE', 'log', { 
                    message: args.map(a => String(a)).join(' ') 
                });
                originalLog.apply(console, args);
            };

            console.warn = function(...args) {
                self.sendToBackend('CONSOLE', 'warn', { 
                    message: args.map(a => String(a)).join(' ') 
                });
                originalWarn.apply(console, args);
            };

            console.error = function(...args) {
                self.sendToBackend('CONSOLE_ERROR', 'error', { 
                    message: args.map(a => String(a)).join(' ') 
                });
                originalError.apply(console, args);
            };
        }

        captureNetworkRequests() {
            const self = this;

            // Intercept XMLHttpRequest
            const originalXHROpen = XMLHttpRequest.prototype.open;
            const originalXHRSend = XMLHttpRequest.prototype.send;

            XMLHttpRequest.prototype.open = function(method, url, ...args) {
                this._loggingTrace = { method, url, startTime: Date.now() };
                return originalXHROpen.call(this, method, url, ...args);
            };

            XMLHttpRequest.prototype.send = function(body) {
                const xhr = this;
                
                self.sendToBackend('API', 'XHR Request started', {
                    method: xhr._loggingTrace.method,
                    url: xhr._loggingTrace.url,
                    body: body ? (typeof body === 'string' ? body.substring(0, 500) : '[Object]') : null
                });

                xhr.addEventListener('load', function() {
                    const duration = Date.now() - xhr._loggingTrace.startTime;
                    self.sendToBackend('API', 'XHR Request completed', {
                        method: xhr._loggingTrace.method,
                        url: xhr._loggingTrace.url,
                        status: xhr.status,
                        statusText: xhr.statusText,
                        duration_ms: duration
                    });
                });

                xhr.addEventListener('error', function() {
                    self.sendToBackend('API_ERROR', 'XHR Request failed', {
                        method: xhr._loggingTrace.method,
                        url: xhr._loggingTrace.url
                    });
                });

                return originalXHRSend.call(this, body);
            };

            // Intercept Fetch
            const originalFetch = window.fetch;

            window.fetch = function(url, options = {}) {
                const startTime = Date.now();
                
                self.sendToBackend('API', 'Fetch started', {
                    url: url,
                    method: options.method || 'GET',
                    body: options.body ? (typeof options.body === 'string' ? options.body.substring(0, 500) : '[Object]') : null
                });

                return originalFetch.apply(this, arguments)
                    .then(response => {
                        const duration = Date.now() - startTime;
                        self.sendToBackend('API', 'Fetch completed', {
                            url: url,
                            status: response.status,
                            statusText: response.statusText,
                            duration_ms: duration
                        });
                        return response;
                    })
                    .catch(error => {
                        self.sendToBackend('API_ERROR', 'Fetch failed', {
                            url: url,
                            error: error.message
                        });
                        throw error;
                    });
            };
        }

        captureErrors() {
            const self = this;

            window.addEventListener('error', function(e) {
                self.sendToBackend('ERROR', 'JavaScript Error', {
                    message: e.message,
                    filename: e.filename,
                    lineno: e.lineno,
                    colno: e.colno,
                    stack: e.error ? e.error.stack : null
                });
            });

            window.addEventListener('unhandledrejection', function(e) {
                self.sendToBackend('ERROR', 'Unhandled Promise Rejection', {
                    reason: String(e.reason),
                    promise: e.promise ? String(e.promise) : null
                });
            });
        }

        captureSAPUI5Events() {
            const self = this;
            
            // Wait for SAPUI5 to load
            const checkUI5 = setInterval(function() {
                if (typeof sap !== 'undefined' && sap.ui && sap.ui.getCore) {
                    clearInterval(checkUI5);
                    
                    self.sendToBackend('SAPUI5', 'SAPUI5 Core loaded', {
                        version: sap.ui.version || 'unknown'
                    });

                    // Capture dialog events (defensive check)
                    if (sap.m && sap.m.Dialog && sap.m.Dialog.prototype && sap.m.Dialog.prototype.open) {
                        const originalDialogOpen = sap.m.Dialog.prototype.open;
                        sap.m.Dialog.prototype.open = function() {
                            self.sendToBackend('SAPUI5', 'Dialog opening', {
                                title: this.getTitle ? this.getTitle() : 'unknown',
                                id: this.getId ? this.getId() : 'unknown'
                            });
                            return originalDialogOpen.apply(this, arguments);
                        };
                    }
                }
            }, 100);

            // Timeout after 10 seconds
            setTimeout(() => clearInterval(checkUI5), 10000);
        }

        // Public API for mode switching
        async switchMode(newMode) {
            if (!['default', 'flight_recorder'].includes(newMode.toLowerCase())) {
                console.error('[LOGGING MODE] Invalid mode:', newMode);
                return false;
            }
            
            try {
                const response = await fetch('/api/logging/mode', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mode: newMode.toLowerCase() })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    console.log(`%c[LOGGING MODE] Switched: ${data.old_mode} → ${data.new_mode}`, 
                        'background: #2196F3; color: white; font-weight: bold; padding: 4px;');
                    
                    // Reload page to reinitialize with new mode
                    setTimeout(() => location.reload(), 1000);
                    return true;
                } else {
                    console.error('[LOGGING MODE] Failed to switch mode:', data.error);
                    return false;
                }
            } catch (error) {
                console.error('[LOGGING MODE] Error switching mode:', error);
                return false;
            }
        }

        async getStatus() {
            try {
                const response = await fetch('/api/logging/mode');
                const data = await response.json();
                return data.success ? data.status : null;
            } catch (error) {
                console.error('[LOGGING MODE] Error getting status:', error);
                return null;
            }
        }

        getCurrentMode() {
            return this.mode;
        }

        getSessionId() {
            return this.sessionId;
        }
    }

    // Initialize global instance
    window.LoggingMode = new LoggingModeManager();

    // Helper for manual logging (works in both modes for explicit events)
    window.logToSystem = function(level, message, details) {
        if (window.LoggingMode && window.LoggingMode.initialized) {
            window.LoggingMode.sendToBackend(level, message, details);
        }
    };

    // Add mode switcher UI (optional, for debugging)
    function addModeSwitcherUI() {
        const switcher = document.createElement('div');
        switcher.id = 'logging-mode-switcher';
        switcher.innerHTML = `
            <style>
                #logging-mode-switcher {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: rgba(0, 0, 0, 0.85);
                    color: white;
                    padding: 12px 16px;
                    border-radius: 6px;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 13px;
                    z-index: 9999;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                    min-width: 200px;
                }
                #logging-mode-switcher h4 {
                    margin: 0 0 8px 0;
                    font-size: 13px;
                    font-weight: 600;
                }
                #logging-mode-switcher .mode-indicator {
                    display: inline-block;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                    margin-left: 8px;
                }
                #logging-mode-switcher .mode-default {
                    background: #4CAF50;
                    color: white;
                }
                #logging-mode-switcher .mode-flight {
                    background: #ff6600;
                    color: white;
                }
                #logging-mode-switcher button {
                    background: #2196F3;
                    color: white;
                    border: none;
                    padding: 6px 12px;
                    margin: 8px 4px 0 0;
                    cursor: pointer;
                    border-radius: 4px;
                    font-size: 11px;
                    font-weight: 600;
                }
                #logging-mode-switcher button:hover {
                    background: #1976D2;
                }
                #logging-mode-switcher .close-btn {
                    float: right;
                    background: transparent;
                    color: #ccc;
                    padding: 0;
                    margin: -8px -8px 0 0;
                    font-size: 18px;
                }
                #logging-mode-switcher .close-btn:hover {
                    color: white;
                }
            </style>
            <button class="close-btn" onclick="this.parentElement.style.display='none'">×</button>
            <h4>Logging Mode 
                <span id="mode-badge" class="mode-indicator mode-default">DEFAULT</span>
            </h4>
            <div style="margin: 8px 0; font-size: 11px; color: #ccc;">
                Session: <span id="session-id">${this.sessionId.substring(0, 20)}...</span>
            </div>
            <button onclick="window.LoggingMode.switchMode('flight_recorder')">
                🔴 Enable Flight Recorder
            </button>
            <button onclick="window.LoggingMode.switchMode('default')">
                ✅ Default Mode
            </button>
        `;
        
        document.body.appendChild(switcher);
        
        // Update indicator based on current mode
        setTimeout(() => {
            const badge = document.getElementById('mode-badge');
            if (window.LoggingMode.isFlightRecorder()) {
                badge.textContent = 'FLIGHT RECORDER';
                badge.className = 'mode-indicator mode-flight';
            }
        }, 500);
    }

    // Add UI after page load (only in development)
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', addModeSwitcherUI);
        } else {
            addModeSwitcherUI();
        }
    }

    // Flush remaining logs before page unload
    window.addEventListener('beforeunload', function() {
        if (window.LoggingMode) {
            window.LoggingMode.flushBatch();
        }
    });

})();