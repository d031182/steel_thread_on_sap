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
        const response = await fetch(`/api/data-products/?source=${selectedSource}`);
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
        
        // Extract actual error message from error object or string
        let errorMsg = "Unknown error";
        if (error.message) {
            errorMsg = error.message;
        } else if (typeof error === 'string') {
            errorMsg = error;
        } else if (error.error) {
            // Handle API error response format
            errorMsg = error.error.message || error.error || JSON.stringify(error.error);
        }
        
        loadingText.setText("Error loading data products: " + errorMsg);
        sap.m.MessageToast.show("Failed to load data products: " + errorMsg);
    }
}

/**
 * Create a tile for a data product (Fiori-compliant design)
 */
function createDataProductTile(dp) {
    // Extract human-readable display name
    let displayName = dp.display_name || dp.displayName || dp.productName || 'Unknown Product';
    
    // Build ORD ID for subtitle (Technical reference)
    const namespace = dp.namespace || 'sap.s4com';
    const productName = dp.productName || dp.name || 'Unknown';
    const version = dp.version || 'v1';
    const ordId = `${namespace}:dataProduct:${productName}:${version}`;
    
    // Get table count
    const tableCount = dp.entity_count || dp.tableCount || 0;
    
    // Footer shows source system context
    const sourceSystem = dp.source_system || 'SAP Data Product';
    const footerText = sourceSystem;
    
    // Create Fiori-compliant tile with ORD ID subtitle
    const tile = new sap.m.GenericTile({
        header: displayName,
        subheader: ordId,
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
 */
export async function showDataProductDetails(dp) {
    const schemaName = dp.name || dp.schemaName || dp.productName;
    const displayName = dp.display_name || dp.displayName || dp.productName || 'Data Product';
    
    // Generate unique ID for this dialog's table
    const uniqueTableId = "tablesTable_" + Date.now();
    
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
                    createTablesTable(uniqueTableId)
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
    await loadTablesData(schemaName, uniqueTableId);
}

/**
 * Create header with breadcrumb and refresh button
 */
function createDataProductHeader(dp, schemaName) {
    const displayName = dp.display_name || dp.displayName || dp.productName || 'Data Product';
    
    return new sap.m.HBox({
        justifyContent: "SpaceBetween",
        alignItems: "Center",
        items: [
            new sap.m.Breadcrumbs({
                links: [
                    new sap.m.Link({ text: "Data Products" }),
                    new sap.m.Link({ text: displayName })
                ]
            }),
            new sap.m.Button({
                icon: "sap-icon://refresh",
                text: "Refresh",
                press: async function() {
                    // Close current dialog and reopen (reload data)
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
    // Build ORD ID for display
    const namespace = dp.namespace || 'sap.s4com';
    const productName = dp.productName || dp.name || 'Unknown';
    const version = dp.version || 'v1';
    const ordId = `${namespace}:dataProduct:${productName}:${version}`;
    
    return new sap.m.VBox({
        items: [
            new sap.m.Title({
                text: displayName,
                level: "H1"
            }),
            new sap.m.Text({
                text: ordId
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
function createTablesTable(uniqueId) {
    return new sap.m.Table({
        id: uniqueId,
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
async function loadTablesData(schemaName, tableId) {
    try {
        const selectedSource = localStorage.getItem('selectedDataSource') || 'sqlite';
        const response = await fetch(`/api/data-products/${schemaName}/tables?source=${selectedSource}`);
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || "Failed to load tables");
        }
        
        const tables = data.tables || [];
        
        // Get table by ID
        const oTable = sap.ui.getCore().byId(tableId);
        
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
        } else {
            console.error("Could not find table with ID:", tableId);
        }
        
    } catch (error) {
        console.error("Error loading tables:", error);
        const oTable = sap.ui.getCore().byId(tableId);
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
    
    // Extract just the table name (remove schema prefix if present)
    let displayName = tableName;
    if (tableName.includes('.')) {
        displayName = tableName.split('.').pop();
    }
    
    // Handle null record count
    const recordCountText = recordCount !== null && recordCount !== undefined 
        ? recordCount.toLocaleString() 
        : "-";
    
    return new sap.m.ColumnListItem({
        cells: [
            new sap.m.Text({ text: displayName }),
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
 * Show table structure in a dialog
 */
async function showTableStructure(schemaName, tableName) {
    let displayName = tableName;
    if (tableName.includes('.')) {
        displayName = tableName.split('.').pop();
    }
    
    const uniqueId = "structureTable_" + Date.now();
    
    const oDialog = new sap.m.Dialog({
        title: `${displayName} - Structure`,
        contentWidth: "800px",
        contentHeight: "600px",
        resizable: true,
        draggable: true,
        content: [
            new sap.m.VBox({
                items: [
                    new sap.m.Text({
                        text: "Loading table structure..."
                    }).addStyleClass("sapUiSmallMargin"),
                    new sap.m.Table({
                        id: uniqueId,
                        growing: false,
                        busy: true,
                        busyIndicatorDelay: 0,
                        columns: [
                            new sap.m.Column({
                                header: new sap.m.Label({ text: "Column Name" }),
                                width: "200px"
                            }),
                            new sap.m.Column({
                                header: new sap.m.Label({ text: "Data Type" }),
                                width: "120px"
                            }),
                            new sap.m.Column({
                                header: new sap.m.Label({ text: "Length" }),
                                width: "80px",
                                hAlign: "Right"
                            }),
                            new sap.m.Column({
                                header: new sap.m.Label({ text: "Nullable" }),
                                width: "80px",
                                hAlign: "Center"
                            }),
                            new sap.m.Column({
                                header: new sap.m.Label({ text: "Foreign Key" }),
                                width: "250px"
                            })
                        ]
                    })
                ]
            })
        ],
        beginButton: new sap.m.Button({
            text: "Close",
            press: function() {
                oDialog.close();
            }
        }),
        afterClose: function() {
            oDialog.destroy();
        }
    });
    
    oDialog.open();
    
    try {
        const selectedSource = localStorage.getItem('selectedDataSource') || 'sqlite';
        const response = await fetch(
            `/api/data-products/${schemaName}/${tableName}/structure?source=${selectedSource}`
        );
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error?.message || "Failed to load table structure");
        }
        
        const columns = data.columns || [];
        
        const oText = oDialog.getContent()[0].getItems()[0];
        oText.setText(`${columns.length} columns in ${displayName}`);
        
        const oTable = sap.ui.getCore().byId(uniqueId);
        oTable.setBusy(false);
        
        columns.forEach(function(col) {
            const columnName = col.name || col.COLUMN_NAME;
            const dataType = col.data_type || col.DATA_TYPE_NAME;
            const length = col.length || col.LENGTH;
            const nullable = col.nullable !== undefined ? col.nullable : col.IS_NULLABLE === 'TRUE';
            const foreignKey = col.foreignKey || col.FOREIGN_KEY;
            
            oTable.addItem(new sap.m.ColumnListItem({
                cells: [
                    new sap.m.Text({ text: columnName }),
                    new sap.m.Text({ text: dataType }),
                    new sap.m.Text({ 
                        text: length !== null && length !== undefined ? String(length) : "-",
                        textAlign: "End"
                    }),
                    new sap.m.Text({ 
                        text: nullable ? "Yes" : "No",
                        textAlign: "Center"
                    }),
                    new sap.m.Text({ 
                        text: foreignKey || "-"
                    })
                ]
            }));
        });
        
        if (columns.length === 0) {
            oTable.setNoData(new sap.m.Text({ text: "No columns found" }));
        }
        
    } catch (error) {
        console.error("Error loading table structure:", error);
        
        const oTable = sap.ui.getCore().byId(uniqueId);
        if (oTable) {
            oTable.setBusy(false);
            oTable.setNoData(new sap.m.Text({ 
                text: "Error: " + error.message 
            }));
        }
        sap.m.MessageToast.show("Error loading structure: " + error.message);
    }
}

/**
 * Show table data in a dialog
 */
async function showTableData(schemaName, tableName) {
    const uniqueDataTextId = "dataStatusText_" + Date.now();
    const uniqueDataTableId = "tableDataTable_" + Date.now();
    
    const oDialog = new sap.m.Dialog({
        title: `${tableName} - Sample Data`,
        contentWidth: "95%",
        contentHeight: "90%",
        resizable: true,
        draggable: true,
        content: [
            new sap.m.VBox({
                items: [
                    new sap.m.Text({
                        id: uniqueDataTextId,
                        text: "Loading first 100 records..."
                    }).addStyleClass("sapUiSmallMargin"),
                    new sap.m.Table({
                        id: uniqueDataTableId,
                        growing: false,
                        busy: true,
                        busyIndicatorDelay: 0,
                        mode: "None"
                    })
                ]
            })
        ],
        beginButton: new sap.m.Button({
            text: "Close",
            press: function() {
                oDialog.close();
            }
        }),
        afterClose: function() {
            oDialog.destroy();
        }
    });
    
    oDialog.open();
    
    try {
        const selectedSource = localStorage.getItem('selectedDataSource') || 'sqlite';
        const response = await fetch(
            `/api/data-products/${schemaName}/${tableName}/query?source=${selectedSource}`,
            {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    limit: 100,
                    offset: 0
                })
            }
        );
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error?.message || "Failed to load table data");
        }
        
        const rows = data.rows || [];
        const columns = data.columns || [];
        const totalCount = data.totalCount || 0;
        
        const essentialColumns = columns.slice(0, 10);
        
        const oText = sap.ui.getCore().byId(uniqueDataTextId);
        if (oText) {
            oText.setText(`Showing ${rows.length} of ${totalCount.toLocaleString()} records (first ${essentialColumns.length} columns)`);
        }
        
        const oTable = sap.ui.getCore().byId(uniqueDataTableId);
        if (oTable) {
            oTable.setBusy(false);
            
            essentialColumns.forEach(function(col) {
                oTable.addColumn(new sap.m.Column({
                    header: new sap.m.Label({ text: col.name }),
                    visible: true,
                    demandPopin: false
                }));
            });
            
            rows.forEach(function(row) {
                const cells = essentialColumns.map(function(col) {
                    const value = row[col.name];
                    return new sap.m.Text({ 
                        text: value !== null && value !== undefined ? String(value) : "-"
                    });
                });
                
                oTable.addItem(new sap.m.ColumnListItem({
                    cells: cells
                }));
            });
            
            if (rows.length === 0) {
                oTable.setNoData(new sap.m.Text({ text: "No data available" }));
            }
        }
        
    } catch (error) {
        const oTable = sap.ui.getCore().byId(uniqueDataTableId);
        if (oTable) {
            oTable.setBusy(false);
            oTable.setNoData(new sap.m.Text({ text: "Error: " + error.message }));
        }
        sap.m.MessageToast.show("Error loading data: " + error.message);
    }
}