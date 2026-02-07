# P2P Dashboard Design Document

**Version**: 1.0  
**Date**: 2026-02-07  
**Status**: Design Phase

---

## Overview

A comprehensive Procure-to-Pay (P2P) Dashboard that provides real-time KPIs and operational insights for procurement and AP teams.

## Business Objectives

1. **Visibility**: Real-time view of P2P process health
2. **Decision Support**: Data-driven insights for procurement optimization
3. **Risk Management**: Early warning for potential issues
4. **Performance Tracking**: Monitor supplier and process performance

---

## KPI Categories & Metrics

### 1. Purchase Order Metrics 📦

**Critical KPIs**:
- **Total PO Value** (Current Period vs Previous)
- **PO Count** (Open, Completed, Cancelled)
- **Average PO Value**
- **PO Processing Time** (Creation to Approval)
- **Late POs** (Past expected delivery date)

**Data Sources**: `PurchaseOrder`, `PurchaseOrderItem`, `PurchaseOrderScheduleLine`

### 2. Supplier Performance 🤝

**Critical KPIs**:
- **Active Suppliers** (Count)
- **Top 10 Suppliers by Spend**
- **Supplier On-Time Delivery Rate** (%)
- **Supplier Quality Score** (Based on confirmations vs actuals)
- **Blocked Suppliers** (Count)

**Data Sources**: `Supplier`, `SupplierPurchasingOrganization`, `PurchaseOrder`

### 3. Invoice Processing 💰

**Critical KPIs**:
- **Total Invoice Value** (Current Period)
- **Pending Invoices** (Count & Value)
- **Average Processing Time** (Receipt to Payment)
- **Invoice Accuracy Rate** (% with no variances)
- **Overdue Invoices** (Count & Value)

**Data Sources**: `SupplierInvoice`, `SupplierInvoiceItem`

### 4. Financial Health 💵

**Critical KPIs**:
- **Cash Tied in POs** (Open PO value)
- **Spend by Category** (Material Group breakdown)
- **Payment Terms Distribution**
- **Discount Utilization Rate** (%)
- **Budget vs Actual Spend**

**Data Sources**: `PurchaseOrderItem`, `PaymentTerms`, `CompanyCode`

### 5. Service Entry Sheets 📋

**Critical KPIs**:
- **Pending Service Sheets** (Count)
- **Service Sheet Value** (Current Period)
- **Average Approval Time**
- **Rejected Service Sheets** (Count & %)

**Data Sources**: `ServiceEntrySheet`, `ServiceEntrySheetItem`

### 6. Operational Efficiency ⚡

**Critical KPIs**:
- **P2P Cycle Time** (PR creation to Payment)
- **Exception Rate** (% of POs/Invoices with issues)
- **Automation Rate** (% of automated processing)
- **Cost per Transaction**
- **Backlog Items** (Pending approvals/actions)

**Calculated from multiple tables**

---

## Dashboard Layout (SAP Fiori Design)

### Page Structure

```
┌─────────────────────────────────────────────────────────┐
│  P2P Dashboard                    [Refresh] [Export]    │
├─────────────────────────────────────────────────────────┤
│  Period: [Last 30 Days ▼]  Company: [All ▼]           │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐│
│  │  Total   │  │  Active  │  │ Pending  │  │  Overdue ││
│  │  PO      │  │ Suppliers│  │ Invoices │  │ Payments ││
│  │  $2.4M   │  │    156   │  │    42    │  │   $89K   ││
│  │  ↑ 12%   │  │  ↓ 2     │  │  ↑ 5     │  │  ↓ 15%   ││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘│
│                                                          │
│  ┌────────────────────────────┐  ┌────────────────────┐│
│  │  Spend by Category         │  │  Top 10 Suppliers  ││
│  │  [Pie Chart]               │  │  [Bar Chart]       ││
│  │                            │  │                    ││
│  └────────────────────────────┘  └────────────────────┘│
│                                                          │
│  ┌─────────────────────────────────────────────────────┐│
│  │  Purchase Orders Trend (Last 90 Days)               ││
│  │  [Line Chart - Value & Count]                       ││
│  └─────────────────────────────────────────────────────┘│
│                                                          │
│  ┌────────────────────────────┐  ┌────────────────────┐│
│  │  Invoice Processing Time   │  │  Payment Terms     ││
│  │  [Histogram]               │  │  Distribution      ││
│  │                            │  │  [Donut Chart]     ││
│  └────────────────────────────┘  └────────────────────┘│
│                                                          │
│  ┌─────────────────────────────────────────────────────┐│
│  │  Recent Purchase Orders                   [View All]││
│  │  ┌──────┬─────────┬──────────┬─────────┬──────────┐││
│  │  │ PO # │ Supplier│ Value    │ Status  │ Due Date │││
│  │  ├──────┼─────────┼──────────┼─────────┼──────────┤││
│  │  │...   │...      │...       │...      │...       │││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### UI Components (SAP Fiori Controls)

- **Header**: `sap.m.Page` with `sap.m.Bar`
- **KPI Tiles**: `sap.m.NumericContent` in `sap.m.GenericTile`
- **Charts**: `sap.viz.ui5.controls.VizFrame` (or Chart.js for simplicity)
- **Tables**: `sap.m.Table` with `sap.m.ColumnListItem`
- **Filters**: `sap.m.Select`, `sap.m.DateRangeSelection`

---

## Backend API Design

### Module Structure

```
modules/p2p_dashboard/
├── module.json                 # Module configuration
├── backend/
│   ├── __init__.py            # Blueprint registration
│   ├── api.py                 # Flask API endpoints
│   ├── kpi_service.py         # KPI calculation logic
│   └── aggregations.py        # SQL aggregation queries
├── frontend/
│   ├── dashboard.html         # Main UI (SAPUI5)
│   ├── dashboard.js           # Controller logic
│   └── dashboard.css          # Styling
├── tests/
│   ├── test_api.py           # API tests
│   └── test_kpi_service.py   # Service tests
└── README.md
```

### API Endpoints

```python
# GET /api/p2p-dashboard/kpis
# Returns all KPIs for specified period
{
  "period": "last_30_days",
  "companyCode": "1000",
  "kpis": {
    "purchaseOrders": {...},
    "suppliers": {...},
    "invoices": {...},
    "financial": {...},
    "serviceSheets": {...},
    "operational": {...}
  },
  "trends": {...},
  "timestamp": "2026-02-07T15:30:00Z"
}

# GET /api/p2p-dashboard/kpis/purchase-orders
# Returns detailed PO metrics

# GET /api/p2p-dashboard/kpis/suppliers
# Returns supplier performance metrics

# GET /api/p2p-dashboard/kpis/invoices
# Returns invoice processing metrics

# GET /api/p2p-dashboard/trends/{metric}?period=90d
# Returns time-series data for trending

# GET /api/p2p-dashboard/drill-down/{kpi}
# Returns detailed breakdown for a specific KPI
```

### KPI Calculation Examples

```python
# Example: Total PO Value (Current Period)
SELECT 
    SUM(NetAmount) as total_value,
    COUNT(DISTINCT PurchaseOrder) as po_count,
    AVG(NetAmount) as avg_value
FROM PurchaseOrderItem
WHERE CreationDate >= :period_start
  AND CreationDate <= :period_end
  AND CompanyCode = :company_code

# Example: Supplier On-Time Delivery Rate
SELECT 
    s.Supplier,
    s.SupplierName,
    COUNT(CASE WHEN pol.DelivDateCategory = 'ON_TIME' THEN 1 END) * 100.0 / COUNT(*) as on_time_rate
FROM Supplier s
JOIN PurchaseOrder po ON po.Supplier = s.Supplier
JOIN PurchaseOrderScheduleLine pol ON pol.PurchaseOrder = po.PurchaseOrder
WHERE pol.ScheduleLineDeliveryDate >= :period_start
GROUP BY s.Supplier, s.SupplierName
ORDER BY on_time_rate DESC
LIMIT 10

# Example: Invoice Accuracy Rate
SELECT 
    COUNT(CASE WHEN variance_flags = 0 THEN 1 END) * 100.0 / COUNT(*) as accuracy_rate
FROM SupplierInvoiceItem
WHERE PostingDate >= :period_start
  AND PostingDate <= :period_end
```

---

## Implementation Phases

### Phase 1: Backend Foundation (2-3 days)
- [x] Design document (this file)
- [ ] Create module structure
- [ ] Implement `kpi_service.py` (core calculations)
- [ ] Create API endpoints in `api.py`
- [ ] Write unit tests (Gu Wu standards)
- [ ] Validate with Feng Shui quality gate

### Phase 2: Basic Frontend (1-2 days)
- [ ] Create dashboard HTML skeleton
- [ ] Implement KPI tiles (4 main metrics)
- [ ] Add refresh functionality
- [ ] Basic responsive layout

### Phase 3: Charts & Visualizations (2-3 days)
- [ ] Integrate Chart.js or SAP VizFrame
- [ ] Implement 4 key charts:
  * Spend by Category (Pie)
  * Top Suppliers (Bar)
  * PO Trend (Line)
  * Payment Terms (Donut)
- [ ] Add chart interactions (drill-down)

### Phase 4: Advanced Features (2-3 days)
- [ ] Period selector (Last 7/30/90 days, Custom)
- [ ] Company code filter
- [ ] Export to Excel/PDF
- [ ] Real-time auto-refresh
- [ ] Drill-down detail views

### Phase 5: Testing & Polish (1-2 days)
- [ ] Integration tests
- [ ] Performance optimization
- [ ] SAP Fiori compliance check
- [ ] User acceptance testing
- [ ] Documentation

**Total Estimate**: 8-13 days (1-2 weeks)

---

## Data Refresh Strategy

### Real-Time Updates
- **WebSocket** for live KPI updates (optional)
- **Polling** every 30 seconds for critical metrics
- **Manual Refresh** button for on-demand updates

### Caching Strategy
- Cache aggregated KPIs for 5 minutes
- Invalidate cache on data changes
- Use Redis for distributed caching (future)

---

## Security Considerations

### Authentication (Deferred)
- Currently: Open access (until login_manager complete)
- Future: Role-based access (Procurement, Finance, Manager)

### Data Privacy
- No PII in dashboard (only aggregated metrics)
- Company code filtering enforced
- Audit logging for sensitive queries

### SQL Injection Prevention ⚠️
- **CRITICAL**: Use parameterized queries ONLY
- No string concatenation for SQL
- Validate all input parameters

---

## Success Metrics

### User Adoption
- Daily active users > 50% of procurement team
- Average session time > 5 minutes
- Refresh rate < 2 seconds

### Business Impact
- Reduced PO cycle time by 15%
- Improved invoice accuracy to 95%
- 90% of exceptions identified within 24 hours

---

## Next Steps

1. **User Approval**: Review this design, confirm KPIs
2. **Implementation**: Start Phase 1 (Backend Foundation)
3. **Incremental Delivery**: Demo after each phase
4. **Feedback Loop**: Iterate based on user feedback

---

## Related Documents

- [[SAP Fiori Design Standards]] - UI guidelines
- [[Modular Architecture]] - Module structure
- [[Gu Wu Testing Framework]] - Testing standards
- [[API-First Development]] - Development approach

---

**Questions for User**:
1. Are these KPIs aligned with your business needs?
2. Any additional metrics you'd like to see?
3. Preferred chart library: Chart.js (simple) or SAP VizFrame (complex)?
4. Should we include drill-down to transaction details?
5. Export format: Excel, PDF, or both?