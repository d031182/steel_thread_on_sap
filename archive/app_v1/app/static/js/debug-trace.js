/**
 * Debug Trace System - Flight Recorder for UX Issues
 * ===================================================
 * Captures every user action, API call, error, and timing for AI analysis
 * 
 * Usage:
 * 1. Add to index.html: <script src="js/debug-trace.js"></script>
 * 2. Enable: localStorage.setItem('DEBUG_TRACE_ENABLED', 'true')
 * 3. Use app normally
 * 4. Download trace: window.DebugTrace.downloadTrace()
 * 5. Share with AI for analysis
 */

(function() {
    'use strict';

    class DebugTraceRecorder {
        constructor() {
            this.traces = [];
            this.sessionId = this.generateSessionId();
            this.startTime = Date.now();
            this.enabled = localStorage.getItem('DEBUG_TRACE_ENABLED') === 'true';
            
            if (this.enabled) {
                this.initialize();
                console.log('%c[DEBUG TRACE] Recorder ACTIVE - Session: ' + this.sessionId, 
                    'background: #00ff00; color: #000; font-weight: bold; padding: 4px;');
            }
        }

        generateSessionId() {
            return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }

        initialize() {
            this.captureConsole();
            this.captureClicks();
            this.captureNetworkRequests();
            this.captureErrors();
            this.captureSAPUI5Events();
            this.capturePerformance();
            this.addControlPanel();
            
            // Initial trace
            this.addTrace('SYSTEM', 'Debug Trace Initialized', {
                sessionId: this.sessionId,
                url: window.location.href,
                userAgent: navigator.userAgent,
                timestamp: new Date().toISOString()
            });
        }

        addTrace(category, action, details = {}) {
            const trace = {
                timestamp: Date.now() - this.startTime,
                absoluteTime: new Date().toISOString(),
                category: category,
                action: action,
                details: details,
                stackTrace: this.getStackTrace()
            };
            
            this.traces.push(trace);
            
            // Also log to console with color coding
            const colors = {
                'CLICK': 'background: #4CAF50; color: white',
                'API': 'background: #2196F3; color: white',
                'ERROR': 'background: #f44336; color: white',
                'CONSOLE': 'background: #9E9E9E; color: white',
                'SAPUI5': 'background: #FF9800; color: white',
                'SYSTEM': 'background: #9C27B0; color: white',
                'PERFORMANCE': 'background: #00BCD4; color: white'
            };
            
            const color = colors[category] || 'background: #607D8B; color: white';
            console.log(
                `%c[${category}] ${action}`,
                color + '; padding: 2px 6px; border-radius: 3px;',
                details
            );
            
            // Auto-save to localStorage periodically
            if (this.traces.length % 10 === 0) {
                this.saveToLocalStorage();
            }
        }

        getStackTrace() {
            try {
                throw new Error();
            } catch (e) {
                return e.stack ? e.stack.split('\n').slice(3, 6).join('\n') : '';
            }
        }

        // 1. Capture Console Logs
        captureConsole() {
            const self = this;
            const originalLog = console.log;
            const originalWarn = console.warn;
            const originalError = console.error;

            console.log = function(...args) {
                self.addTrace('CONSOLE', 'log', { message: args.map(a => String(a)).join(' ') });
                originalLog.apply(console, args);
            };

            console.warn = function(...args) {
                self.addTrace('CONSOLE', 'warn', { message: args.map(a => String(a)).join(' ') });
                originalWarn.apply(console, args);
            };

            console.error = function(...args) {
                self.addTrace('CONSOLE', 'error', { message: args.map(a => String(a)).join(' ') });
                originalError.apply(console, args);
            };
        }

        // 2. Capture All Clicks
        captureClicks() {
            const self = this;
            document.addEventListener('click', function(e) {
                const element = e.target;
                const details = {
                    tagName: element.tagName,
                    id: element.id || null,
                    className: element.className || null,
                    text: element.textContent ? element.textContent.substring(0, 50) : null,
                    coordinates: { x: e.clientX, y: e.clientY }
                };
                
                // Try to get SAPUI5 control info
                if (typeof sap !== 'undefined' && sap.ui && sap.ui.getCore) {
                    const control = sap.ui.getCore().byId(element.id);
                    if (control) {
                        details.sapui5Control = control.getMetadata().getName();
                    }
                }
                
                self.addTrace('CLICK', 'User clicked element', details);
            }, true);
        }

        // 3. Capture Network Requests (XHR & Fetch)
        captureNetworkRequests() {
            const self = this;

            // Intercept XMLHttpRequest
            const originalXHROpen = XMLHttpRequest.prototype.open;
            const originalXHRSend = XMLHttpRequest.prototype.send;

            XMLHttpRequest.prototype.open = function(method, url, ...args) {
                this._debugTrace = { method, url, startTime: Date.now() };
                return originalXHROpen.call(this, method, url, ...args);
            };

            XMLHttpRequest.prototype.send = function(body) {
                const xhr = this;
                
                self.addTrace('API', 'XHR Request Started', {
                    method: xhr._debugTrace.method,
                    url: xhr._debugTrace.url,
                    body: body ? (typeof body === 'string' ? body.substring(0, 200) : '[Object]') : null
                });

                xhr.addEventListener('load', function() {
                    const duration = Date.now() - xhr._debugTrace.startTime;
                    self.addTrace('API', 'XHR Request Completed', {
                        method: xhr._debugTrace.method,
                        url: xhr._debugTrace.url,
                        status: xhr.status,
                        statusText: xhr.statusText,
                        duration: duration + 'ms',
                        responseSize: xhr.responseText ? xhr.responseText.length : 0
                    });
                });

                xhr.addEventListener('error', function() {
                    self.addTrace('ERROR', 'XHR Request Failed', {
                        method: xhr._debugTrace.method,
                        url: xhr._debugTrace.url,
                        error: 'Network error'
                    });
                });

                return originalXHRSend.call(this, body);
            };

            // Intercept Fetch
            const originalFetch = window.fetch;
            window.fetch = function(url, options = {}) {
                const startTime = Date.now();
                
                self.addTrace('API', 'Fetch Request Started', {
                    url: url,
                    method: options.method || 'GET',
                    body: options.body ? (typeof options.body === 'string' ? options.body.substring(0, 200) : '[Object]') : null
                });

                return originalFetch.apply(this, arguments)
                    .then(response => {
                        const duration = Date.now() - startTime;
                        self.addTrace('API', 'Fetch Request Completed', {
                            url: url,
                            status: response.status,
                            statusText: response.statusText,
                            duration: duration + 'ms'
                        });
                        return response;
                    })
                    .catch(error => {
                        self.addTrace('ERROR', 'Fetch Request Failed', {
                            url: url,
                            error: error.message
                        });
                        throw error;
                    });
            };
        }

        // 4. Capture Errors
        captureErrors() {
            const self = this;

            window.addEventListener('error', function(e) {
                self.addTrace('ERROR', 'JavaScript Error', {
                    message: e.message,
                    filename: e.filename,
                    lineno: e.lineno,
                    colno: e.colno,
                    stack: e.error ? e.error.stack : null
                });
            });

            window.addEventListener('unhandledrejection', function(e) {
                self.addTrace('ERROR', 'Unhandled Promise Rejection', {
                    reason: e.reason,
                    promise: String(e.promise)
                });
            });
        }

        // 5. Capture SAPUI5 Events
        captureSAPUI5Events() {
            const self = this;
            
            // Wait for SAPUI5 to load
            const checkUI5 = setInterval(function() {
                if (typeof sap !== 'undefined' && sap.ui && sap.ui.getCore) {
                    clearInterval(checkUI5);
                    
                    self.addTrace('SAPUI5', 'SAPUI5 Core Loaded', {
                        version: sap.ui.version || 'unknown'
                    });

                    // Capture dialog events
                    const originalDialogOpen = sap.m.Dialog.prototype.open;
                    sap.m.Dialog.prototype.open = function() {
                        self.addTrace('SAPUI5', 'Dialog Opening', {
                            title: this.getTitle ? this.getTitle() : 'unknown',
                            id: this.getId ? this.getId() : 'unknown'
                        });
                        return originalDialogOpen.apply(this, arguments);
                    };
                }
            }, 100);

            // Timeout after 10 seconds
            setTimeout(() => clearInterval(checkUI5), 10000);
        }

        // 6. Capture Performance Metrics
        capturePerformance() {
            const self = this;
            
            window.addEventListener('load', function() {
                const perfData = window.performance.timing;
                const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
                
                self.addTrace('PERFORMANCE', 'Page Load Complete', {
                    totalTime: pageLoadTime + 'ms',
                    domReady: (perfData.domContentLoadedEventEnd - perfData.navigationStart) + 'ms',
                    resourcesLoaded: (perfData.loadEventEnd - perfData.domContentLoadedEventEnd) + 'ms'
                });
            });
        }

        // 7. Add Control Panel UI
        addControlPanel() {
            const self = this;
            
            // Create floating control panel
            const panel = document.createElement('div');
            panel.id = 'debug-trace-panel';
            panel.innerHTML = `
                <style>
                    #debug-trace-panel {
                        position: fixed;
                        bottom: 20px;
                        right: 20px;
                        background: rgba(0, 0, 0, 0.9);
                        color: #00ff00;
                        padding: 15px;
                        border-radius: 8px;
                        font-family: 'Courier New', monospace;
                        font-size: 12px;
                        z-index: 10000;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
                        min-width: 250px;
                    }
                    #debug-trace-panel h4 {
                        margin: 0 0 10px 0;
                        color: #00ff00;
                        font-size: 14px;
                    }
                    #debug-trace-panel button {
                        background: #00ff00;
                        color: #000;
                        border: none;
                        padding: 8px 12px;
                        margin: 5px 5px 0 0;
                        cursor: pointer;
                        border-radius: 4px;
                        font-weight: bold;
                        font-size: 11px;
                    }
                    #debug-trace-panel button:hover {
                        background: #00cc00;
                    }
                    #debug-trace-panel .stats {
                        margin: 10px 0;
                        padding: 10px;
                        background: rgba(0, 255, 0, 0.1);
                        border-radius: 4px;
                    }
                    #debug-trace-panel .close-btn {
                        float: right;
                        background: #ff0000;
                        color: white;
                        padding: 4px 8px;
                        margin: -10px -10px 0 0;
                    }
                </style>
                <button class="close-btn" onclick="this.parentElement.style.display='none'">✕</button>
                <h4>🔍 Debug Trace Active</h4>
                <div class="stats">
                    <div>Session: ${this.sessionId.substring(0, 20)}...</div>
                    <div>Traces: <span id="trace-count">0</span></div>
                    <div>Elapsed: <span id="trace-elapsed">0s</span></div>
                </div>
                <button onclick="window.DebugTrace.downloadTrace()">💾 Download</button>
                <button onclick="window.DebugTrace.copyTrace()">📋 Copy</button>
                <button onclick="window.DebugTrace.clearTrace()">🗑️ Clear</button>
                <button onclick="window.DebugTrace.disable()">⏹️ Stop</button>
            `;
            
            document.body.appendChild(panel);
            
            // Update stats periodically
            setInterval(function() {
                document.getElementById('trace-count').textContent = self.traces.length;
                document.getElementById('trace-elapsed').textContent = 
                    Math.round((Date.now() - self.startTime) / 1000) + 's';
            }, 1000);
        }

        // Export Methods
        downloadTrace() {
            const traceData = {
                sessionId: this.sessionId,
                startTime: new Date(this.startTime).toISOString(),
                duration: (Date.now() - this.startTime) + 'ms',
                totalTraces: this.traces.length,
                systemInfo: {
                    url: window.location.href,
                    userAgent: navigator.userAgent,
                    screenResolution: `${window.screen.width}x${window.screen.height}`,
                    viewport: `${window.innerWidth}x${window.innerHeight}`
                },
                traces: this.traces
            };

            const blob = new Blob([JSON.stringify(traceData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `debug-trace-${this.sessionId}.json`;
            a.click();
            URL.revokeObjectURL(url);

            console.log('%c[DEBUG TRACE] Downloaded: ' + a.download, 
                'background: #00ff00; color: #000; font-weight: bold; padding: 4px;');
        }

        copyTrace() {
            const traceData = JSON.stringify({
                sessionId: this.sessionId,
                traces: this.traces
            }, null, 2);

            navigator.clipboard.writeText(traceData).then(() => {
                alert('Debug trace copied to clipboard! Paste it for AI analysis.');
            });
        }

        clearTrace() {
            if (confirm('Clear all traces?')) {
                this.traces = [];
                localStorage.removeItem('DEBUG_TRACE_DATA');
                console.log('%c[DEBUG TRACE] Traces cleared', 
                    'background: #ff9800; color: #000; font-weight: bold; padding: 4px;');
            }
        }

        disable() {
            localStorage.setItem('DEBUG_TRACE_ENABLED', 'false');
            location.reload();
        }

        saveToLocalStorage() {
            try {
                const data = JSON.stringify({
                    sessionId: this.sessionId,
                    traces: this.traces.slice(-100) // Keep last 100 traces
                });
                localStorage.setItem('DEBUG_TRACE_DATA', data);
            } catch (e) {
                console.warn('Failed to save traces to localStorage:', e);
            }
        }
    }

    // Initialize global instance
    window.DebugTrace = new DebugTraceRecorder();

    // Provide helper functions for manual tracing
    window.debugTrace = function(category, action, details) {
        if (window.DebugTrace && window.DebugTrace.enabled) {
            window.DebugTrace.addTrace(category, action, details);
        }
    };

})();