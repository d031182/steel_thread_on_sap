# Snowflake Stage Creation Guide

## Overview
Stages in Snowflake are locations where data files are stored for loading into or unloading from database tables. This guide explains how to create and manage stages in Snowflake.

## What is a Stage?

A stage specifies where data files are stored (staged) so that the data can be loaded into or unloaded from Snowflake tables. Stages are essential for data ingestion workflows.

### Stage Types:

1. **Internal Stages** - Managed by Snowflake
   - User Stage
   - Table Stage
   - Named Internal Stage

2. **External Stages** - Cloud storage locations
   - Amazon S3
   - Azure Blob Storage
   - Google Cloud Storage

---

## Prerequisites

- Active Snowflake account
- Appropriate privileges (CREATE STAGE on schema)
- For external stages: Cloud storage credentials
- Database and schema already created

---

## Method 1: Creating Internal Stages

### Named Internal Stage

Named internal stages are permanent Snowflake objects that can be used by multiple users.

#### Basic Syntax:
```sql
CREATE STAGE <stage_name>;
```

#### Example - Simple Internal Stage:
```sql
-- Create database and schema first
USE DATABASE P2P_DATA_WAREHOUSE;
USE SCHEMA RAW;

-- Create internal stage
CREATE STAGE my_internal_stage;
```

#### Example - Internal Stage with Options:
```sql
CREATE STAGE landing_stage
  FILE_FORMAT = (TYPE = 'CSV' FIELD_DELIMITER = ',' SKIP_HEADER = 1)
  COMMENT = 'Landing stage for CSV files';
```

#### Example - Internal Stage with Directory:
```sql
CREATE STAGE invoice_stage
  DIRECTORY = (ENABLE = TRUE)
  FILE_FORMAT = (TYPE = 'JSON')
  COMMENT = 'Stage for supplier invoice JSON files';
```

### User Stage

Every user has a default stage named `@~`. It's automatically available and doesn't need creation.

```sql
-- List files in user stage
LIST @~;

-- Upload file to user stage (using SnowSQL or PUT command)
PUT file://local_file.csv @~;
```

### Table Stage

Every table has a default stage named `@%<table_name>`. It's automatically created with the table.

```sql
-- Create table (table stage is auto-created)
CREATE TABLE supplier_invoices (
    invoice_id VARCHAR(50),
    amount NUMBER(15,2)
);

-- List files in table stage
LIST @%supplier_invoices;

-- Upload to table stage
PUT file://invoices.csv @%supplier_invoices;
```

---

## Method 2: Creating External Stages

External stages reference data files stored in cloud storage.

### Amazon S3 Stage

#### Using AWS IAM User Credentials:
```sql
CREATE STAGE s3_stage
  URL = 's3://mybucket/path/to/files/'
  CREDENTIALS = (
    AWS_KEY_ID = '<your_aws_key_id>'
    AWS_SECRET_KEY = '<your_aws_secret_key>'
  )
  FILE_FORMAT = (TYPE = 'CSV' FIELD_DELIMITER = ',');
```

#### Using AWS IAM Role (Recommended):
```sql
-- Step 1: Create storage integration (requires ACCOUNTADMIN)
CREATE STORAGE INTEGRATION s3_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = S3
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789:role/snowflake_role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://mybucket/path/');

-- Step 2: Create stage using integration
CREATE STAGE s3_stage
  STORAGE_INTEGRATION = s3_integration
  URL = 's3://mybucket/path/to/files/'
  FILE_FORMAT = (TYPE = 'CSV');
```

### Azure Blob Storage Stage

#### Using SAS Token:
```sql
CREATE STAGE azure_stage
  URL = 'azure://myaccount.blob.core.windows.net/mycontainer/path/'
  CREDENTIALS = (
    AZURE_SAS_TOKEN = '<your_sas_token>'
  )
  FILE_FORMAT = (TYPE = 'CSV');
```

#### Using Storage Integration:
```sql
-- Step 1: Create storage integration
CREATE STORAGE INTEGRATION azure_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = AZURE
  ENABLED = TRUE
  AZURE_TENANT_ID = '<tenant_id>'
  STORAGE_ALLOWED_LOCATIONS = ('azure://myaccount.blob.core.windows.net/mycontainer/');

-- Step 2: Create stage
CREATE STAGE azure_stage
  STORAGE_INTEGRATION = azure_integration
  URL = 'azure://myaccount.blob.core.windows.net/mycontainer/path/'
  FILE_FORMAT = (TYPE = 'JSON');
```

### Google Cloud Storage Stage

```sql
-- Step 1: Create storage integration
CREATE STORAGE INTEGRATION gcs_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = GCS
  ENABLED = TRUE
  STORAGE_ALLOWED_LOCATIONS = ('gcs://mybucket/path/');

-- Step 2: Create stage
CREATE STAGE gcs_stage
  STORAGE_INTEGRATION = gcs_integration
  URL = 'gcs://mybucket/path/'
  FILE_FORMAT = (TYPE = 'PARQUET');
```

---

## File Format Options

### CSV File Format:
```sql
CREATE STAGE csv_stage
  FILE_FORMAT = (
    TYPE = 'CSV'
    FIELD_DELIMITER = ','
    SKIP_HEADER = 1
    FIELD_OPTIONALLY_ENCLOSED_BY = '"'
    NULL_IF = ('NULL', 'null', '')
    EMPTY_FIELD_AS_NULL = TRUE
    COMPRESSION = 'GZIP'
  );
```

### JSON File Format:
```sql
CREATE STAGE json_stage
  FILE_FORMAT = (
    TYPE = 'JSON'
    COMPRESSION = 'AUTO'
    STRIP_OUTER_ARRAY = TRUE
  );
```

### Parquet File Format:
```sql
CREATE STAGE parquet_stage
  FILE_FORMAT = (
    TYPE = 'PARQUET'
    COMPRESSION = 'SNAPPY'
  );
```

### Using Named File Format:
```sql
-- Create reusable file format
CREATE FILE FORMAT my_csv_format
  TYPE = 'CSV'
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1;

-- Create stage using named format
CREATE STAGE data_stage
  FILE_FORMAT = my_csv_format;
```

---

## Complete Example: P2P Data Pipeline Stages

```sql
-- Set context
USE DATABASE P2P_DATA_WAREHOUSE;
USE SCHEMA RAW;

-- 1. Create file formats
CREATE FILE FORMAT csv_format
  TYPE = 'CSV'
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  NULL_IF = ('NULL', '')
  COMPRESSION = 'AUTO';

CREATE FILE FORMAT json_format
  TYPE = 'JSON'
  STRIP_OUTER_ARRAY = TRUE
  COMPRESSION = 'AUTO';

-- 2. Create internal stages for different data types
CREATE STAGE invoice_landing
  FILE_FORMAT = csv_format
  DIRECTORY = (ENABLE = TRUE)
  COMMENT = 'Landing stage for supplier invoice CSV files';

CREATE STAGE purchase_order_landing
  FILE_FORMAT = json_format
  DIRECTORY = (ENABLE = TRUE)
  COMMENT = 'Landing stage for purchase order JSON files';

CREATE STAGE error_stage
  FILE_FORMAT = csv_format
  COMMENT = 'Stage for rejected/error records';

-- 3. Create external S3 stage (if using AWS)
CREATE STORAGE INTEGRATION s3_p2p_integration
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = S3
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'arn:aws:iam::123456789:role/snowflake_p2p_role'
  STORAGE_ALLOWED_LOCATIONS = ('s3://p2p-data-bucket/');

CREATE STAGE s3_external_stage
  STORAGE_INTEGRATION = s3_p2p_integration
  URL = 's3://p2p-data-bucket/incoming/'
  FILE_FORMAT = csv_format
  COMMENT = 'External S3 stage for incoming P2P data';

-- 4. Verify stages
SHOW STAGES;
```

---

## Managing Stages

### List All Stages:
```sql
SHOW STAGES;

-- In specific schema
SHOW STAGES IN SCHEMA RAW;
```

### Describe Stage:
```sql
DESCRIBE STAGE my_stage;
```

### List Files in Stage:
```sql
-- List all files
LIST @my_stage;

-- List files with pattern
LIST @my_stage PATTERN = '.*invoices.*\.csv';

-- List files in subdirectory
LIST @my_stage/subfolder/;
```

### Modify Stage:
```sql
-- Change file format
ALTER STAGE my_stage 
  SET FILE_FORMAT = (TYPE = 'JSON');

-- Change comment
ALTER STAGE my_stage 
  SET COMMENT = 'Updated stage description';

-- Enable directory
ALTER STAGE my_stage 
  SET DIRECTORY = (ENABLE = TRUE);
```

### Drop Stage:
```sql
DROP STAGE IF EXISTS my_stage;
```

---

## Working with Stage Files

### Upload Files (Internal Stages)

Using SnowSQL:
```bash
# Upload single file
PUT file://c:/data/invoices.csv @my_stage;

# Upload with compression
PUT file://c:/data/invoices.csv @my_stage AUTO_COMPRESS=TRUE;

# Upload multiple files
PUT file://c:/data/*.csv @my_stage;

# Upload to subdirectory
PUT file://c:/data/invoices.csv @my_stage/2024/january/;
```

### Download Files

Using SnowSQL:
```bash
# Download from stage to local
GET @my_stage file://c:/downloads/;

# Download specific file
GET @my_stage/invoices.csv file://c:/downloads/;
```

### Remove Files:
```sql
-- Remove specific file
REMOVE @my_stage/invoices.csv;

-- Remove with pattern
REMOVE @my_stage PATTERN = '.*2023.*\.csv';

-- Remove all files
REMOVE @my_stage;
```

---

## Loading Data from Stage

### Basic COPY INTO:
```sql
-- Create target table
CREATE TABLE supplier_invoices (
    invoice_id VARCHAR(50),
    supplier_id VARCHAR(50),
    invoice_date DATE,
    amount NUMBER(15,2)
);

-- Load data from stage
COPY INTO supplier_invoices
FROM @invoice_landing
FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1)
ON_ERROR = 'CONTINUE';
```

### Advanced COPY with Transformations:
```sql
COPY INTO supplier_invoices (invoice_id, supplier_id, invoice_date, amount)
FROM (
    SELECT 
        $1::VARCHAR,
        $2::VARCHAR,
        TO_DATE($3, 'YYYY-MM-DD'),
        $4::NUMBER(15,2)
    FROM @invoice_landing
)
FILE_FORMAT = csv_format
ON_ERROR = 'SKIP_FILE'
PURGE = TRUE;
```

### Load from Specific Files:
```sql
COPY INTO supplier_invoices
FROM @invoice_landing/2024/january/
FILES = ('invoices_01.csv', 'invoices_02.csv')
FILE_FORMAT = csv_format;
```

### Load with Pattern Matching:
```sql
COPY INTO supplier_invoices
FROM @invoice_landing
PATTERN = '.*invoice.*\.csv'
FILE_FORMAT = csv_format;
```

---

## Unloading Data to Stage

### Basic COPY INTO (Unload):
```sql
-- Unload table to stage
COPY INTO @my_stage/export/
FROM supplier_invoices
FILE_FORMAT = (TYPE = 'CSV' COMPRESSION = 'GZIP')
HEADER = TRUE;
```

### Unload with Query:
```sql
COPY INTO @my_stage/monthly_report/
FROM (
    SELECT 
        invoice_id,
        supplier_id,
        invoice_date,
        amount
    FROM supplier_invoices
    WHERE YEAR(invoice_date) = 2024
)
FILE_FORMAT = (TYPE = 'CSV')
SINGLE = TRUE
MAX_FILE_SIZE = 5368709120;  -- 5GB
```

### Unload to External Stage:
```sql
COPY INTO @s3_external_stage/reports/
FROM analytics.monthly_summary
FILE_FORMAT = (TYPE = 'PARQUET')
OVERWRITE = TRUE;
```

---

## Stage Security and Permissions

### Grant Permissions:
```sql
-- Grant usage on stage
GRANT USAGE ON STAGE my_stage TO ROLE data_engineer;

-- Grant read permission
GRANT READ ON STAGE my_stage TO ROLE analyst;

-- Grant write permission (for internal stages)
GRANT WRITE ON STAGE my_stage TO ROLE etl_role;

-- Grant all privileges
GRANT ALL PRIVILEGES ON STAGE my_stage TO ROLE admin_role;
```

### Revoke Permissions:
```sql
REVOKE USAGE ON STAGE my_stage FROM ROLE analyst;
```

### Check Permissions:
```sql
SHOW GRANTS ON STAGE my_stage;
```

---

## Best Practices

### 1. Naming Conventions
```sql
-- Use descriptive names
CREATE STAGE supplier_invoice_landing;
CREATE STAGE purchase_order_archive;

-- Include environment indicators
CREATE STAGE dev_landing_stage;
CREATE STAGE prod_export_stage;
```

### 2. Organize with Subdirectories
```sql
-- Upload to organized structure
PUT file://invoices.csv @my_stage/year=2024/month=01/;
PUT file://orders.csv @my_stage/year=2024/month=01/;
```

### 3. Use Directory Tables
```sql
-- Enable directory for external stages
CREATE STAGE s3_stage
  URL = 's3://mybucket/'
  STORAGE_INTEGRATION = my_integration
  DIRECTORY = (ENABLE = TRUE);

-- Refresh directory
ALTER STAGE s3_stage REFRESH;

-- Query directory
SELECT * FROM DIRECTORY(@s3_stage);
```

### 4. Implement File Format Standards
```sql
-- Create standard file formats
CREATE FILE FORMAT standard_csv
  TYPE = 'CSV'
  FIELD_DELIMITER = ','
  SKIP_HEADER = 1
  COMPRESSION = 'AUTO';

-- Use across multiple stages
CREATE STAGE stage1 FILE_FORMAT = standard_csv;
CREATE STAGE stage2 FILE_FORMAT = standard_csv;
```

### 5. Monitor Stage Usage
```sql
-- Check stage storage
SELECT 
    STAGE_NAME,
    STAGE_SCHEMA,
    STAGE_TYPE,
    STAGE_URL,
    COMMENT
FROM INFORMATION_SCHEMA.STAGES
WHERE STAGE_SCHEMA = 'RAW';

-- Monitor file operations
SELECT 
    FILE_NAME,
    FILE_SIZE,
    LAST_MODIFIED
FROM DIRECTORY(@my_stage);
```

---

## Automation with Python

### Create Stage Programmatically:
```python
import snowflake.connector

# Connect to Snowflake
conn = snowflake.connector.connect(
    user='username',
    password='password',
    account='account_identifier',
    warehouse='compute_wh',
    database='P2P_DATA_WAREHOUSE',
    schema='RAW'
)

cur = conn.cursor()

# Create stage
cur.execute("""
    CREATE STAGE IF NOT EXISTS automated_stage
    FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1)
    COMMENT = 'Created via Python automation'
""")

# List files
cur.execute("LIST @automated_stage")
files = cur.fetchall()
for file in files:
    print(f"File: {file[0]}, Size: {file[1]}")

# Close connection
cur.close()
conn.close()
```

### Upload and Load Data:
```python
import snowflake.connector
import os

conn = snowflake.connector.connect(
    user='username',
    password='password',
    account='account_identifier'
)

cur = conn.cursor()

# Upload file to stage
cur.execute("PUT file://local_data.csv @my_stage AUTO_COMPRESS=TRUE")

# Load data from stage
cur.execute("""
    COPY INTO target_table
    FROM @my_stage/local_data.csv.gz
    FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1)
    ON_ERROR = 'CONTINUE'
""")

# Get load results
results = cur.fetchall()
for row in results:
    print(f"Status: {row[1]}, Rows Loaded: {row[2]}")

cur.close()
conn.close()
```

---

## Common Issues and Solutions

### Issue 1: Access Denied on External Stage
**Error:** "Access denied to path in stage"
**Solution:**
```sql
-- Verify storage integration
DESCRIBE STORAGE INTEGRATION my_integration;

-- Check stage definition
DESCRIBE STAGE my_stage;

-- Verify cloud permissions (AWS IAM, Azure RBAC, GCS IAM)
```

### Issue 2: File Format Mismatch
**Error:** "File format does not match"
**Solution:**
```sql
-- Test file format
SELECT $1, $2, $3
FROM @my_stage (FILE_FORMAT => 'my_format')
LIMIT 10;

-- Update file format
ALTER STAGE my_stage 
SET FILE_FORMAT = (TYPE = 'CSV' FIELD_DELIMITER = '|');
```

### Issue 3: Directory Not Enabled
**Error:** "Directory is not enabled for stage"
**Solution:**
```sql
-- Enable directory
ALTER STAGE my_stage 
SET DIRECTORY = (ENABLE = TRUE);

-- Refresh directory metadata
ALTER STAGE my_stage REFRESH;
```

---

## Cost Optimization

### 1. Clean Up Old Files
```sql
-- Remove files older than 30 days
REMOVE @my_stage PATTERN = '.*/2023/.*';

-- Purge after loading
COPY INTO target_table
FROM @my_stage
PURGE = TRUE;
```

### 2. Compress Files
```sql
-- Enable compression
CREATE STAGE compressed_stage
  FILE_FORMAT = (TYPE = 'CSV' COMPRESSION = 'GZIP');
```

