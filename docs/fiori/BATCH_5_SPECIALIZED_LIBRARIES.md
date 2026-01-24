# SAPUI5 Batch 5: Specialized Libraries & Controls - Complete Guide

**Documentation Batch**: 5 of 5 (BONUS)  
**Topics Covered**: 9 (Smart Controls, Viz Charts, Calendar/Date, File Upload, Suite Controls, Timeline, RichTextEditor, Tree, Mobile-Specific)  
**Date**: January 24, 2026  
**Source**: SAP Official Documentation via Perplexity AI  

---

## 1. Smart Controls (sap.ui.comp)

### Overview

**Smart Controls** are metadata-driven controls that automatically generate UI based on OData service metadata and annotations, drastically reducing development effort for SAP Fiori applications.

### Key Controls

**SmartTable**:
```xml
<smartTable:SmartTable 
    entitySet="Products"
    tableType="ResponsiveTable"
    useTablePersonalisation="true"
    enableAutoBinding="true"
    showRowCount="true"
    beforeRebindTable="onBeforeRebindTable">
    <!-- Columns auto-generated from metadata -->
</smartTable:SmartTable>
```

**SmartFilterBar**:
```xml
<smartFilterBar:SmartFilterBar 
    id="smartFilterBar"
    entitySet="Products"
    persistencyKey="ProductsFilter"
    showClearOnFB="true">
    <!-- Filters auto-generated from metadata -->
</smartFilterBar:SmartFilterBar>
```

**SmartField**:
```xml
<smartField:SmartField 
    value="{ProductName}"
    entitySet="Products"
    editable="true"/>
<!-- Auto-detects type, adds value help, handles validation -->
```

**SmartChart**:
```xml
<smartChart:SmartChart 
    entitySet="Products"
    smartFilterId="smartFilterBar"
    enableAutoBinding="true"/>
<!-- Auto-generates chart from annotations -->
```

**SmartForm**:
```xml
<smartForm:SmartForm 
    entitySet="Products"
    editable="true">
    <!-- Fields auto-generated, layout adaptive -->
</smartForm:SmartForm>
```

### OData Metadata Annotations

Smart controls rely on annotations for behavior:

```xml
<!-- In OData metadata or CDS -->
<Annotations Target="Product">
    <!-- Table columns -->
    <Annotation Term="UI.LineItem">
        <Collection>
            <Record Type="UI.DataField">
                <PropertyValue Property="Value" Path="ProductName"/>
            </Record>
        </Collection>
    </Annotation>
    
    <!-- Field group for forms/filters -->
    <Annotation Term="UI.FieldGroup">
        <Record>
            <PropertyValue Property="Data">
                <Collection>
                    <Record Type="UI.DataField">
                        <PropertyValue Property="Value" Path="Category"/>
                    </Record>
                </Collection>
            </PropertyValue>
        </Record>
    </Annotation>
    
    <!-- Value help -->
    <Annotation Term="Common.ValueList">
        <Record>
            <PropertyValue Property="CollectionPath" String="Categories"/>
        </Record>
    </Annotation>
    
    <!-- Chart definition -->
    <Annotation Term="UI.Chart">
        <Record>
            <PropertyValue Property="ChartType" EnumMember="UI.ChartType/Column"/>
            <PropertyValue Property="Dimensions">
                <Collection>
                    <PropertyPath>Category</PropertyPath>
                </Collection>
            </PropertyValue>
            <PropertyValue Property="Measures">
                <Collection>
                    <PropertyPath>Sales</PropertyPath>
                </Collection>
            </PropertyValue>
        </Record>
    </Annotation>
</Annotations>

<!-- Property annotations -->
<Property Name="Status" sap:sortable="true" sap:filterable="true"/>
<Property Name="Price" sap:unit="Currency"/>
```

### Custom Logic Integration

**beforeRebindTable Event**:
```javascript
onBeforeRebindTable: function(oEvent) {
    var mBindingParams = oEvent.getParameter("bindingParams");
    
    // Add custom filters
    var oCustomFilter = new Filter("Status", FilterOperator.EQ, "Active");
    mBindingParams.filters.push(oCustomFilter);
    
    // Add custom sorters
    var oSorter = new Sorter("ProductName", false);
    mBindingParams.sorter.push(oSorter);
}
```

**Custom Tokens in SmartField**:
```javascript
onAfterRendering: function() {
    var oSmartField = this.byId("supplierField");
    // Add custom token
    oSmartField.addToken(new Token({
        key: "SUP001",
        text: "Supplier ABC"
    }));
}
```

### Best Practices

| Practice | Implementation |
|----------|----------------|
| **Start with metadata** | Ensure OData has complete annotations before UI dev |
| **Debug systematically** | Check metadata → smart control → base control |
| **Extend judiciously** | Use beforeRebind for custom logic, not controller overrides |
| **Personalization** | Enable useTablePersonalisation and SmartVariants |
| **Performance** | Leverage smart controls for large datasets |
| **Fiori Elements synergy** | Use together for low-code apps |

**Limitations**:
- Requires well-annotated OData service
- SAP prioritizes Fiori Elements over standalone smart controls
- Complex customizations may require Fiori Elements extensions

---

## 2. Visualization Charts (sap.viz)

### VizFrame Control

**sap.viz.ui5.controls.VizFrame** is the primary control for creating interactive charts.

### Chart Types

| Chart Type | vizType | Use Case |
|-----------|---------|----------|
| **Column** | `column`, `stacked_column`, `100_stacked_column` | Vertical comparisons |
| **Bar** | `bar`, `stacked_bar`, `100_stacked_bar` | Horizontal comparisons |
| **Line** | `line`, `dual_line` | Trends over time |
| **Pie** | `pie`, `donut` | Part-to-whole ratios |
| **Scatter** | `scatter`, `bubble` | Correlations, x-y relationships |
| **Heatmap** | `heatmap` | Density matrices |
| **Area** | `area`, `100_stacked_area` | Volume trends |
| **Bullet** | `bullet`, `vertical_bullet` | Performance vs target |
| **Combination** | `combination`, `dual_combination` | Multiple measures |

### Basic Configuration

```xml
<viz:VizFrame 
    id="idVizFrame"
    height="400px"
    width="100%"
    vizType="column"
    uiConfig="{applicationSet:'fiori'}"
    vizProperties="{
        title: {text: 'Sales by Category'},
        plotArea: {
            colorPalette: ['#5899DA', '#E8743B', '#19A979'],
            dataLabel: {visible: true}
        },
        legend: {visible: true},
        tooltip: {visible: true}
    }">
    
    <viz:dataset>
        <vizData:FlattenedDataset data="{/SalesData}">
            <vizData:dimensions>
                <vizData:DimensionDefinition 
                    name="Category" 
                    value="{Category}"/>
            </vizData:dimensions>
            <vizData:measures>
                <vizData:MeasureDefinition 
                    name="Sales" 
                    value="{Revenue}"/>
            </vizData:measures>
        </vizData:FlattenedDataset>
    </viz:dataset>
    
    <viz:feeds>
        <viz:FeedItem 
            uid="categoryAxis" 
            type="Dimension" 
            values="Category"/>
        <viz:FeedItem 
            uid="valueAxis" 
            type="Measure" 
            values="Sales"/>
    </viz:feeds>
</viz:VizFrame>
```

### Data Binding

**FlattenedDataset Structure**:
```javascript
// Dimensions (categories, x-axis)
var oDimension = new sap.viz.ui5.data.DimensionDefinition({
    name: "Brand",
    value: "{Brand}"
});

// Measures (values, y-axis)
var oMeasure = new sap.viz.ui5.data.MeasureDefinition({
    name: "CarsBought",
    value: "{Value}"
});

// Dataset
var oDataset = new sap.viz.ui5.data.FlattenedDataset({
    dimensions: [oDimension],
    measures: [oMeasure],
    data: {
        path: "/Reports"
    }
});

oVizFrame.setDataset(oDataset);
```

**Feeds (Map data to visual roles)**:
```javascript
var oCategoryAxis = new sap.viz.ui5.controls.common.feeds.FeedItem({
    uid: "categoryAxis",
    type: "Dimension",
    values: ["Brand"]
});

var oValueAxis = new sap.viz.ui5.controls.common.feeds.FeedItem({
    uid: "valueAxis",
    type: "Measure",
    values: ["CarsBought"]
});

oVizFrame.addFeed(oCategoryAxis);
oVizFrame.addFeed(oValueAxis);
```

### Dynamic Chart Switching

```javascript
// Change chart type on button press
onChartTypeChange: function(oEvent) {
    var sChartType = oEvent.getParameter("selectedItem").getKey();
    var oVizFrame = this.byId("idVizFrame");
    
    // Clear feeds
    oVizFrame.removeAllFeeds();
    
    // Set new type
    oVizFrame.setVizType(sChartType);
    
    // Recreate feeds based on type
    if (sChartType === "pie") {
        oVizFrame.addFeed(new FeedItem({
            uid: "size",
            type: "Measure",
            values: ["Sales"]
        }));
        oVizFrame.addFeed(new FeedItem({
            uid: "color",
            type: "Dimension",
            values: ["Category"]
        }));
    } else {
        // Standard category/value axis
        oVizFrame.addFeed(new FeedItem({
            uid: "categoryAxis",
            type: "Dimension",
            values: ["Category"]
        }));
        oVizFrame.addFeed(new FeedItem({
            uid: "valueAxis",
            type: "Measure",
            values: ["Sales"]
        }));
    }
}
```

### Customization with vizProperties

```javascript
oVizFrame.setVizProperties({
    // Title
    title: {
        text: "Data Analysis",
        visible: true
    },
    
    // Plot area
    plotArea: {
        colorPalette: ['#5899DA', '#E8743B', '#19A979'],
        dataLabel: {
            visible: true,
            showTotal: true
        },
        drawingEffect: 'glossy'
    },
    
    // Legend
    legend: {
        visible: true,
        position: 'right'
    },
    
    // Tooltip
    tooltip: {
        visible: true
    },
    
    // Axes
    categoryAxis: {
        title: {
            visible: true,
            text: "Categories"
        }
    },
    valueAxis: {
        title: {
            visible: true,
            text: "Sales ($)"
        }
    }
});
```

### Best Practices

- ✅ **Dynamic switching**: Change vizType and recreate feeds for responsive UIs
- ✅ **Customization**: Use vizProperties for colors, labels, legends
- ✅ **Fiori theming**: Set uiConfig="{applicationSet:'fiori'}"
- ✅ **Interactivity**: Enable zooming, panning, tooltips
- ✅ **Performance**: VizFrame handles large datasets efficiently
- ✅ **ChartContainer**: Embed in ChartContainer for toolbar and table view
- ❌ **Don't use deprecated Viz charts** (use VizFrame since 1.32+)

---

## 3. Calendar & Date Controls (sap.ui.unified)

### sap.ui.unified.Calendar

**Multi-view calendar for direct date selection**:

```javascript
var oCalendar = new sap.ui.unified.Calendar({
    select: function(oEvent) {
        var aSelectedDates = oEvent.getSource().getSelectedDates();
        // Handle selection
    }
});

// Single day selection (default)
oCalendar.addSelectedDate(new DateRange({
    startDate: new Date(2026, 0, 24)
}));

// Range selection
oCalendar.addSelectedDate(new DateRange({
    startDate: new Date(2026, 0, 20),
    endDate: new Date(2026, 0, 25)
}));

// Multiple days
oCalendar.addSelectedDate(new DateRange({startDate: new Date(2026, 0, 15)}));
oCalendar.addSelectedDate(new DateRange({startDate: new Date(2026, 0, 20)}));
```

**Configuration**:
```javascript
// Show week numbers
oCalendar.setProperty("showWeekNumbers", true);

// Special dates with custom styling
oCalendar.addSpecialDate(new DateTypeRange({
    startDate: new Date(2026, 0, 1),
    endDate: new Date(2026, 0, 1),
    type: sap.ui.unified.CalendarDayType.Type01,
    tooltip: "New Year's Day"
}));
```

### Selection Modes

| Mode | Description | User Interaction |
|------|-------------|------------------|
| **Single Day** | Select one day | Click day |
| **Range** | Select interval | Click start/end, or Shift+Enter twice |
| **Multiple Days** | Individual selections | Click days, Shift+Space for full week |

### sap.m.DateRangePicker

**Input field with calendar picker for date ranges**:

```xml
<DateRangePicker
    dateValue="{/startDate}"
    secondDateValue="{/endDate}"
    displayFormat="dd/MM/yyyy"
    placeholder="Select date range"
    change="onDateRangeChange"/>
```

**Usage**:
```javascript
onDateRangeChange: function(oEvent) {
    var oDateRange = oEvent.getSource();
    var dStartDate = oDateRange.getDateValue();
    var dEndDate = oDateRange.getSecondDateValue();
    
    if (dStartDate && dEndDate) {
        // Valid range selected
        this.filterByDateRange(dStartDate, dEndDate);
    }
}
```

### sap.ui.unified.PlanningCalendar

**Multi-row calendar for appointments across resources**:

```xml
<PlanningCalendar
    id="planningCalendar"
    startDate="{/startDate}"
    appointmentsVisualization="Filled"
    appointmentSelect="onAppointmentSelect"
    showEmptyIntervalHeaders="false"
    showWeekNumbers="true"
    rows="{/people}">
    
    <rows>
        <PlanningCalendarRow
            icon="sap-icon://employee"
            title="{name}"
            appointments="{appointments}">
            <appointments>
                <PlanningCalendarAppointment
                    start="{start}"
                    end="{end}"
                    title="{title}"
                    type="{type}"
                    tentative="{tentative}"/>
            </appointments>
        </PlanningCalendarRow>
    </rows>
</PlanningCalendar>
```

**Model Structure**:
```javascript
var oModel = new JSONModel({
    startDate: new Date(),
    people: [
        {
            name: "John Smith",
            key: "person1",
            appointments: [
                {
                    start: new Date(2026, 0, 24, 10, 0),
                    end: new Date(2026, 0, 24, 12, 0),
                    title: "Meeting",
                    type: "Type01",
                    tentative: false
                },
                {
                    start: new Date(2026, 0, 24, 14, 0),
                    end: new Date(2026, 0, 24, 15, 30),
                    title: "Review",
                    type: "Type02",
                    tentative: true
                }
            ]
        }
    ]
});
```

**Appointment Types** (semantic colors):
- Type01: Blue
- Type02: Orange
- Type03: Green
- Type04: Red

### When to Choose

| Control | Best For | Avoid For |
|---------|----------|-----------|
| **Calendar** | Visible multi-month selection, power users | Compact UIs, time inputs |
| **DateRangePicker** | Input + range picker, space-constrained | Full calendar visibility needed |
| **PlanningCalendar** | Multi-user appointments, scheduling | Simple date picking |

### Best Practices

- ✅ Set startDate dynamically (new Date() for today)
- ✅ Enable week numbers for week-based selection
- ✅ Use specialDates for holidays, important dates
- ✅ Handle min/max dates for valid ranges
- ✅ Test F4 shortcuts (Calendar popup)
- ✅ Customize appointment types with semantic colors
- ❌ Don't use Calendar on mobile (takes too much space)

---

## 4. File Upload Controls

### Control Comparison

| Control | Drag & Drop | Multiple Files | Progress | Best For |
|---------|-------------|----------------|----------|----------|
| **FileUploader** (sap.ui.unified) | Limited | Yes | Basic | Simple uploads |
| **UploadSet** (sap.m) ⭐ **RECOMMENDED** | Native | Yes | Per-file progress | Modern apps |
| **UploadCollection** (sap.m) | Yes | Yes | Advanced | Legacy apps |

### FileUploader (Basic)

```xml
<FileUploader
    id="fileUploader"
    name="myFileUpload"
    uploadUrl="/upload_endpoint"
    multiple="true"
    fileType="pdf,jpg,png"
    maximumFileSize="5"
    mimeType="application/pdf,image/*"
    uploadComplete="onUploadComplete"/>

<Button 
    text="Upload" 
    press="onUploadPress"/>
```

**Controller**:
```javascript
onUploadPress: function() {
    var oFileUploader = this.byId("fileUploader");
    
    if (!oFileUploader.getValue()) {
        MessageToast.show("Please select a file first");
        return;
    }
    
    // Get file
    var domRef = oFileUploader.getFocusDomRef();
    var file = domRef.files[0];
    
    // Validate
    if (file.size > 5 * 1024 * 1024) {
        MessageBox.error("File too large (max 5MB)");
        return;
    }
    
    // Upload
    oFileUploader.upload();
},

onUploadComplete: function(oEvent) {
    var sResponse = oEvent.getParameter("response");
    if (sResponse) {
        MessageToast.show("Upload successful");
        this.byId("fileUploader").clear();
    }
}
```

### UploadSet (Modern) ⭐ RECOMMENDED

```xml
<UploadSet
    id="uploadSet"
    uploadUrl="/upload_endpoint"
    instantUpload="false"
    uploadCompleted="onUploadCompleted"
    items="{uploadModel>/items}">
    
    <toolbar>
        <OverflowToolbar>
            <Title text="Attachments" level="H2"/>
            <ToolbarSpacer/>
            <Button 
                text="Upload All" 
                press="onUploadAll"
                enabled="{= ${uploadModel>/items}.length > 0}"/>
        </OverflowToolbar>
    </toolbar>
</UploadSet>
```

**Model-Driven Approach**:
```javascript
onInit: function() {
    var oModel = new JSONModel({
        items: []
    });
    this.setModel(oModel, "uploadModel");
},

onUploadAll: function() {
    var oUploadSet = this.byId("uploadSet");
    oUploadSet.getItems().forEach(function(oItem) {
        oUploadSet.uploadItem(oItem);
    });
}
```

**Native Drag & Drop**:
- Users drag files onto UploadSet
- Files appear in list with progress indicators
- Upload triggered manually or automatically

### Multiple File Upload Pattern

```javascript
onUploadMultiple: function() {
    var oUploader = this.byId("fileUploader");
    var domRef = oUploader.getFocusDomRef();
    var aFiles = domRef.files;
    
    // Process files sequentially
    this._uploadFileSequentially(aFiles, 0);
},

_uploadFileSequentially: function(aFiles, iIndex) {
    if (iIndex >= aFiles.length) {
        MessageToast.show("All files uploaded");
        return;
    }
    
    var file = aFiles[iIndex];
    var reader = new FileReader();
    
    reader.onload = function(e) {
        var vContent = e.currentTarget.result;
        
        // Create FormData
        var formData = new FormData();
        formData.append('file', file);
        
        // Upload via AJAX
        jQuery.ajax({
            url: "/upload_endpoint",
            method: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function() {
                // Next file
                this._uploadFileSequentially(aFiles, iIndex + 1);
            }.bind(this),
            error: function(error) {
                MessageBox.error("Upload failed: " + file.name);
                // Continue with next file
                this._uploadFileSequentially(aFiles, iIndex + 1);
            }.bind(this)
        });
    }.bind(this);
    
    reader.readAsDataURL(file);
}
```

### Validation

**Frontend**:
```javascript
// Type validation
if (!file.type.match('image/*')) {
    MessageBox.error("Only images allowed");
    return;
}

// Size validation
if (file.size > 5 * 1024 * 1024) {
    MessageBox.error("File exceeds 5MB limit");
    return;
}

// Extension validation
var sExtension = file.name.split('.').pop().toLowerCase();
if (!['jpg', 'png', 'pdf'].includes(sExtension)) {
    MessageBox.error("Invalid file type");
    return;
}
```

**Backend** (OData example):
```javascript
// CSRF token for non-GET
var oModel = this.getView().getModel();
oModel.refreshSecurityToken();

// Upload with OData
oModel.update("/Files('" + fileName + "')/$value", {
    Filecontent: vContent
}, {
    method: "PUT",
    success: function() {
        MessageToast.show("Uploaded successfully");
    },
    error: function(oError) {
        MessageBox.error("Upload failed: " + oError.message);
    }
});
```

### Best Practices

- ✅ **Async multi-upload**: Process files one-by-one to avoid blocking
- ✅ **Progress tracking**: Use ProgressIndicator bound to model
- ✅ **Security**: Validate types/sizes both frontend and backend
- ✅ **CSRF protection**: Fetch token for POST/PUT operations
- ✅ **Error handling**: Track errors per file, show in MessagePopover
- ✅ **Performance**: Limit concurrent uploads
- ✅ **Fiori compliance**: Prefer UploadSet for modern apps
- ✅ **Download support**: Implement base64 decode + File.save()

---

## 5. Suite Controls (sap.suite)

### ChartContainer

**Combines toolbar with multiple chart views and table view**:

```xml
<suite:ChartContainer
    id="chartContainer"
    showPersonalization="true"
    autoAdjustHeight="true"
    showFullScreen="true"
    showLegend="true"
    title="Sales Dashboard">
    
    <suite:content>
        <!-- Chart view 1 -->
        <suite:ChartContainerContent
            icon="sap-icon://vertical-bar-chart"
            title="Column Chart">
            <suite:content>
                <viz:VizFrame vizType="column">
                    <!-- Chart config -->
                </viz:VizFrame>
            </suite:content>
        </suite:ChartContainerContent>
        
        <!-- Chart view 2 -->
        <suite:ChartContainerContent
            icon="sap-icon://pie-chart"
            title="Pie Chart">
            <suite:content>
                <viz:VizFrame vizType="pie">
                    <!-- Chart config -->
                </viz:VizFrame>
            </suite:content>
        </suite:ChartContainerContent>
        
        <!-- Table view -->
        <suite:ChartContainerContent
            icon="sap-icon://table-view"
            title="Table">
            <suite:content>
                <Table items="{/data}">
                    <!-- Table config -->
                </Table>
            </suite:content>
        </suite:ChartContainerContent>
    </suite:content>
    
    <suite:dimensionSelectors>
        <suite:DimensionSelector>
            <!-- Dimension filters -->
        </suite:DimensionSelector>
    </suite:dimensionSelectors>
</suite:ChartContainer>
```

**Features**:
- Switch between chart types and table view
- Toolbar with personalization, legend toggle
- Full screen mode
- Dimension selectors for filtering
- Works with VizFrame and standard tables

### Timeline

**Chronological event display**:

```xml
<suite:Timeline
    id="timeline"
    growing="true"
    growingThreshold="10"
    enableBusyIndicator="true"
    alignment="Right"
    axisOrientation="Vertical"
    select="onTimelineSelect">
    
    <suite:content>
        <suite:TimelineItem
            dateTime="2026-01-24T10:00:00"
            title="Order Created"
            text="Purchase Order #12345 created by John Smith"
            icon="sap-icon://create"
            userNameClickable="false"/>
        
        <suite:TimelineItem
            dateTime="2026-01-24T14:30:00"
            title="Order Approved"
            text="Approved by Manager"
            icon="sap-icon://approve"
            userNameClickable="false"/>
    </suite:content>
</suite:Timeline>
```

**Dynamic Binding**:
```javascript
var oModel = new JSONModel({
    events: [
        {
            dateTime: new Date(2026, 0, 24, 10, 0).toISOString(),
            title: "Event 1",
            text: "Description",
            icon: "sap-icon://activity-individual"
        }
    ]
});

// Bind timeline
oTimeline.bindAggregation("content", {
    path: "/events",
    template: new TimelineItem({
        dateTime: "{dateTime}",
        title: "{title}",
        text: "{text}",
        icon: "{icon}"
    })
});
```

**Properties**:
- **alignment**: Left/Right/Top/Bottom
- **axisOrientation**: Vertical/Horizontal
- **growing**: Enable pagination for large datasets
- **growingThreshold**: Items loaded per page (default: 5)
- **enableBusyIndicator**: Show loading overlay

**Events**:
```javascript
onTimelineSelect: function(oEvent) {
    var oItem = oEvent.getParameter("selectedItem");
    MessageBox.information(
        oItem.getTitle() + "\n" + oItem.getText()
    );
},

onGrow: function(oEvent) {
    // Load next batch from backend
    this.loadMoreEvents();
}
```

### Best Practices

**ChartContainer**:
- ✅ Use for dashboards with multiple visualizations
- ✅ Embed VizFrame for charts
- ✅ Provide table view as alternative
- ✅ Enable personalization for user preferences

**Timeline**:
- ✅ Use ISO 8601 format for dateTime (automatic sorting)
- ✅ Enable growing for >20 items
- ✅ Set meaningful icons for event types
- ✅ Handle select event for navigation
- ✅ Use noDataText for empty states
- ✅ Customize types/colors (Type01-Type04)
- ❌ Don't load all items at once (use pagination)

---

## 6. RichTextEditor (sap.ui.richtexteditor)

### Overview

**WYSIWYG text editing** powered by TinyMCE with formatting toolbar.

### Basic Setup

```javascript
// Controller-based (recommended for custom toolbar)
var oRichTextEditor = new sap.ui.richtexteditor.RichTextEditor({
    id: "editor",
    height: "400px",
    width: "100%",
    editorType: "tinyMCE4",
    customToolbar: true,
    value: "{/content}",
    change: function(oEvent) {
        var sValue = oEvent.getParameter("newValue");
        // Handle change
    }
});

// Add to page
this.byId("editorContainer").addContent(oRichTextEditor);
```

**XML View** (native toolbar):
```xml
<richtexteditor:RichTextEditor
    id="editor"
    height="400px"
    editorType="tinyMCE4"
    value="{/content}"
    change="onChange"/>
```

### Custom Toolbar Configuration

```javascript
oRichTextEditor.setButtonGroups([
    {
        name: "font-style",
        visible: true,
        row: 0,
        priority: 10,
        buttons: ["bold", "italic", "underline", "strikethrough"]
    },
    {
        name: "text-align",
        visible: true,
        row: 0,
        priority: 20,
        buttons: ["justifyleft", "justifycenter", "justifyright", "justifyfull"]
    },
    {
        name: "styles",
        visible: true,
        row: 0,
        priority: 30,
        buttons: ["styleselect"]  // H1-H6, paragraph
    },
    {
        name: "lists",
        visible: true,
        row: 1,
        priority: 10,
        buttons: ["bullist", "numlist"]
    },
    {
        name: "indentation",
        visible: true,
        row: 1,
        priority: 20,
        buttons: ["indent", "outdent"]
    },
    {
        name: "clipboard",
        visible: true,
        row: 1,
        priority: 30,
        buttons: ["cut", "copy", "paste"]
    },
    {
        name: "undo",
        visible: true,
        row: 1,
        priority: 40,
        buttons: ["undo", "redo"]
    },
    {
        name: "link",
        visible: true,
        row: 2,
        priority: 10,
        buttons: ["link", "unlink"]
    },
    {
        name: "insert",
        visible: true,
        row: 2,
        priority: 20,
        buttons: ["image", "table"]  // v1.48+ for table
    },
    {
        name: "format",
        visible: true,
        row: 2,
        priority: 30,
        buttons: ["forecolor", "backcolor", "removeformat"]
    }
]);
```

### Formatting Capabilities

**Text Formatting**:
- Bold, italic, underline, strikethrough
- Font family and size selection
- Foreground and background colors (RGB/HSL/HEX picker with transparency)

**Structure**:
- Headings (H1-H6) via styleselect
- Paragraphs
- Bulleted and numbered lists
- Indentation (indent/outdent)

**Media and Links**:
- Insert/edit links (URL, text, title, target)
- Insert images (width, height, description)
- Insert tables (rows/columns via dialog - v1.48+)

### Mobile Theme Configuration

```javascript
oRichTextEditor.attachBeforeEditorInit(function(oEvent) {
    var oConfig = oEvent.getParameter('configuration');
    oConfig.mobile = {
        theme: "mobile",
        toolbar: [
            "undo", "redo",
            "bold", "italic", "underline",
            "link", "unlink",
            "image",
            "bullist", "numlist",
            "fontsizeselect",
            "forecolor",
            "styleselect",
            "removeformat"
        ]
    };
});
```

### Best Practices

**Layout/UX**:
- ✅ Minimum width: 17.5rem (280px)
- ✅ Default content left-aligned
- ❌ **Desktop only** - Not responsive, avoid on mobile
- ❌ **Not a form control** - Don't use in sap.ui.layout.form

**Performance/Rendering**:
- ✅ Destroy instances when hiding (don't use visibility="hidden")
- ✅ Recreate on show to prevent memory leaks
- ✅ Load sap.m library before custom toolbar init
- ❌ Avoid IE11+ with document.domain changes

**Accessibility**:
- ✅ Use ariaLabelledBy with labels
- ✅ Always visible in edit mode
- ✅ User must click content area to type

**Features by Version**:
- v1.28+: Basic RichTextEditor
- v1.48+: Table insertion
- v1.52+: Headings (styleselect/formatselect)
- v1.54+: Custom row/priority positioning

---

## 7. Tree Controls

### sap.ui.table.TreeTable

**Hierarchical data in tabular format with expand/collapse**:

```xml
<table:TreeTable
    id="treeTable"
    rows="{
        path: '/Products',
        parameters: {
            countMode: 'Inline',
            treeAnnotationProperties: {
                hierarchyLevelFor: 'HierarchyLevel',
                hierarchyNodeFor: 'NodeID',
                hierarchyParentNodeFor: 'ParentNodeID',
                hierarchyDrillStateFor: 'DrillState'
            }
        }
    }"
    expandFirstLevel="true"
    selectionMode="Single"
    enableColumnReordering="true"
    rowSelectionChange="onRowSelect">
    
    <table:columns>
        <table:Column 
            filterProperty="NodeID"
            showFilterMenuEntry="true">
            <Label text="Node ID"/>
            <table:template>
                <Input value="{NodeID}" enabled="false"/>
            </table:template>
        </table:Column>
        
        <table:Column>
            <Label text="Name"/>
            <table:template>
                <Input value="{Name}" enabled="{ui>/editMode}"/>
            </table:template>
        </table:Column>
        
        <table:Column>
            <Label text="Level"/>
            <table:template>
                <Text text="{HierarchyLevel}"/>
            </table:template>
        </table:Column>
    </table:columns>
</table:TreeTable>
```

### Data Model Requirements

**Required Properties**:

| Property | Type | Purpose | Example |
|----------|------|---------|---------|
| **NodeID** | String | Unique identifier | "NODE_001" |
| **HierarchyLevel** | Integer | Indentation level | 0, 1, 2, 3 |
| **ParentNodeID** | String/null | Parent reference | "NODE_PARENT" or null |
| **DrillState** | String | Expand state | "expanded", "collapsed", "leaf" |

**Data Structure Example**:
```javascript
{
    Products: [
        {
            NodeID: "ROOT_1",
            Name: "Electronics",
            HierarchyLevel: 0,
            ParentNodeID: null,
            DrillState: "expanded"
        },
        {
            NodeID: "CHILD_1_1",
            Name: "Computers",
            HierarchyLevel: 1,
            ParentNodeID: "ROOT_1",
            DrillState: "collapsed"
        },
        {
            NodeID: "CHILD_1_1_1",
            Name: "Laptops",
            HierarchyLevel: 2,
            ParentNodeID: "CHILD_1_1",
            DrillState: "leaf"
        }
    ]
}
```

**CRITICAL: ParentNodeID for roots MUST be `null`, not `0`** (0 breaks OData binding)

### Programmatic Expand/Collapse

```javascript
onRowSelect: function(oEvent) {
    var oTable = this.byId("treeTable");
    var iIndex = oEvent.getParameter("rowIndex");
    var oContext = oTable.getContextByIndex(iIndex);
    var sDrillState = oContext.getProperty("DrillState");
    
    if (sDrillState === "collapsed") {
        oTable.expand(iIndex);
    } else if (sDrillState === "expanded") {
        oTable.collapse(iIndex);
    }
},

// Expand all children of selected node
onExpandChildren: function() {
    var oTable = this.byId("treeTable");
    var aSelectedIndices = oTable.getSelectedIndices();
    
    aSelectedIndices.forEach(function(iIndex) {
        this._expandRecursively(oTable, iIndex);
    }.bind(this));
},

_expandRecursively: function(oTable, iIndex) {
    oTable.expand(iIndex);
    
    // Expand children recursively
    var oContext = oTable.getContextByIndex(iIndex);
    var sNodeID = oContext.getProperty("NodeID");
    
    // Find children and expand them
    // Implementation depends on data structure
}
```

### Filtering and Editing

**Search/Filter**:
```javascript
onFilter: function(oEvent) {
    var sQuery = oEvent.getParameter("query");
    var aFilters = [];
    
    if (sQuery) {
        aFilters.push(new Filter("Name", FilterOperator.Contains, sQuery));
    }
    
    this.byId("treeTable").getBinding("rows").filter(aFilters);
}
```

**Editable Mode**:
```javascript
onEdit: function() {
    var oModel = this.getView().getModel("ui");
    oModel.setProperty("/editMode", true);
}
```

### sap.m.Tree (Mobile Alternative)

**Responsive tree for mobile devices**:

```xml
<Tree
    id="mobileTree"
    items="{
        path: '/Categories',
        parameters: {
            arrayNames: ['Items']
        }
    }">
    <StandardTreeItem 
        title="{Name}"
        icon="{Icon}"/>
</Tree>
```

### Best Practices

- ✅ **Performance**: Use countMode: 'Inline', limit initial expand to first level
- ✅ **NULL handling**: Ensure true NULL (not 0) for root ParentNodeID
- ✅ **Fiori Elements**: Use TreeTable Building Block for simplified config
- ✅ **Lazy loading**: Load children on expand via OData $expand
- ✅ **Selection**: Handle rowSelectionChange for navigation
- ✅ **Mobile**: Use sap.m.Tree for responsive support
- ❌ **Don't deep expand initially** (performance issues with large hierarchies)

---

## 8. Mobile-Specific Controls (sap.m)

### Overview

**sap.m library** contains responsive controls designed for touch devices and desktop browsers, automatically adapting to available screen space.

### Key Mobile Controls

**ActionSheet** - Button menu for touch:
```javascript
var oActionSheet = new sap.m.ActionSheet({
    showCancelButton: true,
    buttons: [
        new Button({
            text: "Edit",
            icon: "sap-icon://edit",
            press: function() {
                // Handle edit
            }
        }),
        new Button({
            text: "Delete",
            icon: "sap-icon://delete",
            type: "Reject",
            press: function() {
                // Handle delete
            }
        })
    ]
});

// Open from button
oActionSheet.openBy(oButton);
```

**Carousel** - Swipeable image gallery:
```xml
<Carousel
    height="300px"
    loop="true"
    showPageIndicator="true">
    <Image src="image1.jpg"/>
    <Image src="image2.jpg"/>
    <Image src="image3.jpg"/>
</Carousel>
```

**Slider** - Touch-friendly value selection:
```xml
<Slider
    min="0"
    max="100"
    step="1"
    value="{/volume}"
    liveChange="onSliderChange"
    width="300px"
    enableTickmarks="true"/>
```

**PullToRefresh** - Refresh gesture:
```xml
<Page showHeader="false">
    <PullToRefresh
        id="pullToRefresh"
        refresh="onRefresh"/>
    <List items="{/data}">
        <!-- List items -->
    </List>
</Page>
```

```javascript
onRefresh: function() {
    // Simulate data refresh
    setTimeout(function() {
        this.loadData();
        this.byId("pullToRefresh").hide();
    }.bind(this), 2000);
}
```

**CheckBox** - Touch-optimized selection:
```xml
<CheckBox
    text="I agree to terms"
    selected="{/agreed}"
    select="onCheckBoxSelect"/>
```

**MaskInput** - Formatted data entry:
```xml
<MaskInput
    mask="(999) 999-9999"
    placeholder="Enter phone number"
    placeholderSymbol="_"
    value="{/phone}"/>
```

### SplitApp for Mobile Navigation

```xml
<SplitApp id="splitApp">
    <!-- Master view (list) -->
    <masterPages>
        <Page title="Products">
            <List 
                items="{/products}"
                itemPress="onItemPress">
                <StandardListItem 
                    title="{name}"
                    type="Navigation"/>
            </List>
        </Page>
    </masterPages>
    
    <!-- Detail view -->
    <detailPages>
        <Page title="{/selectedProduct/name}">
            <!-- Product details -->
        </Page>
    </detailPages>
</SplitApp>
```

**Responsive Behavior**:
- **Phone**: Shows only master or detail (navigation between)
- **Tablet/Desktop**: Shows both master and detail side-by-side

### Touch Gestures

**Built-in gesture support**:
- Swipe: Carousel navigation, list item actions
- Tap: Button press, list selection
- Long press: Context menu
- Pinch: Zoom (in specialized controls)
- Pull: Refresh gesture

**Custom Gestures** (if needed):
```javascript
onInit: function() {
    var oControl = this.byId("myControl");
    
    // Attach swipe handler
    oControl.attachBrowserEvent("swipe", function(oEvent) {
        if (oEvent.swipeDirection === "left") {
            // Handle left swipe
        }
    });
}
```

### Device Detection

```javascript
// sap.ui.Device API
if (sap.ui.Device.system.phone) {
    // Phone-specific behavior
    this.byId("splitApp").toMaster();
} else if (sap.ui.Device.system.tablet) {
    // Tablet behavior
    this.showBothViews();
} else {
    // Desktop behavior
    this.enableAdvancedFeatures();
}

// Orientation
if (sap.ui.Device.orientation.landscape) {
    // Landscape layout
}

// Touch support
if (sap.ui.Device.support.touch) {
    // Enable touch-optimized features
}
```

### Responsive Layout with CSS Classes

**Spacing Classes**:
```xml
<VBox class="sapUiSmallMargin">
    <Button text="Action 1" class="sapUiTinyMarginBottom"/>
    <Button text="Action 2" class="sapUiTinyMarginBottom"/>
</VBox>
```

**Size-Specific Classes**:
```xml
<FlexBox 
    class="sapUiResponsiveMargin"
    direction="Row"
    wrap="Wrap">
    <Button text="Button 1"/>
    <Button text="Button 2"/>
</FlexBox>
```

### Best Practices

**Mobile Optimization**:
- ✅ Use sap.m controls (built-in mobile support)
- ✅ Apply sapUiSizeCompact CSS class for consistent sizing
- ✅ Test on actual devices (touch, gestures)
- ✅ Use ActionSheet instead of Menu on mobile
- ✅ Prefer Carousel for image galleries
- ✅ Implement PullToRefresh for data refresh

**Responsive Design**:
- ✅ Load sap.m library first
- ✅ Use SplitApp for master-detail on mobile
- ✅ Test both portrait and landscape
- ✅ Handle orientation changes
- ✅ Use sap.ui.Device API for conditional logic

**Performance**:
- ✅ Lazy load images in Carousel
- ✅ Use growing lists for long data
- ✅ Minimize animations on low-end devices
- ❌ Don't load desktop-only controls on mobile

---

## 9. ProcessFlow (sap.suite.ui.commons)

### Overview

**ProcessFlow** visualizes business processes as flowcharts with nodes, lanes, and connections for workflow status tracking (documents, approvals, orders, etc.).

### Basic Configuration

```xml
<processflow:ProcessFlow 
    id="processFlow"
    lanes="{/lanes}"
    foldedCorners="true"
    scrollable="true"
    wheelZoomable="true">
</processflow:ProcessFlow>
```

### Data Model Structure

```javascript
var oModel = new JSONModel({
    lanes: [
        {
            laneId: "lane1",
            iconUri: "sap-icon://cart",
            text: "Order Processing",
            position: 0,
            children: [
                {
                    nodeId: "node1",
                    laneId: "lane1",
                    title: "Order Created",
                    state: "Positive",  // Completed
                    children: [2]
                },
                {
                    nodeId: "node2",
                    laneId: "lane1",
                    title: "Payment Verified",
                    state: "Positive",
                    children: [3]
                },
                {
                    nodeId: "node3",
                    laneId: "lane1",
                    title: "Shipped",
                    state: "Planned",  // Not started
                    children: []
                }
            ]
        },
        {
            laneId: "lane2",
            iconUri: "sap-icon://shipping-status",
            text: "Fulfillment",
            position: 1,
            children: [
                {
                    nodeId: "node4",
                    laneId: "lane2",
                    title: "Pick Items",
                    state: "Neutral",  // In progress
                    children: [5]
                },
                {
                    nodeId: "node5",
                    laneId: "lane2",
                    title: "Pack",
                    state: "Planned",
                    children: []
                }
            ]
        }
    ]
});

this.getView().setModel(oModel);
```

### Node States (Semantic Colors)

| State | Meaning | Color | Icon |
|-------|---------|-------|------|
| **Positive** | Completed successfully | Green | ✓ |
| **Neutral** | In progress | Blue | ⟳ |
| **Planned** | Not started yet | Gray | ○ |
| **Negative** | Failed/rejected | Red | ✗ |
| **Critical** | Warning/attention needed | Orange | ⚠ |

### Controller Implementation

```javascript
onInit: function() {
    // Load process data
    var oData = this.loadProcessData();
    var oModel = new JSONModel(oData);
    this.getView().setModel(oModel);
    
    // Handle node click
    this.byId("processFlow").attachNodePress(this.onNodePress, this);
},

onNodePress: function(oEvent) {
    var oNode = oEvent.getParameters();
    MessageBox.information(
        "Node: " + oNode.getNodeId() + "\n" +
        "Title: " + oNode.getTitle() + "\n" +
        "State: " + oNode.getState()
    );
    
    // Could open detail dialog, navigate to object, etc.
},

loadProcessData: function() {
    // In real app: Load from OData
    // return this.getView().getModel().read("/ProcessFlowData");
    return { lanes: [...] };
}
```

### Properties & Configuration

**ProcessFlow Properties**:
- `lanes`: Main aggregation for lane/node data
- `foldedCorners`: Show folded corner on nodes
- `scrollable`: Enable scrolling for large flows
- `wheelZoomable`: Enable zoom with mouse wheel
- `showLabels`: Show/hide node labels

**Node Properties**:
- `nodeId`: Unique identifier
- `laneId`: Parent lane identifier
- `title`: Display text
- `state`: Status (Positive, Neutral, Planned, Negative, Critical)
- `children`: Array of child node IDs for connections
- `texts`: Additional text lines
- `stateText`: Custom status text

**Lane Properties**:
- `laneId`: Unique identifier
- `text`: Lane title
- `iconUri`: Icon for lane header
- `position`: Display order (0, 1, 2, ...)
- `children`: Array of nodes in this lane

### OData Integration

```javascript
// Bind to OData service
var oModel = this.getOwnerComponent().getModel();

// Transform OData to ProcessFlow format
oModel.read("/WorkflowItems", {
    success: function(oData) {
        var processData = this.transformToProcessFlow(oData.results);
        var oProcessModel = new JSONModel(processData);
        this.getView().setModel(oProcessModel, "process");
    }.bind(this)
});

transformToProcessFlow: function(aItems) {
    // Group by lane, create node structure
    var lanes = {};
    aItems.forEach(function(item) {
        if (!lanes[item.Stage]) {
            lanes[item.Stage] = {
                laneId: item.Stage,
                text: item.StageName,
                position: item.StageOrder,
                children: []
            };
        }
        lanes[item.Stage].children.push({
            nodeId: item.Id,
            laneId: item.Stage,
            title: item.Description,
            state: this.mapStatus(item.Status),
            children: item.NextSteps.split(',')
        });
    }.bind(this));
    
    return { lanes: Object.values(lanes) };
}
```

### Use Cases

**Order-to-Cash Process**:
- Lanes: Sales, Fulfillment, Finance
- Nodes: Quote → Order → Pick → Ship → Invoice → Payment
- Status: Track order progress in real-time

**Approval Workflows**:
- Lanes: Requester, Manager, Finance, Executive
- Nodes: Request → Review → Approve → Execute
- Status: Show who approved and who's pending

**Manufacturing Process**:
- Lanes: Planning, Production, Quality, Shipping
- Nodes: Design → Build → Test → Package → Ship
- Status: Track production status by stage

**Document Processing**:
- Lanes: Capture, Validate, Approve, Archive
- Nodes: Scan → Extract → Verify → Sign → Store
- Status: Document workflow progress

### Best Practices

**Layout**:
- ✅ 3-5 lanes maximum for readability
- ✅ 5-10 nodes per lane (use scrolling for more)
- ✅ Logical left-to-right flow
- ✅ Clear lane titles with icons

**Data**:
- ✅ Load from OData for real-time status
- ✅ Refresh on interval for live tracking
- ✅ Use meaningful node titles (verb + object)
- ✅ Add stateText for detailed status

**Interaction**:
- ✅ Handle nodePress for details
- ✅ Enable zoom for complex flows
- ✅ Provide legend for states
- ✅ Add toolbar with refresh/export

**Performance**:
- ✅ Limit initial node count (< 100)
- ✅ Use lazy loading for large processes
- ✅ Cache transformed data
- ✅ Debounce updateModel() calls

**Accessibility**:
- ✅ Use semantic colors (not color alone)
- ✅ Add ARIA labels
- ✅ Support keyboard navigation
- ✅ Provide text alternatives

### Integration with SAP S/4HANA

```javascript
// Example: Purchase Order process from S/4HANA
loadPOProcess: function(poNumber) {
    var oModel = this.getView().getModel();
    
    oModel.callFunction("/GetPurchaseOrderFlow", {
        method: "GET",
        urlParameters: {
            PurchaseOrder: poNumber
        },
        success: function(oData) {
            // Transform S/4HANA data to ProcessFlow format
            var processData = {
                lanes: [
                    {
                        laneId: "procurement",
                        text: "Procurement",
                        children: oData.ProcurementSteps.map(step => ({
                            nodeId: step.StepId,
                            title: step.Description,
                            state: step.Status
                        }))
                    },
                    // Additional lanes...
                ]
            };
            
            this.getView().setModel(new JSONModel(processData), "process");
        }.bind(this)
    });
}
```

### Comparison with Timeline

| Feature | ProcessFlow | Timeline |
|---------|-------------|----------|
| **Purpose** | Multi-lane workflow status | Chronological event list |
| **Layout** | Horizontal lanes + nodes | Vertical timeline |
| **Connections** | Arrows between nodes | No connections |
| **Use Case** | Business process tracking | Event history |
| **Interaction** | Click nodes for details | Select items |
| **Best For** | Workflows with branches | Linear event sequences |

---

## Summary - Batch 5

**Topics Covered**: 10 specialized library topics (updated)
- Smart Controls (metadata-driven UI generation)
- Visualization Charts (VizFrame, 15+ chart types)
- Calendar & Date Controls (Calendar, DateRangePicker, PlanningCalendar)
- File Upload Controls (FileUploader, UploadSet, UploadCollection)
- Suite Controls (ChartContainer, Timeline)
- RichTextEditor (WYSIWYG text editing)
- Tree Controls (TreeTable for hierarchies)
- Mobile-Specific Controls (ActionSheet, Carousel, Slider, PullToRefresh)

**Key Takeaways**:
- **Smart Controls**: OData + annotations = minimal coding
- **VizFrame**: 15+ chart types, dynamic switching, customizable
- **Calendar**: Three controls for different use cases (Calendar, DateRangePicker, PlanningCalendar)
- **File Upload**: UploadSet recommended for modern apps with drag & drop
- **Suite**: ChartContainer for dashboards, Timeline for chronological events
- **RichTextEditor**: TinyMCE-powered, desktop only, custom toolbar support
- **TreeTable**: Hierarchical data, requires specific model structure
- **Mobile**: sap.m library with touch gestures, responsive behavior

**Developer Impact**: Specialized controls for advanced use cases (analytics, scheduling, file management)

**Total Coverage (All 5 Batches)**: ~98% of SAPUI5 development patterns including specialized libraries

**Documentation Size**: 395 KB total (335 KB + 60 KB Batch 5)