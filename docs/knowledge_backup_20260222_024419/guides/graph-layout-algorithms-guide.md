# Graph Layout Algorithms - Decision Guide

**Purpose**: Choose the right network graph layout for your data visualization use case  
**Created**: February 4, 2026  
**Library**: vis.js Network (our current implementation)  
**Context**: Knowledge Graph visualization in P2P Data Products application

---

## Quick Decision Matrix

| Use Case | Recommended Layout | Why |
|----------|-------------------|------|
| **Hierarchies** (org charts, file trees) | Hierarchical (directed) | Shows clear parent-child relationships |
| **Database Schema** (tables + FK) | Hierarchical (sortMethod: directed) | Tables flow from products to dependencies |
| **Social Networks** | Force-Directed (barnesHut) | Clusters communities naturally |
| **Small Graphs** (<50 nodes) | Force-Directed (repulsion) | Fast, clear structure |
| **Large Graphs** (100+ nodes) | Force-Directed (barnesHut) | O(n log n) performance |
| **Circular Dependencies** | Force-Directed | Handles cycles gracefully |
| **Tree Structures** | Hierarchical (hubsize) | Emphasizes central nodes |

---

## Available Layouts in vis.js

### 1. Hierarchical Layout (Tree/DAG) 🌳

**Best For**: 
- Organizational charts
- File system trees
- Database schemas (products → tables → columns)
- Directed acyclic graphs (DAGs)
- Any data with clear parent-child relationships

**Configuration**:
```javascript
layout: {
    hierarchical: {
        enabled: true,
        direction: 'UD',        // Up-Down (also: DU, LR, RL)
        sortMethod: 'directed', // Follows edge direction
        levelSeparation: 150,   // Vertical spacing
        nodeSpacing: 100,       // Horizontal spacing
        treeSpacing: 200,       // Space between trees
        blockShifting: true,    // Optimize horizontal space
        edgeMinimization: true, // Reduce edge crossings
        parentCentralization: true // Center parent over children
    }
}
```

**Strengths**:
- ✅ Clear hierarchy visualization
- ✅ No overlapping nodes
- ✅ Predictable, stable layout
- ✅ Easy to trace relationships
- ✅ Good for presentations/documentation

**Weaknesses**:
- ❌ Doesn't handle cycles (circular dependencies)
- ❌ Can be very tall with deep hierarchies
- ❌ Less compact than force-directed

**Our Use Case**: Perfect for CSN schema graph (products → tables, tables → FK relationships)

---

### 2. Force-Directed Layout (Physics-Based) ⚡

**Best For**:
- Social networks (friends, followers)
- Knowledge graphs with complex relationships
- Graphs with cycles/loops
- Discovering clusters and communities
- Any graph where hierarchy isn't clear

**Configuration**:
```javascript
layout: {
    randomSeed: 42 // Reproducible layout
},
physics: {
    enabled: true,
    solver: 'barnesHut', // or 'forceAtlas2Based', 'repulsion'
    barnesHut: {
        gravitationalConstant: -2000,
        centralGravity: 0.3,
        springLength: 95,
        springConstant: 0.04,
        damping: 0.09,
        avoidOverlap: 0.5
    },
    stabilization: {
        enabled: true,
        iterations: 1000
    }
}
```

**Solvers Available**:

#### a) **barnesHut** (Default, Recommended)
- **Algorithm**: Barnes-Hut simulation (O(n log n))
- **Best for**: Large graphs (100-10,000 nodes)
- **Performance**: Fast, scalable
- **Quality**: Good clustering, natural communities
- **Use when**: Graph has >50 nodes

#### b) **forceAtlas2Based** 
- **Algorithm**: Force Atlas 2 (used by Gephi)
- **Best for**: Medium graphs (50-500 nodes)
- **Performance**: Slower than barnesHut
- **Quality**: Better clustering than barnesHut
- **Use when**: Visual quality > performance

#### c) **repulsion**
- **Algorithm**: Simple repulsion (O(n²))
- **Best for**: Small graphs (<50 nodes)
- **Performance**: Slow on large graphs
- **Quality**: Very clean, no overlaps
- **Use when**: Small graph, need perfect layout

**Strengths**:
- ✅ Handles any graph structure (including cycles)
- ✅ Automatic clustering (related nodes group together)
- ✅ Dynamic and interactive
- ✅ Discovers hidden patterns

**Weaknesses**:
- ❌ Non-deterministic (layout changes each time unless randomSeed set)
- ❌ Can be slow to stabilize (large graphs)
- ❌ Hard to find specific nodes (no fixed positions)
- ❌ May need manual tuning of physics parameters

---

### 3. Random Layout (Baseline)

**Best For**: Testing only (never use in production)

**Configuration**:
```javascript
layout: {
    randomSeed: 42 // At least make it reproducible
}
```

**When to use**: Never in production. Only for baseline comparison during development.

---

## Decision Framework

### Step 1: Identify Your Graph Type

**Is your data hierarchical?**
- ✅ YES → Hierarchical Layout
  - Example: Org chart, file tree, database schema
  
- ❌ NO → Force-Directed Layout
  - Example: Social network, knowledge graph, web pages

### Step 2: Consider Graph Size

| Size | Nodes | Recommended |
|------|-------|-------------|
| Tiny | 1-20 | Any layout works |
| Small | 20-50 | Repulsion (force) |
| Medium | 50-500 | BarnesHut (force) |
| Large | 500-5000 | BarnesHut + Clustering |
| Huge | 5000+ | Server-side pre-computation |

### Step 3: Consider User Task

**What is the user trying to do?**

**Trace relationships** (A→B→C)?
- → Hierarchical (easy to follow paths)

**Find clusters/communities**?
- → Force-Directed (automatic grouping)

**Overview/exploration**?
- → Force-Directed (discover patterns)

**Documentation/presentation**?
- → Hierarchical (clean, predictable)

---

## Our Implementation Decision

### Current: Hierarchical Layout

**Why we chose Hierarchical**:
1. ✅ Database schema is inherently hierarchical (products → tables)
2. ✅ FK relationships are directed (table A → table B)
3. ✅ Users need to trace data lineage (follow relationships)
4. ✅ Clean, predictable layout for documentation
5. ✅ No cycles in P2P schema (DAG structure)

**Configuration** (`app/static/js/ui/pages/knowledgeGraphPage.js`):
```javascript
layout: {
    hierarchical: {
        enabled: true,
        direction: 'UD',           // Top-down (products at top)
        sortMethod: 'directed',    // Follow edge direction
        levelSeparation: 150,
        nodeSpacing: 100,
        blockShifting: true,
        edgeMinimization: true,
        parentCentralization: true
    }
}
```

**Result**: 
- Products at top level (blue circles)
- Tables at lower levels (light blue rounded boxes)
- Clear visual hierarchy
- Easy to trace FK relationships

---

## Advanced Layout Techniques

### 1. Hierarchical Direction Options

```javascript
direction: 'UD'  // Up-Down (products on top) ← OUR CHOICE
direction: 'DU'  // Down-Up (products on bottom)
direction: 'LR'  // Left-Right (products on left)
direction: 'RL'  // Right-Left (products on right)
```

**Choose based on**:
- **UD/DU**: Best for wide graphs (many siblings)
- **LR/RL**: Best for deep graphs (many levels)
- **UD**: Most intuitive (matches mental model of "parent above child")

### 2. sortMethod Options

```javascript
sortMethod: 'directed'  // Follow edge direction ← OUR CHOICE
sortMethod: 'hubsize'   // Central nodes at top
```

**directed**: Use when edges have clear meaning (FK relationships, dependencies)  
**hubsize**: Use when central nodes are most important (social networks, APIs)

### 3. Physics Tuning (Force-Directed)

**Problem**: Graph too spread out?
```javascript
springLength: 50  // Shorter (more compact)
```

**Problem**: Nodes overlapping?
```javascript
avoidOverlap: 1.0  // Maximum avoidance
```

**Problem**: Unstable (keeps moving)?
```javascript
stabilization: {
    iterations: 2000  // More iterations
}
```

---

## When to Switch Layouts

### Scenario 1: Graph Has Cycles

**Problem**: Hierarchical layout fails with "Error: Cycle detected"

**Solution**: Switch to force-directed
```javascript
layout: { randomSeed: 42 },
physics: {
    enabled: true,
    solver: 'barnesHut'
}
```

### Scenario 2: Users Want to Explore

**Problem**: Hierarchical is too rigid, users want to rearrange manually

**Solution**: Enable draggable nodes + force-directed
```javascript
physics: {
    enabled: true,
    solver: 'barnesHut',
    stabilization: {
        enabled: true,
        fit: true
    }
},
interaction: {
    dragNodes: true
}
```

### Scenario 3: Too Many Nodes

**Problem**: Hierarchical layout too tall/wide with 500+ nodes

**Solution**: 
1. Add clustering (group related nodes)
2. Use force-directed with Barnes-Hut
3. Add search/filter to focus on subsets

---

## Layout Performance

### Hierarchical Layout

| Nodes | Layout Time | Recommendation |
|-------|-------------|----------------|
| 1-50 | <100ms | ✅ Instant |
| 50-200 | 100-500ms | ✅ Acceptable |
| 200-500 | 500ms-2s | ⚠️ Consider clustering |
| 500+ | 2s+ | ❌ Add filters/search |

**Characteristics**:
- Deterministic (same every time)
- Fast computation (no physics simulation)
- No stabilization wait time

### Force-Directed Layout

| Nodes | Stabilization | Recommendation |
|-------|---------------|----------------|
| 1-50 | <1s | ✅ Use repulsion solver |
| 50-200 | 1-3s | ✅ Use barnesHut |
| 200-1000 | 3-10s | ⚠️ Use barnesHut + clustering |
| 1000+ | 10s+ | ❌ Pre-compute server-side |

**Characteristics**:
- Non-deterministic (different each time unless randomSeed)
- Requires stabilization wait
- Can be tuned for performance vs quality

---

## Best Practices

### DO ✅

1. **Set randomSeed for reproducibility** (force-directed):
   ```javascript
   layout: { randomSeed: 42 }
   ```

2. **Match layout to data structure**:
   - Hierarchies → Hierarchical
   - Networks → Force-directed

3. **Test with real data** (not just toy examples):
   - 10 nodes looks good ≠ 100 nodes will work

4. **Provide layout controls**:
   - Zoom in/out
   - Pan
   - Fit to screen
   - Reset zoom

5. **Consider performance**:
   - Cache computed layouts
   - Add loading indicators
   - Disable physics after stabilization

### DON'T ❌

1. **Don't use force-directed for clear hierarchies**
   - Users will struggle to find the "top" of the graph

2. **Don't use hierarchical for graphs with cycles**
   - Will fail with cycle detection error

3. **Don't forget stabilization indicators**
   - Users need feedback during physics simulation

4. **Don't over-tune physics parameters**
   - Default values work well 90% of the time
   - Only adjust if specific visual problem

5. **Don't ignore mobile**
   - Touch controls need to work
   - Small screens need compact layouts

---

## Common Layout Problems & Solutions

### Problem 1: Hierarchical Graph Too Wide

**Symptom**: Graph extends beyond viewport horizontally

**Solutions**:
```javascript
// Option A: Increase level separation (make taller, narrower)
levelSeparation: 200  // Was 150

// Option B: Change direction to LR (left-right)
direction: 'LR'

// Option C: Add clustering for similar nodes
```

### Problem 2: Force-Directed Graph Unstable

**Symptom**: Nodes keep moving, never settles

**Solutions**:
```javascript
// Increase stabilization iterations
stabilization: {
    iterations: 2000  // Was 1000
}

// Reduce damping (nodes settle faster)
damping: 0.2  // Was 0.09

// Or disable physics after initial layout
physics: {
    enabled: false  // Static after initial layout
}
```

### Problem 3: Nodes Overlapping

**Symptom**: Labels unreadable, nodes on top of each other

**Solutions (Hierarchical)**:
```javascript
nodeSpacing: 150,  // Was 100
levelSeparation: 200  // Was 150
```

**Solutions (Force-Directed)**:
```javascript
barnesHut: {
    avoidOverlap: 1.0  // Maximum avoidance
}
```

### Problem 4: Graph Takes Too Long to Load

**Symptom**: Users wait 5-10 seconds for layout

**Solutions**:
1. **Cache the layout** (store node positions)
2. **Use hierarchical** (faster than force-directed)
3. **Add clustering** (reduce visible nodes)
4. **Pre-compute server-side** (for very large graphs)

---

## Advanced: Hybrid Approaches

### Approach 1: Hierarchical + Manual Adjustment

1. Start with hierarchical (automatic positioning)
2. Allow user to drag nodes for fine-tuning
3. Save custom positions to localStorage
4. Restore saved positions on reload

**Use when**: Need hierarchy + customization

### Approach 2: Force-Directed + Constraints

```javascript
physics: {
    enabled: true,
    solver: 'barnesHut',
    barnesHut: {
        gravitationalConstant: -2000,
        centralGravity: 0.3
    }
}

// Fix certain nodes in place
nodes: [
    { id: 1, fixed: { x: true, y: true }, x: 0, y: 0 }  // Pin root node
]
```

**Use when**: Need clustering + anchor points

### Approach 3: Server-Side Pre-Computation

**For very large graphs (5000+ nodes)**:

1. Compute layout server-side (Python/NetworkX)
2. Store x,y positions in database
3. Send pre-computed positions to frontend
4. Disable physics (instant render)

**Libraries**:
- Python: NetworkX + graphviz
- Neo4j: Built-in graph algorithms
- Gephi: Export layouts to JSON

---

## Vis.js Specific Tips

### Stabilization Options

```javascript
stabilization: {
    enabled: true,
    iterations: 1000,      // More = better layout, slower
    updateInterval: 50,    // UI update frequency
    onlyDynamicEdges: false,
    fit: true              // Auto-zoom to fit after stabilization
}
```

**Recommended values**:
- Small graphs (<50): iterations: 500
- Medium graphs (50-200): iterations: 1000
- Large graphs (200+): iterations: 2000

### Physics Solvers Comparison

| Solver | Speed | Quality | Use Case |
|--------|-------|---------|----------|
| barnesHut | Fast (O(n log n)) | Good | Large graphs (100+) |
| forceAtlas2Based | Medium | Better | Medium graphs (50-200) |
| repulsion | Slow (O(n²)) | Best | Small graphs (<50) |

**Our recommendation**: Start with barnesHut, only switch if layout quality poor

### Disable Physics After Stabilization

```javascript
network.on('stabilizationIterationsDone', () => {
    network.setOptions({ physics: false });
    // Now dragging nodes won't trigger re-layout
});
```

**Benefits**:
- ✅ Layout stays stable
- ✅ Dragging nodes doesn't move others
- ✅ Better performance
- ✅ Predictable behavior

---

## Industry Examples

### Database Tools

| Tool | Graph Type | Layout Choice |
|------|------------|---------------|
| pgAdmin | Schema (tables) | Hierarchical |
| MySQL Workbench | ERD | Hierarchical |
| Neo4j Browser | Property graph | Force-directed |
| DBeaver | Schema | Hierarchical |

**Pattern**: Database schemas → Hierarchical (clear structure)

### Knowledge Graphs

| Tool | Graph Type | Layout Choice |
|------|------------|---------------|
| Neo4j Bloom | Knowledge | Force-directed |
| Gephi | Networks | Force-directed |
| Cytoscape | Biological | Force-directed + Manual |
| GraphDB | RDF | Force-directed |

**Pattern**: Knowledge/semantic graphs → Force-directed (discover patterns)

### Analytics Tools

| Tool | Graph Type | Layout Choice |
|------|------------|---------------|
| Tableau | Relationships | Force-directed |
| Power BI | Hierarchies | Hierarchical |
| Grafana | Dependencies | Hierarchical (Directed) |

**Pattern**: Analytics → Match data structure

---

## Testing Your Layout Choice

### Evaluation Criteria

**After implementing a layout, ask**:

1. **Clarity** (5 = perfect, 1 = messy):
   - Can users immediately understand the structure?
   - Are relationships clear?
   - Is the hierarchy/clustering obvious?

2. **Performance** (5 = instant, 1 = slow):
   - How long to compute layout?
   - Is stabilization acceptable?
   - Can users interact smoothly?

3. **Stability** (5 = rock solid, 1 = chaotic):
   - Does layout stay consistent?
   - Can users find nodes easily?
   - Do interactions (drag, zoom) work well?

4. **Aesthetics** (5 = beautiful, 1 = ugly):
   - Does it look professional?
   - Are spaces used efficiently?
   - Is it pleasant to look at?

**Target scores**:
- Clarity: 4-5 (critical - users must understand quickly)
- Performance: 4-5 (< 2 seconds for medium graphs)
- Stability: 4-5 (predictable behavior)
- Aesthetics: 3-5 (good enough, not primary goal)

### A/B Testing Approach

1. Implement Layout A (e.g., hierarchical)
2. Get user feedback
3. Implement Layout B (e.g., force-directed)
4. Get user feedback
5. Choose based on scores + user preference

**Example from our project**:
- Tried force-directed first → Too chaotic for schema
- Switched to hierarchical → Perfect for our use case
- User happy, no further changes needed

---

## Migration Guide

### From Hierarchical → Force-Directed

```javascript
// BEFORE (Hierarchical)
layout: {
    hierarchical: {
        enabled: true,
        direction: 'UD',
        sortMethod: 'directed'
    }
}

// AFTER (Force-Directed)
layout: {
    randomSeed: 42  // Reproducible
},
physics: {
    enabled: true,
    solver: 'barnesHut',
    stabilization: {
        iterations: 1000
    }
}
```

### From Force-Directed → Hierarchical

```javascript
// BEFORE (Force-Directed)
layout: { randomSeed: 42 },
physics: { enabled: true }

// AFTER (Hierarchical)
layout: {
    hierarchical: {
        enabled: true,
        direction: 'UD',
        sortMethod: 'directed'
    }
},
physics: { enabled: false }  // Disable physics!
```

**Critical**: Always disable physics when using hierarchical!

---

## Future Enhancements

### 1. User-Selectable Layouts

**Feature**: Dropdown to switch between layouts

```javascript
// Layout selector in UI
<Select id="layoutSelect">
    <Option value="hierarchical">Hierarchical (Clear Structure)</Option>
    <Option value="force">Force-Directed (Discover Patterns)</Option>
</Select>

// Update on selection
onLayoutChange(layout) {
    const options = layout === 'hierarchical' 
        ? { layout: { hierarchical: { enabled: true } } }
        : { physics: { enabled: true } };
    
    network.setOptions(options);
    network.stabilize();
}
```

### 2. Layout Presets

**Feature**: Pre-configured layouts for common scenarios

```javascript
const LAYOUT_PRESETS = {
    'schema': {  // Database schema (our current)
        layout: { hierarchical: { direction: 'UD', sortMethod: 'directed' } }
    },
    'cluster': {  // Find communities
        physics: { solver: 'barnesHut' }
    },
    'compact': {  // Fit small screen
        layout: { hierarchical: { direction: 'LR', nodeSpacing: 50 } }
    }
};
```

### 3. Adaptive Layout

**Feature**: Automatically choose layout based on graph properties

```javascript
function selectOptimalLayout(graphData) {
    const nodeCount = graphData.nodes.length;
    const hasCycles = detectCycles(graphData.edges);
    
    if (hasCycles) {
        return 'force-directed';  // Hierarchical can't handle cycles
    } else if (nodeCount < 50) {
        return 'hierarchical';  // Clear structure for small graphs
    } else {
        return 'force-directed';  // Clustering for large graphs
    }
}
```

---

## References

**Vis.js Documentation**:
- Layout: https://visjs.github.io/vis-network/docs/network/layout.html
- Physics: https://visjs.github.io/vis-network/docs/network/physics.html
- Examples: https://visjs.github.io/vis-network/examples/

**Graph Layout Theory**:
- Force-Directed: Fruchterman-Reingold algorithm
- Hierarchical: Sugiyama framework (layered graph drawing)
- Barnes-Hut: Fast n-body simulation (O(n log n))

**Related Docs**:
- [[Graph Visualization Strategy]] - High-level visualization decisions
- [[Knowledge Graph Module]] - Implementation details
- `app/static/js/ui/pages/knowledgeGraphPage.js` - Our implementation

---

## Summary

**Key Takeaways**:

1. **Match layout to data structure**:
   - Hierarchies → Hierarchical layout
   - Networks → Force-directed layout

2. **Consider graph size**:
   - Small (<50) → Any layout
   - Medium (50-500) → barnesHut
   - Large (500+) → Pre-compute or cluster

3. **Optimize for user task**:
   - Trace relationships → Hierarchical
   - Explore patterns → Force-directed
   - Documentation → Hierarchical

4. **Our choice (Hierarchical) is correct**:
   - Database schema is inherently hierarchical
   - Users need clear structure
   - No cycles in our data
   - Performance is excellent

**When to reconsider**: If we add data graph mode with complex business relationships (e.g., customer → orders → invoices with cross-references), then force-directed might be better for that mode.

**Current status**: Layout choice is solid, no changes needed.

---

**Created**: February 4, 2026  
**Author**: AI Assistant (based on vis.js docs + industry research)  
**Status**: Reference guide for future layout decisions