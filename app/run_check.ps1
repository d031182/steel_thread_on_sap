# Load environment and check schema tables
$envFile = Join-Path $PSScriptRoot "..\default-env.json"
$config = Get-Content $envFile | ConvertFrom-Json
$creds = $config.VCAP_SERVICES.hana[0].credentials

$env:HANA_HOST = $creds.host
$env:HANA_PORT = $creds.port
$env:HANA_USER = $creds.user
$env:HANA_PASSWORD = $creds.password

python (Join-Path $PSScriptRoot "check_schema_tables.py")