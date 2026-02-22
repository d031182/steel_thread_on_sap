# Browser Test: Knowledge Graph Rebuild Flow

## Purpose
Verify the complete rebuild flow works in the browser

## Prerequisites
- Server running: `python server.py`
- Browser: Chrome/Firefox/Edge
- URL: http://localhost:5000

## Test Steps

### 1. Navigate to Knowledge Graph V2
1. Open http://localhost:5000
2. Click "Knowledge Graph v2" in navigation

**Expected**: Page loads with placeholder content

### 2. Check Console for Initialization
Open browser DevTools (F12) → Console tab

**Expected logs**:
```
📊 Initializing Knowledge Graph v2 Presenter...
✓ Presenter initialized with Clean Architecture
✓ Backend health: {status: "healthy", version: "2.0.0"}
```

### 3. Click Rebuild Button
Click the blue "Rebuild" button

**Expected**:
1. Toast message: "Rebuilding graph from CSN files..."
2. Loading spinner appears
3. Console logs:
   ```
   Rendering graph: 279 nodes, 297 edges
   ✓ Graph stabilization complete
   ✓ Graph rendered successfully
   ```
4. Graph visualizes with nodes and edges
5. Success dialog: "Graph rebuilt successfully!"

### 4. Verify State in Console
In console, type:
```javascript
window.presenterInstance.getState()
```

**Expected output**:
```javascript
{
  graph: { nodes: DataSet, edges: DataSet },  // <-- NOT null!
  genericGraph: { nodes: Array(279), edges: Array(297) },
  loading: false,
  error: null,
  cacheStatus: { cached: false, csnFilesCount: 8, ... },
  lastRefresh: Date
}
```

### 5. Check Graph Container
In console, type:
```javascript
document.getElementById('kgv2-graph-canvas')
```

**Expected**: Should show canvas element with vis.js network rendered

### 6. Verify Stats Display
Look at info panel above graph

**Expected**:
- Nodes: 279
- Edges: 297  
- CSN Files: 8
- Last Refresh: [timestamp]

## Common Issues

### Issue: Graph stays blank after rebuild
**Debug**:
1. Check console for errors
2. Verify vis.js loaded: `typeof vis` should be "object"
3. Check presenter state: `window.presenterInstance.getState()`
4. Verify data received: Check state.graph and state.genericGraph

### Issue: "Presenter not initialized" message
**Debug**:
1. Check console for initialization errors
2. Verify adapters loaded before presenter
3. Try reloading page

### Issue: Rebuild succeeds but graph doesn't update
**Root Cause**: This was the bug - presenter.rebuild() didn't call loadGraph()
**Fix**: GraphPresenter now automatically loads graph after rebuild

## Success Criteria
- ✅ Graph renders with 279 nodes and 297 edges
- ✅ No console errors
- ✅ Stats display correctly
- ✅ state.graph is NOT null after rebuild