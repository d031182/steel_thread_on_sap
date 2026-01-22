# SAP BTP CLI with HANA Cloud Administration Guide

**Using btp CLI to Manage SAP HANA Cloud Instances**

**Date**: January 21, 2026  
**Source**: https://help.sap.com/docs/hana-cloud/sap-hana-cloud-administration-guide

---

## Overview

The **SAP BTP Command Line Interface (btp CLI)** enables command-line management of SAP HANA Cloud instances in **non-Cloud Foundry environments**. It provides commands for creating, starting, stopping, and managing HANA Cloud instances.

---

## Important: btp CLI vs hana-cli vs CF CLI

### Three Different CLI Tools

| CLI Tool | Purpose | Environment | Installation |
|----------|---------|-------------|--------------|
| **btp CLI** | BTP account & HANA Cloud instance management | Non-CF (Kyma, etc.) | SAP Development Tools |
| **hana-cli** | Database development, HDI containers, schema management | CF + HANA Cloud | npm install |
| **CF CLI** | Cloud Foundry operations, HANA Cloud in CF | Cloud Foundry | GitHub download |

### Which CLI to Use?

**Use btp CLI when:**
- Managing HANA Cloud instances (create, start, stop, delete)
- Working in non-Cloud Foundry environments
- Managing BTP subaccounts, entitlements, services

**Use hana-cli when:**
- Developing with HANA database (tables, views, procedures)
- Managing HDI containers
- Using CDS/CAP framework
- Browser-based database exploration

**Use CF CLI when:**
- HANA Cloud instance is in Cloud Foundry environment
- Managing CF apps, services, routes
- Deploying MTA applications

### Key Limitation

⚠️ **CRITICAL**: SAP HANA Cloud instances provisioned in **Cloud Foundry cannot be managed by btp CLI** - you must use CF CLI instead!

---

## Installation

### Windows (PowerShell)

**Option 1: Automated Script**
```powershell
# Run as Administrator
Invoke-RestMethod 'https://cli.btp.cloud.sap/btpcli-install.ps1' | Invoke-Expression
```

**Option 2: Manual Download**
1. Download from: https://tools.hana.ondemand.com/ (Cloud section)
2. Extract tar.gz file
3. Copy `btp.exe` to a directory in PATH
4. Verify: `btp --version`

### Linux/Mac

**Automated Script:**
```bash
curl https://cli.btp.cloud.sap/btpcli-install.sh | bash
```

**Alternative Script:**
```bash
cd $HOME
curl --remote-name --location --url "https://raw.githubusercontent.com/SAP-samples/sap-tech-bytes/2021-09-01-btp-cli/getbtpcli"
chmod +x getbtpcli
./getbtpcli
```

### Verify Installation

```bash
btp --version
btp help
```

---

## Initial Setup

### 1. Login to BTP

```bash
# Interactive login
btp login

# Prompts for:
# - Server URL: https://cli.btp.cloud.sap/
# - Global account subdomain
# - User email
# - Password
```

**With Parameters:**
```bash
btp login --subdomain <your-subdomain> --user <your-email> --password <your-password>
```

### 2. Target Subaccount

```bash
# Set target subaccount for HANA Cloud operations
btp target --subaccount <subaccount-id>

# Or by name
btp target --subaccount-name "My Subaccount"
```

### 3. Verify Target

```bash
# Check current target
btp target

# List available subaccounts
btp list accounts/subaccount
```

---

## HANA Cloud Instance Management

### Prerequisites

- ✅ Subaccount created with HANA Cloud quota assigned
- ✅ btp CLI logged in and targeted to subaccount
- ✅ Instance **NOT in Cloud Foundry environment**

### Create HANA Cloud Instance

**Free Tier Instance:**
```bash
btp create services/instance \
  --offering-name hana-cloud \
  --plan-name hana-free \
  --name my-hana-db \
  --parameters '{
    "data": {
      "memory": 32,
      "systempassword": "Welcome100.",
      "whitelistIPs": ["0.0.0.0/0"]
    }
  }'
```

**Trial/Production Instance:**
```bash
btp create services/instance \
  --offering-name hana-cloud \
  --plan-name hana \
  --name my-hana-db \
  --parameters '{
    "data": {
      "memory": 32,
      "systempassword": "YourSecurePassword123!",
      "edition": "cloud",
      "whitelistIPs": ["192.168.1.0/24"]
    }
  }'
```

### List Instances

```bash
# List all service instances (including HANA Cloud)
btp list services/instance

# Get specific instance details
btp get services/instance --name my-hana-db

# Or by ID
btp get services/instance --id <instance-id>
```

### Start Instance

```bash
# Start stopped instance
btp update services/instance \
  --id <instance-id> \
  --parameters '{"data":{"serviceStopped":false}}'

# Or by name
btp update services/instance \
  --name my-hana-db \
  --parameters '{"data":{"serviceStopped":false}}'
```

### Stop Instance

```bash
# Stop running instance
btp update services/instance \
  --id <instance-id> \
  --parameters '{"data":{"serviceStopped":true}}'
```

### Update Instance Configuration

**Update Whitelisted IPs:**
```bash
btp update services/instance \
  --id <instance-id> \
  --parameters '{
    "data": {
      "whitelistIPs": ["1.2.3.4/32", "10.0.0.0/8"]
    }
  }'
```

**Scale Instance Memory:**
```bash
btp update services/instance \
  --id <instance-id> \
  --parameters '{
    "data": {
      "memory": 64
    }
  }'
```

### Delete Instance

```bash
# Delete instance (cannot be undone!)
btp delete services/instance --id <instance-id>

# With confirmation skip
btp delete services/instance --name my-hana-db --confirm
```

---

## Common Workflows

### Workflow 1: Create and Configure New Instance

```bash
# 1. Login
btp login

# 2. Target subaccount
btp target --subaccount <subaccount-id>

# 3. Create instance
btp create services/instance \
  --offering-name hana-cloud \
  --plan-name hana-free \
  --name dev-hana \
  --parameters '{"data":{"memory":32,"systempassword":"Welcome100."}}'

# 4. Wait for provisioning (5-10 minutes)
btp get services/instance --name dev-hana

# 5. Configure IP allowlist if needed
btp update services/instance \
  --name dev-hana \
  --parameters '{"data":{"whitelistIPs":["0.0.0.0/0"]}}'
```

### Workflow 2: Daily Start/Stop (Cost Saving)

```bash
# Morning: Start instance
btp update services/instance \
  --name my-hana-db \
  --parameters '{"data":{"serviceStopped":false}}'

# Evening: Stop instance
btp update services/instance \
  --name my-hana-db \
  --parameters '{"data":{"serviceStopped":true}}'
```

### Workflow 3: Instance Monitoring

```bash
# Get instance status
btp get services/instance --name my-hana-db

# List all instances
btp list services/instance

# Check instance details (JSON output)
btp get services/instance --name my-hana-db --format json
```

---

## Cloud Foundry vs Non-CF Environments

### If Your Instance is in Cloud Foundry

⚠️ **Cannot use btp CLI** - Use Cloud Foundry CLI instead:

```bash
# Install CF CLI v8 from GitHub
# https://github.com/cloudfoundry/cli#downloads

# Login to CF
cf login -a <api-endpoint>

# List HANA Cloud services
cf services

# Create HANA Cloud instance in CF
cf create-service hana-cloud hana my-hana-db -c '{"data":{"memory":32,"systempassword":"Welcome100."}}'

# Manage instance
cf update-service my-hana-db -c '{"data":{"serviceStopped":true}}'
```

### Determining Your Environment

**Check in BTP Cockpit:**
1. Navigate to your subaccount
2. Look for **"Cloud Foundry Environment"** or **"Kyma Environment"**
3. If you see CF Orgs/Spaces → Use CF CLI
4. If you see Kyma clusters → Use btp CLI

---

## Integration with hana-cli

**hana-cli** includes btp CLI integration commands!

### Check BTP CLI Installation

```bash
# From hana-cli
hana-cli version

# Look for:
# btp-cli: <version> or "btp CLI not installed"
```

### BTP Commands in hana-cli

```bash
# Set BTP target
hana-cli btp

# List subscriptions
hana-cli sub

# BTP information
hana-cli btpInfo

# List HANA Cloud instances (requires btp CLI)
hana-cli hc

# Start instance (requires btp CLI)
hana-cli hcStart -n my-hana-db

# Stop instance (requires btp CLI)
hana-cli hcStop -n my-hana-db
```

**Note**: These hana-cli commands are wrappers around btp CLI - you need btp CLI installed!

---

## Common Use Cases

### 1. Development Environment Management

```bash
# Create dev instance
btp create services/instance \
  --offering-name hana-cloud \
  --plan-name hana-free \
  --name dev-hana \
  --parameters '{"data":{"memory":32,"systempassword":"DevPass123!"}}'

# Start when needed
btp update services/instance --name dev-hana --parameters '{"data":{"serviceStopped":false}}'

# Stop to save costs
btp update services/instance --name dev-hana --parameters '{"data":{"serviceStopped":true}}'
```

### 2. IP Allowlist Management

```bash
# Allow all (development only!)
btp update services/instance --name my-hana \
  --parameters '{"data":{"whitelistIPs":["0.0.0.0/0"]}}'

# Restrict to specific IPs (production)
btp update services/instance --name my-hana \
  --parameters '{"data":{"whitelistIPs":["203.0.113.0/24","198.51.100.50/32"]}}'
```

### 3. Multi-Instance Management

```bash
# List all instances
btp list services/instance --format json > instances.json

# Loop through and stop all (bash)
for instance in $(btp list services/instance --format json | jq -r '.[].id'); do
  btp update services/instance --id $instance --parameters '{"data":{"serviceStopped":true}}'
done
```

---

## Parameters Reference

### Instance Creation Parameters

```json
{
  "data": {
    "memory": 32,                    // GB (32, 64, 128, 256, 512)
    "systempassword": "Password",    // DBADMIN password
    "edition": "cloud",              // "cloud" or "cloud-enterprise"
    "whitelistIPs": ["0.0.0.0/0"],  // IP allowlist
    "storage": 100,                  // GB (optional)
    "vcpu": 2,                       // vCPU count (optional)
    "requestedOperation": {          // Optional operations
      "action": "start"              // "start" or "stop"
    }
  }
}
```

### Update Parameters

```json
{
  "data": {
    "serviceStopped": true,          // true = stop, false = start
    "whitelistIPs": ["..."],        // Update IP allowlist
    "memory": 64,                    // Scale memory
    "storage": 200                   // Increase storage
  }
}
```

---

## Troubleshooting

### Issue: "btp CLI not installed"

**Check Installation:**
```bash
btp --version
```

**Install:**
- Windows: Run PowerShell script
- Linux/Mac: Run bash script
- Manual: Download from https://tools.hana.ondemand.com/

### Issue: "Not logged in"

**Solution:**
```bash
btp login --subdomain <your-subdomain>
```

### Issue: "No subaccount targeted"

**Solution:**
```bash
btp target --subaccount <subaccount-id>
```

### Issue: "Cannot manage CF instances"

**Reason**: Your HANA Cloud instance is in Cloud Foundry

**Solution**: Use CF CLI instead:
```bash
cf update-service my-hana-db -c '{"data":{"serviceStopped":true}}'
```

### Issue: "Insufficient quota"

**Reason**: Subaccount doesn't have HANA Cloud quota

**Solution**:
1. Go to BTP Cockpit → Entitlements
2. Add SAP HANA Cloud entitlement
3. Assign quota to subaccount

---

## Best Practices

### 1. Daily Start/Stop for Cost Savings

```bash
# Create script: start-hana.sh
#!/bin/bash
btp update services/instance --name my-hana --parameters '{"data":{"serviceStopped":false}}'

# Create script: stop-hana.sh
#!/bin/bash
btp update services/instance --name my-hana --parameters '{"data":{"serviceStopped":true}}'
```

### 2. IP Allowlist Security

```bash
# Production: Restrict to known IPs
btp update services/instance --name prod-hana \
  --parameters '{"data":{"whitelistIPs":["203.0.113.0/24"]}}'

# Development: Can use 0.0.0.0/0 but not recommended
```

### 3. Automated Monitoring

```bash
# Check instance status
btp get services/instance --name my-hana --format json | jq '.status'

# List all instances
btp list services/instance --format json | jq '.[] | {name: .name, status: .status}'
```

### 4. Use with hana-cli

```bash
# Use btp CLI for instance management
btp update services/instance --name my-hana --parameters '{"data":{"serviceStopped":false}}'

# Then use hana-cli for database work
hana-cli connect -n <host>:443 -u DEV_USER -p <password>
hana-cli tables
```

---

## Complete Example: Setting Up Dev Environment

```bash
# 1. Login to BTP
btp login --subdomain mytenant

# 2. Target subaccount
btp target --subaccount dev-subaccount-id

# 3. Create HANA Cloud instance
btp create services/instance \
  --offering-name hana-cloud \
  --plan-name hana-free \
  --name dev-hana \
  --parameters '{
    "data": {
      "memory": 32,
      "systempassword": "HanaDevPass123!",
      "whitelistIPs": ["0.0.0.0/0"]
    }
  }'

# 4. Wait for provisioning (check status)
btp get services/instance --name dev-hana

# 5. Once running, use Database Explorer to create users
# (Open via BTP Cockpit → HANA Cloud Central → Open in DB Explorer)

# 6. Later: Stop when not in use
btp update services/instance --name dev-hana \
  --parameters '{"data":{"serviceStopped":true}}'
```

---

## User Creation Workflow

### Important: btp CLI Does NOT Create Database Users

**What btp CLI Does:**
- ✅ Create/manage HANA Cloud **instances**
- ✅ Start/stop instances
- ✅ Configure instance settings (memory, IPs)

**What btp CLI Does NOT Do:**
- ❌ Create database users
- ❌ Execute SQL statements
- ❌ Manage database objects (tables, views)

### To Create Database Users:

**Method 1: Database Explorer (Recommended)**
1. Use btp CLI to ensure instance is running
2. Open Database Explorer via BTP Cockpit
3. Connect as DBADMIN
4. Execute SQL script to create user

**Method 2: hdbsql/hdbcli (SAP HANA Client)**
```bash
# First ensure instance is running
btp get services/instance --name my-hana

# Then use hdbcli
hdbcli -n <host>:443 -u DBADMIN -p <password> -I create_user.sql
```

**Method 3: hana-cli**
```bash
# After instance is running, configure hana-cli
hana-cli connect -n <host>:443 -u DBADMIN -p <password>

# Then use querySimple for SQL
hana-cli querySimple
```

---

## Command Reference

### Account Management

```bash
# List subaccounts
btp list accounts/subaccount

# Get subaccount details
btp get accounts/subaccount

# List entitlements
btp list accounts/entitlement
```

### Service Management

```bash
# List all services
btp list services/offering

# List service plans
btp list services/plan --offering hana-cloud

# List instances
btp list services/instance

# Get instance details
btp get services/instance --name <name>

# Create instance
btp create services/instance [options]

# Update instance
btp update services/instance [options]

# Delete instance
btp delete services/instance --id <id>
```

### Environment Management

```bash
# List environments
btp list accounts/environment-instance

# Kyma-specific (if applicable)
btp target --kyma <cluster-name>
```

---

## Output Formats

```bash
# JSON output (for scripting)
btp list services/instance --format json

# Table output (human-readable)
btp list services/instance --format table

# Default output
btp list services/instance
```

---

## Integration with Other Tools

### With Cloud Foundry CLI

**If instance is in CF environment:**
```bash
# Use CF CLI instead
cf services
cf update-service my-hana -c '{"data":{"serviceStopped":true}}'
```

### With hana-cli

**hana-cli includes btp CLI wrappers:**
```bash
# Check if btp CLI is available
hana-cli version  # Shows "btp-cli: <version>" or "not installed"

# Use hana-cli BTP commands
hana-cli hc              # List HANA instances
hana-cli hcStart -n db   # Start instance
hana-cli hcStop -n db    # Stop instance
```

### With SAP HANA Client

**After instance is running:**
```bash
# Use hdbcli for SQL
hdbcli -n <host>:443 -u DBADMIN -p <password>

# Execute SQL file
hdbcli -n <host>:443 -u DBADMIN -p <password> -I script.sql
```

---

## Resources

- **Download**: https://tools.hana.ondemand.com/ (Cloud section)
- **Documentation**: https://help.sap.com/docs/btp/sap-business-technology-platform/btp-cli-command-reference
- **HANA Cloud Admin Guide**: https://help.sap.com/docs/hana-cloud/sap-hana-cloud-administration-guide
- **Tutorial**: https://developers.sap.com/tutorials/cp-sapcp-getstarted.html

---

## Summary: CLI Tool Usage

### For Your Current Task (Create Development User):

**You Need:**
1. ✅ **btp CLI** - To manage instance (start/stop if needed)
2. ✅ **Database Explorer** - To create database user (SQL execution)
3. ⚠️ **NOT hana-cli** - Cannot execute multi-line SQL easily

**Workflow:**
1. Ensure instance is running (check in BTP Cockpit or `btp get services/instance`)
2. Open Database Explorer
3. Connect as DBADMIN
4. Execute `create_p2p_user.sql` script
5. Verify user creation

---

**Status**: ✅ btp CLI Documentation Complete  
**Your Instance**: Running in prod-eu10 (likely CF environment)  
**Recommendation**: Use Database Explorer for user creation  
**Next**: Execute SQL script in Database Explorer
