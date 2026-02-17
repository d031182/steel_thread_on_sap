# PowerShell script to rename log → logger directories
# Run this with: powershell -ExecutionPolicy Bypass -File scripts/rename_directories.ps1

$ErrorActionPreference = "Stop"

Write-Host "Renaming log → logger directories..." -ForegroundColor Cyan

# Change to project root
Set-Location "C:\Users\D031182\gitrepo\steel_thread_on_sap"

# Check if old directories exist
if (Test-Path "modules\log") {
    Write-Host "✓ Found modules\log" -ForegroundColor Green
    
    # Remove logger if it exists (shouldn't but just in case)
    if (Test-Path "modules\logger") {
        Write-Host "⚠ Removing existing modules\logger" -ForegroundColor Yellow
        Remove-Item "modules\logger" -Recurse -Force
    }
    
    # Rename modules/log → modules/logger
    Rename-Item -Path "modules\log" -NewName "logger" -Force
    Write-Host "✓ Renamed modules\log → modules\logger" -ForegroundColor Green
} else {
    Write-Host "⚠ modules\log not found (already renamed?)" -ForegroundColor Yellow
}

if (Test-Path "tests\log") {
    Write-Host "✓ Found tests\log" -ForegroundColor Green
    
    # Remove logger if it exists
    if (Test-Path "tests\logger") {
        Write-Host "⚠ Removing existing tests\logger" -ForegroundColor Yellow
        Remove-Item "tests\logger" -Recurse -Force
    }
    
    # Rename tests/log → tests/logger
    Rename-Item -Path "tests\log" -NewName "logger" -Force
    Write-Host "✓ Renamed tests\log → tests\logger" -ForegroundColor Green
} else {
    Write-Host "⚠ tests\log not found (already renamed?)" -ForegroundColor Yellow
}

Write-Host "`n✅ Renaming complete!" -ForegroundColor Green
Write-Host "`nNext: Let Cline know you've completed the renaming" -ForegroundColor Cyan