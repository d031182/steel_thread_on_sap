# App V2 Module Migration Guide

**Version**: 1.0.0  
**Date**: February 8, 2026  
**Status**: Based on knowledge_graph_v2 reference implementation

---

## 📋 Overview

This guide explains how to migrate existing modules to App V2's modular architecture. The migration enables:

- ✅ **Auto-discovery**: Modules loaded automatically from `module.json`
- ✅ **Dependency Injection**: Loose coupling via interfaces
- ✅ **Event-Driven**: Inter-module communication via EventBus
- ✅ **Graceful Degradation**: Works with or without optional dependencies
- ✅ **Lifecycle Management**: Clean initialization and teardown

---

## 🎯 Migration Checklist

### ⭐ STEP 0: Run Feng Shui Validation (OPTIONAL - Comprehensive Module Analysis)

**OPTIONAL**: Before browser testing, run Feng Shui orchestrator for comprehensive analysis:

```bash
# Run multi-agent analysis on module (6 agents in parallel)
python -c "from pathlib import Path; from tools.fengshui.agents.orchestrator import AgentOrchestrator; \
orchestrator = AgentOrchestrator(); \
report = orchestrator.analyze_module_comprehensive(Path('modules/[module_name]'), parallel=True); \
print(f'Health: {report.synthesized_plan.overall_health_score}/100')"

# Example:
python -c "from pathlib import Path; from tools.fengshui.agents.orchestrator import AgentOrchestrator; \
orchestrator = AgentOrchestrator(); \
report = orchestrator.analyze_module_comprehensive(Path('modules/data_products_v2'), parallel=True); \
print(f'Health: {report.synthesized_plan.overall_health_score}/100')"
```

**What Feng Shui Checks** (6 specialized agents):
1. ✅ **Architecture** (DI violations, SOLID principles, coupling)
2. ✅ **Security** (hardcoded secrets, SQL injection, auth issues)
3. ✅ **UX/Fiori** (SAP Fiori compliance, UI patterns)
4. ✅ **Performance** (N+1 queries, nested loops, caching)
5. ✅ **File Organization** (structure, misplaced files, obsolete detection)
6. ✅ **Documentation** (README quality, docstrings, comment coverage)

**Time**: 5-7 seconds (parallel execution)

**Note**: This step is OPTIONAL - the three-tier quality gate system (pre-commit + pre-push) already provides automated validation. This is mainly useful for deep-dive analysis.

---

### Use this checklist for each module migration:

- [ ] **Step 1**: Create `frontend/module.js` with factory function
- [ ] **Step 2**: Update `module.json` with factory + dependencies
- [ ] **Step 3**: Test module loading in App V2
- [ ] **Step 4**: Verify dependency injection works
- [ ] **Step 5**: Test navigation and routing
- [ ] **Step 6**: Document module-specific setup

---

## 📝 Step-by-Step Migration

### Step 1: Create Module.js Factory

Create `modules/[your-module]/frontend/module.js`:

```javascript
/**
 * [Your Module] Entry Point
 * Module integration for App V2
 */

(function() {
    'use strict';

    /**
     * Module factory function
     * 
     * @param {Object} container - DependencyContainer instance
     * @param {Object} eventBus - EventBus instance
     * @returns {Object} Module interface
     */
    window.[YourModule]Factory = function(container, eventBus) {
        
        // ====================
        // DEPENDENCY RESOLUTION
        // ====================
        
        // Required dependencies (throw error if missing)
        // Example: const dataSource = container.get('IDataSource');
        
        // Optional dependencies (use fallback if missing)
        const logger = container.has('ILogger') 
            ? container.get('ILogger')
            : { 
                log: (msg) => console.log('[YourModule]', msg),
                warn: (msg) => console.warn('[YourModule]', msg),
                error: (msg) => console.error('[YourModule]', msg)
              };

        logger.log('Module initialized');

        // ====================
        // MODULE STATE
        // ====================
        
        let currentView = null;
        let isInitialized = false;

        // ====================
        // PUBLIC API
        // ====================
        
        return {
            /**
             * Get module metadata
             */
            getMetadata: function() {
                return {
                    id: 'your_module_id',
                    name: 'Your Module Name',
                    version: '1.0.0',
                    description: 'Module description',
                    category: 'Data Management', // or Analytics, Configuration, System
                    icon: 'sap-icon://your-icon',
                    dependencies: {
                        required: [], // e.g., ['IDataSource']
                        optional: ['ILogger'] // e.g., ['ILogger', 'ICache']
                    }
                };
            },

            /**
             * Initialize module (called once)
             */
            initialize: async function() {
                if (isInitialized) {
                    logger.warn('Module already initialized');
                    return;
                }

                logger.log('Initializing module...');

                try {
                    // Subscribe to events
                    eventBus.subscribe('app:theme-changed', (data) => {
                        logger.log('Theme changed', data);
                        // Handle theme change
                    });

                    // Your initialization logic here
                    
                    isInitialized = true;
                    logger.log('Module initialized successfully');

                    // Publish initialization event
                    eventBus.publish('module:initialized', {
                        moduleId: 'your_module_id',
                        timestamp: new Date().toISOString()
                    });

                } catch (error) {
                    logger.error('Module initialization failed', error);
                    throw error;
                }
            },

            /**
             * Render module view
             * 
             * @param {string} containerId - DOM element ID
             */
            render: async function(containerId) {
                logger.log('Rendering module in container:', containerId);

                try {
                    const container = document.getElementById(containerId);
                    if (!container) {
                        throw new Error(`Container not found: ${containerId}`);
                    }

                    // Create view (use existing SAPUI5 implementation)
                    if (!window.createYourModulePage) {
                        throw new Error('View factory not found: createYourModulePage');
                    }

                    currentView = window.createYourModulePage();
                    
                    // Initialize view if needed
                    if (window.initializeYourModule) {
                        await window.initializeYourModule(currentView);
                    }

                    // Place view in container
                    currentView.placeAt(containerId);

                    // Publish render event
                    eventBus.publish('module:rendered', {
                        moduleId: 'your_module_id',
                        containerId: containerId,
                        timestamp: new Date().toISOString()
                    });

                    logger.log('Module rendered successfully');

                } catch (error) {
                    logger.error('Module render failed', error);
                    
                    // Show user-friendly error
                    const container = document.getElementById(containerId);
                    if (container) {
                        container.innerHTML = `
                            <div style="padding: 20px; text-align: center;">
                                <p style="color: #d32f2f; font-size: 16px;">
                                    <i class="sap-icon sap-icon--alert"></i>
                                    Failed to load [Your Module]
                                </p>
                                <p style="color: #666; font-size: 14px;">
                                    ${error.message}
                                </p>
                            </div>
                        `;
                    }
                    throw error;
                }
            },

            /**
             * Destroy module and cleanup
             */
            destroy: function() {
                logger.log('Destroying module...');

                try {
                    if (currentView && currentView.destroy) {
                        currentView.destroy();
                        currentView = null;
                    }

                    eventBus.publish('module:destroyed', {
                        moduleId: 'your_module_id',
                        timestamp: new Date().toISOString()
                    });

                    logger.log('Module destroyed successfully');

                } catch (error) {
                    logger.error('Module destroy failed', error);
                }
            },

            /**
             * Check if module can be activated
             */
            canActivate: function() {
                // Check required dependencies
                // Return false if missing
                return true;
            },

            /**
             * Get module status
             */
            getStatus: function() {
                return {
                    initialized: isInitialized,
                    hasView: currentView !== null,
                    dependencies: {
                        // List resolved dependencies
                    }
                };
            }
        };
    };

    console.log('[YourModule] Module factory registered');

})();
```

---

### Step 2: Update module.json

Update `modules/[your-module]/module.json`:

```json
{
  "name": "your_module",
  "version": "1.0.0",
  "description": "Your module description",
  "enabled": true,
  "backend": {
    "blueprint": "modules.your_module.backend:blueprint",
    "mount_path": "/api/your-module"
  },
  "frontend": {
    "page_name": "your-module",
    "nav_title": "Your Module",
    "nav_icon": "sap-icon://your-icon",
    "scripts": [
      "modules/your_module/frontend/module.js",
      "modules/your_module/frontend/views/yourModulePage.js"
    ],
    "styles": [
      "modules/your_module/frontend/styles/yourModule.css"
    ],
    "entry_point": {
      "factory": "YourModuleFactory",
      "create_function": "createYourModulePage",
      "init_function": "initializeYourModule"
    }
  },
  "dependencies": {
    "required": [],
    "optional": ["ILogger", "IDataSource"]
  }
}
```

**Key Changes**:
1. Add `module.js` as **first script** in `scripts` array
2. Add `entry_point.factory` with factory function name
3. Change `dependencies` from array to object with `required` and `optional`

---

### Step 3: Test Module Loading

Start the Flask app and navigate to App V2:

```bash
# Start server
python app/app.py

# Open browser
http://localhost:5000/v2
```

**What to Check**:
1. ✅ Module appears in navigation menu
2. ✅ Factory function is called on module load
3. ✅ Dependencies are resolved correctly
4. ✅ View renders in content area
5. ✅ No console errors

---

### Step 4: Verify Dependency Injection

**Test with optional dependencies missing**:

```javascript
// In browser console:
DependencyContainer.clear(); // Remove all services
// Navigate to your module
// Should work with fallback logger
```

**Test with optional dependencies present**:

```javascript
// In browser console:
DependencyContainer.register('ILogger', () => new LogManager());
// Navigate to your module
// Should use LogManager instead of fallback
```

---

### Step 5: Test Navigation and Routing

**Test scenarios**:
1. ✅ Direct URL: `http://localhost:5000/v2#your-module`
2. ✅ Menu navigation: Click module in nav menu
3. ✅ Back/Forward buttons: Browser history works
4. ✅ Page refresh: Module loads correctly after F5

---

## 🔧 Common Patterns

### Pattern 1: Optional Logger Dependency

```javascript
const logger = container.has('ILogger') 
    ? container.get('ILogger')
    : {
        log: (msg) => console.log('[Module]', msg),
        warn: (msg) => console.warn('[Module]', msg),
        error: (msg) => console.error('[Module]', msg)
      };
```

### Pattern 2: Required DataSource Dependency

```javascript
if (!container.has('IDataSource')) {
    throw new Error('IDataSource required but not available');
}
const dataSource = container.get('IDataSource');
```

### Pattern 3: Event Subscription

```javascript
// Subscribe to relevant events
eventBus.subscribe('data:updated', async (data) => {
    logger.log('Data updated, refreshing view', data);
    if (currentView && currentView.refresh) {
        await currentView.refresh();
    }
});
```

### Pattern 4: Event Publishing

```javascript
// Publish events for other modules
eventBus.publish('your-module:action-completed', {
    action: 'refresh',
    timestamp: new Date().toISOString(),
    data: { /* ... */ }
});
```

---

## 🚨 Common Pitfalls

### ❌ Pitfall 1: Forgetting module.js in scripts array

**Problem**: Factory not found error

**Solution**: Add `module.js` as **first script** in `module.json`:

```json
"scripts": [
  "modules/your_module/frontend/module.js",  // <-- MUST BE FIRST
  "modules/your_module/frontend/views/page.js"
]
```

### ❌ Pitfall 2: Wrong factory function name

**Problem**: `Factory function not found` error

**Solution**: Ensure factory name in module.json matches window global:

```javascript
// module.js
window.YourModuleFactory = function() { ... };

// module.json
"entry_point": {
  "factory": "YourModuleFactory"  // <-- MUST MATCH
}
```

### ❌ Pitfall 3: Not handling missing dependencies

**Problem**: Module crashes when optional dependency missing

**Solution**: Always check `container.has()` before using optional deps:

```javascript
const logger = container.has('ILogger') 
    ? container.get('ILogger')
    : /* fallback */;
```

### ❌ Pitfall 4: Not cleaning up resources

**Problem**: Memory leaks, duplicate event handlers

**Solution**: Implement proper `destroy()` method:

```javascript
destroy: function() {
    if (currentView && currentView.destroy) {
        currentView.destroy();
    }
    // Unsubscribe from events if needed
}
```

---

## 📊 Migration Status Tracker

Track your module migrations:

| Module | module.js | module.json | Tested | Status |
|--------|-----------|-------------|--------|--------|
| knowledge_graph_v2 | ✅ | ✅ | ✅ | ✅ Complete |
| data_products | ⬜ | ⬜ | ⬜ | 🚧 Pending |
| p2p_dashboard | ⬜ | ⬜ | ⬜ | 🚧 Pending |
| api_playground | ⬜ | ⬜ | ⬜ | 🚧 Pending |
| ai_assistant | ⬜ | ⬜ | ⬜ | 🚧 Pending |
| feature_manager | ⬜ | ⬜ | ⬜ | 🚧 Pending |
| knowledge_graph (v1) | ⬜ | ⬜ | ⬜ | 🚧 Pending |

---

## 📚 Reference Implementation

**knowledge_graph_v2** is the reference implementation. Study these files:

- `modules/knowledge_graph_v2/frontend/module.js` - Complete factory pattern
- `modules/knowledge_graph_v2/module.json` - Proper configuration
- `app_v2/static/js/core/ModuleRegistry.js` - How modules are loaded

---

## 🆘 Getting Help

**Common Issues**:
1. Module not appearing in nav → Check `enabled: true` in module.json
2. Factory not found → Check factory name matches between files
3. Dependencies not working → Check container.has() before using
4. Render fails → Check view factory function exists

**Resources**:
- `app_v2/README.md` - App V2 architecture overview
- `app_v2/static/js/core/` - Core infrastructure code
- `docs/knowledge/app-v2-modular-architecture-plan.md` - Complete design

---

**Last Updated**: February 8, 2026  
**Author**: P2P Development Team