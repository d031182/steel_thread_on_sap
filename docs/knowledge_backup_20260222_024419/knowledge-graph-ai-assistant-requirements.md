# Knowledge Graph Requirements for AI Assistant

**Date**: 2026-02-21  
**Purpose**: Define what CSN semantics are CRITICAL for AI Assistant to answer user questions  
**Use Case**: AI Assistant queries knowledge graph to understand data structure and generate intelligent responses

---

## AI Assistant Use Cases

### Use Case 1: "Show me all invoices for supplier X"
**AI Needs to Know**:
1. ✅ Which entity is "invoices" (SupplierInvoice)
2. ✅ Which entity is "supplier" (Supplier)
3. ❌ **MISSING**: How they relate (foreign key: SupplierInvoice.SupplierID → Supplier.SupplierID)
4. ❌ **MISSING**: Which column is the filter key (SupplierID, SupplierName?)
5. ❌ **MISSING**: Display labels (@title) to show user-friendly field names

**Required Metadata**:
- Association ON conditions (join paths)
- Foreign key mappings
- Display labels (@title, @Common.Label)

---

### Use Case 2: "What's the total amount of unpaid invoices?"
**AI Needs to Know**:
1. ✅ Which entity has invoice data (SupplierInvoice)
2. ❌ **MISSING**: Which field is "amount" (GrossAmount? NetAmount? TotalAmount?)
3. ❌ **MISSING**: Which field indicates "unpaid" (Status? PaymentStatus?)
4. ❌ **MISSING**: What values mean "unpaid" (status = 'OPEN'? status = 1?)
5. ❌ **MISSING**: Field semantic type (@Semantics.amount, @Semantics.currencyCode)

**Required Metadata**:
- Semantic annotations (@Semantics.amount, @Semantics.currencyCode)
- Business logic annotations (value meanings)
- Field descriptions (@EndUserText.label)

---

### Use Case 3: "Which purchase orders have items with quantity > 100?"
**AI Needs to Know**:
1. ✅ Which entity is "purchase orders" (PurchaseOrder)
2. ✅ Which entity is "items" (PurchaseOrderItem)
3. ❌ **MISSING**: Parent-child relationship (Composition: PurchaseOrder → PurchaseOrderItem)
4. ❌ **MISSING**: Which field is "quantity" (Quantity? OrderQuantity?)
5. ❌ **MISSING**: Cardinality (1:N - one PO has many items)

**Required Metadata**:
- Composition vs Association distinction
- Cardinality (1:1, 1:N, N:M)
- ON conditions (join paths for nested queries)

---

### Use Case 4: "Show invoices with invalid company codes"
**AI Needs to Know**:
1. ✅ Which entity is "invoices" (SupplierInvoice)
2. ✅ Which field is "company codes" (CompanyCode)
3. ❌ **MISSING**: Valid values for CompanyCode (from @Common.ValueList)
4. ❌ **MISSING**: Value help entity (CompanyCodeValueHelp)
5. ❌ **MISSING**: Constraints (notNull, length)

**Required Metadata**:
- Value list configurations (@Common.ValueList)
- Constraints (notNull, length)
- Reference entities for validation

---

## Critical Metadata for AI Understanding

### Priority 1: CRITICAL (Required for Query Generation)

#### 1. Association ON Conditions ⭐ HIGHEST PRIORITY
**Why**: AI cannot generate correct JOIN queries without knowing HOW entities relate

**Current State**: ❌ Not captured
**CSN Source**:
```json
{
  "to_Supplier": {
    "type": "cds.Association",
    "target": "Supplier",
    "on": [
      { "ref": ["SupplierID"] },
      "=",
      { "ref": ["to_Supplier", "SupplierID"] }
    ]
  }
}
```

**What AI Needs**:
```python
{
  "relationship": {
    "from_entity": "SupplierInvoice",
    "from_column": "SupplierID",
    "to_entity": "Supplier",
    "to_column": "SupplierID",
    "join_condition": "SupplierInvoice.SupplierID = Supplier.SupplierID"
  }
}
```

**AI Query Generation**:
```sql
-- With ON condition, AI can generate:
SELECT i.*, s.Name
FROM SupplierInvoice i
INNER JOIN Supplier s ON i.SupplierID = s.SupplierID
WHERE s.SupplierID = 'SUP001'
```

---

#### 2. Display Labels (@title, @Common.Label) ⭐ HIGH PRIORITY
**Why**: AI needs to map user's natural language to technical field names

**Current State**: ❌ Not captured
**CSN Source**:
```json
{
  "CompanyCode": {
    "type": "cds.String",
    "@title": "Company Code",
    "@Common.Label": "Company Code"
  },
  "GrossAmount": {
    "type": "cds.Decimal",
    "@title": "Gross Amount",
    "@Semantics.amount.currencyCode": "Currency"
  }
}
```

**What AI Needs**:
```python
{
  "field_mappings": {
    "CompanyCode": {
      "display_name": "Company Code",
      "user_terms": ["company", "company code", "org code"]
    },
    "GrossAmount": {
      "display_name": "Gross Amount",
      "user_terms": ["amount", "total", "gross", "value"]
    }
  }
}
```

**AI Understanding**:
```
User: "Show invoices for company 1000"
AI Maps: "company" → CompanyCode field
AI Generates: WHERE CompanyCode = '1000'
```

---

#### 3. Semantic Annotations (@Semantics.*) ⭐ HIGH PRIORITY
**Why**: AI needs to understand WHAT TYPE of data each field represents

**Current State**: ❌ Not captured
**CSN Source**:
```json
{
  "NetAmount": {
    "type": "cds.Decimal",
    "@Semantics.amount": true,
    "@Semantics.amount.currencyCode": "Currency"
  },
  "InvoiceDate": {
    "type": "cds.Date",
    "@Semantics.businessDate": true
  },
  "Currency": {
    "type": "cds.String",
    "@Semantics.currencyCode": true
  }
}
```

**What AI Needs**:
```python
{
  "semantic_types": {
    "NetAmount": {
      "type": "amount",
      "currency_field": "Currency",
      "aggregatable": true  # Can do SUM, AVG
    },
    "InvoiceDate": {
      "type": "date",
      "date_role": "business_date",
      "filterable": true  # Can filter by date range
    },
    "Currency": {
      "type": "currency_code",
      "is_dimension": true  # Group by currency
    }
  }
}
```

**AI Query Generation**:
```
User: "What's the total invoice amount?"
AI Knows: NetAmount is @Semantics.amount → Use SUM()
AI Generates: SELECT SUM(NetAmount) FROM SupplierInvoice

User: "Group by currency"
AI Knows: Currency is @Semantics.currencyCode → Use GROUP BY
AI Generates: SELECT Currency, SUM(NetAmount) FROM ... GROUP BY Currency
```

---

#### 4. Cardinality ⭐ HIGH PRIORITY
**Why**: AI needs to know relationship types to generate correct queries and explain data structure

**Current State**: ❌ Not captured
**CSN Source**:
```json
{
  "to_Supplier": {
    "type": "cds.Association",
    "target": "Supplier",
    "cardinality": {
      "max": 1  // Many invoices → One supplier (N:1)
    }
  },
  "items": {
    "type": "cds.Composition",
    "target": "PurchaseOrderItem",
    "cardinality": {
      "max": "*"  // One PO → Many items (1:N)
    }
  }
}
```

**What AI Needs**:
```python
{
  "relationships": {
    "SupplierInvoice_to_Supplier": {
      "type": "N:1",  # Many invoices to one supplier
      "description": "Each invoice belongs to one supplier"
    },
    "PurchaseOrder_to_items": {
      "type": "1:N",  # One PO has many items
      "is_composition": true,  # Parent-child ownership
      "description": "Each purchase order has multiple line items"
    }
  }
}
```

**AI Understanding**:
```
User: "How many suppliers have invoices?"
AI Knows: N:1 relationship → Use DISTINCT on Supplier
AI Generates: SELECT COUNT(DISTINCT SupplierID) FROM SupplierInvoice

User: "Show purchase orders with more than 5 items"
AI Knows: 1:N composition → Use nested query or GROUP BY
AI Generates: 
  SELECT po.* FROM PurchaseOrder po
  WHERE (SELECT COUNT(*) FROM PurchaseOrderItem WHERE PurchaseOrderID = po.ID) > 5
```

---

### Priority 2: HIGH (Required for Data Validation & UI)

#### 5. Type Constraints (length, precision, scale)
**Why**: AI needs to validate user input and explain data limitations

**Current State**: ❌ Not captured
**CSN Source**:
```json
{
  "CompanyCode": {
    "type": "cds.String",
    "length": 10,
    "notNull": true
  },
  "NetAmount": {
    "type": "cds.Decimal",
    "precision": 15,
    "scale": 2
  }
}
```

**What AI Needs**:
```python
{
  "constraints": {
    "CompanyCode": {
      "max_length": 10,
      "required": true,
      "validation": "Must be 10 characters or less"
    },
    "NetAmount": {
      "max_value": 9999999999999.99,  # Based on precision/scale
      "decimal_places": 2
    }
  }
}
```

**AI Validation**:
```
User: "Add invoice with company code VERY_LONG_CODE_12345"
AI: ❌ "CompanyCode exceeds maximum length of 10 characters"

User: "Set amount to 123.456"
AI: ❌ "NetAmount only allows 2 decimal places. Did you mean 123.46?"
```

---

#### 6. Value Lists (@Common.ValueList)
**Why**: AI needs to suggest valid values and validate user input

**Current State**: ❌ Not captured
**CSN Source**:
```json
{
  "Status": {
    "type": "cds.String",
    "@Common.ValueList": {
      "entity": "InvoiceStatusValueHelp",
      "parameters": [
        { "localDataProperty": "Status", "valueListProperty": "Code" }
      ]
    }
  }
}
```

**What AI Needs**:
```python
{
  "value_lists": {
    "Status": {
      "source_entity": "InvoiceStatusValueHelp",
      "valid_values": ["OPEN", "PAID", "CANCELLED", "DISPUTED"],
      "descriptions": {
        "OPEN": "Invoice awaiting payment",
        "PAID": "Invoice fully paid",
        "CANCELLED": "Invoice cancelled",
        "DISPUTED": "Invoice under dispute"
      }
    }
  }
}
```

**AI Assistance**:
```
User: "Show unpaid invoices"
AI Maps: "unpaid" → Status = 'OPEN'
AI: "Found 47 invoices with Status='OPEN' (unpaid)"

User: "Set status to 'pending'"
AI: ❌ "Invalid status 'pending'. Valid values: OPEN, PAID, CANCELLED, DISPUTED"
```

---

#### 7. NOT NULL Constraints
**Why**: AI needs to know which fields are mandatory

**Current State**: ❌ Not captured
**CSN Source**:
```json
{
  "InvoiceID": {
    "type": "cds.String",
    "key": true,
    "notNull": true
  },
  "SupplierID": {
    "type": "cds.String",
    "notNull": true
  },
  "Notes": {
    "type": "cds.String",
    "notNull": false  // Optional
  }
}
```

**AI Validation**:
```
User: "Create invoice without supplier"
AI: ❌ "SupplierID is required (NOT NULL constraint)"

User: "What fields are required for creating an invoice?"
AI: ✅ "Required fields: InvoiceID, SupplierID, InvoiceDate, NetAmount"
```

---

### Priority 3: MEDIUM (Enhances AI Understanding)

#### 8. Composition vs Association
**Why**: AI needs to understand ownership and cascade behavior

**Current State**: ⚠️ Partially captured (type only, not semantics)
**What AI Needs**:
```python
{
  "relationships": {
    "PurchaseOrder_to_items": {
      "type": "Composition",
      "semantics": {
        "ownership": "PurchaseOrder owns PurchaseOrderItem",
        "cascade_delete": true,
        "cannot_exist_independently": true
      }
    }
  }
}
```

**AI Understanding**:
```
User: "Delete purchase order PO123"
AI: ⚠️ "This will also delete all associated line items (cascade delete)"

User: "Can items exist without a purchase order?"
AI: ❌ "No, items are part of a Composition. They cannot exist independently."
```

---

#### 9. Field Descriptions (@EndUserText.quickInfo)
**Why**: AI can explain fields to users in natural language

**Current State**: ❌ Not captured
**CSN Source**:
```json
{
  "PaymentTerms": {
    "type": "cds.String",
    "@EndUserText.label": "Payment Terms",
    "@EndUserText.quickInfo": "Payment conditions agreed with supplier (e.g., Net 30)"
  }
}
```

**AI Explanation**:
```
User: "What is PaymentTerms?"
AI: ✅ "Payment Terms defines the payment conditions agreed with the supplier, 
     such as 'Net 30' (payment due within 30 days)."
```

---

## Summary: Critical Metadata for AI Assistant

### MUST HAVE (Priority 1)
1. ✅ **Association ON Conditions** - Generate correct JOIN queries
2. ✅ **Display Labels** - Map user language to technical fields
3. ✅ **Semantic Annotations** - Understand field types (amount, date, currency)
4. ✅ **Cardinality** - Understand relationship types (1:1, 1:N, N:M)

### SHOULD HAVE (Priority 2)
5. ✅ **Type Constraints** - Validate user input
6. ✅ **Value Lists** - Suggest valid values
7. ✅ **NOT NULL Constraints** - Identify required fields

### NICE TO HAVE (Priority 3)
8. ✅ **Composition Semantics** - Explain ownership
9. ✅ **Field Descriptions** - Natural language explanations

---

## Implementation Impact

### Current State (40% semantic capture)
```
User: "Show invoices for supplier ABC Corp"
AI: ❌ Cannot generate query - don't know:
  - Which field is "supplier" (SupplierID? SupplierName?)
  - How to JOIN entities (missing ON condition)
  - What "ABC Corp" maps to (name? ID?)
```

### Target State (95% semantic capture)
```
User: "Show invoices for supplier ABC Corp"
AI: ✅ Generates:
  SELECT i.* 
  FROM SupplierInvoice i
  INNER JOIN Supplier s ON i.SupplierID = s.SupplierID
  WHERE s.Name = 'ABC Corp'
  
AI Explains: "Found 15 invoices for supplier ABC Corp (ID: SUP001)"
```

---

## Recommended Implementation Order

### Phase 1: Query Generation (7 days)
1. Capture ON conditions → Enable JOIN queries
2. Capture cardinality → Understand relationship types
3. Capture display labels → Map user language to fields

**Impact**: AI can answer 60% of user questions (up from 10%)

### Phase 2: Input Validation (5 days)
4. Capture type constraints → Validate data length/format
5. Capture NOT NULL flags → Identify required fields
6. Capture value lists → Suggest valid values

**Impact**: AI can validate 90% of user inputs

### Phase 3: Natural Language Understanding (3 days)
7. Capture semantic annotations → Understand field meanings
8. Capture field descriptions → Explain concepts
9. Capture composition semantics → Explain ownership

**Impact**: AI provides 95% accurate, human-friendly responses

---

## Conclusion

**CRITICAL FOR AI ASSISTANT** (Priority 1):
1. ⭐ Association ON conditions (join paths)
2. ⭐ Display labels (@title, @Common.Label)
3. ⭐ Semantic annotations (@Semantics.*)
4. ⭐ Cardinality (1:1, 1:N, N:M)

**These 4 metadata types enable AI to**:
- Generate correct SQL queries (JOINs, filters, aggregations)
- Map user's natural language to technical fields
- Understand field meanings (amount, date, currency)
- Explain data structure (relationships, hierarchies)

**Without them, AI is limited to**:
- ❌ Basic entity/field listing
- ❌ No query generation
- ❌ No data validation
- ❌ No natural language understanding

**Recommendation**: Implement Phase 1 immediately to unlock AI Assistant's query generation capabilities.