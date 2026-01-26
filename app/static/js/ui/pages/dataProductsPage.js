/**
 * Data Products Page Module
 * 
 * Handles the main data products listing and details dialogs.
 * Displays data product tiles and manages table exploration.
 * 
 * @author P2P Development Team
 * @version 2.0.0
 */

/**
 * Initialize data products on page load
 */
export async function initializeDataProducts() {
    // Load data products automatically
    await loadDataProducts();
}

/**
 * Load data products from selected source
 */
export async function loadDataProducts() {
    const tilesContainer = sap.ui.getCore().byId("tilesContainer");
    const loadingText = sap.ui.getCore().byId("loadingStatus");
    
    if (!tilesContainer || !loadingText) {
        console.error("Required UI elements not found");
        return;
    }
    
    // Get selected source from localStorage (default: sqlite)
    const selectedSource = localStorage.getItem('selectedDataSource') || 'sqlite';
    const sourceName = selectedSource === 'hana' ? 'HANA Cloud' : 'Local SQLite';
    
    loadingText.setText(`Loading data products from ${sourceName}...`);
    
    try {
        // Load from selected source
        const response = await fetch(`/api/data-products?source=${selectedSource}`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || "Failed to load data products");
        }
        
        const dataProducts = data.data_products || [];
        
        // Update loading text
        loadingText.setText(`Found ${dataProducts.length} data products from ${sourceName}`);
        
        // Clear tiles
        tilesContainer.destroyItems();
        
        // Create tiles for each data product
        dataProducts.forEach(function(dp) {
            tilesContainer.addItem(createDataProductTile(dp));
        });
        
        if (dataProducts.length === 0) {
            loadingText.setText("No data products found in " + sourceName);
        }
        
    } catch (error) {
        console.error("Error loading data products:", error);
        loadingText.setText("Error loading data products: " + error.message);
        sap.m.MessageToast.show("Failed to load data products");
    }
}

/**
 * Create a tile for a data product (Fiori-compliant design)
 */
function createDataProductTile(dp) {
    // Extract human-readable display name
    let displayName = dp.display_name || dp.displayName || dp.productName || 'Unknown Product';
    
    // Build business-friendly subtitle (SAP S/4HANA v1)
    const version = dp.version || 'v1';
    const subtitle = `SAP S/4HANA ${version}`;
    
    // Get table count
    const tableCount = dp.entity_count || dp.tableCount || 0;
    
    // Build footer text with source system (Option C: Footer Context)
    const sourceSystem = dp.source_system || 'SAP Data Product';
    let footerText = sourceSystem;
    
    // Optionally add update date if available
    if (dp.created_at) {
        try {
            const date = new Date(dp.created_at);
            const monthYear = date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
            footerText = `${sourceSystem} • ${monthYear}`;
        } catch (e) {
            footerText = sourceSystem;
        }
    }
    
    // Create Fiori-compliant tile with business focus
    const tile = new sap.m.GenericTile({
        header: displayName,
        subheader: subtitle,
        frameType: "TwoByOne",
        press: function() {
            showDataProductDetails(dp);
        },
        tileContent: [
            new sap.m.TileContent({
                footer: footerText,
                content: [
                    new sap.m.NumericContent({
                        value: tableCount,
                        valueColor: tableCount > 0 ? "Good" : "Neutral",
                        icon: "sap-icon://BusinessSuiteInAppSymbols/icon-data-access",
                        withMargin: false,
                        scale: "Tables",
                        iconDescription: "Data Product Tables"
                    })
                ]
            })
        ]
    });
    
    tile.addStyleClass("sapUiTinyMargin");
    return tile;
}

/**
 * Show data product details dialog
 * FIX: Properly handles refresh button by reopening dialog
 */
export async function showDataProductDetails(dp) {
    const schemaName = dp.schemaName || dp.productName || dp.name;
    const displayName = dp.displayName || dp.productName || schemaName;
    
    // Create dialog IMMEDIATELY (with loading indicator)
    const oDialog = new sap.m.Dialog({
        title: displayName,
        contentWidth: "90%",
        contentHeight: "80%",
        resizable: true,
        draggable: true,
        content: [
            new sap.m.VBox({
                items: [
                    createDataProductHeader(dp, schemaName),
                    createProductInfo(dp, displayName),
                    createTablesSection(),
                    createTablesTable()
                ]
            }).addStyleClass("sapUiSmallMargin")
        ],
        endButton: new sap.m.Button({
            text: "Close",
            press: function() {
                oDialog.close();
            }
        }),
        afterClose: function() {
            oDialog.destroy();
        }
    });
    
    // Open dialog IMMEDIATELY
    oDialog.open();
    
    // Load tables data asynchronously
    await loadTablesData(schemaName);
}

/**
 * Create header with breadcrumb and refresh button
 * FIX: Refresh button now properly reloads the dialog
 */
function createDataProductHeader(dp, schemaName) {
    return new sap.m.HBox({
        justifyContent: "SpaceBetween",
        alignItems: "Center",
        items: [
            new sap.m.Breadcrumbs({
                links: [
                    new sap.m.Link({ text: "Data Products" }),
                    new sap.m.Link({ text: dp.productName || schemaName })
                ]
            }),
            new sap.m.Button({
                icon: "sap-icon://refresh",
                text: "Refresh",
                press: async function() {
                    // FIX: Close current dialog and reopen (reload data)
                    const oDialog = this.getParent().getParent().getParent();
                    oDialog.close();
                    await showDataProductDetails(dp);
                }
            })
        ]
    }).addStyleClass("sapUiSmallMarginBottom");
}

/**
 * Create product information section
 */
function createProductInfo(dp, displayName) {
    return new sap.m.VBox({
        items: [
            new sap.m.Title({
                text: displayName,
                level: "H1"
            }),
            new sap.m.Text({
                text: dp.namespace || "sap"
            }).addStyleClass("sapUiSmallMarginBottom")
        ]
    });
}

/**
 * Create tables section header
 */
function createTablesSection() {
    return new sap.m.Title({
        text: "TABLES",
        level: "H2"
    }).addStyleClass("sapUiMediumMarginTop");
}

/**
 * Create tables table (empty, will be populated)
 */
function createTablesTable() {
    return new sap.m.Table({
        id: "tablesTable",
        growing: true,
        growingThreshold: 20,
        busy: true,
        busyIndicatorDelay: 0,
        columns: [
            new sap.m.Column({
                header: new sap.m.Label({ text: "Table Name" }),
                minScreenWidth: "Tablet",
                demandPopin: true
            }),
            new sap.m.Column({
                header: new sap.m.Label({ text: "Type" }),
                width: "150px",
                hAlign: "Center"
            }),
            new sap.m.Column({
                header: new sap.m.Label({ text: "Records" }),
                width: "150px",
                hAlign: "Right"
            }),
            new sap.m.Column({
                header: new sap.m.Label({ text: "Actions" }),
                width: "250px",
                hAlign: "Center"
            })
        ]
    });
}

/**
 * Load tables data for a schema
 */
async function loadTablesData(schemaName) {
    try {
        const selectedSource = localStorage.getItem('selectedDataSource') || 'sqlite';
        const response = await fetch(`/api/data-products/${schemaName}/tables?source=${selectedSource}`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || "Failed to load tables");
        }
        
        const tables = data.tables || [];
        
        // Update the table with data
        const oTable = sap.ui.getCore().byId("tablesTable");
        if (oTable) {
            oTable.setBusy(false);
            
            tables.forEach(function(table) {
                oTable.addItem(createTableItem(schemaName, table));
            });
            
            if (tables.length === 0) {
                oTable.setNoData(new sap.m.Text({ 
                    text: "No tables found in this data product" 
                }));
            }
        }
        
    } catch (error) {
        const oTable = sap.ui.getCore().byId("tablesTable");
        if (oTable) {
            oTable.setBusy(false);
            oTable.setNoData(new sap.m.Text({ 
                text: "Error loading tables: " + error.message 
            }));
        }
        sap.m.MessageToast.show("Error loading tables: " + error.message);
    }
}

/**
 * Create a table list item
 */
function createTableItem(schemaName, table) {
    const tableName = table.TABLE_NAME || table.name;
    const tableType = table.TABLE_TYPE || table.type || "VIRTUAL";
    const recordCount = table.RECORD_COUNT || table.record_count;
    
    // Handle null record count (performance optimization - counts on demand)
    const recordCountText = recordCount !== null && recordCount !== undefined 
        ? recordCount.toLocaleString() 
        : "-";
    
    return new sap.m.ColumnListItem({
        cells: [
            new sap.m.Text({ text: tableName }),
            new sap.m.ObjectStatus({
                text: tableType,
                state: "Information"
            }),
            new sap.m.Text({ 
                text: recordCountText,
                textAlign: "End"
            }),
            new sap.m.HBox({
                justifyContent: "Center",
                items: [
                    new sap.m.Button({
                        icon: "sap-icon://list",
                        text: "Structure",
                        press: function() {
                            showTableStructure(schemaName, tableName);
                        }
                    }).addStyleClass("sapUiTinyMarginEnd"),
                    new sap.m.Button({
                        icon: "sap-icon://table-view",
                        text: "View Data",
                        type: "Emphasized",
                        press: function() {
                            showTableData(schemaName, tableName);
                        }
                    })
                ]
            })
        ]
    });
}

/**
 * Show table structure (placeholder)
 */
function showTableStructure(schemaName, tableName) {
    sap.m.MessageToast.show("Loading structure for " + tableName + "...");
    // TODO: Implement table structure view
}

/**
 * Show table data (placeholder)
 */
function showTableData(schemaName, tableName) {
    sap.m.MessageToast.show("Loading data for " + tableName + "...");
    // TODO: Implement table data view
}