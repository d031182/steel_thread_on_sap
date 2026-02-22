# AI Assistant HANA Table Name Fix - Quick Summary

**Status**: ✅ Fixed (2026-02-16)  
**Impact**: High - Critical for HANA data source  
**Risk**: Low - Isolated change

---

## The Problem

❌ **Before**: "show number of invoices" → AI generates `SELECT COUNT(*) FROM Invoice_Transactions` → HANA error  
✅ **After**: "show number of invoices" → AI generates `SELECT COUNT(*) FROM P2P_DATAPRODUCT_sap_bdc_Invoice_Transactions_V1` → Success

---

## The Solution (3 Changes)

### 1. Added HANA Table Name Converter
```python
def _get_hana_table_name(self, product_name: str) -> str:
    return f"P2P_DATAPRODUCT_sap_bdc_{product_name}_V1"
```

### 2. Made Data Context Data Source Aware
```python
def _build_data_context(self, data_products: List[Dict], data_source: str = 'sqlite'):
    if data_source == 'hana':
        table_name = self._get_hana_table_name(name)
    else:
        table_name = name
```

### 3. Updated Chat Method
```python
async def chat(self, message: str, conversation_id: str, context: ConversationContext):
    data_source = context.data_source  # ← Extract from context
    data_context = self._build_data_context(data_products, data_source)  # ← Pass it in
```

---

## Files Changed

1. **modules/ai_assistant/backend/services/agent_service.py** - Core fix
2. **test_ai_assistant_invoice_count_hana.py** - Unit tests
3. **test_ai_assistant_hana_e2e.py** - E2E test
4. **docs/knowledge/ai-assistant-hana-table-name-fix.md** - Full documentation

---

## Test Results

✅ **test_hana_table_name_conversion**: Table name mapping works  
✅ **test_data_context_with_hana**: HANA context includes correct table names  
✅ **test_invoice_count_query_with_hana**: End-to-end scenario passes  
✅ **API contract tests**: All passing

---

## Verification Steps

1. Start server: `python server.py`
2. Open UI: http://localhost:5000
3. Switch to "HANA Cloud" data source
4. Ask: "show number of invoices"
5. ✓ Should return correct count with HANA table name in SQL

---

## Key Insight

**SAP HANA Naming Convention**: `<NAMESPACE>_<CATEGORY>_<PROVIDER>_<PRODUCT>_<VERSION>`

Example: `P2P_DATAPRODUCT_sap_bdc_Invoice_Transactions_V1`

The AI's system prompt now includes this pattern, enabling it to generate correct SQL for HANA.

---

## Related Docs

- [[AI Assistant HANA Table Name Fix]] - Full documentation
- [[AI Assistant HANA Data Source Issue]] - Original investigation
- [[AI Assistant SQL Service HANA Issue]] - SQL debugging

---

**TL;DR**: AI Assistant now correctly uses HANA table names (`P2P_DATAPRODUCT_sap_bdc_*_V1`) when HANA data source is active, fixing invoice count queries and all other HANA operations.