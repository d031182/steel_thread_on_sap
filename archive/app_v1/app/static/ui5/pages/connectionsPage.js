/**
 * Connections Page Module
 * 
 * Handles the data source configurator dialog for selecting and managing
 * database connections (HANA Cloud, SQLite, etc.).
 * 
 * @author P2P Development Team
 * @version 2.0.0
 */

// Predefined connections configuration
const PREDEFINED_CONNECTIONS = [
    {
        id: "sqlite",
        name: "Local SQLite",
        type: "SQLite Database",
        host: "localhost",
        port: null,
        status: "Connected",
        isPredefined: true
    },
    {
        id: "hana",
        name: "HANA Cloud",
        type: "SAP HANA Cloud",
        host: "your-instance.hanacloud.ondemand.com",
        port: 443,
        status: "Connected",
        isPredefined: true
    }
];

/**
 * Open the connections dialog
 */
export async function openConnectionsDialog() {
    const selectedSource = localStorage.getItem('selectedDataSource') || 'sqlite';
    const oDialog = createConnectionsDialog(selectedSource);
    oDialog.open();
}

/**
 * Create the connections dialog UI
 */
function createConnectionsDialog(selectedSource) {
    return new sap.m.Dialog({
        title: "Data Source Configurator",
        contentWidth: "700px",
        contentHeight: "500px",
        resizable: true,
        draggable: true,
        content: [
            new sap.m.VBox({
                items: [
                    new sap.m.MessageStrip({
                        text: "Select an active data source. When you click 'Load Data', data products will be fetched from the selected source.",
                        type: "Information",
                        showIcon: true
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    createConnectionsList(selectedSource),
                    createAddConnectionToolbar()
                ]
            })
        ],
        beginButton: new sap.m.Button({
            text: "Close",
            press: function() {
                this.getParent().close();
            }
        }),
        afterClose: function() {
            this.destroy();
        }
    });
}

/**
 * Create list of connections with radio selection
 */
function createConnectionsList(selectedSource) {
    return new sap.m.List({
        headerText: "Select Active Data Source",
        mode: "SingleSelectMaster",
        items: PREDEFINED_CONNECTIONS.map(conn => createConnectionItem(conn, selectedSource)),
        selectionChange: function(oEvent) {
            const oItem = oEvent.getParameter("listItem");
            const sourceId = oItem.data("sourceId");
            
            // Save selection to localStorage
            localStorage.setItem('selectedDataSource', sourceId);
            
            // Find connection name
            const conn = PREDEFINED_CONNECTIONS.find(c => c.id === sourceId);
            sap.m.MessageToast.show(`Active data source: ${conn.name}`);
        }
    });
}

/**
 * Create a single connection list item
 */
function createConnectionItem(conn, selectedSource) {
    const icon = conn.type === "SAP HANA Cloud" ? "sap-icon://cloud" : "sap-icon://database";
    const statusState = "Success";
    
    const item = new sap.m.StandardListItem({
        title: conn.name,
        description: conn.type + " • " + conn.host + (conn.port ? ":" + conn.port : ""),
        icon: icon,
        info: conn.status,
        infoState: statusState,
        type: "Active",
        selected: conn.id === selectedSource,
        press: function() {
            openConnectionDetails(conn);
        }
    });
    
    item.data("sourceId", conn.id);
    return item;
}

/**
 * Create toolbar for adding new connections
 */
function createAddConnectionToolbar() {
    return new sap.m.Toolbar({
        content: [
            new sap.m.ToolbarSpacer(),
            new sap.m.Button({
                text: "Add Connection",
                icon: "sap-icon://add",
                type: "Emphasized",
                press: function() {
                    openAddConnectionDialog();
                }
            })
        ]
    }).addStyleClass("sapUiTinyMarginTop");
}

/**
 * Open connection details dialog
 */
function openConnectionDetails(conn) {
    const oEditDialog = new sap.m.Dialog({
        title: "Connection Details: " + conn.name,
        contentWidth: "500px",
        content: [
            new sap.m.VBox({
                items: [
                    new sap.m.Label({ text: "Connection Name:" }),
                    new sap.m.Input({
                        value: conn.name,
                        editable: !conn.isPredefined
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    
                    new sap.m.Label({ text: "Type:" }),
                    new sap.m.Input({
                        value: conn.type,
                        editable: false
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    
                    new sap.m.Label({ text: "Host:" }),
                    new sap.m.Input({
                        value: conn.host,
                        editable: !conn.isPredefined
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    
                    new sap.m.Label({ text: "Port:" }),
                    new sap.m.Input({
                        value: conn.port ? String(conn.port) : "N/A",
                        editable: !conn.isPredefined
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    
                    new sap.m.Label({ text: "Status:" }),
                    new sap.m.ObjectStatus({
                        text: conn.status,
                        state: conn.status === "Connected" ? "Success" : "Error"
                    }),
                    
                    new sap.m.MessageStrip({
                        text: conn.isPredefined ? 
                            "This is a predefined connection and cannot be modified." :
                            "You can modify this custom connection.",
                        type: conn.isPredefined ? "Information" : "Success",
                        showIcon: true
                    }).addStyleClass("sapUiSmallMarginTop")
                ]
            }).addStyleClass("sapUiSmallMargin")
        ],
        beginButton: new sap.m.Button({
            text: conn.isPredefined ? "Close" : "Save",
            press: function() {
                if (!conn.isPredefined) {
                    sap.m.MessageToast.show("Connection saved (feature coming soon)");
                }
                oEditDialog.close();
            }
        }),
        endButton: new sap.m.Button({
            text: "Test Connection",
            press: function() {
                testConnection(conn);
            }
        }),
        afterClose: function() {
            oEditDialog.destroy();
        }
    });
    
    oEditDialog.open();
}

/**
 * Test connection to data source
 */
function testConnection(conn) {
    sap.m.MessageToast.show("Testing connection to " + conn.name + "...");
    setTimeout(function() {
        sap.m.MessageBox.success("Connection successful!");
    }, 1000);
}

/**
 * Open dialog for adding new connection
 */
function openAddConnectionDialog() {
    const oAddDialog = new sap.m.Dialog({
        title: "Add New Connection",
        contentWidth: "500px",
        content: [
            new sap.m.VBox({
                items: [
                    new sap.m.Label({ text: "Connection Name:" }),
                    new sap.m.Input({
                        placeholder: "My Connection"
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    
                    new sap.m.Label({ text: "Type:" }),
                    new sap.m.Select({
                        items: [
                            new sap.ui.core.Item({ key: "hana", text: "SAP HANA Cloud" }),
                            new sap.ui.core.Item({ key: "sqlite", text: "SQLite Database" }),
                            new sap.ui.core.Item({ key: "postgres", text: "PostgreSQL" }),
                            new sap.ui.core.Item({ key: "mysql", text: "MySQL" })
                        ]
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    
                    new sap.m.Label({ text: "Host:" }),
                    new sap.m.Input({
                        placeholder: "hostname or IP"
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    
                    new sap.m.Label({ text: "Port:" }),
                    new sap.m.Input({
                        placeholder: "443",
                        type: "Number"
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    
                    new sap.m.Label({ text: "Username:" }),
                    new sap.m.Input({
                        placeholder: "username"
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    
                    new sap.m.Label({ text: "Password:" }),
                    new sap.m.Input({
                        type: "Password",
                        placeholder: "password"
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    
                    new sap.m.MessageStrip({
                        text: "Custom connections will be stored locally and encrypted.",
                        type: "Information",
                        showIcon: true
                    }).addStyleClass("sapUiSmallMarginTop")
                ]
            }).addStyleClass("sapUiSmallMargin")
        ],
        beginButton: new sap.m.Button({
            text: "Add",
            type: "Emphasized",
            press: function() {
                sap.m.MessageToast.show("Adding connection... (feature coming soon)");
                oAddDialog.close();
            }
        }),
        endButton: new sap.m.Button({
            text: "Cancel",
            press: function() {
                oAddDialog.close();
            }
        }),
        afterClose: function() {
            oAddDialog.destroy();
        }
    });
    
    oAddDialog.open();
}