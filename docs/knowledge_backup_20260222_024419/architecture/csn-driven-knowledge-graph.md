# CSN-Driven Knowledge Graph Construction

**Date**: 2026-01-31  
**Context**: Using CSN metadata to build P2P data relationship graph efficiently

## Current Problem

**Manual relationship mapping is inefficient**:
- ❌ Hardcoded table relationships in `data_graph_service.py`
- ❌ Must manually update when schema changes
- ❌ Prone to errors and omissions
- ❌ Doesn't scale to 50+ tables

## Solution: CSN-Driven Graph Construction

**Use CSN metadata to automatically discover relationships**:
- ✅ CSN contains entity definitions
- ✅ CSN contains column naming conventions
- ✅ CSN shows primary keys
- ✅ Column names reveal relationships (naming patterns)

---

## CSN Metadata Available

### 1. Entity Structure
```python
entity = csn_parser.get_entity_metadata("PurchaseOrder")
# Returns:
# - name: "PurchaseOrder"
# - columns: [...] 
# - primary_keys: ["PurchaseOrder"]
# - label: "Purchase Order"
```

### 2. Column Metadata
```python
for column in entity.columns:
    # - column.name: "Supplier"
    # - column.type: "cds.String"
    # - column.is_key: False
    # - column.label: "Supplier"
```

### 3. Naming Convention Patterns

**FK columns follow predictable patterns**:
```
PurchaseOrderItem.PurchaseOrder → PurchaseOrder.PurchaseOrder
PurchaseOrderItem.Supplier → Supplier.Supplier
SupplierInvoice.Supplier → Supplier.Supplier
JournalEntry.CompanyCode → CompanyCode.CompanyCode
```

**Pattern**: `{ChildTable}.{ParentTable}` → `{ParentTable}.{ParentTable}`

---

## Proposed Implementation

### Phase 1: CSN-Based Relationship Discovery

```python
# core/services/relationship_mapper.py

class CSNRelationshipMapper:
    """Automatically discover relationships from CSN metadata"""
    
    def __init__(self, csn_parser: CSNParser):
        self.csn_parser = csn_parser
    
    def discover_relationships(self) -> List[Relationship]:
        """
        Scan all CSN entities and infer relationships from:
        1. Column naming patterns
        2. Primary key references
        3. Common FK naming conventions
        """
        relationships = []
        entities = self.csn_parser.list_entities()
        
        for entity_name in entities:
            entity = self.csn_parser.get_entity_metadata(entity_name)
            
            # Check each non-PK column
            for column in entity.columns:
                if column.is_key:
                    continue  # Skip PK columns
                
                # Check if column name matches another entity name
                if column.name in entities:
                    # This is likely a FK!
                    relationships.append(Relationship(
                        from_entity=entity_name,
                        from_column=column.name,
                        to_entity=column.name,
                        to_column=column.name,  # Usually same name
                        relationship_type="many-to-one",
                        inferred=True
                    ))
        
        return relationships
```

### Phase 2: Integrate with Knowledge Graph

```python
# modules/knowledge_graph/backend/data_graph_service.py

class DataGraphService:
    def __init__(self, data_source: DataSource, csn_parser: CSNParser):
        self.data_source = data_source
        self.relationship_mapper = CSNRelationshipMapper(csn_parser)
    
    def build_graph(self, schema: str) -> Dict:
        """Build graph using CSN-discovered relationships"""
        
        # 1. Get all entities from CSN
        entities = self.csn_parser.list_entities()
        
        # 2. Discover relationships automatically
        relationships = self.relationship_mapper.discover_relationships()
        
        # 3. Query data for each entity
        nodes = []
        edges = []
        
        for entity in entities:
            # Query entity data
            data = self.data_source.query_table(schema, entity, limit=100)
            
            # Create nodes from data
            for row in data['rows']:
                nodes.append({
                    'id': f"{entity}:{row[pk]}",
                    'label': entity,
                    'properties': row
                })
        
        # 4. Create edges from discovered relationships
        for rel in relationships:
            # Query and match data
            edges.extend(self._create_edges_for_relationship(rel, data))
        
        return {'nodes': nodes, 'edges': edges}
```

---

## Benefits

### 1. Automatic Discovery ✅
```python
# Instead of hardcoding:
relationships = [
    ("PurchaseOrderItem", "PurchaseOrder", "PurchaseOrder"),
    ("PurchaseOrderItem", "Supplier", "Supplier"),
    # ... 50+ more relationships
]

# CSN automatically discovers ALL relationships:
relationships = relationship_mapper.discover_relationships()
# Returns 100+ relationships automatically!
```

### 2. Self-Maintaining ✅
- Schema changes in CSN → Graph adapts automatically
- Add new tables → Relationships auto-discovered
- Rename columns → Pattern matching updates

### 3. Accurate ✅
- Based on actual schema metadata
- Uses SAP naming conventions
- Leverages primary key information

### 4. Efficient ✅
- One-time CSN parsing
- Cached relationship mappings
- No manual maintenance

---

## Implementation Plan

### Step 1: Create Relationship Mapper (30 min)
**File**: `core/services/relationship_mapper.py`
- Implement `CSNRelationshipMapper` class
- Add relationship discovery logic
- Use naming pattern matching

### Step 2: Extend CSN Parser (15 min)
**Update**: `core/services/csn_parser.py`
- Add `get_potential_foreign_keys()` method
- Return columns that match other entity names

### Step 3: Update Data Graph Service (45 min)
**Update**: `modules/knowledge_graph/backend/data_graph_service.py`
- Inject `CSNParser` dependency
- Use `CSNRelationshipMapper`
- Remove hardcoded relationships

### Step 4: Add Caching (15 min)
**Update**: `core/services/relationship_mapper.py`
- Cache discovered relationships
- Refresh only when CSN changes

### Step 5: Test (30 min)
**Create**: `modules/knowledge_graph/tests/test_relationship_mapper.py`
- Test discovery logic
- Verify all P2P relationships found
- Check performance

**Total time**: ~2.5 hours

---

## Example: Discovered Relationships

```python
# CSN-based discovery would find:

[
    # Purchase Orders
    Relationship("PurchaseOrderItem", "PurchaseOrder", "PurchaseOrder", "PurchaseOrder"),
    Relationship("PurchaseOrderItem", "Supplier", "Supplier", "Supplier"),
    Relationship("PurchaseOrderItem", "Product", "Product", "Product"),
    
    # Supplier Invoices
    Relationship("SupplierInvoice", "Supplier", "Supplier", "Supplier"),
    Relationship("SupplierInvoiceItem", "SupplierInvoice", "SupplierInvoice", "SupplierInvoice"),
    Relationship("SupplierInvoiceItem", "PurchaseOrder", "PurchaseOrder", "PurchaseOrder"),
    
    # Journal Entries
    Relationship("JournalEntry", "CompanyCode", "CompanyCode", "CompanyCode"),
    Relationship("JournalEntry", "Supplier", "Supplier", "Supplier"),
    
    # Service Entry Sheets
    Relationship("ServiceEntrySheet", "PurchaseOrder", "PurchaseOrder", "PurchaseOrder"),
    
    # ... and 50+ more, ALL discovered automatically!
]
```

---

## Advanced: Confidence Scoring

```python
class Relationship:
    def __init__(self, from_entity, from_column, to_entity, to_column):
        self.from_entity = from_entity
        self.from_column = from_column
        self.to_entity = to_entity
        self.to_column = to_column
        self.confidence = self._calculate_confidence()
    
    def _calculate_confidence(self) -> float:
        """Calculate confidence that this is a real relationship"""
        score = 0.0
        
        # Exact name match (strongest signal)
        if self.from_column == self.to_entity:
            score += 0.8
        
        # Column matches target PK
        if self.to_column in target_entity.primary_keys:
            score += 0.2
        
        # Data type compatibility
        if self.from_column.type == self.to_column.type:
            score += 0.1
        
        return min(score, 1.0)
```

---

## Next Steps

**Immediate** (Do this):
1. ✅ Create `CSNRelationshipMapper` class
2. ✅ Integrate with `DataGraphService`
3. ✅ Test with P2P schema
4. ✅ Remove hardcoded relationships

**Future Enhancements**:
- Add manual override capability (for non-standard relationships)
- Support compound FK relationships
- Add relationship validation (check data actually matches)
- Generate relationship documentation automatically

---

## Conclusion

**YES - CSN is perfect for this!** ✅

**Benefits**:
- 🚀 Automatic discovery of 100+ relationships
- 🔄 Self-maintaining (adapts to schema changes)
- ✅ Accurate (based on actual metadata)
- ⚡ Efficient (one-time parsing, cached results)

**Current state**: Manual relationship mapping (inefficient)  
**With CSN**: Automatic relationship discovery (optimal)

**Recommendation**: Implement `CSNRelationshipMapper` to make knowledge graph construction intelligent and maintainable!

---

## References

- [[CSN Parser]] - `core/services/csn_parser.py`
- [[Data Graph Service]] - `modules/knowledge_graph/backend/data_graph_service.py`
- [[Graph Visualization Strategy]] - `docs/knowledge/guidelines/graph-visualization-strategy.md`