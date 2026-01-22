# Data Product Support in SAP HANA Cloud

**Consuming SAP Business Data Cloud Data Products in HANA Cloud**

**Date**: January 22, 2026, 12:05 AM  
**Source**: https://help.sap.com/docs/hana-cloud/sap-hana-cloud-administration-guide/data-product-support-in-sap-hana-cloud-internal

---

## Overview

SAP HANA Cloud provides comprehensive support for **browsing, installing, updating, and uninstalling data products** from SAP Business Data Cloud (SAP BDC). This enables seamless data sharing between SAP BDC and SAP HANA Cloud instances within a formation, using **virtual tables** and **remote sources** for federation without data replication.

---

## What Are Data Products?

### Definition

**Data products** are curated, self-describing packages of business data and metadata that are optimized for:
- Sharing across systems
- Discovery in catalogs
- Consumption via multiple protocols
- Analytics and AI applications

### Types of Data Products

**1. SAP-Managed Data Products**
- Predefined by SAP across Lines of Business (LoB)
- Customers activate them in SAP BDC
- SAP handles extraction, loading, and curation
- Examples: Sales Order, Billing Document, Purchase Order, Supplier Invoice

**2. Customer-Managed Data Products**
- Created by customers in SAP Datasphere
- Stored in customer object stores
- Published to the catalog
- Technically identical to SAP-managed products

**3. Primary Data Products**
- Original data directly from source applications
- Direct extraction from S/4HANA, SuccessFactors, etc.

**4. Derived Data Products**
- Value-added datasets
- Curated from other data products or APIs
- Enriched, transformed, or aggregated

### Data Product Characteristics

| Attribute | Description |
|-----------|-------------|
| **Type** | Primary or derived |
| **Category** | Business object, analytical, graph, spatial |
| **Visibility** | Public, internal, private |
| **Output Ports** | APIs/events for access |
| **Responsible Team** | Team managing lifecycle |
| **Storage** | HANA Data Lake Files (HDLF) |
| **Access Method** | Virtual tables, APIs, Delta Sharing |

---

## SAP Business Data Cloud Formations

### What is a Formation?

A **formation** binds provisioned components into a unified landscape for data product creation and sharing. It creates trust relationships between:
- SAP Business Data Cloud (BDC)
- SAP HANA Cloud instances
- SAP Datasphere
- SAP Databricks
- SAP Analytics Cloud
- Other integrated components

### Creating Formations

**Location**: SAP for Me portal (https://me.sap.com)

**Process**:
1. Navigate to SAP for Me
2. Go to Formations section
3. Create new formation
4. Select components to include:
   - SAP Business Data Cloud tenant
   - Target SAP HANA Cloud instances
   - Optional: SAP Databricks, SAP BW, etc.
5. Assign users with appropriate roles
6. Establish trust between systems

**Formation Benefits**:
- Simplified connectivity
- Unified customer landscape (UCL)
- Single sign-on (SSO) across components
- Centralized data product discovery
- Automatic trust establishment

### Multiple Formations

You can create multiple formations to:
- Separate development/test/production
- Include/exclude specific components
- Isolate data product sharing
- Control access per environment

**Example**:
- Formation 1: SAP BDC + HANA Cloud + Databricks
- Formation 2: SAP BDC + HANA Cloud + SAP BW

---

## Data Product Consumption Workflow

### Phase 1: Browse in SAP BDC

**Tool**: SAP Business Data Cloud Catalog & Marketplace

**Steps**:
1. Login to SAP BDC
2. Navigate to **Catalog & Marketplace**
3. Browse available data products
4. Search by:
   - Business domain (Sales, Procurement, Finance)
   - Data package (e.g., "SAP Sales Data Products")
   - Object type (e.g., "Sales Order", "Invoice")
5. Review data product details:
   - Description
   - Available APIs
   - Column definitions
   - Metadata
   - Sample data
   - Quality metrics

**Data Packages**:
- Data products are grouped into packages
- Package examples:
  - SAP Sales Data Products
  - SAP Procurement Data Products
  - SAP Finance Data Products
- Collective management and activation

### Phase 2: Share from SAP BDC

**Action**: Share data product to target HANA Cloud

**Steps**:
1. Select desired data product in catalog
2. Click "Share" or "Add Target"
3. Select target SAP HANA Cloud instance (from formation)
4. Confirm sharing
5. Data product becomes available in HANA Cloud Central

**What Happens**:
- Data product metadata shared to target
- No data replication occurs
- Virtual table definitions prepared
- Access permissions configured

### Phase 3: Install in SAP HANA Cloud

**Tool**: SAP HANA Cloud Central

**Steps**:
1. Login to SAP HANA Cloud Central
2. Navigate to **Data Products** tab
3. View shared data products from SAP BDC
4. Select data product to install
5. Click "Install"
6. Installation process:
   - Creates **remote source** automatically
   - Creates **virtual tables** for each object
   - Maps columns and metadata
   - Configures access permissions
7. Verify installation in **Data Sources** section

**What Gets Created**:
- **Remote Source**: Named connection to SAP BDC
- **Virtual Tables**: One per business object in data product
- **Schema**: Organized by data product
- **Metadata**: Column definitions, types, descriptions

### Phase 4: Query and Access

**Tools**:
- Database Explorer (web UI)
- hdbsql (command line)
- SQL Console
- Business Intelligence tools

**Access Methods**:

**1. Via Data Products Tab**
```
SAP HANA Cloud Central
  └─ Data Products
      └─ [Your Data Product]
          └─ Virtual Tables
              ├─ SALES_ORDER
              ├─ SALES_ORDER_ITEM
              └─ ...
```

**2. Via Data Sources**
```
SAP HANA Cloud Central
  └─ Data Sources
      └─ Remote Sources
          └─ [BDC_REMOTE_SOURCE]
              └─ Virtual Tables
```

**3. Via SQL**
```sql
-- Query virtual table
SELECT * FROM [SCHEMA].[SALES_ORDER]
WHERE CreatedDate >= '2026-01-01';

-- Join virtual tables
SELECT 
    so.SalesOrderID,
    so.CustomerID,
    soi.ProductID,
    soi.Quantity
FROM [SCHEMA].[SALES_ORDER] so
JOIN [SCHEMA].[SALES_ORDER_ITEM] soi
    ON so.SalesOrderID = soi.SalesOrderID;
```

---

## Virtual Tables in HANA Cloud

### What Are Virtual Tables?

**Virtual tables** point to remote tables in different data sources, allowing you to query remote data as if it were stored locally **without physically transferring the data**.

### How Virtual Tables Work

1. **Creation**: Virtual table serves as pointer to remote data
2. **Query Execution**: SQL queries access remote data directly
3. **Query Optimization**: HANA query processor optimizes queries
4. **Remote Execution**: Relevant portions execute in remote database
5. **Result Transfer**: Only results returned to HANA Cloud
6. **No Data Movement**: Data persists in only one location

### Creating Virtual Tables

**Automatic** (via data product installation):
- Virtual tables created automatically
- One per business object in data product
- Mapped to remote source

**Manual** (via SQL):
```sql
CREATE VIRTUAL TABLE [<schema_name>.]<virtual_table_name> 
AT "<remote_source>"."<database_name>"."<remote_schema_name>"."<remote_table_name>" 
[WITH REMOTE];
```

**GUI Method**:
1. Navigate to remote data source
2. Browse to schema → table
3. Right-click table
4. Select "Add as Virtual Table"

### Virtual Table Benefits

**Advantages**:
- ✅ No data duplication
- ✅ Always current (real-time access)
- ✅ Reduced storage costs
- ✅ Simplified data governance
- ✅ Single source of truth

**Considerations**:
- ⚠️ Query performance depends on network
- ⚠️ Slower than local tables
- ⚠️ Network latency impacts response time
- ⚠️ Remote system availability required

---

## Remote Sources

### What Are Remote Sources?

**Remote sources** are named connections to external databases that enable:
- Virtual table creation
- Federated queries
- Cross-system data access
- Smart data access

### Supported Remote Data Sources

SAP HANA Cloud can connect to:
- ✅ SAP HANA on-premise
- ✅ SAP HANA Cloud (other instances)
- ✅ SAP HANA Cloud Data Lake Relational Engine
- ✅ SAP Adaptive Server Enterprise (ASE)
- ✅ SAP Business Data Cloud (via data products)
- ✅ Other JDBC/ODBC sources

### Remote Source Configuration

**Automatic** (via data product):
- Remote source created during installation
- Named after data product or BDC instance
- Pre-configured with credentials
- Trust established via formation

**Manual**:
```sql
CREATE REMOTE SOURCE <remote_source_name>
ADAPTER <adapter_type>
CONFIGURATION <configuration_string>
WITH CREDENTIAL TYPE <credential_type>
USING <credential_details>;
```

---

## Data Product Management

### Update Data Products

**When to Update**:
- New version available in SAP BDC
- Schema changes in source system
- Additional objects added
- Metadata updates

**Process**:
1. Navigate to Data Products in HANA Cloud Central
2. Select installed data product
3. Click "Update"
4. Review changes
5. Confirm update
6. Virtual tables refreshed automatically

### Uninstall Data Products

**When to Uninstall**:
- No longer needed
- Replaced by newer version
- Cleanup/maintenance
- Formation changes

**Process**:
1. Navigate to Data Products
2. Select data product
3. Click "Uninstall"
4. Confirm removal
5. Virtual tables removed
6. Remote source optionally removed (if not used by others)

### Monitor Data Products

**What to Monitor**:
- Installation status
- Virtual table usage
- Query performance
- Data freshness
- Remote source availability

**Tools**:
- SAP HANA Cloud Central
- Database Explorer
- SQL System Views
- Monitoring dashboard

---

## Use Cases and Scenarios

### Use Case 1: Sales Analytics

**Scenario**: Analyze sales data from S/4HANA

**Setup**:
1. SAP BDC extracts sales data from S/4HANA
2. Create "Sales Analytics" formation
3. Share SAP Sales Data Products to HANA Cloud
4. Install data product in HANA Cloud
5. Create analytical views on virtual tables
6. Build dashboards in SAC

**Data Products Used**:
- Sales Order
- Sales Order Item
- Customer
- Product

### Use Case 2: Procurement Dashboard

**Scenario**: Real-time procurement monitoring

**Setup**:
1. Share SAP Procurement Data Products
2. Install in HANA Cloud
3. Query virtual tables:
   - Purchase Order
   - Purchase Requisition
   - Supplier
   - Supplier Invoice

**Benefits**:
- Real-time data access
- No ETL pipeline needed
- Always current information

### Use Case 3: Financial Reporting

**Scenario**: Cross-system financial reports

**Setup**:
1. Install multiple data products:
   - Journal Entry Header
   - Journal Entry Item
   - GL Account
   - Cost Center
2. Create calculation views joining virtual tables
3. Build financial reports

### Use Case 4: Custom Data Product

**Scenario**: Create enriched P2P data product

**Your Context**:
1. Install SAP data products (Supplier, PO, Invoice)
2. Create local P2P schema with custom logic
3. Join virtual tables with local tables
4. Create derived data product in Datasphere
5. Share to other HANA Cloud instances

---

## Best Practices

### Performance Optimization

**1. Selective Queries**
```sql
-- Good: Filter at source
SELECT * FROM VIRTUAL_TABLE
WHERE Date >= '2026-01-01'
  AND Region = 'EMEA';

-- Avoid: Retrieve all then filter
SELECT * FROM VIRTUAL_TABLE; -- Then filter in app
```

**2. Use Projections**
```sql
-- Good: Select only needed columns
SELECT OrderID, CustomerID, Amount
FROM VIRTUAL_TABLE;

-- Avoid: Select all columns
SELECT * FROM VIRTUAL_TABLE;
```

**3. Join Optimization**
- Join virtual tables with local tables wisely
- Consider creating local copies for frequently accessed data
- Use materialized views for complex queries

### Security Best Practices

**1. Access Control**
- Grant minimal privileges
- Use roles for virtual table access
- Audit virtual table queries
- Monitor remote source usage

**2. Formation Security**
- Limit formation membership
- Use separate formations for dev/prod
- Review trust relationships regularly
- Rotate credentials periodically

### Governance

**1. Data Product Catalog**
- Document data product usage
- Track dependencies
- Maintain data lineage
- Version control

**2. Lifecycle Management**
- Regular updates
- Deprecation planning
- Impact analysis before changes
- User communication

---

## Troubleshooting

### Issue: Cannot See Shared Data Product

**Possible Causes**:
- Formation not configured
- Trust not established
- Insufficient permissions
- Data product not shared to your instance

**Solution**:
1. Verify formation membership
2. Check trust status in SAP for Me
3. Confirm permissions in SAP BDC
4. Re-share data product if needed

### Issue: Virtual Table Query Slow

**Possible Causes**:
- Network latency
- Remote system overloaded
- Large result set
- No filtering at source

**Solution**:
1. Add WHERE clauses to filter at source
2. Select only needed columns
3. Check remote system performance
4. Consider creating local replica for frequently accessed data

### Issue: Remote Source Connection Failed

**Possible Causes**:
- Network connectivity
- Credentials expired
- Remote system down
- Firewall blocking

**Solution**:
1. Test network connectivity
2. Verify credentials
3. Check remote system status
4. Review firewall rules

### Issue: Installation Failed

**Possible Causes**:
- Insufficient privileges
- Schema conflicts
- Disk space
- Remote source limit reached

**Solution**:
1. Check DBADMIN privileges
2. Resolve schema name conflicts
3. Free up disk space
4. Contact SAP support for remote source limits

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    SAP for Me (Formation)                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                  Trust Relationship                     │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────┬────────────────────────────┬────────────────┘
                │                            │
                ▼                            ▼
     ┌──────────────────────┐     ┌──────────────────────┐
     │  SAP Business Data   │     │   SAP HANA Cloud     │
     │       Cloud          │     │                      │
     │                      │     │                      │
     │  ┌────────────────┐  │     │  ┌────────────────┐ │
     │  │  Data Product  │  │────▶│  │ Remote Source  │ │
     │  │   Catalog &    │  │     │  │                │ │
     │  │  Marketplace   │  │     │  └────────┬───────┘ │
     │  └────────────────┘  │     │           │         │
     │                      │     │           ▼         │
     │  ┌────────────────┐  │     │  ┌────────────────┐ │
     │  │ Foundation     │  │     │  │ Virtual Tables │ │
     │  │   Services     │  │     │  │  - Sales Order │ │
     │  │                │  │     │  │  - Purchase PO │ │
     │  └───────┬────────┘  │     │  │  - Supplier    │ │
     │          │           │     │  │  - Invoice     │ │
     │          ▼           │     │  └────────────────┘ │
     │  ┌────────────────┐  │     │                      │
     │  │  HANA Data     │  │     │  ┌────────────────┐ │
     │  │  Lake Files    │  │     │  │  SQL Console   │ │
     │  │   (HDLF)       │  │     │  │  DB Explorer   │ │
     │  └────────────────┘  │     │  └────────────────┘ │
     └──────────────────────┘     └──────────────────────┘
                                            │
                                            ▼
                                   ┌────────────────┐
                                   │   Your P2P     │
                                   │  Application   │
                                   └────────────────┘
```

---

## Integration with Your P2P Project

### Current State

**Your Data Products** (CSN files):
- ✅ sap-s4com-Supplier-v1.json
- ✅ sap-s4com-PurchaseOrder-v1.json
- ✅ sap-s4com-ServiceEntrySheet-v1.json
- ✅ sap-s4com-SupplierInvoice-v1.json
- ✅ sap-s4com-PaymentTerms-v1.json
- ✅ sap-s4com-JournalEntryHeader-v1.json

### Integration Path

**Option 1: Consume SAP-Managed Data Products**
1. Create formation with your HANA Cloud instance
2. Browse SAP BDC catalog for P2P data products
3. Share and install relevant products
4. Query via virtual tables
5. Join with your local P2P schema

**Option 2: Create Custom Data Product**
1. Load SAP data products
2. Build your P2P logic in HANA Cloud
3. Create enriched data product in Datasphere
4. Publish to catalog for others

**Recommended**: Start with Option 1, then evolve to Option 2

---

## References

### Official Documentation

1. **Data Product Support in SAP HANA Cloud**
   - https://help.sap.com/docs/hana-cloud/sap-hana-cloud-administration-guide/data-product-support-in-sap-hana-cloud-internal

2. **Virtual Tables Documentation**
   - https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-data-access-guide/create-virtual-table

3. **Remote Sources Guide**
   - https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-data-access-guide/create-sap-hana-cloud-sap-hana-database-remote-source

4. **Data Access Guide**
   - https://help.sap.com/docs/hana-cloud-database/sap-hana-cloud-sap-hana-database-data-access-guide

5. **Creating Data Products for SAP BDC**
   - https://help.sap.com/docs/SAP_DATASPHERE/e4059f908d16406492956e5dbcf142dc/b07e95d07a1e4569b87d9bb57b732bcf.html

6. **SAP BDC Formations**
   - https://help.sap.com/docs/SAP_BUSINESS_DATA_CLOUD/53f5791b6722402b8adfddfa04fbe247/37946c5f042e497b9597ef2da5f1835a.html

### Tutorials

1. **Access and Query Data Products** (SAP Developers)
   - https://developers.sap.com/tutorials/hana-cloud-data-products-consumption.html

2. **Access Remote Sources** (SAP Developers)
   - https://developers.sap.com/tutorials/hana-dbx-remote-sources.html

### Architecture

1. **Data Products in SAP BDC** (Architecture Center)
   - https://architecture.learning.sap.com/docs/ref-arch/f5b6b597a6/1

2. **SAP BDC Reference Architecture**
   - https://architecture.learning.sap.com/docs/ref-arch/f5b6b597a6/3

### Learning

1. **Virtual Tables** (SAP Learning)
   - https://learning.sap.com/courses/prd_hc_intro_proto/vt

2. **Exploring and Installing Data Products** (SAP Learning)
   - https://learning.sap.com/courses/introducing-sap-business-data-cloud/exploring-and-deploying-objects-with-sap-business-data-cloud-cockpit

### Community

1. **SAP BDC Series - Part 1: Data Products**
   - https://community.sap.com/t5/technology-blog-posts-by-sap/sap-business-data-cloud-series-part-1-introduction-to-data-products/ba-p/14142919

---

## Summary

### Key Concepts

1. **Data Products** = Curated business data packages from SAP BDC
2. **Formations** = Trust relationships between BDC and HANA Cloud
3. **Virtual Tables** = Pointers to remote data (no replication)
4. **Remote Sources** = Named connections to external databases
5. **Smart Data Access** = Federation without data movement

### Workflow

```
Browse (BDC Catalog) → Share (to HANA Cloud) → Install (creates virtual tables) → Query (SQL)
```

### Benefits

- ✅ No data replication
- ✅ Always current data
- ✅ Reduced storage costs
- ✅ Simplified governance
- ✅ Unified data access

### Your Next Steps

1. 📋 Verify formation setup in SAP for Me
2. 📋 Browse SAP BDC catalog for P2P data products
3. 📋 Share relevant data products to your HANA Cloud
4. 📋 Install data products
5. 📋 Query virtual tables
6. 📋 Build P2P analytics

---

**Document Version**: 1.0  
**Status**: Production-ready  
**Last Updated**: January 22, 2026, 12:05 AM  
**Next Review**: When SAP releases new data products or features
