# BDC MCP Server - CSN/ORD Retrieval Guide

**Retrieving Data Product CSN Definitions via BDC MCP Server**

**Date**: January 22, 2026, 11:55 AM  
**Status**: Production-ready capability discovered

---

## Overview

The **BDC MCP Server** provides programmatic access to **CSN (Core Schema Notation)** definitions and **ORD (Open Resource Discovery)** metadata for all SAP Business Data Cloud data products. This enables dynamic retrieval of up-to-date schema definitions without relying on static local files.

---

## What is CSN?

**Core Schema Notation (CSN)** is SAP's standard format for defining data models:

- **Entities**: Business objects (e.g., Supplier, PurchaseOrder)
- **Elements**: Fields/columns with metadata
- **Associations**: Relationships between entities
- **Annotations**: Semantic information (@EndUserText, etc.)
- **Types**: Data types, lengths, precision

CSN provides the **authoritative schema definition** for data products.

---

## What is ORD?

**Open Resource Discovery (ORD)** is SAP's standard for describing APIs and data resources:

- **Resource Definitions**: Links to schemas, APIs, events
- **Metadata**: Descriptions, versions, release status
- **Entry Points**: Delta Sharing URLs, API endpoints
- **Discovery**: Catalog information

---

## BDC MCP Server Configuration

### Server Details

**Server Name**: `BDC mcp`  
**Type**: `streamableHttp`  
**URL**: `https://mcp-server.bdci.internal.cfapps.sap.hana.ondemand.com/mcp`

### Available Tools

| Tool | Purpose | Auto-Approve |
|------|---------|--------------|
| `csnSchema` | Retrieve CSN definition from URL | ✅ Yes |
| `availableDataProducts` | List all data products with ORD | ✅ Yes |
| `dataProductDetails` | Get detailed product info | ✅ Yes |
| `formationDetails` | Get formation configuration | ✅ Yes |
| `installedDataProductsInHana` | List installed products | ✅ Yes |
| `availableDataProductsForHana` | List installable products | ✅ Yes |
| `installDataProductInHana` | Install data product | ✅ Yes |
| `deleteDataProductInHana` | Remove data product | ✅ Yes |
| `SQLQueryWithHana` | Execute SQL against HANA | ✅ Yes |

---

## CSN Retrieval Workflow

### Step 1: Get Available Data Products

**Tool**: `availableDataProducts`

**Request**:
```json
{
  "server_name": "BDC mcp",
  "tool_name": "availableDataProducts",
  "arguments": {}
}
```

**Response** (excerpt):
```json
[
  {
    "ordId": "sap.s4com:apiResource:Supplier:v1",
    "description": "A business partner who provides materials and/or services.",
    "shortDescription": "Data Product Supplier",
    "releaseStatus": "active",
    "disabled": false,
    "entryPoints": [
      {
        "value": "https://...files.hdl.../sharing/v1/shares/sap.s4com.supplier:v1"
      }
    ],
    "resourceDefinitions": [
      {
        "type": "sap-csn-interop-effective-v1",
        "mediaType": "application/json",
        "url": "https://canary.discovery.api.sap/.../specification/..."
      }
    ]
  }
]
```

**Key Fields**:
- `ordId`: Unique data product identifier
- `resourceDefinitions[0].url`: CSN schema URL
- `resourceDefinitions[0].type`: Format type (CSN)
- `entryPoints[0].value`: Delta Sharing endpoint
- `disabled`: Whether product is available

### Step 2: Extract CSN URL

From the response, extract the CSN URL:
```javascript
const csnUrl = dataProduct.resourceDefinitions
  .find(rd => rd.type === "sap-csn-interop-effective-v1")
  ?.url;
```

### Step 3: Retrieve CSN Schema

**Tool**: `csnSchema`

**Request**:
```json
{
  "server_name": "BDC mcp",
  "tool_name": "csnSchema",
  "arguments": {
    "csnUrl": "https://canary.discovery.api.sap/open-resource-discovery-static/v0/api/b6d7050b-8c9a-4c4d-9689-346e4ab14855/specification/5b6cb175-7b2e-4fbc-bdf3-bfd315abeab5"
  }
}
```

**Response Structure**:
```json
{
  "meta": {},
  "definitions": {
    "supplier": {},
    "supplier.Supplier": {
      "elements": {
        "Supplier": {
          "@EndUserText.quickInfo": "Account Number of Supplier",
          "key": true,
          "type": "cds.String",
          "length": 10
        },
        "SupplierName": {
          "@EndUserText.quickInfo": "Name of Supplier",
          "type": "cds.String",
          "length": 80
        }
        // ... more fields
      }
    }
  }
}
```

---

## CSN Schema Structure

### Top Level
```json
{
  "meta": {},           // Metadata
  "definitions": {}     // Entity definitions
}
```

### Entity Definition
```json
"supplier.Supplier": {
  "elements": {
    "FieldName": {
      "@EndUserText.quickInfo": "Field description",
      "key": true,                    // Primary key flag
      "type": "cds.String",           // CDS data type
      "length": 10,                   // Field length
      "precision": 34,                // For decimals
      "scale": 4                      // For decimals
    }
  }
}
```

### CDS Data Types

| CDS Type | Description | Example |
|----------|-------------|---------|
| `cds.String` | Character string | `"ACME Corp"` |
| `cds.Date` | Date (YYYY-MM-DD) | `"2026-01-22"` |
| `cds.Boolean` | True/False | `true` |
| `cds.Decimal` | Decimal number | `123.45` |
| `cds.Integer` | Whole number | `42` |
| `cds.UUID` | Unique identifier | `"a1b2c3..."` |
| `cds.Association` | Entity relationship | (target entity) |

### Associations

Relationships between entities:
```json
"_SupplierCompany": {
  "type": "cds.Association",
  "target": "supplier.SupplierCompanyCode",
  "on": [
    { "ref": ["Supplier"] },
    "=",
    { "ref": ["_SupplierCompany", "Supplier"] }
  ]
}
```

---

## P2P Data Products - CSN URLs

### Core P2P Data Products

| Data Product | ORD ID | Status | CSN Available |
|--------------|--------|--------|---------------|
| **Supplier** | `sap.s4com:apiResource:Supplier:v1` | ✅ Active | ✅ Yes |
| **Purchase Order** | `sap.s4com:apiResource:PurchaseOrder:v1` | ✅ Active | ✅ Yes |
| **Supplier Invoice** | `sap.s4com:apiResource:SupplierInvoice:v1` | ✅ Active | ✅ Yes |
| **Service Entry Sheet** | `sap.s4com:apiResource:ServiceEntrySheet:v1` | ✅ Active | ✅ Yes |
| **Payment Terms** | `sap.s4com:apiResource:PaymentTerms:v1` | ✅ Active | ✅ Yes |
| **Journal Entry Header** | `sap.s4com:apiResource:JournalEntryHeader:v1` | ✅ Active | ✅ Yes |

### Supplier CSN Example

**Entities**:
1. `supplier.Supplier` (Main entity, 120+ fields)
2. `supplier.SupplierCompanyCode` (Company-specific data)
3. `supplier.SupplierPurchasingOrganization` (Purchasing data)
4. `supplier.SupplierWithHoldingTax` (Tax data)

**Key Fields** (Supplier entity):
- `Supplier` (String, 10) - Primary key
- `SupplierName` (String, 80)
- `SupplierFullName` (String, 220)
- `Country` (String, 3)
- `CreationDate` (Date)
- `VATRegistration` (String, 20)
- `PostingIsBlocked` (Boolean)
- `PurchasingIsBlocked` (Boolean)
- And 100+ more fields...

---

## Comparison: Local Files vs. BDC MCP

### Local CSN Files

**Location**: `data-products/`

**Files**:
```
sap-s4com-Supplier-v1.en.json
sap-s4com-PurchaseOrder-v1.en.json
sap-s4com-SupplierInvoice-v1.en-complete.json
sap-s4com-ServiceEntrySheet-v1.en.json
sap-s4com-PaymentTerms-v1.en.json
sap-s4com-JournalEntryHeader-v1.en.json
```

**Advantages**:
- ✅ Offline access
- ✅ No API dependency
- ✅ Fast access
- ✅ Version controlled

**Limitations**:
- ⚠️ May become outdated
- ⚠️ Manual updates required
- ⚠️ No automated sync

### BDC MCP CSN Retrieval

**Method**: API call via MCP tool

**Advantages**:
- ✅ Always current
- ✅ Authoritative source
- ✅ Automated retrieval
- ✅ Real-time updates
- ✅ All 100+ data products available

**Limitations**:
- ⚠️ Requires network access
- ⚠️ API call overhead
- ⚠️ Depends on BDC availability

---

## Implementation Examples

### Example 1: Retrieve Single CSN

```python
# Python (using Cline MCP integration)
from mcp_client import use_mcp_tool

# Step 1: Get available products
products = use_mcp_tool(
    server_name="BDC mcp",
    tool_name="availableDataProducts",
    arguments={}
)

# Step 2: Find Supplier and extract CSN URL
supplier = next(p for p in products if p['ordId'] == 'sap.s4com:apiResource:Supplier:v1')
csn_url = supplier['resourceDefinitions'][0]['url']

# Step 3: Retrieve CSN
csn_schema = use_mcp_tool(
    server_name="BDC mcp",
    tool_name="csnSchema",
    arguments={"csnUrl": csn_url}
)

# Result: Complete CSN schema
print(csn_schema['definitions']['supplier.Supplier'])
```

### Example 2: Bulk CSN Download

```python
# Download all P2P data product CSNs
p2p_products = [
    'sap.s4com:apiResource:Supplier:v1',
    'sap.s4com:apiResource:PurchaseOrder:v1',
    'sap.s4com:apiResource:SupplierInvoice:v1',
    'sap.s4com:apiResource:ServiceEntrySheet:v1',
    'sap.s4com:apiResource:PaymentTerms:v1',
    'sap.s4com:apiResource:JournalEntryHeader:v1'
]

for product_id in p2p_products:
    # Get product metadata
    product = next(p for p in products if p['ordId'] == product_id)
    csn_url = product['resourceDefinitions'][0]['url']
    
    # Retrieve CSN
    csn = use_mcp_tool(
        server_name="BDC mcp",
        tool_name="csnSchema",
        arguments={"csnUrl": csn_url}
    )
    
    # Save to file
    filename = f"data-products/{product_id.replace(':', '-')}-live.json"
    with open(filename, 'w') as f:
        json.dump(csn, f, indent=2)
```

### Example 3: Compare Local vs. Live

```python
import json

# Load local CSN
with open('data-products/sap-s4com-Supplier-v1.en.json') as f:
    local_csn = json.load(f)

# Retrieve live CSN from BDC
live_csn = get_csn_from_bdc('sap.s4com:apiResource:Supplier:v1')

# Compare entities
local_entities = set(local_csn['definitions'].keys())
live_entities = set(live_csn['definitions'].keys())

print("New entities:", live_entities - local_entities)
print("Removed entities:", local_entities - live_entities)

# Compare fields in main entity
local_fields = set(local_csn['definitions']['supplier.Supplier']['elements'].keys())
live_fields = set(live_csn['definitions']['supplier.Supplier']['elements'].keys())

print("New fields:", live_fields - local_fields)
print("Removed fields:", local_fields - live_fields)
```

---

## Flask Backend Integration Plan

### API Endpoint Design

**Endpoint 1: Get Available Data Products**
```
GET /api/bdc/data-products
```
**Response**:
```json
[
  {
    "ordId": "sap.s4com:apiResource:Supplier:v1",
    "name": "Supplier",
    "description": "A business partner who provides materials and/or services",
    "releaseStatus": "active",
    "csnUrl": "https://...",
    "deltaShareUrl": "https://..."
  }
]
```

**Endpoint 2: Get CSN Schema**
```
GET /api/bdc/csn/<ord_id>
```
**Example**: `/api/bdc/csn/sap.s4com:apiResource:Supplier:v1`

**Response**:
```json
{
  "ordId": "sap.s4com:apiResource:Supplier:v1",
  "definitions": {
    "supplier.Supplier": {
      "elements": { /* ... */ }
    }
  }
}
```

**Endpoint 3: Compare Local vs. Live**
```
GET /api/bdc/csn/compare/<ord_id>
```
**Response**:
```json
{
  "ordId": "sap.s4com:apiResource:Supplier:v1",
  "localVersion": "2026-01-15",
  "liveVersion": "2026-01-22",
  "differences": {
    "newEntities": [],
    "removedEntities": [],
    "newFields": ["BPPanValidFromDate"],
    "removedFields": [],
    "modifiedFields": []
  }
}
```

### Implementation Code Sketch

```python
# app.py
from flask import Flask, jsonify
import subprocess
import json

@app.route('/api/bdc/data-products')
def get_available_data_products():
    """Get all available data products from BDC"""
    result = call_mcp_tool(
        server="BDC mcp",
        tool="availableDataProducts",
        args={}
    )
    
    # Transform to simpler format
    products = []
    for dp in result:
        csn_def = next(
            (rd for rd in dp['resourceDefinitions'] 
             if rd['type'] == 'sap-csn-interop-effective-v1'),
            None
        )
        
        products.append({
            'ordId': dp['ordId'],
            'name': dp['ordId'].split(':')[-2],
            'description': dp['description'],
            'shortDescription': dp['shortDescription'],
            'releaseStatus': dp['releaseStatus'],
            'disabled': dp['disabled'],
            'csnUrl': csn_def['url'] if csn_def else None,
            'deltaShareUrl': dp['entryPoints'][0]['value'] if dp['entryPoints'] else None
        })
    
    return jsonify(products)

@app.route('/api/bdc/csn/<path:ord_id>')
def get_csn_schema(ord_id):
    """Retrieve CSN schema for specific data product"""
    # Get data products
    products = call_mcp_tool(
        server="BDC mcp",
        tool="availableDataProducts",
        args={}
    )
    
    # Find matching product
    product = next((p for p in products if p['ordId'] == ord_id), None)
    if not product:
        return jsonify({'error': 'Data product not found'}), 404
    
    # Extract CSN URL
    csn_def = next(
        (rd for rd in product['resourceDefinitions'] 
         if rd['type'] == 'sap-csn-interop-effective-v1'),
        None
    )
    
    if not csn_def:
        return jsonify({'error': 'CSN not available'}), 404
    
    # Retrieve CSN
    csn = call_mcp_tool(
        server="BDC mcp",
        tool="csnSchema",
        args={"csnUrl": csn_def['url']}
    )
    
    return jsonify({
        'ordId': ord_id,
        'csnUrl': csn_def['url'],
        'schema': csn
    })

def call_mcp_tool(server, tool, args):
    """Helper to call MCP tools via CLI"""
    # Implementation depends on MCP client availability
    # Could use subprocess or direct MCP client library
    pass
```

---

## Frontend Integration

### Data Products Explorer Enhancement

**Add "View Live CSN" Button**:
```javascript
// In dataProductsExplorer.js
async function viewLiveCSN(ordId) {
    showLoader();
    
    try {
        const response = await fetch(`/api/bdc/csn/${ordId}`);
        const data = await response.json();
        
        // Display in modal
        showCSNModal(data.schema);
    } catch (error) {
        showError('Failed to retrieve CSN schema');
    } finally {
        hideLoader();
    }
}

function showCSNModal(schema) {
    // Display CSN in formatted view
    const entities = Object.keys(schema.definitions);
    
    const html = `
        <div class="csn-viewer">
            <h3>CSN Schema</h3>
            ${entities.map(entityName => `
                <div class="entity">
                    <h4>${entityName}</h4>
                    <table>
                        <tr>
                            <th>Field</th>
                            <th>Type</th>
                            <th>Length</th>
                            <th>Key</th>
                            <th>Description</th>
                        </tr>
                        ${renderFields(schema.definitions[entityName])}
                    </table>
                </div>
            `).join('')}
        </div>
    `;
    
    openModal(html);
}
```

---

## Use Cases

### Use Case 1: Schema Validation

**Scenario**: Verify local CSN files are up-to-date

**Steps**:
1. Retrieve live CSN from BDC
2. Compare with local CSN file
3. Report differences
4. Update local file if needed

**Benefit**: Ensure application uses current schemas

### Use Case 2: Dynamic Table Creation

**Scenario**: Create HANA tables matching BDC schema

**Steps**:
1. Retrieve CSN for data product
2. Parse entity definitions
3. Generate CREATE TABLE SQL
4. Execute in HANA

**Benefit**: Automated table creation matching source

### Use Case 3: API Documentation

**Scenario**: Generate API docs from CSN

**Steps**:
1. Retrieve all P2P CSN schemas
2. Extract field definitions
3. Generate OpenAPI/Swagger spec
4. Publish documentation

**Benefit**: Auto-generated, always current docs

### Use Case 4: Data Quality Validation

**Scenario**: Validate data against CSN constraints

**Steps**:
1. Retrieve CSN schema
2. Extract field types, lengths, constraints
3. Validate data against rules
4. Report violations

**Benefit**: Ensure data quality at source

---

## CSN Field Metadata

### Available Annotations

**@EndUserText.quickInfo**: Human-readable description
```json
"@EndUserText.quickInfo": "Account Number of Supplier"
```

**key**: Primary key indicator
```json
"key": true
```

**type**: CDS data type
```json
"type": "cds.String"
```

**length**: Maximum field length
```json
"length": 80
```

**precision/scale**: For decimal numbers
```json
"precision": 34,
"scale": 4
```

---

## Supplier CSN - Complete Structure

### Main Entity: supplier.Supplier

**Field Count**: 120+ fields

**Categories**:

**1. Identifiers** (10 fields)
- Supplier (key)
- AddressID
- Customer
- InternationalLocationNumber (1, 2, 3)

**2. Names** (10 fields)
- SupplierName
- SupplierFullName
- BPSupplierName
- BusinessPartnerName1-4
- OrganizationBPName1-2

**3. Address** (15 fields)
- Country
- Region
- CityName
- PostalCode
- StreetName
- BPAddrCityName
- BPAddrStreetName
- DistrictName

**4. Tax Information** (15 fields)
- VATRegistration
- TaxJurisdiction
- TaxNumber1-6
- TaxNumberType
- TaxNumberResponsible
- WithholdingTaxCountry

**5. Organizational** (10 fields)
- SupplierAccountGroup
- Industry
- IndustryType
- SupplierCorporateGroup
- AuthorizationGroup

**6. Status Flags** (15 fields)
- AccountIsBlockedForPosting
- PostingIsBlocked
- PurchasingIsBlocked
- PaymentIsBlockedForSupplier
- DeletionIndicator
- IsOneTimeAccount
- IsNaturalPerson
- VATLiability

**7. Contact** (5 fields)
- PhoneNumber1
- PhoneNumber2
- FaxNumber
- SupplierLanguage

**8. Dates** (5 fields)
- CreationDate
- BirthDate
- SuplrQltyInProcmtCertfnValidTo
- BPPanValidFromDate

**9. Business Process** (20 fields)
- SupplierQualityManagementSystem
- SupplierProcurementBlock
- SuplrProofOfDelivRlvtCode
- TradingPartner
- FactoryCalendar
- PaymentReason

**10. Regional/Country-Specific** (20+ fields)
- UK_* fields (8 fields for UK)
- AU_* fields (9 fields for Australia)
- US_* fields
- BR_* fields (Brazil)
- IN_* fields (India)

**11. Associations** (2)
- _SupplierCompany → SupplierCompanyCode
- _SupplierPurchasingOrg → SupplierPurchasingOrganization

---

## Best Practices

### 1. Caching Strategy

**Cache CSN definitions** to avoid repeated API calls:
```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def get_cached_csn(ord_id, cache_date):
    """Cache CSN for 24 hours"""
    return retrieve_csn_from_bdc(ord_id)

# Use with daily cache key
cache_key = datetime.now().strftime('%Y-%m-%d')
csn = get_cached_csn(ord_id, cache_key)
```

### 2. Error Handling

```python
try:
    csn = call_mcp_tool(
        server="BDC mcp",
        tool="csnSchema",
        args={"csnUrl": csn_url}
    )
except MCPError as e:
    # Fall back to local file
    with open(f'data-products/{ord_id}-local.json') as f:
        csn = json.load(f)
    logging.warning(f"Used local CSN fallback: {e}")
```

### 3. Version Tracking

**Store CSN version metadata**:
```json
{
  "ordId": "sap.s4com:apiResource:Supplier:v1",
  "retrievedAt": "2026-01-22T11:54:00Z",
  "csnUrl": "https://...",
  "checksum": "a1b2c3d4...",
  "definitions": { /* ... */ }
}
```

### 4. Incremental Updates

**Only update if changed**:
```python
def update_csn_if_changed(ord_id):
    live_csn = retrieve_from_bdc(ord_id)
    local_csn = load_local_csn(ord_id)
    
    if csn_checksum(live_csn) != csn_checksum(local_csn):
        save_local_csn(ord_id, live_csn)
        return True  # Updated
    return False  # No change
```

---

## Security Considerations

### Access Control

**BDC MCP Server**:
- Requires SAP authentication
- Formation membership required
- Respects data product permissions
- Audit logging enabled

**Best Practices**:
- Don't expose CSN URLs publicly
- Cache responsibly
- Rate limit API calls
- Log CSN retrievals

---

## Troubleshooting

### Issue: CSN URL Not Found

**Symptom**: `resourceDefinitions` is empty or has no CSN type

**Cause**: Data product not activated or CSN not published

**Solution**:
1. Check data product status (disabled field)
2. Verify formation includes BDC
3. Contact SAP if CSN missing

### Issue: MCP Tool Call Fails

**Symptom**: MCP error or timeout

**Possible Causes**:
- Network connectivity
- BDC server unavailable
- Authentication expired
- Invalid CSN URL

**Solution**:
1. Check network connectivity
2. Verify BDC MCP server config
3. Test with simple `availableDataProducts` call
4. Use local CSN file as fallback

### Issue: CSN Format Different from Expected

**Symptom**: Missing fields or unexpected structure

**Cause**: CSN format evolution or version mismatch

**Solution**:
1. Check CSN version in response
2. Review SAP documentation for format changes
3. Update parsing logic
4. Add compatibility layer

---

## Future Enhancements

### Phase 1: Basic Integration ✅
- [x] Document BDC MCP capabilities
- [x] Test CSN retrieval
- [ ] Add to project documentation

### Phase 2: Backend API (Planned)
- [ ] Create Flask endpoints
- [ ] Implement caching
- [ ] Add error handling
- [ ] Write tests

### Phase 3: Frontend UI (Planned)
- [ ] Add "View CSN" button
- [ ] CSN schema viewer modal
- [ ] Compare local vs. live UI
- [ ] Download CSN option

### Phase 4: Automation (Future)
- [ ] Scheduled CSN updates
- [ ] Change notifications
- [ ] Automatic local file sync
- [ ] Schema version tracking

---

## Related Documentation

1. **DATA_PRODUCT_SUPPORT_IN_HANA_CLOUD.md**
   - Data products overview
   - Virtual tables and remote sources

2. **RETRIEVE_DATA_PRODUCTS_FROM_HANA.md**
   - Querying installed data products
   - HANA SQL examples

3. **P2P_DATA_PRODUCTS_GAP_ANALYSIS.md**
   - P2P data product analysis
   - Entity mapping

4. **CSN_ENTITY_MAPPING_ANALYSIS.md**
   - Local CSN file analysis
   - Entity relationships

---

## Quick Reference

### BDC MCP Tools Summary

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `availableDataProducts` | List all products | `{}` | Array of products with ORD |
| `csnSchema` | Get CSN schema | `{csnUrl}` | CSN definitions |
| `dataProductDetails` | Get product info | `{ordId}` | Detailed metadata |
| `installedDataProductsInHana` | List installed | `{}` | Installed products |
| `SQLQueryWithHana` | Run SQL | `{query}` | Query results |

### CSN URL Pattern

```
https://canary.discovery.api.sap/open-resource-discovery-static/v0/
  api/{api_id}/
  specification/{spec_id}
```

### ORD ID Pattern

```
sap.{product}:apiResource:{BusinessObject}:v{version}

Examples:
- sap.s4com:apiResource:Supplier:v1
- sap.s4com:apiResource:PurchaseOrder:v1
- sap.s4com:apiResource:SupplierInvoice:v1
```

---

## Appendix: Complete Supplier Schema Fields

### supplier.Supplier (Main Entity)

**120+ Fields** organized by category:

**Core Identity** (10):
Supplier, SupplierAccountGroup, SupplierName, SupplierFullName, BPSupplierName, BPSupplierFullName, Customer, AddressID, InternationalLocationNumber1-3

**Names & Labels** (10):
BusinessPartnerName1-4, OrganizationBPName1-2, FormOfAddress, AddressSearchTerm1-2

**Address** (15):
Country, Region, CityName, PostalCode, StreetName, BPAddrCityName, BPAddrStreetName, DistrictName, POBoxDeviatingCityName, TrainStationName

**Tax** (20):
VATRegistration, TaxJurisdiction, TaxNumber1-6, TaxNumberType, TaxNumberResponsible, ResponsibleType, VATLiability, TaxInvoiceRepresentativeName, FiscalAddress

**Status** (15):
AccountIsBlockedForPosting, PostingIsBlocked, PurchasingIsBlocked, PaymentIsBlockedForSupplier, DeletionIndicator, IsOneTimeAccount, IsNaturalPerson, IsBusinessPurposeCompleted, SupplierCentralDeletionIsBlock

**Contact** (8):
PhoneNumber1, PhoneNumber2, FaxNumber, SupplierLanguage, ContactInfo

**Business** (20):
Industry, IndustryType, SupplierCorporateGroup, AuthorizationGroup, SupplierProcurementBlock, SuplrQualityManagementSystem, SupplierProfession, BusinessType

**Dates** (5):
CreationDate, BirthDate, SuplrQltyInProcmtCertfnValidTo, BPPanValidFromDate, CreatedByUser

**UK-Specific** (8):
UK_ContractorBusinessType, UK_PartnerTradingName, UK_PartnerTaxReference, UK_VerificationStatus, UK_VerificationNumber, UK_CompanyRegistrationNumber, UK_VerifiedTaxStatus

**AU-Specific** (9):
AU_PayerIsPayingToCarryOnEnt, AU_IndividualIsUnder18, AU_PaymentIsExceeding75, AU_PaymentIsWhollyInputTaxed, etc.

**India** (3):
IN_GSTSupplierClassification, BusinessPartnerPanNumber, BPPanReferenceNumber

**Brazil** (2):
BR_TaxIsSplit, BRSpcfcTaxBasePercentageCode

**Logistics** (10):
SupplierStandardCarrierAccess, SupplierFwdAgentFreightGroup, SupplierTransportationChain, SupplierStagingTimeInDays, SupplierSchedulingProcedure, CollectiveNumberingIsRelevant

**System** (10):
DataMediumExchangeIndicator, DataExchangeInstructionKey, SortField, AlternativePayeeAccountNumber, ReferenceAccountGroup

**Data Controllers** (11):
DataControllerSet, DataController1-10

**Associations** (2):
_SupplierCompany, _SupplierPurchasingOrg

---

## Summary

### Key Findings

1. ✅ **BDC MCP Server provides CSN retrieval** via `csnSchema` tool
2. ✅ **All data products have CSN URLs** in ORD metadata
3. ✅ **Real-time schema access** - always current definitions
4. ✅ **Complete schema information** - all fields, types, annotations
5. ✅ **100+ data products available** including all P2P products

### Advantages Over Local Files

| Aspect | Local Files | BDC MCP API |
|--------|-------------|-------------|
| Currency | ⚠️ May be outdated | ✅ Always current |
| Completeness | ⚠️ Partial coverage | ✅ All 100+ products |
| Maintenance | ⚠️ Manual updates | ✅ Automatic |
| Availability | ✅ Offline | ⚠️ Requires network |
| Speed | ✅ Instant | ⚠️ API call overhead |

### Recommendation

**Hybrid Approach**:
- Keep local CSN files for offline/fast access
- Use BDC MCP for validation and updates
- Implement comparison tool
- Schedule periodic sync

---

**Document Version**: 1.0  
**Status**: Production-ready  
**Last Updated**: January 22, 2026, 11:55 AM  
**Next Steps**: Implement Flask API endpoints for CSN retrieval
