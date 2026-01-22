# SAP HANA Client Installation Guide

**For Windows - SAP HANA Cloud CLI (hdbcli)**

**Date**: January 21, 2026  
**Required Version**: SAP HANA Client 2.4.167 or higher (for HANA Cloud)

---

## Overview

The **SAP HANA Client** provides command-line tools for connecting to SAP HANA Cloud databases, including:
- **hdbcli** - SQL command-line interface
- **hdbsql** - SQL script executor
- JDBC/ODBC drivers
- Python/Node.js database interfaces

---

## Prerequisites

✅ **Windows 64-bit** operating system  
✅ **Administrator privileges** for installation  
✅ **SAPCAR tool** for unpacking .SAR files (downloadable from SAP)  
✅ **SAP User Account** with Software Download Center access

---

## Installation Steps

### Step 1: Download SAP HANA Client

1. **Access SAP Software Download Center**
   - Navigate to: https://support.sap.com/swdc
   - Login with your S-user credentials

2. **Navigate to HANA Client**
   - Go to: **Support Packages & Patches**
   - Select: **By Alphabetical Index (A-Z)**
   - Choose: **H** → **HANA CLIENTS**
   - Select: **SAP HANA CLIENT 2.0**

3. **Download Latest Version**
   - Find the latest revision (e.g., 2.22.x or higher)
   - Download: `IMDB_CLIENT20_<version>_<build>.SAR` for **Windows x86_64**
   - Example: `IMDB_CLIENT20_022_22-80002949.SAR`

4. **Download SAPCAR** (if not already installed)
   - In same download center, search for "SAPCAR"
   - Download Windows x64 version
   - Example: `SAPCAR_1320-80000935.EXE`

### Step 2: Extract the Installation Files

1. **Create Installation Directory**
   ```powershell
   # Create directory for HANA Client files
   New-Item -Path "C:\SAP\HDBClient" -ItemType Directory -Force
   cd C:\SAP\HDBClient
   ```

2. **Copy Files**
   - Copy downloaded `.SAR` file to `C:\SAP\HDBClient`
   - Copy `SAPCAR.EXE` to same directory

3. **Extract Archive**
   ```powershell
   # Extract using SAPCAR
   .\SAPCAR.EXE -xvf IMDB_CLIENT20_<version>.SAR
   ```

   This creates a `HDB_CLIENT_WINDOWS_X86_64` subdirectory.

### Step 3: Install SAP HANA Client

**Option A: GUI Installation (Recommended)**

1. **Run Installer**
   ```powershell
   cd HDB_CLIENT_WINDOWS_X86_64
   .\hdbsetup.exe
   ```

2. **Follow Installation Wizard**
   - Select: **Install new SAP HANA Database Client**
   - Choose installation path (default: `C:\Program Files\SAP\hdbclient`)
   - Accept license agreement
   - Wait for installation to complete

3. **Verify PATH**
   - Installer should automatically add to system PATH
   - Check: Open new Command Prompt and run `echo %PATH%`
   - Should see: `C:\Program Files\SAP\hdbclient`

**Option B: Command-Line Installation**

```powershell
# Run installer in unattended mode
cd HDB_CLIENT_WINDOWS_X86_64
.\hdbinst.exe -a client --path="C:\Program Files\SAP\hdbclient"
```

### Step 4: Verify Installation

1. **Open New Command Prompt** (important - to reload PATH)

2. **Check hdbcli Version**
   ```powershell
   hdbcli --version
   ```

   Expected output:
   ```
   SAP HANA Database Client
   version: 2.22.xx
   ```

3. **Check Environment Variables**
   ```powershell
   # Check if PATH includes hdbclient
   echo %PATH%

   # Check HDB_CLIENT_HOME (optional)
   echo %HDB_CLIENT_HOME%
   ```

4. **Test SQL Connection** (requires HANA instance details)
   ```powershell
   hdbcli -n <host>:<port> -u <username> -p <password>
   ```

---

## Post-Installation Configuration

### Manual PATH Configuration (if needed)

If installer didn't add to PATH:

1. **Open System Properties**
   - Press `Win + R`, type `sysdm.cpl`, press Enter
   - Click **Advanced** tab → **Environment Variables**

2. **Edit System PATH**
   - Under **System variables**, select `Path`
   - Click **Edit** → **New**
   - Add: `C:\Program Files\SAP\hdbclient`
   - Click **OK** on all dialogs

3. **Restart Command Prompt** to reload PATH

### Set HDB_CLIENT_HOME (Optional)

```powershell
# Set environment variable
setx HDB_CLIENT_HOME "C:\Program Files\SAP\hdbclient" /M
```

---

## Using hdbcli

### Basic Connection

```bash
# Connect to HANA Cloud instance
hdbcli -n <hostname>:<port> -u <username> -p <password>

# Example
hdbcli -n abc123.hana.trial-us10.hanacloud.ondemand.com:443 -u P2P_DEV_USER -p MyPassword123!
```

### Connection with SSL (HANA Cloud requires SSL)

```bash
# HANA Cloud requires encrypted connections
hdbcli -n <hostname>:443 -u <username> -p <password> -e -ssltruststore
```

### Execute SQL File

```bash
# Run SQL script
hdbcli -n <hostname>:443 -u <username> -p <password> -I script.sql
```

### Interactive Mode

```bash
# Connect and start interactive session
hdbcli -n <hostname>:443 -u <username> -p <password>

# Once connected, run SQL:
SELECT * FROM USERS;
```

---

## Common Commands

```bash
# Show help
hdbcli --help

# Show version
hdbcli --version

# List available options
hdbcli -h

# Connect with specific database
hdbcli -n <host>:443 -u <user> -p <password> -d <database>

# Export results to CSV
hdbcli -n <host>:443 -u <user> -p <password> -o output.csv "SELECT * FROM table"
```

---

## Connection Information for HANA Cloud

### Finding Your Connection Details

1. **Open SAP BTP Cockpit**
   - Navigate to your subaccount
   - Go to **Cloud Foundry** → **Spaces**
   - Select your space

2. **Open SAP HANA Cloud Central**
   - Click **SAP HANA Cloud** in left menu
   - Find your instance
   - Click **Actions** (⋮) → **Copy SQL Endpoint**

3. **Connection String Format**
   ```
   <instance-id>.hana.<region>.hanacloud.ondemand.com:443
   ```

   Example:
   ```
   abc12345-6789-abcd-ef01-234567890abc.hana.trial-us10.hanacloud.ondemand.com:443
   ```

---

## Troubleshooting

### Issue: "hdbcli is not recognized"

**Solution:**
1. Verify installation path exists: `C:\Program Files\SAP\hdbclient`
2. Check PATH environment variable
3. Restart Command Prompt/PowerShell
4. Add to PATH manually if needed

### Issue: "Connection failed"

**Possible Causes:**
1. Wrong hostname/port
2. Instance stopped (start in HANA Cloud Central)
3. IP allowlist restrictions (add your IP in HANA Cloud Central)
4. Wrong credentials
5. Missing SSL configuration

**Solution:**
```bash
# Try with explicit SSL settings
hdbcli -n <host>:443 -u <user> -p <password> -e -ssltruststore
```

### Issue: "Certificate validation failed"

**Solution:**
```bash
# Accept self-signed certificates (development only!)
hdbcli -n <host>:443 -u <user> -p <password> -e -ssltruststore -sslvalidatecertificate false
```

### Issue: Version too old

**Check Version:**
```bash
hdbcli --version
```

**Required:** 2.4.167 or higher for HANA Cloud

**Solution:** Download latest version from SAP Software Download Center

---

## Additional Tools Included

### hdbsql
SQL command-line processor (alternative to hdbcli)

```bash
hdbsql -n <host>:443 -u <user> -p <password>
```

### JDBC Driver
Located at: `C:\Program Files\SAP\hdbclient\ngdbc.jar`

### ODBC Driver
Automatically registered during installation

### Python Driver
```bash
# Install via pip
pip install hdbcli
```

---

## Version Requirements

| Component | Minimum Version | Recommended |
|-----------|----------------|-------------|
| SAP HANA Client | 2.4.167 | Latest (2.22.x) |
| Windows | 10 64-bit | 11 64-bit |
| Python (optional) | 3.7+ | 3.11+ |
| Node.js (optional) | 14+ | 20+ |

---

## Resources

- **Official Guide**: SAP HANA Client Installation and Update Guide (PDF)
- **SAP Note**: 2769719 - Release Policy for SAP HANA Client
- **Download Center**: https://support.sap.com/swdc
- **Documentation**: https://help.sap.com/docs/SAP_HANA_CLIENT

---

## Next Steps After Installation

1. ✅ Verify installation with `hdbcli --version`
2. ✅ Get connection details from HANA Cloud Central
3. ✅ Test connection: `hdbcli -n <host>:443 -u P2P_DEV_USER -p <password>`
4. ✅ Run test query: `SELECT * FROM USERS;`
5. ✅ Execute P2P schema creation scripts

---

**Status**: Ready for installation  
**Last Updated**: January 21, 2026, 10:18 PM  
**Next**: Download from SAP Software Download Center
