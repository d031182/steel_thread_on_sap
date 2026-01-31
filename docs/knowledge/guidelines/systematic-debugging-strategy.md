# Systematic Debugging Strategy

**Purpose**: Eliminate trial-and-error debugging by following industry-standard practices for root cause analysis

**Last Updated**: 2026-01-31

---

## ⚠️ THE PROBLEM WE'RE SOLVING

**Bad Pattern** (What happened today):
1. User reports: "Data mode doesn't work"
2. AI tries random fixes (backend limit, frontend error handling)
3. 30+ minutes wasted on symptoms, not root cause
4. Real bug: Duplicate node IDs in vis.js

**Good Pattern** (What should happen):
1. Reproduce issue with minimal test case (5 min)
2. Capture full error stack trace (1 min)
3. Read error message carefully (2 min)
4. Locate exact line causing error (2 min)
5. Fix root cause (5 min)
**Total**: 15 minutes vs 60 minutes

---

## 🎯 DEBUGGING METHODOLOGY

### Phase 1: REPRODUCE (5 minutes)

**Goal**: Get a reliable, minimal reproduction

```bash
# Step 1: Create isolated test case
python test_api_direct.py  # Test API only (no browser)

# Step 2: Verify error occurs consistently
python -c "
import requests
response = requests.get('http://localhost:5000/api/knowledge-graph/?mode=data&max_records=5')
print(response.status_code)
print(response.json())
"

# Step 3: Check API response structure
# - Does API return 200 OK?
# - Does response have expected keys?
# - Are there duplicate IDs in response?
```

**Industry Standard**: Always test at lowest layer first (API → UI)

---

### Phase 2: CAPTURE ERROR (2 minutes)

**Goal**: Get COMPLETE error information

```bash
# Step 1: Enable detailed logging
# Already configured in app/app.py - check logs/app.log

# Step 2: Capture browser console (if UI issue)
# F12 → Console → Copy full error stack

# Step 3: Capture network traffic
# F12 → Network → Copy API response
```

**What to capture**:
- ✅ Full error message
- ✅ Stack trace (ALL lines, not just first)
- ✅ Line numbers
- ✅ Variable values at error point
- ✅ API request/response

**Industry Standard**: Logs beat guessing

---

### Phase 3: READ ERROR CAREFULLY (2 minutes)

**Goal**: Understand what ACTUALLY failed

```
Example Error:
"Error: Cannot add item: item with id record-JournalEntry-A already exists
at renderGraph (knowledgeGraphPage.js:438:16)"
```

**Analysis Checklist**:
- ✅ What is the error type? (`Error`, `TypeError`, `ReferenceError`)
- ✅ What operation failed? ("Cannot add item")
- ✅ What was the constraint? ("id already exists")
- ✅ What was the value? ("record-JournalEntry-A")
- ✅ Where did it fail? (line 438 in renderGraph)

**Key Insight**: Error message tells you EXACTLY what's wrong!

---

### Phase 4: LOCATE ROOT CAUSE (3 minutes)

**Goal**: Find WHERE the bad data is created

```bash
# Step 1: Find error location
# Line 438: new vis.DataSet(graphData.nodes)
# → vis.js is rejecting duplicate node IDs

# Step 2: Trace backwards - where do nodes come from?
# graphData.nodes ← API response ← backend

# Step 3: Check API response for duplicates
python -c "
import requests
r = requests.get('http://localhost:5000/api/knowledge-graph/?mode=data&max_records=5')
data = r.json()
node_ids = [n['id'] for n in data.get('nodes', [])]
duplicates = [x for x in set(node_ids) if node_ids.count(x) > 1]
print(f'Duplicate IDs: {duplicates}')
"

# Step 4: Find ID generation code
# grep -r "node_id = " modules/knowledge_graph/
```

**Industry Standard**: Work backwards from error to source

---

### Phase 5: FIX ROOT CAUSE (5 minutes)

**Goal**: Fix the actual problem, not symptoms

```python
# ❌ WRONG: Fix symptoms
# - Add try/catch to hide error
# - Filter duplicates in frontend
# - Limit data to avoid duplicates

# ✅ RIGHT: Fix root cause
# - Make node IDs actually unique
node_id = f"record-{schema}-{table_name}-{pk_value}"  # Add schema!
```

**Validation**:
```bash
# Re-run test
python test_api_direct.py

# Verify no duplicates
python -c "
import requests
r = requests.get('http://localhost:5000/api/knowledge-graph/?mode=data&max_records=20')
data = r.json()
node_ids = [n['id'] for n in data.get('nodes', [])]
assert len(node_ids) == len(set(node_ids)), 'Still have duplicates!'
print('✓ No duplicates!')
"
```

---

## 🚀 AUTOMATED DEBUGGING TOOLS

### Tool 1: API Test Script (test_api_direct.py)

**Purpose**: Test backend without browser complexity

```python
#!/usr/bin/env python3
"""
Direct API Testing - No Browser Required

Usage: python test_api_direct.py
"""
import requests
import sys

def test_knowledge_graph_data_mode():
    """Test data mode for duplicate node IDs"""
    url = 'http://localhost:5000/api/knowledge-graph/'
    params = {'mode': 'data', 'source': 'sqlite', 'max_records': 20}
    
    print(f"Testing: {url}")
    print(f"Params: {params}")
    
    # Make request
    r = requests.get(url, params=params)
    
    # Check status
    if r.status_code != 200:
        print(f"❌ FAIL: HTTP {r.status_code}")
        print(r.text)
        sys.exit(1)
    
    # Parse response
    data = r.json()
    
    # Check structure
    if not data.get('success'):
        print(f"❌ FAIL: API returned success=false")
        print(f"Error: {data.get('error')}")
        sys.exit(1)
    
    # Check for duplicate node IDs
    nodes = data.get('nodes', [])
    node_ids = [n['id'] for n in nodes]
    duplicates = [x for x in set(node_ids) if node_ids.count(x) > 1]
    
    if duplicates:
        print(f"❌ FAIL: Found {len(duplicates)} duplicate node IDs:")
        for dup_id in duplicates:
            count = node_ids.count(dup_id)
            print(f"  - {dup_id} appears {count} times")
        sys.exit(1)
    
    # Success
    print(f"✓ PASS: {len(nodes)} unique nodes, {len(data.get('edges', []))} edges")
    print(f"✓ No duplicate node IDs")
    return 0

if __name__ == '__main__':
    sys.exit(test_knowledge_graph_data_mode())
```

**Usage**:
```bash
# Test after any change
python test_api_direct.py

# Output:
# ✓ PASS: 360 unique nodes, 0 edges
# ✓ No duplicate node IDs
```

---

### Tool 2: Data Validation Script

**Purpose**: Validate data quality before rendering

```python
# scripts/python/validate_graph_data.py
def validate_graph_data(nodes, edges):
    """
    Validate graph data structure
    
    Returns: (is_valid, errors)
    """
    errors = []
    
    # Check for duplicate node IDs
    node_ids = [n['id'] for n in nodes]
    duplicates = [x for x in set(node_ids) if node_ids.count(x) > 1]
    if duplicates:
        errors.append(f"Duplicate node IDs: {duplicates}")
    
    # Check all nodes have required fields
    for node in nodes:
        if 'id' not in node:
            errors.append(f"Node missing 'id': {node}")
        if 'label' not in node:
            errors.append(f"Node missing 'label': {node.get('id')}")
    
    # Check all edges reference valid nodes
    node_id_set = set(node_ids)
    for edge in edges:
        if edge.get('from') not in node_id_set:
            errors.append(f"Edge references invalid 'from' node: {edge.get('from')}")
        if edge.get('to') not in node_id_set:
            errors.append(f"Edge references invalid 'to' node: {edge.get('to')}")
    
    return (len(errors) == 0, errors)
```

---

## 📋 DEBUGGING CHECKLIST

**Before implementing ANY fix**:

- [ ] Can I reproduce the issue reliably?
- [ ] Have I captured the COMPLETE error message?
- [ ] Have I read the error message carefully?
- [ ] Do I understand what operation failed?
- [ ] Have I tested the API directly (no browser)?
- [ ] Have I checked API response for bad data?
- [ ] Have I traced back to where bad data is created?
- [ ] Am I fixing ROOT CAUSE (not symptoms)?
- [ ] Have I validated the fix with automated test?

**If ANY answer is NO**: STOP and complete that step first!

---

## 🎓 INDUSTRY BEST PRACTICES

### 1. Test-Driven Debugging (TDD)

```python
# FIRST: Write test that reproduces bug
def test_no_duplicate_node_ids():
    response = api.get_knowledge_graph(mode='data', max_records=20)
    node_ids = [n['id'] for n in response['nodes']]
    assert len(node_ids) == len(set(node_ids))  # Should FAIL initially

# SECOND: Fix code until test passes
# modules/knowledge_graph/backend/data_graph_service.py
node_id = f"record-{schema}-{table_name}-{pk_value}"  # Add schema

# THIRD: Re-run test
# ✓ PASS
```

### 2. Logging-Driven Development

```python
# Add strategic logging BEFORE debugging
logger.info(f"Creating node: {node_id}")
logger.debug(f"Node data: {node_data}")

# When bug occurs, logs show you exactly what happened:
# "Creating node: record-JournalEntry-A"
# "Creating node: record-JournalEntry-A"  ← Duplicate!
```

### 3. Fail Fast Principle

```python
# Add assertions to catch bugs early
assert len(node_ids) == len(set(node_ids)), f"Duplicate IDs: {duplicates}"

# Crash with clear error > Silent corruption
```

---

## 💡 KEY LEARNINGS

1. **Browser testing is LAST RESORT** (per .clinerules 6.1)
   - API tests: 5 seconds
   - Browser tests: 60+ seconds
   - Test APIs first, UI last

2. **Read error messages LITERALLY**
   - "Cannot add item: item with id X already exists" = duplicate ID
   - Error tells you WHAT and WHERE
   - Don't guess - read!

3. **Work backwards from error**
   - Error location → Data source → Root cause
   - Trace data flow in reverse

4. **Fix root cause, not symptoms**
   - Symptom: Vis.js crashes
   - Root cause: Backend generates duplicate IDs
   - Fix: Make IDs unique

5. **Automate validation**
   - Write test once
   - Run after every change
   - Catch regressions immediately

---

## 📚 REFERENCES

- [[Testing Standards]] - Existing test guidelines
- [[Module Error Handling Pattern]] - Consistent error patterns
- [[Automated UI Testing]] - When to use UI tests
- .clinerules Section 6.1 - Browser Testing Last Resort

---

**Summary**: Follow this 5-phase methodology (Reproduce → Capture → Read → Locate → Fix) instead of trial-and-error. Total time: ~15 minutes vs 60+ minutes.