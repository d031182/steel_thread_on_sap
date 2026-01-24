# SAPUI5 API Quick Reference

**Purpose**: Quick reference for commonly used SAPUI5 controls in P2P application  
**Source**: Scraped from SAPUI5 SDK via Perplexity MCP  
**Date**: January 24, 2026  
**SAPUI5 Version**: 1.87+ (minimum), 1.136-1.142 (recommended)

---

## 📚 Table of Contents

1. [Basic Controls](#basic-controls) - Page, Button, Input, List
2. [Layout Controls](#layout-controls) - IconTabBar
3. [Data Display](#data-display) - Table, Column
4. [Message Controls](#message-controls) - MessageStrip, Dialog
5. [Input Controls](#input-controls) - Switch
6. [Quick Examples](#quick-examples)

---

## Basic Controls

### sap.m.Page

**Purpose**: Container for page content with title, navigation, and content aggregation

**Key Properties**:
- `title` (string) - Page title displayed in header
- `class` (string) - CSS class (e.g., "sapUiContentPadding")
- `showHeader` (boolean) - Show/hide header (default: true)
- `showNavButton` (boolean) - Show back navigation button

**Key Aggregations**:
- `content` (sap.ui.core.Control[]) - Main page content area
- `header` (sap.m.IBar) - Custom header bar
- `footer` (sap.m.IBar) - Page footer toolbar

**JavaScript Example**:
```javascript
var oPage = new sap.m.Page({
    title: "Invoice Details",
    class: "sapUiContentPadding",
    showNavButton: true,
    content: [
        new sap.m.Text({ text: "Page content here" })
    ]
});
```

**XML Example**:
```xml
<Page title="Invoice Details" class="sapUiContentPadding">
    <content>
        <Text text="Page content here"/>
    </content>
</Page>
```

---

### sap.m.Button

**Purpose**: Triggers actions on press

**Key Properties**:
- `text` (string) - Button label
- `type` (sap.m.ButtonType) - Visual style (Default, Emphasized, Accept, Reject, etc.)
- `icon` (string) - SAP icon (e.g., "sap-icon://add")
- `enabled` (boolean) - Enable/disable button (default: true)
- `tooltip` (string) - Hover text

**Key Events**:
- `press` - Fired when button is clicked

**Key Associations**:
- `ariaDescribedBy` - Links to Label for accessibility

**JavaScript Example**:
```javascript
var oButton = new sap.m.Button({
    text: "Save",
    type: "Emphasized",
    icon: "sap-icon://save",
    press: function() {
        // Handle save action
        console.log("Save clicked");
    }
});
```

**XML Example**:
```xml
<Button text="Save" 
        type="Emphasized" 
        icon="sap-icon://save" 
        press="onSavePress"/>
```

---

### sap.m.Input

**Purpose**: Enables user data input (single-line text field)

**Key Properties**:
- `value` (string) - Input value
- `placeholder` (string) - Placeholder text
- `enabled` (boolean) - Enable/disable input
- `valueState` (sap.ui.core.ValueState) - Error, Warning, Success, None
- `valueStateText` (string) - Error message text
- `required` (boolean) - Mandatory field indicator

**Key Events**:
- `change` - Fired when value changes and focus leaves field
- `liveChange` - Fired on every keystroke

**JavaScript Example**:
```javascript
var oInput = new sap.m.Input({
    value: "",
    placeholder: "Enter invoice number",
    required: true,
    valueState: "Error",
    valueStateText: "Invoice number is required",
    change: function(oEvent) {
        var sValue = oEvent.getParameter("value");
        console.log("Input changed to:", sValue);
    }
});
```

**XML Example**:
```xml
<Input value="{/invoiceNumber}" 
       placeholder="Enter invoice number"
       required="true"
       valueState="Error"
       valueStateText="Invoice number is required"
       change="onInvoiceNumberChange"/>
```

---

### sap.m.List

**Purpose**: Container for list items

**Key Properties**:
- `mode` (sap.m.ListMode) - None, SingleSelect, MultiSelect, Delete
- `growing` (boolean) - Enable growing/lazy loading
- `growingThreshold` (int) - Number of items to load initially

**Key Aggregations**:
- `items` (sap.m.ListItemBase[]) - List items

**Key Events**:
- `selectionChange` - Fired when selection changes
- `itemPress` - Fired when item is pressed

**JavaScript Example**:
```javascript
var oList = new sap.m.List({
    mode: "SingleSelect",
    selectionChange: function(oEvent) {
        var oItem = oEvent.getParameter("listItem");
        console.log("Selected:", oItem.getTitle());
    },
    items: [
        new sap.m.StandardListItem({ title: "Item 1" }),
        new sap.m.StandardListItem({ title: "Item 2" })
    ]
});
```

---

## Layout Controls

### sap.m.IconTabBar

**Purpose**: Tab control for displaying collections of tabs with associated content

**Key Properties**:
- `showSelection` (boolean) - Show/hide tab selection indicators
- `expandable` (boolean) - Enable expand/collapse behavior

**Key Aggregations**:
- `items` (sap.m.IconTabFilter[]) - Tab items
- `content` (sap.ui.core.Control[]) - Shared content displayed below tabs

**Key Events**:
- `select` - Fires on tab selection
  - Parameters: `item` (sap.m.IconTabFilter), `key` (string)
- `expand` - Fires when tab expands/collapses

**JavaScript Example**:
```javascript
var oIconTabBar = new sap.m.IconTabBar({
    showSelection: true,
    expandable: false,
    select: function(oEvent) {
        var sKey = oEvent.getParameter("key");
        console.log("Selected tab:", sKey);
        // Filter content based on tab
    },
    items: [
        new sap.m.IconTabFilter({
            icon: "sap-icon://list",
            text: "All",
            key: "all"
        }),
        new sap.m.IconTabFilter({
            icon: "sap-icon://settings",
            text: "Settings",
            key: "settings"
        })
    ],
    content: [
        new sap.m.Text({ text: "Tab content here" })
    ]
});
```

**XML Example**:
```xml
<IconTabBar id="myTabBar" showSelection="true" select="onTabSelect">
    <items>
        <IconTabFilter icon="sap-icon://list" text="All" key="all"/>
        <IconTabFilter icon="sap-icon://settings" text="Settings" key="settings"/>
    </items>
    <content>
        <Text text="Tab content here"/>
    </content>
</IconTabBar>
```

**Usage Tips**:
- Use `key` property to identify tabs in select event
- Place content in IconTabFilter for tab-specific content
- Use shared `content` aggregation for content that changes based on tab selection
- Support filtering patterns (e.g., filter table based on selected tab)

---

## Data Display

### sap.m.Table

**Purpose**: Responsive table for displaying data in tabular format with columns

**Key Properties**:
- `growing` (boolean) - Enable lazy loading (default: false)
- `growingThreshold` (int) - Items to load initially (e.g., 100)
- `growingScrollToLoad` (boolean) - Load more on scroll vs button click
- `backgroundDesign` (sap.m.BackgroundDesign) - Solid, Translucent, Transparent
- `fixedLayout` (boolean) - Fixed column widths (default: false)
- `mode` (sap.m.ListMode) - None, SingleSelect, MultiSelect

**Key Aggregations**:
- `columns` (sap.m.Column[]) - Table columns
- `items` (sap.m.ColumnListItem[]) - Table rows (binding)

**Key Methods**:
- `addColumn(oColumn)` - Add column
- `removeColumn(vColumn)` - Remove column
- `removeAllColumns()` - Remove all columns
- `getColumns()` - Get all columns

**Key Events** (inherited from ListBase):
- `selectionChange` - Selection changed
- `itemPress` - Row clicked

**JavaScript Example**:
```javascript
var oTable = new sap.m.Table({
    growing: true,
    growingThreshold: 100,
    growingScrollToLoad: true,
    mode: "MultiSelect",
    columns: [
        new sap.m.Column({
            header: new sap.m.Text({ text: "Invoice #" }),
            demandPopin: true,
            minScreenWidth: "Tablet"
        }),
        new sap.m.Column({
            header: new sap.m.Text({ text: "Amount" })
        })
    ]
});

// Bind items
oTable.bindItems({
    path: "/invoices",
    template: new sap.m.ColumnListItem({
        cells: [
            new sap.m.Text({ text: "{invoiceNumber}" }),
            new sap.m.Text({ text: "{amount}" })
        ]
    })
});
```

**XML Example with Growing Mode**:
```xml
<Table items="{/invoices}" 
       growing="true" 
       growingThreshold="100"
       growingScrollToLoad="true"
       mode="MultiSelect">
    <columns>
        <Column demandPopin="true" minScreenWidth="Tablet">
            <Text text="Invoice #"/>
        </Column>
        <Column>
            <Text text="Amount"/>
        </Column>
    </columns>
    <items>
        <ColumnListItem>
            <cells>
                <Text text="{invoiceNumber}"/>
                <Text text="{amount}"/>
            </cells>
        </ColumnListItem>
    </items>
</Table>
```

**Pop-in Behavior** (Responsive):
- Columns with `demandPopin="true"` move into details area on small screens
- `minScreenWidth` defines breakpoint (Phone, Tablet, Desktop)
- `popinDisplay` controls layout (Inline, Block)
- At least one column always stays in table layout

**Sorting/Filtering Example**:
```xml
<Table items="{ 
    path: '/invoices', 
    sorter: { path: 'invoiceNumber', descending: false },
    filters: { path: 'status', operator: 'EQ', value1: 'Posted' }
}">
```

---

### sap.m.Column

**Purpose**: Defines table column properties

**Key Properties**:
- `header` (sap.ui.core.Control) - Column header (usually sap.m.Text or Label)
- `width` (sap.ui.core.CSSSize) - Column width (e.g., "10rem", "25%")
- `hAlign` (sap.ui.core.TextAlign) - Horizontal alignment (Begin, Center, End)
- `vAlign` (sap.ui.core.VerticalAlign) - Vertical alignment
- `demandPopin` (boolean) - Force pop-in on small screens
- `minScreenWidth` (string) - Breakpoint for pop-in (Phone, Tablet, Desktop)
- `popinDisplay` (sap.m.PopinDisplay) - Pop-in layout (Inline, Block)

**Example**:
```javascript
new sap.m.Column({
    header: new sap.m.Text({ text: "Invoice Date" }),
    width: "10rem",
    hAlign: "Begin",
    demandPopin: true,
    minScreenWidth: "Tablet"
});
```

---

## Message Controls

### sap.m.MessageStrip

**Purpose**: Display contextual messages on page (info, warning, error, success)

**Key Properties**:
- `type` (sap.ui.core.MessageType) - Information, Warning, Error, Success
- `text` (string) - Message text
- `showIcon` (boolean) - Show type icon (default: false)
- `showCloseButton` (boolean) - Show close button (default: false)

**Key Events**:
- `close` - Fired when close button clicked

**JavaScript Example**:
```javascript
var oMessageStrip = new sap.m.MessageStrip({
    type: "Error",
    text: "Failed to load data. Please try again.",
    showIcon: true,
    showCloseButton: true,
    close: function() {
        console.log("Message strip closed");
    }
});
```

**XML Example**:
```xml
<MessageStrip type="Error" 
              text="Failed to load data. Please try again."
              showIcon="true"
              showCloseButton="true"
              close="onMessageClose"/>
```

**CSS Classes** (for styling reference):
```css
/* Information (Blue) */
.sapMMessageStripInformation {
    background-color: rgba(10, 110, 209, 0.1);
    border-left: 4px solid #0a6ed1;
}

/* Success (Green) */
.sapMMessageStripSuccess {
    background-color: rgba(16, 126, 62, 0.1);
    border-left: 4px solid #107e3e;
}

/* Warning (Orange) */
.sapMMessageStripWarning {
    background-color: rgba(233, 115, 12, 0.1);
    border-left: 4px solid #e9730c;
}

/* Error (Red) */
.sapMMessageStripError {
    background-color: rgba(187, 0, 0, 0.1);
    border-left: 4px solid #bb0000;
}
```

---

### sap.m.Dialog

**Purpose**: Modal popup dialog

**Key Properties**:
- `title` (string) - Dialog title
- `type` (sap.m.DialogType) - Standard, Message
- `contentWidth` (sap.ui.core.CSSSize) - Dialog width
- `contentHeight` (sap.ui.core.CSSSize) - Dialog height
- `draggable` (boolean) - Enable dragging
- `resizable` (boolean) - Enable resizing

**Key Aggregations**:
- `content` (sap.ui.core.Control[]) - Dialog content
- `buttons` (sap.m.Button[]) - Footer buttons

**Key Methods**:
- `open()` - Open dialog
- `close()` - Close dialog

**Key Events**:
- `afterOpen` - After dialog opened
- `afterClose` - After dialog closed

**JavaScript Example**:
```javascript
var oDialog = new sap.m.Dialog({
    title: "Confirm Delete",
    type: "Message",
    content: [
        new sap.m.Text({ text: "Are you sure you want to delete this invoice?" })
    ],
    beginButton: new sap.m.Button({
        text: "Delete",
        type: "Emphasized",
        press: function() {
            // Perform delete
            oDialog.close();
        }
    }),
    endButton: new sap.m.Button({
        text: "Cancel",
        press: function() {
            oDialog.close();
        }
    })
});

// Open dialog
oDialog.open();
```

---

## Input Controls

### sap.m.Switch

**Purpose**: Toggle switch control (on/off)

**Key Properties**:
- `state` (boolean) - Switch state (true=on, false=off)
- `enabled` (boolean) - Enable/disable switch
- `customTextOn` (string) - Custom text for ON state
- `customTextOff` (string) - Custom text for OFF state
- `type` (sap.m.SwitchType) - Default, AcceptReject

**Key Events**:
- `change` - Fired when state changes
  - Parameters: `state` (boolean)

**JavaScript Example**:
```javascript
var oSwitch = new sap.m.Switch({
    state: true,
    customTextOn: "ON",
    customTextOff: "OFF",
    change: function(oEvent) {
        var bState = oEvent.getParameter("state");
        console.log("Switch changed to:", bState);
    }
});
```

**XML Example**:
```xml
<Switch state="{/enabled}" 
        customTextOn="ON" 
        customTextOff="OFF"
        change="onSwitchChange"/>
```

**With Custom Data** (storing metadata):
```xml
<Switch state="{enabled}" change="onToggle">
    <customData>
        <core:CustomData key="featureKey" value="{key}"/>
    </customData>
</Switch>
```

Access custom data in event:
```javascript
onToggle: function(oEvent) {
    var oSwitch = oEvent.getSource();
    var sKey = oSwitch.data("featureKey");
    var bState = oEvent.getParameter("state");
    console.log("Feature", sKey, "toggled to", bState);
}
```

---

## Quick Examples

### Complete Page with Table
```javascript
var oPage = new sap.m.Page({
    title: "Invoices",
    content: [
        new sap.m.Table({
            growing: true,
            growingThreshold: 100,
            columns: [
                new sap.m.Column({
                    header: new sap.m.Text({ text: "Invoice #" })
                }),
                new sap.m.Column({
                    header: new sap.m.Text({ text: "Amount" })
                })
            ],
            items: {
                path: "/invoices",
                template: new sap.m.ColumnListItem({
                    cells: [
                        new sap.m.Text({ text: "{invoiceNumber}" }),
                        new sap.m.Text({ text: "{amount}" })
                    ]
                })
            }
        })
    ]
});
```

### Form with Validation
```javascript
var oForm = new sap.m.VBox({
    items: [
        new sap.m.Label({ text: "Invoice Number *", required: true }),
        new sap.m.Input({
            value: "{/invoiceNumber}",
            valueState: "Error",
            valueStateText: "Invoice number is required",
            change: function(oEvent) {
                var sValue = oEvent.getParameter("value");
                if (sValue) {
                    oEvent.getSource().setValueState("None");
                } else {
                    oEvent.getSource().setValueState("Error");
                }
            }
        }),
        new sap.m.Button({
            text: "Save",
            type: "Emphasized",
            press: function() {
                // Validate and save
            }
        })
    ]
});
```

### IconTabBar with Filtering
```javascript
var oTable = new sap.m.Table({ /* ... */ });

var oIconTabBar = new sap.m.IconTabBar({
    select: function(oEvent) {
        var sKey = oEvent.getParameter("key");
        var oBinding = oTable.getBinding("items");
        
        if (sKey === "all") {
            oBinding.filter([]);
        } else {
            oBinding.filter([
                new sap.ui.model.Filter("status", "EQ", sKey)
            ]);
        }
    },
    items: [
        new sap.m.IconTabFilter({
            icon: "sap-icon://list",
            text: "All",
            key: "all"
        }),
        new sap.m.IconTabFilter({
            icon: "sap-icon://accept",
            text: "Posted",
            key: "posted"
        })
    ],
    content: [oTable]
});
```

---

## Common Patterns

### Value State Management
```javascript
// Set error state
oInput.setValueState("Error");
oInput.setValueStateText("Field is required");

// Set success state
oInput.setValueState("Success");
oInput.setValueStateText("Valid");

// Clear state
oInput.setValueState("None");
```

### Model Binding
```javascript
// Bind property
oInput.bindProperty("value", "/invoiceNumber");

// Bind aggregation
oTable.bindItems({
    path: "/invoices",
    template: new sap.m.ColumnListItem({ /* ... */ })
});

// Set property via model
var oModel = oInput.getModel();
oModel.setProperty("/invoiceNumber", "2024-001");
```

### Event Handling
```javascript
// Attach event
oButton.attachPress(function() {
    console.log("Button pressed");
});

// Detach event
oButton.detachPress(fnHandler);

// Get event parameters
oTable.attachSelectionChange(function(oEvent) {
    var oItem = oEvent.getParameter("listItem");
    var bSelected = oEvent.getParameter("selected");
});
```

---

## SAP Icons Reference

Common icons for buttons and tabs:

```
sap-icon://add
sap-icon://save
sap-icon://delete
sap-icon://edit
sap-icon://refresh
sap-icon://filter
sap-icon://list
sap-icon://settings
sap-icon://home
sap-icon://attachment
sap-icon://documents
sap-icon://download
sap-icon://upload
sap-icon://accept
sap-icon://decline
```

Full icon explorer: https://sapui5.hana.ondemand.com/test-resources/sap/m/demokit/icon-explorer/webapp/index.html

---

## Additional Resources

- **SAPUI5 SDK**: https://sapui5.hana.ondemand.com/sdk/
- **API Reference**: https://sapui5.hana.ondemand.com/#/api
- **Samples**: https://sapui5.hana.ondemand.com/#/controls
- **Icon Explorer**: https://sapui5.hana.ondemand.com/test-resources/sap/m/demokit/icon-explorer/

---

**Status**: ✅ **QUICK REFERENCE COMPLETE**

**Coverage**: 10 most common controls with properties, methods, events, and examples

**Last Updated**: January 24, 2026