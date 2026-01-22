# Script to retrieve entity counts from SAP Data Products
# This script fetches data product APIs and counts entities programmatically

param(
    [string]$DataProductName = "",
    [switch]$ListAll = $false,
    [int]$MaxProducts = 10
)

# Function to extract entity names from API Reference HTML
function Get-EntityDefinitions {
    param(
        [string]$HtmlContent
    )
    
    $entities = @()
    
    # Look for entity definition headers in the HTML
    # Pattern: <h3>EntityName</h3> or class names containing entity definitions
    $entityPattern = '<h3[^>]*>([^<]+)</h3>|class="entity-name[^"]*">([^<]+)<'
    
    $matches = [regex]::Matches($HtmlContent, $entityPattern)
    
    foreach ($match in $matches) {
        $entityName = if ($match.Groups[1].Success) { 
            $match.Groups[1].Value 
        } else { 
            $match.Groups[2].Value 
        }
        
        # Filter out common HTML headers that aren't entities
        if ($entityName -and 
            $entityName -notmatch '^(Introduction|Overview|API Reference|Entity Definitions|Elements|Description)$' -and
            $entityName -match '^[A-Z]') {
            $entities += $entityName
        }
    }
    
    # Alternative pattern: Look for entity definitions in JSON-like structures
    $jsonPattern = '"@odata\.type"\s*:\s*"[^"]*\.([A-Z][a-zA-Z0-9_]+)"'
    $jsonMatches = [regex]::Matches($HtmlContent, $jsonPattern)
    
    foreach ($match in $jsonMatches) {
        $entityName = $match.Groups[1].Value
        if ($entityName -and $entities -notcontains $entityName) {
            $entities += $entityName
        }
    }
    
    # Most reliable: Look for the actual entity definition pattern in CSN
    # Pattern: entity name followed by element definitions
    $csnPattern = '(?ms)^([A-Z][a-zA-Z0-9_]+)\s*$.*?abapOriginalName:'
    $csnMatches = [regex]::Matches($HtmlContent, $csnPattern)
    
    foreach ($match in $csnMatches) {
        $entityName = $match.Groups[1].Value.Trim()
        if ($entityName -and $entities -notcontains $entityName -and $entityName.Length -lt 50) {
            $entities += $entityName
        }
    }
    
    return $entities | Select-Object -Unique
}

# Function to fetch data product list
function Get-DataProductList {
    Write-Host "Fetching data product list from SAP Business Accelerator Hub..." -ForegroundColor Cyan
    
    try {
        $url = "https://api.sap.com/dataproducts"
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing -ErrorAction Stop
        
        # Extract data product links
        $linkPattern = 'href="(/dataproducts/[^"]+)"[^>]*>([^<]+)</a>'
        $matches = [regex]::Matches($response.Content, $linkPattern)
        
        $products = @()
        foreach ($match in $matches) {
            $link = $match.Groups[1].Value
            $name = $match.Groups[2].Value.Trim()
            
            if ($name -and $name -notmatch '^(Data Products|Overview|API)$') {
                $products += [PSCustomObject]@{
                    Name = $name
                    Link = "https://api.sap.com$link"
                }
            }
        }
        
        return $products | Select-Object -Unique Name, Link
    }
    catch {
        Write-Error "Failed to fetch data product list: $_"
        return @()
    }
}

# Function to analyze a specific data product
function Analyze-DataProduct {
    param(
        [string]$ProductUrl,
        [string]$ProductName
    )
    
    Write-Host "`nAnalyzing: $ProductName" -ForegroundColor Yellow
    Write-Host "URL: $ProductUrl" -ForegroundColor Gray
    
    try {
        # Get the data product overview page
        $response = Invoke-WebRequest -Uri $ProductUrl -UseBasicParsing -ErrorAction Stop
        
        # Look for API links in Output Ports
        $apiPattern = 'href="(/dataproducts/[^"]+/api[^"]*)"'
        $apiMatches = [regex]::Matches($response.Content, $apiPattern)
        
        if ($apiMatches.Count -eq 0) {
            Write-Host "  No APIs found" -ForegroundColor Red
            return [PSCustomObject]@{
                DataProduct = $ProductName
                EntityCount = 0
                Entities = @()
                Status = "No APIs"
            }
        }
        
        Write-Host "  Found $($apiMatches.Count) API(s)" -ForegroundColor Green
        
        $allEntities = @()
        
        foreach ($apiMatch in $apiMatches | Select-Object -First 1) {
            $apiUrl = "https://api.sap.com" + $apiMatch.Groups[1].Value
            
            Write-Host "  Fetching API Reference from: $apiUrl" -ForegroundColor Gray
            
            try {
                $apiResponse = Invoke-WebRequest -Uri $apiUrl -UseBasicParsing -ErrorAction Stop
                
                # Extract entities from the API reference page
                $entities = Get-EntityDefinitions -HtmlContent $apiResponse.Content
                
                if ($entities.Count -gt 0) {
                    $allEntities += $entities
                    Write-Host "  Found entities: $($entities -join ', ')" -ForegroundColor Green
                }
                else {
                    Write-Host "  No entities found in API response" -ForegroundColor Yellow
                }
            }
            catch {
                Write-Warning "  Failed to fetch API: $_"
            }
        }
        
        $uniqueEntities = $allEntities | Select-Object -Unique
        
        return [PSCustomObject]@{
            DataProduct = $ProductName
            EntityCount = $uniqueEntities.Count
            Entities = $uniqueEntities
            Status = "Success"
        }
    }
    catch {
        Write-Error "Failed to analyze $ProductName : $_"
        return [PSCustomObject]@{
            DataProduct = $ProductName
            EntityCount = 0
            Entities = @()
            Status = "Error: $_"
        }
    }
}

# Main execution
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host "SAP Data Product Entity Counter" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

if ($ListAll) {
    # Get all data products
    $products = Get-DataProductList
    
    if ($products.Count -eq 0) {
        Write-Error "No data products found"
        exit 1
    }
    
    Write-Host "Found $($products.Count) data products`n" -ForegroundColor Green
    
    # Analyze each product (limited by MaxProducts)
    $results = @()
    $count = 0
    
    foreach ($product in $products) {
        if ($count -ge $MaxProducts) {
            Write-Host "`nReached maximum product limit ($MaxProducts)" -ForegroundColor Yellow
            break
        }
        
        $result = Analyze-DataProduct -ProductUrl $product.Link -ProductName $product.Name
        $results += $result
        $count++
        
        Start-Sleep -Seconds 1  # Be nice to the server
    }
    
    # Summary
    Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
    Write-Host "SUMMARY" -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    
    $results | Format-Table -Property DataProduct, EntityCount, Status -AutoSize
    
    Write-Host "`nEntity Distribution:" -ForegroundColor Yellow
    $results | Group-Object EntityCount | Sort-Object Name | ForEach-Object {
        Write-Host "  $($_.Name) entity/entities: $($_.Count) data products" -ForegroundColor White
    }
    
    # Export detailed results
    $outputFile = "data_product_entities_analysis.csv"
    $results | Export-Csv -Path $outputFile -NoTypeInformation
    Write-Host "`nDetailed results exported to: $outputFile" -ForegroundColor Green
    
    # Show examples of multi-entity products
    $multiEntity = $results | Where-Object { $_.EntityCount -gt 1 }
    if ($multiEntity.Count -gt 0) {
        Write-Host "`nData Products with Multiple Entities:" -ForegroundColor Yellow
        foreach ($product in $multiEntity) {
            Write-Host "  - $($product.DataProduct): $($product.EntityCount) entities" -ForegroundColor Cyan
            Write-Host "    Entities: $($product.Entities -join ', ')" -ForegroundColor Gray
        }
    }
}
elseif ($DataProductName) {
    # Analyze specific data product
    $products = Get-DataProductList
    $product = $products | Where-Object { $_.Name -like "*$DataProductName*" } | Select-Object -First 1
    
    if (-not $product) {
        Write-Error "Data product '$DataProductName' not found"
        Write-Host "`nAvailable data products (first 20):" -ForegroundColor Yellow
        $products | Select-Object -First 20 | ForEach-Object {
            Write-Host "  - $($_.Name)"
        }
        exit 1
    }
    
    $result = Analyze-DataProduct -ProductUrl $product.Link -ProductName $product.Name
    
    Write-Host "`n" + ("=" * 80) -ForegroundColor Cyan
    Write-Host "RESULT" -ForegroundColor Cyan
    Write-Host ("=" * 80) -ForegroundColor Cyan
    Write-Host "Data Product: $($result.DataProduct)" -ForegroundColor White
    Write-Host "Entity Count: $($result.EntityCount)" -ForegroundColor $(if ($result.EntityCount -gt 1) { "Yellow" } else { "Green" })
    Write-Host "Entities:" -ForegroundColor White
    foreach ($entity in $result.Entities) {
        Write-Host "  - $entity" -ForegroundColor Cyan
    }
}
else {
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\Get-DataProductEntities.ps1 -ListAll -MaxProducts 10" -ForegroundColor White
    Write-Host "    Analyze first 10 data products and show statistics`n" -ForegroundColor Gray
    
    Write-Host "  .\Get-DataProductEntities.ps1 -DataProductName 'Cash Flow'" -ForegroundColor White
    Write-Host "    Analyze a specific data product`n" -ForegroundColor Gray
    
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\Get-DataProductEntities.ps1 -ListAll -MaxProducts 20" -ForegroundColor Cyan
    Write-Host "  .\Get-DataProductEntities.ps1 -DataProductName 'Cash Flow'" -ForegroundColor Cyan
    Write-Host "  .\Get-DataProductEntities.ps1 -DataProductName 'Customer'" -ForegroundColor Cyan
}

Write-Host ""
