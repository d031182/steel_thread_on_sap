# Global Context State Management - Industry Standard Patterns

**Date**: 2026-02-16  
**Problem**: Global shell component (AI Assistant) needs access to page-specific state (datasource selection)  
**Context**: Enterprise SPA with modular architecture

---

## The Problem (Industry-Standard Scenario)

**Scenario**: 
- **Global Component**: AI Assistant (shell-bar button, available everywhere)
- **Page-Specific State**: Current datasource ("HANA Cloud" vs "Local")
- **Challenge**: Global component doesn't know current page state

**This is a classic SPA architecture problem solved by multiple industry patterns.**

---

## Industry-Standard Solutions (Ranked by Best Practice)

### 1. ⭐ **Pub/Sub (Observer Pattern)** - RECOMMENDED

**Used By**: Redux, MobX, SAP UI5 EventBus, Angular Services, Vue Event Bus

**How It Works**:
```
Data Products Page → Publishes: "datasource:changed" event
AI Assistant → Subscribes: Listens for event, updates state
```

**Implementation** (Your EventBus):
```javascript
// Data Products Module (Publisher)
_onDatasourceChange: function(datasource) {
    // Update local state
    this._currentDatasource = datasource;
    
    // Broadcast to all subscribers
    eventBus.publish('datasource:changed', {
        datasource: datasource,
        source: 'data_products_v2',
        timestamp: new Date().toISOString()
    });
}

// AI Assistant Module (Subscriber)
initialize: function() {
    // Subscribe to datasource changes
    eventBus.subscribe('datasource:changed', (event) => {
        logger.log('Datasource changed to:', event.datasource);
        currentDatasource = event.datasource;
        // Recreate overlay with new datasource
        overlay = new AIAssistantOverlay(adapter, currentDatasource);
    });
}

// Global shell button
getShellActions: function() {
    return [{
        press: function() {
            // Uses latest datasource from subscription
            overlay.open();
        }
    }];
}
```

**Pros**:
- ✅ Decoupled: Modules don't know about each other
- ✅ Scalable: Any module can subscribe to datasource changes
- ✅ Standard: Used by Redux, Angular, Vue, SAP UI5
- ✅ Testable: Easy to mock events

**Cons**:
- ⚠️ Requires event documentation
- ⚠️ Potential memory leaks if not unsubscribed

---

### 2. ⭐ **Central State Management (Flux/Redux Pattern)**

**Used By**: Redux, Vuex, NgRx, Recoil, Zustand

**How It Works**:
```
Centralized Store
├── Current Datasource: "hana"
├── User Preferences: {...}
└── App State: {...}

All modules read from store
All modules dispatch actions to update store
```

**Implementation** (Store Pattern):
```javascript
// Global State Store (Singleton)
window.AppState = {
    datasource: 'p2p_data',  // Default
    
    setDatasource(datasource) {
        this.datasource = datasource;
        this.notify();
    },
    
    getDatasource() {
        return this.datasource;
    },
    
    subscribers: [],
    subscribe(callback) {
        this.subscribers.push(callback);
    },
    notify() {
        this.subscribers.forEach(cb => cb(this.datasource));
    }
};

// Data Products Module
_onDatasourceChange: function(datasource) {
    AppState.setDatasource(datasource);
}

// AI Assistant Module
initialize: function() {
    AppState.subscribe((datasource) => {
        overlay = new AIAssistantOverlay(adapter, datasource);
    });
}

getShellActions: function() {
    return [{
        press: function() {
            const datasource = AppState.getDatasource();
            overlay = new AIAssistantOverlay(adapter, datasource);
            overlay.open();
        }
    }];
}
```

**Pros**:
- ✅ Single source of truth
- ✅ Predictable state changes
- ✅ Time-travel debugging possible
- ✅ Industry standard (Redux pattern)

**Cons**:
- ⚠️ More boilerplate
- ⚠️ Learning curve for team

---

### 3. ⭐ **Context API Pattern**

**Used By**: React Context, Angular Dependency Injection, Vue Provide/Inject

**How It Works**:
```
App Root
└── ContextProvider (datasource)
    ├── Data Products Page (consumer)
    ├── AI Assistant (consumer)
    └── Other Modules (consumers)
```

**Implementation** (DependencyContainer):
```javascript
// Register datasource in container
container.register('currentDatasource', {
    value: 'p2p_data',
    setValue: function(ds) { this.value = ds; }
});

// Data Products Module
_onDatasourceChange: function(datasource) {
    container.get('currentDatasource').setValue(datasource);
}

// AI Assistant Module
getShellActions: function() {
    return [{
        press: function() {
            const datasource = container.get('currentDatasource').value;
            overlay = new AIAssistantOverlay(adapter, datasource);
            overlay.open();
        }
    }];
}
```

**Pros**:
- ✅ Leverages existing DI container
- ✅ Type-safe (if using TypeScript)
- ✅ Clean API

**Cons**:
- ⚠️ Not reactive by default (need to add observers)
- ⚠️ Container becomes stateful

---

### 4. **URL/Router State Pattern**

**Used By**: React Router, Angular Router, Vue Router

**How It Works**:
```
URL: #/data-products-v2?datasource=hana

AI Assistant reads datasource from URL
Always reflects current page state
```

**Implementation**:
```javascript
// Data Products Module
_onDatasourceChange: function(datasource) {
    // Update URL query parameter
    window.location.hash = `/data-products-v2?datasource=${datasource}`;
}

// AI Assistant Module
getShellActions: function() {
    return [{
        press: function() {
            // Parse datasource from URL
            const params = new URLSearchParams(window.location.hash.split('?')[1]);
            const datasource = params.get('datasource') || 'p2p_data';
            
            overlay = new AIAssistantOverlay(adapter, datasource);
            overlay.open();
        }
    }];
}
```

**Pros**:
- ✅ Shareable URLs
- ✅ Browser back/forward works
- ✅ State persists across page reloads

**Cons**:
- ⚠️ Not all state should be in URL
- ⚠️ URL can get messy

---

### 5. **Local Storage/Session Storage Pattern**

**Used By**: Persistence libraries, user preferences

**How It Works**:
```
Data Products → Saves datasource to localStorage
AI Assistant → Reads datasource from localStorage
```

**Implementation**:
```javascript
// Data Products Module
_onDatasourceChange: function(datasource) {
    localStorage.setItem('currentDatasource', datasource);
}

// AI Assistant Module
getShellActions: function() {
    return [{
        press: function() {
            const datasource = localStorage.getItem('currentDatasource') || 'p2p_data';
            overlay = new AIAssistantOverlay(adapter, datasource);
            overlay.open();
        }
    }];
}
```

**Pros**:
- ✅ Persists across sessions
- ✅ Simple implementation

**Cons**:
- ⚠️ Not reactive (need polling or storage events)
- ⚠️ Storage events don't fire in same tab
- ⚠️ Security concerns for sensitive data

---

## Recommended Approach for Your Architecture

### **Best Practice: Pub/Sub (EventBus)** ⭐⭐⭐

**Why**:
1. ✅ You already have EventBus in place (`app_v2/static/js/core/EventBus.js`)
2. ✅ Aligns with your modular architecture
3. ✅ No coupling between modules (module isolation maintained)
4. ✅ Standard pattern used by SAP UI5, Angular, Vue
5. ✅ Easy to test

**Implementation Steps**:

1. **Define Event Contract** (Documentation):
```javascript
/**
 * Application Events
 * 
 * datasource:changed
 * - Published by: data_products_v2 module
 * - Payload: { datasource: "hana" | "p2p_data", source: string, timestamp: string }
 * - Consumers: ai_assistant, any module needing datasource info
 */
```

2. **Data Products Module** (Publisher):
```javascript
_onDatasourceChange: function(event) {
    const datasource = event.getParameter("selectedItem").getKey();
    this._currentDatasource = datasource;
    
    // Publish event
    this._eventBus.publish('datasource:changed', {
        datasource: datasource,
        source: 'data_products_v2'
    });
}
```

3. **AI Assistant Module** (Subscriber):
```javascript
initialize: async function() {
    // ... existing code ...
    
    // Subscribe to datasource changes
    this._currentDatasource = 'p2p_data'; // Default
    
    eventBus.subscribe('datasource:changed', (event) => {
        logger.log('Datasource changed to:', event.datasource);
        this._currentDatasource = event.datasource;
    });
}

getShellActions: function() {
    return [{
        press: () => {
            // Recreate overlay with latest datasource
            overlay = new AIAssistantOverlay(
                adapter, 
                this._currentDatasource
            );
            overlay.open();
        }
    }];
}
```

---

## Alternative: Hybrid Approach

**Combine Pub/Sub + Router State** (Most Robust):

```javascript
// 1. EventBus for real-time updates
eventBus.subscribe('datasource:changed', (event) => {
    currentDatasource = event.datasource;
});

// 2. URL as fallback (for direct navigation)
getShellActions: function() {
    return [{
        press: () => {
            // Try in-memory state first
            let datasource = this._currentDatasource;
            
            // Fallback to URL if available
            if (!datasource) {
                const params = new URLSearchParams(window.location.hash.split('?')[1]);
                datasource = params.get('datasource') || 'p2p_data';
            }
            
            overlay = new AIAssistantOverlay(adapter, datasource);
            overlay.open();
        }
    }];
}
```

---

## Comparison Matrix

| Pattern | Coupling | Scalability | Reactivity | Complexity | Industry Use |
|---------|----------|-------------|------------|------------|--------------|
| **Pub/Sub** | Low | High | High | Low | ⭐⭐⭐⭐⭐ |
| **Redux** | Low | High | High | Medium | ⭐⭐⭐⭐⭐ |
| **Context** | Medium | Medium | Medium | Low | ⭐⭐⭐⭐ |
| **URL** | Low | High | Low | Low | ⭐⭐⭐ |
| **Storage** | Low | Low | Low | Low | ⭐⭐ |

---

## Implementation Priority

**Immediate** (Quick Win):
1. ✅ EventBus Pub/Sub pattern
2. ✅ Document event contract
3. ✅ Add subscription in AI Assistant
4. ✅ Add publish in Data Products

**Future** (If App Grows):
1. Consider Redux/Zustand for complex state
2. Add URL state for bookmarkable pages
3. Add localStorage for user preferences persistence

---

## References

**Industry Standards**:
- **Redux**: https://redux.js.org/ (Flux pattern)
- **SAP UI5 EventBus**: https://ui5.sap.com/ (Pub/Sub pattern)
- **Angular Services**: https://angular.io/ (DI + Observables)
- **Vue Event Bus**: https://vuejs.org/ (Pub/Sub pattern)

**Your Architecture**:
- EventBus: `app_v2/static/js/core/EventBus.js`
- DependencyContainer: `app_v2/static/js/core/DependencyContainer.js`
- Module Federation: `docs/knowledge/module-federation-standard.md`

---

**Conclusion**: **Pub/Sub via EventBus** is the industry-standard best practice for your scenario, perfectly aligns with your modular architecture, and requires minimal changes to implement.