/**
 * Data Products V2 Page View
 * ===========================
 * 
 * Tile-based data products browser with HANA/SQLite source switching
 * Based on proven working V1 pattern, adapted for App V2 architecture
 * 
 * @author P2P Development Team
 * @version 2.3.1 (Based on Working V1)
 */

(function() {
    'use strict';

    /**
     * Create Data Products V2 Page with Tiles
     * 
     * @param {Array} dataProducts - List of data products
     * @param {String} currentSource - Current data source ('hana' or 'sqlite')
     * @param {Object} callbacks - Event callbacks
     * @returns {sap.m.Page} SAPUI5 Page control
     */
    window.createDataProductsV2Page = function(dataProducts, currentSource, callbacks) {
        
        callbacks = callbacks || {};
        currentSource = currentSource || 'sqlite';
        
        // Source switcher dropdown
        const sourceSelect = new sap.m.Select({
            id: 'dataProductsSourceSelect',
            selectedKey: currentSource,
            items: [
                new sap.ui.core.Item({ key: 'sqlite', text: 'SQLite (Local)' }),
                new sap.ui.core.Item({ key: 'hana', text: 'HANA Cloud' })
            ],
            change: function(event) {
                const newSource = event.getParameter('selectedItem').getKey();
                if (callbacks.onSourceChange) {
                    callbacks.onSourceChange(newSource);
                }
            }
        });
        
        // Header bar with source switcher and refresh
        const headerBar = new sap.m.Bar({
            contentLeft: [
                new sap.m.Title({
                    text: "Data Products",
                    level: "H2"
                })
            ],
            contentRight: [
                sourceSelect,
                new sap.m.Button({
                    icon: "sap-icon://refresh",
                    text: "Refresh",
                    press: function() {
                        if (callbacks.onRefresh) {
                            callbacks.onRefresh();
                        }
                    }
                }).addStyleClass('sapUiTinyMarginBegin')
            ]
        });

        // Status bar with count and source
        const sourceName = currentSource === 'hana' ? 'HANA Cloud' : 'SQLite';
        const statusText = new sap.m.Text({
            id: 'dataProductsStatusText',
            text: `Found ${dataProducts.length} data products (Source: ${sourceName})`
        }).addStyleClass('sapUiSmallMargin');

        // Create FlexBox container for tiles (simpler, more reliable)
        const tileContainer = new sap.m.FlexBox({
            id: 'dataProductsTileContainer',
            wrap: 'Wrap',
            alignItems: 'Start'
        });
        
        // Add tiles
        dataProducts.forEach(dp => {
            tileContainer.addItem(createProductTile(dp, callbacks));
        });

        // Main page
        const page = new sap.m.Page({
            customHeader: headerBar,
            content: [
                statusText,
                tileContainer
            ]
        });

        // Add refresh method for module to call
        page.refresh = function(updatedProducts, updatedSource) {
            const source = updatedSource || currentSource;
            const srcName = source === 'hana' ? 'HANA Cloud' : 'SQLite';
            
            // Update status text
            const status = sap.ui.getCore().byId('dataProductsStatusText');
            if (status) {
                status.setText(`Found ${updatedProducts.length} data products (Source: ${srcName})`);
            }
            
            // Update source select
            const select = sap.ui.getCore().byId('dataProductsSourceSelect');
            if (select) {
                select.setSelectedKey(source);
            }
            
            // Update tiles (use destroyItems, not destroyTiles!)
            const container = sap.ui.getCore().byId('dataProductsTileContainer');
            if (container) {
                container.destroyItems();
                updatedProducts.forEach(dp => {
                    container.addItem(createProductTile(dp, callbacks));
                });
            }
        };

        return page;
    };

    /**
     * Create a single product tile (V1 proven pattern)
     */
    function createProductTile(dp, callbacks) {
        // Extract display name
        const displayName = dp.display_name || dp.displayName || dp.product_name || dp.productName || 'Unknown Product';
        
        // Build ORD ID
        const namespace = dp.namespace || 'sap.s4com';
        const productName = dp.product_name || dp.productName || dp.name || 'unknown';
        const version = dp.version || 'v1';
        const ordId = `${namespace}:dataProduct:${productName}:${version}`;
        
        // Get table count
        const tableCount = dp.table_count || dp.entity_count || dp.tableCount || 0;
        
        // Footer shows source context
        const sourceSystem = dp.source_system || 'SAP Data Product';
        
        const tile = new sap.m.GenericTile({
            header: displayName,
            subheader: ordId,
            frameType: "TwoByOne",
            press: function() {
                if (callbacks.onProductClick) {
                    callbacks.onProductClick(dp);
                }
            },
            tileContent: [
                new sap.m.TileContent({
                    footer: sourceSystem,
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
     * Show data product details dialog with tables
     */
    window.showDataProductDetailsV2 = function(dp, dataSource) {
        const schemaName = dp.product_name || dp.name || dp.schemaName || dp.productName;
        const displayName = dp.display_name || dp.displayName || dp.product_name || dp.productName || 'Data Product';
        
        const uniqueTableId = "tablesTable_" + Date.now();
        
        const oDialog = new sap.m.Dialog({
            title: displayName,
            contentWidth: "90%",
            contentHeight: "80%",
            resizable: true,
            draggable: true,
            content: [
                new sap.m.VBox({
                    items: [
                        new sap.m.Text({
                            text: `Loading tables for ${displayName}...`
                        }).addStyleClass('sapUiSmallMargin'),
                        new sap.m.Table({
                            id: uniqueTableId,
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
                        })
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
        
        oDialog.open();
        loadTablesDataV2(schemaName, uniqueTableId, dataSource);
    };

    /**
     * Load tables data asynchronously
     */
    async function loadTablesDataV2(schemaName, tableId, dataSource) {
        try {
            const tables = await dataSource.getTables(schemaName);
            
            const oTable = sap.ui.getCore().byId(tableId);
            if (!oTable) {
                console.error("Table not found:", tableId);
                return;
            }
            
            oTable.setBusy(false);
            
            tables.forEach(table => {
                const tableName = table.table_name || table.TABLE_NAME || table.name;
                const displayName = tableName.includes('.') ? tableName.split('.').pop() : tableName;
                const tableType = table.TABLE_TYPE || table.type || "VIRTUAL";
                const recordCount = table.record_count || table.RECORD_COUNT;
                const recordCountText = recordCount !== null && recordCount !== undefined 
                    ? recordCount.toLocaleString() 
                    : "-";
                
                oTable.addItem(new sap.m.ColumnListItem({
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
                                        showTableStructureV2(schemaName, tableName, dataSource);
                                    }
                                }).addStyleClass("sapUiTinyMarginEnd"),
                                new sap.m.Button({
                                    icon: "sap-icon://table-view",
                                    text: "View Data",
                                    type: "Emphasized",
                                    press: function() {
                                        showTableDataV2(schemaName, tableName, dataSource);
                                    }
                                })
                            ]
                        })
                    ]
                }));
            });
            
            if (tables.length === 0) {
                oTable.setNoData(new sap.m.Text({ 
                    text: "No tables found in this data product" 
                }));
            }
            
        } catch (error) {
            console.error('Error loading tables:', error);
            const oTable = sap.ui.getCore().byId(tableId);
            if (oTable) {
                oTable.setBusy(false);
                oTable.setNoData(new sap.m.Text({ 
                    text: "Error: " + error.message 
                }));
            }
            sap.m.MessageToast.show('Error loading tables: ' + error.message);
        }
    }

    /**
     * Show table structure dialog
     */
    async function showTableStructureV2(schemaName, tableName, dataSource) {
        const displayName = tableName.includes('.') ? tableName.split('.').pop() : tableName;
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
                                    width: "180px"
                                }),
                                new sap.m.Column({
                                    header: new sap.m.Label({ text: "Data Type" }),
                                    width: "100px"
                                }),
                                new sap.m.Column({
                                    header: new sap.m.Label({ text: "Length" }),
                                    width: "70px",
                                    hAlign: "Right"
                                }),
                                new sap.m.Column({
                                    header: new sap.m.Label({ text: "Nullable" }),
                                    width: "70px",
                                    hAlign: "Center"
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
            const columns = await dataSource.getTableStructure(schemaName, tableName);
            
            const oText = oDialog.getContent()[0].getItems()[0];
            oText.setText(`${columns.length} columns in ${displayName}`);
            
            const oTable = sap.ui.getCore().byId(uniqueId);
            oTable.setBusy(false);
            
            columns.forEach(col => {
                const columnName = col.name || col.column_name || col.COLUMN_NAME;
                const dataType = col.data_type || col.DATA_TYPE_NAME;
                const length = col.length || col.LENGTH;
                const nullable = col.nullable !== undefined ? col.nullable : col.is_nullable;
                
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
     * Show table data dialog
     */
    async function showTableDataV2(schemaName, tableName, dataSource) {
        const displayName = tableName.includes('.') ? tableName.split('.').pop() : tableName;
        const uniqueDataTextId = "dataStatusText_" + Date.now();
        const uniqueDataTableId = "tableDataTable_" + Date.now();
        
        const oDialog = new sap.m.Dialog({
            title: `${displayName} - Sample Data`,
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
            const result = await dataSource.queryTable(schemaName, tableName, 100, 0);
            
            const rows = result.rows || [];
            const columns = result.columns || [];
            const totalCount = result.totalCount || 0;
            
            const essentialColumns = columns.slice(0, 10);
            
            const oText = sap.ui.getCore().byId(uniqueDataTextId);
            if (oText) {
                oText.setText(
                    `Showing ${rows.length} of ${totalCount.toLocaleString()} records ` +
                    `(first ${essentialColumns.length} columns)`
                );
            }
            
            const oTable = sap.ui.getCore().byId(uniqueDataTableId);
            if (oTable) {
                oTable.setBusy(false);
                
                essentialColumns.forEach(col => {
                    oTable.addColumn(new sap.m.Column({
                        header: new sap.m.Label({ text: col.name }),
                        visible: true,
                        demandPopin: false
                    }));
                });
                
                rows.forEach(row => {
                    const cells = essentialColumns.map(col => {
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
            console.error("Error loading table data:", error);
            const oTable = sap.ui.getCore().byId(uniqueDataTableId);
            if (oTable) {
                oTable.setBusy(false);
                oTable.setNoData(new sap.m.Text({ text: "Error: " + error.message }));
            }
            sap.m.MessageToast.show("Error loading data: " + error.message);
        }
    }

    console.log('[DataProductsV2] View factory registered (v2.3.1 - Based on Working V1)');

})();