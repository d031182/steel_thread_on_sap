# Dual-Mode Logging System Design

**Status**: 📋 DESIGN PHASE  
**Created**: 2026-02-07  
**Purpose**: Two-tier logging strategy for production vs debugging scenarios

---

## Overview

The P2P Data Products application requires **two distinct logging modes**:

1. **Default Mode** (Production): Business-level activity tracking
2. **Flight Recorder Mode** (Debug): Full end-to-end technical tracing

---

## 🎯 Requirements

### Mode 1: Default (Production Logging)

**Purpose**: Track **business-level activities** for audit, compliance, and monitoring

**What to Log**:
- ✅ User authentication events (login, logout, session)
- ✅ API endpoint calls (which API was called, by whom)
- ✅ Business operations (data product access, SQL execution, graph queries)
- ✅ Security events (unauthorized access, permission changes)
- ✅ System health events (module startup/shutdown, errors)

**What NOT to Log**:
- ❌ Request/response payloads (unless error)
- ❌ UI interactions (clicks, form inputs)
- ❌ Console logs from frontend
- ❌ Performance timings (unless threshold exceeded)
- ❌ Stack traces (unless error)

**Backend Behavior**:
```python
# Default mode logs only business-level events
logger.info("User 'john.doe' logged in successfully")
logger.info("API called: GET /api/data-products by user 'john.doe'")
logger.error("Failed to connect to HANA: Connection timeout")
```

**Frontend Behavior**:
```javascript
// NO automatic logging in default mode
// Only explicit business events logged via API
```

---

### Mode 2: Flight Recorder (Debug Logging)

**Purpose**: Capture **everything** for comprehensive debugging and issue analysis

**What to Log**:
- ✅ **Everything from Default Mode** (business activities)
- ✅ **Frontend activities**: All clicks, form inputs, navigation
- ✅ **API details**: Full request/response payloads, headers, timing
- ✅ **Console logs**: All console.log/warn/error from browser
- ✅ **JavaScript errors**: Complete stack traces, context
- ✅ **Performance metrics**: Every operation's duration
- ✅ **SAPUI5 events**: Dialog opens, control interactions
- ✅ **Network calls**: XHR/Fetch with payload inspection

**Backend Behavior**:
```python
# Flight Recorder logs EVERYTHING
logger.info("Request: POST /api/sql/execute", extra={
    'payload': request.json,
    'headers': dict(request.headers),
    'user': current_user,
    'session_id': session.id
})

logger.info("Response: 200 OK", extra={
    'duration_ms': 234.5,
    'rows_returned': 15,
    'query': sql_query
})
```

**Frontend Behavior**:
```javascript
// Flight Recorder WRITES TO BACKEND LOG via /api/logs/client
// Every trace is sent to backend for centralized storage

// Click captured
fetch('/api/logs/client', {
    method: 'POST',
    body: JSON.stringify({
        level: 'INFO',
        category: 'CLICK',
        message: 'User clicked: Search button',
        details: { x: 450, y: 300, element: 'Button#search' }
    })
});

// API call captured
fetch('/api/logs/client', {
    method: 'POST',
    body: JSON.stringify({
        level: 'INFO',
        category: 'API',
        message: 'Fetch started: GET /api/data-products',
        details: { url: '/api/data-products', method: 'GET' }
    })
});
```

---

## 🏗️ Architecture Design

### Configuration

**Feature Flag**:
```json
{
    "logging_mode": {
        "enabled": true,
        "mode": "default",  // Options: "default" | "flight_recorder"
        "description": "Controls logging verbosity",
        "allowedValues": ["default", "flight_recorder"]
    }
}
```

**Environment Variable** (for backend):
```bash
LOGGING_MODE=default  # or "flight_recorder"
```

**LocalStorage** (for frontend):
```javascript
localStorage.setItem('LOGGING_MODE', 'default');  // or "flight_recorder"
```

---

### Backend Implementation

**File**: `modules/log_manager/backend/logging_modes.py` (NEW)

```python
"""
Logging Modes Configuration
============================
Controls logging behavior based on mode (default vs flight_recorder)
"""

import os
from enum import Enum
from typing import Optional

class LoggingMode(Enum):
    """Logging mode enumeration"""
    DEFAULT = "default"
    FLIGHT_RECORDER = "flight_recorder"

class LoggingModeManager:
    """Manages logging mode configuration"""
    
    def __init__(self):
        self._mode = self._get_mode_from_env()
    
    def _get_mode_from_env(self) -> LoggingMode:
        """Get logging mode from environment"""
        mode_str = os.getenv('LOGGING_MODE', 'default').lower()
        try:
            return LoggingMode(mode_str)
        except ValueError:
            return LoggingMode.DEFAULT
    
    @property
    def mode(self) -> LoggingMode:
        """Current logging mode"""
        return self._mode
    
    @mode.setter
    def mode(self, value: LoggingMode):
        """Set logging mode"""
        self._mode = value
    
    def is_flight_recorder(self) -> bool:
        """Check if flight recorder mode is active"""
        return self._mode == LoggingMode.FLIGHT_RECORDER
    
    def should_log_request_details(self) -> bool:
        """Should log full request details?"""
        return self.is_flight_recorder()
    
    def should_log_response_details(self) -> bool:
        """Should log full response details?"""
        return self.is_flight_recorder()
    
    def should_accept_frontend_logs(self) -> bool:
        """Should accept frontend logs via /api/logs/client?"""
        # Always accept (for error reporting)
        # But Flight Recorder accepts ALL types, Default only errors
        return True
    
    def should_log_performance_metrics(self) -> bool:
        """Should log detailed performance metrics?"""
        return self.is_flight_recorder()

# Global instance
logging_mode_manager = LoggingModeManager()
```

---

### Frontend Implementation

**File**: `app/static/js/logging-modes.js` (NEW)

```javascript
/**
 * Dual-Mode Logging System - Frontend
 * ====================================
 * Manages logging behavior based on mode:
 * - DEFAULT: Business-level only, no automatic logging
 * - FLIGHT_RECORDER: Full tracing + backend sync
 */

(function() {
    'use strict';

    class LoggingModeManager {
        constructor() {
            this.mode = this.getMode();
            this.sessionId = this.generateSessionId();
            
            if (this.isFlightRecorder()) {
                this.initializeFlightRecorder();
            }
        }

        getMode() {
            // Priority: localStorage > feature flag > default
            const stored = localStorage.getItem('LOGGING_MODE');
            if (stored) {
                return stored.toLowerCase();
            }
            
            // TODO: Fetch from /api/features/logging_mode
            return 'default';
        }

        isFlightRecorder() {
            return this.mode === 'flight_recorder';
        }

        generateSessionId() {
            return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        }

        initializeFlightRecorder() {
            console.log('%c[FLIGHT RECORDER] Mode ACTIVE', 
                'background: #ff6600; color: white; font-weight: bold; padding: 4px;');
            
            // Capture everything and send to backend
            this.captureClicks();
            this.captureConsole();
            this.captureNetworkRequests();
            this.captureErrors();
            this.captureSAPUI5Events();
        }

        // Send log to backend
        sendToBackend(category, action, details = {}) {
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

            // Use sendBeacon for reliability (works even during page unload)
            const blob = new Blob([JSON.stringify(logEntry)], { type: 'application/json' });
            navigator.sendBeacon('/api/logs/client', blob);
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
                'PERFORMANCE': 'INFO'
            };
            return levelMap[category] || 'INFO';
        }

        captureClicks() {
            document.addEventListener('click', (e) => {
                const element = e.target;
                this.sendToBackend('CLICK', 'User clicked element', {
                    tagName: element.tagName,
                    id: element.id || null,
                    className: element.className || null,
                    text: element.textContent ? element.textContent.substring(0, 50) : null,
                    coordinates: { x: e.clientX, y: e.clientY }
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
            // Intercept Fetch
            const originalFetch = window.fetch;
            const self = this;

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
                    reason: String(e.reason)
                });
            });
        }

        captureSAPUI5Events() {
            const self = this;
            const checkUI5 = setInterval(function() {
                if (typeof sap !== 'undefined' && sap.ui && sap.ui.getCore) {
                    clearInterval(checkUI5);
                    
                    const originalDialogOpen = sap.m.Dialog.prototype.open;
                    sap.m.Dialog.prototype.open = function() {
                        self.sendToBackend('SAPUI5', 'Dialog opening', {
                            title: this.getTitle ? this.getTitle() : 'unknown'
                        });
                        return originalDialogOpen.apply(this, arguments);
                    };
                }
            }, 100);

            setTimeout(() => clearInterval(checkUI5), 10000);
        }

        // Public API for mode switching
        switchMode(newMode) {
            if (['default', 'flight_recorder'].includes(newMode.toLowerCase())) {
                localStorage.setItem('LOGGING_MODE', newMode.toLowerCase());
                location.reload();
            } else {
                console.error('Invalid logging mode:', newMode);
            }
        }

        getCurrentMode() {
            return this.mode;
        }
    }

    // Initialize global instance
    window.LoggingModeManager = new LoggingModeManager();

    // Helper for manual logging
    window.logToSystem = function(level, message, details) {
        if (window.LoggingModeManager) {
            window.LoggingModeManager.sendToBackend(level, message, details);
        }
    };

})();
```

---

## 📋 Implementation Plan

### Phase 1: Backend Infrastructure (2-3 hours)

- [ ] Create `modules/log_manager/backend/logging_modes.py`
- [ ] Update `app/app.py` middleware to respect logging mode
- [ ] Add `/api/logging/mode` endpoint (GET/POST for mode switching)
- [ ] Update `/api/logs/client` to handle Flight Recorder logs
- [ ] Add environment variable `LOGGING_MODE` support
- [ ] Write unit tests for LoggingModeManager

### Phase 2: Frontend Infrastructure (2-3 hours)

- [ ] Create `app/static/js/logging-modes.js`
- [ ] Integrate with existing `debug-trace.js` (refactor if needed)
- [ ] Add mode switcher UI component
- [ ] Test frontend → backend log sync
- [ ] Write integration tests

### Phase 3: Feature Flag Integration (1 hour)

- [ ] Add `logging_mode` to `feature_flags.json`
- [ ] Update Feature Manager UI to control logging mode
- [ ] Test mode switching via Feature Manager

### Phase 4: Documentation & Testing (1 hour)

- [ ] Update `docs/knowledge/INDEX.md` with links
- [ ] Create operational guide for production teams
- [ ] Test both modes end-to-end
- [ ] Performance testing (ensure Flight Recorder doesn't overwhelm backend)

---

## 🔍 Key Design Decisions

### 1. Why Two Separate Modes?

**Production (Default)**:
- Low overhead, audit-focused
- Won't fill logs with noise
- Complies with GDPR (no unnecessary user data)

**Debug (Flight Recorder)**:
- Opt-in for troubleshooting
- Temporary activation during issue investigation
- Complete picture for AI-assisted analysis

### 2. Why Send Frontend Logs to Backend in Flight Recorder?

**Benefits**:
- ✅ **Centralized**: All logs (frontend + backend) in one database
- ✅ **Correlation**: Match frontend click → API call → database query
- ✅ **Persistent**: Survives browser refresh, not lost in console
- ✅ **AI-Ready**: Backend can analyze patterns across sessions
- ✅ **Timeline**: Reconstruct exact sequence of events

**Drawbacks & Mitigation**:
- ⚠️ Network overhead → Use `sendBeacon` (non-blocking, reliable)
- ⚠️ Log volume → Rate limiting, batching (TODO: Phase 5)
- ⚠️ Database growth → Shorter retention for Flight Recorder logs (2 days)

### 3. How to Switch Modes?

**Option A: Feature Flag** (Recommended for production)
```bash
# Via Feature Manager UI
POST /api/features/logging_mode
{ "mode": "flight_recorder" }
```

**Option B: Environment Variable** (For deployment-level control)
```bash
# In .env file
LOGGING_MODE=flight_recorder
```

**Option C: localStorage** (For individual user debugging)
```javascript
// In browser console
localStorage.setItem('LOGGING_MODE', 'flight_recorder')
location.reload()
```

---

## 📊 Expected Log Volume

### Default Mode (Production)

**Estimate**: ~500 logs/day for 10 active users
- Login/logout: ~20/day
- API calls: ~400/day
- Errors: ~10/day
- System events: ~70/day

**Database Growth**: ~1MB/week

### Flight Recorder Mode (Debug)

**Estimate**: ~50,000 logs/day for 1 user in debugging session
- Clicks: ~1,000/day
- API calls: ~500/day (with full payload)
- Console logs: ~5,000/day
- Performance metrics: ~43,000/day
- Errors: ~500/day

**Database Growth**: ~100MB/day (WHY short retention needed!)

**Mitigation**:
- Flight Recorder retention: 2 days only
- Auto-cleanup: Purge logs older than retention period
- Rate limiting: Max 1000 logs/minute per session

---

## 🎓 Usage Examples

### Scenario 1: Production (Default Mode)

**User Action**: User logs in, views data products, logs out

**Backend Logs**:
```
[INFO] User 'john.doe' logged in successfully
[INFO] GET /api/data-products - Duration: 145ms
[INFO] POST /api/sql/execute - Duration: 234ms
[INFO] User 'john.doe' logged out
```

**Frontend Logs**: None (no automatic logging)

**Total Logs**: 4 entries

---

### Scenario 2: Debugging (Flight Recorder Mode)

**User Action**: User clicks button, form submission fails

**Frontend Logs → Backend**:
```
[INFO] [CLICK] User clicked element: Button#submit
[INFO] [API] Fetch started: POST /api/sql/execute
[ERROR] [API_ERROR] Fetch failed: 400 Bad Request
[ERROR] [CONSOLE_ERROR] Error: Invalid SQL syntax
```

**Backend Logs**:
```
[INFO] POST /api/sql/execute - Payload: { query: "SELECT * FROM..." }
[ERROR] SQL validation failed: Missing FROM clause
[ERROR] Response: 400 Bad Request - Duration: 45ms
```

**Total Logs**: 7 entries (4 frontend + 3 backend)

**AI Analysis**: Can reconstruct entire flow and identify root cause

---

## 🚀 Next Steps

1. **Approve this design** - Confirm requirements met
2. **Prioritize phases** - Which phase to implement first?
3. **Assign resources** - Who implements? (AI-assisted or manual?)
4. **Timeline** - When do you need this operational?

---

## Related Documents

- [[Application Logging]] - Current logging infrastructure
- [[Debug Trace System]] - Existing frontend tracing
- [[Log Intelligence]] - Log analysis capabilities
- [[Feature Flags]] - Configuration management