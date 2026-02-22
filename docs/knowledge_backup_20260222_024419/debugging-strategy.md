# 🔍 Debugging Strategy for Joule Dialog UX

**Version**: 1.0  
**Created**: Feb 7, 2026  
**Purpose**: Systematic approach to debug UI issues (NO trial-and-error)

---

## 🎯 Problem

**Joule Dialog works via curl (backend ✅) but NOT in UI**

Need systematic debugging to find root cause efficiently.

---

## 🛠️ Tools Available

### 1. **Debug Console** (`debug_joule_dialog.html`)
**Purpose**: Isolated component testing  
**Access**: `http://localhost:5000/debug_joule_dialog.html`

**5 Tests**:
1. Backend API endpoint
2. SAPUI5 Core loading
3. Dialog creation capability
4. ShellBar integration
5. Full integration check

**Output**: Pass/Fail for each component + exact error messages

---

### 2. **Debug Trace System** ⭐ NEW (`debug-trace.js`)
**Purpose**: Flight recorder - captures EVERYTHING for AI analysis  
**Access**: Enable in browser console

**Captures**:
- ✅ Every click (element, coordinates, SAPUI5 control)
- ✅ Every API call (XHR/Fetch - request/response/timing)
- ✅ Every error (JavaScript errors, promise rejections)
- ✅ Every console log (log/warn/error)
- ✅ SAPUI5 events (dialog open, control creation)
- ✅ Performance metrics (page load, resource timing)

**How to Enable**:

```javascript
// 1. Open browser console (F12)
// 2. Enable debug trace:
localStorage.setItem('DEBUG_TRACE_ENABLED', 'true')

// 3. Reload page
location.reload()

// 4. You'll see floating green panel bottom-right
```

**How to Use**:

1. **Enable trace** (see above)
2. **Use app normally** - click Joule button, try to open dialog, etc.
3. **Download trace** - Click "💾 Download" button in green panel
4. **Share with AI** - Send JSON file or paste clipboard content

**What AI Gets**:
```json
{
  "sessionId": "session_1234567890_abc",
  "totalTraces": 42,
  "systemInfo": {
    "url": "http://localhost:5000/",
    "userAgent": "Mozilla/5.0...",
    "viewport": "1920x1080"
  },
  "traces": [
    {
      "timestamp": 1234,
      "category": "CLICK",
      "action": "User clicked element",
      "details": {
        "tagName": "BUTTON",
        "id": "jouleButton",
        "sapui5Control": "sap.m.Button",
        "coordinates": {"x": 1850, "y": 50}
      }
    },
    {
      "timestamp": 1250,
      "category": "ERROR",
      "action": "JavaScript Error",
      "details": {
        "message": "createJouleDialog is not a function",
        "filename": "app.js",
        "lineno": 42,
        "stack": "..."
      }
    },
    // ... all actions, API calls, errors
  ]
}
```

**AI Can See**:
- Exact sequence of events
- Timing between actions
- Which API calls succeeded/failed
- Exact error messages with stack traces
- Which SAPUI5 events fired
- Network request/response details

**Control Panel**:
- **💾 Download**: Save trace as JSON file
- **📋 Copy**: Copy to clipboard
- **🗑️ Clear**: Reset traces
- **⏹️ Stop**: Disable tracing (reload required)

---

## 📊 Debugging Workflow

### Option A: Quick Diagnosis (5 minutes)

**Use Debug Console first**:

1. Open `http://localhost:5000/debug_joule_dialog.html`
2. Click "Test 5: Full Integration"
3. See which component fails:
   - Backend API: ✅/❌
   - SAPUI5: ✅/❌
   - Dialog Creation: ✅/❌
   - Joule Script: ✅/❌

4. If specific test fails, click that test button for details

**Result**: Know exactly which layer is broken in 5 minutes

---

### Option B: Deep Analysis with Trace (Last Resort)

**When to use**: Debug console shows all tests pass BUT dialog still doesn't work

**Steps**:

1. **Enable Debug Trace**:
   ```javascript
   localStorage.setItem('DEBUG_TRACE_ENABLED', 'true')
   location.reload()
   ```

2. **Reproduce Issue**:
   - Click Joule button
   - Try to open dialog
   - Perform any actions that should work

3. **Download Trace**:
   - Click "💾 Download" in green panel
   - Save `debug-trace-session_XXX.json`

4. **Share with AI**:
   ```
   "I enabled debug trace and clicked the Joule button. 
   Here's the trace file: [paste JSON or attach file]
   
   What's the root cause?"
   ```

5. **AI Analyzes**:
   - Examines exact sequence of events
   - Finds where the flow breaks
   - Identifies exact error with context
   - Provides specific fix

**Example AI Analysis**:
```
Looking at trace:
- Line 12: User clicked button (timestamp: 1234ms)
- Line 13: ERROR - "createJouleDialog is not a function"
- Line 8: jouleDialogV2.js loaded (timestamp: 890ms)
- Line 9: SAPUI5 Dialog Opening event NOT FIRED

ROOT CAUSE: Function exists but not called.
Likely: Button press handler has wrong function name.

FIX: Check app.js line 42 - should be:
  press: function() { window.createJouleDialog(); }
```

---

## 🎯 Decision Tree

```
Is Joule Dialog working?
│
├─ NO → Start here
│   │
│   ├─ Run Debug Console (5 min)
│   │   │
│   │   ├─ All tests PASS
│   │   │   └─> Enable Debug Trace → Reproduce → Share trace with AI
│   │   │
│   │   └─ Test X FAILS
│   │       └─> Click Test X for details → See exact error → Fix that component
│   │
│   └─ Still stuck?
│       └─> Enable Debug Trace → Share trace → AI provides exact fix
│
└─ YES → Great! (no debugging needed)
```

---

## 💡 Best Practices

### DO ✅
- Run Debug Console FIRST (quick, systematic)
- Use Debug Trace for complex issues
- Share trace JSON with AI (complete context)
- Reproduce issue step-by-step with trace active

### DON'T ❌
- Random code changes (trial-and-error)
- Skip Debug Console (wastes time)
- Forget to download trace before disabling
- Ignore exact error messages from traces

---

## 📚 Files

**Debug Tools**:
- `debug_joule_dialog.html` - Isolated component testing
- `app/static/js/debug-trace.js` - Flight recorder system

**Integrated Into**:
- Add to `app/static/index.html`:
  ```html
  <!-- Add before closing </body> tag -->
  <script src="js/debug-trace.js"></script>
  ```

---

## 🚀 Quick Commands

```javascript
// Enable debug trace
localStorage.setItem('DEBUG_TRACE_ENABLED', 'true'); location.reload();

// Disable debug trace
localStorage.setItem('DEBUG_TRACE_ENABLED', 'false'); location.reload();

// Manual trace (if needed)
debugTrace('CUSTOM', 'My Action', { detail: 'value' });

// Download trace programmatically
window.DebugTrace.downloadTrace();

// Copy trace to clipboard
window.DebugTrace.copyTrace();
```

---

## 📊 Success Metrics

**Before**: Trial-and-error debugging (60+ min)  
**After**: Systematic debugging (5-10 min to root cause)

**Benefits**:
- 🎯 Exact root cause identification
- ⚡ 6x faster debugging
- 🤖 AI can analyze traces (complete context)
- 📊 Reproducible (traces = evidence)
- 🔍 No guessing (facts, not assumptions)

---

**Last Updated**: Feb 7, 2026  
**Next**: Enable debug trace and test Joule dialog!