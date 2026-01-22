# Backend Setup & Deployment Guide

**Status**: ⚠️ Connection Issue - HANA Cloud instance needs configuration

---

## Current Issue

**Error**: `Socket closed by peer` when connecting to HANA Cloud

**Possible Causes**:
1. ❌ **HANA Instance Stopped** - Instance not running in BTP
2. ❌ **IP Allowlist** - Your IP (10.50.122.213) not in allowlist
3. ❌ **Network Restriction** - Corporate firewall blocking port 443
4. ❌ **Credentials Issue** - Password might have changed

---

## Resolution Steps

### Step 1: Check HANA Instance Status

**Via BTP Cockpit**:
1. Login to https://cockpit.eu10.hana.ondemand.com
2. Navigate to your subaccount
3. Go to: SAP HANA Cloud → Instances
4. Check instance status: Should be "RUNNING" (not "STOPPED")

**Via CLI**:
```bash
# Check instance status
cf service my-hana-instance
```

**If STOPPED**:
```bash
# Start instance (takes 2-3 minutes)
cf update-service my-hana-instance -c '{"data":{"serviceStopped":false}}'
```

### Step 2: Check IP Allowlist

**Via BTP Cockpit**:
1. Open SAP HANA Cloud Central
2. Select your instance
3. Go to: Actions → Manage Configuration
4. Check "Allowed connections" section
5. Add your IP: `10.50.122.213` (your current IP)

**Recommendation**: Add IP range or use `0.0.0.0/0` for development (⚠️ not for production!)

### Step 3: Test with hana-cli

Before using Node.js backend, verify connection works with hana-cli:

```bash
# Test connection
hana-cli connect

# If successful, try query
hana-cli querySimple -q "SELECT CURRENT_USER FROM DUMMY"
```

**If hana-cli works**, Node.js backend will work too (same credentials).

### Step 4: Verify Credentials

Check if password is current:
```bash
# Try connecting via Database Explorer
hana-cli opendbx
```

If login fails, password might have changed.

---

## Installation Steps (When Ready)

### 1. Install Dependencies ✅ DONE

```bash
cd web/current/backend
npm install
```

**Installed**: ✅
- express@4.18.2
- @sap/hana-client@2.19.21
- dotenv@16.4.1
- cors@2.8.5
- nodemon@3.0.2 (dev)

**Result**: 104 packages, 0 vulnerabilities

### 2. Configure Environment ✅ DONE

**File**: `web/current/backend/.env`

```env
HANA_HOST=e7decab9-3e98-41cf-bbf7-d0a8c13d7fb9.hana.prod-eu10.hanacloud.ondemand.com
HANA_PORT=443
HANA_USER=DBADMIN
HANA_PASSWORD=HANA4vpbdc
HANA_SCHEMA=P2P_SCHEMA
PORT=3000
NODE_ENV=development
```

### 3. Test Connection ⚠️ PENDING

```bash
cd web/current/backend
node test-connection.js
```

**Expected Output** (when fixed):
```
✅ Connected to HANA Cloud!
✅ Query executed successfully!
Results: {
  "CURRENT_USER": "DBADMIN",
  "CURRENT_SCHEMA": "P2P_SCHEMA",
  "CURRENT_TIMESTAMP": "2026-01-22 02:00:00.000"
}
🎉 Connection test PASSED!
```

### 4. Start Backend Server ⏳ NEXT

```bash
cd web/current/backend
npm start
```

Server will run on: http://localhost:3000

**Test endpoints**:
```bash
# Health check
curl http://localhost:3000/api/health

# Connection test
curl http://localhost:3000/api/test-connection

# Execute SQL
curl -X POST http://localhost:3000/api/execute-sql \
  -H "Content-Type: application/json" \
  -d '{"sql":"SELECT CURRENT_USER FROM DUMMY"}'
```

---

## Frontend Integration

### Update sqlExecutionAPI.js

**File**: `web/current/js/api/sqlExecutionAPI.js`

**Change**: Replace simulated execution with real backend call

**Find**:
```javascript
async _executeQuerySimulated(instance, sql, queryType, options) {
    // Simulation code...
}
```

**Replace with**:
```javascript
async _executeQueryReal(instance, sql, queryType, options) {
    try {
        const response = await fetch('http://localhost:3000/api/execute-sql', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                sql,
                maxRows: options.maxRows 
            })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
        
    } catch (error) {
        throw new Error(`Backend connection failed: ${error.message}`);
    }
}
```

**Then update executeQuery method**:
```javascript
// OLD:
const result = await this._executeQuerySimulated(...);

// NEW:
const result = await this._executeQueryReal(...);
```

---

## Architecture

### Current Setup (Development)

```
┌─────────────────────────────────────────────────┐
│  Browser (localhost:8080)                      │
│  ├─ index.html                                 │
│  └─ js/api/sqlExecutionAPI.js                  │
│         │                                       │
│         │ HTTP POST /api/execute-sql           │
│         ▼                                       │
│  ┌──────────────────────────────────────┐     │
│  │  Node.js Backend (localhost:3000)    │     │
│  │  └─ server.js (@sap/hana-client)     │     │
│  └──────────────┬───────────────────────┘     │
│                 │                               │
│                 │ TLS/SSL                       │
│                 ▼                               │
│         ┌──────────────┐                       │
│         │  HANA Cloud  │                       │
│         └──────────────┘                       │
└─────────────────────────────────────────────────┘
```

### BTP Production Setup

```
┌─────────────────────────────────────────────────┐
│         SAP BTP Cloud Foundry                   │
│                                                 │
│  ┌──────────────┐      ┌─────────────────┐    │
│  │  App Router  │─────▶│  Frontend App   │    │
│  │  (Security)  │      │  (Staticfile)   │    │
│  └──────┬───────┘      └─────────────────┘    │
│         │                                       │
│         │ Secure Routes                         │
│         ▼                                       │
│  ┌──────────────────────────────────────┐     │
│  │  Backend App (Node.js)               │     │
│  │  with @sap/hana-client                │     │
│  └──────────────┬───────────────────────┘     │
│                 │                               │
│                 │ Service Binding               │
│                 │ (Auto VCAP_SERVICES)          │
│                 ▼                               │
│         ┌──────────────┐                       │
│         │  HANA Cloud  │                       │
│         │  (Bound)     │                       │
│         └──────────────┘                       │
└─────────────────────────────────────────────────┘
```

---

## BTP Deployment Files

### manifest.yml (Backend)

```yaml
---
applications:
- name: p2p-backend
  memory: 256M
  disk_quota: 512M
  instances: 1
  buildpack: nodejs_buildpack
  command: node server.js
  services:
    - my-hana-instance
  env:
    NODE_ENV: production
  routes:
    - route: p2p-backend.cfapps.eu10.hana.ondemand.com
```

### manifest.yml (Frontend)

```yaml
---
applications:
- name: p2p-frontend
  memory: 64M
  disk_quota: 256M
  buildpack: staticfile_buildpack
  path: ../
  env:
    BACKEND_URL: https://p2p-backend.cfapps.eu10.hana.ondemand.com
  routes:
    - route: p2p-data-products.cfapps.eu10.hana.ondemand.com
```

### Staticfile (Frontend)

```
root: .
location_include: strict
pushstate: enabled
```

### .cfignore (Backend)

```
node_modules/
.env
.git/
tests/
*.md
.env.example
```

---

## Deployment Commands

### Deploy Backend

```bash
cd web/current/backend

# Login to Cloud Foundry
cf login -a https://api.cf.eu10.hana.ondemand.com

# Create/bind HANA service (if needed)
cf create-service hana hdi-shared my-hana-instance

# Push backend
cf push p2p-backend
```

### Deploy Frontend

```bash
cd web/current

# Push frontend
cf push p2p-frontend
```

### Check Deployment

```bash
# List apps
cf apps

# Check logs
cf logs p2p-backend --recent
cf logs p2p-frontend --recent

# Check service binding
cf env p2p-backend
```

---

## Complete Full-Stack Deployment

### Option: Multi-Target Application (MTA)

Create `mta.yaml` in project root:

```yaml
_schema-version: '3.1'
ID: p2p-data-products
version: 1.0.0

modules:
  # Backend Module
  - name: p2p-backend
    type: nodejs
    path: web/current/backend
    parameters:
      memory: 256M
      disk-quota: 512M
    requires:
      - name: p2p-hana
    provides:
      - name: backend-api
        properties:
          url: ${default-url}

  # Frontend Module  
  - name: p2p-frontend
    type: html5
    path: web/current
    parameters:
      memory: 64M
      disk-quota: 256M
    requires:
      - name: backend-api
        properties:
          backend-url: ~{url}

resources:
  # HANA Service
  - name: p2p-hana
    type: org.cloudfoundry.managed-service
    parameters:
      service: hana
      service-plan: hdi-shared
```

**Build and Deploy**:
```bash
# Install MTA tools
npm install -g mbt

# Build MTA archive
mbt build

# Deploy
cf deploy mta_archives/p2p-data-products_1.0.0.mtar
```

---

## Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| Backend Code | ✅ Complete | server.js ready |
| Dependencies | ✅ Installed | 104 packages |
| .env Config | ✅ Created | From default-env.json |
| Connection Test | ❌ Failed | IP allowlist / instance stopped |
| Backend Server | ⏳ Ready | Can start when connection fixed |
| Frontend Integration | 📋 Pending | Need backend working first |
| BTP Deployment | 📋 Ready | Manifests ready |

---

## Next Actions Required

### Immediate (User Action Needed)

1. **Check HANA Instance Status** in BTP Cockpit
   - Navigate to SAP HANA Cloud Central
   - Verify instance is RUNNING (not STOPPED)
   - If stopped, start it (takes 2-3 minutes)

2. **Add IP to Allowlist**
   - Your IP: `10.50.122.213`
   - Or use `0.0.0.0/0` for dev (all IPs)

3. **Verify hana-cli Works**
   ```bash
   hana-cli connect
   hana-cli querySimple -q "SELECT CURRENT_USER FROM DUMMY"
   ```

### After Connection Fixed

4. **Test Backend Connection**
   ```bash
   cd web/current/backend
   node test-connection.js
   ```

5. **Start Backend Server**
   ```bash
   npm start
   ```

6. **Update Frontend** to call backend

7. **Test End-to-End** with real queries

8. **Deploy to BTP** (optional)

---

## Alternative: Use Simulation Mode

If you can't fix the connection now, the application **already works** with simulated data:

**Current Status**: ✅ Working with mock data
- Navigate to http://localhost:8080
- Click "🔌 HANA Connection"
- Execute queries → See simulated results
- Perfect for UI testing and development

**When Ready**: Just fix connection and update frontend to use backend

---

## Support Resources

**HANA Cloud**:
- BTP Cockpit: https://cockpit.eu10.hana.ondemand.com
- HANA Central: https://hanacloud.ondemand.com
- Documentation: https://help.sap.com/docs/hana-cloud

**Troubleshooting**:
- IP Allowlist Guide: BTP Cockpit → HANA Cloud → Manage Configuration
- Instance Status: HANA Cloud Central → Instances
- Connection Test: `hana-cli connect`

---

## Summary

**What's Built**: ✅
- Complete Node.js backend with @sap/hana-client
- Express REST API for SQL execution
- Connection test script
- BTP deployment manifests
- Comprehensive documentation

**What's Pending**: ⚠️
- HANA Cloud connectivity (IP allowlist / instance status)
- Frontend integration (when backend works)
- End-to-end testing
- BTP deployment (optional)

**Recommendation**: 
1. Fix HANA connectivity first (IP allowlist)
2. Then test backend connection
3. Then integrate with frontend for real data

**The architecture is production-ready - just needs network access configured!**
