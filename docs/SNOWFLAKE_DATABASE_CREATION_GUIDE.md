# Snowflake Database Creation Guide

## Overview
This guide explains how to create databases in Snowflake using various methods.

## Prerequisites
- Active Snowflake account
- Appropriate privileges (ACCOUNTADMIN or role with CREATE DATABASE privilege)
- Access to Snowflake Web UI, SnowSQL, or programmatic interface

---

## Method 1: Using Snowflake Web UI

### Steps:
1. **Log into Snowflake**
   - Navigate to your Snowflake account URL: `https://<account_identifier>.snowflakecomputing.com`
   - Enter credentials

2. **Navigate to Databases**
   - Click on "Data" in the left sidebar
   - Select "Databases"

3. **Create Database**
   - Click "+ Database" button (top right)
   - Enter database name
   - (Optional) Add comment for documentation
   - Click "Create"

---

## Method 2: Using SQL Commands

### Basic Syntax:
```sql
CREATE DATABASE <database_name>;
```

### Example - Simple Database:
```sql
CREATE DATABASE MY_P2P_DATABASE;
```

### Example - Database with Options:
```sql
CREATE DATABASE MY_P2P_DATABASE
  COMMENT = 'Procure-to-Pay data warehouse'
  DATA_RETENTION_TIME_IN_DAYS = 7;
```

### Example - Database from Share:
```sql
CREATE DATABASE SHARED_DATABASE
  FROM SHARE <provider_account>.<share_name>;
```

### Example - Clone Existing Database:
```sql
CREATE DATABASE MY_P2P_DATABASE_CLONE
  CLONE MY_P2P_DATABASE;
```

---

## Method 3: Using SnowSQL (CLI)

### Steps:
1. **Install SnowSQL** (if not already installed)
   ```bash
   # Download from Snowflake website or use package manager
   ```

2. **Connect to Snowflake**
   ```bash
   snowsql -a <account_identifier> -u <username>
   ```

3. **Create Database**
   ```sql
   CREATE DATABASE MY_DATABASE;
   ```

---

## Method 4: Using Python (Snowflake Connector)

### Installation:
```bash
pip install snowflake-connector-python
```

### Python Script:
```python
import snowflake.connector

# Establish connection
conn = snowflake.connector.connect(
    user='<username>',
    password='<password>',
    account='<account_identifier>',
    warehouse='<warehouse_name>',
    role='<role_name>'
)

# Create cursor
cur = conn.cursor()

# Create database
cur.execute("""
    CREATE DATABASE IF NOT EXISTS MY_P2P_DATABASE
    COMMENT = 'Created via Python connector'
""")

print("Database created successfully")

# Close connection
cur.close()
conn.close()
```

---

## Method 5: Using Other Programming Languages

### Node.js Example:
```javascript
const snowflake = require('snowflake-sdk');

const connection = snowflake.createConnection({
  account: '<account_identifier>',
  username: '<username>',
  password: '<password>',
  warehouse: '<warehouse_name>',
  role: '<role_name>'
});

connection.connect((err, conn) => {
  if (err) {
    console.error('Unable to connect: ' + err.message);
  } else {
    conn.execute({
      sqlText: 'CREATE DATABASE MY_P2P_DATABASE',
      complete: (err, stmt, rows) => {
        if (err) {
          console.error('Failed to execute statement: ' + err.message);
        } else {
          console.log('Database created successfully');
        }
      }
    });
  }
});
```

---

## Database Creation Options

### Key Parameters:

| Parameter | Description | Example |
|-----------|-------------|---------|
| `DATA_RETENTION_TIME_IN_DAYS` | Time Travel retention period (0-90 days) | `DATA_RETENTION_TIME_IN_DAYS = 7` |
| `MAX_DATA_EXTENSION_TIME_IN_DAYS` | Maximum extension for Time Travel | `MAX_DATA_EXTENSION_TIME_IN_DAYS = 14` |
| `COMMENT` | Documentation comment | `COMMENT = 'Production database'` |
| `FROM SHARE` | Create from shared database | `FROM SHARE provider.share_name` |
| `CLONE` | Clone existing database | `CLONE source_database` |
| `TRANSIENT` | Create transient database (no fail-safe) | `CREATE TRANSIENT DATABASE temp_db` |

### Transient Database:
```sql
-- Transient databases do not have fail-safe period
-- Lower storage costs, suitable for temporary/staging data
CREATE TRANSIENT DATABASE STAGING_DATABASE
  COMMENT = 'Temporary staging environment';
```

---

## Post-Creation Steps

### 1. Verify Database Creation:
```sql
SHOW DATABASES LIKE 'MY_P2P_DATABASE';
```

### 2. Use the Database:
```sql
USE DATABASE MY_P2P_DATABASE;
```

### 3. Create Schemas:
```sql
CREATE SCHEMA RAW_DATA;
CREATE SCHEMA STAGING;
CREATE SCHEMA ANALYTICS;
```

### 4. Grant Permissions:
```sql
-- Grant usage to a role
GRANT USAGE ON DATABASE MY_P2P_DATABASE TO ROLE DATA_ANALYST;

-- Grant create schema privilege
GRANT CREATE SCHEMA ON DATABASE MY_P2P_DATABASE TO ROLE DATA_ENGINEER;

-- Grant ownership
GRANT OWNERSHIP ON DATABASE MY_P2P_DATABASE TO ROLE ADMIN_ROLE;
```

---

## Complete Example: P2P Database Setup

```sql
-- Step 1: Create database
CREATE DATABASE P2P_DATA_WAREHOUSE
  COMMENT = 'Procure-to-Pay Data Warehouse'
  DATA_RETENTION_TIME_IN_DAYS = 7;

-- Step 2: Use the database
USE DATABASE P2P_DATA_WAREHOUSE;

-- Step 3: Create schemas
CREATE SCHEMA RAW
  COMMENT = 'Raw data from source systems';

CREATE SCHEMA STAGING
  COMMENT = 'Staging area for transformations';

CREATE SCHEMA ANALYTICS
  COMMENT = 'Analytics-ready data models';

CREATE SCHEMA ARCHIVE
  COMMENT = 'Historical archived data';

-- Step 4: Grant permissions
GRANT USAGE ON DATABASE P2P_DATA_WAREHOUSE TO ROLE P2P_ANALYST;
GRANT USAGE ON SCHEMA RAW TO ROLE P2P_ANALYST;
GRANT SELECT ON ALL TABLES IN SCHEMA RAW TO ROLE P2P_ANALYST;

-- Step 5: Verify
SHOW DATABASES LIKE 'P2P_DATA_WAREHOUSE';
SHOW SCHEMAS IN DATABASE P2P_DATA_WAREHOUSE;
```

---

## Best Practices

### 1. Naming Conventions
- Use uppercase for database names (Snowflake convention)
- Use descriptive names that indicate purpose
- Avoid spaces (use underscores)
- Examples: `SALES_DW`, `CUSTOMER_360`, `P2P_ANALYTICS`

### 2. Security
- Grant minimal required permissions
- Use role-based access control (RBAC)
- Document all access grants
- Regularly audit permissions

### 3. Organization
- Create separate schemas for different data layers
- Use consistent schema naming across databases
- Common pattern: `RAW`, `STAGING`, `CURATED`, `ANALYTICS`

### 4. Data Retention
- Set appropriate retention periods based on compliance requirements
- Consider storage costs vs. recovery needs
- Standard databases: 0-90 days Time Travel
- Enterprise edition: Up to 90 days

### 5. Documentation
- Always add meaningful comments
- Document database purpose and ownership
- Maintain metadata about data sources
- Use COMMENT parameter liberally

---

## Managing Databases

### List All Databases:
```sql
SHOW DATABASES;
```

### Get Database Details:
```sql
DESCRIBE DATABASE MY_P2P_DATABASE;
```

### Modify Database:
```sql
-- Change comment
ALTER DATABASE MY_P2P_DATABASE 
  SET COMMENT = 'Updated description';

-- Change data retention
ALTER DATABASE MY_P2P_DATABASE 
  SET DATA_RETENTION_TIME_IN_DAYS = 14;

-- Rename database
ALTER DATABASE MY_P2P_DATABASE 
  RENAME TO P2P_PRODUCTION;
```

### Drop Database:
```sql
-- Be careful! This is permanent after fail-safe period
DROP DATABASE IF EXISTS MY_P2P_DATABASE;
```

### Undrop Database (Time Travel):
```sql
-- Restore within retention period
UNDROP DATABASE MY_P2P_DATABASE;
```

---

## Common Issues and Solutions

### Issue 1: Insufficient Privileges
**Error:** "Insufficient privileges to operate on database"
**Solution:** 
```sql
-- Request ACCOUNTADMIN or role with CREATE DATABASE privilege
USE ROLE ACCOUNTADMIN;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE MY_ROLE;
```

### Issue 2: Database Already Exists
**Error:** "Database already exists"
**Solution:**
```sql
-- Use IF NOT EXISTS clause
CREATE DATABASE IF NOT EXISTS MY_DATABASE;
```

### Issue 3: Invalid Database Name
**Error:** "Invalid identifier"
**Solution:**
- Use valid characters: letters, numbers, underscores
- Start with letter or underscore
- Max length: 255 characters
- Use quotes for special cases: `CREATE DATABASE "my-database"`

---

## Cost Considerations

### Storage Costs
- Active storage: Charged monthly
- Time Travel storage: Charged for retained data
- Fail-safe storage: Charged for 7-day fail-safe period

### Optimization Tips
1. Use transient databases for temporary data
2. Set appropriate data retention periods
3. Regularly purge unnecessary data
4. Consider cloning for dev/test environments
5. Monitor storage usage with `SHOW DATABASES`

---

## Monitoring and Maintenance

### Check Database Size:
```sql
-- Using Information Schema
SELECT 
    TABLE_CATALOG AS DATABASE_NAME,
    SUM(ACTIVE_BYTES) / (1024*1024*1024) AS ACTIVE_GB,
    SUM(TIME_TRAVEL_BYTES) / (1024*1024*1024) AS TIME_TRAVEL_GB,
    SUM(FAILSAFE_BYTES) / (1024*1024*1024) AS FAILSAFE_GB
FROM SNOWFLAKE.ACCOUNT_USAGE.TABLE_STORAGE_METRICS
WHERE TABLE_CATALOG = 'MY_P2P_DATABASE'
GROUP BY TABLE_CATALOG;
```

### Monitor Database Usage:
```sql
-- Query history for specific database
SELECT 
    QUERY_TEXT,
    EXECUTION_TIME,
    USER_NAME,
    START_TIME
FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE DATABASE_NAME = 'MY_P2P_DATABASE'
ORDER BY START_TIME DESC
LIMIT 100;
```

---

## Additional Resources

- **Snowflake Documentation:** https://docs.snowflake.com/en/sql-reference/sql/create-database
- **Snowflake Community:** https://community.snowflake.com
- **Best Practices:** https://docs.snowflake.com/en/user-guide/best-practices

---

## Summary

Creating a database in Snowflake is straightforward:

1. **Simplest method:** `CREATE DATABASE MY_DATABASE;`
2. **Web UI:** Click + Database button
3. **Programmatically:** Use Snowflake connectors
4. **Always:** Grant appropriate permissions and document

Choose the method that best fits your workflow and automation needs.
