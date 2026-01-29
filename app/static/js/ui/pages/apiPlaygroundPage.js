/**
 * API Playground Page Module
 * 
 * Provides universal API testing interface as a full page in the application.
 * Uses Flexible Column Layout for 3-column design: Explorer | Builder | Response
 * 
 * Architecture: Full page (not dialog), peer to Data Products page
 * Floorplan: Custom layout using sap.f.FlexibleColumnLayout
 * Navigation: Page switching via IconTabBar in main app
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */

// Store discovered APIs globally for this module
let discoveredAPIs = {};
let selectedEndpoint = null;

/**
 * Create API Playground Page Content
 * Returns VBox that can be placed in mainContent area
 * @returns {sap.m.VBox} Complete API Playground UI
 */
export function createAPIPlaygroundPage() {
    return new sap.m.VBox({
        id: "apiPlaygroundContent",
        items: [
            // Page title
            new sap.m.Title({
                text: "API Playground",
                level: "H2"
            }),
            
            // Description
            new sap.m.Text({
                text: "Test all module APIs • Auto-discovered from module.json"
            }).addStyleClass("sapUiTinyMarginTop"),
            
            // Stats bar
            new sap.m.Toolbar({
                id: "apiStatsToolbar",
                content: [
                    new sap.m.Label({ text: "Modules:" }),
                    new sap.m.Text({ id: "statsModules", text: "0" }).addStyleClass("sapUiTinyMarginBegin"),
                    new sap.m.ToolbarSeparator(),
                    new sap.m.Label({ text: "Endpoints:" }),
                    new sap.m.Text({ id: "statsEndpoints", text: "0" }).addStyleClass("sapUiTinyMarginBegin"),
                    new sap.m.ToolbarSpacer(),
                    new sap.m.Button({
                        icon: "sap-icon://refresh",
                        text: "Refresh APIs",
                        press: function() {
                            discoverAPIs();
                        }
                    })
                ]
            }).addStyleClass("sapUiSmallMarginTop"),
            
            // Main 3-column layout
            new sap.f.FlexibleColumnLayout({
                id: "apiPlaygroundFCL",
                layout: sap.f.LayoutType.ThreeColumnsMidExpanded,
                backgroundDesign: sap.m.BackgroundDesign.Solid,
                
                // BEGIN: API Explorer
                beginColumnPages: [
                    createAPIExplorerPage()
                ],
                
                // MID: Request Builder
                midColumnPages: [
                    createRequestBuilderPage()
                ],
                
                // END: Response Viewer
                endColumnPages: [
                    createResponseViewerPage()
                ]
            }).addStyleClass("sapUiSmallMarginTop").setHeight("700px")
        ]
    }).addStyleClass("sapUiContentPadding");
}

/**
 * Initialize API Playground
 * Called when page is first shown
 */
export async function initializeAPIPlayground() {
    console.log('📋 Initializing API Playground...');
    await discoverAPIs();
}

/**
 * Create API Explorer Page (BEGIN Column)
 * List of all discovered APIs organized by module
 */
function createAPIExplorerPage() {
    return new sap.m.Page({
        id: "apiExplorerPage",
        title: "API Explorer",
        showHeader: true,
        subHeader: new sap.m.Toolbar({
            content: [
                new sap.m.SearchField({
                    id: "apiSearchField",
                    width: "100%",
                    placeholder: "Search APIs...",
                    search: function(oEvent) {
                        filterAPIList(oEvent.getParameter("query"));
                    }
                })
            ]
        }),
        content: [
            new sap.m.List({
                id: "apiExplorerList",
                mode: sap.m.ListMode.SingleSelectMaster,
                selectionChange: function(oEvent) {
                    const oItem = oEvent.getParameter("listItem");
                    if (oItem && oItem.data("endpoint")) {
                        loadEndpointToBuilder(
                            oItem.data("moduleName"),
                            oItem.data("endpoint")
                        );
                    }
                }
            })
        ]
    });
}

/**
 * Create Request Builder Page (MID Column)
 * Form for configuring API requests
 */
function createRequestBuilderPage() {
    return new sap.m.Page({
        id: "requestBuilderPage",
        title: "Request Builder",
        showHeader: true,
        content: [
            new sap.m.VBox({
                items: [
                    // HTTP Method
                    new sap.m.Label({ text: "HTTP Method", required: true }),
                    new sap.m.Select({
                        id: "httpMethodSelect",
                        width: "200px",
                        items: [
                            new sap.m.Item({ key: "GET", text: "GET" }),
                            new sap.m.Item({ key: "POST", text: "POST" }),
                            new sap.m.Item({ key: "PUT", text: "PUT" }),
                            new sap.m.Item({ key: "DELETE", text: "DELETE" })
                        ],
                        selectedKey: "GET"
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    
                    // Endpoint URL
                    new sap.m.Label({ text: "Endpoint URL", required: true }),
                    new sap.m.Input({
                        id: "endpointUrlInput",
                        width: "100%",
                        placeholder: "/api/module/endpoint",
                        value: ""
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    
                    // Path Parameters (for URLs with <param>)
                    new sap.m.Label({ text: "Path Parameters" }),
                    new sap.m.Input({
                        id: "pathParamsInput",
                        width: "100%",
                        placeholder: "e.g., feature_name=logging (for /<feature_name>/ endpoints)",
                        visible: false
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    
                    // Request Body (for POST/PUT)
                    new sap.m.Label({ text: "Request Body (JSON)" }),
                    new sap.m.TextArea({
                        id: "requestBodyInput",
                        rows: 10,
                        width: "100%",
                        placeholder: '{\n  "key": "value"\n}',
                        enabled: false
                    }).addStyleClass("sapUiTinyMarginBottom"),
                    
                    // Action buttons
                    new sap.m.Toolbar({
                        content: [
                            new sap.m.ToolbarSpacer(),
                            new sap.m.Button({
                                text: "Execute",
                                icon: "sap-icon://play",
                                type: sap.m.ButtonType.Emphasized,
                                press: function() {
                                    executeAPIRequest();
                                }
                            }),
                            new sap.m.Button({
                                text: "Clear",
                                icon: "sap-icon://clear-all",
                                press: function() {
                                    clearRequestBuilder();
                                }
                            })
                        ]
                    })
                ]
            }).addStyleClass("sapUiContentPadding")
        ]
    });
}

/**
 * Create Response Viewer Page (END Column)
 * Displays API responses with tabs for different views
 */
function createResponseViewerPage() {
    return new sap.m.Page({
        id: "responseViewerPage",
        title: "Response",
        showHeader: true,
        content: [
            // Response metadata bar
            new sap.m.Toolbar({
                id: "responseMetadataBar",
                content: [
                    new sap.m.Label({ text: "Status:" }),
                    new sap.m.Text({ id: "responseStatus", text: "-" }).addStyleClass("sapUiTinyMarginBegin"),
                    new sap.m.ToolbarSeparator(),
                    new sap.m.Label({ text: "Time:" }),
                    new sap.m.Text({ id: "responseTime", text: "-" }).addStyleClass("sapUiTinyMarginBegin"),
                    new sap.m.ToolbarSpacer(),
                    new sap.m.Button({
                        icon: "sap-icon://copy",
                        text: "Copy",
                        enabled: false,
                        id: "copyResponseBtn",
                        press: function() {
                            copyResponseToClipboard();
                        }
                    })
                ]
            }).addStyleClass("sapUiSmallMarginBottom"),
            
            // Response tabs
            new sap.m.IconTabBar({
                id: "responseTabBar",
                items: [
                    new sap.m.IconTabFilter({
                        key: "formatted",
                        text: "Formatted",
                        icon: "sap-icon://doc-attachment",
                        content: [
                            new sap.m.TextArea({
                                id: "formattedResponse",
                                rows: 25,
                                width: "100%",
                                editable: false,
                                value: "Execute a request to see the formatted response..."
                            })
                        ]
                    }),
                    new sap.m.IconTabFilter({
                        key: "raw",
                        text: "Raw",
                        icon: "sap-icon://text",
                        content: [
                            new sap.m.TextArea({
                                id: "rawResponse",
                                rows: 25,
                                width: "100%",
                                editable: false,
                                value: "Execute a request to see the raw response..."
                            })
                        ]
                    })
                ]
            })
        ]
    });
}

/**
 * Discover APIs from backend
 * Populates API Explorer with all available endpoints
 */
async function discoverAPIs() {
    try {
        console.log('🔍 Discovering module APIs...');
        
        const response = await fetch('/api/playground/discover');
        const data = await response.json();
        
        if (data.success) {
            discoveredAPIs = data.apis;
            populateAPIExplorer(data.apis);
            updateStats(data.stats);
            sap.m.MessageToast.show(`Discovered ${data.stats.total_endpoints} endpoints from ${data.stats.total_modules} modules`);
        } else {
            sap.m.MessageBox.error('Failed to discover APIs: ' + data.error);
        }
    } catch (error) {
        console.error('API discovery error:', error);
        sap.m.MessageBox.error('Error discovering APIs: ' + error.message);
    }
}

/**
 * Populate API Explorer list
 */
function populateAPIExplorer(apis) {
    const oList = sap.ui.getCore().byId("apiExplorerList");
    if (!oList) return;
    
    oList.destroyItems();
    
    // Group by module
    for (const [moduleName, config] of Object.entries(apis)) {
        // Module group header
        oList.addItem(new sap.m.GroupHeaderListItem({
            title: config.displayName,
            upperCase: false
        }));
        
        // Endpoints for this module
        config.endpoints.forEach((endpoint, idx) => {
            oList.addItem(new sap.m.StandardListItem({
                title: `${endpoint.method} ${endpoint.path}`,
                description: endpoint.description || '',
                type: sap.m.ListType.Active,
                customData: [
                    new sap.ui.core.CustomData({ key: "moduleName", value: moduleName }),
                    new sap.ui.core.CustomData({ key: "endpoint", value: JSON.stringify(endpoint) }),
                    new sap.ui.core.CustomData({ key: "baseUrl", value: config.baseUrl })
                ]
            }));
        });
    }
}

/**
 * Update stats toolbar
 */
function updateStats(stats) {
    const oModulesText = sap.ui.getCore().byId("statsModules");
    const oEndpointsText = sap.ui.getCore().byId("statsEndpoints");
    
    if (oModulesText) oModulesText.setText(stats.total_modules.toString());
    if (oEndpointsText) oEndpointsText.setText(stats.total_endpoints.toString());
}

/**
 * Filter API list by search query
 */
function filterAPIList(query) {
    const oList = sap.ui.getCore().byId("apiExplorerList");
    if (!oList) return;
    
    const filter = new sap.ui.model.Filter({
        filters: [
            new sap.ui.model.Filter("title", sap.ui.model.FilterOperator.Contains, query),
            new sap.ui.model.Filter("description", sap.ui.model.FilterOperator.Contains, query)
        ],
        and: false
    });
    
    oList.getBinding("items").filter(query ? [filter] : []);
}

/**
 * Load selected endpoint into request builder
 */
function loadEndpointToBuilder(moduleName, endpointData) {
    const endpoint = typeof endpointData === 'string' ? JSON.parse(endpointData) : endpointData;
    const config = discoveredAPIs[moduleName];
    
    selectedEndpoint = { moduleName, endpoint, baseUrl: config.baseUrl };
    
    // Set method
    const oMethodSelect = sap.ui.getCore().byId("httpMethodSelect");
    if (oMethodSelect) oMethodSelect.setSelectedKey(endpoint.method);
    
    // Set URL
    const oUrlInput = sap.ui.getCore().byId("endpointUrlInput");
    if (oUrlInput) oUrlInput.setValue(config.baseUrl + endpoint.path);
    
    // Show/hide path parameters field
    const oParamsInput = sap.ui.getCore().byId("pathParamsInput");
    const hasParams = endpoint.path.includes('<') && endpoint.path.includes('>');
    if (oParamsInput) {
        oParamsInput.setVisible(hasParams);
        oParamsInput.setValue('');
    }
    
    // Enable/disable request body
    const oBodyInput = sap.ui.getCore().byId("requestBodyInput");
    if (oBodyInput) {
        const isBodyMethod = ['POST', 'PUT'].includes(endpoint.method);
        oBodyInput.setEnabled(isBodyMethod);
        if (!isBodyMethod) oBodyInput.setValue('');
    }
}

/**
 * Execute API request
 */
async function executeAPIRequest() {
    const oMethodSelect = sap.ui.getCore().byId("httpMethodSelect");
    const oUrlInput = sap.ui.getCore().byId("endpointUrlInput");
    const oParamsInput = sap.ui.getCore().byId("pathParamsInput");
    const oBodyInput = sap.ui.getCore().byId("requestBodyInput");
    
    if (!oUrlInput) return;
    
    let url = oUrlInput.getValue();
    const method = oMethodSelect ? oMethodSelect.getSelectedKey() : 'GET';
    
    // Handle path parameters
    if (url.includes('<') && url.includes('>') && oParamsInput) {
        const paramValue = oParamsInput.getValue();
        if (!paramValue) {
            sap.m.MessageBox.warning('Please enter path parameter value');
            return;
        }
        // Replace <param> with value
        url = url.replace(/<[^>]+>/, paramValue);
    }
    
    // Show loading
    updateResponseViewer('loading', null, null, 'Executing request...');
    
    try {
        const startTime = performance.now();
        
        const options = {
            method: method,
            headers: { 'Content-Type': 'application/json' }
        };
        
        // Add body for POST/PUT
        if (['POST', 'PUT'].includes(method) && oBodyInput) {
            const body = oBodyInput.getValue();
            if (body.trim()) {
                try {
                    JSON.parse(body); // Validate JSON
                    options.body = body;
                } catch (e) {
                    sap.m.MessageBox.error('Invalid JSON in request body');
                    return;
                }
            }
        }
        
        const response = await fetch(url, options);
        const endTime = performance.now();
        const duration = (endTime - startTime).toFixed(2);
        
        // Parse response
        const contentType = response.headers.get('content-type');
        let responseData;
        
        if (contentType && contentType.includes('application/json')) {
            responseData = await response.json();
        } else {
            responseData = await response.text();
        }
        
        // Display response
        updateResponseViewer(
            response.ok ? 'success' : 'error',
            response.status,
            duration,
            responseData
        );
        
    } catch (error) {
        updateResponseViewer('error', null, null, error.message);
        console.error('API request error:', error);
    }
}

/**
 * Update response viewer with results
 */
function updateResponseViewer(status, statusCode, duration, data) {
    // Update metadata bar
    const oStatusText = sap.ui.getCore().byId("responseStatus");
    const oTimeText = sap.ui.getCore().byId("responseTime");
    const oCopyBtn = sap.ui.getCore().byId("copyResponseBtn");
    
    if (oStatusText) {
        if (status === 'loading') {
            oStatusText.setText('Loading...');
        } else if (statusCode) {
            oStatusText.setText(`${statusCode} ${status === 'success' ? 'OK' : 'Error'}`);
        } else {
            oStatusText.setText('Error');
        }
    }
    
    if (oTimeText) {
        oTimeText.setText(duration ? `${duration}ms` : '-');
    }
    
    if (oCopyBtn) {
        oCopyBtn.setEnabled(status !== 'loading');
    }
    
    // Format response
    let formattedText, rawText;
    
    if (status === 'loading') {
        formattedText = rawText = data;
    } else if (typeof data === 'object') {
        formattedText = JSON.stringify(data, null, 2);
        rawText = JSON.stringify(data);
    } else {
        formattedText = rawText = String(data);
    }
    
    // Update response text areas
    const oFormattedArea = sap.ui.getCore().byId("formattedResponse");
    const oRawArea = sap.ui.getCore().byId("rawResponse");
    
    if (oFormattedArea) oFormattedArea.setValue(formattedText);
    if (oRawArea) oRawArea.setValue(rawText);
}

/**
 * Clear request builder form
 */
function clearRequestBuilder() {
    const oMethodSelect = sap.ui.getCore().byId("httpMethodSelect");
    const oUrlInput = sap.ui.getCore().byId("endpointUrlInput");
    const oParamsInput = sap.ui.getCore().byId("pathParamsInput");
    const oBodyInput = sap.ui.getCore().byId("requestBodyInput");
    
    if (oMethodSelect) oMethodSelect.setSelectedKey('GET');
    if (oUrlInput) oUrlInput.setValue('');
    if (oParamsInput) {
        oParamsInput.setValue('');
        oParamsInput.setVisible(false);
    }
    if (oBodyInput) {
        oBodyInput.setValue('');
        oBodyInput.setEnabled(false);
    }
    
    selectedEndpoint = null;
}

/**
 * Copy response to clipboard
 */
function copyResponseToClipboard() {
    const oFormattedArea = sap.ui.getCore().byId("formattedResponse");
    if (oFormattedArea) {
        const text = oFormattedArea.getValue();
        navigator.clipboard.writeText(text).then(() => {
            sap.m.MessageToast.show('Response copied to clipboard');
        }).catch(err => {
            console.error('Copy failed:', err);
            sap.m.MessageToast.show('Copy failed');
        });
    }
}