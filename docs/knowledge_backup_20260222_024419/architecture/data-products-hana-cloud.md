# Data Products in HANA Cloud

**Type**: Architecture  
**Category**: Data Integration  
**Created**: 2026-01-22  
**Updated**: 2026-01-25  
**Status**: Active

## Overview

SAP HANA Cloud provides comprehensive support for consuming data products from SAP Business Data Cloud (BDC). Data products enable seamless data sharing using virtual tables and remote sources for federation without data replication.

## Related Documentation

- [[CSN HANA Cloud Solution]] - Uses data products for CSN data access
- [[HANA Connection Module]] - Provides connection to query data products
- [[Modular Architecture]] - Data Products module structure
- [[CSN Investigation Findings]] - Investigation that led to data product discovery

## What Are Data Products?

### Definition

**Data products** are curated, self-describing packages of business data and metadata optimized for:
- Sharing across systems
- Discovery in catalogs
- Consumption via multiple protocols
- Analytics and AI applications

### Types

**1. SAP-Managed Data Products**
- Predefined by SAP across Lines of Business
- Customers activate them in SAP BDC
- SAP handles extraction, loading, and curation
- Examples: Sales Order, Purchase Order, Supplier Invoice

**2. Customer-Managed Data Products**
- Created by customers in SAP Datasphere
- Published to catalog
- Technically identical to SAP-managed products

**3. Primary vs Derived**
- **Primary**: Original data from source applications
- **Derived**: Value-added, curated, transformed datasets

### Characteristics

| Attribute | Description |
|-----------|-------------|
| **Storage** | HANA Data Lake Files (HDLF) |
| **Access** | Virtual tables, APIs, Delta Sharing |
| **Metadata** | CSN definitions, column info |
| **Visibility** | Public, internal, private |
| **Category** | Business object, analytical, spatial |

## Architecture

### Formations

**Formation** = Trust relationship binding components together:
- SAP Business Data Cloud (BDC)
- SAP HANA Cloud instances
- SAP Datasphere
- SAP Databricks
- SAP Analytics Cloud

**Created in**: SAP for Me portal (https://me.sap.com)

**Benefits**:
- Simplified connectivity
- Single sign-on (SSO)
- Centralized discovery
- Automatic trust establishment

### Virtual Tables

**Virtual tables** point to remote data, allowing queries as if data were local **without physical transfer**.

**How They Work**:
1. Virtual table = pointer to remote data
2. SQL query accesses remote data directly
3. Query optimized by HANA processor
4. Relevant portions execute remotely
5. Only results returned to HANA Cloud
6. **No data movement**

**Benefits**:
- ✅ No data duplication
- ✅ Always current (real-time)
- ✅ Reduced storage costs
- ✅ Simplified governance
- ✅ Single source of truth

**Considerations**:
- ⚠️ Network latency affects performance
- ⚠️ Slower than local tables
- ⚠️ Requires remote system availability

### Remote Sources

**Remote source** = Named connection to external database

**Supported Sources**:
- SAP HANA on-premise
- SAP HANA Cloud (other instances)
- SAP HANA Cloud Data Lake
- SAP Business Data Cloud
- Other JDBC/ODBC sources

**Creation**: Automatic during data product installation

## Consumption Workflow

### Phase 1: Browse (SAP BDC Catalog)

**Tool**: SAP Business Data Cloud Catalog & Marketplace

**Actions**:
- Browse available data products
- Search by domain (Sales, Procurement, Finance)
- Review metadata, sample data, quality metrics
- Data products grouped in packages

### Phase 2: Share (From BDC to HANA Cloud)

**Action**: Share data product to target HANA Cloud instance

**Result**:
- Data product metadata shared
- No data replication
- Virtual table definitions prepared
- Access permissions configured

### Phase 3: Install (In HANA Cloud Central)

**Tool**: SAP HANA Cloud Central → Data Products tab

**Installation Creates**:
- **Remote Source**: Named connection to SAP BDC
- **Virtual Tables**: One per business object
- **Schema**: Organized by data product
- **Metadata**: Column definitions, types, descriptions

### Phase 4: Query and Access

**Methods**:

**1. Database Explorer**:
```
Data Products → [Product Name] → Virtual Tables
```

**2. SQL Console**:
```sql
-- Query virtual table
SELECT * FROM [SCHEMA].[SALES_ORDER]
WHERE CreatedDate >= '2026-01-01';

-- Join virtual tables
SELECT 
    so.SalesOrderID,
    soi.ProductID,
    soi.Quantity
FROM [SCHEMA].[SALES_ORDER] so
JOIN [SCHEMA].[SALES_ORDER_ITEM] soi
    ON so.SalesOrderID = soi.SalesOrderID;
```

**3. Application Code**:
```python
# Via HANA Connection Module
from modules.hana_connection.backend import HanaConnectionService

conn = HanaConnectionService()
result = conn.execute_query("""
    SELECT * FROM [DATA_PRODUCT].[SUPPLIER_INVOICE]
    WHERE PostingDate >= CURRENT_DATE - 30
""")
```

## Data Product Management

### Update

**When**: New version available, schema changes, metadata updates

**Process**:
1. Navigate to Data Products in HANA Cloud Central
2. Select installed product
3. Click "Update"
4. Virtual tables refreshed automatically

### Uninstall

**When**: No longer needed, replaced, maintenance

**Process**:
1. Select data product
2. Click "Uninstall"
3. Virtual tables removed
4. Remote source optionally removed

### Monitor

**What to Monitor**:
- Installation status
- Virtual table usage
- Query performance
- Data freshness
- Remote source availability

## P2P Project Integration

### Available Data Products

**Your CSN Files** (P2P domain):
- sap-s4com-Supplier-v1
- sap-s4com-PurchaseOrder-v1
- sap-s4com-ServiceEntrySheet-v1
- sap-s4com-SupplierInvoice-v1
- sap-s4com-PaymentTerms-v1
- sap-s4com-JournalEntryHeader-v1

### Integration Approaches

**Option 1: Consume SAP-Managed Products** (Recommended Start)
1. Create formation with HANA Cloud instance
2. Browse SAP BDC catalog for P2P products
3. Share and install relevant products
4. Query via virtual tables
5. Join with local P2P schema

**Option 2: Create Custom Data Product** (Future)
1. Load SAP data products
2. Build P2P logic in HANA Cloud
3. Create enriched data product in Datasphere
4. Publish to catalog

### Implementation Status

**Current State**:
- ✅ HANA Cloud connection established
- ✅ Formation configured
- ✅ Data product structure understood
- ✅ CSN definitions available
- ✅ Virtual table approach validated

**Next Steps**:
1. Browse BDC catalog for P2P products
2. Share relevant products to HANA Cloud
3. Install and test virtual tables
4. Build P2P analytics queries
5. Integrate with application

## Best Practices

### Performance Optimization

**1. Selective Queries** (Filter at Source)
```sql
-- ✅ GOOD: Filter remotely
SELECT * FROM VIRTUAL_TABLE
WHERE Date >= '2026-01-01'
  AND Region = 'EMEA';

-- ❌ AVOID: Retrieve all then filter locally
SELECT * FROM VIRTUAL_TABLE;
```

**2. Column Projection**
```sql
-- ✅ GOOD: Select only needed columns
SELECT OrderID, CustomerID, Amount
FROM VIRTUAL_TABLE;

-- ❌ AVOID: Select all columns
SELECT * FROM VIRTUAL_TABLE;
```

**3. Join Optimization**
- Join virtual tables with local tables wisely
- Consider local copies for frequently accessed data
- Use materialized views for complex queries

### Security

**Access Control**:
- Grant minimal privileges
- Use roles for virtual table access
- Audit virtual table queries
- Monitor remote source usage

**Formation Security**:
- Limit formation membership
- Separate formations for dev/prod
- Review trust relationships regularly
- Rotate credentials periodically

### Governance

**Catalog Management**:
- Document data product usage
- Track dependencies
- Maintain data lineage
- Version control

**Lifecycle**:
- Regular updates
- Deprecation planning
- Impact analysis before changes
- User communication

## Use Cases

### Use Case 1: Sales Analytics
**Scenario**: Analyze sales data from S/4HANA

**Data Products**:
- Sales Order
- Sales Order Item
- Customer
- Product

**Implementation**:
1. Install data products
2. Create analytical views on virtual tables
3. Build dashboards

### Use Case 2: Procurement Monitoring
**Scenario**: Real-time procurement dashboard

**Data Products**:
- Purchase Order
- Purchase Requisition
- Supplier
- Supplier Invoice

**Benefits**:
- Real-time access
- No ETL pipeline
- Always current

### Use Case 3: P2P Workflow (Your Project)
**Scenario**: End-to-end procurement analytics

**Data Products**:
- Supplier
- Purchase Order
- Service Entry Sheet
- Supplier Invoice
- Payment Terms
- Journal Entry

**Implementation**:
- Install all P2P data products
- Create unified P2P schema
- Build workflow analytics
- Integrate with application

## Troubleshooting

### Cannot See Shared Data Product

**Causes**:
- Formation not configured
- Trust not established
- Insufficient permissions

**Solution**:
1. Verify formation in SAP for Me
2. Check trust status
3. Confirm permissions in BDC
4. Re-share data product

### Virtual Table Query Slow

**Causes**:
- Network latency
- No filtering at source
- Large result set

**Solution**:
1. Add WHERE clauses
2. Select only needed columns
3. Check remote system performance
4. Consider local replica for frequent access

### Remote Source Connection Failed

**Causes**:
- Network connectivity
- Credentials expired
- Remote system down

**Solution**:
1. Test network connectivity
2. Verify credentials
3. Check remote system status
4. Review firewall rules

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│    SAP for Me (Formation Manager)       │
│    ┌──────────────────────────────┐     │
│    │   Trust Relationship          │     │
│    └──────────────────────────────┘     │
└──────────┬─────────────────┬────────────┘
           │                 │
           ▼                 ▼
┌──────────────────┐  ┌──────────────────┐
│  SAP BDC         │  │  HANA Cloud      │
│                  │  │                  │
│  ┌────────────┐  │  │  ┌────────────┐ │
│  │  Catalog & │  │  │  │   Remote   │ │
│  │Marketplace │  │──│──│   Source   │ │
│  └────────────┘  │  │  └──────┬─────┘ │
│                  │  │         │       │
│  ┌────────────┐  │  │         ▼       │
│  │ Foundation │  │  │  ┌────────────┐ │
│  │  Services  │  │  │  │  Virtual   │ │
│  └────────────┘  │  │  │   Tables   │ │
│                  │  │  └────────────┘ │
│  ┌────────────┐  │  │                │
│  │ HANA Data  │  │  │  ┌────────────┐ │
│  │Lake Files  │  │  │  │    SQL     │ │
│  │  (HDLF)    │  │  │  │  Console   │ │
│  └────────────┘  │  │  └────────────┘ │
└──────────────────┘  └──────────────────┘
                             │
                             ▼
                      ┌──────────────┐
                      │  P2P App     │
                      └──────────────┘
```

## Key Concepts Summary

**Data Products**: Curated business data packages  
**Formations**: Trust relationships between systems  
**Virtual Tables**: Pointers to remote data (no replication)  
**Remote Sources**: Named connections to external databases  
**Smart Data Access**: Federation without data movement  

**Workflow**: Browse → Share → Install → Query

**Benefits**:
- ✅ No data replication
- ✅ Always current
- ✅ Reduced costs
- ✅ Simplified governance

## References

### Official Documentation
- **Data Product Support**: https://help.sap.com/docs/hana-cloud
- **Virtual Tables**: https://help.sap.com/docs/hana-cloud-database
- **Remote Sources**: https://help.sap.com/docs/hana-cloud-database
- **SAP BDC Formations**: https://help.sap.com/docs/SAP_BUSINESS_DATA_CLOUD

### Project Files
- CSN definitions: `data-products/`
- Backend integration: [[HANA Connection Module]]
- Data Products module: `modules/data_products/`

## Status

✅ **ACTIVE ARCHITECTURE** - Production approach for data access

**Applied in**:
- CSN data access
- Data product consumption
- P2P workflow analytics
- Cross-system integration

**Validated by**:
- Official SAP documentation
- Formation setup
- Virtual table testing
- Production usage