# Knowledge Graph Semantic Enhancement - Implementation Plan

**Date**: 2026-02-21  
**Status**: APPROVED - Ready for Implementation  
**Goal**: Increase CSN semantic capture from 40% → 95% to enable AI Assistant query generation

---

## Overview

Current knowledge graph captures only ~40% of CSN semantics, preventing AI Assistant from generating SQL queries or answering user questions effectively. This plan implements a 3-phase enhancement to unlock AI capabilities.

**Key Documents**:
- Analysis: [[knowledge-graph-csn-semantic-completeness-analysis]]
- Requirements: [[knowledge-graph-ai-assistant-requirements]]

---

## Phase 1: Query Generation Foundation (7 days) ⭐ CRITICAL

**Goal**: Enable AI to generate JOIN queries and map user language to fields  
**Impact**: AI capability 10% → 60%

### Task CRIT-22: Capture Association ON Conditions (2 days) ⭐ HIGHEST PRIORITY

**Why**: AI cannot generate JOIN queries without knowing how entities relate

**Files to Modify**:
1. `core/services/csn_parser.py` (lines 150-200)
2. `core/services/relationship_mapper.py` (lines 80-120)
3. `modules/knowledge_graph_v2/backend/graph.py`

**Implementation**:

```python
# core/services/csn_parser.py
class CSNParser:
    def _parse_association(self, element_name: str, element_def: Dict) -> AssociationMetadata:
        """Extract complete association metadata including ON conditions"""
        
        # Extract target entity
        target = element_def.get('target', '')
        
        # Extract cardinality
        cardinality = element_def.get('cardinality', {})
        cardinality_max = cardinality.get('max', 1)
        
        # Extract foreign keys
        keys = element_def.get('keys', [])
        foreign_keys = []
        for key in keys:
            if 'ref' in key:
                foreign_keys.append({
                    'local_field': key['ref'][0] if isinstance(key['ref'], list) else key['ref']
                })
        
        # Extract ON conditions ⭐ NEW
        on_conditions = element_def.get('on', [])
        join_conditions = self._parse_on_conditions(on_conditions)
        
        return AssociationMetadata(
            name=element_name,
            target=target,
            cardinality='many' if cardinality_max == '*' else 'one',
            keys=foreign_keys,
            on_conditions=join_conditions  # ⭐ NEW
        )
    
    def _parse_on_conditions(self, on_clause: List) -> List[Dict]:
        """
        Parse ON condition into structured join information
        
        Example ON clause:
        [
            { "ref": ["SupplierID"] },
            "=",
            { "ref": ["to_Supplier", "SupplierID"] }
        ]
        
        Returns:
        [
            {
                "left_field": "SupplierID",
                "operator": "=",
                "right_entity": "to_Supplier",
                "right_field": "SupplierID"
            }
        ]
        """
        join_conditions = []
        
        # Parse ON clause (simplified for basic = comparisons)
        i = 0
        while i < len(on_clause):
            if isinstance(on_clause[i], dict) and 'ref' in on_clause[i]:
                left_ref = on_clause[i]['ref']
                left_field = left_ref[0] if isinstance(left_ref, list) else left_ref
                
                # Next should be operator
                if i + 1 < len(on_clause) and isinstance(on_clause[i + 1], str):
                    operator = on_clause[i + 1]
                    
                    # Next should be right side
                    if i + 2 < len(on_clause) and isinstance(on_clause[i + 2], dict):
                        right_ref = on_clause[i + 2]['ref']
                        
                        if isinstance(right_ref, list) and len(right_ref) >= 2:
                            join_conditions.append({
                                'left_field': left_field,
                                'operator': operator,
                                'right_entity': right_ref[0],
                                'right_field': right_ref[1]
                            })
                        
                        i += 3
                        continue
            
            i += 1
        
        return join_conditions
```

**Graph Storage Enhancement**:

```python
# modules/knowledge_graph_v2/backend/graph.py
class GraphService:
    def _build_relationship_edge(self, relationship: Dict) -> Dict:
        """Build edge with complete join metadata"""
        
        edge = {
            'id': f"{relationship['from_entity']}_to_{relationship['to_entity']}",
            'source': relationship['from_entity'],
            'target': relationship['to_entity'],
            'label': relationship['name'],
            'type': relationship['type'],
            
            # ⭐ NEW: Join metadata for AI query generation
            'join_metadata': {
                'on_conditions': relationship.get('on_conditions', []),
                'cardinality': relationship.get('cardinality', 'one'),
                'foreign_keys': relationship.get('keys', [])
            }
        }
        
        return edge
```

**Testing**:

```python
# tests/knowledge_graph_v2/test_on_condition_capture.py
def test_association_on_condition_extraction():
    """Test: ON conditions extracted from CSN"""
    parser = CSNParser('docs/csn')
    metadata = parser.get_entity_metadata('SupplierInvoice')
    
    # Find to_Supplier association
    supplier_assoc = next(
        (a for a in metadata.associations if a.name == 'to_Supplier'),
        None
    )
    
    assert supplier_assoc is not None
    assert len(supplier_assoc.on_conditions) > 0
    assert supplier_assoc.on_conditions[0]['left_field'] == 'SupplierID'
    assert supplier_assoc.on_conditions[0]['right_field'] == 'SupplierID'
    assert supplier_assoc.on_conditions[0]['operator'] == '='

def test_ai_join_query_generation():
    """Test: AI can generate JOIN query using ON conditions"""
    graph_service = GraphService()
    graph_data = graph_service.get_graph(source='sqlite', mode='schema')
    
    # Find relationship edge
    edge = next(
        (e for e in graph_data['edges'] 
         if e['source'] == 'SupplierInvoice' and e['target'] == 'Supplier'),
        None
    )
    
    assert edge is not None
    assert 'join_metadata' in edge
    assert len(edge['join_metadata']['on_conditions']) > 0
    
    # AI can now generate:
    # SELECT * FROM SupplierInvoice i
    # INNER JOIN Supplier s ON i.SupplierID = s.SupplierID
```

**Success Criteria**:
- ✅ All associations have ON conditions extracted
- ✅ Graph edges contain `join_metadata` with ON conditions
- ✅ AI Assistant can query graph for join paths
- ✅ Test coverage: 90%+

---

### Task HIGH-22: Capture Display Labels & Semantic Annotations (2 days)

**Why**: AI needs to map user's natural language ("amount", "company") to technical fields

**Files to Modify**:
1. `core/services/csn_parser.py` (ColumnMetadata dataclass)
2. `modules/knowledge_graph_v2/backend/graph.py`

**Implementation**:

```python
# core/services/csn_parser.py
@dataclass
class ColumnMetadata:
    """Column metadata with annotations"""
    name: str
    type: str
    length: Optional[int] = None
    is_key: bool = False
    is_nullable: bool = True
    
    # ⭐ NEW: Annotation metadata
    display_label: Optional[str] = None  # @title, @Common.Label
    description: Optional[str] = None    # @EndUserText.quickInfo
    semantic_type: Optional[str] = None  # @Semantics.amount, @Semantics.currencyCode
    semantic_properties: Dict[str, Any] = field(default_factory=dict)
    all_annotations: Dict[str, Any] = field(default_factory=dict)

class CSNParser:
    def _extract_column_metadata(self, col_name: str, col_def: Dict) -> ColumnMetadata:
        """Extract column with complete annotations"""
        
        # Extract display label
        display_label = (
            col_def.get('@title') or 
            col_def.get('@Common.Label') or 
            col_def.get('@EndUserText.label')
        )
        
        # Extract description
        description = (
            col_def.get('@EndUserText.quickInfo') or
            col_def.get('@Common.QuickInfo')
        )
        
        # Extract semantic type
        semantic_type = None
        semantic_properties = {}
        
        for key, value in col_def.items():
            if key.startswith('@Semantics.'):
                semantic_key = key.replace('@Semantics.', '')
                
                if '.' not in semantic_key:
                    # Primary semantic type (e.g., @Semantics.amount)
                    semantic_type = semantic_key
                else:
                    # Semantic property (e.g., @Semantics.amount.currencyCode)
                    parts = semantic_key.split('.', 1)
                    semantic_properties[parts[1]] = value
        
        # Extract all annotations
        all_annotations = {
            k: v for k, v in col_def.items() 
            if k.startswith('@')
        }
        
        return ColumnMetadata(
            name=col_name,
            type=col_def.get('type', 'unknown'),
            length=col_def.get('length'),
            is_key=col_def.get('key', False),
            is_nullable=not col_def.get('notNull', False),
            display_label=display_label,
            description=description,
            semantic_type=semantic_type,
            semantic_properties=semantic_properties,
            all_annotations=all_annotations
        )
```

**Success Criteria**:
- ✅ Display labels extracted for all annotated fields
- ✅ Semantic types (@Semantics.amount, etc.) captured
- ✅ AI can map "amount" → NetAmount field via semantic type
- ✅ Test coverage: 85%+

---

### Task HIGH-23: Capture Cardinality Metadata (1 day)

**Why**: AI needs to understand relationship types (1:1, 1:N, N:M) for query planning

**Implementation**: Already partially implemented in CRIT-22 above

**Success Criteria**:
- ✅ Cardinality captured for all associations
- ✅ Graph edges show relationship type (1:1, 1:N, N:M)
- ✅ AI can determine if relationship is one-to-many vs many-to-one

---

### Task HIGH-24: Add Annotation Query APIs (1 day)

**Why**: AI needs to search fields by semantic type or display label

**Files to Create**:
1. `modules/knowledge_graph_v2/backend/annotation_query_service.py`

**Implementation**:

```python
# modules/knowledge_graph_v2/backend/annotation_query_service.py
class AnnotationQueryService:
    """Query graph by annotation metadata"""
    
    def __init__(self, graph_service: GraphService):
        self.graph_service = graph_service
        self._annotation_index = None
    
    def find_fields_by_semantic_type(self, semantic_type: str) -> List[Dict]:
        """
        Find all fields with specific semantic type
        
        Example:
            find_fields_by_semantic_type('amount')
            # Returns: [
            #     {'entity': 'SupplierInvoice', 'field': 'NetAmount'},
            #     {'entity': 'PurchaseOrder', 'field': 'TotalAmount'}
            # ]
        """
        self._ensure_index()
        return self._annotation_index['semantic_types'].get(semantic_type, [])
    
    def find_fields_by_display_label(self, label: str) -> List[Dict]:
        """Find fields by display label (fuzzy match)"""
        self._ensure_index()
        results = []
        
        label_lower = label.lower()
        for field_id, field_label in self._annotation_index['display_labels'].items():
            if label_lower in field_label.lower():
                entity, field_name = field_id.split('.', 1)
                results.append({
                    'entity': entity,
                    'field': field_name,
                    'display_label': field_label
                })
        
        return results
    
    def get_aggregatable_fields(self, entity: str) -> List[str]:
        """Get fields that can be aggregated (SUM, AVG, etc.)"""
        # Fields with @Semantics.amount, @Analytics.Measure
        semantic_fields = self.find_fields_by_semantic_type('amount')
        return [
            f['field'] for f in semantic_fields 
            if f['entity'] == entity
        ]
```

**API Endpoint**:

```python
# modules/knowledge_graph_v2/backend/api.py
@knowledge_graph_v2_bp.route('/api/knowledge-graph-v2/query/by-semantic-type', methods=['GET'])
def query_by_semantic_type():
    """Query fields by semantic type (e.g., amount, currencyCode)"""
    semantic_type = request.args.get('type')
    
    if not semantic_type:
        return jsonify({'error': 'type parameter required'}), 400
    
    service = AnnotationQueryService(graph_service)
    fields = service.find_fields_by_semantic_type(semantic_type)
    
    return jsonify({'semantic_type': semantic_type, 'fields': fields})
```

**Success Criteria**:
- ✅ API endpoints for querying by semantic type, display label
- ✅ AI can find all "amount" fields across entities
- ✅ AI can find fields by fuzzy label match
- ✅ API contract tests pass

---

## Phase 2: Data Validation (5 days)

**Goal**: Enable AI to validate user input and explain constraints  
**Impact**: AI capability 60% → 90%

### Task MED-18: Capture Type Constraints (1 day)

**Implementation**: Extract length, precision, scale, notNull from CSN

### Task MED-19: Capture Value Lists (2 days)

**Implementation**: Extract @Common.ValueList configurations

### Task MED-20: Add Constraint Validation APIs (1 day)

**Implementation**: Create APIs to validate field values

### Task MED-21: Integration Testing (1 day)

**Implementation**: Test AI Assistant end-to-end with enhanced metadata

---

## Phase 3: Natural Language Understanding (3 days)

**Goal**: Enable AI to explain concepts and composition semantics  
**Impact**: AI capability 90% → 95%

### Tasks:
- Capture field descriptions (@EndUserText.quickInfo)
- Distinguish Composition vs Association semantics
- Add natural language query APIs

---

## Success Metrics

### Current State (40% semantic capture)
- ❌ AI can answer 10% of user questions
- ❌ Cannot generate JOIN queries
- ❌ Cannot validate data
- ❌ Cannot understand user terminology

### After Phase 1 (60% semantic capture)
- ✅ AI can answer 60% of user questions
- ✅ Can generate JOIN queries with ON conditions
- ✅ Can map user language to technical fields
- ✅ Can explain relationship types

### After Phase 2 (90% semantic capture)
- ✅ AI can answer 90% of user questions
- ✅ Can validate user input against constraints
- ✅ Can suggest valid values from value lists

### After Phase 3 (95% semantic capture)
- ✅ AI can answer 95% of user questions
- ✅ Can explain concepts in natural language
- ✅ Can explain composition semantics

---

## Testing Strategy

### Unit Tests (per task)
- CSN parser extracts all new metadata
- Graph service stores metadata correctly
- Query APIs return correct results

### Integration Tests (Phase 1 end)
- AI Assistant generates correct SQL JOIN query
- AI Assistant maps user language to fields
- AI Assistant explains relationship types

### E2E Tests (Phase 2 end)
- User asks "Show invoices for supplier ABC" → Correct query generated
- User asks "What's the total amount?" → Correct aggregation
- User inputs invalid value → Validation error with helpful message

---

## Risk Mitigation

**Risk 1**: ON condition parsing fails for complex CSN
- **Mitigation**: Start with simple = comparisons, add complex cases incrementally
- **Fallback**: Manual relationship definitions if parser fails

**Risk 2**: Performance degradation with annotation indexing
- **Mitigation**: Build index lazily, cache aggressively
- **Monitoring**: Track graph query performance before/after

**Risk 3**: Breaking changes to existing graph consumers
- **Mitigation**: Add new fields, keep existing fields unchanged
- **Testing**: Run full regression test suite

---

## Dependencies

- CSN files available in `docs/csn/`
- Knowledge Graph V2 module operational
- AI Assistant backend can query graph service
- Test environment with sample data

---

## Timeline

| Phase | Duration | Completion Date |
|-------|----------|-----------------|
| Phase 1: Query Generation | 7 days | 2026-02-28 |
| Phase 2: Data Validation | 5 days | 2026-03-05 |
| Phase 3: Natural Language | 3 days | 2026-03-08 |
| **Total** | **15 days** | **2026-03-08** |

---

## References

- Analysis Document: [[knowledge-graph-csn-semantic-completeness-analysis]]
- AI Requirements: [[knowledge-graph-ai-assistant-requirements]]
- CSN Parser: `core/services/csn_parser.py`
- Relationship Mapper: `core/services/relationship_mapper.py`
- Graph Service: `modules/knowledge_graph_v2/backend/graph.py`