# SAPUI5 Developer Reference

**Purpose**: Comprehensive reference for SAPUI5 advanced controls and patterns  
**Version**: 1.0  
**Last Updated**: January 24, 2026  
**Source**: Scraped from SAPUI5 SDK via Perplexity MCP

---

## 📚 Table of Contents

1. [FlexibleColumnLayout](#flexiblecolumnlayout)
2. [DynamicPage](#dynamicpage)
3. [Data Binding](#data-binding)
4. [Routing and Navigation](#routing-and-navigation)
5. [Best Practices](#best-practices)

---

## FlexibleColumnLayout

### Overview

**`sap.f.FlexibleColumnLayout`** implements a responsive **master-detail-detail paradigm**, displaying up to three pages in separate columns (begin, mid, end) with adaptive layouts based on screen size and navigation.

**Namespace**: `sap.f`  
**Available Since**: SAPUI5 1.46  
**Use Case**: Multi-panel applications, master-detail patterns

### Structure

```
┌──────────┬──────────┬──────────┐
│  Begin   │   Mid    │   End    │
│ (Master) │ (Detail) │ (Detail) │
│          │          │          │
│  List    │  Object  │  Sub-    │
│  View    │  Page    │  Detail  │
└──────────┴──────────┴──────────┘

Responsive:
Phone:    [One Column]
Tablet:   [Two Columns]
Desktop:  [Up to Three Columns]
```

### Column Structure

**Three Columns**:
1. **Begin (Master)**: Leftmost column for lists or navigation
2. **Mid (Detail)**: Center for primary content
3. **End (Detail-Detail)**: Rightmost for sub-details

**Responsive Behavior**:
- **Small screens**: Collapses to one column
- **Medium screens**: Two columns
- **Large screens**: Three columns
- Automatic adaptation based on container width

### Key Properties

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `layout` | string | Determines visible columns and sizes | "OneColumn" |
| `backgroundDesign` | string | Column background style | "Solid" |
| `defaultTransitionNamePrefix` | string | Prefix for page transitions | "" |
| `animation` | boolean | Enable/disable animations | true |
| `preservePageInHistory` | boolean | Keep pages in browser history | false |

### Aggregations

| Aggregation | Type | Description |
|-------------|------|-------------|
| `beginColumnPages` | sap.ui.core.Control[] | Pages in begin column |
| `midColumnPages` | sap.ui.core.Control[] | Pages in mid column |
| `endColumnPages` | sap.ui.core.Control[] | Pages in end column |

### Layout Types

The `layout` property controls column visibility and widths:

| Layout | Description | Columns Visible | Use Case |
|--------|-------------|-----------------|----------|
| `OneColumn` | Full screen single page | One active (begin/mid/end) | Initial list view |
| `TwoColumnsBeginExpanded` | Master wide, detail narrow | Begin (wide), Mid | List + detail |
| `TwoColumnsMidExpanded` | Detail wide, master narrow | Begin, Mid (wide) | Focus on detail |
| `ThreeColumnsMidExpanded` | All three, mid wide | Begin, Mid (wide), End | Balanced view |
| `ThreeColumnsEndExpanded` | All three, end wide | Begin, Mid, End (wide) | Focus on sub-detail |
| `MidColumnFullScreen` | Mid column only | Mid (full width) | Detail focus |
| `EndColumnFullScreen` | End column only | End (full width) | Sub-detail focus |

**Additional layouts**: See SAPUI5 API documentation for complete list and exact width percentages.

### Navigation Patterns

**Semantic Navigation Helper**:

```javascript
// Use sap.f.FlexibleColumnLayoutSemanticHelper
var oFCL = this.byId("fcl");
var oHelper = sap.f.FlexibleColumnLayoutSemanticHelper.getInstance(oFCL);

// Navigate semantically
oHelper.to("detailPageId");  // Shifts focus to mid column
```

**Manual Navigation**:
```javascript
// Change layout property
oFCL.setLayout(sap.f.LayoutType.TwoColumnsBeginExpanded);

// Add/remove pages from aggregations
oFCL.addMidColumnPage(oDetailPage);
```

**Recommended**: Use semantic helper for UX best practices (handles state transitions, back navigation automatically).

### Responsive Behavior

**Automatic Adaptation**:
- Phone (< 600px): One column
- Tablet (600-1024px): Two columns
- Desktop (> 1024px): Up to three columns

**User Controls**:
- Expand/collapse via header buttons
- Resize columns via gestures
- Full-screen mode for columns

### Code Examples

#### Basic FlexibleColumnLayout (XML)

```xml
<mvc:View xmlns:mvc="sap.ui.core.mvc" 
          xmlns="sap.m" 
          xmlns:f="sap.f">
    
    <f:FlexibleColumnLayout id="fcl" 
                            layout="TwoColumnsBeginExpanded">
        
        <!-- Begin Column (Master) -->
        <f:beginColumnPages>
            <Page title="Customers">
                <List items="{/customers}">
                    <StandardListItem 
                        title="{name}" 
                        description="{city}"
                        type="Navigation"
                        press="onCustomerPress"/>
                </List>
            </Page>
        </f:beginColumnPages>
        
        <!-- Mid Column (Detail) -->
        <f:midColumnPages>
            <Page title="Customer Details">
                <ObjectPageLayout/>
            </Page>
        </f:midColumnPages>
        
        <!-- End Column (Sub-Detail) -->
        <f:endColumnPages>
            <Page title="Order Details"/>
        </f:endColumnPages>
        
    </f:FlexibleColumnLayout>
    
</mvc:View>
```

#### JavaScript Controller Navigation

```javascript
// Controller
sap.ui.define([
    "sap/ui/core/mvc/Controller",
    "sap/f/FlexibleColumnLayoutSemanticHelper"
], function(Controller, FlexibleColumnLayoutSemanticHelper) {
    "use strict";
    
    return Controller.extend("app.controller.Main", {
        
        onCustomerPress: function(oEvent) {
            var oFCL = this.byId("fcl");
            var oHelper = FlexibleColumnLayoutSemanticHelper.getInstance(oFCL);
            
            // Navigate to mid column
            var sLayout = oHelper.getNextUIState(2).layout;
            oFCL.setLayout(sLayout);
            
            // Or use semantic method
            oHelper.to("detailPageId");
        },
        
        onBack: function() {
            var oFCL = this.byId("fcl");
            var oHelper = FlexibleColumnLayoutSemanticHelper.getInstance(oFCL);
            
            // Navigate back semantically
            var sLayout = oHelper.getPreviousUIState().layout;
            oFCL.setLayout(sLayout);
        }
        
    });
});
```

### Best Practices

1. **Use Semantic Helper**:
   - ✅ Handles recommended UX patterns
   - ✅ Manages state transitions
   - ✅ Back navigation automatic
   - ❌ Don't manually manage layouts unless needed

2. **Responsive Design**:
   - ✅ Test on all device sizes
   - ✅ Don't over-nest layouts
   - ✅ Use appropriate content for each column
   - ❌ Avoid complex layouts on mobile

3. **Navigation**:
   - ✅ Master → Detail → Sub-Detail flow
   - ✅ Breadcrumbs for orientation
   - ✅ Back button always visible
   - ❌ Don't skip navigation levels

4. **Performance**:
   - ✅ Lazy load column content
   - ✅ Use `initialLoad` for pages
   - ✅ Limit pages per aggregation
   - ❌ Don't load all pages upfront

5. **Accessibility**:
   - ✅ Label columns with ARIA
   - ✅ Keyboard navigation support
   - ✅ Screen reader announcements
   - ❌ Don't hide essential controls

### Use Cases

**Master-Detail Applications**:
- Email client (inbox → message → attachment)
- Customer management (list → details → orders)
- Document browser (folders → files → preview)
- Product catalog (categories → products → specifications)

**When to Use**:
- ✅ Multi-level navigation needed
- ✅ Related content to display simultaneously
- ✅ Desktop-focused application
- ✅ Complex data relationships

**When NOT to Use**:
- ❌ Simple single-page apps
- ❌ Mobile-only applications
- ❌ No hierarchical data
- ❌ Use `sap.m.SplitApp` for simpler cases

### Integration with Fiori Floorplans

**Combine with**:
- Begin column: List Report
- Mid column: Object Page
- End column: Related Object Page or details

---

## DynamicPage

### Overview

**`sap.f.DynamicPage`** is a core SAPUI5 layout control providing a **responsive page structure** with:
- Dynamic header (title + optional content)
- Main scrollable content area
- Optional footer toolbar
- Built-in expand/collapse, snap, pin behaviors

**Foundation** for all SAP Fiori pages.

**Namespace**: `sap.f`  
**Available Since**: SAPUI5 1.42

### Structure

```
┌─────────────────────────────────────────┐
│      Dynamic Page Title (headerTitle)   │
│  • Title, Subtitle                      │
│  • Actions (right-aligned)              │
│  • Snapped content (visible when snap)  │
│  • Expanded content (hidden when snap)  │
│  • Expand/Collapse arrow                │
├─────────────────────────────────────────┤
│   Header Content (headerContent)        │
│  • Expandable area                      │
│  • Inputs, variants, filters, KPIs      │
│  • Hidden when collapsed/snapped        │
├─────────────────────────────────────────┤
│          Main Content (content)         │
│  • Scrollable area                      │
│  • Forms, tables, charts, etc.          │
│  • Independent scrolling                │
│                                         │
│  [Content scrolls under header]         │
│                                         │
├─────────────────────────────────────────┤
│    Footer Toolbar (footer) - Optional   │
│  • Save, Cancel, Messages               │
│  • Floating above content               │
└─────────────────────────────────────────┘
```

### Key Components

#### 1. Header Title (Mandatory)

**`sap.f.DynamicPageTitle`**:

```javascript
new sap.f.DynamicPageTitle({
    heading: [new sap.m.Title({text: "Order #12345"})],
    snappedHeading: [new sap.m.Title({text: "Order #12345"})],
    expandedHeading: [new sap.m.Title({text: "Sales Order #12345"})],
    actions: [
        new sap.m.Button({text: "Edit", icon: "sap-icon://edit"}),
        new sap.m.Button({text: "Delete", icon: "sap-icon://delete"})
    ],
    snappedContent: [
        new sap.m.Label({text: "Status: Approved"})
    ],
    expandedContent: [
        new sap.m.HBox({
            items: [
                new sap.m.ObjectAttribute({title: "Customer", text: "ABC Corp"}),
                new sap.m.ObjectAttribute({title: "Amount", text: "$10,000"})
            ]
        })
    ]
})
```

**Components**:
- `heading`: Always visible title
- `snappedHeading`: Title when snapped (optional, uses heading if not set)
- `expandedHeading`: Title when expanded (optional)
- `actions`: Right-aligned action buttons
- `snappedContent`: Content visible when header snapped
- `expandedContent`: Content visible when header expanded

#### 2. Header Content (Optional)

**Expandable area** below title:
```javascript
headerContent: [
    new sap.m.Panel({
        headerText: "Filters",
        content: [
            new sap.m.Input({placeholder: "Search..."}),
            new sap.m.Select({items: [...]})
        ]
    })
]
```

**Purpose**: Filters, variants, KPIs, secondary information

**Behavior**: Hidden when header collapsed/snapped

#### 3. Content (Mandatory)

**Main scrollable area**:
```javascript
content: [
    new sap.m.VBox({
        items: [
            new sap.m.Panel({...}),
            new sap.m.Table({...}),
            new sap.m.Form({...})
        ]
    })
]
```

**Can contain**: Any UI5 controls, forms, tables, charts

#### 4. Footer (Optional)

**Floating toolbar**:
```javascript
footer: new sap.m.OverflowToolbar({
    content: [
        new sap.m.ToolbarSpacer(),
        new sap.m.Button({text: "Save", type: "Emphasized"}),
        new sap.m.Button({text: "Cancel"})
    ]
})
```

**Use**: Edit mode actions, finalizing operations

### Key Properties

| Property | Type | Description | Default |
|----------|------|-------------|---------|
| `title` | string | Page title | "" |
| `headerTitle` | sap.f.DynamicPageTitle | **Mandatory** title area | null |
| `headerContent` | sap.ui.core.Control[] | Expandable header content | [] |
| `content` | sap.ui.core.Control[] | Main content | [] |
| `footer` | sap.ui.core.IBar | Footer toolbar | null |
| `headerExpanded` | boolean | Initial expanded state | true |
| `toggleHeaderOnTitleClick` | boolean | Enable snap on title click | true |
| `preserveHeaderStateOnScroll` | boolean | Keep state during scroll | false |
| `showFooter` | boolean | Show/hide footer | false |
| `fitContent` | boolean | Fit content to container | false |

### Behaviors

#### 1. Snapped/Expanded/Collapsed

**Snapped**:
- Header collapses on scroll (default: ~20% scroll)
- Hides `headerContent`
- Shows `snappedContent` in title
- Prioritizes main content visibility

**Expanded**:
- Full header visible
- Shows `expandedContent` in title
- Shows `headerContent` area
- More context for user

**How to Control**:
- **Scroll**: Automatically snaps (default behavior)
- **Title Click**: Click title area to toggle
- **Arrow Icon**: Click expand/collapse arrow
- **Programmatic**: `oPage.setHeaderExpanded(false);`

#### 2. Pin/Unpin

**Pin Header**:
- Keeps header visible while scrolling
- User control via pin icon
- Combines with snap for optimal UX
- Default: Enabled

**Benefits**:
- Quick access to header actions
- Header info always visible
- User preference

#### 3. Scroll Behavior

**Default**:
- Content scrolls under header
- Header snaps at scroll threshold
- Smooth transitions
- Automatic on desktop

**FitContainer Mode**:
```javascript
fitContent: true  // For constrained layouts
```

**Use**: When page is within another scrollable container

### Responsive Features

| Screen Size | Behavior |
|-------------|----------|
| **Desktop** | Full header, all interactions enabled |
| **Tablet** | Adapted header, touch-friendly |
| **Mobile** | Simplified header, essential actions only |

**Interactions** (All active by default):
1. ✅ Snap on scroll
2. ✅ Snap on title click
3. ✅ Pin/unpin header

### Code Examples

#### Basic DynamicPage (XML)

```xml
<mvc:View xmlns:mvc="sap.ui.core.mvc" 
          xmlns="sap.m" 
          xmlns:f="sap.f">
    
    <f:DynamicPage title="My Page" 
                   headerExpanded="true" 
                   toggleHeaderOnTitleClick="true">
        
        <!-- Header Title -->
        <f:headerTitle>
            <f:DynamicPageTitle>
                <f:heading>
                    <Title text="Sales Order #12345"/>
                </f:heading>
                <f:actions>
                    <Button text="Edit" icon="sap-icon://edit"/>
                    <Button text="Delete" icon="sap-icon://delete"/>
                </f:actions>
                <f:snappedContent>
                    <Label text="Status: Approved"/>
                </f:snappedContent>
                <f:expandedContent>
                    <HBox>
                        <ObjectAttribute title="Customer" text="ABC Corp"/>
                        <ObjectAttribute title="Amount" text="$10,000"/>
                    </HBox>
                </f:expandedContent>
            </f:DynamicPageTitle>
        </f:headerTitle>
        
        <!-- Header Content (Expandable) -->
        <f:headerContent>
            <Panel headerText="Order Details">
                <VBox>
                    <Label text="Date: 2026-01-24"/>
                    <Label text="Status: Processing"/>
                </VBox>
            </Panel>
        </f:headerContent>
        
        <!-- Main Content -->
        <f:content>
            <ScrollContainer height="100%">
                <VBox class="sapUiSmallMargin">
                    <Panel headerText="Items">
                        <Table items="{/items}">
                            <!-- Table columns -->
                        </Table>
                    </Panel>
                </VBox>
            </ScrollContainer>
        </f:content>
        
        <!-- Footer -->
        <f:footer>
            <OverflowToolbar>
                <ToolbarSpacer/>
                <Button text="Save" type="Emphasized"/>
                <Button text="Cancel"/>
            </OverflowToolbar>
        </f:footer>
        
    </f:DynamicPage>
    
</mvc:View>
```

#### Pure JavaScript Example

```javascript
// Create DynamicPage in JavaScript
var oDynamicPage = new sap.f.DynamicPage({
    title: "My Page",
    headerExpanded: true,
    toggleHeaderOnTitleClick: true,
    
    headerTitle: new sap.f.DynamicPageTitle({
        heading: [new sap.m.Title({text: "Order #12345"})],
        actions: [
            new sap.m.Button({
                text: "Edit",
                icon: "sap-icon://edit",
                press: function() { console.log("Edit clicked"); }
            })
        ],
        snappedContent: [
            new sap.m.Label({text: "Status: Approved"})
        ],
        expandedContent: [
            new sap.m.HBox({
                items: [
                    new sap.m.ObjectAttribute({
                        title: "Customer",
                        text: "ABC Corp"
                    })
                ]
            })
        ]
    }),
    
    headerContent: [
        new sap.m.Panel({
            headerText: "Details",
            content: [
                new sap.m.Text({text: "Order information"})
            ]
        })
    ],
    
    content: [
        new sap.m.ScrollContainer({
            height: "100%",
            content: [
                new sap.m.Text({text: "Main content here"})
            ]
        })
    ],
    
    footer: new sap.m.OverflowToolbar({
        content: [
            new sap.m.ToolbarSpacer(),
            new sap.m.Button({text: "Save", type: "Emphasized"}),
            new sap.m.Button({text: "Cancel"})
        ]
    })
});

oDynamicPage.placeAt("content");
```

### When to Use

✅ **Use DynamicPage when**:
- Building freestyle Fiori apps
- Need collapsible header with actions
- Object Page-like layout
- Simple to moderately complex pages
- Custom page layouts

✅ **Prefer `sap.f.SemanticPage`** when:
- Structured content with semantic areas
- Standard Fiori page patterns
- Reduces development effort

❌ **Don't Use when**:
- Fiori Elements floorplans (embed it automatically)
- Small content better in dialogs
- Simple page without header interactions

### Best Practices

1. **Always Include HeaderTitle**:
   - Mandatory for dynamic behavior
   - Omit `headerContent` if empty (disables interactions)

2. **Header Content**:
   - Position key info (KPIs, status) in title
   - Use `headerContent` for secondary info
   - Don't overcrowd header

3. **Actions**:
   - Place primary actions in title
   - Use footer for finalizing (Save/Cancel)
   - Hide unavailable actions

4. **Scrolling**:
   - Test scroll threshold
   - Adjust for content height
   - Consider mobile scroll behavior

5. **Combinations**:
   - Pair with FlexibleColumnLayout for multi-panel
   - Use with `sap.uxap.ObjectPageLayout` for complex objects
   - Consider `sap.m.SplitApp` for simpler master-detail

### Demos and Samples

**SAPUI5 Demo Kit**:
- Dynamic Page Freestyle Example
- Dynamic Page with Analytical Table
- Dynamic Page with Sticky Subheader
- Dynamic Page with Wizard

**Access**: https://sapui5.hana.ondemand.com → Samples → sap.f.DynamicPage

---

## Data Binding

### Overview

**SAPUI5 data binding** connects UI controls to data models (like **JSONModel**) for automatic updates, supporting multiple binding types.

### Binding Types

| Type | Purpose | Syntax Example |
|------|---------|----------------|
| **Property Binding** | Single value | `{/firstName}` |
| **Aggregation Binding** | Collections | `items="{/items}"` |
| **Element Binding** | Context/object | Relative paths |
| **Expression Binding** | Computed values | `{= ${a} > ${b}}` |
| **Two-Way Binding** | Editable fields | `<Input value="{/name}"/>` |

### JSONModel Setup

**Creating and Assigning Model**:

```javascript
// Create JSONModel with data
var oModel = new sap.ui.model.json.JSONModel({
    firstName: "John",
    lastName: "Doe",
    company: {
        name: "SAP",
        location: "Walldorf"
    },
    orders: [
        { id: 1, text: "Order 1", amount: 100 },
        { id: 2, text: "Order 2", amount: 200 }
    ]
});

// Assign to view (unnamed model)
this.getView().setModel(oModel);

// Or assign with name
this.getView().setModel(oModel, "app");
```

**Data Structure**: Client-side JSON, ideal for small datasets without server paging.

### Property Binding

**Binds control property to model path**:

**XML**:
```xml
<!-- Simple binding -->
<Input value="{/firstName}"/>

<!-- Nested path -->
<Input value="{/company/name}"/>

<!-- Named model -->
<Input value="{app>/firstName}"/>
```

**JavaScript**:
```javascript
// Bind property programmatically
oInput.bindProperty("value", "/firstName");

// Or set via constructor
var oInput = new sap.m.Input({
    value: "{/firstName}"
});
```

**Paths**:
- `/firstName` - Root level property
- `/company/name` - Nested property
- `/orders/0/text` - Array item property

### Aggregation Binding

**Binds collections** (table rows, list items) using template:

**XML**:
```xml
<Table items="{/orders}">
    <columns>
        <Column><Text text="ID"/></Column>
        <Column><Text text="Text"/></Column>
    </columns>
    <items>
        <ColumnListItem>
            <cells>
                <Text text="{id}"/>
                <Text text="{text}"/>
            </cells>
        </ColumnListItem>
    </items>
</Table>
```

**JavaScript**:
```javascript
// Create template
var oTemplate = new sap.m.ColumnListItem({
    cells: [
        new sap.m.Text({text: "{id}"}),
        new sap.m.Text({text: "{text}"})
    ]
});

// Bind aggregation
oTable.bindAggregation("items", "/orders", oTemplate);

// Or via constructor
var oTable = new sap.m.Table({
    items: {
        path: "/orders",
        template: oTemplate
    }
});
```

### Element Binding

**Binds entire object context** to control/view:

```javascript
// Bind element to specific path
oForm.bindElement("/orders/0");

// Now relative paths work
// {id} → /orders/0/id
// {text} → /orders/0/text
```

**Use Case**: Detail pages, forms for single object

### Expression Binding

**Computed values** using `{= ... }` syntax:

**Operators**:
- Unary: `!` (NOT)
- Arithmetic: `+ - * / %`
- Comparison: `< > <= >= === !==`
- Logical: `&& ||`
- Conditional: `? :`

**Examples**:

```xml
<!-- Boolean logic -->
<Text text="{= ${createMode} === true ? 'Yes' : 'No'}"/>

<!-- Visibility control -->
<Button visible="{= !${editMode} || ${isAdmin}}"/>

<!-- Member access -->
<Text visible="{= ${/firstName}.length > 0}"/>

<!-- Arithmetic -->
<Text text="{= ${price} * ${quantity}}"/>

<!-- Complex -->
<Text text="{= ${total} > 1000 ? 'High' : ${total} > 500 ? 'Medium' : 'Low'}"/>
```

**Benefits**:
- No formatter function needed
- Evaluated automatically
- Faster than custom functions
- Cleaner code

### Formatter Functions

**Custom value formatting**:

**Define Formatter**:
```javascript
// In controller or global scope
jQuery.sap.declare("my.app.formatter");
my.app.formatter = {
    toUpperCase: function(value) {
        return value ? value.toUpperCase() : "";
    },
    
    formatCurrency: function(amount) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(amount);
    },
    
    formatDate: function(date) {
        return new Date(date).toLocaleDateString();
    }
};
```

**Use in Binding**:

**XML**:
```xml
<Input value="{
    path: '/firstName',
    formatter: 'my.app.formatter.toUpperCase'
}"/>

<Text text="{
    path: '/amount',
    formatter: '.formatCurrency'
}"/>
```

**JavaScript**:
```javascript
var oText = new sap.m.Text({
    text: {
        path: "/amount",
        formatter: function(value) {
            return "$" + value.toFixed(2);
        }
    }
});
```

### Two-Way Binding

**Updates model when control changes**:

```javascript
// Set binding mode
oModel.setDefaultBindingMode(sap.ui.model.BindingMode.TwoWay);

// Input automatically updates model
<Input value="{/firstName}"/>  <!-- User types → model updates -->
```

**Modes**:
- `TwoWay`: Control ↔ Model (default for inputs)
- `OneWay`: Model → Control (display-only)
- `OneTime`: Single read from model

**Control Explicitly**:
```xml
<Input value="{
    path: '/firstName',
    mode: 'TwoWay'
}"/>

<Text text="{
    path: '/firstName',
    mode: 'OneWay'
}"/>
```

### Relative Binding

**Using Named Models**:

```javascript
// Named model
this.getView().setModel(oModel, "app");
this.getView().setModel(i18nModel, "i18n");

// Bind with name
<Input value="{app>/firstName}"/>
<Text text="{i18n>/title}"/>
```

**Relative Paths** (within element binding):
```javascript
// After bindElement("/orders/0")
<Text text="{id}"/>        // Relative to /orders/0/id
<Text text="{text}"/>      // Relative to /orders/0/text
```

### Data Binding Best Practices

1. **Name Models for Clarity**:
   ```javascript
   this.getView().setModel(oDataModel, "app");
   this.getView().setModel(i18nModel, "i18n");
   ```

2. **Use Types for Validation**:
   ```xml
   <Input value="{
       path: '/email',
       type: 'sap.ui.model.type.String',
       constraints: {
           email: true
       }
   }"/>
   ```

3. **Prefer Expression Binding** for simple logic:
   ```xml
   <!-- Faster than formatter -->
   <Text text="{= ${amount} * 1.2}"/>
   ```

4. **Set Binding Mode** explicitly for performance:
   ```javascript
   // OneWay for display-only
   oModel.setDefaultBindingMode(sap.ui.model.BindingMode.OneWay);
   ```

5. **Handle Hierarchies**:
   ```javascript
   /products/0/name          // Array item
   /company/address/city     // Nested object
   ```

6. **Test with UI5 Walkthrough**: 15-step tutorial covering models, bindings, i18n, validation

### Binding Patterns Summary

```javascript
// Property binding
{/path/to/property}

// Aggregation binding
items="{/arrayPath}"

// Element binding
bindElement("/objectPath")

// Expression binding
{= expression with ${paths}}

// Formatter
{path: '/prop', formatter: 'func'}

// Two-way
{path: '/prop', mode: 'TwoWay'}

// Named model
{modelName>/path}
```

---

## Routing and Navigation

### Overview

**SAPUI5 routing** controls application state efficiently by mapping **URL patterns** to views and managing navigation through a centralized router configured in `manifest.json`.

### Core Architecture

**Three-Layer System**:

1. **Routes**: Define URL patterns
2. **Targets**: Specify which views to display
3. **Router**: Orchestrates navigation

**Flow**:
```
navTo("detail") → Router matches route 
               → Triggers target 
               → Loads view
```

### Manifest.json Configuration

**Location**: `manifest.json` → `"sap.ui5"` → `"routing"`

**Structure**:
```json
{
  "sap.ui5": {
    "routing": {
      "config": {
        "routerClass": "sap.m.routing.Router",
        "viewType": "XML",
        "viewPath": "app.view",
        "controlId": "app",
        "controlAggregation": "pages",
        "transition": "slide"
      },
      "routes": [
        {
          "name": "overview",
          "pattern": "",
          "target": "overview"
        },
        {
          "name": "detail",
          "pattern": "detail/{id}",
          "target": "detail"
        }
      ],
      "targets": {
        "overview": {
          "viewName": "Overview",
          "viewLevel": 1
        },
        "detail": {
          "viewName": "Detail",
          "viewLevel": 2
        }
      }
    }
  }
}
```

### Routes Array

**Each route defines**:

| Property | Required | Description | Example |
|----------|----------|-------------|---------|
| `name` | ✅ Yes | Route identifier | "detail" |
| `pattern` | ✅ Yes | URL pattern | "detail/{id}" |
| `target` | ✅ Yes | Target to load | "detail" |

**Pattern Syntax**:
```javascript
""                    // Empty (default/home)
"products"            // Fixed path
"products/{id}"       // Parameter
"products/{id}/edit"  // Multiple segments
"products/{id:int}"   // Typed parameter
"products/{id}/:tab:" // Optional parameter
"*catchAll"          // Catch-all for 404
```

### Targets Object

**Each target specifies**:

| Property | Required | Description |
|----------|----------|-------------|
| `viewName` | ✅ Yes | View file name |
| `viewPath` | No | Override default path |
| `viewType` | No | XML, JS, JSON, HTML |
| `viewLevel` | No | For transitions (1, 2, 3...) |
| `transition` | No | slide, show, flip |
| `controlId` | No | Container control |
| `controlAggregation` | No | Target aggregation |

### Navigation Methods

#### navTo() - Primary Navigation

**In Controller**:
```javascript
// Get router from component
var oRouter = this.getOwnerComponent().getRouter();

// Navigate to route
oRouter.navTo("detail", {
    id: "12345"  // Parameters
});

// With query parameters
oRouter.navTo("detail", {
    id: "12345"
}, {
    tab: "orders"  // Query params
});
```

**URL Result**:
```
#/detail/12345
#/detail/12345?tab=orders
```

#### navBack() - Backward Navigation

```javascript
// Navigate back
oRouter.navBack();

// Or use browser history
window.history.go(-1);
```

### Parameters and Query

**Route Parameters** (mandatory):
```json
{
  "pattern": "product/{productId}/order/{orderId}"
}
```

**Access in Controller**:
```javascript
onInit: function() {
    var oRouter = this.getOwnerComponent().getRouter();
    oRouter.getRoute("productOrder").attachPatternMatched(this._onRouteMatched, this);
},

_onRouteMatched: function(oEvent) {
    var oArgs = oEvent.getParameter("arguments");
    var sProductId = oArgs.productId;
    var sOrderId = oArgs.orderId;
    
    // Load data
    this._loadProduct(sProductId, sOrderId);
}
```

**Query Parameters** (optional):
```javascript
// Set query
oRouter.navTo("detail", {id: "123"}, {tab: "info"});

// Access query
var oArgs = oEvent.getParameter("arguments");
var sTab = oArgs["?query"].tab;
```

### Deep Linking

**Enable bookmarkable URLs**:

```
https://myapp.com/#/product/12345
https://myapp.com/#/customer/abc123/orders
```

**Benefits**:
- Users can bookmark specific pages
- Share links to exact application state
- Browser back/forward buttons work
- SEO-friendly (for public apps)

### Hash Navigation

**Hash Structure**:
```
#/route/param1/param2?query=value
```

**Examples**:
```
#/                        // Home/overview
#/customers               // Customer list
#/customers/123           // Customer detail
#/customers/123?tab=orders // Customer with tab
```

### Handling Invalid Routes

**Bypassed Event** (route not found):

```javascript
// In Component.js
init: function() {
    // Initialize router
    this.getRouter().initialize();
    
    // Handle bypassed routes
    this.getRouter().attachBypassed(function(oEvent) {
        var sHash = oEvent.getParameter("hash");
        console.log("Route not found:", sHash);
        
        // Navigate to "not found" page
        this.getRouter().getTargets().display("notFound");
    }, this);
}
```

**Not Found Page**:
```json
{
  "targets": {
    "notFound": {
      "viewName": "NotFound",
      "transition": "show"
    }
  }
}
```

### Router Initialization

**In Component.js** (mandatory):

```javascript
sap.ui.define([
    "sap/ui/core/UIComponent"
], function(UIComponent) {
    "use strict";
    
    return UIComponent.extend("app.Component", {
        
        metadata: {
            manifest: "json"
        },
        
        init: function() {
            // Call parent init
            UIComponent.prototype.init.apply(this, arguments);
            
            // Initialize router
            this.getRouter().initialize();
        }
    });
});
```

**Why in Component.js**:
- Centralized initialization
- Available to all controllers
- Single router instance
- Better state management

### Event Handling and Navigation

**List to Detail Example**:

**ListView Controller**:
```javascript
onItemPress: function(oEvent) {
    // Get selected item
    var oItem = oEvent.getSource();
    var oContext = oItem.getBindingContext();
    var sPath = oContext.getPath();  // e.g., "/customers/5"
    var oObject = oContext.getObject();
    
    // Navigate to detail
    var oRouter = this.getOwnerComponent().getRouter();
    oRouter.navTo("detail", {
        id: oObject.id
    });
}
```

**DetailView Controller**:
```javascript
onInit: function() {
    var oRouter = this.getOwnerComponent().getRouter();
    oRouter.getRoute("detail").attachPatternMatched(this._onRouteMatched, this);
},

_onRouteMatched: function(oEvent) {
    var oArgs = oEvent.getParameter("arguments");
    var sId = oArgs.id;
    
    // Bind view to selected item
    var sPath = "/customers/" + sId;
    this.getView().bindElement({
        path: sPath
    });
}
```

### Best Practices

1. **Initialize in Component.js**:
   - ✅ Centralized router management
   - ✅ Available to all controllers
   - ❌ Don't initialize in individual controllers

2. **Use Separate Views**:
   - ✅ One view per route target
   - ✅ App shell view as wrapper
   - ✅ Lazy loading benefits

3. **Deep Linking**:
   - ✅ Always support bookmarkable URLs
   - ✅ Use meaningful patterns
   - ✅ Test back/forward navigation

4. **Error Handling**:
   - ✅ Handle bypassed routes
   - ✅ Display "Not Found" page
   - ✅ Log navigation errors

5. **Parameters**:
   - ✅ Use route parameters for required data
   - ✅ Use query parameters for optional state
   - ✅ Validate parameters in controller

6. **State Management**:
   - ✅ Router controls application state
   - ✅ Avoid storing state in controllers
   - ✅ Use URL as single source of truth

### Complete Navigation Example

**Manifest.json**:
```json
{
  "routing": {
    "config": {
      "routerClass": "sap.m.routing.Router",
      "viewType": "XML",
      "viewPath": "app.view",
      "controlId": "app",
      "controlAggregation": "pages"
    },
    "routes": [
      {
        "name": "home",
        "pattern": "",
        "target": "home"
      },
      {
        "name": "customerDetail",
        "pattern": "customers/{customerId}",
        "target": "customerDetail"
      },
      {
        "name": "orderDetail",
        "pattern": "customers/{customerId}/orders/{orderId}",
        "target": "orderDetail"
      }
    ],
    "targets": {
      "home": {
        "viewName": "Home",
        "viewLevel": 1
      },
      "customerDetail": {
        "viewName": "CustomerDetail",
        "viewLevel": 2
      },
      "orderDetail": {
        "viewName": "OrderDetail",
        "viewLevel": 3
      }
    }
  }
}
```

**Home Controller**:
```javascript
onCustomerPress: function(oEvent) {
    var oCustomer = oEvent.getSource().getBindingContext().getObject();
    this.getOwnerComponent().getRouter().navTo("customerDetail", {
        customerId: oCustomer.id
    });
}
```

**CustomerDetail Controller**:
```javascript
onInit: function() {
    this.getOwnerComponent().getRouter()
        .getRoute("customerDetail")
        .attachPatternMatched(this._onRouteMatched, this);
},

_onRouteMatched: function(oEvent) {
    var sCustomerId = oEvent.getParameter("arguments").customerId;
    this.getView().bindElement("/customers/" + sCustomerId);
},

onOrderPress: function(oEvent) {
    var oOrder = oEvent.getSource().getBindingContext().getObject();
    this.getOwnerComponent().getRouter().navTo("orderDetail", {
        customerId: this._customerId,
        orderId: oOrder.id
    });
}
```

### Routing Patterns Summary

```javascript
// Basic navigation
oRouter.navTo("routeName");

// With parameters
oRouter.navTo("detail", {id: "123"});

// With query
oRouter.navTo("detail", {id: "123"}, {tab: "info"});

// Back navigation
oRouter.navBack();

// Get current route
var oRoute = oRouter.getRoute("routeName");

// Attach route matched
oRoute.attachPatternMatched(handler, this);

// Get parameters
var oArgs = oEvent.getParameter("arguments");
var sId = oArgs.id;
var sTab = oArgs["?query"].tab;
```

---

## Best Practices

### General Development

1. **API-First Approach** ⭐:
   - Implement business logic as APIs
   - Zero UI dependencies
   - Testable in Node.js
   - Reusable across environments

2. **Pure JavaScript for UI5** ⭐:
   - Direct control instantiation
   - Easy debugging (console.log, breakpoints)
   - Avoid XML views unless required
   - Cleaner, more maintainable

3. **Follow Fiori Guidelines**:
   - Use standard controls only
   - SAP Horizon theme
   - Fiori spacing system
   - Responsive design patterns

### Control Selection

**When to Use What**:

| Need | Use Control | Alternative |
|------|-------------|-------------|
| Multi-panel | FlexibleColumnLayout | SplitApp (simpler) |
| Complex page | DynamicPage | SemanticPage (structured) |
| Simple page | sap.m.Page | - |
| Object details | ObjectPageLayout | DynamicPage + sections |
| List | sap.m.Table (growing) | sap.ui.table.Table (desktop) |

### Performance

1. **Lazy Loading**:
   ```javascript
   growing: true,
   growingThreshold: 20
   ```

2. **Efficient Binding**:
   ```javascript
   // OneWay for read-only
   oModel.setDefaultBindingMode(BindingMode.OneWay);
   ```

3. **Limit Page Loads**:
   - Load views on demand
   - Use router for navigation (automatic lazy load)
   - Avoid loading all pages upfront

### Testing

**Test Checklist**:
- [ ] All routes work
- [ ] Parameters pass correctly
- [ ] Deep links function
- [ ] Back navigation correct
- [ ] Responsive layouts adapt
- [ ] Touch interactions work
- [ ] Keyboard navigation
- [ ] Screen reader support

---

## Resources

### Official Documentation

- **SAPUI5 SDK**: https://sapui5.hana.ondemand.com/sdk/
- **SAP Fiori Design**: https://experience.sap.com/fiori-design-web/
- **Demo Kit**: https://sapui5.hana.ondemand.com

### Project Documentation

- **This Guide**: `docs/fiori/SAPUI5_DEVELOPER_REFERENCE.md`
- **Floorplans Guide**: `docs/fiori/FIORI_FLOORPLANS_COMPLETE_GUIDE.md`
- **API Quick Reference**: `docs/fiori/SAPUI5_API_QUICK_REFERENCE.md`
- **Fiori Design Report**: `docs/fiori/FIORI_DESIGN_SCRAPING_REPORT.md`
- **Developer Onboarding**: `docs/DEVELOPER_ONBOARDING_GUIDE.md`

### Learning Resources

- SAPUI5 Walkthrough (15 steps)
- Navigation and Routing Tutorial
- Data Binding Tutorial
- SAP Community blogs
- YouTube tutorials

---

## Summary

### Key Concepts

1. **FlexibleColumnLayout**: Master-detail-detail with responsive columns
2. **DynamicPage**: Foundation for Fiori pages with dynamic header
3. **Data Binding**: Automatic UI ↔ Model synchronization
4. **Routing**: URL-based navigation and deep linking

### Essential Patterns

```javascript
// FlexibleColumnLayout navigation
var oHelper = FlexibleColumnLayoutSemanticHelper.getInstance(oFCL);
oHelper.to("detailPage");

// DynamicPage with header
var oPage = new sap.f.DynamicPage({
    headerTitle: new sap.f.DynamicPageTitle({...}),
    headerContent: [...],
    content: [...]
});

// Data binding
var oModel = new sap.ui.model.json.JSONModel({data});
this.getView().setModel(oModel);
// {/path/to/property}

// Routing
oRouter.navTo("detail", {id: "123"});
```

### Next Steps

1. ✅ Read this reference completely
2. ✅ Review Fiori Floorplans Guide
3. ✅ Check project examples
4. ✅ Build prototype with these controls
5. ✅ Test responsive behavior

---

**Status**: ✅ Complete Reference - Production Ready

**Version**: 1.0

**Source**: Scraped from SAPUI5 SDK (January 24, 2026)

This reference provides comprehensive coverage of advanced SAPUI5 controls and patterns for building enterprise SAP Fiori applications.