/**
 * VisJsGraphAdapter
 * 
 * Converts generic graph format (from backend) to vis.js network format.
 * 
 * Architecture: Adapter Layer
 * Purpose: Format transformation (Generic → vis.js)
 * 
 * @author P2P Development Team
 * @version 1.0.0 (Phase 5.1 - Adapter Layer)
 * @date 2026-02-08
 */

class VisJsGraphAdapter {
    constructor() {
        // Node styling configuration by type
        this.nodeStyles = {
            TABLE: {
                shape: 'box',
                color: {
                    border: '#2B7CE9',
                    background: '#D2E5FF',
                    highlight: {
                        border: '#2B7CE9',
                        background: '#A4CAFE'
                    }
                },
                font: {
                    color: '#000000',
                    size: 14,
                    face: '72 Regular, sans-serif' // SAP 72 font
                },
                borderWidth: 2,
                borderWidthSelected: 3
            },
            VIEW: {
                shape: 'ellipse',
                color: {
                    border: '#FFA500',
                    background: '#FFE4B5',
                    highlight: {
                        border: '#FFA500',
                        background: '#FFD07A'
                    }
                },
                font: {
                    color: '#000000',
                    size: 14,
                    face: '72 Regular, sans-serif'
                },
                borderWidth: 2,
                borderWidthSelected: 3
            },
            SYNONYM: {
                shape: 'diamond',
                color: {
                    border: '#8B4513',
                    background: '#DEB887',
                    highlight: {
                        border: '#8B4513',
                        background: '#BCA068'
                    }
                },
                font: {
                    color: '#000000',
                    size: 14,
                    face: '72 Regular, sans-serif'
                },
                borderWidth: 2,
                borderWidthSelected: 3
            },
            // Default style for unknown types
            DEFAULT: {
                shape: 'dot',
                color: {
                    border: '#808080',
                    background: '#D3D3D3',
                    highlight: {
                        border: '#808080',
                        background: '#A9A9A9'
                    }
                },
                font: {
                    color: '#000000',
                    size: 14,
                    face: '72 Regular, sans-serif'
                },
                borderWidth: 2,
                borderWidthSelected: 3
            }
        };

        // Edge styling configuration by type
        this.edgeStyles = {
            FOREIGN_KEY: {
                color: { color: '#2B7CE9', highlight: '#1A5BB8' },
                arrows: { to: { enabled: true, scaleFactor: 1 } },
                width: 2,
                selectionWidth: 3,
                smooth: { type: 'continuous' }
            },
            ASSOCIATION: {
                color: { color: '#FFA500', highlight: '#FF8C00' },
                arrows: { to: { enabled: true, scaleFactor: 1 } },
                width: 2,
                selectionWidth: 3,
                smooth: { type: 'continuous' }
            },
            // Default edge style
            DEFAULT: {
                color: { color: '#808080', highlight: '#404040' },
                arrows: { to: { enabled: true, scaleFactor: 1 } },
                width: 2,
                selectionWidth: 3,
                smooth: { type: 'continuous' }
            }
        };
    }

    /**
     * Convert generic graph to vis.js format
     * 
     * @param {Object} genericGraph - Generic graph from backend
     * @param {Array} genericGraph.nodes - Array of generic nodes
     * @param {Array} genericGraph.edges - Array of generic edges
     * @returns {Object} vis.js compatible graph {nodes: DataSet, edges: DataSet}
     */
    convertToVisJs(genericGraph) {
        if (!genericGraph) {
            throw new Error('Generic graph is required');
        }

        if (!genericGraph.nodes || !Array.isArray(genericGraph.nodes)) {
            throw new Error('Generic graph must have nodes array');
        }

        if (!genericGraph.edges || !Array.isArray(genericGraph.edges)) {
            throw new Error('Generic graph must have edges array');
        }

        // Convert nodes
        const visNodes = genericGraph.nodes.map(node => this.convertNode(node));

        // Convert edges
        const visEdges = genericGraph.edges.map(edge => this.convertEdge(edge));

        return {
            nodes: visNodes,
            edges: visEdges
        };
    }

    /**
     * Convert a single generic node to vis.js format
     * 
     * @param {Object} genericNode - Generic node
     * @param {string} genericNode.id - Node ID
     * @param {string} genericNode.label - Node label
     * @param {string} genericNode.type - Node type (TABLE, VIEW, etc.)
     * @param {Object} genericNode.properties - Optional node properties
     * @returns {Object} vis.js node
     */
    convertNode(genericNode) {
        if (!genericNode || !genericNode.id) {
            throw new Error('Node must have an id');
        }

        // Get style for this node type
        const style = this.nodeStyles[genericNode.type] || this.nodeStyles.DEFAULT;

        // Build title (hover tooltip) with properties
        const title = this._buildNodeTitle(genericNode);

        return {
            id: genericNode.id,
            label: genericNode.label || genericNode.id,
            title: title,
            group: genericNode.type || 'DEFAULT',
            ...style, // Spread style properties
            // Store original data for reference
            originalData: genericNode
        };
    }

    /**
     * Convert a single generic edge to vis.js format
     * 
     * @param {Object} genericEdge - Generic edge
     * @param {string} genericEdge.source - Source node ID
     * @param {string} genericEdge.target - Target node ID
     * @param {string} genericEdge.label - Edge label
     * @param {string} genericEdge.type - Edge type (FOREIGN_KEY, etc.)
     * @returns {Object} vis.js edge
     */
    convertEdge(genericEdge) {
        if (!genericEdge || !genericEdge.source || !genericEdge.target) {
            throw new Error('Edge must have source and target');
        }

        // Get style for this edge type
        const style = this.edgeStyles[genericEdge.type] || this.edgeStyles.DEFAULT;

        return {
            from: genericEdge.source,
            to: genericEdge.target,
            label: genericEdge.label || '',
            title: `${genericEdge.type || 'LINK'}: ${genericEdge.source} → ${genericEdge.target}`,
            ...style, // Spread style properties
            // Store original data for reference
            originalData: genericEdge
        };
    }

    /**
     * Build HTML title (tooltip) for node
     * 
     * @private
     * @param {Object} node - Generic node
     * @returns {string} HTML title string
     */
    _buildNodeTitle(node) {
        let title = `<div class="node-tooltip">`;
        title += `<strong>${node.label || node.id}</strong><br/>`;
        title += `<em>Type: ${node.type || 'Unknown'}</em><br/>`;

        // Add properties if available
        if (node.properties && Object.keys(node.properties).length > 0) {
            title += `<br/><strong>Properties:</strong><br/>`;
            for (const [key, value] of Object.entries(node.properties)) {
                title += `${key}: ${value}<br/>`;
            }
        }

        title += `</div>`;
        return title;
    }

    /**
     * Get node style by type (for external use)
     * 
     * @param {string} nodeType - Node type
     * @returns {Object} Style object
     */
    getNodeStyle(nodeType) {
        return this.nodeStyles[nodeType] || this.nodeStyles.DEFAULT;
    }

    /**
     * Get edge style by type (for external use)
     * 
     * @param {string} edgeType - Edge type
     * @returns {Object} Style object
     */
    getEdgeStyle(edgeType) {
        return this.edgeStyles[edgeType] || this.edgeStyles.DEFAULT;
    }

    /**
     * Validate generic graph structure
     * 
     * @param {Object} graph - Graph to validate
     * @returns {boolean} True if valid
     * @throws {Error} If invalid
     */
    validateGraph(graph) {
        if (!graph) {
            throw new Error('Graph is required');
        }

        if (!graph.nodes || !Array.isArray(graph.nodes)) {
            throw new Error('Graph must have nodes array');
        }

        if (!graph.edges || !Array.isArray(graph.edges)) {
            throw new Error('Graph must have edges array');
        }

        // Validate each node has required fields
        graph.nodes.forEach((node, index) => {
            if (!node.id) {
                throw new Error(`Node at index ${index} missing id`);
            }
        });

        // Validate each edge has required fields
        graph.edges.forEach((edge, index) => {
            if (!edge.source || !edge.target) {
                throw new Error(`Edge at index ${index} missing source or target`);
            }
        });

        return true;
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VisJsGraphAdapter;
}