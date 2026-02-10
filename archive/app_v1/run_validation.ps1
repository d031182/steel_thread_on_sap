# Load environment from default-env.json and run validation
param(
    [Parameter(Mandatory=$true)]
    [string]$ProductName
)

# Load default-env.json
$envFile = Join-Path $PSScriptRoot "..\default-env.json"
if (Test-Path $envFile) {
    $config = Get-Content $envFile | ConvertFrom-Json
    
    # Extract HANA credentials from VCAP_SERVICES
    if ($config.VCAP_SERVICES.hana -and $config.VCAP_SERVICES.hana[0].credentials) {
        $creds = $config.VCAP_SERVICES.hana[0].credentials
        
        # Set environment variables
        $env:HANA_HOST = $creds.host
        $env:HANA_PORT = $creds.port
        $env:HANA_USER = $creds.user
        $env:HANA_PASSWORD = $creds.password
        $env:HANA_SCHEMA = $creds.schema
        
        Write-Host "Environment loaded from default-env.json" -ForegroundColor Green
        Write-Host "  HANA_HOST: $env:HANA_HOST" -ForegroundColor Cyan
        Write-Host "  HANA_USER: $env:HANA_USER" -ForegroundColor Cyan
    }
    else {
        Write-Host "No HANA credentials found in default-env.json" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "default-env.json not found" -ForegroundColor Red
    exit 1
}

# Run validation
$scriptPath = Join-Path $PSScriptRoot "validate_csn_against_hana.py"
python $scriptPath $ProductName