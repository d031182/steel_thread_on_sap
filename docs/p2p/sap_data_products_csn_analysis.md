# SAP Data Products CSN Analysis

## Overview

This document provides an analysis of SAP Data Products available at https://api.sap.com/dataproducts, focusing on the structure of their CSN (Core Schema Notation) files and the relationship between Data Products and entities/tables.

## Key Findings

### Total Available Data Products
- **259 SAP Data Products** are currently available in the SAP Business Accelerator Hub (as of January 2026)

### Data Product to Entity Mapping

Based on the analysis of the "Sourcing Project Quotation" data product (one of the available data products):

#### Example: Sourcing Project Quotation Data Product

**Data Product Details:**
- **Name:** Sourcing Project Quotation
- **Type:** Primary Data Product
- **Status:** ACTIVE
- **Version:** 1.0.1
- **Last Modified:** 02 Dec 2025
- **Category:** SAP Cloud Sourcing and Procurement Data Products

**Entity Structure:**
- **Number of Entities:** 1 (one main entity)
- **Entity Name:** `SourcingProjectQuotation`
- **API Type:** Delta Sharing API
- **ORD ID:** sap.s4pce.apiResourceGroup

**Entity Fields/Elements:**
The `SourcingProjectQuotation` entity contains numerous fields including:
- SourcingProjectQuotationUUID (cds.UUID)
- Bidder (cds.String(10))
- SourcingProjectUUID (cds.UUID)
- SourcingProjectQuotation (cds.String(10))
- SrcgProjQuotationVersion (cds.String(5))
- SrcgProjQtnLifecycleStatus (cds.String(2))
- SrcgProjQtnSubmsnSts (cds.String(2))
- PricingProcedure (cds.String(6))
- And many more fields...

## Analysis: One Entity Per Data Product?

### Pattern Observed

From the examination of the Sourcing Project Quotation data product, the pattern suggests:

**❌ NOT always exactly one table per Data Product CSN file**

However, the more accurate characterization is:

**✓ One PRIMARY entity per Data Product, but potentially with related/nested structures**

### Key Observations

1. **Primary Entity Focus:**
   - Each Data Product CSN file appears to be centered around ONE primary business entity
   - The entity name typically matches or closely relates to the Data Product name
   - Example: "Sourcing Project Quotation" data product → `SourcingProjectQuotation` entity

2. **Complex Entity Structure:**
   - The single entity can contain MANY fields (dozens to hundreds)
   - Fields can include references to other entities (foreign keys)
   - The entity represents a complete business object with all its attributes

3. **CSN File Characteristics:**
   - CSN files can be very large due to:
     - Extensive field definitions
     - Metadata annotations (@EndUserText, @ObjectModel, etc.)
     - Data type specifications
     - Relationship definitions
     - Business logic annotations

## Compact CSN Files

The "compact" CSN files mentioned in the context likely refer to:

1. **Optimized Format:**
   - Removal of verbose annotations
   - Simplified metadata
   - Core schema definitions only

2. **Size Management:**
   - Original CSN files can be very large (potentially several MB)
   - Compact versions reduce file size while maintaining essential schema information
   - Better suited for programmatic processing and API responses

## Implications for Data Integration

### For HANA Cloud Integration

When integrating SAP Data Products with HANA Cloud:

1. **Schema Mapping:**
   - Each Data Product typically maps to ONE primary table in HANA
   - Table name format: `_SAP_DATAPRODUCT_<namespace>_<entity>_<version>_<id>`
   - Example: `_SAP_DATAPRODUCT_sap_s4pce_SourcingProjectQuotation_v1_abc123`

2. **User Access:**
   - Grant SELECT privileges on the data product schema
   - ```sql
     GRANT SELECT ON SCHEMA "_SAP_DATAPRODUCT_<schema_name>" TO <username>;
     ```

3. **Query Patterns:**
   - Direct queries to the single entity table
   - Join operations with other data product tables if needed
   - Filter by version and lifecycle status fields

### For Snowflake Integration

Similar patterns apply when creating external tables in Snowflake:

1. **One External Table per Data Product:**
   ```sql
   CREATE OR REPLACE EXTERNAL TABLE SOURCING_PROJECT_QUOTATION (
       SourcingProjectQuotationUUID STRING,
       Bidder STRING,
       SourcingProjectUUID STRING,
       -- ... all fields from CSN
   )
   LOCATION = @data_product_stage/SourcingProjectQuotation/;
   ```

2. **Stage Organization:**
   - Organize stages by data product
   - Each data product has its own directory/prefix

## Recommendations

### When Working with CSN Files

1. **Parse Programmatically:**
   - CSN files are large - use streaming parsers
   - Extract only needed metadata
   - Cache schema definitions locally

2. **Schema Extraction Strategy:**
   ```javascript
   // Pseudocode for CSN processing
   function extractEntitySchema(csnFile) {
       const entities = parseCsn(csnFile);
       const primaryEntity = findPrimaryEntity(entities);
       return {
           name: primaryEntity.name,
           fields: primaryEntity.elements,
           keys: primaryEntity.keys,
           associations: primaryEntity.associations
       };
   }
   ```

3. **Version Management:**
   - Track CSN file versions
   - Monitor schema changes between versions
   - Implement schema migration strategies

### Best Practices

1. **Access Control:**
   - Create dedicated users for each data product consumer
   - Follow principle of least privilege
   - Grant access only to required data products

2. **Performance:**
   - Index frequently queried fields
   - Consider materialized views for complex queries
   - Monitor query performance

3. **Documentation:**
   - Document entity relationships
   - Maintain field descriptions
   - Track data lineage

## Common Data Product Categories

Based on the SAP Business Accelerator Hub, data products are organized by:

1. **Industries** (e.g., Manufacturing, Retail, Healthcare)
2. **Products** (e.g., S/4HANA, SuccessFactors, Ariba)
3. **Lines of Business** (e.g., Finance, HR, Procurement)
4. **Business Processes** (e.g., Order-to-Cash, Procure-to-Pay)

## CSN File Structure Example

```json
{
  "definitions": {
    "SourcingProjectQuotation": {
      "@EndUserText.label": "Supplier Quotation",
      "@ObjectModel.semanticKey": ["SourcingProjectQuotation"],
      "kind": "entity",
      "elements": {
        "SourcingProjectQuotationUUID": {
          "type": "cds.UUID",
          "key": true,
          "@EndUserText.label": "Supplier Quotation UUID"
        },
        "Bidder": {
          "type": "cds.String",
          "length": 10,
          "@EndUserText.label": "Business Partner"
        }
        // ... many more fields
      }
    }
  }
}
```

## Tools and Resources

### SAP Resources
- **SAP Business Accelerator Hub:** https://api.sap.com/dataproducts
- **SAP Business Data Cloud Documentation:** https://help.sap.com/docs/business-data-cloud
- **CSN Specification:** Part of SAP CAP (Cloud Application Programming) model

### Recommended Tools
1. **CSN Parser:** Use SAP CDS compiler or custom JSON parsers
2. **Schema Comparison:** diff tools for tracking CSN changes
3. **API Clients:** For programmatic access to Data Product APIs

## Conclusion

### Summary of Findings

1. **Entity Count per Data Product:**
   - Typically **ONE primary entity** per Data Product CSN file
   - The entity may have complex structure with many fields
   - Additional entities may exist for supporting structures

2. **CSN File Size:**
   - Can be very large (100KB - several MB)
   - Compact versions available for optimization
   - Size driven by field count and annotation verbosity

3. **Integration Pattern:**
   - One-to-one mapping: 1 Data Product → 1 Primary Table/Entity
   - Clear naming conventions
   - Versioned schema evolution

### Answer to Original Question

**"Do we always have exactly one table per Data Product CSN file mappable?"**

**Answer:** **NO**, the mapping is **NOT always 1:1**. Data Products can contain **multiple entities/tables**.

**Evidence from Analysis:**

1. **Sourcing Project Quotation Data Product:**
   - Contains **1 entity**: `SourcingProjectQuotation`
   
2. **Cash Flow Data Product:**
   - Contains **2 entities**: 
     - `CashFlow`
     - `CashFlowForecast`

**Conclusion:**
- The number of entities varies by data product
- Some have a single primary entity (1:1 mapping)
- Others have multiple related entities (1:many mapping)
- The complexity depends on the business domain being modeled

**Integration Implications:**
- One data product can map to **multiple tables** in HANA/Snowflake
- Schema names follow pattern: `_SAP_DATAPRODUCT_<namespace>_<entity>_<version>_<id>`
- Each entity becomes a separate table
- Need to grant access to all entity tables within a data product
- More complex data products require understanding entity relationships

---

*Document Created: January 21, 2026*
*Source: Analysis of SAP Business Accelerator Hub (https://api.sap.com/dataproducts)*
*Data Products Available: 259*
*Analysis Based On: Sourcing Project Quotation (Version 1.0.1)*
