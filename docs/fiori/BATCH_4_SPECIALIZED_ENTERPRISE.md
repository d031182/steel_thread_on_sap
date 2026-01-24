# SAPUI5 Batch 4: Specialized & Enterprise Topics - Complete Guide

**Documentation Batch**: 4 of 4  
**Topics Covered**: 10 (Accessibility, Security, SAP BAS, Deployment, Custom Controls, Popovers, Layouts, Empty States, Search/Filter, Personalization)  
**Date**: January 24, 2026  
**Source**: SAP Official Documentation via Perplexity AI  

---

## 1. Accessibility (A11y) & WCAG 2.2 Standards

### Standards Compliance

SAPUI5 1.136+ implements **WCAG 2.2 and ARIA 1.2 specifications**, meeting current industry standards for inclusive design.[SAP follows WCAG 2.2 as basis for design, development, testing, and accessibility reporting]

### Built-in Accessibility Features

**Keyboard Navigation**:
- Full navigation and control interaction support
- Proper tab order management
- Clear focus visualization for keyboard users

**Screen Reader Support**:
- Compatibility with assistive technologies
- Semantic markup and proper labeling
- ARIA implementation for dynamic content

**Visual Support**:
- High Contrast theming for low vision users
- Browser zoom support with layout adaptation
- Target size: Minimum 24x24 pixel interactive elements

### WCAG 2.2 Key Requirements

| Requirement | Implementation |
|-------------|----------------|
| **Target Size** | 24x24px minimum interactive elements |
| **Alternative Input** | Drag-and-drop can be done with single pointer actions |
| **Redundancy Prevention** | Avoid redundant data entry |
| **Consistent Navigation** | Predictable navigation patterns |

### Developer Best Practices

```javascript
// Use UI5 controls correctly without overriding accessibility
<Button text="Submit" 
        ariaLabelledBy="formTitle"
        press="onSubmit"/>

// Provide meaningful labels
<Label text="Email Address" labelFor="emailInput"/>
<Input id="emailInput" value="{/email}"/>

// Group related content
<Panel headerText="Personal Information"
       accessible="true"
       ariaLabelledBy="panelHeader">
    <!-- Form fields -->
</Panel>
```

**Key Guidelines**:
- ✅ Use UI5 controls correctly without overriding accessibility features
- ✅ Follow updated UI5 Accessibility Guide
- ✅ Implement both framework-level and application-level measures
- ❌ Don't customize controls in ways that break accessibility
- ✅ Test with screen readers, keyboard-only, and high contrast

---

## 2. Security Best Practices

### Input Validation and Sanitization

**Always validate and sanitize user inputs** before processing or rendering:

```javascript
// Use SAPUI5 model types for automatic validation
<Input value="{
    path: 'age',
    type: 'sap.ui.model.type.Integer'
}"/>

// Sanitize untrusted data in controllers
var sSafeText = jQuery.sap.encodeHTML(sUserInput);
this.byId("display").setText(sSafeText);
```

**ESLint Integration**:
```bash
npm install eslint eslint-config-ui5 --save-dev
```

`.eslintrc.json`:
```json
{
  "extends": ["eslint-config-ui5"]
}
```

### XSS Prevention

**Cross-Site Scripting** occurs when untrusted input renders as executable code:

```xml
<!-- GOOD: Default escaping enabled -->
<Text text="{/userInput}"/>

<!-- AVOID: HTML mode without sanitization -->
<FormattedText htmlText="{/unsafeHtml}"/>

<!-- SAFE: Use escape=true explicitly -->
<Text text="{path: '/data', escape: true}"/>
```

**Scanning Tools**:
- Cybersecurity Extension for SAP (CES): Detects 900+ UI5 vulnerabilities
- ESLint with ui5 config: Development-time checks

### CSRF Protection

```javascript
// OData V2: Automatic token handling
var oModel = new sap.ui.model.odata.v2.ODataModel("/sap/opu/odata/...");

// Manual AJAX: Include CSRF token
jQuery.ajax({
    url: "/api/endpoint",
    method: "POST",
    headers: {
        "X-CSRF-Token": oCsrfToken
    },
    data: oPayload
});
```

### Content Security Policy (CSP)

```html
<!-- Configure in server or BTP -->
<meta http-equiv="Content-Security-Policy" 
      content="script-src 'self' sapui5.hana.ondemand.com;
               style-src 'self' 'unsafe-inline';">
```

**Best Practices**:
- Allow only trusted domains
- Avoid inline scripts/styles
- Use nonce or hash-based whitelisting

### Authentication and Authorization

```javascript
// Use SAP Cloud Identity Services for SSO
// Define granular roles
// Monitor access via BTP audit logs

// Example: Role-based UI visibility
if (oUserInfo.hasRole("ADMIN")) {
    this.byId("adminPanel").setVisible(true);
}
```

### Security Checklist

| Practice | Tool/Method | Purpose |
|----------|-------------|---------|
| Input Validation | Model types, ESLint | Prevent injection |
| XSS Prevention | Escaping, CSP | Block script execution |
| CSRF Protection | Tokens via OData | Prevent forged requests |
| Authorization | SSO/MFA, roles | Control access |
| Code Review | CES, ESLint | Detect 900+ issues |
| Data Protection | Encryption | Secure data |
| Monitoring | BTP logs, SIEM | Detect anomalies |

---

## 3. SAP Business Application Studio (BAS) & Fiori Tools

### Overview

SAP BAS is a **cloud-based IDE on SAP BTP** for developing SAP Fiori applications with:
- Dev spaces with pre-installed extensions
- Templates and generators
- Modelers and editors
- Preview and deployment tools

### Setup Process

**1. Access BAS**:
- Log in to SAP BTP Cockpit
- Assign BAS entitlements to subaccount
- Subscribe to service
- Assign role collections to users

**2. Create Dev Space**:
```
Dev Space Types:
- SAP Fiori: UI5/Fiori apps with drag-and-drop
- ABAP: RAP/ABAP development
- CAP/Full-stack: Backend + frontend
```

**3. Workspace Setup**:
- Create workspace for your project
- Isolated environment with predefined tools
- Explorer, editor, terminal, sidebar

### Fiori Application Generator

**Wizard-based approach**:
1. Start generator from command palette
2. Select template (Freestyle, Worklist, List Report)
3. Connect to OData service
4. Configure UI (XML views, drag-and-drop)
5. Generate project structure

```bash
# Command palette (F1)
> Fiori: Open Application Generator
```

### Service Modeler

- Design OData/CDS models
- Bind to live data sources
- Visual modeling of entities and relationships

### Annotation Editor

- Edit CDS annotations for UI semantics
- Field labels, behaviors, value helps
- Fiori adaptations without code

### Preview and Debug

```bash
# Start preview
npm start

# Debug in browser
# Set breakpoints in JavaScript
# Use browser DevTools
```

### Deployment Features

**Build and Deploy**:
```bash
# Build MTA
npm run build

# Deploy to BTP
cf deploy mta_archives/myapp.mtar

# Register in Fiori Launchpad
# Monitor via BTP Cockpit
```

### Best Practices

- ✅ Use Fiori Tools extension
- ✅ Test thoroughly before deployment
- ✅ Follow SAPUI5 standards
- ✅ Use Git for version control
- ✅ Secure with BTP framework
- ✅ Use Guided Answers for troubleshooting

---

## 4. Deployment & CI/CD

### SAPUI5 Deployment to SAP BTP Cloud Foundry

**Deployment targets**:
- HTML5 Application Repository (central repo for UI5 apps)
- Cloud Foundry runtime
- Fiori Launchpad integration

### MTA (Multi-Target Application) Structure

**mta.yaml example**:
```yaml
ID: myui5-app
version: 1.0.0

modules:
  - name: myui5-app
    type: html5
    path: ./ui5-app
    parameters:
      html5-runtime:
        extension: ".html5"
        repo:
          type: cf
          name: my-html5-repo
    requires:
      - name: myui5-app-destination
```

### CI/CD Pipeline with SAP CI/CD Service

**Complete Setup**:

**1. Subscribe to SAP CI/CD**:
- BTP Cockpit → Services → Continuous Integration & Delivery
- Log in with BTP credentials

**2. Add Credentials**:
```
GitHub: Token for repo access
CF Deploy: BTP user/pass or service key
```

**3. Add Repository**:
- Repositories tab → Add
- GitHub repo URL, branch (main)
- Generate webhook secret

**4. Create Job** (Job Editor Mode):
```
Pipeline Stages:
├── Build
│   ├── npm install
│   ├── ui5 build
│   └── mbt build (.mtar output)
├── Test
│   ├── Unit tests (QUnit)
│   └── Linting
├── Acceptance (optional)
│   └── Integration tests
└── Release
    ├── Deploy to CF
    └── Activate in HTML5 Repo
```

**5. Configure Release Stage**:
```
Deploy to Cloud Foundry Space: ON
Organization: <your-org>
API Endpoint: https://api.cf.eu10.hana.ondemand.com
Space: <your-space>
Credentials: <CF credentials>
```

**6. GitHub Webhook**:
```
Settings > Webhooks > Add
Payload URL: <from CI/CD>
Secret: <webhook secret>
Events: Push to main
```

### GitHub Actions Pipeline

**.github/workflows/deploy.yml**:
```yaml
name: UI5 MTA Deploy

on:
  push:
    branches: [main]

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Build UI5 app
        run: npm run build
      
      - name: Build MTA
        run: |
          npm install -g mbt
          mbt build
      
      - name: Deploy to Cloud Foundry
        uses: SAP/cf-mta-deploy-action@v1
        with:
          cfApiEndpoint: ${{ secrets.CF_API }}
          cfOrg: ${{ secrets.CF_ORG }}
          cfSpace: ${{ secrets.CF_SPACE }}
          cfUser: ${{ secrets.CF_USER }}
          cfPassword: ${{ secrets.CF_PASSWORD }}
          mtaPath: mta_archives
```

### Jenkins Pipeline

```groovy
pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        sh 'npm install'
        sh 'ui5 build'
      }
    }
    stage('Test') {
      steps {
        sh 'npm test'
      }
    }
    stage('Deploy MTA') {
      steps {
        sh 'mbt build'
        sh 'cf deploy mta_archives/*.mtar'
      }
    }
  }
}
```

### Best Practices

| Practice | Implementation |
|----------|----------------|
| **Security** | Service keys/OAuth for CF (not user/pass) |
| **Stages Order** | Plan → Code → Scan → Build → UT → Package → Deploy |
| **Artifacts** | Archive .mtar to Nexus/GitHub Packages |
| **Testing** | QUnit for UI5, aim >80% coverage |
| **Branching** | main for prod, dev for QA |
| **Monitoring** | CI/CD logs + CF app logs |
| **UI5-Specific** | ui5-deploy.yaml for repo/transport targets |

---

## 5. Custom Control Development

### Basic Structure

```javascript
sap.ui.define([
    "sap/ui/core/Control"
], function(Control) {
    "use strict";
    
    return Control.extend("your.namespace.CustomControl", {
        metadata: {
            library: "your.namespace",
            properties: {
                width: { type: "sap.ui.core.CSSSize" },
                height: { type: "sap.ui.core.CSSSize" },
                text: { type: "string" }
            },
            aggregations: {
                content: {
                    type: "sap.ui.core.Control",
                    multiple: true,
                    singularName: "content"
                }
            },
            events: {
                press: {}
            }
        },
        
        renderer: function(oRm, oControl) {
            oRm.write("<div");
            oRm.writeControlData(oControl);
            oRm.writeAttributeEscaped("style", 
                "width: " + oControl.getWidth() + 
                "; height: " + oControl.getHeight() + ";");
            oRm.writeClasses();
            oRm.write(">");
            
            // Render aggregations
            var aContent = oControl.getContent();
            for (var i = 0; i < aContent.length; i++) {
                oRm.renderControl(aContent[i]);
            }
            
            oRm.write("</div>");
        },
        
        onBeforeRendering: function() {
            // Actions before DOM update
        },
        
        onAfterRendering: function() {
            // Actions after DOM rendered
            // Initialize 3rd-party libs here
        },
        
        ontap: function(oEvent) {
            this.firePress();
        }
    });
});
```

### Metadata Components

**Properties** (typed values):
```javascript
properties: {
    value: { type: "string", defaultValue: "" },
    enabled: { type: "boolean", defaultValue: true },
    width: { type: "sap.ui.core.CSSSize", defaultValue: "100%" }
}
```

**Aggregations** (child controls):
```javascript
aggregations: {
    items: {
        type: "sap.ui.core.Control",
        multiple: true,
        singularName: "item"
    }
},
defaultAggregation: "items"
```

**Events** (custom events):
```javascript
events: {
    change: {
        parameters: {
            value: { type: "string" }
        }
    }
}
```

### Renderer Function

**RenderManager methods**:
```javascript
oRm.writeControlData(oControl);     // MANDATORY for SAPUI5 tracking
oRm.writeAttribute("id", sId);       // Custom attributes
oRm.writeAttributeEscaped("data-value", sValue);
oRm.writeClasses();                  // CSS classes
oRm.write("<div>");                  // HTML tags
oRm.renderControl(oChildControl);    // Nested controls
oRm.write("</div>");
```

### Lifecycle Methods

| Method | When | Purpose |
|--------|------|---------|
| **init** | Once at creation | Constructor-like initialization |
| **onBeforeRendering** | Before each render | Prepare data, DOM not changed yet |
| **onAfterRendering** | After each render | DOM available, init 3rd-party libs |
| **exit** | Control destruction | Cleanup, prevent memory leaks |

### Usage in XML Views

```xml
<mvc:View xmlns:custom="your/namespace">
    <custom:CustomControl 
        width="200px" 
        height="100px"
        text="Hello"
        press="onCustomPress">
        <custom:content>
            <Label text="Child content"/>
        </custom:content>
    </custom:CustomControl>
</mvc:View>
```

### Best Practices

- ✅ Extend sap.ui.core.Control for full control
- ✅ Use TypeScript for better IDE support
- ✅ Organize in library/namespace for reuse
- ✅ Always call oRm.writeControlData()
- ✅ Avoid DOM queries in renderer
- ✅ Init 3rd-party wrappers in onAfterRendering
- ✅ Declare library in metadata
- ✅ Modularize CSS separately
- ✅ Test design-time support
- ✅ Call parent methods in lifecycle hooks

---

## 6. Popovers & Contextual UI

### Core Popover Types

**sap.m.Popover**:
- Always displays as popover
- Use only for minimal content on smartphones
- Can consume excessive screen space on mobile

**sap.m.ResponsivePopover** ⭐ **RECOMMENDED**:
- Adaptive: Dialog on smartphones, popover on tablets/desktops
- Closed with X button on mobile
- Better responsive behavior

### Popover Structure

```javascript
var oPopover = new sap.m.Popover({
    title: "Product Details",
    placement: sap.m.PlacementType.Right,
    content: [
        new sap.m.Text({ text: "Details here" })
    ],
    footer: new sap.m.Toolbar({
        content: [
            new sap.m.Button({
                text: "Close",
                press: function() {
                    oPopover.close();
                }
            })
        ]
    })
});

// Open popover
oPopover.openBy(oButton);
```

### Structure Components

| Component | Guidelines |
|-----------|-----------|
| **Back button** (optional) | Required only if users can trigger nested popovers |
| **Title** (optional) | Brief, descriptive |
| **Content** | Max 2 groups, 8 fields, single-column tables |
| **Actions/Footer** (optional) | Action buttons for user interactions |

### Placement and Positioning

```javascript
// Placement types
sap.m.PlacementType.Right      // Default
sap.m.PlacementType.Left
sap.m.PlacementType.Top
sap.m.PlacementType.Bottom
sap.m.PlacementType.Auto       // System determines best position
```

### Modal Mode

```javascript
var oModalPopover = new sap.m.Popover({
    modal: true,  // Blocks entire screen
    title: "Confirm Action",
    content: [
        new sap.m.Text({ text: "Are you sure?" })
    ],
    beginButton: new sap.m.Button({
        text: "Confirm",
        press: function() {
            // Action
            oModalPopover.close();
        }
    }),
    endButton: new sap.m.Button({
        text: "Cancel",
        press: function() {
            oModalPopover.close();
        }
    })
});
```

### When to Use

**Use Popover if:**
- You need custom structure
- You want UI elements not available with Quick View

**Use Quick View if:**
- Standardized display is sufficient
- Predefined structure works

**Don't Use Popover if:**
- Objects appear in list-detail layout (show in details area)

### Best Practices

- ✅ Keep content concise
- ✅ Never stack popovers (show in place)
- ✅ Use responsive variants for cross-device compatibility
- ✅ Use descriptive text for accessibility
- ✅ Limit content to prevent mobile screen issues
- ❌ Don't overload with information

---

## 7. DynamicPage Header & Advanced Layouts

### DynamicPage Structure

```xml
<f:DynamicPage 
    headerPinnable="true"
    toggleHeaderOnTitleClick="true"
    preserveHeaderStateOnScroll="true">
    
    <f:title>
        <f:DynamicPageTitle>
            <f:breadcrumbs>
                <m:Breadcrumbs currentLocationText="Details"/>
            </f:breadcrumbs>
            
            <f:expandedContent>
                <m:Text text="Expanded view content"/>
            </f:expandedContent>
            
            <f:snappedContent>
                <m:Text text="Compact view"/>
            </f:snappedContent>
            
            <f:actions>
                <m:Button text="Edit" icon="sap-icon://edit"/>
                <m:Button text="Save" icon="sap-icon://save"/>
            </f:actions>
        </f:DynamicPageTitle>
    </f:title>
    
    <f:header>
        <f:DynamicPageHeader pinnable="true">
            <m:Panel headerText="Header Content">
                <!-- Charts, KPIs, etc. -->
            </m:Panel>
        </f:DynamicPageHeader>
    </f:header>
    
    <f:content>
        <m:Table items="{/data}">
            <!-- Table content -->
        </m:Table>
    </f:content>
</f:DynamicPage>
```

### Key Aggregations

| Aggregation | Purpose | Key Features |
|-------------|---------|--------------|
| **DynamicPageTitle** | Key object info | heading, subheading, breadcrumbs, actions |
| **DynamicPageHeader** | Below title | Any controls, expand/collapse, pinnable |
| **content** | Main scrollable area | Tables, forms, supports sticky subheaders |
| **breadcrumbs** | Navigation path | sap.m.Breadcrumbs |
| **actions** | Primary actions | Button array (Save, Cancel, etc.) |

### Expand/Collapse Behavior

**States**:
- **Expanded**: Full header visible
- **Snapped**: Compact, sticky on scroll
- **Pinned**: User-locked sticky state

**Configuration**:
```javascript
headerPinnable="true"          // User can pin header
toggleHeaderOnTitleClick="true" // Click title to expand/collapse
```

### Sticky Header and Subheader

```xml
<!-- Sticky subheader with IconTabBar -->
<f:DynamicPage 
    stickySubheaderProvider="iconTabBar"
    fitContent="true">
    
    <f:content>
        <IconTabBar id="iconTabBar" sticky="true">
            <!-- Tabs -->
        </IconTabBar>
    </f:content>
</f:DynamicPage>
```

**Known Issue** (SAPUI5 1.71.64+):
- Header with IconTabBar "jumps" on scroll-up when pinned
- Workaround: `fitContent="true"` (disables some table stickiness)
- Fixed in later versions

### Best Practices

**Content Guidelines**:
- ✅ Limit header content to essentials (KPIs, images)
- ✅ Max 3-5 actions
- ✅ Use semantic hierarchy

**Responsive Design**:
- ✅ Use snappedContent for mobile (compact view)
- ✅ Test breakpoints for breadcrumbs/actions swap
- ✅ Combine with FlexibleColumnLayout for complex apps

**Performance**:
- ✅ Lazy-load header content
- ✅ Use fitContainer="true" for auto-sizing
- ❌ Don't overload header (causes scroll jumps)

---

## 8. Empty States & No Data Handling

### IllustratedMessage Control

```javascript
var oEmptyState = new sap.f.IllustratedMessage({
    illustrationType: sap.f.IllustratedMessageType.NoSearchResults,
    title: "No Results Found",
    description: "Try different keywords or check your filters.",
    additionalContent: [
        new sap.m.Button({
            text: "Clear Filters",
            press: function() {
                // Reset filters
            }
        })
    ]
});

// Show in table when no data
if (aData.length === 0) {
    oTable.setNoData(oEmptyState);
}
```

### When to Show Empty States

Show empty states when:
- ✅ No activities, mail, or initial setup (first-time use)
- ✅ No search results or filter results
- ✅ Task completion with no output
- ✅ Empty lists, panels, dashboards, or alerts

❌ Never leave screens feeling empty or showing blank space

### Structure Components

| Component | Guidelines | Example |
|-----------|-----------|---------|
| **Primary message (headline)** | Single-line explanation | "No search results" |
| **Description** | 3 lines max; context and next steps | "Try different keywords" |
| **Call to action** | Secondary button or link | "Add data", "Clear filters" |
| **Illustration** | Optional, context-specific | Experiment empty/error states |

### Design Guidelines

**Messaging**:
```javascript
// GOOD: Relatable, actionable
title: "No results for 'budget spreadsheet'"
description: "Try fewer keywords or check spelling."

// BAD: Negative, unhelpful
title: "Nothing found"
description: "No data."
```

**Types**:
- **Informational**: Basic no-data notification
- **Action-oriented**: With CTAs or links to docs/tasks

### Best Practices

- ✅ Explain what *would* appear with data
- ✅ Guide next steps clearly
- ✅ Use consistent visuals (colors, fonts, spacing)
- ✅ Headline first, then description, then CTA
- ✅ Minimal illustrations that aid understanding
- ✅ Never use primary buttons (use secondary)
- ✅ Ensure user has permissions for suggested actions
- ✅ Accessible: Clear copy, proper hierarchy
- ✅ Test translations
- ❌ Don't leave screens feeling "empty" or negative

---

## 9. Search & Filter Patterns

### Core Controls

**SearchField** (sap.m.SearchField):
```xml
<SearchField 
    width="300px"
    placeholder="Search products..."
    search="onSearch"
    liveChange="onLiveSearch"/>
```

**FilterBar** (sap.ui.comp.filterbar.FilterBar):
- Customizable bar for predefined filters
- Supports client-side and server-side filtering

**SmartFilterBar** (sap.ui.comp.smartfilterbar.SmartFilterBar):
- Auto-generates filters from OData metadata
- Ideal for Fiori apps with server-side integration

### Client-Side Filtering

```javascript
onSearch: function(oEvent) {
    var sValue = oEvent.getParameter("value");
    var aFilters = [];
    
    if (sValue) {
        // Multi-field search (OR condition)
        aFilters.push(
            new Filter("ProductID", FilterOperator.Contains, sValue)
        );
        aFilters.push(
            new Filter("Name", FilterOperator.Contains, sValue)
        );
        aFilters.push(
            new Filter("Category", FilterOperator.Contains, sValue)
        );
    }
    
    // Combine with OR
    var oFinalFilter = new Filter({
        filters: aFilters,
        and: false  // OR condition
    });
    
    // Apply to table binding
    this.byId("productsTable")
        .getBinding("items")
        .filter(oFinalFilter);
}
```

### Server-Side Filtering

```javascript
// Create filter
var oFilter = new Filter("Status", FilterOperator.EQ, "Active");

// Option 1: Model read
oModel.read("/Products", {
    filters: [oFilter],
    success: function(oData) {
        // Handle results
    }
});

// Option 2: Binding with filters
var oTable = this.byId("table");
oTable.bindItems({
    path: "/Products",
    template: oItemTemplate,
    filters: [oFilter]
});

// Result: OData URL includes $filter=Status eq 'Active'
```

### Sorting and Grouping

**Sorting**:
```javascript
var oSorter = new Sorter("ProductName", false); // Ascending
var oSorterDesc = new Sorter("Price", true);     // Descending

oBinding.sort([oSorter]);

// Server-side: Generates $orderby=ProductName asc
```

**Grouping**:
```javascript
var oGrouper = new Sorter("Category", false, true); // group=true

oBinding.sort([oGrouper]);

// Groups items by Category in UI
```

### Filter Operators

| Operator | Use Case | Example |
|----------|----------|---------|
| **Contains** | Text search | Name contains "Book" |
| **EQ** | Exact match | Status equals "Active" |
| **NE** | Not equal | Type not equals "Draft" |
| **GT** | Greater than | Price > 100 |
| **LT** | Less than | Quantity < 10 |
| **GE** | Greater or equal | Stock >= 50 |
| **LE** | Less or equal | Age <= 65 |
| **BT** | Between | Date between start and end |

### Best Practices

**Performance**:
- ✅ Prefer server-side for large datasets
- ✅ Client-side for small/cached data
- ✅ Limit filters to high-use fields

**Multi-field Search**:
- ✅ Use `and: false` for OR across fields
- ✅ Search "80" matches name OR category

**Empty Handling**:
- ✅ Skip filter creation if value is empty
- ❌ Don't filter with empty values (hides all data)

**UI Placement**:
- ✅ SearchField in toolbar/header
- ✅ FilterBar as dedicated bar above content
- ✅ SmartFilterBar for metadata-driven apps

---

## 10. Personalization & User Settings

### SmartTable Personalization

```xml
<smartTable:SmartTable 
    entitySet="Products"
    useTablePersonalisation="true"
    showRowCount="true"
    enableAutoBinding="true">
    <!-- Table content -->
</smartTable:SmartTable>
```

**Features**:
- Settings icon in toolbar opens personalization dialog
- Users can:
  * Control column visibility and ordering
  * Configure data sorting
  * Apply filtering and grouping
- Fields sortable, filterable, groupable by default unless marked:
  ```xml
  sap:sortable="false"
  sap:filterable="false"
  sap:groupable="false"
  ```

### VariantManagement Control

```xml
<smartVariantManagement:SmartVariantManagement 
    id="variantManagement"
    persistencyKey="myAppVariants"
    showShare="true"/>
```

**Capabilities**:
- Save current filter bar and table settings as named views
- Quickly switch between saved configurations
- Persist changes for future sessions
- Share public views with other users (requires BTP configuration)

### Personalization Engine (sap.m.p13n.Engine)

For custom controls or Freestyle applications:

```javascript
// Initialize engine
var oP13nEngine = sap.m.p13n.Engine.getInstance();

// Register control
oP13nEngine.register(oTable, {
    helper: new sap.m.p13n.PersistenceProvider({
        control: oTable
    }),
    controller: {
        Columns: new sap.m.p13n.SelectionController({
            targetAggregation: "columns",
            control: oTable
        }),
        Sort: new sap.m.p13n.SortController({
            control: oTable
        }),
        Group: new sap.m.p13n.GroupController({
            control: oTable
        })
    }
});

// Open personalization dialog
oP13nEngine.show(oTable, ["Columns", "Sort"]);
```

### Controller Types

| Controller | Purpose |
|-----------|---------|
| **SelectionController** | Column visibility |
| **SortController** | Data sorting |
| **GroupController** | Data grouping |

### Selection Mode Configuration

```javascript
// Change from ClearAll to SelectAll mode
oP13nEngine.attachEventOnce("beforeShow", function(oEvent) {
    var oDialog = oEvent.getParameter("dialog");
    oDialog.getContent()[0].setMode("SelectAll");
});
```

### End-User Capabilities

Users can personalize by:
- ✅ Saving filter bar and table settings as reusable views
- ✅ Adding app-specific links
- ✅ Adding, moving, and removing sections
- ✅ Arranging cards on overview pages
- ✅ Creating public views visible to other users

### Implementation Requirements

**Unique IDs Required**:
```xml
<!-- All controls must have unique IDs -->
<mvc:View id="mainView">
    <Table id="productsTable">
        <P13nDialog id="personalizationDialog"/>
    </Table>
</mvc:View>
```

**manifest.json Dependencies**:
```json
{
  "sap.ui5": {
    "dependencies": {
      "libs": {
        "sap.m": {},
        "sap.ui.comp": {}
      }
    }
  }
}
```

### Best Practices

- ✅ Include required libraries in manifest.json
- ✅ Use VariantManagement with table personalization
- ✅ Enable proper control configuration
- ✅ Ensure unique IDs for all controls
- ✅ Test with multiple variants
- ✅ Provide default/standard view
- ✅ Consider localStorage for client-side persistence
- ✅ Use BTP services for cross-device persistence

---

## Summary - Batch 4

**Topics Covered**: 10 specialized enterprise topics
- Accessibility & WCAG 2.2 compliance
- Security best practices (XSS, CSRF, CSP)
- SAP BAS & Fiori Tools development environment
- Deployment & CI/CD pipelines
- Custom Control development patterns
- Popovers & contextual UI
- DynamicPage header & advanced layouts
- Empty states & no data handling
- Search & filter patterns
- Personalization & user settings

**Key Takeaways**:
- **Accessibility**: WCAG 2.2 compliance built-in, keyboard navigation, screen reader support
- **Security**: Input validation, XSS prevention, CSRF protection, CSP
- **SAP BAS**: Cloud IDE with generators, modelers, editors, preview, deployment
- **Deployment**: MTA structure, SAP CI/CD service, GitHub Actions, Jenkins
- **Custom Controls**: Extend Control, metadata, renderer, lifecycle methods
- **Popovers**: ResponsivePopover for cross-device, modal mode for decisions
- **DynamicPage**: Title, header, content, expand/collapse, sticky behavior
- **Empty States**: IllustratedMessage, clear messaging, actionable guidance
- **Search/Filter**: Client-side vs server-side, FilterOperators, sorting/grouping
- **Personalization**: SmartTable, VariantManagement, P13n Engine, user preferences

**Developer Impact**: Enterprise-grade patterns for production-ready applications

**Combined Coverage (Batches 1+2+3+4)**: ~95% of SAPUI5 enterprise development patterns