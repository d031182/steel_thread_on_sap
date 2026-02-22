# vis.js Library Reference

**Type**: JavaScript Visualization Library  
**Purpose**: Network graph visualization for Knowledge Graph V2  
**Official Docs**: https://visjs.github.io/vis-network/docs/  
**GitHub**: https://github.com/visjs  
**Status**: Active (Used in [[knowledge-graph-v2-phase-5-frontend-architecture]])

---

## Overview

vis.js is a dynamic, browser-based visualization library designed for ease of use and handling large amounts of dynamic data. It provides multiple visualization components, with **Network** being the core component used for our knowledge graph visualization.

### Core Modules
- **Network**: Interactive network graphs (nodes and edges) - **PRIMARY USE CASE**
- **Timeline**: Timeline visualizations
- **Graph2d**: 2D graph plotting
- **Graph3d**: 3D graph rendering
- **DataSet**: Data management component

---

## Network Visualization (Primary Component)

### Key Features

1. **Dynamic & Automatic Organization**
   - Displays network views with automatic layout
   - Physics-based positioning (spring lengths)
   - Self-organizing graph structures

2. **Customization**
   - Custom shapes (image, circularImage, ellipse, etc.)
   - Styles, colors, sizes
   - Images as node representations
   - Animations with configurable duration and easing

3. **Interactivity**
   - Drag nodes
   - Click/select elements
   - Hover tooltips
   - Touch support for mobile

4. **Performance**
   - Smooth operation on modern browsers (Chrome, Firefox, Opera, Safari, IE9+)
   - Mobile-optimized with touch support
   - Handles large datasets efficiently

---

## Data Structure

### Nodes
**Required Properties**:
- `id`: Number or string (unique identifier)

**Optional Properties**:
- `label`: Display text
- `title`: Hover tooltip text
- `shape`: Visual representation (image, circularImage, ellipse, box, etc.)
- `value`: Used for scaling
- `widthConstraint`: Min/max width with valign
- `heightConstraint`: Min/max height
- `color`: Node color
- `size`: Node size

**Example**:
```javascript
{
  id: 1,
  label: 'Entity Name',
  title: 'Hover text',
  shape: 'circularImage',
  image: '/path/to/image.png'
}
```

### Edges
**Required Properties**:
- `from`: Source node ID
- `to`: Target node ID

**Optional Properties**:
- `label`: Edge label
- `title`: Hover tooltip
- `length`: Physics spring length
- `dashes`: Boolean or array for dashed lines
- `arrows`: Arrow configuration

**Example**:
```javascript
{
  from: 1,
  to: 2,
  label: 'relates_to',
  length: 200,
  dashes: false
}
```

---

## DataSet Component

Used for managing unstructured data with reactive updates.

**Operations**:
- `add(items)`: Add new items
- `update(items)`: Update existing items
- `remove(id)`: Remove items
- `on('add/update/remove', callback)`: Listen for changes

**Example**:
```javascript
const nodes = new vis.DataSet([
  {id: 1, label: 'Node 1'},
  {id: 2, label: 'Node 2'}
]);

const edges = new vis.DataSet([
  {from: 1, to: 2}
]);

// Listen for changes
nodes.on('add', (event, properties) => {
  console.log('Nodes added:', properties.items);
});
```

---

## Initialization Pattern

```javascript
// 1. Get container element
const container = document.getElementById('network');

// 2. Prepare data
const data = {
  nodes: new vis.DataSet([
    {id: 1, label: 'Node 1'},
    {id: 2, label: 'Node 2'}
  ]),
  edges: new vis.DataSet([
    {from: 1, to: 2}
  ])
};

// 3. Configure options
const options = {
  nodes: {
    shape: 'dot',
    scaling: {
      min: 10,
      max: 30
    }
  },
  edges: {
    width: 2,
    smooth: true
  },
  physics: {
    stabilization: false
  }
};

// 4. Create network
const network = new vis.Network(container, data, options);
```

---

## Events

### Node/Edge Events
- `click`: User clicks on node/edge
- `select`: Selection changes
- `dragStart`: Drag begins
- `dragging`: During drag
- `dragEnd`: Drag completes
- `hoverNode`: Mouse over node
- `blurNode`: Mouse leaves node

### Network Events
- `animationFinished`: Animation completes
- `resize`: Container resizes
- `stabilizationIterationsDone`: Physics stabilization complete

**Event Handling Example**:
```javascript
network.on('click', function(params) {
  if (params.nodes.length > 0) {
    const nodeId = params.nodes[0];
    console.log('Clicked node:', nodeId);
  }
});
```

---

## Key Methods

### Navigation
- `focusOnNode(nodeId, options)`: Center and zoom on node
- `fit(options)`: Fit entire network in view
- `moveTo(options)`: Move to specific position/zoom

### Data Manipulation
- `setData(data)`: Replace all data
- `addNodeMode()`: Enable node adding mode
- `addEdgeMode()`: Enable edge connecting mode
- `deleteSelected()`: Remove selected items

### Utility
- `releaseNode()`: Stop dragging programmatically
- `DOMtoCanvas(position)`: Convert DOM coordinates to canvas
- `canvasToDOM(position)`: Convert canvas coordinates to DOM
- `getPositions([nodeIds])`: Get node positions
- `getSelectedNodes()`: Get selected node IDs
- `getSelectedEdges()`: Get selected edge IDs

---

## Animations

Configurable with `duration` (milliseconds) and easing functions.

**Easing Functions**:
- `linear`: Constant speed
- `easeInQuad`: Slow start, fast end
- `easeOutQuad`: Fast start, slow end
- `easeInOutQuad`: Slow start and end
- `easeInCubic`, `easeOutCubic`, `easeInOutCubic`: Cubic variations
- Many more cubic, quartic, quintic variations

**Example**:
```javascript
network.moveTo({
  position: {x: 0, y: 0},
  scale: 1.5,
  animation: {
    duration: 1000,
    easingFunction: 'easeInOutQuad'
  }
});
```

---

## Performance Considerations

1. **Large Datasets**
   - vis.js handles thousands of nodes efficiently
   - Use clustering for very large graphs
   - Disable physics for static graphs

2. **Mobile Optimization**
   - Touch events fully supported
   - Pinch-to-zoom enabled
   - Responsive to viewport changes

3. **Browser Compatibility**
   - Chrome: Excellent
   - Firefox: Excellent
   - Safari: Excellent
   - Edge: Excellent
   - IE9+: Good (legacy support)

---

## Integration Ecosystem

### Official Packages
- `vis-network`: Core network visualization
- `vis-data`: DataSet and DataView components
- `vis-timeline`: Timeline component
- `vis-graph3d`: 3D graph rendering

### Third-Party Integrations
- **R**: `visNetwork` package (CRAN)
- **Neo4j**: `neovis.js` for graph database visualization
- **React**: Community wrappers available
- **Angular**: Community wrappers available

---

## Usage in Knowledge Graph V2

**Current Implementation** (see [[knowledge-graph-v2-phase-5-frontend-architecture]]):

```javascript
// modules/knowledge_graph_v2/frontend/presenters/GraphPresenter.js
class GraphPresenter {
  initializeNetwork(container, data, options) {
    this.network = new vis.Network(container, data, options);
    this._setupEventHandlers();
  }
  
  _setupEventHandlers() {
    this.network.on('click', this._handleNodeClick.bind(this));
    this.network.on('stabilizationIterationsDone', () => {
      this.network.setOptions({ physics: false });
    });
  }
}
```

**Key Features Used**:
1. ✅ Dynamic node/edge rendering from API data
2. ✅ Physics-based layout with spring lengths
3. ✅ Click events for node selection
4. ✅ Hover tooltips for entity details
5. ✅ DataSet for reactive updates
6. ✅ Stabilization for initial layout
7. ✅ Custom styling per entity type

---

## Dynamic Color & Theme APIs ⭐ CRITICAL

### setOptions() - Primary Theme API

**Primary Method**: `network.setOptions(newOptions)`

**Purpose**: Updates graph styling dynamically at runtime without recreating the network.

**Key Features**:
- ✅ **Runtime Updates**: Changes colors instantly without page reload
- ✅ **No Network Recreation**: Preserves graph state and position
- ✅ **Propagates to New Data**: New nodes/edges inherit updated styles
- ✅ **Performance**: Lightweight operation, no re-layout needed

**Configuration Structure**:
```javascript
const options = {
  nodes: {
    color: {
      background: '#97C2FC',
      border: '#2B7CE9',
      highlight: {
        background: '#D2E5FF',
        border: '#2B7CE9'
      },
      hover: {
        background: '#E5F2FF',
        border: '#2B7CE9'
      }
    }
  },
  edges: {
    color: {
      color: '#2B7CE9',
      highlight: '#D2E5FF',
      hover: '#97C2FC',
      opacity: 1.0
    }
  },
  groups: {
    'TABLE': {
      color: {
        background: '#EBF5FE',
        border: '#0070F2'
      }
    },
    'VIEW': {
      color: {
        background: '#FEF7F1',
        border: '#E9730C'
      }
    }
  }
};

// Apply theme
network.setOptions(options);
```

### Groups System - Best Practice for Color Palettes

**Concept**: Nodes assigned a `group` property share styling via centralized group definitions.

**Why Use Groups**:
1. **Color Palette Management**: Define themes once, apply to many nodes
2. **Consistency**: All nodes in group inherit same colors
3. **Easy Theme Switching**: Change group definition, all nodes update
4. **Semantic Meaning**: Groups represent node types (TABLE, VIEW, etc.)

**Implementation**:
```javascript
// 1. Define nodes with group
const nodes = [
  { id: 1, label: 'Users', group: 'TABLE' },
  { id: 2, label: 'UserView', group: 'VIEW' },
  { id: 3, label: 'UserAlias', group: 'SYNONYM' }
];

// 2. Define group styles in options
const options = {
  groups: {
    TABLE: {
      color: {
        background: '#EBF5FE',  // SAP Brand Blue light
        border: '#0070F2'        // SAP Brand Blue
      },
      shape: 'box'
    },
    VIEW: {
      color: {
        background: '#FEF7F1',  // SAP Warning Orange light
        border: '#E9730C'        // SAP Warning Orange
      },
      shape: 'ellipse'
    },
    SYNONYM: {
      color: {
        background: '#F1FAF4',  // SAP Success Green light
        border: '#107E3E'        // SAP Success Green
      },
      shape: 'diamond'
    }
  }
};

// 3. Create network
const network = new vis.Network(container, { nodes, edges }, options);
```

**Current Usage**: Already implemented in `VisJsGraphAdapter.js` with SAP Fiori colors!

### Dynamic Theme Switching Pattern

**Use Case**: Support light/dark modes, user preferences, accessibility themes

**Implementation**:
```javascript
// Define multiple theme palettes
const sapFioriLight = {
  nodes: {
    color: {
      background: '#FFFFFF',
      border: '#89919A'
    }
  },
  edges: {
    color: '#0070F2'
  },
  groups: {
    TABLE: {
      color: {
        background: '#EBF5FE',
        border: '#0070F2'
      }
    },
    VIEW: {
      color: {
        background: '#FEF7F1',
        border: '#E9730C'
      }
    }
  }
};

const sapFioriDark = {
  nodes: {
    color: {
      background: '#32363A',
      border: '#6A6D70'
    }
  },
  edges: {
    color: '#89919A'
  },
  groups: {
    TABLE: {
      color: {
        background: '#1D3557',
        border: '#457B9D'
      }
    },
    VIEW: {
      color: {
        background: '#3E2723',
        border: '#FF6F00'
      }
    }
  }
};

// Switch themes dynamically
function applyTheme(isDark) {
  const theme = isDark ? sapFioriDark : sapFioriLight;
  network.setOptions(theme);
  // Optional: redraw if layout changes needed
  // network.redraw();
}

// Trigger on button click or user preference
document.getElementById('theme-toggle').addEventListener('click', () => {
  const isDark = document.body.classList.toggle('dark-mode');
  applyTheme(isDark);
});
```

**Future Enhancement**: SAP Fiori Horizon Dark Mode support for Knowledge Graph V2.

### Edge Color Flexibility

**Three Ways to Set Edge Colors**:

1. **Simple String**:
```javascript
edges: {
  color: '#2B7CE9'  // All edges use this color
}
```

2. **Detailed Object**:
```javascript
edges: {
  color: {
    color: '#2B7CE9',      // Default color
    highlight: '#D2E5FF',  // Selected edge
    hover: '#97C2FC',      // Mouse over
    opacity: 1.0,          // Transparency
    inherit: 'from'        // Inherit from source node
  }
}
```

3. **Function (Advanced)**:
```javascript
edges: {
  color: function(edge) {
    // Dynamic color based on edge properties
    if (edge.type === 'FOREIGN_KEY') return '#0070F2';
    if (edge.type === 'ASSOCIATION') return '#E9730C';
    return '#89919A';
  }
}
```

### Performance Tips

1. **Avoid Unnecessary Redraws**:
   - `setOptions()` is lightweight, no need to call `redraw()` unless layout changes
   - Theme updates propagate automatically to new nodes/edges

2. **Batch Updates**:
   - Update all color-related options in one `setOptions()` call
   - Better performance than multiple calls

3. **DataSet Propagation**:
   - New nodes added via `nodes.add()` automatically inherit group styles
   - No need to manually apply colors to new data

**Example**:
```javascript
// ✅ GOOD: Single setOptions call
network.setOptions({
  nodes: { color: {...} },
  edges: { color: {...} },
  groups: { TABLE: {...}, VIEW: {...} }
});

// ❌ BAD: Multiple setOptions calls
network.setOptions({ nodes: { color: {...} } });
network.setOptions({ edges: { color: {...} } });
network.setOptions({ groups: { TABLE: {...} } });
```

---

## References

- **Official Documentation**: https://visjs.github.io/vis-network/docs/
- **GitHub Repository**: https://github.com/visjs
- **Examples**: https://visjs.github.io/vis-network/examples/
- **DataSet Docs**: https://visjs.github.io/vis-data/
- **R Integration**: https://cran.r-project.org/web/packages/visNetwork/

---

## Related Documentation

- [[knowledge-graph-v2-phase-5-frontend-architecture]] - Implementation details
- [[knowledge-graph-v2-api-design]] - Backend API integration
- [[GraphPresenter]] - Presenter layer using vis.js
- [[KnowledgeGraphApiClient]] - Data fetching adapter

---

**Last Updated**: 2026-02-15  
**Version**: vis-network 9.x (current stable)