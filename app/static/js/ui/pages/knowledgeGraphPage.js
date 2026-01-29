/**
 * Knowledge Graph Page
 * 
 * Visualizes relationships between data products, tables, and fields
 * using a force-directed graph
 * 
 * @author P2P Development Team
 * @version 1.0.0
 */

/**
 * Create Knowledge Graph Page
 * @returns {sap.m.VBox} Knowledge Graph page content
 */
export function createKnowledgeGraphPage() {
    return new sap.m.VBox({
        id: "knowledgeGraphContent",
        items: [
            // Page header
            new sap.m.Title({
                text: "Knowledge Graph",
                level: "H2"
            }),
            
            new sap.m.Text({
                text: "Visual representation of data product relationships"
            }).addStyleClass("sapUiTinyMarginTop"),
            
            // Toolbar with controls
            new sap.m.Toolbar({
                content: [
                    new sap.m.Button({
                        text: "Refresh Graph",
                        icon: "sap-icon://refresh",
                        press: function() {
                            loadKnowledgeGraph();
                        }
                    }),
                    new sap.m.ToolbarSeparator(),
                    new sap.m.Label({ text: "Layout:" }),
                    new sap.m.Select({
                        id: "layoutSelect",
                        selectedKey: "force",
                        items: [
                            new sap.ui.core.Item({ key: "force", text: "Force-Directed" }),
                            new sap.ui.core.Item({ key: "circular", text: "Circular" }),
                            new sap.ui.core.Item({ key: "hierarchical", text: "Hierarchical" })
                        ],
                        change: function() {
                            loadKnowledgeGraph();
                        }
                    }),
                    new sap.m.ToolbarSpacer(),
                    new sap.m.Label({ text: "Nodes: " }),
                    new sap.m.Text({ id: "nodeCount", text: "0" }),
                    new sap.m.ToolbarSeparator(),
                    new sap.m.Label({ text: "Edges: " }),
                    new sap.m.Text({ id: "edgeCount", text: "0" })
                ]
            }).addStyleClass("sapUiSmallMarginTop"),
            
            // Graph container (HTML canvas)
            new sap.ui.core.HTML({
                id: "graphContainer",
                content: `
                    <div id="knowledgeGraphCanvas" style="width: 100%; height: 600px; border: 1px solid #ddd; border-radius: 8px; background: white; margin-top: 1rem;">
                        <div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #666;">
                            <div style="text-align: center;">
                                <div style="font-size: 48px; margin-bottom: 1rem;">📊</div>
                                <div style="font-size: 18px; font-weight: 600; margin-bottom: 0.5rem;">Knowledge Graph</div>
                                <div>Click "Refresh Graph" to load visualization</div>
                            </div>
                        </div>
                    </div>
                `,
                afterRendering: function() {
                    // Load vis.js library dynamically
                    loadVisJSLibrary();
                }
            }),
            
            // Legend
            new sap.m.Panel({
                headerText: "Legend",
                expandable: true,
                expanded: false,
                content: [
                    new sap.m.VBox({
                        items: [
                            new sap.m.HBox({
                                items: [
                                    new sap.ui.core.HTML({
                                        content: '<div style="width: 20px; height: 20px; border-radius: 50%; background: #0070f2; margin-right: 10px;"></div>'
                                    }),
                                    new sap.m.Text({ text: "Data Product" })
                                ]
                            }).addStyleClass("sapUiTinyMarginTop"),
                            new sap.m.HBox({
                                items: [
                                    new sap.ui.core.HTML({
                                        content: '<div style="width: 20px; height: 20px; border-radius: 50%; background: #30914c; margin-right: 10px;"></div>'
                                    }),
                                    new sap.m.Text({ text: "Table" })
                                ]
                            }).addStyleClass("sapUiTinyMarginTop"),
                            new sap.m.HBox({
                                items: [
                                    new sap.ui.core.HTML({
                                        content: '<div style="width: 40px; height: 2px; background: #666; margin-right: 10px; margin-top: 9px;"></div>'
                                    }),
                                    new sap.m.Text({ text: "Contains relationship" })
                                ]
                            }).addStyleClass("sapUiTinyMarginTop"),
                            new sap.m.HBox({
                                items: [
                                    new sap.ui.core.HTML({
                                        content: '<div style="width: 40px; height: 2px; background: #e26310; margin-right: 10px; margin-top: 9px;"></div>'
                                    }),
                                    new sap.m.Text({ text: "Foreign key relationship" })
                                ]
                            }).addStyleClass("sapUiTinyMarginTop")
                        ]
                    }).addStyleClass("sapUiSmallMargin")
                ]
            }).addStyleClass("sapUiSmallMarginTop")
        ]
    }).addStyleClass("sapUiContentPadding");
}

/**
 * Initialize Knowledge Graph page
 */
export async function initializeKnowledgeGraph() {
    console.log('📊 Initializing Knowledge Graph...');
    // Auto-load graph data
    await loadKnowledgeGraph();
}

let network = null;

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
 * Load and visualize knowledge graph
 */
async function loadKnowledgeGraph() {
    try {
        console.log('Loading knowledge graph data...');
        
        // Fetch data products
        const response = await fetch('/api/data-products?source=sqlite');
        const data = await response.json();
        
        if (!data.success || !data.data_products) {
            sap.m.MessageToast.show('No data products found');
            return;
        }
        
        const products = data.data_products;
        
        // Build graph data
        const graphData = buildGraphData(products);
        
        // Update stats
        updateGraphStats(graphData);
        
        // Render graph
        renderGraph(graphData);
        
        sap.m.MessageToast.show(`Loaded ${products.length} data products`);
        
    } catch (error) {
        console.error('Error loading knowledge graph:', error);
        sap.m.MessageBox.error('Failed to load knowledge graph: ' + error.message);
    }
}

/**
 * Build graph data structure from data products
 */
function buildGraphData(products) {
    const nodes = [];
    const edges = [];
    let nodeId = 1;
    
    // Create nodes for each data product
    products.forEach(product => {
        const productId = `product-${nodeId++}`;
        
        // Add product node
        nodes.push({
            id: productId,
            label: product.displayName || product.productName,
            title: `${product.productName}\n${product.tableCount || 0} tables`,
            group: 'product',
            size: 30,
            font: { size: 16, bold: true }
        });
        
        // Add table nodes (simplified - just show count as a single node)
        if (product.tableCount > 0) {
            const tablesId = `tables-${nodeId++}`;
            nodes.push({
                id: tablesId,
                label: `${product.tableCount} Tables`,
                title: `${product.tableCount} tables in ${product.productName}`,
                group: 'table',
                size: 20,
                font: { size: 12 }
            });
            
            // Connect product to tables
            edges.push({
                from: productId,
                to: tablesId,
                label: 'contains',
                arrows: 'to'
            });
        }
    });
    
    return { nodes, edges };
}

/**
 * Update graph statistics
 */
function updateGraphStats(graphData) {
    const nodeText = sap.ui.getCore().byId("nodeCount");
    const edgeText = sap.ui.getCore().byId("edgeCount");
    
    if (nodeText) nodeText.setText(graphData.nodes.length.toString());
    if (edgeText) edgeText.setText(graphData.edges.length.toString());
}

/**
 * Render graph using vis.js
 */
function renderGraph(graphData) {
    // Wait for vis.js to load
    if (!window.vis) {
        setTimeout(() => renderGraph(graphData), 500);
        return;
    }
    
    const container = document.getElementById('knowledgeGraphCanvas');
    if (!container) {
        console.error('Graph container not found');
        return;
    }
    
    const layoutSelect = sap.ui.getCore().byId("layoutSelect");
    const layout = layoutSelect ? layoutSelect.getSelectedKey() : 'force';
    
    // Configure visualization options
    const options = {
        nodes: {
            shape: 'dot',
            scaling: {
                min: 10,
                max: 30
            },
            font: {
                size: 14,
                face: 'Arial'
            }
        },
        edges: {
            width: 2,
            color: { inherit: 'from' },
            smooth: {
                type: 'cubicBezier',
                forceDirection: layout === 'hierarchical' ? 'vertical' : 'none'
            }
        },
        physics: {
            enabled: layout === 'force',
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
            improvedLayout: true,
            hierarchical: layout === 'hierarchical' ? {
                direction: 'UD',
                sortMethod: 'directed',
                levelSeparation: 150
            } : false
        },
        groups: {
            product: {
                color: { background: '#0070f2', border: '#0064d9' },
                font: { color: '#ffffff' }
            },
            table: {
                color: { background: '#30914c', border: '#237a3c' },
                font: { color: '#ffffff' }
            }
        },
        interaction: {
            hover: true,
            tooltipDelay: 200,
            zoomView: true,
            dragView: true
        }
    };
    
    // Create network
    const data = {
        nodes: new vis.DataSet(graphData.nodes),
        edges: new vis.DataSet(graphData.edges)
    };
    
    if (network) {
        network.destroy();
    }
    
    network = new vis.Network(container, data, options);
    
    // Add event listeners
    network.on('click', function(params) {
        if (params.nodes.length > 0) {
            const nodeId = params.nodes[0];
            const node = data.nodes.get(nodeId);
            console.log('Clicked node:', node);
            sap.m.MessageToast.show('Selected: ' + node.label);
        }
    });
    
    console.log('✓ Graph rendered with', graphData.nodes.length, 'nodes and', graphData.edges.length, 'edges');
}