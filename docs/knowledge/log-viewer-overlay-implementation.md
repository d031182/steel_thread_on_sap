# Log Viewer Overlay Implementation

**Date**: 2026-02-16  
**Pattern**: Shell Overlay (same as AI Assistant)  
**Status**: ✅ Complete

---

## Overview

The Log Viewer is implemented as a **shell overlay** (full-screen modal), following the same pattern as the AI Assistant. No navigation tab is needed.

### Access Method

**ShellBar Button**:
- Icon: `sap-icon://log`
- Tooltip: "Log Viewer"
- Position: Right side of ShellBar, after AI Assistant button
- Action: Opens full-screen log viewer overlay

---

## Architecture

### Pattern: Shell Overlay

**Why This Pattern?**:
- ✅ Consistent with AI Assistant UX
- ✅ No navigation tab needed (reduces clutter)
- ✅ Full-screen viewing for better log visibility
- ✅ Can be opened/closed independently of navigation

**Similarities with AI Assistant**:
| Feature | AI Assistant | Log Viewer |
|---------|-------------|-----------|
| Trigger | ShellBar button | ShellBar button |
| Pattern | Full-screen overlay | Full-screen overlay |
| Z-index | 10000 | 10000 |
| Top offset | 60px (shellbar) | 60px (shellbar) |
| Close button | Yes | Yes |
| No nav tab | ✅ | ✅ |

---

## Implementation

### 1. Frontend Overlay (`LogViewerOverlay.js`)

**File**: `modules/logger/frontend/views/LogViewerOverlay.js`

**Structure**:
```javascript
window.LogViewerOverlay = {
    open: function() {
        // Create and open dialog
    },
    
    close: function() {
        // Close and destroy dialog
    },
    
    _createDialog: function() {
        // Create sap.m.Dialog with table
    },
    
    _loadLogs: function() {
        // Fetch logs from /api/logger/logs
    },
    
    _displayLogs: function(logs) {
        // Populate table
    }
};
```

**Features**:
- 📊 **Table View**: Timestamp, Level, Category, Message columns
- 🔍 **Filters**: By level (ERROR, WARN, INFO) and category
- 🔄 **Refresh**: Manual refresh button
- 📤 **Export**: Download logs as JSON
- 🎚️ **Mode Toggle**: Switch between Default and Flight Recorder modes
- ⚡ **Auto-refresh**: Polls every 5 seconds in Flight Recorder mode

### 2. ShellBar Integration

**File**: `app_v2/static/index.html`

```javascript
// In ShellBar additionalContent array
new sap.m.Button({
    icon: "sap-icon://log",
    tooltip: "Log Viewer",
    press: function() {
        if (window.LogViewerOverlay) {
            window.LogViewerOverlay.open();
        }
    }
}),
```

### 3. Module Configuration

**File**: `modules/logger/module.json`

```json
{
  "id": "logger",
  "frontend": {
    "scripts": [
      "/modules/logger/views/LogViewerOverlay.js"
    ],
    "entry_point": {
      "overlay": "LogViewerOverlay",
      "open_function": "open"
    }
  }
}
```

**Key Changes from Standard Module**:
- ❌ NO `page_name` (not a navigation page)
- ❌ NO `nav_title` or `nav_icon` (no tab)
- ❌ NO `route` (not routed)
- ✅ Uses `overlay` entry point (like AI Assistant)

---

## UI Components

### Dialog Layout

```
┌─────────────────────────────────────────────────────────┐
│ Log Viewer                                    [Refresh] [Close] │
├─────────────────────────────────────────────────────────┤
│ Toolbar:                                                │
│   Level: [All ▾]  Category: [All ▾]  [Default|Flight]  │
│   [Export] [Clear Filters]                              │
├─────────────────────────────────────────────────────────┤
│ Timestamp     | Level   | Category  | Message          │
│ 02/16 23:15:30| ERROR   | API       | Request failed   │
│ 02/16 23:15:25| INFO    | CLICK     | Button clicked   │
│ 02/16 23:15:20| WARN    | CONSOLE   | Slow response    │
│ ...                                                      │
└─────────────────────────────────────────────────────────┘
```

### Toolbar Controls

**Filters**:
- Level dropdown: ALL, ERROR, WARN, INFO
- Category dropdown: ALL, API, CLICK, CONSOLE, ERROR, SAPUI5

**Actions**:
- Refresh button: Reload logs manually
- Clear Filters: Reset to ALL/ALL
- Export button: Download logs as JSON

**Mode Toggle**:
- SegmentedButton: Default | Flight Recorder
- Instantly switches logging mode via API
- Auto-refresh enabled in Flight Recorder mode

---

## API Integration

### GET /api/logger/logs

**Request**:
```javascript
const params = new URLSearchParams({
    limit: 100,
    offset: 0,
    level: 'ERROR',    // optional
    category: 'API'    // optional
});

fetch(`/api/logger/logs?${params}`);
```

**Response**:
```json
{
    "status": "success",
    "data": {
        "logs": [
            {
                "timestamp": "2026-02-16T23:15:30.123Z",
                "level": "ERROR",
                "category": "API",
                "message": "Request failed",
                "details": { ... }
            }
        ],
        "total": 150,
        "limit": 100,
        "offset": 0
    }
}
```

### POST /api/logger/mode

**Request**:
```javascript
fetch('/api/logger/mode', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mode: 'flight_recorder' })
});
```

**Response**:
```json
{
    "status": "success",
    "message": "Logging mode changed to flight_recorder",
    "data": {
        "mode": "flight_recorder",
        "is_flight_recorder": true,
        "features": { ... }
    }
}
```

---

## User Experience

### Opening Log Viewer

1. User clicks **Log** button in ShellBar (sap-icon://log)
2. Full-screen overlay opens instantly
3. Logs loaded from backend (empty if not implemented yet)
4. User can filter, refresh, export

### Closing Log Viewer

- Click **Close** button
- Press ESC key (standard dialog behavior)
- Click outside dialog (if dismissable)

### Flight Recorder Mode

**Activation**:
1. Open Log Viewer
2. Click "Flight Recorder" in mode toggle
3. Mode changed via API
4. Auto-refresh starts (every 5 seconds)
5. Frontend logs now streaming to backend

**Visual Feedback**:
- SegmentedButton shows active mode
- Toast message: "Logging mode changed to flight_recorder"
- Table auto-refreshes with new logs

---

## Files Created/Modified

### New Files (1)
1. `modules/logger/frontend/views/LogViewerOverlay.js` (300+ lines)
   - Full-screen log viewer overlay
   - Table with filters
   - Mode toggle
   - Export functionality

### Modified Files (2)
1. `modules/logger/module.json`
   - Updated scripts array
   - Changed entry_point to overlay pattern
   
2. `app_v2/static/index.html`
   - Added LogViewerOverlay script
   - Added log button to ShellBar

---

## Testing

### Manual Test Steps

1. **Start Server**:
   ```bash
   python server.py
   ```

2. **Open Application**:
   ```
   http://localhost:5000
   ```

3. **Click Log Button**:
   - Look for log icon in ShellBar (right side)
   - Click to open overlay

4. **Test Features**:
   - ✅ Overlay opens full-screen
   - ✅ Table displays (empty message if no logs)
   - ✅ Filters work (Level, Category)
   - ✅ Mode toggle switches between Default/Flight Recorder
   - ✅ Export downloads JSON
   - ✅ Refresh reloads logs
   - ✅ Close button works

5. **Test Flight Recorder**:
   - Switch to Flight Recorder mode
   - Perform actions (click buttons, navigate)
   - Watch logs auto-refresh
   - Verify frontend logs appear in table

---

## Key Differences from App V1

### App V1 Log Viewer
- Navigation page (has route `/logs`)
- Sidebar navigation item
- Part of main application flow

### App V2 Log Viewer
- ✅ Shell overlay (no route)
- ✅ ShellBar button (no sidebar item)
- ✅ Independent of navigation
- ✅ Consistent with AI Assistant pattern

---

## Future Enhancements

### Phase 1 (Current)
- ✅ Shell overlay pattern
- ✅ Basic table view
- ✅ Filters (level, category)
- ✅ Mode toggle
- ✅ Export functionality

### Phase 2 (Planned)
- [ ] Real-time streaming (WebSocket)
- [ ] Log details panel (expand row for full details)
- [ ] Search functionality
- [ ] Time range picker
- [ ] Performance metrics view

### Phase 3 (Advanced)
- [ ] Log correlation (match frontend → backend → database)
- [ ] AI-powered log analysis
- [ ] Anomaly detection
- [ ] Log retention management UI

---

## Related Documentation

- [[Dual Mode Logging System]] - Core logging architecture
- [[AI Assistant Shell Overlay Implementation]] - Reference pattern
- [[Module Federation Standard]] - Module structure guidelines

---

## Design Rationale

### Why Shell Overlay?

**Advantages**:
1. **Accessibility**: Always available (ShellBar button)
2. **Non-intrusive**: Doesn't occupy navigation space
3. **Context-independent**: Can be used from any page
4. **Consistent UX**: Matches AI Assistant pattern

**Comparison**:
| Pattern | Pros | Cons |
|---------|------|------|
| Navigation Tab | Dedicated space | Takes up navigation slot |
| Shell Overlay | Always accessible | Overlays content |
| Modal Dialog | Focused view | Blocks interaction |

**Decision**: Shell Overlay (best balance)

### Why No Module.js Factory?

Unlike typical modules with navigation pages, the log module uses a simpler pattern:
- AI Assistant: `window.AIAssistantOverlay.open()`
- Log Viewer: `window.LogViewerOverlay.open()`

**No need for**:
- ModuleRegistry entry (not a routed page)
- Factory function (overlay is global singleton)
- Complex lifecycle (open/close only)

---

## Success Criteria

✅ **Functional**:
- Log button visible in ShellBar
- Overlay opens on click
- Table displays logs
- Filters work
- Mode toggle functional
- Export works

✅ **UX**:
- Full-screen overlay
- 60px top offset (shellbar clearance)
- Draggable/resizable
- Clean, professional appearance
- Consistent with AI Assistant

✅ **Technical**:
- No console errors
- API calls successful
- Proper cleanup on close
- Memory leak free

---

## Conclusion

The Log Viewer now follows the same shell overlay pattern as the AI Assistant, providing a consistent, accessible, and non-intrusive way to view application logs.

**Key Achievement**: Unified UX pattern across utility features (AI Assistant + Log Viewer), both accessible via ShellBar without navigation tabs.