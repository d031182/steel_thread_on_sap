/**
 * Knowledge Graph Page V2
 * 
 * Clean Architecture view layer for Knowledge Graph visualization.
 * Uses dependency injection with Presenter pattern.
 * 
 * Architecture: View Layer (MVP Pattern)
 * Dependencies: GraphPresenter, vis.js
 * 
 * @author P2P Development Team
 * @version 1.0.0 (Phase 5.3 - View Layer)
 * @date 2026-02-08
 */

/**
 * Create Knowledge Graph V2 Page
 * @returns {sap.m.VBox} Knowledge Graph V2 page content
 */
window.createKnowledgeGraphPageV2 = function() {
    // Header Bar with action buttons
    const headerBar = new sap.m.Bar({
        contentLeft: [
            new sap.m.Title({
                text: "Knowledge Graph v2",
                level: "H2"
            })
        ],
        contentMiddle: [
            new sap.m.ObjectStatus({
                id: "kgv2-cache-status",
                text: "Not loaded",
                state: "None"
            })
        ],
        contentRight: [
            new sap.m.Button({
                id: "kgv2-refresh-btn",
                text: "Refresh",
                icon: "sap-icon://refresh",
                type: "Default",
                press: function() {
                    handleRefresh();
                }
            }),
            new sap.m.Button({
                id: "kgv2-rebuild-btn",
                text: "Rebuild",
                icon: "sap-icon://synchronize",
                type: "Emphasized",
                press: function() {
                    handleRebuild();
                }
            }),
            new sap.m.Button({
                id: "kgv2-clear-cache-btn",
                text: "Clear Cache",
                icon: "sap-icon://delete",
                type: "Reject",
                press: function() {
                    handleClearCache();
                }
            })
        ]
    });

    // Info panel with stats
    const infoPanel = new sap.m.HBox({
        justifyContent: "SpaceBetween",
        alignItems: "Center",
        items: [
            new sap.m.HBox({
                items: [
                    new sap.m.Label({ text: "Nodes:" }).addStyleClass("sapUiTinyMarginEnd"),
                    new sap.m.Text({ id: "kgv2-node-count", text: "0" })
                ]
            }),
            new sap.m.HBox({
                items: [
                    new sap.m.Label({ text: "Edges:" }).addStyleClass("sapUiTinyMarginEnd"),
                    new sap.m.Text({ id: "kgv2-edge-count", text: "0" })
                ]
            }),
            new sap.m.HBox({
                items: [
                    new sap.m.Label({ text: "CSN Files:" }).addStyleClass("sapUiTinyMarginEnd"),
                    new sap.m.Text({ id: "kgv2-csn-count", text: "0" })
                ]
            }),
            new sap.m.HBox({
                items: [
                    new sap.m.Label({ text: "Last Refresh:" }).addStyleClass("sapUiTinyMarginEnd"),
                    new sap.m.Text({ id: "kgv2-last-refresh", text: "Never" })
                ]
            }),
            new sap.m.Button({
                text: "Filter Columns",
                icon: "sap-icon://filter",
                type: "Transparent",
                press: function() {
                    openColumnFilterDialog();
                }
            })
        ]
    }).addStyleClass("sapUiSmallMarginTop sapUiSmallMarginBottom");

    // Error message bar (hidden by default)
    const errorBar = new sap.m.MessageStrip({
        id: "kgv2-error-bar",
        text: "",
        type: "Error",
        showIcon: true,
        visible: false
    }).addStyleClass("sapUiSmallMarginBottom");

    // Graph container with vis.js network
    const graphContainer = new sap.ui.core.HTML({
        id: "kgv2-graph-html",
        content: `
            <div id="kgv2-graph-canvas" style="width: 100%; height: calc(100vh - 320px); border: 1px solid #d9d9d9; border-radius: 0.25rem; background: #ffffff; position: relative;">
                <!-- Loading overlay -->
                <div id="kgv2-loading-overlay" style="display: none; position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(255, 255, 255, 0.8); z-index: 1000; display: flex; align-items: center; justify-content: center;">
                    <div style="text-align: center;">
                        <div class="sapUiBusyIndicator" style="margin-bottom: 1rem;"></div>
                        <div style="font-size: 16px; color: #666;">Loading graph...</div>
                    </div>
                </div>
                
                <!-- Placeholder content (shown when no graph loaded) -->
                <div id="kgv2-placeholder" style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666;">
                    <div style="text-align: center;">
                        <div style="font-size: 48px; margin-bottom: 1rem;">📊</div>
                        <div style="font-size: 18px; font-weight: 600; margin-bottom: 0.5rem;">Knowledge Graph v2</div>
                        <div style="font-size: 14px;">Click "Refresh" to load schema graph</div>
                        <div style="font-size: 12px; color: #999; margin-top: 0.5rem;">Clean Architecture • DDD • Generic Format</div>
                    </div>
                </div>
            </div>
        `,
        afterRendering: function() {
            // Load vis.js library and initialize presenter
            loadVisJSLibrary();
            initializePresenter();
        }
    });

    // Main layout
    return new sap.m.VBox({
        items: [
            headerBar,
            errorBar,
            infoPanel,
            graphContainer
        ]
    }).addStyleClass("sapUiContentPadding");
}

// Global state
let presenterInstance = null;
let networkInstance = null;

/**
 * Load vis.js library dynamically
 */
function loadVisJSLibrary() {
    if (window.vis) {
        console.log('✓ vis.js already loaded');
        return;
    }
    
    console.log('Loading vis.js library...');
    
    // Load CSS
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://cdn.jsdelivr.net/npm/vis-network@9.1.2/dist/dist/vis-network.min.css';
    document.head.appendChild(link);
    
    // Load JS
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/vis-network@9.1.2/dist/vis-network.min.js';
    script.onload = function() {
        console.log('✓ vis.js loaded successfully');
    };
    document.head.appendChild(script);
}

/**
 * Initialize presenter with dependencies (Dependency Injection)
 */
async function initializePresenter() {
    try {
        // Wait for adapter classes to be available
        if (typeof KnowledgeGraphApiClient === 'undefined' || 
            typeof VisJsGraphAdapter === 'undefined' ||
            typeof GraphPresenter === 'undefined') {
            console.warn('Waiting for adapter classes...');
            setTimeout(initializePresenter, 500);
            return;
        }

        console.log('📊 Initializing Knowledge Graph v2 Presenter...');

        // Create dependencies (Dependency Injection)
        const apiClient = new KnowledgeGraphApiClient('/api/knowledge-graph');
        const visJsAdapter = new VisJsGraphAdapter();

        // Create presenter
        presenterInstance = new GraphPresenter(apiClient, visJsAdapter);
        
        // Make presenter and adapter globally accessible for debugging
        window.presenterInstance = presenterInstance;
        window.visJsAdapter = visJsAdapter;

        // Subscribe to state changes (Observer pattern)
        presenterInstance.subscribe(onPresenterStateChange);

        console.log('✓ Presenter initialized with Clean Architecture');

        // Perform health check
        try {
            const health = await apiClient.healthCheck();
            console.log('✓ Backend health:', health);
        } catch (error) {
            console.error('⚠️ Backend health check failed:', error);
        }

    } catch (error) {
        console.error('Failed to initialize presenter:', error);
        showError('Initialization failed: ' + error.message);
    }
}

/**
 * Initialize Knowledge Graph V2 page (entry point)
 */
window.initializeKnowledgeGraphV2 = async function() {
    console.log('📊 Knowledge Graph v2 page loaded');
    // Presenter initialization happens in afterRendering
};

/**
 * Handle presenter state changes (Observer pattern callback)
 * 
 * @param {Object} state - New presenter state
 */
function onPresenterStateChange(state) {
    console.log('[View] State changed:', {
        hasGraph: !!state.graph,
        hasGenericGraph: !!state.genericGraph,
        loading: state.loading,
        error: state.error,
        graphNodesLength: state.graph?.nodes?.length,
        graphEdgesLength: state.graph?.edges?.length
    });

    // Update loading overlay
    updateLoadingState(state.loading);

    // Update error bar
    if (state.error) {
        showError(state.error);
    } else {
        hideError();
    }

    // Update graph visualization
    if (state.graph && !state.loading) {
        renderGraph(state.graph);
        updateStats(state);
        hidePlaceholder();
    }

    // Update cache status
    updateCacheStatus(state.cacheStatus);
}

/**
 * Update loading overlay visibility
 */
function updateLoadingState(isLoading) {
    const overlay = document.getElementById('kgv2-loading-overlay');
    if (overlay) {
        overlay.style.display = isLoading ? 'flex' : 'none';
    }

    // Disable buttons during loading
    const refreshBtn = sap.ui.getCore().byId('kgv2-refresh-btn');
    const rebuildBtn = sap.ui.getCore().byId('kgv2-rebuild-btn');
    const clearBtn = sap.ui.getCore().byId('kgv2-clear-cache-btn');

    if (refreshBtn) refreshBtn.setEnabled(!isLoading);
    if (rebuildBtn) rebuildBtn.setEnabled(!isLoading);
    if (clearBtn) clearBtn.setEnabled(!isLoading);
}

/**
 * Show error message
 */
function showError(message) {
    const errorBar = sap.ui.getCore().byId('kgv2-error-bar');
    if (errorBar) {
        errorBar.setText(message);
        errorBar.setVisible(true);
    }
}

/**
 * Hide error message
 */
function hideError() {
    const errorBar = sap.ui.getCore().byId('kgv2-error-bar');
    if (errorBar) {
        errorBar.setVisible(false);
    }
}

/**
 * Hide placeholder content
 */
function hidePlaceholder() {
    const placeholder = document.getElementById('kgv2-placeholder');
    if (placeholder) {
        placeholder.style.display = 'none';
    }
}

/**
 * Update statistics display
 */
function updateStats(state) {
    const nodeCount = sap.ui.getCore().byId('kgv2-node-count');
    const edgeCount = sap.ui.getCore().byId('kgv2-edge-count');
    const csnCount = sap.ui.getCore().byId('kgv2-csn-count');
    const lastRefresh = sap.ui.getCore().byId('kgv2-last-refresh');

    if (nodeCount && state.graph) {
        nodeCount.setText(state.graph.nodes.length.toString());
    }
    if (edgeCount && state.graph) {
        edgeCount.setText(state.graph.edges.length.toString());
    }
    if (csnCount && state.cacheStatus) {
        csnCount.setText(state.cacheStatus.csnFilesCount.toString());
    }
    if (lastRefresh && state.lastRefresh) {
        const time = state.lastRefresh.toLocaleTimeString();
        lastRefresh.setText(time);
    }
}

/**
 * Update cache status indicator
 */
function updateCacheStatus(cacheStatus) {
    const statusControl = sap.ui.getCore().byId('kgv2-cache-status');
    if (!statusControl) return;

    if (cacheStatus.cached) {
        statusControl.setText('Cached');
        statusControl.setState('Success');
    } else {
        statusControl.setText('Rebuilt');
        statusControl.setState('Warning');
    }
}

/**
 * Render vis.js graph
 */
function renderGraph(visJsGraph) {
    console.log('[View] renderGraph() called with:', {
        hasNodes: !!visJsGraph.nodes,
        hasEdges: !!visJsGraph.edges,
        nodesLength: visJsGraph.nodes?.length,
        edgesLength: visJsGraph.edges?.length
    });
    
    // Wait for vis.js to load
    if (!window.vis) {
        console.warn('[View] vis.js not loaded yet, retrying...');
        setTimeout(() => renderGraph(visJsGraph), 500);
        return;
    }

    const container = document.getElementById('kgv2-graph-canvas');
    if (!container) {
        console.error('Graph container not found');
        return;
    }

    // Check if data is already wrapped in DataSets (from presenter)
    const nodesData = (visJsGraph.nodes instanceof vis.DataSet) ? visJsGraph.nodes : new vis.DataSet(visJsGraph.nodes || []);
    const edgesData = (visJsGraph.edges instanceof vis.DataSet) ? visJsGraph.edges : new vis.DataSet(visJsGraph.edges || []);
    
    console.log('Rendering graph:', nodesData.length, 'nodes,', edgesData.length, 'edges');

    // Get vis.js configuration from adapter (includes HTML tooltip support)
    const options = window.visJsAdapter ? window.visJsAdapter.getDefaultOptions() : {
        nodes: {
            scaling: {
                min: 10,
                max: 30
            }
        },
        edges: {
            smooth: {
                type: 'continuous'
            }
        },
        physics: {
            enabled: true,
            barnesHut: {
                gravitationalConstant: -2000,
                springConstant: 0.001,
                springLength: 200
            },
            stabilization: {
                iterations: 150
            }
        },
        layout: {
            improvedLayout: true
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            zoomView: true,
            dragView: true,
            navigationButtons: true
            // NOTE: HTML rendering in tooltips is enabled by default via 'title' attribute
        }
    };

    // Use DataSets (already created by presenter or create if needed)
    const data = {
        nodes: nodesData,
        edges: edgesData
    };

    // Destroy existing network
    if (networkInstance) {
        networkInstance.destroy();
    }

    // Create new network
    networkInstance = new vis.Network(container, data, options);

    // Setup custom tooltip handlers for HTML rendering
    if (window.visJsAdapter) {
        window.visJsAdapter.setupTooltipHandlers(networkInstance, data.nodes, data.edges);
    }

    // Add event listeners
    networkInstance.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = data.nodes.get(nodeId);
            console.log('Node clicked:', node);
            sap.m.MessageToast.show(`Selected: ${node.label}`);
        }
    });

    networkInstance.on('stabilizationIterationsDone', function() {
        console.log('✓ Graph stabilization complete');
    });

    console.log('✓ Graph rendered successfully');
}

/**
 * Handle refresh button (load with cache)
 */
async function handleRefresh() {
    if (!presenterInstance) {
        sap.m.MessageToast.show('Presenter not initialized');
        return;
    }

    try {
        await presenterInstance.refresh();
        console.log('✓ Refresh complete');
    } catch (error) {
        console.error('Refresh failed:', error);
        sap.m.MessageBox.error(`Refresh failed: ${error.message}`);
    }
}

/**
 * Handle rebuild button (force rebuild, bypass cache)
 */
async function handleRebuild() {
    if (!presenterInstance) {
        sap.m.MessageToast.show('Presenter not initialized');
        return;
    }

    try {
        sap.m.MessageToast.show('Rebuilding graph from CSN files...');
        const result = await presenterInstance.rebuild();
        sap.m.MessageBox.success('Graph rebuilt successfully!', {
            title: 'Rebuild Complete'
        });
        console.log('✓ Rebuild complete', result);
    } catch (error) {
        console.error('Rebuild failed:', error);
        sap.m.MessageBox.error(`Rebuild failed: ${error.message || error}`);
    }
}

/**
 * Handle clear cache button
 */
async function handleClearCache() {
    if (!presenterInstance) {
        sap.m.MessageToast.show('Presenter not initialized');
        return;
    }

    // Confirm action
    sap.m.MessageBox.confirm(
        'This will clear the cached graph and force a rebuild. Continue?',
        {
            title: 'Clear Cache',
            onClose: async function(action) {
                if (action === sap.m.MessageBox.Action.OK) {
                    try {
                        sap.m.MessageToast.show('Clearing cache and rebuilding...');
                        await presenterInstance.clearCacheAndReload();
                        sap.m.MessageBox.success('Cache cleared and graph rebuilt!', {
                            title: 'Cache Cleared'
                        });
                        console.log('✓ Cache cleared');
                    } catch (error) {
                        console.error('Clear cache failed:', error);
                        sap.m.MessageBox.error(`Clear cache failed: ${error.message}`);
                    }
                }
            }
        }
    );
}

/**
 * Open column filter dialog
 */
function openColumnFilterDialog() {
    if (!presenterInstance) {
        sap.m.MessageToast.show('Presenter not initialized');
        return;
    }

    // Get state for current filters
    const state = presenterInstance.getState();
    const currentFilters = state.columnFilters || {};

    // Create dialog
    const dialog = new sap.m.Dialog({
        title: "Filter Table Columns",
        contentWidth: "500px",
        content: [
            new sap.m.VBox({
                items: [
                    // Table name input
                    new sap.m.Label({ text: "Table Name:", required: true }),
                    new sap.m.Input({
                        id: "kgv2-filter-table-name",
                        placeholder: "e.g., PurchaseOrder, Invoice",
                        value: currentFilters.tableName || "",
                        required: true
                    }).addStyleClass("sapUiSmallMarginBottom"),

                    // Semantic type dropdown
                    new sap.m.Label({ text: "Semantic Type (optional):" }),
                    new sap.m.ComboBox({
                        id: "kgv2-filter-semantic-type",
                        placeholder: "Select semantic type...",
                        items: [
                            new sap.ui.core.Item({ key: "", text: "(All)" }),
                            new sap.ui.core.Item({ key: "amount", text: "Amount" }),
                            new sap.ui.core.Item({ key: "date", text: "Date" }),
                            new sap.ui.core.Item({ key: "id", text: "ID" }),
                            new sap.ui.core.Item({ key: "text", text: "Text" }),
                            new sap.ui.core.Item({ key: "status", text: "Status" }),
                            new sap.ui.core.Item({ key: "quantity", text: "Quantity" })
                        ],
                        selectedKey: currentFilters.semanticType || ""
                    }).addStyleClass("sapUiSmallMarginBottom"),

                    // Search input
                    new sap.m.Label({ text: "Search (optional):" }),
                    new sap.m.Input({
                        id: "kgv2-filter-search",
                        placeholder: "Search in name, label, or description...",
                        value: currentFilters.search || ""
                    }).addStyleClass("sapUiSmallMarginBottom"),

                    // Results display (hidden initially)
                    new sap.m.Text({
                        id: "kgv2-filter-results-summary",
                        visible: false
                    }).addStyleClass("sapUiSmallMarginTop"),

                    // Results table (hidden initially)
                    new sap.m.Table({
                        id: "kgv2-filter-results-table",
                        visible: false,
                        columns: [
                            new sap.m.Column({ header: new sap.m.Label({ text: "Name" }) }),
                            new sap.m.Column({ header: new sap.m.Label({ text: "Type" }) }),
                            new sap.m.Column({ header: new sap.m.Label({ text: "Semantic Type" }) }),
                            new sap.m.Column({ header: new sap.m.Label({ text: "Label" }) })
                        ]
                    }).addStyleClass("sapUiSmallMarginTop")
                ]
            }).addStyleClass("sapUiContentPadding")
        ],
        beginButton: new sap.m.Button({
            text: "Apply Filter",
            type: "Emphasized",
            press: async function() {
                await applyColumnFilter(dialog);
            }
        }),
        endButton: new sap.m.Button({
            text: "Close",
            press: function() {
                dialog.close();
            }
        }),
        afterClose: function() {
            dialog.destroy();
        }
    });

    dialog.open();
}

/**
 * Apply column filter from dialog
 */
async function applyColumnFilter(dialog) {
    const tableNameInput = sap.ui.getCore().byId('kgv2-filter-table-name');
    const semanticTypeCombo = sap.ui.getCore().byId('kgv2-filter-semantic-type');
    const searchInput = sap.ui.getCore().byId('kgv2-filter-search');

    const tableName = tableNameInput.getValue().trim();
    const semanticType = semanticTypeCombo.getSelectedKey();
    const search = searchInput.getValue().trim();

    // Validate table name
    if (!tableName) {
        sap.m.MessageToast.show('Please enter a table name');
        return;
    }

    try {
        // Build filters object
        const filters = {};
        if (semanticType) {
            filters.semantic_type = semanticType;
        }
        if (search) {
            filters.search = search;
        }

        // Call presenter
        await presenterInstance.loadTableColumns(tableName, filters);

        // Display results
        const state = presenterInstance.getState();
        const results = state.filteredColumns;

        if (results) {
            // Update results summary
            const summary = sap.ui.getCore().byId('kgv2-filter-results-summary');
            summary.setText(`Found ${results.columns.length} of ${results.total_columns} columns`);
            summary.setVisible(true);

            // Update results table
            const table = sap.ui.getCore().byId('kgv2-filter-results-table');
            table.removeAllItems();

            results.columns.forEach(col => {
                table.addItem(new sap.m.ColumnListItem({
                    cells: [
                        new sap.m.Text({ text: col.name }),
                        new sap.m.Text({ text: col.type }),
                        new sap.m.Text({ text: col.semantic_type || '—' }),
                        new sap.m.Text({ text: col.display_label || '—' })
                    ]
                }));
            });

            table.setVisible(true);

            sap.m.MessageToast.show(`Filtered to ${results.columns.length} columns`);
        }

    } catch (error) {
        console.error('Filter failed:', error);
        sap.m.MessageBox.error(`Filter failed: ${error.message}`);
    }
}
