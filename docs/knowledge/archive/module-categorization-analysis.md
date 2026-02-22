# Module Categorization Analysis

**Author**: AI Assistant  
**Date**: February 8, 2026  
**Purpose**: Categorize existing modules as Infrastructure vs Feature to guide app_v2 architecture  
**Related**: [[App v2 Modular Architecture Plan]], [[Infrastructure vs Feature Modules]]

---

## 🎯 The Question

**User Asked**:
> "Some of the existing modules, I'm not sure if there are rather infrastructure in nature, or if they are really application features. Could help me to categorize, so that I can understand how they will fit and be integrated into the proposed architecture?"

---

## 📊 Module Categories

### Category 1: 🔧 Infrastructure Modules (Core Services)

**Definition**: Provide foundational capabilities that OTHER modules depend on. No direct user-facing features (or minimal UI for configuration).

**Characteristics**:
- ✅ Other modules depend on them (via `ILogger`, `IDataSource`, etc.)
- ✅ Provide services/interfaces (registered in DependencyContainer)
- ✅ Typically no navigation tab (or config-only UI)
- ✅ Always enabled (or rarely disabled)
- ✅ Could theoretically move to `core/` layer

---

#### 1.1 `log_manager` 🔧 **Infrastructure**

**What**: Centralized logging system with SQLite persistence

**Why Infrastructure**:
- ✅ Other modules depend on it via `ILogger` interface
- ✅ Provides service: Logging capability
- ✅ No primary business feature (it's a support service)
- ✅ UI exists but mainly for viewing/configuring logs (not primary workflow)

**In App v2**:
```javascript
// Provides: ILogger service
DependencyContainer.register('ILogger', () => new LogManagerAdapter());

// Consumed by: knowledge_graph_v2, data_products, ai_assistant, etc.
const logger = DependencyContainer.get('ILogger');
logger.log("Action performed", "INFO");
```

**UI Treatment**:
- ⚠️ **Debate**: Should it have a navigation tab?
- **Option A**: Settings icon in header (opens log viewer dialog) - NO navigation tab
- **Option B**: Navigation tab "Logs" (for debugging/admin users)
- **Recommendation**: Option A (infrastructure shouldn't clutter main navigation)

**Migration Plan**: 
- ✅ Keep as module (other modules depend on it as optional dependency)
- ✅ Implements `ILogger` interface
- ✅ Provides NoOpLogger fallback

---

#### 1.2 `hana_connection` 🔧 **Infrastructure**

**What**: HANA Cloud connection management and query execution

**Why Infrastructure**:
- ✅ Provides service: Database connectivity
- ✅ No user-facing feature (it's plumbing)
- ✅ Used by Repository Pattern (core layer)
- ✅ Configuration-only UI (connection strings, credentials)

**In App v2**:
```javascript
// Provides: IDataSource service (for HANA)
// But actually: This is BACKEND-ONLY infrastructure!
// Frontend modules don't directly use HANA connections

// Backend: Used by core/repositories/_hana_repository.py
# Frontend: No UI needed (backend handles connections transparently)
```

**UI Treatment**:
- ❌ **No navigation tab needed** (backend-only infrastructure)
- ✅ **Config UI**: Could have settings dialog for connection management
- ✅ **Status UI**: Could show connection health in app header/footer

**Migration Plan**:
- 🤔 **CANDIDATE FOR CORE**: Could move to `core/connections/hana_connection.py`
- ✅ **OR**: Keep as module if UI for connection management is valuable
- **Recommendation**: Keep as module with config-only UI (no nav tab)

---

#### 1.3 `login_manager` 🔧 **Infrastructure**

**What**: User authentication and session management

**Why Infrastructure**:
- ✅ Foundational capability (security)
- ✅ Other modules depend on it (need user context)
- ✅ Always enabled (can't disable authentication!)
- ✅ No primary business feature (it's a gateway)

**In App v2**:
```javascript
// Provides: IAuthService
DependencyContainer.register('IAuthService', () => new LoginManagerAdapter());

// Consumed by: ALL modules (need to check user permissions)
const auth = DependencyContainer.get('IAuthService');
if (!auth.isAuthenticated()) {
  // Redirect to login
}
```

**UI Treatment**:
- ❌ **No navigation tab** (login is a dialog/page, not a feature)
- ✅ **Login Dialog**: Shown before app loads
- ✅ **User Menu**: Shows current user in app header

**Migration Plan**:
- ✅ Keep as module (but special type: "authentication")
- ✅ Loads BEFORE other modules (bootstrap phase)
- ✅ Provides IAuthService interface

---

#### 1.4 `feature_manager` 🔧 **Infrastructure**

**What**: Feature flag management (enable/disable modules/features)

**Why Infrastructure**:
- ✅ Controls OTHER modules (meta-level)
- ✅ No primary business feature
- ✅ Configuration-only UI

**In App v2**:
```javascript
// Provides: IFeatureFlags service
DependencyContainer.register('IFeatureFlags', () => new FeatureFlagsAdapter());

// Used by: ModuleRegistry (check if module should load)
const featureFlags = DependencyContainer.get('IFeatureFlags');
if (featureFlags.isEnabled('knowledge_graph_v2')) {
  // Load module
}
```

**UI Treatment**:
- ⚠️ **Debate**: Admin-only settings page?
- **Option A**: Settings icon → Feature flags config
- **Option B**: Navigation tab "Settings" → Feature flags section
- **Recommendation**: Option A (infrastructure shouldn't clutter nav)

**Migration Plan**:
- ✅ Keep as module (meta-module for controlling others)
- ✅ Provides IFeatureFlags interface
- ✅ Loads EARLY (before feature modules)

---

#### 1.5 `debug_mode` 🔧 **Infrastructure**

**What**: Debug capabilities (verbose logging, performance metrics, etc.)

**Why Infrastructure**:
- ✅ Development/troubleshooting tool
- ✅ No primary business feature
- ✅ Enhances other modules (adds debug overlays)

**In App v2**:
```javascript
// Provides: IDebugger service
DependencyContainer.register('IDebugger', () => new DebugModeAdapter());

// Consumed by: All modules (for debugging)
const debugger = DependencyContainer.get('IDebugger');
debugger.trace("Operation started", { data });
```

**UI Treatment**:
- ❌ **No navigation tab**
- ✅ **Debug Panel**: Toggle in app header (shows/hides debug overlay)
- ✅ **Keyboard Shortcut**: Ctrl+Shift+D to enable

**Migration Plan**:
- ✅ Keep as module (optional capability)
- ✅ Provides IDebugger interface with NoOpDebugger fallback
- ✅ UI extensions (adds debug panel to app shell)

---

### Category 2: 🎯 Feature Modules (Business Capabilities)

**Definition**: Deliver user-facing business value. These ARE the application features that users come to use.

**Characteristics**:
- ✅ User navigates to them (navigation tab)
- ✅ Solve specific business problems
- ✅ Can be disabled (app still works, just missing that capability)
- ✅ May depend on infrastructure modules
- ✅ STAY in `modules/` directory

---

#### 2.1 `knowledge_graph` 🎯 **Feature Module**

**What**: Schema visualization (legacy v1)

**Why Feature**:
- ✅ User navigates to "Knowledge Graph" tab
- ✅ Solves business problem: Understand database schema
- ✅ Primary workflow: Build → Visualize → Interact
- ✅ Can be disabled (app works without it)

**In App v2**:
```javascript
// Auto-discovered from module.json
// Navigation tab: "Knowledge Graph"
// Depends on: ILogger (optional), IDataSource (optional)
```

**Migration Plan**:
- ✅ Stays in `modules/knowledge_graph/`
- ✅ Gets navigation tab
- ✅ Declares optional dependencies

---

#### 2.2 `knowledge_graph_v2` 🎯 **Feature Module** ⭐ REFERENCE

**What**: Schema visualization with Clean Architecture

**Why Feature**:
- ✅ User navigates to "Knowledge Graph v2" tab
- ✅ Solves business problem: Understand database schema (improved UX)
- ✅ Primary workflow: Build → Visualize → Interact → Export
- ✅ Can be disabled

**In App v2**:
```javascript
// ⭐ REFERENCE IMPLEMENTATION
// Perfect example of Clean Architecture module
// Shows how feature modules should be structured
```

**Migration Plan**:
- ✅ **FIRST MODULE TO MIGRATE** (reference implementation)
- ✅ Demonstrates optional dependencies (log_manager, data_products)
- ✅ Shows graceful degradation pattern

---

#### 2.3 `p2p_dashboard` 🎯 **Feature Module**

**What**: P2P process KPIs and metrics visualization

**Why Feature**:
- ✅ User navigates to "P2P Dashboard" tab
- ✅ Solves business problem: Monitor procurement process health
- ✅ Primary workflow: View KPIs → Analyze trends → Drill down
- ✅ Can be disabled (for non-P2P users)

**In App v2**:
```javascript
// Navigation tab: "P2P Dashboard"
// Depends on: IDataSource (required - needs P2P data!)
```

**Migration Plan**:
- ✅ Stays in `modules/p2p_dashboard/`
- ✅ Gets navigation tab
- ✅ Declares required dependency on data_products (needs P2P data to function)

---

#### 2.4 `ai_assistant` 🎯 **Feature Module**

**What**: Joule AI chatbot for natural language queries

**Why Feature**:
- ✅ User navigates to "AI Assistant" tab
- ✅ Solves business problem: Natural language data access
- ✅ Primary workflow: Ask questions → Get insights
- ✅ Can be disabled (for users who don't need AI)

**In App v2**:
```javascript
// Navigation tab: "AI Assistant" (or "Joule")
// Depends on: groq_client (required), ILogger (optional), IDataSource (optional)
```

**Migration Plan**:
- ✅ Stays in `modules/ai_assistant/`
- ✅ Gets navigation tab
- ✅ Already has frontend/ directory (good example!)
- ✅ Declares required dependency on groq_client

---

### Category 3: 🛠️ Developer Tools (Hybrid)

**Definition**: Tools primarily for developers/admins, but have user-facing UI. Can be toggled on/off.

**Characteristics**:
- ✅ Have navigation tabs
- ✅ But serve technical/admin purposes (not core business features)
- ✅ Can be disabled in production
- ✅ Optional dependencies

---

#### 3.1 `api_playground` 🛠️ **Developer Tool**

**What**: Interactive API testing interface

**Why Developer Tool**:
- ✅ Primary users: Developers, QA, Admins
- ✅ Purpose: Test APIs, debug, explore endpoints
- ✅ Not core business feature (but valuable!)
- ✅ Can be disabled in production environments

**In App v2**:
```javascript
// Navigation tab: "API Playground" (or "Developer Tools")
// Depends on: ILogger (optional - log API calls)
```

**UI Treatment**:
- ✅ **Navigation tab**: Yes (for developers)
- ⚠️ **Production**: Might be disabled via feature flags
- ✅ **Permission**: Could require admin role

**Migration Plan**:
- ✅ Stays in `modules/api_playground/`
- ✅ Gets navigation tab (but optional in production)
- ✅ Declares optional dependency on log_manager

---

#### 3.2 `sql_execution` 🛠️ **Developer Tool**

**What**: Execute arbitrary SQL queries against databases

**Why Developer Tool**:
- ✅ Primary users: Developers, Admins, Power Users
- ✅ Purpose: Ad-hoc queries, data exploration, debugging
- ✅ Not core business feature (technical tool)
- ✅ Security risk (disable in production?)

**In App v2**:
```javascript
// Navigation tab: "SQL Execution" (or under "Developer Tools")
// Depends on: IDataSource (required - needs database access)
```

**UI Treatment**:
- ✅ **Navigation tab**: Yes (for power users)
- ⚠️ **Production**: Should be disabled (security risk!)
- ✅ **Permission**: Requires elevated privileges

**Migration Plan**:
- ✅ Stays in `modules/sql_execution/`
- ✅ Gets navigation tab (but gated by permissions)
- ⚠️ **Consider**: Could merge with api_playground as "Developer Tools" module

---

#### 3.3 `csn_validation` 🛠️ **Developer Tool**

**What**: Validate CSN schemas against HANA Cloud standards

**Why Developer Tool**:
- ✅ Primary users: Developers, Data Engineers
- ✅ Purpose: Ensure schema compliance, catch errors early
- ✅ Not user-facing business feature
- ✅ Development/QA tool

**In App v2**:
```javascript
// Navigation tab: "CSN Validation" (or under "Developer Tools")
// Depends on: IDataSource (required - needs to read schemas)
```

**UI Treatment**:
- ⚠️ **Debate**: Does this need a tab?
- **Option A**: Background validation (no UI, runs on schema changes)
- **Option B**: Developer tools section (show validation report)
- **Recommendation**: Option A (automate it, minimal UI)

**Migration Plan**:
- 🤔 **CANDIDATE FOR AUTOMATION**: Could be background service (no UI)
- ✅ **OR**: Keep as module with minimal config UI
- **Recommendation**: Keep as module, but consider making it background-only

---

#### 3.4 `data_products` 🛠️ **Hybrid** (Infrastructure + Feature)

**What**: SAP Data Products integration (create tables, query data)

**Why Hybrid**:
- ✅ Infrastructure: Provides `IDataSource` interface (other modules use it)
- ✅ Feature: Users navigate to it to manage data products
- ✅ Both a service AND a feature

**In App v2**:
```javascript
// Provides: IDataSource service (Infrastructure)
DependencyContainer.register('IDataSource', () => new DataProductsAdapter());

// Also has: Navigation tab "Data Products" (Feature)
// User workflow: Create → Manage → Query data products
```

**UI Treatment**:
- ✅ **Navigation tab**: Yes (users manage data products)
- ✅ **Service Provider**: Yes (other modules query via IDataSource)
- ✅ **Dual Role**: Both infrastructure AND feature

**Migration Plan**:
- ✅ Stays in `modules/data_products/`
- ✅ Gets navigation tab
- ✅ Provides IDataSource interface
- ✅ Other modules depend on it optionally

---

## 📋 Complete Module Categorization

| Module | Category | Has Nav Tab? | Provides Service? | User-Facing? | Always Enabled? |
|--------|----------|--------------|-------------------|--------------|-----------------|
| `log_manager` | 🔧 Infrastructure | ⚠️ Maybe | ✅ ILogger | ⚠️ Minimal | ✅ Recommended |
| `hana_connection` | 🔧 Infrastructure | ❌ No | ✅ Backend only | ❌ No | ✅ Yes |
| `login_manager` | 🔧 Infrastructure | ❌ No | ✅ IAuthService | ⚠️ Login only | ✅ Always |
| `feature_manager` | 🔧 Infrastructure | ⚠️ Admin | ✅ IFeatureFlags | ⚠️ Config only | ✅ Yes |
| `debug_mode` | 🔧 Infrastructure | ❌ No | ✅ IDebugger | ⚠️ Overlay only | ❌ Dev only |
| `data_products` | 🛠️ **Hybrid** | ✅ Yes | ✅ IDataSource | ✅ Yes | ❌ Optional |
| `knowledge_graph` | 🎯 Feature | ✅ Yes | ❌ No | ✅ Yes | ❌ Optional |
| `knowledge_graph_v2` | 🎯 Feature | ✅ Yes | ❌ No | ✅ Yes | ❌ Optional |
| `p2p_dashboard` | 🎯 Feature | ✅ Yes | ❌ No | ✅ Yes | ❌ Optional |
| `ai_assistant` | 🎯 Feature | ✅ Yes | ❌ No | ✅ Yes | ❌ Optional |
| `api_playground` | 🛠️ Dev Tool | ✅ Yes | ❌ No | ✅ Yes (devs) | ❌ Optional |
| `sql_execution` | 🛠️ Dev Tool | ✅ Yes | ❌ No | ✅ Yes (devs) | ❌ Optional |
| `csn_validation` | 🛠️ Dev Tool | ⚠️ Maybe | ❌ No | ⚠️ Minimal | ❌ Optional |

---

## 🏗️ How This Fits Into App v2 Architecture

### Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    App v2 Shell                             │
│  (Navigation, Routing, Authentication, Feature Flags)       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            Core Infrastructure Layer (DI)                   │
│  - DependencyContainer                                      │
│  - EventBus                                                 │
│  - Interfaces (ILogger, IDataSource, IAuth, etc.)          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│        Infrastructure Modules (Services)                    │
│  - log_manager → ILogger                                    │
│  - login_manager → IAuthService                             │
│  - feature_manager → IFeatureFlags                          │
│  - debug_mode → IDebugger                                   │
│  - hana_connection → Backend only                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│        Hybrid Modules (Service + Feature)                   │
│  - data_products → IDataSource + Nav Tab                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│        Feature Modules (Business Value)                     │
│  - knowledge_graph_v2 → Nav Tab                             │
│  - p2p_dashboard → Nav Tab                                  │
│  - ai_assistant → Nav Tab                                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│        Developer Tools (Optional)                           │
│  - api_playground → Nav Tab (dev only)                      │
│  - sql_execution → Nav Tab (admin only)                     │
│  - csn_validation → Background or Tab                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Integration Strategy for Each Category

### Infrastructure Modules → Service Providers

**What They Do**:
- Register services in DependencyContainer
- Provide interfaces (ILogger, IAuthService, etc.)
- No navigation tabs (or config-only tabs)

**Example**: `log_manager`
```javascript
// modules/log_manager/frontend/module.js
export default {
    type: 'infrastructure',
    
    async initialize() {
        // Register service
        DependencyContainer.register('ILogger', () => new LogManagerAdapter());
        
        // Subscribe to events (log them)
        eventBus.subscribe('*', (eventName, data) => {
            this.log(eventName, data);
        });
    },
    
    // NO navigation tab (or admin-only settings tab)
    hasNavigation: false,
    
    // Provides service
    provides: ['ILogger']
};
```

---

### Feature Modules → User Workflows

**What They Do**:
- Have navigation tabs
- Consume services from infrastructure modules
- Implement business workflows
- Can be disabled

**Example**: `knowledge_graph_v2`
```javascript
// modules/knowledge_graph_v2/frontend/module.js
export default {
    type: 'feature',
    
    constructor() {
        // Will be injected during initialize
        this.logger = null;
        this.dataSource = null;
    },
    
    async initialize() {
        // Consume services
        this.logger = DependencyContainer.get('ILogger');
        this.dataSource = DependencyContainer.get('IDataSource');
    },
    
    // Has navigation tab
    hasNavigation: true,
    
    async createUI() {
        // Build feature UI
        return createKnowledgeGraphPageV2();
    }
};
```

---

### Hybrid Modules → Both

**What They Do**:
- Provide services (infrastructure)
- Have user-facing UI (feature)
- Navigate tab + service registration

**Example**: `data_products`
```javascript
// modules/data_products/frontend/module.js
export default {
    type: 'hybrid',
    
    async initialize() {
        // Register service (Infrastructure)
        DependencyContainer.register('IDataSource', () => new DataProductsAdapter());
        
        // Also has UI (Feature)
    },
    
    // Has navigation tab (Feature aspect)
    hasNavigation: true,
    
    // Provides service (Infrastructure aspect)
    provides: ['IDataSource']
};
```

---

## 🤔 Recommendations for Each Module

### Infrastructure: Consider Refactoring

**1. `log_manager`** 🔧
- **Current**: Module with UI
- **Recommendation**: Keep as module, but minimize UI
- **Reason**: Other modules depend on ILogger interface
- **UI**: Settings icon → Log viewer dialog (NO nav tab)

**2. `hana_connection`** 🔧
- **Current**: Module with backend only
- **Recommendation**: Could move to `core/connections/`
- **Reason**: Pure infrastructure, no UI, used by Repository Pattern
- **Alternative**: Keep as module if connection management UI is valuable

**3. `login_manager`** 🔧
- **Current**: Module with authentication logic
- **Recommendation**: Keep as special "bootstrap" module
- **Reason**: Must load before any other modules
- **UI**: Login dialog only (no nav tab)

**4. `feature_manager`** 🔧
- **Current**: Module with feature flag management
- **Recommendation**: Keep as admin module
- **Reason**: Meta-module for controlling others
- **UI**: Settings icon → Feature flags config (no nav tab)

**5. `debug_mode`** 🔧
- **Current**: Module with debug capabilities
- **Recommendation**: Keep as optional module
- **Reason**: Valuable for development, easily disabled
- **UI**: Debug panel toggle in header (no nav tab)

---

### Features: Migrate As-Is

**6. `knowledge_graph`** 🎯
- ✅ Stay in modules/
- ✅ Navigation tab
- ✅ Optional dependencies

**7. `knowledge_graph_v2`** 🎯 ⭐
- ✅ **FIRST TO MIGRATE** (reference implementation)
- ✅ Navigation tab
- ✅ Shows optional dependency pattern

**8. `p2p_dashboard`** 🎯
- ✅ Stay in modules/
- ✅ Navigation tab
- ✅ Required dependency on data_products

**9. `ai_assistant`** 🎯
- ✅ Stay in modules/
- ✅ Navigation tab
- ✅ Already has frontend/ directory (proof of concept!)

---

### Developer Tools: Group or Keep Separate?

**10. `api_playground`** 🛠️
- **Option A**: Keep as separate module with nav tab
- **Option B**: Merge with sql_execution as "Developer Tools" module
- **Recommendation**: Keep separate (different purposes)

**11. `sql_execution`** 🛠️
- **Option A**: Keep as separate module
- **Option B**: Merge with api_playground
- **Option C**: Integrate into data_products (as "Query" tab)
- **Recommendation**: Option C (query belongs with data products)

**12. `csn_validation`** 🛠️
- **Option A**: Keep as module with minimal UI
- **Option B**: Make it background-only (automated validation)
- **Option C**: Move to `tools/` directory (not a module)
- **Recommendation**: Option B (automate it, no UI needed)

---

### Hybrid: Special Handling

**13. `data_products`** 🛠️
- ✅ Keep as-is (both service provider AND feature)
- ✅ Navigation tab: "Data Products" (manage data products)
- ✅ Service: IDataSource (other modules query via this)
- ✅ Critical dependency for p2p_dashboard

---

## 🎯 Proposed Navigation Structure for App v2

```
App Header
├── [App Title: "P2P Data Products"]
├── Settings ⚙️ (dropdown)
│   ├── Feature Flags (feature_manager)
│   ├── View Logs (log_manager)
│   └── Debug Mode (debug_mode)
└── User Menu 👤 (login_manager)
    ├── Profile
    └── Logout

Main Navigation Tabs
├── 📊 P2P Dashboard        (p2p_dashboard)
├── 🕸️ Knowledge Graph v2   (knowledge_graph_v2)
├── 🤖 AI Assistant         (ai_assistant)
├── 📦 Data Products        (data_products)
└── 🔧 Developer Tools      (dropdown - admin only)
    ├── API Playground      (api_playground)
    └── SQL Execution       (sql_execution)
```

**Benefits**:
- ✅ Clean main navigation (only user-facing features)
- ✅ Infrastructure in settings (discoverable but not cluttering)
- ✅ Developer tools grouped (easily disabled in production)
- ✅ Auto-generated from module.json metadata

---

## 📊 Module Migration Priority

### Phase 1: Reference Implementation (1-2 days)
1. **knowledge_graph_v2** ⭐ (feature, perfect example)
   - Shows optional dependencies (log_manager, data_products)
   - Demonstrates graceful degradation
   - Complete Clean Architecture

### Phase 2: Infrastructure Services (2-3 days)
2. **log_manager** (infrastructure, service provider)
   - Implements ILogger interface
   - Used by all feature modules
3. **feature_manager** (infrastructure, meta-service)
   - Controls module loading
4. **login_manager** (infrastructure, bootstrap)
   - Must load before everything else

### Phase 3: Hybrid Module (1 day)
5. **data_products** (hybrid)
   - Both service provider AND feature
   - Complex but valuable

### Phase 4: Feature Modules (3-4 days)
6. **p2p_dashboard** (feature)
   - Depends on data_products (required)
7. **ai_assistant** (feature)
   - Already has frontend/ directory
8. **knowledge_graph** (feature, legacy)
   - Deprecate after v2 stable?

### Phase 5: Developer Tools (2-3 days)
9. **api_playground** (dev tool)
   - Optional, admin-only
10. **sql_execution** (dev tool)
    - Consider merging with data_products
11. **csn_validation** (dev tool)
    - Consider automating (background only)

### Phase 6: Cleanup (1 day)
12. **debug_mode** (infrastructure)
    - Optional development capability
13. **hana_connection** (infrastructure)
    - Backend-only, consider moving to core/

---

## 🎓 Decision Framework: Is This Infrastructure or Feature?

**Ask These Questions**:

1. **Do other modules depend on it?**
   - YES → Infrastructure (provides service)
   - NO → Feature (standalone capability)

2. **What's the primary user?**
   - End user (business value) → Feature
   - Developer/Admin (technical) → Infrastructure or Dev Tool
   - System (no user) → Infrastructure

3. **Can the app function without it?**
   - NO (critical) → Infrastructure
   - YES (optional) → Feature or Dev Tool

4. **Does it have a primary workflow?**
   - YES (user navigates here to accomplish task) → Feature
   - NO (configures system, provides service) → Infrastructure

5. **Is it business value or plumbing?**
   - Business value (user pays for) → Feature
   - Plumbing (makes features work) → Infrastructure

---

## 🎯 Summary & Recommendations

### Clear Infrastructure (Should NOT clutter main navigation)
- ✅ `log_manager` - Settings icon → Log viewer
- ✅ `hana_connection` - Background only (no UI)
- ✅ `login_manager` - Login dialog (no nav tab)
- ✅ `feature_manager` - Settings → Feature flags
- ✅ `debug_mode` - Debug panel toggle (no nav tab)

### Clear Features (Should have navigation tabs)
- ✅ `knowledge_graph_v2` ⭐ (Reference implementation)
- ✅ `p2p_dashboard` (Business KPIs)
- ✅ `ai_assistant` (Natural language interface)
- ✅ `knowledge_graph` (Legacy, consider deprecating)

### Hybrid (Both service + feature)
- ✅ `data_products` (Provides IDataSource + Manage UI)

### Developer Tools (Optional navigation, admin-only)
- ✅ `api_playground` (Testing interface)
- ⚠️ `sql_execution` (Consider merging with data_products)
- ⚠️ `csn_validation` (Consider automating, no UI)

---

## 🚀 Impact on App v2 Design

**DependencyContainer Registration**:

```javascript
// Infrastructure modules register services (Phase 2)
DependencyContainer.register('ILogger', () => new LogManagerAdapter());
DependencyContainer.register('IAuthService', () => new LoginManager());
DependencyContainer.register('IFeatureFlags', () => new FeatureManager());
DependencyContainer.register('IDebugger', () => new DebugMode());

// Hybrid modules register services (Phase 3)
DependencyContainer.register('IDataSource', () => new DataProductsAdapter());

// Feature modules consume services (Phase 4)
const kg = new KnowledgeGraphV2(
    DependencyContainer.get('ILogger'),
    DependencyContainer.get('IDataSource')
);
```

**NavigationBuilder**:

```javascript
// Only feature modules + hybrid modules get tabs
const featureModules = registry.getAll()
    .filter(m => m.type === 'feature' || m.type === 'hybrid');

const tabs = featureModules.map(m => 
    new sap.m.IconTabFilter({
        key: m.id,
        icon: m.icon,
        text: m.name
    })
);

// Infrastructure modules: NO tabs (available via DI)
```

---

## 📖 References

**Related Documents**:
- [[Infrastructure vs Feature Modules]] - Original categorization work
- [[App v2 Modular Architecture Plan]] - Overall architecture
- [[Modular Architecture]] - Self-contained module structure

**Key Insight**: Not all modules are equal! Infrastructure provides services, features provide value, hybrids do both. App v2 architecture must handle all three types appropriately.

---

**Date**: February 8, 2026  
**Status**: 📋 ANALYSIS COMPLETE - Ready for user validation and architecture refinement