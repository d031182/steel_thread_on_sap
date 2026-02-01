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
    // Left panel: Settings (fixed width)
    const settingsPanel = new sap.m.VBox({
        width: "320px",
        items: [
            new sap.m.Title({
                text: "Graph Settings",
                level: "H3"
            }),
            
            // Mode selection
            new sap.m.VBox({
                items: [
                    new sap.m.Label({ text: "Mode:" }).addStyleClass("sapUiTinyMarginTop"),
                    new sap.m.Select({
                        id: "modeSelect",
                        selectedKey: "schema",
                        width: "100%",
                        items: [
                            new sap.ui.core.Item({ key: "schema", text: "Architecture (Products & Tables)" }),
                            new sap.ui.core.Item({ key: "data", text: "Data (Records & Relationships)" })
                        ],
                        change: function() {
                            loadKnowledgeGraph();
                        }
                    })
                ]
            }).addStyleClass("sapUiSmallMarginTop"),
            
            // Layout selection
            new sap.m.VBox({
                items: [
                    new sap.m.Label({ text: "Layout:" }).addStyleClass("sapUiTinyMarginTop"),
                    new sap.m.Select({
                        id: "layoutSelect",
                        selectedKey: "force",
                        width: "100%",
                        items: [
                            new sap.ui.core.Item({ key: "force", text: "Force-Directed" }),
                            new sap.ui.core.Item({ key: "circular", text: "Circular" }),
                            new sap.ui.core.Item({ key: "hierarchical", text: "Hierarchical" })
                        ],
                        change: function() {
                            loadKnowledgeGraph();
                        }
                    })
                ]
            }).addStyleClass("sapUiSmallMarginTop"),
            
            // Refresh button
            new sap.m.Button({
                text: "Refresh Graph",
                icon: "sap-icon://refresh",
                type: "Emphasized",
                width: "100%",
                press: function() {
                    loadKnowledgeGraph();
                }
            }).addStyleClass("sapUiSmallMarginTop"),
            
            // Refresh Cache button
            new sap.m.Button({
                text: "Refresh Cache",
                icon: "sap-icon://sys-help",
                type: "Default",
                width: "100%",
                press: function() {
                    refreshOntologyCache();
                }
            }).addStyleClass("sapUiTinyMarginTop"),
            
            // Stats
            new sap.m.HBox({
                justifyContent: "SpaceBetween",
                items: [
                    new sap.m.Label({ text: "Nodes:" }),
                    new sap.m.Text({ id: "nodeCount", text: "0" })
                ]
            }).addStyleClass("sapUiSmallMarginTop"),
            new sap.m.HBox({
                justifyContent: "SpaceBetween",
                items: [
                    new sap.m.Label({ text: "Edges:" }),
                    new sap.m.Text({ id: "edgeCount", text: "0" })
                ]
            }).addStyleClass("sapUiTinyMarginTop"),
            
            // Algorithm Panel
            new sap.m.Panel({
                id: "algorithmPanel",
                headerText: "Graph Algorithms",
                expandable: true,
                expanded: false,
                content: [
                    new sap.m.VBox({
                        items: [
                            // Centrality Analysis
                            new sap.m.VBox({
                                items: [
                                    new sap.m.Label({ text: "Centrality:" }).addStyleClass("sapUiTinyMarginTop"),
                                    new sap.m.Select({
                                        id: "centralityAlgorithmSelect",
                                        selectedKey: "betweenness",
                                        width: "100%",
                                        items: [
                                            new sap.ui.core.Item({ key: "betweenness", text: "Betweenness" }),
                                            new sap.ui.core.Item({ key: "pagerank", text: "PageRank" }),
                                            new sap.ui.core.Item({ key: "degree", text: "Degree" }),
                                            new sap.ui.core.Item({ key: "closeness", text: "Closeness" })
                                        ]
                                    }),
                                    new sap.m.Button({
                                        text: "Calculate",
                                        type: "Emphasized",
                                        width: "100%",
                                        press: function() {
                                            runCentralityAnalysis();
                                        }
                                    }).addStyleClass("sapUiTinyMarginTop")
                                ]
                            }).addStyleClass("sapUiTinyMarginTop"),
                            
                            // Community Detection
                            new sap.m.VBox({
                                items: [
                                    new sap.m.Label({ text: "Communities:" }).addStyleClass("sapUiTinyMarginTop"),
                                    new sap.m.Select({
                                        id: "communityAlgorithmSelect",
                                        selectedKey: "louvain",
                                        width: "100%",
                                        items: [
                                            new sap.ui.core.Item({ key: "louvain", text: "Louvain" }),
                                            new sap.ui.core.Item({ key: "label_propagation", text: "Label Propagation" }),
                                            new sap.ui.core.Item({ key: "greedy_modularity", text: "Greedy Modularity" })
                                        ]
                                    }),
                                    new sap.m.Button({
                                        text: "Detect",
                                        type: "Emphasized",
                                        width: "100%",
                                        press: function() {
                                            runCommunityDetection();
                                        }
                                    }).addStyleClass("sapUiTinyMarginTop")
                                ]
                            }).addStyleClass("sapUiTinyMarginTop"),
                            
                            // Results display
                            new sap.m.Text({
                                id: "algorithmResults",
                                text: ""
                            }).addStyleClass("sapUiSmallMarginTop")
                        ]
                    }).addStyleClass("sapUiSmallMargin")
                ]
            }).addStyleClass("sapUiSmallMarginTop"),
            
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
                                        content: '<div style="width: 16px; height: 16px; border-radius: 50%; background: #1976d2; margin-right: 8px;"></div>'
                                    }),
                                    new sap.m.Text({ text: "Data Product" })
                                ]
                            }).addStyleClass("sapUiTinyMarginTop"),
                            new sap.m.HBox({
                                items: [
                                    new sap.ui.core.HTML({
                                        content: '<div style="width: 16px; height: 16px; border-radius: 50%; background: #4caf50; margin-right: 8px;"></div>'
                                    }),
                                    new sap.m.Text({ text: "Table/Record" })
                                ]
                            }).addStyleClass("sapUiTinyMarginTop"),
                            new sap.m.HBox({
                                items: [
                                    new sap.ui.core.HTML({
                                        content: '<div style="width: 30px; height: 2px; background: #666; margin-right: 8px; margin-top: 7px;"></div>'
                                    }),
                                    new sap.m.Text({ text: "Contains" })
                                ]
                            }).addStyleClass("sapUiTinyMarginTop"),
                            new sap.m.HBox({
                                items: [
                                    new sap.ui.core.HTML({
                                        content: '<div style="width: 30px; height: 2px; background: #ff9800; margin-right: 8px; margin-top: 7px;"></div>'
                                    }),
                                    new sap.m.Text({ text: "Foreign Key" })
                                ]
                            }).addStyleClass("sapUiTinyMarginTop")
                        ]
                    }).addStyleClass("sapUiSmallMargin")
                ]
            }).addStyleClass("sapUiSmallMarginTop")
        ]
    }).addStyleClass("sapUiContentPadding");
    
    // Right panel: Graph visualization (flexible width)
    const graphPanel = new sap.m.VBox({
        items: [
            new sap.m.Title({
                text: "Knowledge Graph",
                level: "H3"
            }),
            new sap.m.Text({
                text: "Visual representation of data product relationships"
            }).addStyleClass("sapUiTinyMarginTop"),
            
            // Graph container (HTML canvas) - full height
            new sap.ui.core.HTML({
                id: "graphContainer",
                content: `
                    <div id="knowledgeGraphCanvas" style="width: 100%; height: calc(100vh - 300px); border: 1px solid #ddd; border-radius: 8px; background: white; margin-top: 1rem;">
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
            })
        ]
    }).addStyleClass("sapUiContentPadding");
    
    // Two-column layout: Settings left (fixed), Graph right (flexible)
    return new sap.m.HBox({
        items: [
            settingsPanel,
            new sap.m.VBox({ width: "1rem" }), // Spacer
            graphPanel
        ]
    });
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
let currentGraphData = null;  // Store current graph data for re-rendering

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
        
        // Get configured source and mode
        const source = localStorage.getItem('selectedDataSource') || 'sqlite';
        const sourceName = source === 'hana' ? 'HANA Cloud' : 'Local SQLite';
        
        const modeSelect = sap.ui.getCore().byId("modeSelect");
        const mode = modeSelect ? modeSelect.getSelectedKey() : 'schema';
        const modeName = mode === 'schema' ? 'Architecture' : 'Data';
        
        // Fetch knowledge graph
        const response = await fetch(`/api/knowledge-graph/?source=${source}&mode=${mode}&max_records=20`);
        const data = await response.json();
        
        // Check for success (API returns {success: true/false})
        if (data.success === false) {
            const errorMsg = (data.error && data.error.message) || data.error || 'Unknown error';
            sap.m.MessageToast.show(`Failed to load graph: ${errorMsg}`);
            console.error('API error:', data.error);
            return;
        }
        
        // Check if we have valid data
        if (!data.nodes || !Array.isArray(data.nodes)) {
            sap.m.MessageToast.show('Invalid graph data received from API');
            console.error('Invalid data structure:', data);
            return;
        }
        
        // Graph data comes pre-built from backend (with stats already calculated)
        const graphData = {
            nodes: data.nodes || [],
            edges: data.edges || []
        };
        
        // Store for re-rendering
        currentGraphData = {
            graphData: graphData,
            stats: data.stats
        };
        
        // Update stats (use backend-calculated stats if available, otherwise count arrays)
        if (data.stats) {
            updateGraphStatsFromBackend(data.stats);
        } else {
            updateGraphStats(graphData);
        }
        
        // Render graph
        renderGraph(graphData);
        
        const tableCount = data.stats?.table_count || data.stats?.product_count || 0;
        const countLabel = mode === 'schema' ? 'products' : 'tables';
        
        if (data.message) {
            sap.m.MessageToast.show(data.message);
        } else {
            sap.m.MessageToast.show(`${modeName} view: ${graphData.nodes.length} nodes from ${sourceName} (${tableCount} ${countLabel})`);
        }
        
    } catch (error) {
        console.error('Error loading knowledge graph:', error);
        const errorMsg = error?.message || error?.toString() || 'Unknown error';
        sap.m.MessageBox.error('Failed to load knowledge graph: ' + errorMsg);
    }
}


/**
 * Update graph statistics from backend response
 */
function updateGraphStatsFromBackend(stats) {
    const nodeText = sap.ui.getCore().byId("nodeCount");
    const edgeText = sap.ui.getCore().byId("edgeCount");
    
    if (nodeText) nodeText.setText((stats.node_count || 0).toString());
    if (edgeText) edgeText.setText((stats.edge_count || 0).toString());
}

/**
 * Update graph statistics from graph data arrays (fallback)
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
                color: { 
                    background: '#e3f2fd',  // Light blue background
                    border: '#1976d2',       // Dark blue border
                    highlight: {
                        background: '#bbdefb',
                        border: '#0d47a1'
                    }
                },
                font: { 
                    color: '#0d47a1',        // Dark blue text
                    size: 14,
                    bold: true
                }
            },
            table: {
                color: { 
                    background: '#e8f5e9',   // Light green background
                    border: '#388e3c',       // Dark green border
                    highlight: {
                        background: '#c8e6c9',
                        border: '#1b5e20'
                    }
                },
                font: { 
                    color: '#1b5e20',        // Dark green text
                    size: 11
                }
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

/**
 * Run centrality analysis
 */
async function runCentralityAnalysis() {
    try {
        const algorithmSelect = sap.ui.getCore().byId("centralityAlgorithmSelect");
        const algorithm = algorithmSelect ? algorithmSelect.getSelectedKey() : 'betweenness';
        
        const source = localStorage.getItem('selectedDataSource') || 'sqlite';
        
        console.log(`Running ${algorithm} centrality analysis...`);
        
        // Show loading
        const resultsText = sap.ui.getCore().byId("algorithmResults");
        if (resultsText) {
            resultsText.setText("Calculating centrality... ⏳");
        }
        
        // Call API
        const response = await fetch('/api/knowledge-graph/algorithms/centrality', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source, algorithm })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error?.message || 'Failed to calculate centrality');
        }
        
        // Display top 10 results
        const top10 = data.top_10 || [];
        let resultText = `Top 10 Most Critical Nodes (${algorithm}):\n`;
        top10.forEach((item, i) => {
            const nodeLabel = item.node.split('-').pop(); // Get last part of node ID
            resultText += `${i + 1}. ${nodeLabel}: ${item.score.toFixed(4)}\n`;
        });
        
        if (resultsText) {
            resultsText.setText(resultText);
        }
        
        // Color nodes by centrality in visualization
        if (network) {
            colorNodesByCentrality(data.scores);
        }
        
        sap.m.MessageToast.show(`Centrality calculated: ${Object.keys(data.scores).length} nodes analyzed`);
        
    } catch (error) {
        console.error('Error running centrality analysis:', error);
        const resultsText = sap.ui.getCore().byId("algorithmResults");
        if (resultsText) {
            resultsText.setText("Error: " + error.message);
        }
        sap.m.MessageBox.error('Failed to calculate centrality: ' + error.message);
    }
}

/**
 * Run community detection
 */
async function runCommunityDetection() {
    try {
        const algorithmSelect = sap.ui.getCore().byId("communityAlgorithmSelect");
        const algorithm = algorithmSelect ? algorithmSelect.getSelectedKey() : 'louvain';
        
        const source = localStorage.getItem('selectedDataSource') || 'sqlite';
        
        console.log(`Running ${algorithm} community detection...`);
        
        // Show loading
        const resultsText = sap.ui.getCore().byId("algorithmResults");
        if (resultsText) {
            resultsText.setText("Detecting communities... ⏳");
        }
        
        // Call API
        const response = await fetch('/api/knowledge-graph/algorithms/communities', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source, algorithm })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error?.message || 'Failed to detect communities');
        }
        
        // Display cluster statistics
        const clusterStats = data.cluster_stats || {};
        const numClusters = Object.keys(clusterStats).length;
        
        let resultText = `Found ${numClusters} communities (${algorithm}):\n`;
        Object.entries(clusterStats).forEach(([cluster, info]) => {
            resultText += `${cluster}: ${info.count} nodes\n`;
        });
        
        if (resultsText) {
            resultsText.setText(resultText);
        }
        
        // Color nodes by community in visualization
        if (network) {
            colorNodesByCommunity(data.communities);
        }
        
        sap.m.MessageToast.show(`Communities detected: ${numClusters} clusters found`);
        
    } catch (error) {
        console.error('Error running community detection:', error);
        const resultsText = sap.ui.getCore().byId("algorithmResults");
        if (resultsText) {
            resultsText.setText("Error: " + error.message);
        }
        sap.m.MessageBox.error('Failed to detect communities: ' + error.message);
    }
}

/**
 * Color nodes by centrality score
 */
function colorNodesByCentrality(scores) {
    if (!network) return;
    
    const nodes = network.body.data.nodes;
    const maxScore = Math.max(...Object.values(scores));
    
    // Generate color gradient from light to dark based on score
    nodes.forEach(node => {
        const score = scores[node.id] || 0;
        const intensity = score / maxScore;
        
        // Color gradient: light yellow (low) → dark red (high)
        const r = Math.round(255);
        const g = Math.round(255 * (1 - intensity * 0.7));
        const b = Math.round(255 * (1 - intensity));
        
        nodes.update({
            id: node.id,
            color: {
                background: `rgb(${r}, ${g}, ${b})`,
                border: '#d32f2f',
                highlight: {
                    background: `rgb(${r-20}, ${g-20}, ${b-20})`,
                    border: '#b71c1c'
                }
            },
            title: `${node.label}\nCentrality: ${score.toFixed(4)}`
        });
    });
    
    console.log('✓ Nodes colored by centrality');
}

/**
 * Color nodes by community
 */
function colorNodesByCommunity(communities) {
    if (!network) return;
    
    const nodes = network.body.data.nodes;
    
    // Generate distinct colors for each community
    const clusterColors = {
        'cluster_0': { bg: '#e3f2fd', border: '#1976d2' },
        'cluster_1': { bg: '#e8f5e9', border: '#388e3c' },
        'cluster_2': { bg: '#fff3e0', border: '#f57c00' },
        'cluster_3': { bg: '#f3e5f5', border: '#7b1fa2' },
        'cluster_4': { bg: '#fce4ec', border: '#c2185b' },
        'cluster_5': { bg: '#e0f2f1', border: '#00796b' }
    };
    
    // Update node colors
    nodes.forEach(node => {
        const cluster = communities[node.id];
        const colors = clusterColors[cluster] || { bg: '#eeeeee', border: '#757575' };
        
        nodes.update({
            id: node.id,
            color: {
                background: colors.bg,
                border: colors.border,
                highlight: {
                    background: colors.bg,
                    border: colors.border
                }
            },
            title: `${node.label}\nCommunity: ${cluster}`
        });
    });
    
    console.log('✓ Nodes colored by community');
}

/**
 * Refresh ontology cache
 * 
 * Clears and rebuilds the cached relationship discovery data.
 * Use this after schema changes or CSN updates.
 */
async function refreshOntologyCache() {
    try {
        console.log('Refreshing ontology cache...');
        
        const source = localStorage.getItem('selectedDataSource') || 'sqlite';
        
        // Show progress message
        sap.m.MessageToast.show('Refreshing ontology cache...');
        
        // Call cache refresh API
        const response = await fetch('/api/knowledge-graph/cache/refresh', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error?.message || 'Failed to refresh cache');
        }
        
        // Show success with statistics
        const stats = data.statistics;
        const message = `Cache refreshed! Discovered ${stats.discovered} relationships in ${stats.discovery_time_ms.toFixed(0)}ms`;
        
        sap.m.MessageBox.success(message, {
            title: "Cache Refreshed",
            onClose: function() {
                // Reload graph to show updated data
                loadKnowledgeGraph();
            }
        });
        
        console.log('✓ Cache refreshed:', stats);
        
    } catch (error) {
        console.error('Error refreshing cache:', error);
        sap.m.MessageBox.error('Failed to refresh cache: ' + error.message);
    }
}
