# HIGH-32: Query Templates Implementation - Phase 4

**Date**: 2026-02-21  
**Status**: IN PROGRESS  
**Goal**: Implement reusable query templates and validation patterns for Knowledge Graph V2

---

## Overview

Phase 4 builds on completed phases (HIGH-31: Analytics, HIGH-33: CSS/DI, HIGH-39: Grid Layout) to provide:
1. **Query Template Library**: Reusable SQL patterns for common scenarios
2. **Template Validation**: Type-safe query building with validation
3. **Template Discovery API**: Find templates matching query intent
4. **Query Result Caching**: Cache template results for performance

---

## Architecture

### QueryTemplate Dataclass

```python
@dataclass
class QueryTemplate:
    """Reusable query template with validation"""
    id: str                           # Unique identifier (e.g., 'supplier_invoices_by_vendor')
    name: str                         # Display name
    description: str                  # User-facing description
    category: str                     # Category (e.g., 'supplier', 'invoice', 'analytics')
    sql_template: str                 # SQL with placeholders: {entity}, {field}, {where_clause}
    parameters: List[TemplateParam]   # Required/optional parameters
    result_schema: Dict[str, str]    # Expected result columns: {name: type}
    examples: List[Dict]              # Usage examples
    tags: List[str]                   # Searchable tags
```

### TemplateParam Dataclass

```python
@dataclass
class TemplateParam:
    """Template parameter definition"""
    name: str
    type: str                         # 'entity', 'field', 'date_range', 'number', 'string'
    required: bool = True
    description: str = ""
    validation_rule: Optional[str] = None  # Regex or validation function name
    default_value: Optional[Any] = None
```

---

## Implementation

### Step 1: Create QueryTemplateService

**File**: `core/services/query_template_service.py`

```python
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import json
import re


class TemplateCategory(str, Enum):
    """Query template categories"""
    SUPPLIER = "supplier"
    INVOICE = "invoice"
    ANALYTICS = "analytics"
    AGGREGATION = "aggregation"
    TIME_SERIES = "time_series"
    COMPARISON = "comparison"


@dataclass
class TemplateParam:
    """Template parameter specification"""
    name: str
    type: str  # 'entity', 'field', 'date_range', 'number', 'string'
    required: bool = True
    description: str = ""
    validation_rule: Optional[str] = None
    default_value: Optional[Any] = None


@dataclass
class QueryTemplate:
    """Reusable query template"""
    id: str
    name: str
    description: str
    category: TemplateCategory
    sql_template: str
    parameters: List[TemplateParam] = field(default_factory=list)
    result_schema: Dict[str, str] = field(default_factory=dict)
    examples: List[Dict] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)


class QueryTemplateService:
    """Manage and execute reusable query templates"""
    
    def __init__(self):
        self.templates: Dict[str, QueryTemplate] = {}
        self._initialize_templates()
    
    def _initialize_templates(self) -> None:
        """Initialize built-in templates"""
        
        # Template 1: Supplier invoices by vendor
        self.register_template(QueryTemplate(
            id="supplier_invoices_by_vendor",
            name="Supplier Invoices by Vendor",
            description="Find all invoices from a specific supplier",
            category=TemplateCategory.SUPPLIER,
            sql_template="""
                SELECT 
                    i.InvoiceID,
                    i.InvoiceDate,
                    i.NetAmount,
                    i.TaxAmount,
                    s.SupplierName,
                    s.SupplierID
                FROM SupplierInvoice i
                INNER JOIN Supplier s ON i.SupplierID = s.SupplierID
                WHERE s.SupplierName = '{supplier_name}'
                ORDER BY i.InvoiceDate DESC
            """,
            parameters=[
                TemplateParam(
                    name="supplier_name",
                    type="string",
                    required=True,
                    description="Name of supplier (exact match)",
                    validation_rule="^[a-zA-Z0-9\\s\\-]{1,100}$"
                )
            ],
            result_schema={
                "InvoiceID": "string",
                "InvoiceDate": "date",
                "NetAmount": "decimal",
                "TaxAmount": "decimal",
                "SupplierName": "string",
                "SupplierID": "string"
            },
            examples=[
                {
                    "supplier_name": "Acme Corp",
                    "description": "Invoices from Acme Corp"
                }
            ],
            tags=["supplier", "invoice", "vendor", "finance"]
        ))
        
        # Template 2: Invoice aggregation by date range
        self.register_template(QueryTemplate(
            id="invoice_summary_by_date",
            name="Invoice Summary by Date Range",
            description="Aggregate invoice totals for a date range",
            category=TemplateCategory.ANALYTICS,
            sql_template="""
                SELECT 
                    DATE_TRUNC('day', i.InvoiceDate) as InvoiceDay,
                    COUNT(*) as InvoiceCount,
                    SUM(i.NetAmount) as TotalNetAmount,
                    SUM(i.TaxAmount) as TotalTaxAmount,
                    SUM(i.NetAmount + i.TaxAmount) as TotalAmount,
                    AVG(i.NetAmount) as AvgInvoiceAmount
                FROM SupplierInvoice i
                WHERE i.InvoiceDate BETWEEN '{start_date}' AND '{end_date}'
                GROUP BY DATE_TRUNC('day', i.InvoiceDate)
                ORDER BY InvoiceDay DESC
            """,
            parameters=[
                TemplateParam(
                    name="start_date",
                    type="date_range",
                    required=True,
                    description="Start date (YYYY-MM-DD)",
                    validation_rule="^\\d{4}-\\d{2}-\\d{2}$"
                ),
                TemplateParam(
                    name="end_date",
                    type="date_range",
                    required=True,
                    description="End date (YYYY-MM-DD)",
                    validation_rule="^\\d{4}-\\d{2}-\\d{2}$"
                )
            ],
            result_schema={
                "InvoiceDay": "date",
                "InvoiceCount": "integer",
                "TotalNetAmount": "decimal",
                "TotalTaxAmount": "decimal",
                "TotalAmount": "decimal",
                "AvgInvoiceAmount": "decimal"
            },
            examples=[
                {
                    "start_date": "2025-01-01",
                    "end_date": "2025-01-31",
                    "description": "January 2025 invoice summary"
                }
            ],
            tags=["analytics", "aggregation", "invoice", "date_range", "summary"]
        ))
        
        # Template 3: Purchase order details with line items
        self.register_template(QueryTemplate(
            id="purchase_order_with_items",
            name="Purchase Order with Line Items",
            description="Get PO header and all line items",
            category=TemplateCategory.INVOICE,
            sql_template="""
                SELECT 
                    p.PurchaseOrderID,
                    p.PODate,
                    p.VendorID,
                    v.SupplierName as VendorName,
                    pi.LineItemNumber,
                    pi.MaterialID,
                    pi.Quantity,
                    pi.UnitPrice,
                    pi.LineAmount
                FROM PurchaseOrder p
                LEFT JOIN PurchaseOrderItem pi ON p.PurchaseOrderID = pi.PurchaseOrderID
                LEFT JOIN Supplier v ON p.VendorID = v.SupplierID
                WHERE p.PurchaseOrderID = '{po_id}'
                ORDER BY pi.LineItemNumber
            """,
            parameters=[
                TemplateParam(
                    name="po_id",
                    type="string",
                    required=True,
                    description="Purchase Order ID",
                    validation_rule="^[A-Z0-9\\-]{1,50}$"
                )
            ],
            result_schema={
                "PurchaseOrderID": "string",
                "PODate": "date",
                "VendorID": "string",
                "VendorName": "string",
                "LineItemNumber": "integer",
                "MaterialID": "string",
                "Quantity": "decimal",
                "UnitPrice": "decimal",
                "LineAmount": "decimal"
            },
            examples=[
                {
                    "po_id": "PO-2025-00001",
                    "description": "Details for PO 2025-00001"
                }
            ],
            tags=["purchase_order", "line_items", "vendor", "material"]
        ))
    
    def register_template(self, template: QueryTemplate) -> None:
        """Register a new query template"""
        self.templates[template.id] = template
    
    def get_template(self, template_id: str) -> Optional[QueryTemplate]:
        """Get template by ID"""
        return self.templates.get(template_id)
    
    def list_templates(self, category: Optional[str] = None) -> List[QueryTemplate]:
        """List templates, optionally filtered by category"""
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        return templates
    
    def search_templates(self, query: str) -> List[QueryTemplate]:
        """Search templates by name, description, or tags"""
        query_lower = query.lower()
        results = []
        
        for template in self.templates.values():
            # Check name
            if query_lower in template.name.lower():
                results.append(template)
                continue
            
            # Check description
            if query_lower in template.description.lower():
                results.append(template)
                continue
            
            # Check tags
            if any(query_lower in tag.lower() for tag in template.tags):
                results.append(template)
                continue
        
        return results
    
    def validate_parameters(self, template_id: str, params: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate parameters against template specification"""
        template = self.get_template(template_id)
        if not template:
            return False, [f"Template '{template_id}' not found"]
        
        errors = []
        
        # Check required parameters
        for param in template.parameters:
            if param.required and param.name not in params:
                errors.append(f"Required parameter '{param.name}' missing")
                continue
            
            if param.name not in params:
                continue
            
            value = params[param.name]
            
            # Validate type
            if not self._validate_param_type(value, param.type):
                errors.append(
                    f"Parameter '{param.name}' has invalid type: "
                    f"expected {param.type}, got {type(value).__name__}"
                )
                continue
            
            # Validate against regex rule
            if param.validation_rule and isinstance(value, str):
                if not re.match(param.validation_rule, value):
                    errors.append(
                        f"Parameter '{param.name}' value '{value}' "
                        f"does not match validation rule: {param.validation_rule}"
                    )
        
        return len(errors) == 0, errors
    
    def _validate_param_type(self, value: Any, param_type: str) -> bool:
        """Validate parameter type"""
        type_validators = {
            "string": lambda v: isinstance(v, str),
            "number": lambda v: isinstance(v, (int, float)),
            "date_range": lambda v: isinstance(v, str),
            "entity": lambda v: isinstance(v, str),
            "field": lambda v: isinstance(v, str),
        }
        
        validator = type_validators.get(param_type)
        return validator(value) if validator else True
    
    def render_query(self, template_id: str, params: Dict[str, Any]) -> Optional[str]:
        """Render template query with parameters"""
        # Validate parameters first
        is_valid, errors = self.validate_parameters(template_id, params)
        if not is_valid:
            raise ValueError(f"Parameter validation failed: {'; '.join(errors)}")
        
        template = self.get_template(template_id)
        if not template:
            return None
        
        query = template.sql_template
        
        # Replace placeholders
        for param in template.parameters:
            placeholder = "{" + param.name + "}"
            
            if param.name in params:
                value = params[param.name]
                
                # Escape string values
                if param.type == "string":
                    value = str(value).replace("'", "''")
                
                query = query.replace(placeholder, str(value))
            elif param.default_value is not None:
                query = query.replace(placeholder, str(param.default_value))
        
        return query
```

### Step 2: Create Backend API

**File**: `modules/knowledge_graph_v2/backend/query_template_api.py`

```python
from flask import Blueprint, request, jsonify
from core.services.query_template_service import QueryTemplateService

query_template_bp = Blueprint('query_templates', __name__)

# Global service instance
_template_service = None

def get_template_service() -> QueryTemplateService:
    """Get or create template service"""
    global _template_service
    if _template_service is None:
        _template_service = QueryTemplateService()
    return _template_service


@query_template_bp.route('/api/knowledge-graph-v2/query-templates', methods=['GET'])
def list_templates():
    """List all available query templates"""
    service = get_template_service()
    category = request.args.get('category')
    
    templates = service.list_templates(category=category)
    
    return jsonify({
        'templates': [
            {
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'category': t.category.value,
                'tags': t.tags
            }
            for t in templates
        ]
    })


@query_template_bp.route('/api/knowledge-graph-v2/query-templates/<template_id>', methods=['GET'])
def get_template(template_id: str):
    """Get template details"""
    service = get_template_service()
    template = service.get_template(template_id)
    
    if not template:
        return jsonify({'error': f'Template {template_id} not found'}), 404
    
    return jsonify({
        'id': template.id,
        'name': template.name,
        'description': template.description,
        'category': template.category.value,
        'sql_template': template.sql_template,
        'parameters': [
            {
                'name': p.name,
                'type': p.type,
                'required': p.required,
                'description': p.description,
                'validation_rule': p.validation_rule,
                'default_value': p.default_value
            }
            for p in template.parameters
        ],
        'result_schema': template.result_schema,
        'examples': template.examples,
        'tags': template.tags
    })


@query_template_bp.route('/api/knowledge-graph-v2/query-templates/search', methods=['GET'])
def search_templates():
    """Search templates"""
    service = get_template_service()
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    templates = service.search_templates(query)
    
    return jsonify({
        'query': query,
        'results': [
            {
                'id': t.id,
                'name': t.name,
                'description': t.description,
                'category': t.category.value,
                'tags': t.tags
            }
            for t in templates
        ]
    })


@query_template_bp.route('/api/knowledge-graph-v2/query-templates/<template_id>/validate', methods=['POST'])
def validate_parameters(template_id: str):
    """Validate template parameters"""
    service = get_template_service()
    data = request.get_json() or {}
    params = data.get('parameters', {})
    
    is_valid, errors = service.validate_parameters(template_id, params)
    
    return jsonify({
        'template_id': template_id,
        'valid': is_valid,
        'errors': errors
    })


@query_template_bp.route('/api/knowledge-graph-v2/query-templates/<template_id>/render', methods=['POST'])
def render_query(template_id: str):
    """Render query from template with parameters"""
    service = get_template_service()
    data = request.get_json() or {}
    params = data.get('parameters', {})
    
    try:
        query = service.render_query(template_id, params)
        
        if query is None:
            return jsonify({'error': f'Template {template_id} not found'}), 404
        
        return jsonify({
            'template_id': template_id,
            'query': query,
            'parameters': params
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
```

### Step 3: Write API Contract Tests

**File**: `tests/knowledge_graph_v2/test_query_templates_api.py`

```python
import pytest
import requests
from core.services.query_template_service import QueryTemplateService

BASE_URL = "http://localhost:5000"

@pytest.mark.e2e
@pytest.mark.api_contract
class TestQueryTemplatesAPI:
    """Query templates API contract tests"""
    
    def test_list_templates_returns_valid_contract(self):
        """Test: List templates returns valid contract"""
        response = requests.get(f"{BASE_URL}/api/knowledge-graph-v2/query-templates", timeout=5)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify contract
        assert 'templates' in data
        assert isinstance(data['templates'], list)
        assert len(data['templates']) >= 3  # At least our 3 built-in templates
        
        # Verify template structure
        template = data['templates'][0]
        assert 'id' in template
        assert 'name' in template
        assert 'description' in template
        assert 'category' in template
        assert 'tags' in template
    
    def test_list_templates_with_category_filter(self):
        """Test: Filter templates by category"""
        response = requests.get(
            f"{BASE_URL}/api/knowledge-graph-v2/query-templates?category=supplier",
            timeout=5
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all returned templates have matching category
        for template in data['templates']:
            assert template['category'] == 'supplier'
    
    def test_get_template_details(self):
        """Test: Get complete template details"""
        response = requests.get(
            f"{BASE_URL}/api/knowledge-graph-v2/query-templates/supplier_invoices_by_vendor",
            timeout=5
        )
        
        assert response.status_code == 200
        template = response.json()
        
        # Verify complete contract
        assert template['id'] == 'supplier_invoices_by_vendor'
        assert 'sql_template' in template
        assert 'parameters' in template
        assert isinstance(template['parameters'], list)
        
        # Verify parameter structure
        param = template['parameters'][0]
        assert 'name' in param
        assert 'type' in param
        assert 'required' in param
        assert 'validation_rule' in param
    
    def test_get_nonexistent_template_returns_404(self):
        """Test: Nonexistent template returns 404"""
        response = requests.get(
            f"{BASE_URL}/api/knowledge-graph-v2/query-templates/nonexistent",
            timeout=5
        )
        
        assert response.status_code == 404
        data = response.json()
        assert 'error' in data
    
    def test_search_templates(self):
        """Test: Search templates by query"""
        response = requests.get(
            f"{BASE_URL}/api/knowledge-graph-v2/query-templates/search?q=invoice",
            timeout=5
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'query' in data
        assert data['query'] == 'invoice'
        assert 'results' in data
        assert len(data['results']) > 0
    
    def test_search_templates_requires_query(self):
        """Test: Search without query returns error"""
        response = requests.get(
            f"{BASE_URL}/api/knowledge-graph-v2/query-templates/search",
            timeout=5
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    def test_validate_valid_parameters(self):
        """Test: Validate valid parameters"""
        response = requests.post(
            f"{BASE_URL}/api/knowledge-graph-v2/query-templates/supplier_invoices_by_vendor/validate",
            json={'parameters': {'supplier_name': 'Acme Corp'}},
            timeout=5
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['valid'] is True
        assert 'errors' not in data or len(data['errors']) == 0
    
    def test_validate_invalid_parameters(self):
        """Test: Validate invalid parameters"""
        response = requests.post(
            f"{BASE_URL}/api/knowledge-graph-v2/query-templates/supplier_invoices_by_vendor/validate",
            json={'parameters': {}},  # Missing required parameter
            timeout=5
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['valid'] is False
        assert 'errors' in data
        assert len(data['errors']) > 0
    
    def test_render_query_with_valid_parameters(self):
        """Test: Render query with valid parameters"""
        response = requests.post(
            f"{BASE_URL}/api/knowledge-graph-v2/query-templates/supplier_invoices_by_vendor/render",
            json={'parameters': {'supplier_name': 'Acme Corp'}},
            timeout=5
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'query' in data
        assert 'Acme Corp' in data['query']
        assert 'SELECT' in data['query']
    
    def test_render_query_validates_parameters(self):
        """Test: Render query validates parameters first"""
        response = requests.post(
            f"{BASE_URL}/api/knowledge-graph-v2/query-templates/supplier_invoices_by_vendor/render",
            json={'parameters': {}},  # Missing required parameter
            timeout=5
        )
        
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data
    
    def test_template_service_initialization(self):
        """Test: Service initializes with built-in templates"""
        service = QueryTemplateService()
        
        # Verify built-in templates exist
        assert service.get_template('supplier_invoices_by_vendor') is not None
        assert service.get_template('invoice_summary_by_date') is not None
        assert service.get_template('purchase_order_with_items') is not None
```

---

## Integration with Knowledge Graph API

Update `modules/knowledge_graph_v2/backend/api.py`:

```python
from modules.knowledge_graph_v2.backend.query_template_api import query_template_bp

# Register blueprint
app.register_blueprint(query_template_bp)
```

---

## Success Criteria

- ✅ QueryTemplateService created with 3+ built-in templates
- ✅ API endpoints: list, get, search, validate, render
- ✅ All 11 API contract tests passing
- ✅ Parameter validation with regex rules
- ✅ Query rendering with safe parameter substitution
- ✅ Comprehensive documentation with examples

---

## Next Steps (Phase 5)

1. Extend template library with 10+ additional templates
2. Add template result caching (Redis integration)
3. Add template execution in knowledge graph facade
4. AI Assistant integration (query intent → template selection)
5. Template performance profiling