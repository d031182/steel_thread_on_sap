# SAP CAP CSN - Core Schema Notation

**Source**: https://cap.cloud.sap/docs/cds/csn  
**Last Updated**: 2026-02-23  
**Status**: Official SAP CAP Documentation

## Overview

**CSN** (pronounced "Season") is a JSON-based notation for compact representations of CDS models, optimized for sharing and interpreting models as plain JavaScript objects derived from JSON Schema.

### Purpose

- **Canonical runtime format** for SAP Cloud Application Programming (CAP)
- **Dynamic processing** of models at runtime
- **Extensions by third parties** through JavaScript objects
- **Translation to SQL DDL** for databases (SAP HANA, PostgreSQL, SQLite, H2)
- **Ecosystem exchange** via CSN Interop specification

## Core Structure

CSN models consist of optional top-level properties:

### Top-Level Properties

| Property | Type | Description |
|----------|------|-------------|
| `requires` | Array | Imported models |
| `definitions` | Dictionary | Named definitions (types, entities, views) |
| `extensions` | Array | Unnamed aspects |
| `i18n` | Dictionary | Text translations for internationalization |

### Definition Name Rules

**Valid naming conventions**:
- ✅ Nonempty strings
- ❌ Cannot start/end with `.` or `::`
- ❌ Cannot contain `..`, `:::`, or multiple `::`

## Core Definition Kinds

### 1. Type Definitions

**Kind**: `"type"`

**Key Properties**:
- `type`: Base type (e.g., `cds.String`, `cds.Decimal`)
- `elements`: Structured type elements
- `items`: Array type items
- `enum`: Enumeration values
- `includes`: Copied elements from other types

**Example Use**:
```json
{
  "kind": "type",
  "type": "cds.String",
  "length": 100
}
```

**Structured Types**:
```json
{
  "kind": "type",
  "elements": {
    "firstName": { "type": "cds.String" },
    "lastName": { "type": "cds.String" }
  }
}
```

**Enums**:
```json
{
  "kind": "type",
  "type": "cds.String",
  "enum": {
    "active": { "val": "A" },
    "inactive": { "val": "I" }
  }
}
```

### 2. Entity Definitions

**Kind**: `"entity"`

**Key Properties**:
- `elements`: Entity elements/columns
  - `key`: Boolean flag for primary keys
  - `virtual`: Boolean flag for non-persistent fields
  - `notNull`: Boolean flag for required fields
- `includes`: Inherited elements from other entities/types

**Example**:
```json
{
  "PurchaseOrder": {
    "kind": "entity",
    "elements": {
      "ID": { 
        "type": "cds.UUID", 
        "key": true 
      },
      "OrderNumber": { 
        "type": "cds.String", 
        "length": 10,
        "notNull": true
      },
      "TotalAmount": { 
        "type": "cds.Decimal",
        "precision": 15,
        "scale": 2
      }
    }
  }
}
```

### 3. View Definitions

**Kind**: `"entity"` (with `query`)

**Key Properties**:
- `query`: CQN (Core Query Notation) format
- `params`: Query parameters

**Example**:
```json
{
  "kind": "entity",
  "query": {
    "SELECT": {
      "from": { "ref": ["PurchaseOrder"] },
      "columns": ["ID", "OrderNumber"]
    }
  }
}
```

### 4. Projection Definitions

**Kind**: `"entity"` (with `projection`)

**Key Properties**:
- `projection`: SELECT statement
- `elements`: Inferred elements from projection

**Example**:
```json
{
  "kind": "entity",
  "projection": {
    "SELECT": {
      "from": { "ref": ["PurchaseOrder"] }
    }
  }
}
```

## Annotations

Annotations use `@` prefix and appear as flat key-value pairs:

```json
{
  "PurchaseOrder": {
    "kind": "entity",
    "@common.label": "Purchase Order",
    "@readonly": true,
    "elements": {
      "OrderNumber": {
        "type": "cds.String",
        "@title": "Order #"
      }
    }
  }
}
```

### Common Annotations

| Annotation | Purpose | Example |
|------------|---------|---------|
| `@title` | Element label | `"Order Number"` |
| `@description` | Documentation | `"Unique identifier"` |
| `@readonly` | Non-editable field | `true` |
| `@assert.format` | Validation pattern | `"^[A-Z0-9]+$"` |

## Associations

Associations follow scalar type definitions with special reference forms:

```json
{
  "PurchaseOrderItem": {
    "kind": "entity",
    "elements": {
      "order": {
        "type": "cds.Association",
        "target": "PurchaseOrder",
        "keys": [
          { "ref": ["OrderID"] }
        ]
      }
    }
  }
}
```

## Literals & Expressions

### Time Literals
```json
{
  "timestamp": "16:11Z"
}
```

### Expressions
```json
{
  "=": "foo.bar < 9"
}
```

### Enum Symbols
```json
{
  "#": "asc"
}
```

## CSN Interop

**CSN Interop** is a standardized subset for ecosystem exchange:
- **Purpose**: Cross-system data model sharing
- **Spec**: https://sap.github.io/csn-interop-specification/
- **Use Cases**: BTP ecosystem integration, third-party tool compatibility

## Related Specifications

| Spec | Description | Link |
|------|-------------|------|
| **CDL** | Core Data Language (human-readable) | https://cap.cloud.sap/docs/cds/cdl |
| **CQL** | Core Query Language | https://cap.cloud.sap/docs/cds/cql |
| **CQN** | Core Query Notation (runtime queries) | https://cap.cloud.sap/docs/cds/cqn |
| **Built-in Types** | Standard CDS types | https://cap.cloud.sap/docs/cds/types |

## Use in This Project

### Current CSN Usage

1. **CSN Files Location**: `docs/csn/` directory
   - Contains P2P data product CSN definitions
   - Example: `PurchaseOrder.csn`, `Supplier.csn`

2. **CSN Parser**: `core/services/csn_parser.py`
   - Parses CSN files into Python objects
   - Extracts definitions, elements, associations

3. **Database Rebuild**: `scripts/python/rebuild_sqlite_from_csn.py`
   - Reads CSN files
   - Creates SQLite schema matching CSN structure
   - **Hierarchy**: Data Products → Tables → Columns

### Key Mappings

| CSN Concept | SQLite Mapping |
|-------------|----------------|
| CSN File | Data Product |
| `definitions` | Tables |
| `elements` | Columns |
| `type` | Column data type |
| `@title` | Column description |

### Example Transformation

**CSN Input** (`PurchaseOrder.csn`):
```json
{
  "definitions": {
    "PurchaseOrder": {
      "kind": "entity",
      "elements": {
        "OrderNumber": { "type": "cds.String", "length": 10 },
        "TotalAmount": { "type": "cds.Decimal", "precision": 15, "scale": 2 }
      }
    }
  }
}
```

**SQLite Output**:
```sql
CREATE TABLE PurchaseOrder (
  OrderNumber TEXT,
  TotalAmount REAL
);

INSERT INTO data_products (name) VALUES ('Purchase Order');
INSERT INTO tables (name, data_product_id) VALUES ('PurchaseOrder', 1);
INSERT INTO columns (name, type, table_id) VALUES ('OrderNumber', 'TEXT', 1);
INSERT INTO columns (name, type, table_id) VALUES ('TotalAmount', 'REAL', 1);
```

## References

1. [Official CSN Documentation](https://cap.cloud.sap/docs/cds/csn)
2. [CAP Core Concepts](https://cap.cloud.sap/docs/get-started/concepts)
3. [CSN Interop Specification](https://sap.github.io/csn-interop-specification/)
4. [CDS Language Reference](https://cap.cloud.sap/docs/cds/)

---

**Tags**: #csn #sap-cap #cds #data-modeling #schema #documentation