# Analyze CSN Data Product Files

Write-Host "`n=== CSN Data Product Entity Analysis ===`n" -ForegroundColor Cyan

$files = @(
    'sap-s4com-Supplier-v1.json',
    'sap-s4com-PurchaseOrder-v1.json',
    'sap-s4com-SupplierInvoice-v1.json',
    'sap-s4com-ServiceEntrySheet-v1.json',
    'sap-s4com-PaymentTerms-v1.json',
    'sap-s4com-JournalEntryHeader-v1.json'
)

$totalEntities = 0

foreach($file in $files) {
    if (Test-Path $file) {
        $json = Get-Content $file | ConvertFrom-Json
        $count = $json.definitions.PSObject.Properties.Count
        $totalEntities += $count
        
        Write-Host "$file" -ForegroundColor Yellow
        Write-Host "  Entities: $count" -ForegroundColor Green
        
        # Show first 5 entity names
        $entityNames = $json.definitions.PSObject.Properties.Name | Select-Object -First 5
        Write-Host "  Sample entities:" -ForegroundColor White
        foreach($entity in $entityNames) {
            Write-Host "    - $entity" -ForegroundColor Gray
        }
        Write-Host ""
    }
}

Write-Host "=== SUMMARY ===" -ForegroundColor Cyan
Write-Host "Total Data Products: $($files.Count)" -ForegroundColor Green
Write-Host "Total Entities: $totalEntities" -ForegroundColor Green
Write-Host "Average per Data Product: $([math]::Round($totalEntities / $files.Count, 2))" -ForegroundColor Green
Write-Host ""
