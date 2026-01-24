# API Playground Module - Implementation Plan

**Module Name**: `api-playground`
**Purpose**: Universal API testing tool that auto-discovers and tests ALL module APIs
**Category**: Developer Tools
**Version**: 1.0

---

## 🎯 Vision

**One playground to test them all!**

The API Playground automatically discovers all registered modules, reads their API configurations from `module.json`, and generates an interactive testing interface for EVERY API endpoint.

## 🏗️ Architecture

### Core Innovation: Auto-Discovery

```python
# How it works:
1. Module Registry discovers all modules
2. API Playground reads each module's module.json
3. Extracts API configuration (endpoints, methods, parameters)
4. Generates test UI dynamically
5. Handles requests to any module's API
```

### Module Structure

```
modules/api-playground/
├── module.json                 # Configuration
├── backend/
│   ├── __init__.py
│   ├── playground_service.py  # Core: Auto-discover APIs
│   └── api.py                 # Playground's own API (meta!)
├── frontend/
│   ├── Playground.view.xml    # SAP Fiori UI (future)
│   └── Playground.controller.js
├── templates/
│   └── playground.html         # Standalone HTML UI
├── tests/
│   └── test_playground.py
└── docs/
    └── README.md
```

## 📋 Features

### Phase 1: Basic (Today - 30 minutes)
- [x] Auto-discover all modules via Module Registry
- [x] Read API configuration from each module.json
- [x] Generate dynamic test UI for all endpoints
- [x] Execute API calls and show responses
- [x] Standalone HTML interface

### Phase 2: Enhanced (Week 2)
- [ ] Request history
- [ ] Save test scenarios
- [ ] Request templates
- [ ] Authentication handling
- [ ] Response formatting (JSON, XML, etc.)

### Phase 3: Production (Week 3)
- [ ] SAP Fiori UI integration
- [ ] Test collections (like Postman)
- [ ] Export/import test suites
- [ ] API documentation generation
- [ ] Performance metrics

## 🎨 User Experience

### How Developers Will Use It

**Scenario 1: Testing Feature Manager**
```
1. Open API Playground: http://localhost:5001/playground
2. See "Feature Manager" in module list
3. Click to expand → See all 7 endpoints
4. Click "GET /api/features" → Execute → See results
5. Try "POST /api/features/logging/toggle" → Success!
```

**Scenario 2: Testing HANA Connection (Future)**
```
1. Open API Playground
2. See "HANA Connection Manager" in list
3. Click endpoint: "POST /api/hana/connect"
4. Fill parameters (host, port, user, password)
5. Execute → See connection result
```

**Scenario 3: Testing SQL Execution (Future)**
```
1. Open API Playground
2. Select "SQL Execution" module
3. Endpoint: "POST /api/sql/execute"
4. Enter SQL: "SELECT * FROM TableA"
5. Execute → See query results
```

## 🔧 Implementation Details

### 1. Playground Service (Core Logic)

```python
class PlaygroundService:
    """
    Auto-discovers module APIs and generates test interface.
    """
    
    def __init__(self, module_registry):
        self.registry = module_registry
        self.discovered_apis = {}
    
    def discover_apis(self):
        """Scan all modules and extract API info from module.json"""
        for module_name, module_config in self.registry.get_all_modules().items():
            if 'api' in module_config:
                self.discovered_apis[module_name] = {
                    'displayName': module_config.get('displayName'),
                    'baseUrl': module_config['api'].get('baseUrl'),
                    'endpoints': module_config['api'].get('endpoints', [])
                }
    
    def get_all_apis(self):
        """Get all discovered APIs"""
        return self.discovered_apis
    
    def get_module_api(self, module_name):
        """Get API for specific module"""
        return self.discovered_apis.get(module_name)
```

### 2. module.json API Section

**Every module declares its API endpoints:**

```json
{
  "name": "feature-manager",
  "api": {
    "baseUrl": "/api/features",
    "endpoints": [
      {
        "path": "/",
        "method": "GET",
        "description": "Get all features",
        "parameters": []
      },
      {
        "path": "/<feature_name>/toggle",
        "method": "POST",
        "description": "Toggle a feature",
        "parameters": [
          {
            "name": "feature_name",
            "type": "path",
            "required": true,
            "description": "Name of the feature"
          }
        ]
      }
    ]
  }
}
```

### 3. Dynamic Test UI

**HTML template generates UI from discovered APIs:**

```html
<!-- For each module -->
<div class="module-section">
    <h3>{{ module.displayName }}</h3>
    <p>Base URL: {{ module.api.baseUrl }}</p>
    
    <!-- For each endpoint -->
    <div class="endpoint">
        <span class="method">{{ endpoint.method }}</span>
        <code>{{ endpoint.path }}</code>
        <button onclick="testEndpoint('{{ module.name }}', '{{ endpoint }}')">
            Test
        </button>
    </div>
</div>
```

## 🎯 Benefits

### For Current Project
- ✅ Test Feature Manager API instantly
- ✅ Test HANA Connection API (when built)
- ✅ Test Data Products API (when built)
- ✅ Test ALL future modules automatically

### For Future Projects
- ✅ Drop in API Playground module
- ✅ Auto-discovers new project's APIs
- ✅ No configuration needed
- ✅ Instant testing capability

### For Team
- ✅ No need for Postman/Insomnia
- ✅ Self-documenting APIs
- ✅ Shared testing environment
- ✅ Consistent testing workflow

## 📊 Example Output

**When you open http://localhost:5001/playground:**

```
🎯 API Playground
═══════════════════════════════════════

📦 Discovered Modules: 1

┌─────────────────────────────────────┐
│ Feature Manager                      │
│ Base URL: /api/features             │
├─────────────────────────────────────┤
│ GET  /                    [Test]    │
│ GET  /<name>              [Test]    │
│ POST /<name>/enable       [Test]    │
│ POST /<name>/disable      [Test]    │
│ POST /<name>/toggle       [Test]    │
│ GET  /export              [Test]    │
│ POST /import              [Test]    │
│ POST /reset               [Test]    │
└─────────────────────────────────────┘

[Click any Test button to execute]

Test Output:
┌─────────────────────────────────────┐
│ GET /api/features                   │
│ Status: 200 OK                      │
│ Time: 45ms                          │
│                                     │
│ Response:                           │
│ {                                   │
│   "success": true,                  │
│   "count": 2,                       │
│   "features": { ... }               │
│ }                                   │
└─────────────────────────────────────┘
```

## 🚀 Implementation Steps

### Step 1: Create Module Structure (5 min)
```bash
modules/api-playground/
├── module.json
├── backend/
│   ├── __init__.py
│   ├── playground_service.py
│   └── api.py
└── templates/
    └── playground.html
```

### Step 2: Implement Playground Service (10 min)
- Auto-discovery logic
- API metadata extraction
- Request execution

### Step 3: Create Dynamic UI (10 min)
- HTML template
- JavaScript for API calls
- Response formatting

### Step 4: Register with Module Registry (5 min)
- Test auto-discovery
- Verify Feature Manager appears
- Test endpoint execution

**Total Time**: 30 minutes

## 🎁 Future Enhancements

### Week 2
- Request history (localStorage)
- Save favorite endpoints
- Request templates
- Copy as curl command

### Week 3
- SAP Fiori UI integration
- Test collections
- Export test results
- API documentation generator

### Week 4
- Authentication testing
- Rate limiting visualization
- Performance metrics
- Team collaboration features

## 💡 Key Innovation

**This is NOT just a test tool.**

This is a **self-documenting, auto-generating API testing platform** that:
1. Requires ZERO configuration
2. Works with ANY module you create
3. Grows automatically as you add modules
4. Becomes part of your reusable module library

**Every future project gets instant API testing!** 🎉

## ✅ Success Criteria

- [ ] Discovers Feature Manager API ✓
- [ ] Shows all 8 endpoints ✓
- [ ] Can execute each endpoint ✓
- [ ] Shows request/response ✓
- [ ] Works with future modules ✓
- [ ] Reusable in other projects ✓

---

**Ready to implement?** This will be a game-changer! 🚀