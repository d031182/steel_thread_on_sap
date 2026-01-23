# Debug Mode Feature Implementation Plan

**Feature**: Debug Mode Toggle for Enhanced Troubleshooting  
**Date**: January 23, 2026, 10:08 PM  
**Status**: In Progress  

---

## Overview

Add a debug mode toggle to the Log Viewer dialog that enables detailed execution logging for troubleshooting purposes.

## Requirements

### User-Facing Features
1. Toggle button in Log Viewer dialog
2. Visual state indicator (OFF/ON with color coding)
3. Persists across page reloads (localStorage)
4. Easy to activate/deactivate
5. Shows debug logs in console and backend

### Technical Features
1. **Frontend Debug Logger** - Singleton service
2. **localStorage persistence** - survives browser refresh
3. **Function entry/exit logging** - automatic tracing
4. **Parameter & result logging** - detailed data capture
5. **Performance timing** - execution time tracking
6. **Backend integration** - send debug logs to server

---

## Implementation Steps

### Phase 1: Debug Logger Service (30 min)
**File**: `web/current/js/utils/debugLogger.js`

Features:
- Singleton pattern
- localStorage state management
- Conditional logging (only when enabled)
- Entry/exit tracing
- Performance timing
- Backend log sending

### Phase 2: UI Integration (15 min)
**File**: `web/current/index.html`

Changes:
- Add Debug Mode toggle button to Log Viewer dialog
- Color-coded state indicator
- Event handler for toggle
- Update dialog layout

### Phase 3: Function Instrumentation (15 min)
**Files**: `web/current/index.html`

Add debug logging to key functions:
- `showTableStructure()`
- `showTableData()`
- `openProductDetailDialog()`
- `loadDataProducts()`

### Phase 4: Testing & Documentation (10 min)
- Test toggle functionality
- Verify localStorage persistence
- Test debug log output
- Update documentation

---

## Technical Design

### Debug Logger API

```javascript
class DebugLogger {
    // Singleton instance
    static instance = null;
    
    // State
    isEnabled() { }
    enable() { }
    disable() { }
    toggle() { }
    
    // Logging
    log(message, data) { }
    entry(functionName, params) { }
    exit(functionName, result, startTime) { }
    error(functionName, error) { }
    
    // Performance
    startTimer() { }
    endTimer(label, startTime) { }
}
```

### Storage Format

```javascript
localStorage.setItem('debugMode', 'true' | 'false')
```

### Debug Log Format

```javascript
{
    timestamp: '2026-01-23T22:08:00.000Z',
    type: 'ENTRY' | 'EXIT' | 'LOG' | 'ERROR',
    function: 'functionName',
    data: { /* contextual data */ },
    duration: 123 // ms (for EXIT)
}
```

---

## UI Design

### Log Viewer Dialog Addition

```
┌─────────────────────────────────────────┐
│  Application Logs                  [X]  │
├─────────────────────────────────────────┤
│  Logs (100)  [All] [Info] [Warning]    │
│  [Error] [🔄 Refresh] [🗑️ Clear]       │
│  [🐛 Debug Mode: OFF]  ← NEW BUTTON    │
├─────────────────────────────────────────┤
│  Time    Level   Message                │
│  ─────────────────────────────────────  │
│  ...logs...                             │
└─────────────────────────────────────────┘
```

**Button States**:
- OFF: Gray background, text "Debug Mode: OFF"
- ON: Green background, text "Debug Mode: ON"

---

## Example Usage

### Scenario: Troubleshoot Structure Dialog

**Step 1**: User enables Debug Mode
```
[Clicks "Debug Mode: OFF" button]
→ Button becomes green: "Debug Mode: ON"
→ Toast: "Debug Mode enabled"
```

**Step 2**: User reproduces issue
```
[Clicks Structure button]
→ Console shows detailed trace:
  [DEBUG] ENTRY: showTableStructure(schema, table)
  [DEBUG]   params: {schema: "...", table: "..."}
  [DEBUG] LOG: Calling getTableStructure API
  [DEBUG] LOG: API result received
  [DEBUG]   data: {success: true, columns: [...]}
  [DEBUG] LOG: Creating dialog with 34 columns
  [DEBUG] EXIT: showTableStructure - 125ms
```

**Step 3**: AI analyzes logs
```
Me: "I can see the issue - in the LOG entry at step 3,
     the columns array has lowercase property names
     but the UI is trying to access uppercase names."
```

---

## Files to Create/Modify

### New Files
1. `web/current/js/utils/debugLogger.js` (NEW) - Debug service
2. `DEBUG_MODE_FEATURE_PLAN.md` (THIS FILE) - Implementation plan

### Modified Files
1. `web/current/index.html` - Add toggle button + instrument functions
2. `backend/app.py` - Optional: Add debug log endpoint

---

## Success Criteria

- [x] Plan created
- [ ] Debug logger service implemented
- [ ] UI toggle button added
- [ ] localStorage persistence working
- [ ] Key functions instrumented
- [ ] Testing complete
- [ ] Documentation updated
- [ ] Committed to Git

---

## Timeline

**Total Estimated Time**: 70 minutes
- Phase 1 (Debug Logger): 30 min
- Phase 2 (UI Integration): 15 min
- Phase 3 (Instrumentation): 15 min
- Phase 4 (Testing & Docs): 10 min

**Start**: 10:08 PM
**Expected Completion**: 11:18 PM

---

## Notes

- Keep debug logging lightweight (performance)
- Only log when debug mode enabled
- Clear, structured log format
- Easy to enable/disable
- Useful for AI troubleshooting