# Logger Module

**Version**: 1.0.0  
**Status**: ✅ Backend Complete | 🚧 Frontend In Progress  
**App Version**: V2

---

## Overview

Modern dual-mode logging system for the P2P Data Products application.

### Two Logging Modes

1. **DEFAULT Mode** (Production)
   - Business-level activity tracking only
   - Minimal overhead, audit-focused
   - Logs: User auth, API calls, business operations, errors
   - Frontend: ERROR logs only

2. **FLIGHT RECORDER Mode** (Debug)
   - Comprehensive end-to-end tracing
   - Everything logged (clicks, console, network, performance)
   - Frontend: ALL logs sent to backend
   - Purpose: Troubleshooting and AI-assisted analysis

---

## Architecture

### Backend (✅ Complete)

**Components**:
- `logging_modes.py`: LoggingModeManager (dual-mode configuration)
- `api.py`: Flask REST API (4 endpoints)
- Singleton pattern for global mode management
- Environment variable support (`LOGGING_MODE`)

**API Endpoints**:
```
GET  /api/logger/mode       - Get current logging mode
POST /api/logger/mode       - Set logging mode
POST /api/logger/client     - Receive frontend logs
GET  /api/logger/logs       - Retrieve logs (TODO)
GET  /api/logger/health     - Health check
```

**Example Usage**:
```python
from modules.logger.backend.logging_modes import logging_mode_manager, LoggingMode

# Check current mode
if logging_mode_manager.is_flight_recorder():
    # Log detailed information
    pass

# Switch modes
logging_mode_manager.mode = LoggingMode.FLIGHT_RECORDER
```

### Frontend (🚧 In Progress)

**Planned Components**:
- `module.js`: Factory pattern (App V2)
- `FlightRecorderInterceptor.js`: Captures clicks, console, network, errors
- `loggerPage.js`: SAPUI5 log viewer UI
- `LoggerAdapter.js`: API client

---

## Configuration

### Environment Variable
```bash
# In .env file
LOGGING_MODE=default          # or "flight_recorder"
```

### Feature Flags (Integration Pending)
```json
{
  "logging_mode": {
    "enabled": true,
    "mode": "default",
    "allowedValues": ["default", "flight_recorder"]
  }
}
```

### LocalStorage (Frontend)
```javascript
// Switch mode in browser
localStorage.setItem('LOGGING_MODE', 'flight_recorder');
location.reload();
```

---

## Testing

### Unit Tests (✅ 13/13 Passing)

```bash
# Run logger tests
pytest modules/logger/tests/unit/test_logging_modes.py -v

# Results: 13 passed in 3.43s
```

**Test Coverage**:
- ✅ LoggingMode enum
- ✅ LoggingModeManager initialization
- ✅ Environment variable support
- ✅ Mode switching
- ✅ Feature flags (all modes)
- ✅ Dictionary export

---

## Usage Examples

### Switching Modes

**Via API**:
```bash
# Set to Flight Recorder mode
curl -X POST http://localhost:5000/api/logger/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "flight_recorder"}'

# Check current mode
curl http://localhost:5000/api/logger/mode
```

**Via Python**:
```python
from modules.logger.backend.logging_modes import logging_mode_manager, LoggingMode

# Set mode
logging_mode_manager.mode = LoggingMode.FLIGHT_RECORDER

# Check features
if logging_mode_manager.should_log_request_details():
    # Log full request payload
    pass
```

### Frontend Logging (When Complete)

**Default Mode** (ERROR only):
```javascript
// Only errors sent to backend
console.error("Critical error occurred");
// → Sent to /api/logger/client
```

**Flight Recorder Mode** (ALL):
```javascript
// Everything sent to backend
console.log("User clicked button");     // → Sent
console.warn("API response slow");      // → Sent
console.error("Request failed");         // → Sent
```

---

## Integration Status

### ✅ Complete
- [x] LoggingModeManager (dual-mode config)
- [x] REST API endpoints
- [x] Unit tests (13 passing)
- [x] module.json (App V2 config)

### 🚧 In Progress
- [ ] Frontend module factory
- [ ] Flight Recorder interceptor
- [ ] Log viewer UI (SAPUI5)
- [ ] API client adapter

### 📋 Pending
- [ ] Database persistence (LogRepository)
- [ ] Feature flag integration
- [ ] Integration tests
- [ ] E2E tests
- [ ] Performance testing (Flight Recorder overhead)

---

## Design Decisions

### Why Two Modes?

**Production (DEFAULT)**:
- Low overhead → No performance impact
- Audit-focused → Compliance (GDPR)
- Minimal noise → Easy to review

**Debug (FLIGHT RECORDER)**:
- Opt-in → Only when needed
- Comprehensive → Complete picture for troubleshooting
- Temporary → Short retention (2 days)

### Why Send Frontend Logs to Backend?

**Benefits**:
1. **Centralized**: All logs in one place (frontend + backend)
2. **Correlation**: Match frontend click → API call → database query
3. **Persistent**: Survives browser refresh
4. **AI-Ready**: Backend can analyze patterns
5. **Timeline**: Reconstruct exact event sequence

**Mitigation**:
- Use `sendBeacon` (non-blocking)
- Rate limiting (max 1000 logs/min)
- Shorter retention for Flight Recorder logs

---

## Performance Considerations

### Expected Log Volume

**DEFAULT Mode**:
- ~500 logs/day (10 users)
- ~1MB/week database growth

**FLIGHT RECORDER Mode**:
- ~50,000 logs/day (1 user debugging)
- ~100MB/day database growth
- **WHY** short retention needed (2 days max)

---

## Related Documentation

- [[Dual-Mode Logging System Design]] - Complete design proposal
- [[Application Logging]] - Current logging infrastructure
- [[App V2 Architecture]] - Modular architecture guide

---

## Changelog

### v1.0.0 (2026-02-13)
- ✅ Initial backend implementation
- ✅ LoggingModeManager with dual-mode support
- ✅ REST API (4 endpoints)
- ✅ Unit tests (13 passing)
- ✅ App V2 module configuration