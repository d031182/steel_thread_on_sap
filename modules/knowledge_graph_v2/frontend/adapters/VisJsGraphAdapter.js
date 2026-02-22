/**
 * Vis.js Graph Adapter
 * 
 * Converts generic Graph domain objects to vis.js format.
 * 
 * Responsibilities:
 * - Convert GraphNode → vis.js node format
 * - Convert GraphEdge → vis.js edge format  
 * - Apply vis.js-specific styling
 * 
 * Does NOT:
 * - Manage graph lifecycle (GraphPresenter's job)
 * - Handle user interactions (GraphPresenter's job)
 * - Make API calls (KnowledgeGraphApiClient's job)
 */
class VisJsGraphAdapter {
    /**
     * Validate graph structure before conversion
     * 
     * @param {Object} graph - Generic graph to validate
     * @throws {Error} If graph structure is invalid
     */
    validateGraph(graph) {
        if (!graph) {
            throw new Error('Graph is null or undefined');
        }

        if (!graph.nodes || !Array.isArray(graph.nodes)) {
            throw new Error('Graph must have a nodes array');
        }

        if (!graph.edges || !Array.isArray(graph.edges)) {
            throw new Error('Graph must have an edges array');
        }

        // Validate node structure
        graph.nodes.forEach((node, index) => {
            if (!node.id) {
                throw new Error(`Node at index ${index} missing required 'id' field`);
            }
            if (!node.label) {
                console.warn(`[VisJsGraphAdapter] Node ${node.id} missing label`);
            }
        });

        // Validate edge structure
        graph.edges.forEach((edge, index) => {
            if (!edge.source_id) {
                throw new Error(`Edge at index ${index} missing required 'source_id' field`);
            }
            if (!edge.target_id) {
                throw new Error(`Edge at index ${index} missing required 'target_id' field`);
            }
        });

        console.log(`[VisJsGraphAdapter] Graph validated: ${graph.nodes.length} nodes, ${graph.edges.length} edges`);
    }

    /**
     * Convert generic Graph domain object to vis.js format
     * Alias for convertGraph() to match GraphPresenter interface
     * 
     * @param {Object} graph - Generic graph with nodes/edges arrays
     * @returns {Object} - {nodes: DataSet, edges: DataSet}
     */
    convertToVisJs(graph) {
        return this.convertGraph(graph);
    }

    /**
     * Convert generic Graph domain object to vis.js format
     * 
     * @param {Object} graph - Generic graph with nodes/edges arrays
     * @returns {Object} - {nodes: DataSet, edges: DataSet}
     */
    convertGraph(graph) {
        if (!graph || !graph.nodes || !graph.edges) {
            console.warn('[VisJsGraphAdapter] Invalid graph structure', graph);
            return {
                nodes: new vis.DataSet([]),
                edges: new vis.DataSet([])
            };
        }

        const nodes = graph.nodes.map(node => this.convertNode(node));
        const edges = graph.edges.map(edge => this.convertEdge(edge));

        return {
            nodes: new vis.DataSet(nodes),
            edges: new vis.DataSet(edges)
        };
    }

    /**
     * Convert generic GraphNode to vis.js node format
     * 
     * @param {Object} node - Generic node {id, label, type, properties}
     * @returns {Object} - Vis.js node format
     */
    convertNode(node) {
        const visNode = {
            id: node.id,
            label: node.label,
            tooltipHtml: this._buildNodeTooltip(node)  // Custom property for our tooltip
        };

        // Apply styling based on node type
        switch (node.type) {
            case 'product':
                visNode.color = {
                    background: '#E3F2FD',
                    border: '#1976D2',
                    highlight: {
                        background: '#BBDEFB',
                        border: '#0D47A1'
                    }
                };
                visNode.shape = 'box';
                visNode.font = { size: 16, bold: true };
                visNode.borderWidth = 2;
                break;

            case 'table':
                visNode.color = {
                    background: '#F3E5F5',
                    border: '#7B1FA2',
                    highlight: {
                        background: '#E1BEE7',
                        border: '#4A148C'
                    }
                };
                visNode.shape = 'ellipse';
                visNode.font = { size: 14 };
                break;

            default:
                visNode.color = {
                    background: '#E0E0E0',
                    border: '#616161',
                    highlight: {
                        background: '#BDBDBD',
                        border: '#212121'
                    }
                };
                visNode.shape = 'dot';
        }

        return visNode;
    }

    /**
     * Convert generic GraphEdge to vis.js edge format
     * 
     * Enhanced (HIGH-50): Display cardinality and ON conditions
     * 
     * @param {Object} edge - Generic edge {source_id, target_id, type, label, properties}
     * @returns {Object} - Vis.js edge format
     */
    convertEdge(edge) {
        const visEdge = {
            from: edge.source_id,
            to: edge.target_id,
            tooltipHtml: this._buildEdgeTooltip(edge)  // Custom property for our tooltip
        };

        // Apply styling based on edge type
        switch (edge.type) {
            case 'contains':
                visEdge.arrows = 'to';
                visEdge.color = {
                    color: '#1976D2',
                    highlight: '#0D47A1'
                };
                visEdge.width = 2;
                visEdge.label = 'contains';
                visEdge.font = { size: 12, color: '#1976D2' };
                break;

            case 'foreign_key':
                // Enhanced label with cardinality (HIGH-50)
                const cardinality = edge.properties?.cardinality;
                const fkColumn = edge.label || edge.properties?.fk_column;
                
                // Build label: "column_name [cardinality]"
                let label = fkColumn || 'FK';
                if (cardinality) {
                    label += ` [${cardinality}]`;
                }
                
                visEdge.label = label;
                visEdge.arrows = 'to';
                visEdge.color = {
                    color: '#7B1FA2',
                    highlight: '#4A148C'
                };
                visEdge.width = 1;
                visEdge.font = { size: 11, color: '#7B1FA2', align: 'top' };
                visEdge.smooth = { 
                    type: 'curvedCW', 
                    roundness: 0.2 
                };
                
                // Style composition relationships differently
                if (edge.properties?.is_composition) {
                    visEdge.dashes = true;
                    visEdge.width = 2;
                }
                
                // Style many-to-many relationships differently
                if (edge.properties?.is_many_to_many) {
                    visEdge.color = {
                        color: '#F57C00',
                        highlight: '#E65100'
                    };
                    visEdge.font = { size: 11, color: '#F57C00', align: 'top' };
                }
                break;

            default:
                visEdge.arrows = 'to';
                visEdge.color = '#757575';
                visEdge.label = edge.label || edge.type;
        }

        return visEdge;
    }

    /**
     * Build HTML tooltip for node (shown on hover)
     * 
     * @param {Object} node - Generic node
     * @returns {string} - HTML string for tooltip
     */
    _buildNodeTooltip(node) {
        let tooltip = `<div style="font-family: Arial, sans-serif; max-width: 300px;">`;
        tooltip += `<strong style="font-size: 14px; color: #1976D2;">${node.label}</strong><br>`;
        tooltip += `<em style="color: #666; font-size: 12px;">Type: ${node.type}</em><br>`;

        if (node.properties) {
            if (node.properties.description) {
                tooltip += `<br><span style="font-size: 12px;">${node.properties.description}</span>`;
            }

            if (node.properties.entity_label) {
                tooltip += `<br><span style="font-size: 12px; color: #666;">Label: ${node.properties.entity_label}</span>`;
            }

            // Show semantic summary if available (HIGH-30)
            if (node.properties.semantic_summary) {
                const summary = node.properties.semantic_summary;
                tooltip += `<br><br><strong style="font-size: 12px;">Semantic Annotations:</strong>`;
                tooltip += `<br><span style="font-size: 11px;">• ${summary.total_columns} columns</span>`;
                tooltip += `<br><span style="font-size: 11px;">• ${summary.labeled_columns} with labels</span>`;
                tooltip += `<br><span style="font-size: 11px;">• ${summary.semantic_columns} with semantics</span>`;
                tooltip += `<br><span style="font-size: 11px;">• ${summary.key_columns} key fields</span>`;
            }
        }

        tooltip += `</div>`;
        return tooltip;
    }

    /**
     * Build HTML tooltip for edge (shown on hover)
     * 
     * Enhanced (HIGH-50): Show cardinality and ON conditions
     * 
     * @param {Object} edge - Generic edge
     * @returns {string} - HTML string for tooltip
     */
    _buildEdgeTooltip(edge) {
        let tooltip = `<div style="font-family: Arial, sans-serif; max-width: 400px;">`;
        
        const props = edge.properties || {};
        
        // Edge type header
        tooltip += `<strong style="font-size: 13px; color: #7B1FA2;">`;
        if (edge.type === 'foreign_key') {
            tooltip += 'Foreign Key Relationship';
        } else if (edge.type === 'contains') {
            tooltip += 'Containment';
        } else {
            tooltip += edge.type;
        }
        tooltip += `</strong><br>`;

        // Basic info
        if (props.source_table && props.target_table) {
            tooltip += `<span style="font-size: 12px; color: #666;">`;
            tooltip += `${props.source_table} → ${props.target_table}`;
            tooltip += `</span><br>`;
        }

        if (props.fk_column) {
            tooltip += `<span style="font-size: 12px;">Column: <code style="background: #f5f5f5; padding: 2px 4px; border-radius: 3px;">${props.fk_column}</code></span><br>`;
        }

        // NEW: Cardinality (HIGH-50)
        if (props.cardinality) {
            tooltip += `<br><strong style="font-size: 12px; color: #F57C00;">Cardinality: ${props.cardinality}</strong><br>`;
        }

        // NEW: ON Conditions (HIGH-50)
        if (props.on_conditions && props.on_conditions.length > 0) {
            tooltip += `<br><strong style="font-size: 12px; color: #1976D2;">JOIN Conditions:</strong><br>`;
            props.on_conditions.forEach(condition => {
                tooltip += `<span style="font-size: 11px; font-family: monospace; color: #333;">• ${condition}</span><br>`;
            });
        } else if (props.join_clause) {
            // Fallback to formatted join_clause if on_conditions array not available
            tooltip += `<br><strong style="font-size: 12px; color: #1976D2;">JOIN:</strong><br>`;
            tooltip += `<span style="font-size: 11px; font-family: monospace; color: #333;">${props.join_clause}</span><br>`;
        }

        // Relationship type flags
        if (props.is_composition) {
            tooltip += `<br><span style="font-size: 11px; color: #F57C00;">⚡ Composition relationship</span><br>`;
        }
        
        if (props.is_many_to_many) {
            tooltip += `<br><span style="font-size: 11px; color: #F57C00;">⚡ Many-to-many relationship</span><br>`;
        }

        // Confidence indicator
        if (props.confidence !== undefined) {
            const confidenceColor = props.confidence > 0.8 ? '#4CAF50' : props.confidence > 0.5 ? '#FF9800' : '#F44336';
            tooltip += `<br><span style="font-size: 11px; color: ${confidenceColor};">Confidence: ${(props.confidence * 100).toFixed(0)}%</span>`;
            
            if (props.inferred) {
                tooltip += ` <em style="color: #999;">(inferred)</em>`;
            }
        }

        tooltip += `</div>`;
        return tooltip;
    }

    /**
     * Get default vis.js options for graph visualization
     * 
     * @returns {Object} - Vis.js options object
     */
    getDefaultOptions() {
        // Create custom tooltip element (will be shown/hidden by event handlers)
        this._createTooltipElement();

        return {
            nodes: {
                shape: 'dot',
                size: 16,
                font: {
                    size: 14,
                    face: 'Arial'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 1,
                shadow: true,
                smooth: {
                    type: 'continuous'
                }
            },
            physics: {
                stabilization: {
                    enabled: true,
                    iterations: 100
                },
                barnesHut: {
                    gravitationalConstant: -8000,
                    centralGravity: 0.3,
                    springLength: 200,
                    springConstant: 0.04,
                    damping: 0.09
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 200,
                navigationButtons: true,
                keyboard: true
            },
            layout: {
                improvedLayout: true,
                hierarchical: {
                    enabled: false
                }
            }
        };
    }

    /**
     * Create custom tooltip DOM element for HTML rendering
     * vis.js title attribute doesn't support HTML, so we use a custom approach
     */
    _createTooltipElement() {
        // Remove existing tooltip if present
        const existing = document.getElementById('vis-graph-tooltip');
        if (existing) {
            existing.remove();
        }

        // Create new tooltip element
        const tooltip = document.createElement('div');
        tooltip.id = 'vis-graph-tooltip';
        tooltip.style.cssText = `
            position: absolute;
            visibility: hidden;
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            z-index: 10000;
            max-width: 400px;
            pointer-events: none;
            font-family: Arial, sans-serif;
        `;
        document.body.appendChild(tooltip);

        this._tooltipElement = tooltip;
    }

    /**
     * Show custom tooltip at specified position
     * 
     * @param {string} htmlContent - HTML content to display
     * @param {number} x - X coordinate (page coordinates)
     * @param {number} y - Y coordinate (page coordinates)
     */
    _showTooltip(htmlContent, x, y) {
        if (!this._tooltipElement) {
            this._createTooltipElement();
        }

        this._tooltipElement.innerHTML = htmlContent;
        this._tooltipElement.style.left = (x + 10) + 'px';
        this._tooltipElement.style.top = (y + 10) + 'px';
        this._tooltipElement.style.visibility = 'visible';
    }

    /**
     * Hide custom tooltip
     */
    _hideTooltip() {
        if (this._tooltipElement) {
            this._tooltipElement.style.visibility = 'hidden';
        }
    }

    /**
     * Setup tooltip event handlers for network
     * Call this after creating the vis.Network instance
     * 
     * @param {vis.Network} network - vis.js network instance
     * @param {vis.DataSet} nodesDataSet - DataSet containing node data
     * @param {vis.DataSet} edgesDataSet - DataSet containing edge data
     */
    setupTooltipHandlers(network, nodesDataSet, edgesDataSet) {
        // Store references for tooltip content lookup
        this._nodesDataSet = nodesDataSet;
        this._edgesDataSet = edgesDataSet;

        // Show tooltip on hover
        network.on('hoverNode', (params) => {
            const node = nodesDataSet.get(params.node);
            if (node && node.tooltipHtml) {
                this._showTooltip(node.tooltipHtml, params.event.pageX, params.event.pageY);
            }
        });

        network.on('hoverEdge', (params) => {
            const edge = edgesDataSet.get(params.edge);
            if (edge && edge.tooltipHtml) {
                this._showTooltip(edge.tooltipHtml, params.event.pageX, params.event.pageY);
            }
        });

        // Hide tooltip when not hovering
        network.on('blurNode', () => {
            this._hideTooltip();
        });

        network.on('blurEdge', () => {
            this._hideTooltip();
        });

        // Hide tooltip on drag/zoom
        network.on('dragStart', () => {
            this._hideTooltip();
        });

        network.on('zoom', () => {
            this._hideTooltip();
        });

        console.log('✓ Custom tooltip handlers registered');
    }

    /**
     * Get hierarchical layout options (for tree-like structures)
     * 
     * @returns {Object} - Vis.js options with hierarchical layout
     */
    getHierarchicalOptions() {
        const options = this.getDefaultOptions();
        options.layout.hierarchical = {
            enabled: true,
            direction: 'UD',  // Up-Down
            sortMethod: 'directed',
            levelSeparation: 150,
            nodeSpacing: 200
        };
        options.physics.enabled = false;  // Disable physics for hierarchical layout
        return options;
    }

    /**
     * Filter graph by entity types
     * 
     * @param {Object} graph - Original graph {nodes, edges}
     * @param {Array<string>} entityTypes - Array of entity types to include
     * @returns {Object} - Filtered graph
     */
    filterByEntityTypes(graph, entityTypes) {
        if (!entityTypes || entityTypes.length === 0) {
            return graph;
        }

        const filteredNodes = graph.nodes.filter(node => {
            return entityTypes.includes(node.type) || 
                   entityTypes.includes(node.properties?.entity_type);
        });

        const nodeIds = new Set(filteredNodes.map(n => n.id));
        const filteredEdges = graph.edges.filter(edge => {
            return nodeIds.has(edge.source_id) && nodeIds.has(edge.target_id);
        });

        return {
            nodes: filteredNodes,
            edges: filteredEdges
        };
    }
}

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VisJsGraphAdapter;
}