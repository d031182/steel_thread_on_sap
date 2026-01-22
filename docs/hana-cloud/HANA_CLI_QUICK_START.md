# hana-cli Quick Start Guide

**SAP HANA Developer Command Line Interface**

**Installed Version**: 3.202504.1  
**Installation Date**: January 21, 2026  
**Installation Method**: npm with --ignore-scripts flag

---

## Overview

The **hana-cli** is a command-line tool for SAP HANA developers that provides over 100 commands for database management, HDI container operations, and SAP BTP integration.

---

## Installation

```bash
# Install globally with npm (skipping native compilation)
npm install -g hana-cli --ignore-scripts
```

**Note**: The `--ignore-scripts` flag was used to skip the compilation of native dependencies (better-sqlite3) which requires Visual Studio Build Tools.

---

## Installed Components

- **hana-cli**: 3.202504.1 ⭐
- **@sap/cds**: 7.9.1 (CAP framework)
- **@sap/cds-dk**: 8.9.1 (CDS Development Kit)
- **@cap-js/hana**: 0.4.0 (HANA adapter)
- **hdb**: 0.19.8 (Node.js HANA driver)
- **cf-cli**: 8.17.0 (Cloud Foundry CLI)
- **Node.js**: v24.11.0

---

## Basic Commands

### Connection & Setup

```bash
# Connect to HANA Cloud instance
hana-cli connect -n <host>:<port> -u <username> -p <password>

# Example
hana-cli connect -n abc123.hana.trial-us10.hanacloud.ondemand.com:443 -u P2P_DEV_USER -p MyPassword123

# Check connection status
hana-cli status

# List HANA Cloud instances
hana-cli hc
```

### Database Exploration

```bash
# List all schemas
hana-cli schemas

# List tables in a schema
hana-cli tables -s P2P_DEV

# List all tables
hana-cli tables

# Inspect a specific table
hana-cli inspectTable -s P2P_DEV -t Suppliers

# List views
hana-cli views -s P2P_DEV

# List procedures
hana-cli procedures -s P2P_DEV
```

### SQL Execution

```bash
# Execute simple SQL query
hana-cli querySimple

# Call a stored procedure
hana-cli callProcedure -s P2P_DEV -p MyProcedure
```

### HDI Container Management

```bash
# List all HDI containers
hana-cli containers

# Create new HDI container
hana-cli createContainer -c my_container

# Drop HDI container
hana-cli dropContainer -c my_container
```

### User Management

```bash
# List all users
hana-cli users

# Inspect specific user
hana-cli inspectUser -u P2P_DEV_USER

# Create XSA admin user
hana-cli createXSAAdmin -u ADMIN_USER -p Password123
```

### System Information

```bash
# General system info
hana-cli systemInfo

# Host information
hana-cli hostInformation

# Data volumes
hana-cli dataVolumes

# Disk usage
hana-cli disks

# Port assignments
hana-cli ports

# Features and version
hana-cli features
```

### Browser-Based UI

```bash
# Launch browser-based UI (recommended for beginners)
hana-cli UI

# Open DB Explorer
hana-cli opendbx

# Open Business Application Studio
hana-cli openbas
```

### SAP BTP Integration

```bash
# Set BTP target
hana-cli btp

# List BTP subscriptions
hana-cli sub

# BTP information
hana-cli btpInfo

# List HANA Cloud instances
hana-cli hc

# Start HANA Cloud instance
hana-cli hcStart -n my_instance

# Stop HANA Cloud instance
hana-cli hcStop -n my_instance
```

### Service Management

```bash
# List HDI service instances
hana-cli hdi

# List schema service instances
hana-cli schemaInstances

# List SecureStore instances
hana-cli securestore

# List user-provided services
hana-cli ups
```

### Troubleshooting & Diagnostics

```bash
# List trace files
hana-cli traces

# View trace contents
hana-cli traceContents

# List certificates
hana-cli certificates

# Get privilege error details
hana-cli privilegeError -g <error_guid>

# INI file contents
hana-cli iniContents
```

### Development Tools

```bash
# Display CDS preview
hana-cli cds -s P2P_DEV -t Suppliers

# Mass convert tables to CDS
hana-cli massConvert

# Create DB module
hana-cli createModule

# Generate service key connection
hana-cli serviceKey -i my_instance -k my_key
```

---

## Common Workflows

### 1. Initial Connection Setup

```bash
# Step 1: Connect to HANA Cloud
hana-cli connect -n <host>:443 -u <username> -p <password>

# Step 2: Verify connection
hana-cli status

# Step 3: List available schemas
hana-cli schemas
```

### 2. Explore Database Schema

```bash
# List all tables in your schema
hana-cli tables -s P2P_DEV

# Inspect specific table structure
hana-cli inspectTable -s P2P_DEV -t PurchaseOrders

# View table data in browser UI
hana-cli inspectTableUI -s P2P_DEV -t PurchaseOrders
```

### 3. Execute SQL Queries

```bash
# Interactive query
hana-cli querySimple

# Then enter SQL:
# SELECT * FROM P2P_DEV.Suppliers;

# Or use browser UI for easier querying
hana-cli querySimpleUI
```

### 4. Manage HDI Containers

```bash
# Create container
hana-cli createContainer -c P2P_CONTAINER -g P2P_GROUP

# List containers
hana-cli containers

# Drop when done
hana-cli dropContainer -c P2P_CONTAINER
```

---

## Connection Configuration

### Using default-env.json

The `hana-cli connect` command creates a `default-env.json` file with connection details:

```json
{
  "VCAP_SERVICES": {
    "hana": [
      {
        "name": "hana",
        "label": "hana",
        "tags": ["hana", "database"],
        "credentials": {
          "host": "abc123.hana.trial-us10.hanacloud.ondemand.com",
          "port": "443",
          "user": "P2P_DEV_USER",
          "password": "MyPassword123",
          "schema": "P2P_DEV"
        }
      }
    ]
  }
}
```

Once configured, most commands will use these stored credentials automatically.

---

## Tips & Best Practices

### 1. Use Browser UI for Complex Tasks
```bash
# Launch full UI
hana-cli UI

# Easier for:
# - Browsing large tables
# - Complex SQL queries
# - Schema exploration
```

### 2. Use Aliases
Many commands have short aliases:
- `hana-cli c` = `hana-cli connect`
- `hana-cli t` = `hana-cli tables`
- `hana-cli v` = `hana-cli views`
- `hana-cli s` = `hana-cli status`

### 3. Tab Completion
```bash
# Generate completion script
hana-cli completion

# For PowerShell, add to profile:
# hana-cli completion >> $PROFILE
```

### 4. Get Help
```bash
# General help
hana-cli --help

# Command-specific help
hana-cli connect --help
hana-cli tables --help
```

---

## Comparison: hana-cli vs hdbcli

| Feature | hana-cli (npm) | hdbcli (SAP Client) |
|---------|----------------|---------------------|
| Installation | `npm install -g hana-cli` | SAP Software Download |
| Size | ~900 packages | ~50MB installer |
| Language | JavaScript/Node.js | C/C++ native |
| Commands | 100+ specialized commands | SQL-only |
| Browser UI | ✅ Yes | ❌ No |
| HDI Support | ✅ Extensive | ❌ Limited |
| BTP Integration | ✅ Yes | ❌ No |
| CDS/CAP | ✅ Built-in | ❌ No |
| Use Case | Development/Administration | SQL execution |

**Recommendation**: 
- Use **hana-cli** for development, schema management, HDI containers
- Use **hdbcli** for production SQL scripts, automated jobs

---

## Common Issues & Solutions

### Issue: "hana-cli command not found"

**Solution:**
```bash
# Verify npm global path is in PATH
npm config get prefix

# Should be: C:\Users\<username>\AppData\Roaming\npm
# Add to PATH if missing
```

### Issue: Connection fails

**Check:**
1. HANA Cloud instance is running (check in BTP Cockpit)
2. IP allowlist includes your IP address
3. Credentials are correct
4. Port 443 is accessible

**Solution:**
```bash
# Start instance if stopped
hana-cli hcStart -n <instance_name>

# Check connection
hana-cli connect -n <host>:443 -u <user> -p <password>
```

### Issue: SSL/Certificate errors

**Solution:**
HANA Cloud requires SSL. Ensure:
- Using port 443
- Connection string includes SSL parameters
- Certificates are valid

---

## Resources

- **GitHub**: https://github.com/SAP-samples/hana-developer-cli-tool-example
- **Changelog**: https://github.com/SAP-samples/hana-developer-cli-tool-example/blob/main/CHANGELOG.md
- **npm Package**: https://www.npmjs.com/package/hana-cli
- **SAP Community**: https://community.sap.com/

---

## Next Steps

1. ✅ Install hana-cli (completed)
2. 📋 Connect to your HANA Cloud instance
3. 📋 Explore your schema with `hana-cli tables`
4. 📋 Try browser UI with `hana-cli UI`
5. 📋 Execute P2P database scripts
6. 📋 Create HDI containers for deployment

---

**Installation Status**: ✅ Complete  
**Last Updated**: January 21, 2026, 10:27 PM  
**Ready to use**: YES - Start with `hana-cli connect`
