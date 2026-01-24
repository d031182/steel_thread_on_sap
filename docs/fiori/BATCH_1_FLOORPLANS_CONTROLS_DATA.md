# Batch 1: Floorplans, Controls & Data Patterns

**Purpose**: Comprehensive guide for additional Fiori floorplans, SAPUI5 controls, and OData patterns  
**Version**: 1.0  
**Date**: January 24, 2026  
**Source**: Scraped from SAP official sources via Perplexity MCP  
**Part of**: Comprehensive SAP documentation project

---

## 📚 Table of Contents

1. [Overview Page Floorplan](#overview-page-floorplan)
2. [Wizard Floorplan](#wizard-floorplan)
3. [Analytical List Page](#analytical-list-page)
4. [sap.m.Table](#sapmtable)
5. [sap.m.List](#sapmlist)
6. [Forms (sap.ui.layout.form)](#forms)
7. [sap.ui.table.Table](#sapuitable)
8. [Fragments & Dialogs](#fragments--dialogs)
9. [OData V2](#odata-v2)
10. [OData V4](#odata-v4)

---

## Overview Page Floorplan

### Purpose
**Data-driven dashboard** aggregating key information via cards, providing quick previews, KPIs, and navigation to detailed apps on a single responsive page.

### Structure
```
┌─────────────────────────────────────┐
│  KPI Header (up to 4 numbers)       │
├─────────────────────────────────────┤
│  Preview Cards (high-priority)      │
│  • KPI Cards                        │
│  • Table Cards                      │
│  • Analytical Cards                 │
│  • List Cards                       │
├─────────────────────────────────────┤
│  Facets (bottom menu)               │
│  Links to full object lists         │
└─────────────────────────────────────┘
```

### Card Types
- **KPI Cards**: Metrics like "Overdue deliveries" with tap navigation
- **Table Cards**: Preview lists (max 3 rows fixed), responsive tables
- **Analytical Cards**: Charts (StackedColumn, etc.) with UI.Chart annotations
- **List Cards**: Quick-access objects requiring attention

### Key Features
- **Dynamic page layout**: Full-screen responsive
- **Flat or hierarchical navigation**: Prioritizes less frequent items
- **Filter bar**: Standard contextual filtering
- **Personalization**: Users rearrange cards, filter, pin
- **Role-tailored**: Customize per user (warehouse vs logistics)

### Creation (Fiori Elements)
1. SAP Business Application Studio → **Overview Page Application** template
2. Connect OData service
3. Define cards via annotations (UI.DataPoint for KPIs, UI.Chart)
4. Deploy to Fiori Launchpad

### When to Use
✅ Dashboard scenarios with multiple data sources  
✅ KPI monitoring across domains  
✅ Quick navigation to detailed apps  
❌ Single data source (use List Report)

---

## Wizard Floorplan

### Purpose
Guides users through **long or unfamiliar tasks** (3-8 steps minimum) by dividing into sequential sections, ending with read-only summary.

### Structure
```
┌─────────────────────────────────────┐
│  Dynamic Page Header (step-based)   │
│  No snapping, space-saving          │
├─────────────────────────────────────┤
│  Walkthrough Screen                 │
│  Displays one form section at time  │
│  Sequential progression             │
├─────────────────────────────────────┤
│  Summary Page (read-only)           │
│  All entered data for review        │
├─────────────────────────────────────┤
│  Footer Toolbar                     │
│  Navigation actions                 │
└─────────────────────────────────────┘
```

### Key Properties
- **Steps**: 3-8 steps recommended
- **Linear workflow**: Fixed sequence, prevents overload
- **Validation**: Per step before advancing
- **Review page**: Read-only overview before submission
- **Responsive**: Full-screen, modal (80%/70%), or flexible column (rightmost)

### Usage Scenarios
- Create scenarios: Employee onboarding, complex form entry
- Edit scenarios: Guided updates of complex objects
- Modal dialogs: Quick edits in compact scenarios
- Flexible column: Wizard in right column after list selection

### When to Use
✅ Complex tasks (questionnaires, multi-step creation)  
✅ Unfamiliar workflows needing guidance  
✅ 3-8 distinct steps  
❌ Simple tasks (use Object Page)  
❌ Listings (use List Report)

---

## Analytical List Page

### Purpose
**Analytics-first floorplan** combining charts, tables, and visual filters for data investigation and root cause analysis.

### Structure
```
┌─────────────────────────────────────┐
│  Header (Expandable/Collapsible)    │
│  • Visual Filter Bar (chart impact) │
│  • Smart Filter Bar (traditional)   │
│  • KPI Tags (global metrics)        │
├─────────────────────────────────────┤
│  Content Area (View Switch)         │
│  • Hybrid: Chart + Table            │
│  • Chart-only                       │
│  • Table-only                       │
│  With toolbars for each             │
└─────────────────────────────────────┘
```

### Key Components
- **Visual Filters**: Show data impact, quick assessment
- **Smart Filter Bar**: Precise control
- **Chart**: UI.Chart annotations (bar, dimensions, measures)
- **Table**: UI.LineItem annotations, responsive/analytical types
- **KPIs**: Reflect filter changes in title

### Creation (Fiori Elements)
1. Business Application Studio → **Analytic List Page** template
2. Select data source, entityset, table type
3. Guided development: Add columns (UI.LineItem), configure chart (UI.Chart)
4. Set PresentationVariant for chart/table/sorting

### ALP vs List Report

| Aspect | Analytical List Page | List Report |
|--------|---------------------|-------------|
| **Focus** | Analytics: charts + visual filters + KPIs | Transactional lists with basic filters |
| **Views** | Hybrid/chart/table with drill-down | Primarily responsive table |
| **Header** | Visual/smart filter bar + expandable | Smart filter bar only |
| **Use Case** | Data investigation, root cause | Worklist processing |

### When to Use
✅ Filter impact visualization needed  
✅ Chart/table switching  
✅ KPI monitoring  
✅ Drill-down capabilities  
❌ Simple list processing

---

## sap.m.Table

### Purpose
**Responsive table** for mobile/tablet with growing mode, selection, sticky headers.

### Key Properties
- **columns**: Aggregation of sap.m.Column (order must match items cells)
- **items**: Rows (e.g., ColumnListItem)
- **growing**: Lazy loading (`growing="true" growingThreshold="20"`)
- **mode / selectionMode**: None, SingleSelectMaster, MultiSelect
- **sticky**: Keep headers fixed (`sticky="ColumnHeaders"`)
- **responsiveBehavior**: Adapts to screen size
- **backgroundDesign**: Solid, Translucent, Transparent

### Best Practices
- Match **columns** order exactly with **items** cells
- Use **growing** for >100 rows (mobile limit: 100 rows/4 columns)
- XML views for declarative binding
- OData navigation: `{path: 'NavProperty'}`
- Dynamic binding: Create template, bind via `table.bindItems()`

### Example (XML)
```xml
<Table items="{/Skills}" growing="true" sticky="ColumnHeaders" selectionMode="MultiSelect">
  <columns>
    <Column><Text text="Name"/></Column>
    <Column><Text text="Rating"/></Column>
  </columns>
  <items>
    <ColumnListItem>
      <cells>
        <Text text="{Name}"/>
        <Text text="{Rating}"/>
      </cells>
    </ColumnListItem>
  </items>
</Table>
```

### When to Use
✅ Mobile/tablet scenarios  
✅ Responsive layouts  
✅ Growing lists (<100 items visible)  
❌ Desktop with large datasets (use sap.ui.table.Table)

---

## sap.m.List

### Purpose
Container for **StandardListItem**, **CustomListItem**, and other list items, optimized for mobile (100-item limit).

### Key Properties
- **items**: Array of list items
- **growing**: Lazy loading for large lists
- **growingThreshold**: Initial render count (default: 20)
- **growingScrollToLoad**: Auto-load on scroll
- **mode**: Selection mode (None, SingleSelectMaster, MultiSelect)
- **backgroundDesign**: Solid, Translucent, Transparent

### Item Types
- **StandardListItem**: Pre-built with title, description, icon, info, type (Navigation, Active, Detail)
- **CustomListItem**: Container for custom content

### Swipe Actions
```javascript
<List swipe="onSwipe">
  <items>
    <StandardListItem title="Item" press="onPress"/>
  </items>
</List>
```

### Navigation
```javascript
// In controller
onItemPress: function(oEvent) {
  var oItem = oEvent.getSource();
  var sId = oItem.getBindingContext().getProperty("id");
  this.getOwnerComponent().getRouter().navTo("detail", {id: sId});
}
```

### Best Practices
- Limit to **100 items** on mobile
- Use **growing** for more
- **StandardListItem** for consistency
- **CustomListItem** only for complex needs
- Bind with templates (`templateShareable: true`)

### When to Use
✅ Simple item lists  
✅ Mobile/tablet scenarios  
✅ Navigation lists  
❌ Tabular data (use sap.m.Table)

---

## Forms

### sap.ui.layout.form.Form
**Flexible control** arranging labels and fields into groups and rows with responsive layouts.

**Components**:
- **FormContainer**: Groups FormElements
- **FormElement**: Pairs label with fields
- **Layouts**: ResponsiveLayout, GridLayout, SimpleFormLayout

### sap.ui.layout.form.SimpleForm
**Simpler API** stacking titles, labels, and fields in `content` aggregation.

**Content Order**:
1. `sap.ui.core.Title` (section titles)
2. `sap.m.Label` (field labels)
3. Input controls (sap.m.Input, DatePicker, etc.)

### Responsive Columns

**Fiori Elements Default**:
- S (Phone): 1 column
- M (Tablet): 3 columns
- L (Desktop): 4 columns
- XL (Wide): 6 columns

**Earlier Apps**:
- S: 1, M: 2, L: 3, XL: 4

### Example (SimpleForm)
```javascript
new sap.ui.layout.form.SimpleForm({
  content: [
    new sap.ui.core.Title({text: "Personal Info"}),
    new sap.m.Label({text: "Name"}),
    new sap.m.Input({placeholder: "Enter name"}),
    new sap.m.Label({text: "Email"}),
    new sap.m.Input({placeholder: "Enter email"}),
    new sap.ui.core.Title({text: "Address"}),
    new sap.m.Label({text: "City"}),
    new sap.m.Input({placeholder: "Enter city"})
  ]
});
```

### Best Practices
- **SimpleForm** for quick, stacked forms
- **Form** for complex grouping and responsiveness
- Load libraries: `sap.ui.layout`, `sap.m`
- Test responsive behavior
- Avoid mixing incompatible titles (use `sap.ui.core.Title` in SimpleForm)

---

## sap.ui.table.Table

### Purpose
**Desktop-optimized control** (GridTable) for large datasets with virtualization, sorting, filtering, multi-selection.

### Key Features
- **Columns**: `addColumn()`, `insertColumn()`, `getColumns()`
- **Rows**: Virtualization renders only visible rows
- **Selection**: Multi-selection (`selectionMode: "MultiToggle"`)
- **Sorting**: `getSortedColumns()`
- **Filtering**: Via `sap.ui.table.Column` filterProperty
- **Virtualization**: `threshold` for OData paging, `visibleRowCountMode`

### Related Controls
- **TreeTable**: Hierarchical data with TreeAutoExpandMode
- **AnalyticalTable**: Analytical OData with AnalyticalColumn

### Performance Best Practices
- Enable **row virtualization** (default, ~20-50 visible)
- Avoid fixed high `visibleRowCount` (>100)
- Bind to OData with `threshold` (e.g., 100)
- Limit **visible columns** (5-10 on tablets)
- Use `showOverlay` for loading states

### vs sap.m.Table

| Feature | sap.ui.table.Table | sap.m.Table |
|---------|-------------------|-------------|
| **Focus** | Desktop, large data | Mobile/tablet |
| **Virtualization** | Native | Manual (growing) |
| **Sorting/Filtering** | Built-in | Manual |
| **Selection** | Advanced multi | Basic |
| **Performance** | Optimized for 1000s | Limited to 100s |

### When to Use
✅ Desktop applications  
✅ Large datasets (1000s of rows)  
✅ Advanced sorting/filtering  
✅ Multi-selection requirements  
❌ Mobile-primary apps (use sap.m.Table)

---

## Fragments & Dialogs

### Purpose
**Fragments** are lightweight, reusable UI subtrees without controllers, ideal for dialogs, popovers, nested UI.

### Types
- **XML Fragments**: Declarative (most common)
- **JS Fragments**: Programmatic
- **HTML Fragments**: Raw HTML snippets

### XML Fragment Structure
```xml
<core:FragmentDefinition xmlns="sap.m" xmlns:core="sap.ui.core">
  <Dialog title="Hello fragments!">
    <Text text="Hi {textModel>/myName}!"/>
    <buttons>
      <Button text="OK" press="onClose"/>
    </buttons>
  </Dialog>
</core:FragmentDefinition>
```

### Lifecycle & Instantiation

**Load Methods**:
1. **Synchronous**: `sap.ui.xmlfragment(viewId, "namespace.view.FragmentName")`
2. **Async (Recommended)**: `Fragment.load({name: "namespace.view.FragmentName"})`

**Lifecycle Flow**:
1. Load/check existence (cache in controller)
2. Add as **dependent**: `oView.addDependent(oFragment)`
3. Insert into container: `oDialog.open()`
4. Destroy on close: `oFragment.destroy()`

### Caching Pattern
```javascript
_getFormFragment: function(sFragmentName) {
  if (!this._formFragments) this._formFragments = {};
  
  var oFormFragment = this._formFragments[sFragmentName];
  if (oFormFragment) return oFormFragment;
  
  oFormFragment = sap.ui.xmlfragment(
    this.getView().getId(), 
    "namespace.view." + sFragmentName
  );
  
  return this._formFragments[sFragmentName] = oFormFragment;
}
```

### Dialog Loading (Async)
```javascript
loadMyFragment: function() {
  const oView = this.getView();
  if (!this.oDialog) {
    this.oDialog = Fragment.load({
      name: "namespace.view.MyDialog"
    }).then(oDialog => {
      oView.addDependent(oDialog);
      return oDialog;
    });
  }
},

onOpen: function() {
  this.oDialog.then(oDialog => oDialog.open());
}
```

### Best Practices
- Cache instances in controller
- Use **Promise-based** `Fragment.load`
- Add as **view dependent** for lifecycle management
- Prefix IDs with view ID: `sap.ui.xmlfragment(view.getId(), ...)`
- Nest fragments for modularity
- Handle `open/close` events
- Keep reusable (no controller logic)

### Common Use Cases
- **Dialog**: Modal windows for user input
- **MessageBox**: Standard confirmation/alert dialogs
- **Popover**: Contextual information
- **Display/Edit swap**: Multiple fragments for different modes

---

## OData V2

### Purpose
**Server-side model** where data resides on server; client only knows visible (requested) data. Operations (sorting, filtering) performed on server.

### Model Setup
```javascript
var oModel = new ODataModel({
  serviceUrl: "http://services.odata.org/Northwind/Northwind.svc",
  serviceUrlParams: { myParam: "value1" },
  metadataUrlParams: { myParam: "value1" }
});
```

### CRUD Operations
- **Create**: Specify `groupId` (default: deferred "changes" group)
- **Read**: Automatic via binding or `oModel.read()`
- **Update**: Two-way binding or `oModel.update()`
- **Delete**: `oModel.remove("/EntityName(" + id + ")")`

### Batch Processing
```javascript
oModel.setDeferredGroups(["myGroupId"]);
oModel.setChangeGroups({
  "EntityTypeName": {
    groupId: "myGroupId",
    changeSetId: "ID",
    single: true
  }
});

oModel.submitChanges({
  groupId: "myGroupId",
  success: mySuccessHandler,
  error: myErrorHandler
});
```

### SmartTable with OData V2
```xml
<mvc:View xmlns:smart="sap.ui.comp.smarttable">
  <smart:SmartTable 
    id="smartTable" 
    entitySet="Products"
    enableAutoBinding="true">
  </smart:SmartTable>
</mvc:View>
```

### Server-Side Operations
- **Filtering**: Automatic when binding with `$filter`
- **Sorting**: Via `$orderby` parameter
- **Paging**: Server-side with threshold

### Best Practices
- Use batch requests for multiple operations
- Configure deferred groups for controlled submission
- Enable server-side filtering/sorting
- SmartTable for rapid development
- Handle errors with success/error callbacks

---

## OData V4

### Purpose
**Modern OData standard** with improved batching, two-way binding, server processing, and operation support.

### Model Setup
**Manifest.json**:
```json
"sap.ui5": {
  "models": {
    "": {
      "dataSource": "default",
      "settings": {
        "odataVersion": "4.0"
      }
    }
  }
}
```

**Programmatic**:
```javascript
new sap.ui.model.odata.v4.ODataModel({
  serviceUrl: "...",
  settings: { odataVersion: "4.0" }
});
```

### Binding
- **Two-way binding**: `{ path: '/EntitySet(ID)', mode: 'TwoWay' }`
- **List binding**: `<Table items="{/EntitySet}">`
- **Server-side ops**: `$filter`, `$orderby`, `$select`, `$expand`

### CRUD Operations
- **Create**: `oContext.createGroupInstance()` then `oModel.submitBatch(oGroupId)`
- **Read**: Direct binding to paths
- **Update**: Two-way binding auto-sends PATCH; use `submitBatch()` for grouping
- **Delete**: `oContext.delete("$direct").then(...)`

### Batch Requests
Multiple requests automatically **grouped into single HTTP batch**:
```javascript
oModel.createGroupInstance();
oModel.submitBatch(groupId);
```

### Actions & Functions
- **Bound**: `oContext.callAction(...)`
- **Unbound**: `oModel.bindAction('/actionName')`

### Metadata Levels
- **Minimal** (default): Load on demand for performance
- **Full**: Set `earlyRequests: true` for complete $metadata upfront

### Side Effects
Automatic handling via annotations like `SideEffects` in metadata; model issues dependent requests in batches.

### OData V4 vs V2

| Feature | V4 | V2 |
|---------|----|----|
| **Batch Requests** | Native, full support | Limited |
| **Two-Way Binding** | Entities + contained | Basic |
| **Server Processing** | Advanced ($count, $search, aggregates) | Basic |
| **Operations** | Full functions/actions | Partial |
| **Performance** | Lazy metadata, efficient | Eager, heavier |
| **Standards** | OData 4.0 spec | OData 2.0 |

### Best Practices
- Use **lazy loading** and server-side operations
- Always group changes with batches
- Enable **synchronization mode: 'None'** for async
- Test with SAPUI5 Demo Kit Sales Orders sample
- Migrate to V4 for batching/operations advantages

---

## Summary

### Batch 1 Coverage

**Floorplans** (3 additional):
- ✅ Overview Page (dashboard with cards)
- ✅ Wizard (multi-step guided processes)
- ✅ Analytical List Page (analytics-first)

**Controls** (5 major):
- ✅ sap.m.Table (responsive tables)
- ✅ sap.m.List (item lists)
- ✅ Forms (sap.ui.layout.form)
- ✅ sap.ui.table.Table (desktop tables)
- ✅ Fragments & Dialogs (reusable UI)

**Data Patterns** (2 versions):
- ✅ OData V2 (batch, CRUD, SmartTable)
- ✅ OData V4 (modern, improved batching)

### Total Documentation

**Current Status**:
- Batch 0 (Initial): 143 KB (2 files)
- Batch 1 (This): ~30 KB (1 file)
- **Total**: ~173 KB

**Coverage Progress**:
- Fiori Design: ~25% → Target 90%
- SAPUI5 SDK: ~15% → Target 85%
- Help Portal: ~10% → Target 75%

### Next Steps

**Batch 2 Topics** (planned):
1. Input controls (Input, ComboBox, DatePicker)
2. Display controls (ObjectHeader, ObjectStatus)
3. Action controls (Button, Toolbar)
4. Shell Bar & Side Navigation
5. IconTabBar deep dive
6. Message Handling patterns
7. Error Handling patterns
8. Loading & Busy indicators
9. Value Help & Search
10. Formatters & Types

**Estimated**: 80 KB additional documentation

---

**Version**: 1.0  
**Status**: ✅ Batch 1 Complete  
**Source**: SAP Fiori Design, SAPUI5 SDK, SAP Help Portal  
**Date**: January 24, 2026

This document provides comprehensive coverage of additional floorplans, major controls, and OData patterns for building enterprise SAP Fiori applications.