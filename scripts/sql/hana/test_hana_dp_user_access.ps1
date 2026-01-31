# ============================================
# Test HANA_DP_USER Data Product Access
# Using: hdbsql CLI
# Purpose: Verify user can access data products
# ============================================

param(
    [Parameter(Mandatory=$false)]
    [string]$Password = ""
)

# Load HANA credentials
$envFile = "default-env.json"
if (-not (Test-Path $envFile)) {
    Write-Host "ERROR: $envFile not found" -ForegroundColor Red
    exit 1
}

$env = Get-Content $envFile | ConvertFrom-Json
$hana = $env.VCAP_SERVICES.hana[0].credentials

$HANA_HOST = $hana.host
$HANA_PORT = $hana.port

# Prompt for password if not provided
if ([string]::IsNullOrEmpty($Password)) {
    $securePassword = Read-Host "Enter password for HANA_DP_USER" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}

Write-Host "=== Testing HANA_DP_USER Access ===" -ForegroundColor Cyan
Write-Host "Host: $HANA_HOST"
Write-Host "Port: $HANA_PORT"
Write-Host "User: HANA_DP_USER"
Write-Host ""

# ============================================
# TEST 1: Connection Test
# ============================================

Write-Host "=== Test 1: Connection ===" -ForegroundColor Yellow

$connectionTest = "SELECT CURRENT_USER, CURRENT_SCHEMA FROM DUMMY;"

$result = hdbsql -n "$HANA_HOST`:$HANA_PORT" -u HANA_DP_USER -p $Password -e -C -a $connectionTest 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "  X Connection failed!" -ForegroundColor Red
    Write-Host $result
    exit 1
}

Write-Host "  OK Connection successful" -ForegroundColor Green
Write-Host $result
Write-Host ""

# ============================================
# TEST 2: List Data Product Schemas
# ============================================

Write-Host "=== Test 2: List Data Product Schemas ===" -ForegroundColor Yellow

$listSchemasSQL = @"
SELECT SCHEMA_NAME, SCHEMA_OWNER, CREATE_TIME 
FROM SYS.SCHEMAS 
WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%' 
ORDER BY CREATE_TIME DESC;
"@

$result = hdbsql -n "$HANA_HOST`:$HANA_PORT" -u HANA_DP_USER -p $Password -e -C -a $listSchemasSQL 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "  X Cannot list schemas (missing CATALOG READ?)" -ForegroundColor Red
    Write-Host $result
} else {
    Write-Host "  OK Can list schemas" -ForegroundColor Green
    Write-Host $result
}

Write-Host ""

# ============================================
# TEST 3: List Virtual Tables
# ============================================

Write-Host "=== Test 3: List Virtual Tables ===" -ForegroundColor Yellow

$listTablesSQL = @"
SELECT SCHEMA_NAME, TABLE_NAME, IS_VIRTUAL 
FROM SYS.TABLES 
WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%' 
AND IS_VIRTUAL = 'TRUE' 
ORDER BY SCHEMA_NAME, TABLE_NAME;
"@

$result = hdbsql -n "$HANA_HOST`:$HANA_PORT" -u HANA_DP_USER -p $Password -e -C -a $listTablesSQL 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "  X Cannot list tables" -ForegroundColor Red
    Write-Host $result
} else {
    Write-Host "  OK Can list virtual tables" -ForegroundColor Green
    Write-Host $result
}

Write-Host ""

# ============================================
# TEST 4: Query Sample Data
# ============================================

Write-Host "=== Test 4: Query Sample Data ===" -ForegroundColor Yellow

# Try to query first found data product
$getFirstTableSQL = @"
SELECT TOP 1 SCHEMA_NAME || '.' || TABLE_NAME AS FULL_TABLE_NAME
FROM SYS.TABLES 
WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%' 
AND IS_VIRTUAL = 'TRUE';
"@

$tableName = hdbsql -n "$HANA_HOST`:$HANA_PORT" -u HANA_DP_USER -p $Password -e -j -quiet $getFirstTableSQL 2>&1 | Select-Object -First 1

if ($tableName -and $tableName -match '\S') {
    $tableName = $tableName.Trim()
    Write-Host "Querying: $tableName" -ForegroundColor Gray
    
    $querySQL = "SELECT TOP 5 * FROM $tableName;"
    
    $result = hdbsql -n "$HANA_HOST`:$HANA_PORT" -u HANA_DP_USER -p $Password -e -C -a $querySQL 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  X Cannot query data (missing SELECT privilege?)" -ForegroundColor Red
        Write-Host $result
    } else {
        Write-Host "  OK Can query data successfully" -ForegroundColor Green
        Write-Host $result
    }
} else {
    Write-Host "  ! No virtual tables found to test" -ForegroundColor Yellow
}

Write-Host ""

# ============================================
# TEST 5: Check Granted Privileges
# ============================================

Write-Host "=== Test 5: My Privileges ===" -ForegroundColor Yellow

$myPrivilegesSQL = @"
SELECT SCHEMA_NAME, PRIVILEGE 
FROM SYS.GRANTED_PRIVILEGES 
WHERE GRANTEE = CURRENT_USER 
AND SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%' 
ORDER BY SCHEMA_NAME;
"@

$result = hdbsql -n "$HANA_HOST`:$HANA_PORT" -u HANA_DP_USER -p $Password -e -C -a $myPrivilegesSQL 2>&1

Write-Host $result
Write-Host ""

# ============================================
# SUMMARY
# ============================================

Write-Host "=== Test Summary ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "If all tests passed:" -ForegroundColor White
Write-Host "  OK HANA_DP_USER can access data products" -ForegroundColor Green
Write-Host "  OK User can list schemas and tables" -ForegroundColor Green
Write-Host "  OK User can query data" -ForegroundColor Green
Write-Host ""
Write-Host "Ready for application development!" -ForegroundColor Green