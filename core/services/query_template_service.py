from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
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
            templates = [t for t in templates if t.category.value == category]
        
        return templates
    
    def list_templates_with_metadata(self, category: Optional[str] = None) -> Dict:
        """
        List templates with formatted response metadata.
        
        Args:
            category: Optional category filter
            
        Returns:
            dict: Formatted response with templates array
        """
        templates = self.list_templates(category=category)
        
        return {
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
        }
    
    def get_template_with_metadata(self, template_id: str) -> Tuple[Dict, int]:
        """
        Get template with formatted response metadata.
        
        Args:
            template_id: Template identifier
            
        Returns:
            tuple: (response_dict, status_code)
        """
        template = self.get_template(template_id)
        
        if not template:
            return {'error': f'Template {template_id} not found'}, 404
        
        return {
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
        }, 200
    
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
    
    def search_templates_with_metadata(self, query: str) -> Dict:
        """
        Search templates with formatted response metadata.
        
        Args:
            query: Search query
            
        Returns:
            dict: Formatted response with query and results
        """
        templates = self.search_templates(query)
        
        return {
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
        }
    
    def validate_parameters(self, template_id: str, params: Dict[str, Any]) -> Tuple[bool, List[str]]:
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
    
    def validate_parameters_with_metadata(self, template_id: str, params: Dict[str, Any]) -> Dict:
        """
        Validate parameters with formatted response metadata.
        
        Args:
            template_id: Template identifier
            params: Parameters to validate
            
        Returns:
            dict: Formatted response with validation result
        """
        is_valid, errors = self.validate_parameters(template_id, params)
        
        return {
            'template_id': template_id,
            'valid': is_valid,
            'errors': errors
        }
    
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
    
    def render_query_with_metadata(self, template_id: str, params: Dict[str, Any]) -> Tuple[Dict, int]:
        """
        Render query with formatted response metadata.
        
        Args:
            template_id: Template identifier
            params: Parameters for rendering
            
        Returns:
            tuple: (response_dict, status_code)
        """
        try:
            query = self.render_query(template_id, params)
            
            if query is None:
                return {'error': f'Template {template_id} not found'}, 404
            
            return {
                'template_id': template_id,
                'query': query,
                'parameters': params
            }, 200
        except ValueError as e:
            return {'error': str(e)}, 400