# Module Federation Standard

**Status**: ✅ ACTIVE STANDARD  
**Version**: 1.0  
**Date**: February 15, 2026  
**Scope**: All modules in P2P Data Products application

---

## Executive Summary

This document defines the **Module Federation Architecture** as the standard approach for building modular applications in the P2P Data Products project. This architecture enables:

- ✅ **Single Source of Truth**: `module.json` contains all configuration
- ✅ **Clear Separation**: Backend (logic) vs Frontend (presentation)
- ✅ **Runtime Discovery**: Modules loaded dynamically via configuration
- ✅ **Independent Development**: Teams can work on modules independently
- ✅ **Type Safety**: Structured contracts for module communication

---

## Architecture Overview

### Core Principle

> "Configuration-driven module discovery with clear separation of concerns"

**Backend Responsibility**: Access control, business logic, data access  
**Frontend Responsibility**: UI presentation, user experience, navigation

**Configuration File**: `module.json` (single source of truth)

### System Flow

```
Application Startup:
1. Backend reads all module.json files
2. Backend serves enabled modules via /api/modules/frontend-registry
3. Frontend fetches module metadata
4. Frontend builds navigation from metadata
5. Modules lazy-load on user interaction
```

---

## Module Structure (STANDARD)

Every module MUST follow this directory structure:

```
modules/[module_name]/
├── module.json              # ⭐ Configuration (single source of truth)
├── README.md                # Module documentation
├── backend/                 # Backend (optional)
│   ├── __init__.py
│   ├── api.py              # Flask Blueprint
│   ├── services/           # Business logic
│   ├── repositories/       # Data access
│   └── models.py           # Data models
├── frontend/               # Frontend (optional)
│   ├── module.js           # Module bootstrap
│   ├── views/              # UI components
│   ├── adapters/           # API adapters
│   └── presenters/         # Presentation logic
└── tests/                  # Tests (REQUIRED)
    ├── unit/               # Unit tests
    ├── integration/        # Integration tests
    └── e2e/                # End-to-end tests
```

---

## module.json Schema (MANDATORY)

### Required Fields

```json
{
  "id": "module_name",              // REQUIRED: Unique identifier (snake_case)
  "name": "Module Display Name",    // REQUIRED: Human-readable name
  "version": "1.0.0",               // REQUIRED: Semantic versioning
  "description": "Module purpose",  // REQUIRED: Brief description
  "category": "category_name",      // REQUIRED: Module category
  "enabled": true,                  // REQUIRED: Feature flag (true/false)
  
  "frontend": {                     // REQUIRED if module has UI
    "page_name": "module-name",     // Page identifier (kebab-case)
    "nav_title": "Display Name",    // Navigation title
    "nav_icon": "sap-icon://...",   // SAP icon (SAPUI5 standard)
    "route": "/module-name",        // Frontend route
    "show_in_navigation": true,     // Show in nav bar (boolean)
    "scripts": [                    // JavaScript files to load
      "/modules/module_name/frontend/module.js"
    ],
    "styles": [],                   // CSS files to load (optional)
    "entry_point": {                // Module bootstrap
      "factory": "ModuleFactory"    // Factory function name
    }
  },
  
  "backend": {                      // REQUIRED if module has backend
    "type": "api",                  // Type: api | service | worker
    "module_path": "modules.module_name.backend",
    "blueprint": "modules.module_name.backend:blueprint",
    "mount_path": "/api/module-name"
  },
  
  "dependencies": {                 // Optional: Module dependencies
    "required": ["ILogger"],        // Required interfaces
    "optional": ["ICache"]          // Optional interfaces
  }
}
```

### Complete Example

```json
{
  "id": "ai_assistant",
  "name": "AI Assistant",
  "version": "1.0.0",
  "description": "Conversational AI assistant with Pydantic AI + Groq",
  "category": "infrastructure",
  "enabled": true,
  "eager_init": true,
  
  "frontend": {
    "page_name": "ai-assistant",
    "nav_title": "AI Assistant",
    "nav_icon": "sap-icon://collaborate",
    "show_in_navigation": false,
    "route": "/ai-assistant",
    "scripts": [
      "/modules/ai_assistant/frontend/adapters/AIAssistantAdapter.js",
      "/modules/ai_assistant/frontend/views/AIAssistantOverlay.js",
      "/modules/ai_assistant/frontend/module.js"
    ],
    "styles": [],
    "entry_point": {
      "factory": "AIAssistantModule"
    }
  },
  
  "backend": {
    "blueprint": "modules.ai_assistant.backend:blueprint",
    "mount_path": "/api/ai-assistant",
    "dependencies": ["pydantic-ai", "pydantic-ai[groq]"],
    "database_paths": {
      "p2p_data": "database/p2p_data.db",
      "p2p_graph": "database/p2p_graph.db",
      "conversations": "database/ai_assistant_conversations.db"
    }
  },
  
  "dependencies": {
    "required": [],
    "optional": ["ILogger"]
  },
  
  "api_endpoints": [
    {
      "path": "/api/ai-assistant/chat",
      "method": "POST",
      "description": "Send message to AI assistant"
    }
  ],
  
  "configuration": {
    "groq_model": "llama-3.3-70b-versatile",
    "max_conversation_length": 20,
    "response_timeout": 30
  }
}
```

---

## Naming Conventions (MANDATORY)

### Module IDs
- **Format**: `snake_case`
- **Examples**: `ai_assistant`, `data_products_v2`, `knowledge_graph_v2`
- **Rules**: 
  - Lowercase only
  - Underscores for word separation
  - No version suffix (use version field instead)

### Frontend Routes
- **Format**: `/kebab-case`
- **Examples**: `/ai-assistant`, `/data-products-v2`, `/knowledge-graph-v2`
- **Rules**:
  - Lowercase only
  - Hyphens for word separation
  - Must start with `/`

### API Mount Paths
- **Format**: `/api/kebab-case`
- **Examples**: `/api/ai-assistant`, `/api/data-products`, `/api/knowledge-graph`
- **Rules**:
  - Must start with `/api/`
  - Lowercase only
  - Hyphens for word separation

### Page Names
- **Format**: `kebab-case`
- **Examples**: `ai-assistant`, `data-products-v2`, `knowledge-graph-v2`
- **Rules**:
  - Lowercase only
  - Hyphens for word separation
  - Used for HTML element IDs

### Factory Names
- **Format**: `PascalCase` + `Module` or `Factory`
- **Examples**: `AIAssistantModule`, `DataProductsV2Factory`, `KnowledgeGraphFactory`
- **Rules**:
  - PascalCase
  - Must end with `Module` or `Factory`
  - Exported as global (window scope)

---

## Backend Standards

### Flask Blueprint Registration

```python
from flask import Blueprint

# Blueprint naming: [module_name]_api
blueprint = Blueprint('ai_assistant_api', __name__)

@blueprint.route('/chat', methods=['POST'])
def chat():
    """API endpoint implementation"""
    return jsonify({"success": True})
```

### Service Layer (Business Logic)

```python
class AIAssistantService:
    """Service handles business logic"""
    
    def __init__(self, conversation_repository):
        self.conversation_repo = conversation_repository
    
    def process_message(self, message: str) -> str:
        """Process user message and generate response"""
        # Business logic here
        pass
```

### Repository Layer (Data Access)

```python
class ConversationRepository:
    """Repository handles data persistence"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
    
    def save_conversation(self, conversation):
        """Save conversation to database"""
        # Data access logic here
        pass
```

### Dependency Injection (REQUIRED)

```python
# In server.py
from modules.ai_assistant.backend.services.agent_service import AgentService
from modules.ai_assistant.backend.repositories.conversation_repository import ConversationRepository

# Create dependencies
conversation_repo = ConversationRepository(db_path)
agent_service = AgentService(conversation_repo)

# Inject via blueprint
blueprint.agent_service = agent_service
```

---

## Frontend Standards

### Module Bootstrap Pattern

```javascript
// modules/ai_assistant/frontend/module.js
(function() {
    'use strict';
    
    class AIAssistantModule {
        constructor() {
            this.initialized = false;
        }
        
        async init(dependencies) {
            if (this.initialized) return;
            
            // Store dependencies
            this.logger = dependencies.logger;
            this.eventBus = dependencies.eventBus;
            
            // Initialize module
            await this.setupUI();
            
            this.initialized = true;
        }
        
        async setupUI() {
            // UI initialization logic
        }
        
        destroy() {
            // Cleanup logic
        }
    }
    
    // Export to global scope
    window.AIAssistantModule = AIAssistantModule;
})();
```

### API Adapter Pattern

```javascript
// modules/ai_assistant/frontend/adapters/AIAssistantAdapter.js
class AIAssistantAdapter {
    constructor(baseUrl = '/api/ai-assistant') {
        this.baseUrl = baseUrl;
    }
    
    async sendMessage(sessionId, message) {
        const response = await fetch(`${this.baseUrl}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, message })
        });
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return response.json();
    }
}
```

### View Pattern (Presenter/View Separation)

```javascript
// Presenter (business logic)
class AIAssistantPresenter {
    constructor(adapter, view) {
        this.adapter = adapter;
        this.view = view;
    }
    
    async handleUserMessage(message) {
        this.view.showLoading();
        
        try {
            const response = await this.adapter.sendMessage(this.sessionId, message);
            this.view.displayMessage(response.message);
        } catch (error) {
            this.view.showError(error.message);
        } finally {
            this.view.hideLoading();
        }
    }
}

// View (UI rendering)
class AIAssistantView {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }
    
    showLoading() {
        // Show loading indicator
    }
    
    displayMessage(message) {
        // Render message in UI
    }
    
    showError(error) {
        // Display error to user
    }
}
```

---

## Testing Standards (MANDATORY)

### Backend API Contract Tests

```python
import pytest
import requests

@pytest.mark.e2e
@pytest.mark.api_contract
def test_ai_assistant_chat_endpoint():
    """Test: /api/ai-assistant/chat returns valid contract"""
    # ARRANGE
    url = "http://localhost:5000/api/ai-assistant/chat"
    payload = {
        "session_id": "test-session",
        "message": "Hello"
    }
    
    # ACT
    response = requests.post(url, json=payload, timeout=5)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert 'success' in data
    assert 'message' in data
    assert isinstance(data['message'], str)
```

### Frontend API Tests

```python
@pytest.mark.e2e
@pytest.mark.api_contract
def test_frontend_module_registry():
    """Test: Frontend registry returns module metadata"""
    # ARRANGE
    url = "http://localhost:5000/api/modules/frontend-registry"
    
    # ACT
    response = requests.get(url, timeout=5)
    
    # ASSERT
    assert response.status_code == 200
    data = response.json()
    assert 'modules' in data
    assert len(data['modules']) > 0
    
    # Validate structure
    module = data['modules'][0]
    assert 'id' in module
    assert 'name' in module
    assert 'icon' in module
    assert 'route' in module
```

---

## Quality Standards

### Feng Shui Validation

Every module MUST pass Feng Shui quality gate:

```bash
python -m tools.fengshui gate --module ai_assistant
```

**Required Checks**:
1. ✅ module.json structure valid
2. ✅ Frontend/backend separation enforced
3. ✅ Naming conventions followed
4. ✅ API contracts tested
5. ✅ Test coverage >= 70%
6. ✅ No critical security issues
7. ✅ Documentation complete

### Gu Wu Test Coverage

All modules MUST have API contract tests:

```bash
pytest tests/ -m api_contract
```

**Required Tests**:
- Backend API endpoints
- Frontend API endpoints  
- Error handling
- Edge cases

---

## Migration Checklist

When creating a new module, follow this checklist:

### Phase 1: Setup (30 min)
- [ ] Create module directory: `modules/[name]/`
- [ ] Create `module.json` with all required fields
- [ ] Create `README.md` with module description
- [ ] Create directory structure (backend/, frontend/, tests/)

### Phase 2: Backend (2-4 hours)
- [ ] Implement Flask Blueprint (`backend/api.py`)
- [ ] Implement Service Layer (`backend/services/`)
- [ ] Implement Repository Layer (`backend/repositories/`)
- [ ] Register blueprint in `server.py` with DI
- [ ] Write API contract tests

### Phase 3: Frontend (2-4 hours)
- [ ] Create module bootstrap (`frontend/module.js`)
- [ ] Create API adapter (`frontend/adapters/`)
- [ ] Create views/presenters (`frontend/views/`, `frontend/presenters/`)
- [ ] Export factory to global scope
- [ ] Write frontend API tests

### Phase 4: Integration (1-2 hours)
- [ ] Test module loads via `/api/modules/frontend-registry`
- [ ] Test navigation appears correctly
- [ ] Test end-to-end user flows
- [ ] Run Feng Shui quality gate
- [ ] Update documentation

---

## Common Patterns

### Pattern 1: Configuration-Driven Module Discovery

**Problem**: Hard-coded module list  
**Solution**: Scan `modules/` for `module.json` files

```python
def discover_modules():
    """Auto-discover modules from filesystem"""
    modules_dir = Path('modules')
    modules = []
    
    for module_path in modules_dir.iterdir():
        if not module_path.is_dir():
            continue
        
        module_json = module_path / 'module.json'
        if module_json.exists():
            with open(module_json) as f:
                config = json.load(f)
                if config.get('enabled', False):
                    modules.append(config)
    
    return modules
```

### Pattern 2: Lazy Loading

**Problem**: Large initial page load  
**Solution**: Load modules on-demand

```javascript
class ModuleRegistry {
    async loadModule(moduleId) {
        if (this.loadedModules.has(moduleId)) {
            return this.loadedModules.get(moduleId);
        }
        
        // Dynamic import
        const module = await import(`/modules/${moduleId}/frontend/module.js`);
        const instance = new module.default();
        await instance.init(this.dependencies);
        
        this.loadedModules.set(moduleId, instance);
        return instance;
    }
}
```

### Pattern 3: Dependency Injection

**Problem**: Tight coupling between components  
**Solution**: Constructor injection with interfaces

```python
# Define interface
class IDataSource:
    def get_data(self): pass

# Implement interface
class SqliteDataSource(IDataSource):
    def get_data(self):
        return self.db.query("SELECT * FROM data")

# Inject dependency
class DataProductsService:
    def __init__(self, data_source: IDataSource):
        self.data_source = data_source
    
    def get_products(self):
        return self.data_source.get_data()
```

---

## Anti-Patterns (AVOID)

### ❌ Anti-Pattern 1: Hard-Coded Module List

```python
# DON'T DO THIS
MODULES = [
    {'id': 'ai_assistant', 'name': 'AI Assistant'},
    {'id': 'data_products', 'name': 'Data Products'}
]
```

**Why**: Requires code change for every new module  
**Solution**: Use configuration-driven discovery

### ❌ Anti-Pattern 2: Backend Owns UI Presentation

```python
# DON'T DO THIS
@blueprint.route('/render-ui')
def render_ui():
    return render_template('module.html', title='My Module')
```

**Why**: Violates separation of concerns  
**Solution**: Backend returns data, frontend handles presentation

### ❌ Anti-Pattern 3: Service Locator Pattern

```python
# DON'T DO THIS
class ServiceLocator:
    @staticmethod
    def get_service(name):
        return SERVICES[name]

service = ServiceLocator.get_service('data_source')
```

**Why**: Hidden dependencies, hard to test  
**Solution**: Use constructor injection

### ❌ Anti-Pattern 4: God Object

```python
# DON'T DO THIS
class ModuleManager:
    def load_modules(self): pass
    def register_blueprints(self): pass
    def handle_routing(self): pass
    def manage_state(self): pass
    def process_data(self): pass
```

**Why**: Too many responsibilities  
**Solution**: Single Responsibility Principle (SRP)

---

## Troubleshooting

### Module Not Appearing in Navigation

**Check**:
1. ✅ `module.json` exists and is valid JSON
2. ✅ `enabled: true` in module.json
3. ✅ `show_in_navigation: true` in frontend section
4. ✅ Module directory in `modules/` folder
5. ✅ Server restarted after adding module

### Module Not Loading

**Check**:
1. ✅ Scripts paths correct in module.json
2. ✅ Factory function exported to global scope
3. ✅ Browser console for JavaScript errors
4. ✅ Network tab shows scripts loading (200 OK)

### API Endpoints Not Working

**Check**:
1. ✅ Blueprint registered in server.py
2. ✅ Mount path matches module.json
3. ✅ Flask server running
4. ✅ Test with curl: `curl -X POST http://localhost:5000/api/[module]/[endpoint]`

---

## References

### Internal Documentation
- [[App V2 Modular Architecture Plan]] - Complete architecture overview
- [[Module Migration Guide]] - Step-by-step migration instructions
- [[Configuration-Based Dependency Injection]] - DI patterns
- [[API-First Contract Testing Methodology]] - Testing approach

### Industry Standards
- **Webpack Module Federation**: Runtime code sharing
- **SAP Fiori**: UI5 + OData separation model
- **BFF Pattern**: Backend-for-Frontend (deferred for future)
- **Single-SPA**: Micro-frontend orchestration

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 15, 2026 | Initial standard based on current architecture |

---

## Approval

**Approved By**: User  
**Date**: February 15, 2026  
**Status**: ✅ ACTIVE STANDARD

---

**End of Document**