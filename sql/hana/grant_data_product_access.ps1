# ============================================
# Grant HANA_DP_USER Access to Data Products
# Using: hdbsql CLI
# Execute as: DBADMIN
# ============================================

# Load HANA credentials from default-env.json
$envFile = "default-env.json"
if (-not (Test-Path $envFile)) {
    Write-Host "ERROR: $envFile not found" -ForegroundColor Red
    exit 1
}

$env = Get-Content $envFile | ConvertFrom-Json
$hana = $env.VCAP_SERVICES.hana[0].credentials

$HANA_HOST = $hana.host
$HANA_PORT = $hana.port
$HANA_USER = $hana.user
$HANA_PASSWORD = $hana.password

Write-Host "=== Connecting to HANA Cloud ===" -ForegroundColor Cyan
Write-Host "Host: $HANA_HOST"
Write-Host "Port: $HANA_PORT"
Write-Host "User: $HANA_USER"
Write-Host ""

# ============================================
# STEP 1: Find Data Product Schemas
# ============================================

Write-Host "=== Step 1: Finding Data Product Schemas ===" -ForegroundColor Yellow

$findSchemasSQL = @"
SELECT SCHEMA_NAME FROM SYS.SCHEMAS WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%' ORDER BY SCHEMA_NAME;
"@

Write-Host "Executing discovery query..." -ForegroundColor Gray
$schemas = hdbsql -n "$HANA_HOST`:$HANA_PORT" -u $HANA_USER -p $HANA_PASSWORD -e -C -a -j -quiet $findSchemasSQL 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to connect or query schemas" -ForegroundColor Red
    Write-Host $schemas
    exit 1
}

# Parse schema names from output
$schemaList = @()
$schemas -split "`n" | ForEach-Object {
    $line = $_.Trim()
    if ($line -match '^_SAP_DATAPRODUCT') {
        $schemaList += $line
        Write-Host "  Found: $line" -ForegroundColor Green
    }
}

if ($schemaList.Count -eq 0) {
    Write-Host "WARNING: No data product schemas found!" -ForegroundColor Yellow
    Write-Host "Make sure data products are installed in HANA Cloud Central"
    exit 0
}

Write-Host ""
Write-Host "Found $($schemaList.Count) data product schema(s)" -ForegroundColor Green
Write-Host ""

# ============================================
# STEP 2: Grant Basic Privileges
# ============================================

Write-Host "=== Step 2: Granting Basic Privileges ===" -ForegroundColor Yellow

$basicGrants = @"
GRANT CATALOG READ TO HANA_DP_USER;
GRANT CONNECT TO HANA_DP_USER;
"@

Write-Host "Granting CATALOG READ and CONNECT..." -ForegroundColor Gray
$result = hdbsql -n "$HANA_HOST`:$HANA_PORT" -u $HANA_USER -p $HANA_PASSWORD -e -quiet $basicGrants 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "Note: Basic grants may already exist (this is OK)" -ForegroundColor Yellow
} else {
    Write-Host "  ✓ Basic privileges granted" -ForegroundColor Green
}

Write-Host ""

# ============================================
# STEP 3: Grant SELECT on Each Data Product Schema
# ============================================

Write-Host "=== Step 3: Granting SELECT on Data Product Schemas ===" -ForegroundColor Yellow

$successCount = 0
$failCount = 0

foreach ($schema in $schemaList) {
    Write-Host "Granting SELECT on: $schema" -ForegroundColor Gray
    
    $grantSQL = "GRANT SELECT ON SCHEMA `"$schema`" TO HANA_DP_USER;"
    
    $result = hdbsql -n "$HANA_HOST`:$HANA_PORT" -u $HANA_USER -p $HANA_PASSWORD -e -quiet $grantSQL 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Granted successfully" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "  ! May already be granted or insufficient privileges" -ForegroundColor Yellow
        $failCount++
    }
}

Write-Host ""
Write-Host "=== Grant Summary ===" -ForegroundColor Cyan
Write-Host "  Success: $successCount" -ForegroundColor Green
Write-Host "  Skipped: $failCount (may already exist)" -ForegroundColor Yellow
Write-Host ""

# ============================================
# STEP 4: Verify Grants
# ============================================

Write-Host "=== Step 4: Verifying Grants ===" -ForegroundColor Yellow

$verifySQL = @"
SELECT SCHEMA_NAME, PRIVILEGE FROM SYS.GRANTED_PRIVILEGES 
WHERE GRANTEE = 'HANA_DP_USER' 
AND SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%' 
ORDER BY SCHEMA_NAME;
"@

Write-Host "Checking granted privileges..." -ForegroundColor Gray
$privileges = hdbsql -n "$HANA_HOST`:$HANA_PORT" -u $HANA_USER -p $HANA_PASSWORD -e -C -a $verifySQL

Write-Host ""
Write-Host "=== Granted Privileges ===" -ForegroundColor Cyan
Write-Host $privileges
Write-Host ""

# ============================================
# STEP 5: Test Instructions
# ============================================

Write-Host "=== Next Steps ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test access with:" -ForegroundColor White
Write-Host '  hdbsql -n "' -NoNewline; Write-Host "$HANA_HOST`:$HANA_PORT" -NoNewline -ForegroundColor Yellow; Write-Host '" -u HANA_DP_USER -p "your_password"' 
Write-Host ""
Write-Host "Then run:" -ForegroundColor White
Write-Host "  SELECT SCHEMA_NAME, TABLE_NAME FROM SYS.TABLES WHERE SCHEMA_NAME LIKE '_SAP_DATAPRODUCT%';" -ForegroundColor Yellow
Write-Host ""
Write-Host "✓ Setup complete!" -ForegroundColor Green