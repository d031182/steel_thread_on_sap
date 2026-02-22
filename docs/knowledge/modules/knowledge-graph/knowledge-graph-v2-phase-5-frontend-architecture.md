# Knowledge Graph v2 - Phase 5: Frontend Architecture

**Status**: Planning Phase  
**Approach**: Clean Architecture (matching backend quality)  
**Estimated Effort**: 4-6 hours  
**Goal**: Production-ready frontend with proper separation of concerns

---

## Architecture Overview

### Clean Architecture Layers (Frontend)

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  (UI Components - SAPUI5/Fiori, DOM manipulation)           │
│  - knowledgeGraphPageV2.js                                  │
│  - Renders vis.js network visualization                     │
│  - User interaction handlers (zoom, filter, search)         │
└─────────────────────────────────────────────────────────────┘
                            ↓ uses
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTER LAYER                           │
│  (View Models, UI State Management)                         │
│  - GraphPresenter.js                                        │
│  - Transforms domain data → UI-ready format                 │
│  - Manages UI state (loading, error, success)               │
│  - Handles user actions (rebuild, refresh, clear cache)     │
└─────────────────────────────────────────────────────────────┘
                            ↓ uses
┌─────────────────────────────────────────────────────────────┐
│                    ADAPTER LAYER                             │
│  (Format Conversion, API Communication)                     │
│  - VisJsGraphAdapter.js (Generic → vis.js format)          │
│  - KnowledgeGraphApiClient.js (HTTP client)                 │
│  - Handles format transformations                           │
│  - Abstracts API communication                              │
└─────────────────────────────────────────────────────────────┘
                            ↓ uses
┌─────────────────────────────────────────────────────────────┐
│                    API LAYER                                 │
│  (Backend v2 REST API)                                      │
│  - GET /api/knowledge-graph/schema                       │
│  - POST /api/knowledge-graph/schema/rebuild              │
│  - GET /api/knowledge-graph/status                       │
│  - DELETE /api/knowledge-graph/cache                     │
└─────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
modules/knowledge_graph_v2/
├── frontend/
│   ├── adapters/
│   │   ├── VisJsGraphAdapter.js          # Generic → vis.js converter
│   │   └── KnowledgeGraphApiClient.js    # API HTTP client
│   ├── presenters/
│   │   └── GraphPresenter.js             # View model + state management
│   ├── views/
│   │   └── knowledgeGraphPageV2.js       # UI rendering + interactions
│   ├── styles/
│   │   └── knowledgeGraphV2.css          # Component-specific styles
│   └── index.html                         # Standalone page (optional)
├── tests/
│   └── frontend/
│       ├── adapters/
│       │   ├── test_VisJsGraphAdapter.js
│       │   └── test_ApiClient.js
│       ├── presenters/
│       │   └── test_GraphPresenter.js
│       └── integration/
│           └── test_e2e_flow.js
└── README.md
```

---

## Component Responsibilities

### 1. VisJsGraphAdapter (Adapter Layer)

**Purpose**: Convert generic graph format → vis.js format

**Input** (Generic from backend):
```javascript
{
  nodes: [
    { id: "Product", label: "Product", type: "TABLE", properties: {...} }
  ],
  edges: [
    { source: "Product", target: "Supplier", label: "FOREIGN_KEY" }
  ]
}
```

**Output** (vis.js format):
```javascript
{
  nodes: [
    { id: "Product", label: "Product", group: "TABLE", title: "..." }
  ],
  edges: [
    { from: "Product", to: "Supplier", label: "FOREIGN_KEY", arrows: "to" }
  ]
}
```

**Methods**:
- `convertToVisJs(genericGraph)` - Main conversion
- `convertNode(genericNode)` - Node conversion
- `convertEdge(genericEdge)` - Edge conversion
- `getNodeStyle(nodeType)` - Styling based on type

---

### 2. KnowledgeGraphApiClient (Adapter Layer)

**Purpose**: Abstract API communication, handle errors

**Methods**:
- `async getSchemaGraph(useCache = true)` - GET /schema
- `async rebuildSchemaGraph()` - POST /schema/rebuild
- `async getStatus()` - GET /status
- `async clearCache()` - DELETE /cache
- `async healthCheck()` - GET /health

**Error Handling**:
- Network errors
- HTTP errors (400, 500)
- Timeout handling
- Retry logic (optional)

---

### 3. GraphPresenter (Presenter Layer)

**Purpose**: Manage UI state, coordinate adapter + view

**State Management**:
```javascript
{
  graph: null,              // Current graph data
  loading: false,           // Loading indicator
  error: null,              // Error message
  cacheStatus: {
    cached: false,
    csnFilesCount: 0
  }
}
```

**Methods**:
- `async loadGraph(useCache)` - Load and present graph
- `async rebuild()` - Force rebuild
- `async refresh()` - Refresh current view
- `async clearCache()` - Clear backend cache
- `handleError(error)` - Error presentation
- `updateView()` - Notify view of state changes

**Observer Pattern**:
- View subscribes to presenter state changes
- Presenter notifies view when state updates
- Decouples presenter from view implementation

---

### 4. knowledgeGraphPageV2.js (Presentation Layer)

**Purpose**: Render UI, handle user interactions

**UI Components**:
1. **Header Bar** (SAPUI5 Bar)
   - Title: "Knowledge Graph v2"
   - Refresh button
   - Rebuild button
   - Clear cache button (admin)
   
2. **Status Panel** (SAPUI5 ObjectStatus)
   - Cache status indicator
   - CSN files count
   - Last refresh time

3. **Graph Container** (vis.js Network)
   - Interactive graph visualization
   - Zoom controls
   - Search/filter (future)

4. **Loading Overlay**
   - Busy indicator during async operations

**Event Handlers**:
- `onRefresh()` - Reload graph (with cache)
- `onRebuild()` - Force rebuild (no cache)
- `onClearCache()` - Clear cache + reload
- `onNodeClick(nodeId)` - Show node details
- `onZoomIn/Out()` - Graph zoom controls

---

## Data Flow Example

### User clicks "Refresh" button:

```
1. View Layer (knowledgeGraphPageV2.js)
   └─> onRefresh() called
       └─> presenter.loadGraph(useCache=true)

2. Presenter Layer (GraphPresenter.js)
   └─> setState({ loading: true })
   └─> notifyView() // Show loading indicator
   └─> apiClient.getSchemaGraph(true)

3. Adapter Layer (KnowledgeGraphApiClient.js)
   └─> fetch('/api/knowledge-graph/schema?use_cache=true')
   └─> Response: { success: true, graph: {...}, cache_used: true }
   └─> return genericGraph

4. Presenter Layer (GraphPresenter.js)
   └─> visJsAdapter.convertToVisJs(genericGraph)
   └─> setState({ graph: visJsGraph, loading: false })
   └─> notifyView() // Update with new data

5. View Layer (knowledgeGraphPageV2.js)
   └─> onStateChange(newState)
   └─> Hide loading indicator
   └─> Render graph with vis.js
```

---

## Testing Strategy

### Unit Tests (Jest/Mocha + Chai)

**Adapter Tests**:
```javascript
describe('VisJsGraphAdapter', () => {
  it('converts generic node to vis.js format', () => {
    const generic = { id: 'n1', label: 'Product', type: 'TABLE' };
    const visJs = adapter.convertNode(generic);
    
    expect(visJs).to.deep.equal({
      id: 'n1',
      label: 'Product',
      group: 'TABLE',
      shape: 'box',
      color: {...}
    });
  });
  
  it('converts generic edge to vis.js format', () => {
    const generic = { source: 'n1', target: 'n2', label: 'FK' };
    const visJs = adapter.convertEdge(generic);
    
    expect(visJs).to.deep.equal({
      from: 'n1',
      to: 'n2',
      label: 'FK',
      arrows: 'to'
    });
  });
});
```

**API Client Tests** (with mocks):
```javascript
describe('KnowledgeGraphApiClient', () => {
  it('fetches schema graph successfully', async () => {
    // Mock fetch
    global.fetch = sinon.stub().resolves({
      ok: true,
      json: async () => ({ success: true, graph: {...} })
    });
    
    const result = await client.getSchemaGraph();
    
    expect(result.success).to.be.true;
    expect(result.graph).to.exist;
  });
  
  it('handles 500 errors gracefully', async () => {
    global.fetch = sinon.stub().resolves({
      ok: false,
      status: 500,
      json: async () => ({ success: false, error: 'Internal error' })
    });
    
    await expect(client.getSchemaGraph()).to.be.rejectedWith('Internal error');
  });
});
```

**Presenter Tests**:
```javascript
describe('GraphPresenter', () => {
  it('updates loading state during load', async () => {
    const states = [];
    presenter.subscribe((state) => states.push(state.loading));
    
    await presenter.loadGraph();
    
    expect(states).to.deep.equal([true, false]);
  });
  
  it('handles API errors gracefully', async () => {
    apiClient.getSchemaGraph = sinon.stub().rejects(new Error('API error'));
    
    await presenter.loadGraph();
    
    expect(presenter.state.error).to.equal('API error');
    expect(presenter.state.loading).to.be.false;
  });
});
```

### Integration Tests (Playwright)

**E2E Flow Test**:
```javascript
test('full graph visualization flow', async ({ page }) => {
  // Navigate to page
  await page.goto('http://localhost:5001/knowledge-graph-v2');
  
  // Wait for initial load
  await page.waitForSelector('.vis-network');
  
  // Verify graph rendered
  const nodes = await page.$$('.vis-node');
  expect(nodes.length).toBeGreaterThan(0);
  
  // Click refresh button
  await page.click('#refreshButton');
  await page.waitForSelector('.vis-network');
  
  // Click rebuild button
  await page.click('#rebuildButton');
  await page.waitForSelector('.sapMBusyIndicator', { state: 'hidden' });
  
  // Verify graph updated
  const updatedNodes = await page.$$('.vis-node');
  expect(updatedNodes.length).toBeGreaterThan(0);
});
```

---

## SAP Fiori Compliance

**Follow v2 standards** (see .clinerules):
1. ✅ Use standard SAPUI5 controls (Bar, Button, ObjectStatus)
2. ✅ Built-in properties for sizing (width, height, contentWidth)
3. ✅ CSS only for colors/animations, NOT layout
4. ✅ Pure JavaScript (easier debugging than XML)
5. ✅ Start simple → incremental complexity

**Control Selection**:
- Header: `sap.m.Bar` with `sap.m.Button` actions
- Status: `sap.m.ObjectStatus` for cache indicator
- Container: Standard `div` for vis.js network
- Loading: `sap.m.BusyIndicator` overlay

---

## Implementation Plan

### Phase 5.1: Adapter Layer (Foundation)
1. Create `VisJsGraphAdapter.js` with conversion logic
2. Create `KnowledgeGraphApiClient.js` with API methods
3. Write unit tests for both adapters
4. **Deliverable**: Generic → vis.js conversion working

### Phase 5.2: Presenter Layer (Orchestration)
1. Create `GraphPresenter.js` with state management
2. Implement observer pattern for view updates
3. Write unit tests for presenter
4. **Deliverable**: State management + coordination working

### Phase 5.3: View Layer (UI)
1. Create `knowledgeGraphPageV2.js` with SAPUI5 controls
2. Integrate vis.js network visualization
3. Implement user interaction handlers
4. Create `knowledgeGraphV2.css` for styling
5. **Deliverable**: Full working UI

### Phase 5.4: Integration & Testing
1. Write Playwright E2E tests
2. Test with real backend API
3. Performance optimization
4. **Deliverable**: Production-ready frontend

### Phase 5.5: Module Registration
1. Update `module.json` with frontend paths
2. Register page in app router
3. Add navigation menu item
4. **Deliverable**: v2 accessible to users

---

## Success Criteria

**Functional Requirements**:
- ✅ Graph visualization renders correctly
- ✅ Refresh button loads graph (with cache)
- ✅ Rebuild button forces cache bypass
- ✅ Clear cache button works (admin)
- ✅ Status panel shows cache state
- ✅ Loading indicators during async operations
- ✅ Error messages display gracefully

**Non-Functional Requirements**:
- ✅ Clean Architecture (separation of concerns)
- ✅ Unit test coverage: 80%+ per layer
- ✅ Integration test coverage: Key user flows
- ✅ SAP Fiori compliant UI
- ✅ Performance: <2s initial load, <500ms interactions
- ✅ Responsive design (desktop focus)

**Quality Gates**:
- ✅ Feng Shui validation passes (architectural compliance)
- ✅ All tests passing (unit + integration)
- ✅ Manual QA: Load, interact, refresh, rebuild
- ✅ Code review: Clean, documented, maintainable

---

## Next Steps

1. **Review this architecture** - Ensure alignment with goals
2. **Start Phase 5.1** - Build adapter layer first
3. **Iterative development** - Test each layer independently
4. **Continuous validation** - Run tests after each component
5. **Final integration** - Connect all layers and test E2E

**Estimated Timeline**:
- Phase 5.1 (Adapters): 1-1.5 hours
- Phase 5.2 (Presenter): 1 hour  
- Phase 5.3 (View): 1.5-2 hours
- Phase 5.4 (Testing): 1 hour
- Phase 5.5 (Registration): 30 minutes
- **Total**: 4-6 hours

---

## References

- Backend API: `modules/knowledge_graph_v2/backend/api.py`
- v1 Frontend (reference): `modules/knowledge_graph/frontend/knowledgeGraphPage.js`
- SAP Fiori Guidelines: `.clinerules` section 9
- Clean Architecture: [[Knowledge Graph v2 Architecture Proposal]]