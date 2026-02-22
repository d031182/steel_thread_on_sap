# AI Assistant HANA Datasource Issue - Root Cause Analysis

**Date**: 2026-02-16  
**Status**: 🔴 BUG IDENTIFIED  
**Severity**: Medium (Feature works, but not with HANA datasource)

---

## Executive Summary

The AI Assistant **backend properly uses `/core/interfaces`** (✅ Module Isolation PASS), but there's a **frontend integration bug** where the AI Assistant overlay doesn't pass the currently selected datasource to the backend API.

**Result**: AI always queries SQLite data products, even when user has selected "HANA Cloud" in the dropdown.

---

## Test Results

### ✅ Backend Works Correctly

**Test**: `test_ai_assistant_hana_context.py`

```
================================================================================
✅ TEST PASSED: AI Assistant properly uses HANA context
================================================================================

When context specifies { datasource: "hana" }:
- ✅ Found HANA product: Company Code
- ✅ Found HANA product: Cost Center
- ✅ Found HANA product: Journal Entry
- ✅ Found HANA product: Payment Terms
- ✅ Found HANA product: Product
- ✅ Found HANA product: Purchase Order
- ✅ Found HANA product: Service Entry Sheet
```

**Conclusion**: Backend correctly:
1. Maps `datasource: "hana"` → `facade_key: "hana"`
2. Gets HANA facade from Data Products API
3. Queries HANA data products via `IDataProductRepository` interface
4. Returns HANA data to AI agent

---

## Root Cause Analysis

### Problem Flow

```
User Action:
1. User selects "HANA Cloud" in dropdown on Data Products page
2. User clicks "AI Assistant" button
3. AI Assistant overlay opens
4. User asks "show list of data products"

Current Behavior (❌ BUG):
5. Overlay calls: POST /api/ai-assistant/chat { message: "..." }
6. Backend defaults to: context = { datasource: "p2p_data" }  ← WRONG!
7. AI queries SQLite products
8. Shows Local products instead of HANA

Expected Behavior (✅ FIX):
5. Overlay calls: POST /api/ai-assistant/chat { 
     message: "...", 
     context: { datasource: "hana" }  ← PASS CURRENT DATASOURCE
   }
6. Backend uses: context = { datasource: "hana" }  ← CORRECT!
7. AI queries HANA products
8. Shows HANA products
```

---

## Code Analysis

### Frontend: AIAssistantOverlay.js (❌ Missing Context)

**File**: `modules/ai_assistant/frontend/views/AIAssistantOverlay.js`

**Line 132-139**:
```javascript
_handleSendMessage: function() {
    const message = this._input.getValue().trim();
    // ... validation ...
    
    // ❌ BUG: No context passed!
    this._adapter.sendMessage(message)
        .then(response => { ... })
}
```

**Problem**: 
- Overlay doesn't receive datasource parameter from caller
- Overlay doesn't pass context to adapter
- Adapter doesn't send context to backend

---

### Frontend: AIAssistantAdapter.js (Supports Context)

**File**: `modules/ai_assistant/frontend/adapters/AIAssistantAdapter.js`

**Line 23-43**:
```javascript
async sendMessage(message) {
    const response = await fetch(`${this.baseUrl}/api/ai-assistant/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message })  // ❌ Only message, no context
    });
    return await response.json();
}
```

**Note**: The `/chat` endpoint DOES accept context parameter (see below), but adapter doesn't send it.

---

### Backend: api.py (✅ Supports Context)

**File**: `modules/ai_assistant/backend/api.py`

**Line 483-525**:
```python
@blueprint.route('/chat', methods=['POST'])
def chat():
    """
    Request:
        {
            "message": "User message",
            "conversation_id": "optional-uuid",
            "context": {...}  # ✅ Context IS supported!
        }
    """
    data = request.get_json()
    req = ChatRequest(**data)
    
    # Get or create conversation
    if conversation_id:
        session = conversation_service.get_conversation(conversation_id)
    else:
        # ✅ Creates conversation with context if provided
        session = conversation_service.create_conversation(req.context)
```

**Conclusion**: Backend fully supports context, but frontend doesn't pass it!

---

## Solution Design

### Option 1: Pass Datasource to Overlay Constructor (RECOMMENDED)

**Pros**:
- Clean separation of concerns
- Overlay knows datasource from the start
- Can show datasource in dialog title

**Implementation**:
```javascript
// Data Products Page calls:
const currentDatasource = this._getCurrentDatasource(); // 'hana' or 'p2p_data'
const overlay = new AIAssistantOverlay(adapter, currentDatasource);
overlay.open();

// AIAssistantOverlay.js constructor:
window.AIAssistantOverlay = function(adapter, datasource) {
    this._adapter = adapter;
    this._datasource = datasource || 'p2p_data'; // Default to SQLite
    this._dialog = null;
};

// AIAssistantOverlay.js _handleSendMessage:
_handleSendMessage: function() {
    const message = this._input.getValue().trim();
    
    this._adapter.sendMessage(message, {
        datasource: this._datasource  // ✅ Pass datasource!
    })
    .then(response => { ... });
}

// AIAssistantAdapter.js sendMessage:
async sendMessage(message, context) {
    const response = await fetch(`${this.baseUrl}/api/ai-assistant/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            message,
            context: context || {}  // ✅ Include context!
        })
    });
    return await response.json();
}
```

---

### Option 2: Dynamic Datasource Dropdown in Overlay

**Pros**:
- User can switch datasource without closing overlay
- More flexible

**Cons**:
- More UI complexity
- Need to handle conversation reset when datasource changes

**Implementation**:
- Add datasource dropdown to overlay toolbar
- Listen for changes
- Create new conversation when datasource changes

---

### Option 3: EventBus Pattern (App-Wide Datasource)

**Pros**:
- Centralized datasource state
- All components auto-sync

**Cons**:
- More complex architecture
- Requires EventBus implementation

---

## Recommended Fix (Option 1)

### Step 1: Update AIAssistantAdapter

**File**: `modules/ai_assistant/frontend/adapters/AIAssistantAdapter.js`

```javascript
async sendMessage(message, context) {
    const response = await fetch(`${this.baseUrl}/api/ai-assistant/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            message,
            context: context || {}
        })
    });
    return await response.json();
}
```

### Step 2: Update AIAssistantOverlay Constructor

**File**: `modules/ai_assistant/frontend/views/AIAssistantOverlay.js`

```javascript
window.AIAssistantOverlay = function(adapter, datasource) {
    this._adapter = adapter;
    this._datasource = datasource || 'p2p_data';
    this._dialog = null;
};
```

### Step 3: Update Overlay Message Sender

```javascript
_handleSendMessage: function() {
    const message = this._input.getValue().trim();
    // ...
    
    this._adapter.sendMessage(message, {
        datasource: this._datasource
    })
    .then(response => { ... });
}
```

### Step 4: Update Dialog Title (Show Datasource)

```javascript
_createDialog: function() {
    const datasourceLabel = this._datasource === 'hana' ? 'HANA Cloud' : 'Local';
    
    this._dialog = new sap.m.Dialog({
        title: `Joule AI Assistant (${datasourceLabel})`,
        // ...
    });
}
```

### Step 5: Update Data Products Page (Call Site)

**File**: Find where AI Assistant overlay is opened (likely in Data Products module)

```javascript
// Get current datasource from dropdown
const currentDatasource = this._datasourceComboBox.getSelectedKey(); // 'hana' or 'p2p_data'

// Pass to overlay
const overlay = new AIAssistantOverlay(this._aiAdapter, currentDatasource);
overlay.open();
```

---

## Testing Plan

### 1. Manual Testing

```
Test Case 1: Local Datasource
1. Open Data Products page
2. Select "Local" from dropdown
3. Click "AI Assistant"
4. Ask "show list of data products"
Expected: Shows SQLite products (CompanyCode, CostCenter, etc.)

Test Case 2: HANA Datasource
1. Open Data Products page
2. Select "HANA Cloud" from dropdown
3. Click "AI Assistant"
4. Ask "show list of data products"
Expected: Shows HANA products (Company Code, Cost Center, Purchase Order, etc.)

Test Case 3: Switch Datasource
1. Open with "Local", ask question
2. Close overlay
3. Switch to "HANA Cloud"
4. Reopen overlay, ask question
Expected: Shows HANA products (new conversation with HANA context)
```

### 2. Automated API Testing

**File**: `test_ai_assistant_hana_context.py` (Already created)

Run: `python test_ai_assistant_hana_context.py`

Expected: ✅ All tests pass

---

## Impact Analysis

### Module Isolation: ✅ NO IMPACT

This fix **does NOT affect module isolation**:
- AI Assistant still uses only `IDataProductRepository` interface
- No new cross-module imports
- Pure frontend parameter passing
- Backend already supports context

### Files to Change

1. `modules/ai_assistant/frontend/adapters/AIAssistantAdapter.js` (1 method)
2. `modules/ai_assistant/frontend/views/AIAssistantOverlay.js` (2 methods)
3. `modules/data_products_v2/frontend/[view].js` (1 line - pass datasource)

**Complexity**: LOW (< 30 lines of code)  
**Risk**: LOW (Backward compatible - context optional)

---

## Related Documents

- [[AI Assistant Module Isolation Audit]] - Module isolation compliance (A+ grade)
- [[Module Isolation Enforcement Standard]] - Architecture rules
- [[AI Assistant UX Design]] - Original design documents
- [[API First Contract Testing Methodology]] - Testing approach

---

**Status**: 🔴 BUG IDENTIFIED, SOLUTION DESIGNED  
**Next Step**: Implement Option 1 (Pass Datasource to Constructor)  
**Priority**: MEDIUM (Feature works, but HANA datasource not accessible via UI)