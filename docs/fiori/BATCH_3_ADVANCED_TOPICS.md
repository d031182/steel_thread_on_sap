# SAPUI5 Batch 3: Advanced Topics - Complete Guide

**Documentation Batch**: 3 of 4  
**Topics Covered**: 10 (Component Lifecycle, Performance, Testing, Smart Controls, Fiori Elements, Annotations, Extensions, i18n, Responsive Design)  
**Date**: January 24, 2026  
**Source**: SAP Official Documentation via Perplexity AI  

---

## 1. Component Lifecycle & Best Practices

### Component Structure
```javascript
sap.ui.define([
    "sap/ui/core/UIComponent",
    "sap/ui/Device"
], function(UIComponent, Device) {
    return UIComponent.extend("yourapp.Component", {
        metadata: {
            manifest: "json"  // References manifest.json
        },
        
        init: function() {
            // Call base init FIRST
            UIComponent.prototype.init.apply(this, arguments);
            
            // Initialize routing
            this.getRouter().initialize();
            
            // Set models
            this.setModel(models.createDeviceModel(), "device");
        },
        
        destroy: function() {
            // Clean up resources
            UIComponent.prototype.destroy.apply(this, arguments);
        }
    });
});
```

### Lifecycle Methods
| Method | When | Purpose |
|--------|------|---------|
| **init** | Startup | Initialize routing, set models, resource bundles |
| **destroy** | Teardown | Release models, handlers, timers to prevent leaks |

### manifest.json Configuration
Centralizes app setup:
- **routing**: Defines routes, targets (views)
- **models**: Predefines OData/JSON models
- **resourceBundles**: i18n configuration

**Best Practices**: 
- Always call base `init`/`destroy`
- Initialize routing in `init`
- Name models for binding clarity
- Use `Component.create()` for dynamic loading

---

## 2. Performance Optimization

### Key Techniques

#### Async Loading
```html
<script 
    src="resources/sap-ui-core.js" 
    data-sap-ui-preload="async"
    data-sap-ui-libs="sap.m">
</script>
```
**Impact**: Non-blocking startup, faster initialization

#### Lazy Loading
- **Views**: Load on navigation via routing
- **Data**: Use `growing="true"` on lists/tables
- **Components**: Dynamic with ComponentContainer

#### OData Optimization
```javascript
// Use $select for projections
oTable.bindRows({
    path: "/Orders",
    parameters: { 
        $select: "OrderID,Customer,Total",
        $top: 20
    }
});
```

#### Bundling & Minification
Use UI5 Tooling: `ui5 build` for production
- Combines JS/CSS into fewer files
- Minifies for smaller payloads

### Performance Guidelines
| Operation | Guideline |
|-----------|-----------|
| **Initial Load** | Async + lazy + CDN |
| **Data Fetching** | $select, $top, batch |
| **Lists/Tables** | growing mode, threshold |
| **Rendering** | Aggregation binding |

**Best Practices**: 
- Use AKAMAI CDN for UI5 resources
- setBusyIndicatorDelay(500) to prevent flashing
- Monitor with UI5 Inspector/Lighthouse
- Batch OData requests (V4 auto-batches)

---

## 3. Testing (QUnit, OPA5)

### Testing Pyramid
- **Unit Tests (QUnit)**: Fast, isolated controller/model tests
- **Integration Tests (OPA5)**: UI interaction simulation
- **E2E Tests**: Optional full-stack validation

### QUnit Unit Tests
```javascript
sap.ui.define([
    "com/myapp/controller/Main.controller",
    "sap/ui/thirdparty/sinon"
], function(MainController) {
    QUnit.module("MainController", {
        beforeEach: function() {
            this.controller = new MainController();
            sinon.stub(this.controller, "getView").returns(oViewStub);
        },
        afterEach: function() {
            this.controller.getView.restore();
        }
    });
    
    QUnit.test("Method works correctly", function(assert) {
        assert.strictEqual(this.controller.callMe(), 42);
    });
});
```

### OPA5 Integration Tests
```javascript
// Page object: test/integration/pages/Main.js
Opa5.createPageObjects({
    onTheMainPage: {
        actions: {
            iPressButton: function() {
                return this.waitFor({
                    controlType: "sap.m.Button",
                    actions: new Press()
                });
            }
        },
        assertions: {
            iSeeTitle: function() {
                return this.waitFor({
                    controlType: "sap.m.Title",
                    success: function() {
                        Opa5.assert.ok(true, "Title found");
                    }
                });
            }
        }
    }
});
```

### Mock Server
```javascript
// test/localService/mockserver.js
var oMockServer = new MockServer({
    rootUri: "/sap/opu/odata/"
});
oMockServer.simulate("localService/metadata.xml", "localService/mockdata");
oMockServer.start();
```

**Best Practices**: 
- Target 80%+ coverage
- Stub external dependencies
- Use beforeEach/afterEach for setup/cleanup
- Run tests in CI/CD
- Mock server for backend isolation

---

## 4. Smart Controls

### Overview
`sap.ui.comp` library controls that leverage OData metadata and annotations for automatic configuration.

### Core Smart Controls
- **SmartField** - Auto-renders appropriate input based on metadata
- **SmartTable** - Table driven by annotations
- **SmartFilterBar** - Self-configuring filter interface
- **SmartChart** - Visualization with annotations
- **SmartVariants** - Saved configurations

### Example
```xml
<smartField:SmartField value="{MaterialID}"/>
<!-- Automatically:
- Shows value help if @Consumption.valueHelpDefinition exists
- Formats based on @Semantics
- Validates based on @FieldControl
-->
```

### OData Metadata Requirements
```javascript
// Entity properties with annotations
{
    "Sortable": true,
    "Filterable": true,
    "sap:label": "Material Number",
    "sap:value-list": "fixed-values"
}
```

**Best Practices**: 
- Use for Fiori Elements apps (automatic)
- Configure via annotations, not code
- Understand metadata vs control issues
- Backend-first approach (SAP Gateway/CDS)

---

## 5. Fiori Elements Overview

### Purpose
Framework providing predefined templates for common app patterns with minimal custom coding.

### Core Templates
| Template | Use Case | Key Features |
|----------|----------|--------------|
| **List Report** | Tabular data + filtering | SelectionFields, LineItem, actions |
| **Object Page** | Object details | HeaderInfo, Facets, sections |
| **Worklist** | Task-oriented lists | Simple list to details |
| **Overview Page** | Dashboard | Cards from multiple sources |

### Development Approach
1. Create OData service (Gateway/CAP)
2. Add UI annotations (CDS/SEGW)
3. Generate app via SAP BAS template
4. Configure manifest.json
5. Add custom extensions if needed

### Key Annotations
```javascript
// CDS View example
@UI.lineItem: [
    { position: 10, label: 'Order ID' },
    { position: 20, label: 'Customer' }
]
@UI.headerInfo: {
    typeName: 'Order',
    title: { value: OrderID }
}
```

**Best Practices**: 
- Use SAP BAS Fiori Tools for guided dev
- Leverage predefined building blocks
- Extend via framework points (not freestyle)
- Test with feature showcase apps

---

## 6. Annotation-Driven Development

### Core Concept
Define UI structure/behavior in OData metadata via vocabularies (UI.v1, Common.v1) instead of code.

### Key UI Annotations
| Annotation | Purpose | Example |
|-----------|---------|---------|
| **UI.LineItem** | Table columns | Collection of DataFields |
| **UI.HeaderInfo** | Object headers | TypeName, Title, Description |
| **UI.Facets** | Form sections | ReferenceFacet, CollectionFacet |
| **UI.SelectionFields** | Filter fields | Array of PropertyPath |
| **Common.ValueList** | Value help | CollectionPath, Parameters |

### CDS Implementation
```sql
@UI.lineItem: [
    { position: 10, label: 'ID', importance: #HIGH },
    { position: 20, label: 'Name' }
]
@UI.headerInfo: {
    typeName: 'Product',
    title: { value: ProductID }
}
define view ProductView as select from Product {
    key ProductID,
    ProductName,
    Price
}
```

### SAP Gateway
Add annotations in SEGW or via XML in `$metadata`:
```xml
<Annotation Term="UI.LineItem">
    <Collection>
        <Record Type="UI.DataField">
            <PropertyValue Property="Value" PropertyPath="ProductID"/>
        </Record>
    </Collection>
</Annotation>
```

**Best Practices**: 
- Define in backend (CDS/SEGW), not locally
- Use BAS Service Modeler for editing
- Test via Fiori Elements floorplans
- Backend-first ensures consistency

---

## 7. Extension Points & Flexibility

### Extension Types

**Custom Sections** (Object Page):
```javascript
// manifest.json
"extends": {
    "extensions": {
        "sap.ui.controllerExtensions": {
            "EntitySet": {
                "EntitySet": "Products",
                "Sections": {
                    "CustomSection": {
                        "id": "customSection1",
                        "type": "XMLFragment",
                        "fragmentName": "com.myapp.ext.CustomSection"
                    }
                }
            }
        }
    }
}
```

**Custom Actions**:
```javascript
// Add button to toolbar
"Actions": {
    "CustomAction": {
        "id": "customAction1",
        "text": "{i18n>CUSTOM_ACTION}",
        "press": "com.myapp.ext.controller.Custom.onCustomAction",
        "enabled": "{= ${ui>/editMode} !== 'Editable' }"
    }
}
```

**Controller Extensions**:
```javascript
// webapp/ext/controller/EntitySet.controller.js
sap.ui.define([], function() {
    return {
        onCustomAction: function() {
            // Custom logic using extensionAPI
            this.extensionAPI.getEditFlow().invokeAction(...);
        }
    };
});
```

**Fragment Extensions**:
```xml
<!-- webapp/ext/CustomSection.fragment.xml -->
<core:FragmentDefinition xmlns="sap.m" xmlns:core="sap.ui.core">
    <VBox>
        <Text text="Custom content"/>
    </VBox>
</core:FragmentDefinition>
```

**Best Practices**: 
- Use extensionAPI ONLY (avoid direct control access)
- Place extensions in `webapp/ext/`
- Add custom columns: Define + implement content
- Test with feature showcase samples

---

## 8. i18n & Localization

### Setup
```
webapp/
└── i18n/
    ├── i18n.properties        # Default (English)
    ├── i18n_de.properties     # German
    ├── i18n_de_AT.properties  # Austrian German
    └── i18n_zh_Hans.properties # Simplified Chinese
```

### manifest.json Configuration
```json
"models": {
    "i18n": {
        "type": "sap.ui.model.resource.ResourceModel",
        "settings": {
            "bundleName": "yourapp.i18n.i18n",
            "supportedLocales": ["", "de", "de_AT", "zh_Hans"],
            "fallbackLocale": "en"
        }
    }
}
```

### Usage in XML
```xml
<Text text="{i18n>welcome}"/>
<Button text="{i18n>saveButton}"/>
```

### Dynamic Parameters
```javascript
// Properties file: helloUser=Hello {0}!

// Controller
var oBundle = this.getModel("i18n").getResourceBundle();
var sText = oBundle.getText("helloUser", ["John"]);  // "Hello John!"

// Or use formatMessage
var sFormatted = oBundle.formatMessage("helloUser", ["John"]);
```

### Locale Detection
Auto-detects via browser/OS locale:
```javascript
var sLocale = sap.ui.getCore().getConfiguration().getLanguage();
// Returns: "en-US", "de-DE", etc.

// Manual set
sap.ui.getCore().getConfiguration().setLanguage("de_DE");
```

**Best Practices**: 
- Start i18n from day one
- Use meaningful keys (app.title not text1)
- Define supportedLocales explicitly
- Test fallback chain
- Never hardcode strings

---

## 9. Device Adaptation & Responsive Design

### Breakpoints
| Size | Range | Device |
|------|-------|--------|
| **S** | Up to 599px | Phone |
| **M** | 600-1024px | Tablet |
| **L** | 1025-1440px | Desktop |
| **XL** | >1440px | Large Desktop |

### sap.ui.Device API
```javascript
// Device detection
if (sap.ui.Device.system.phone) {
    // Phone-specific layout
} else if (sap.ui.Device.system.tablet) {
    // Tablet layout
} else {
    // Desktop layout
}

// Media query handler
sap.ui.Device.media.attachHandler(function(mParams) {
    console.log("Breakpoint:", mParams.name); // "Phone", "Tablet", "Desktop"
}, this, sap.ui.Device.media.RANGESETS.SAP_STANDARD);
```

### Responsive Spacing
```xml
<!-- CSS classes for adaptive spacing -->
<VBox class="sapUiMediumMargin sapUiResponsiveContentPadding">
    <Text text="Content with responsive spacing"/>
</VBox>
```

**Spacing Classes**:
- Margins: sapUiTiny/Small/Medium/LargeMargin
- Padding: sapUiTiny/Small/Medium/LargePadding
- Responsive: sapUiResponsiveMargin, sapUiResponsiveContentPadding

### Responsive Layouts

#### Grid Layout
```xml
<layout:Grid 
    defaultSpan="XL6 L6 M6 S12"
    hSpacing="1"
    vSpacing="1">
    <Text text="Half width on L/XL, full on S"/>
</layout:Grid>
```

#### FlexBox Layout
```xml
<FlexBox
    direction="Row"
    wrap="Wrap"
    fitContainer="true"
    class="sapUiResponsiveMargin">
    <items>
        <Text text="Item 1"/>
        <Text text="Item 2"/>
    </items>
</FlexBox>
```

### Mobile-First Approach
1. Design for phone first (S breakpoint)
2. Enhance for tablet (M)
3. Add desktop features (L/XL)

**Touch-Friendly**: Minimum 44x44px tap targets

**Best Practices**: 
- Use sap.m controls (responsive by default)
- Test across S/M/L/XL breakpoints
- Avoid sap.ui.commons (desktop-only)
- Use REM units for accessibility
- Mobile-first CSS approach
- Test on real devices

---

## Summary - Batch 3

**Topics Covered**: 10 advanced development topics
- Component architecture and lifecycle
- Performance optimization strategies
- Testing approaches (unit + integration)
- Smart Controls for metadata-driven UIs
- Fiori Elements templates
- Annotation-driven development
- Extension points for customization
- i18n and localization
- Responsive design patterns

**Key Takeaways**:
- **Component**: Use init/destroy lifecycle, manifest.json for config
- **Performance**: Async loading, lazy loading, OData optimization
- **Testing**: QUnit for units, OPA5 for integration, mock servers
- **Smart Controls**: Metadata-driven, minimal coding
- **Fiori Elements**: Templates + annotations = apps
- **Annotations**: Backend-defined UI structure
- **Extensions**: Custom sections/actions via manifest + fragments
- **i18n**: ResourceModel + properties files
- **Responsive**: S/M/L/XL breakpoints, sap.ui.Device API

**Developer Impact**: Advanced patterns for enterprise-grade applications

**Combined Coverage (Batches 1+2+3)**: ~90% of SAPUI5 development patterns