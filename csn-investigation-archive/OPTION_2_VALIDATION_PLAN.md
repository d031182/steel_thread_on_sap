# Option 2 Validation Plan - Discovery API from BTP

**Purpose**: Test if Discovery API is accessible from BTP Cloud Foundry  
**Date**: 2026-01-23  
**Estimated Time**: 30-60 minutes

---

## What We're Validating

**Question**: Can a BTP Cloud Foundry app access Discovery API URLs?

**Discovery API Example**:
```
https://eu10.discovery.projects.api.ondemand.com/dataProduct/sap.s4.beh.purchaseorder.v1.PurchaseOrder.v1/schema
```

---

## Validation Approach: Minimal Test Deployment

### Step 1: Create Minimal Test App (10 minutes)

Create a tiny Flask app that just tests Discovery API:

```python
# test_discovery_api.py
from flask import Flask, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Discovery API Test - Visit /test to run"

@app.route('/test')
def test_discovery():
    """Test if Discovery API is accessible from BTP"""
    
    test_url = "https://eu10.discovery.projects.api.ondemand.com/dataProduct/sap.s4.beh.purchaseorder.v1.PurchaseOrder.v1/schema"
    
    result = {
        'test_url': test_url,
        'test_time': str(datetime.now())
    }
    
    try:
        # Test 1: Basic GET request
        response = requests.get(test_url, timeout=10)
        result['status_code'] = response.status_code
        result['success'] = response.status_code == 200
        result['headers'] = dict(response.headers)
        
        if response.status_code == 200:
            result['data_preview'] = response.text[:500]
            result['conclusion'] = "✅ Discovery API accessible from BTP!"
        elif response.status_code == 401:
            result['conclusion'] = "⚠️ API accessible but needs authentication"
        elif response.status_code == 403:
            result['conclusion'] = "❌ API accessible but forbidden (needs authorization)"
        else:
            result['conclusion'] = f"❓ Unexpected status: {response.status_code}"
            
    except requests.exceptions.Timeout:
        result['success'] = False
        result['error'] = "Timeout - API took too long to respond"
        result['conclusion'] = "❌ API timeout - might be blocked or slow"
        
    except requests.exceptions.ConnectionError as e:
        result['success'] = False
        result['error'] = str(e)
        result['conclusion'] = "❌ Connection failed - API not accessible from BTP"
        
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
        result['conclusion'] = f"❌ Error: {type(e).__name__}"
    
    return jsonify(result)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

### Step 2: Create manifest.yml (5 minutes)

```yaml
# manifest.yml
applications:
- name: discovery-api-test
  memory: 128M
  instances: 1
  buildpack: python_buildpack
  command: python test_discovery_api.py
```

### Step 3: Create requirements.txt (1 minute)

```
Flask==2.3.0
requests==2.31.0
```

### Step 4: Deploy to BTP (10 minutes)

```bash
# Login to Cloud Foundry
cf login -a https://api.cf.eu10.hana.ondemand.com

# Deploy test app
cf push

# Get app URL
cf apps
```

### Step 5: Test the Endpoint (5 minutes)

```bash
# Visit the test endpoint
curl https://discovery-api-test.cfapps.eu10.hana.ondemand.com/test
```

---

## Possible Outcomes

### Outcome A: ✅ Success (Status 200)
**Meaning**: Discovery API works from BTP without auth!

**Next Steps**:
1. Option 2 is viable!
2. Implement full CSN endpoint using Discovery API
3. Keep Option 1 as backup

**Implementation**: Already written in `backend/app.py`, just deploy

---

### Outcome B: ⚠️ Auth Required (Status 401/403)
**Meaning**: API accessible but needs authentication

**Next Steps**:
1. Research authentication method
2. Check SAP documentation
3. Might need API keys or OAuth
4. If auth is complex, prefer Option 1

**Decision**: Depends on auth complexity

---

### Outcome C: ❌ Not Accessible (Connection Error)
**Meaning**: BTP network also blocks Discovery API

**Next Steps**:
1. Option 2 not viable
2. Proceed with Option 1 (HANA SQL)
3. No external API dependency needed

**Conclusion**: Option 1 is the only solution

---

### Outcome D: ❌ Timeout
**Meaning**: API slow or unreliable from BTP

**Next Steps**:
1. Not suitable for production
2. Prefer Option 1 for reliability
3. Local HANA query will be faster

**Conclusion**: Option 1 is better

---

## Alternative: Quick Local Test (If Possible)

**Can try**: Using a VPN or proxy to test Discovery API

```bash
# Test with curl (might fail locally)
curl -v "https://eu10.discovery.projects.api.ondemand.com/dataProduct/sap.s4.beh.purchaseorder.v1.PurchaseOrder.v1/schema"
```

**Expected**: Connection refused or timeout (already tested, failed)

---

## Recommendation for Validation

### Fast Path (30 minutes):
1. Create minimal test app (above code)
2. Deploy to BTP
3. Test `/test` endpoint
4. Make decision based on result

### Decision Tree:
```
Deploy test app to BTP
    │
    ├─ Success (200) ─────────► Option 2 viable, implement it
    │
    ├─ Auth needed (401/403) ──► Research auth, decide if worth it
    │
    └─ Failed/Timeout ─────────► Option 1 (HANA SQL) is the solution
```

---

## My Recommendation

**Given what we know**:
- HANA table exists with CSN data ✅
- Discovery API blocked locally ❌
- Unknown if BTP has access ❓

**I suggest**:
1. **Start with Option 1** (HANA SQL) - we know it works, just needs privilege
2. **Test Option 2 later** if curious - but don't block on it
3. **Rationale**: Why risk deployment test when solution exists?

**However, if you want certainty**:
- Deploy test app (30 min) to know for sure
- Then make informed decision

---

## What Do You Prefer?

**Option A**: Grant HANA privileges, implement Option 1 (HANA SQL) - 2 hours total

**Option B**: Deploy test app first, validate Option 2 - 30 min test + implementation

**Option C**: Implement both with fallback logic - Try Option 2, fall back to Option 1

Which validation approach makes most sense to you?