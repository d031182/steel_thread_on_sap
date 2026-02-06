# Add pytest and Python to Windows Defender exclusions
# Run this script as Administrator

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  Adding pytest/Python to Windows Defender Exclusions" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "To run as Administrator:" -ForegroundColor Yellow
    Write-Host "1. Right-click PowerShell" -ForegroundColor Yellow
    Write-Host "2. Select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host "3. Navigate to project: cd c:\Users\D031182\gitrepo\steel_thread_on_sap" -ForegroundColor Yellow
    Write-Host "4. Run: .\scripts\add_pytest_exclusion.ps1" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host "[1/4] Finding Python and pytest paths..." -ForegroundColor Yellow

try {
    # Find pytest path
    $pytestCommand = Get-Command pytest -ErrorAction SilentlyContinue
    if ($pytestCommand) {
        $pytestPath = $pytestCommand.Source
        Write-Host "  [OK] Found pytest: $pytestPath" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] pytest not found in PATH" -ForegroundColor Red
        $pytestPath = $null
    }

    # Find python path
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        $pythonPath = $pythonCommand.Source
        Write-Host "  [OK] Found python: $pythonPath" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL] python not found in PATH" -ForegroundColor Red
        $pythonPath = $null
    }

    # Project directory
    $projectPath = "c:\Users\D031182\gitrepo\steel_thread_on_sap"
    Write-Host "  [OK] Project path: $projectPath" -ForegroundColor Green

} catch {
    $errorMsg = $_.Exception.Message
    Write-Host "  [FAIL] Error finding paths: $errorMsg" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/4] Current Windows Defender exclusions:" -ForegroundColor Yellow
try {
    $currentExclusions = (Get-MpPreference).ExclusionPath
    if ($currentExclusions) {
        foreach ($exclusion in $currentExclusions) {
            Write-Host "  - $exclusion" -ForegroundColor Gray
        }
    } else {
        Write-Host "  (None)" -ForegroundColor Gray
    }
} catch {
    $errorMsg = $_.Exception.Message
    Write-Host "  Could not read current exclusions: $errorMsg" -ForegroundColor Red
}

Write-Host ""
Write-Host "[3/4] Adding exclusions..." -ForegroundColor Yellow

$added = 0
$failed = 0

# Add pytest exclusion
if ($pytestPath) {
    try {
        Add-MpPreference -ExclusionPath $pytestPath -ErrorAction Stop
        Write-Host "  [OK] Added pytest exclusion" -ForegroundColor Green
        $added++
    } catch {
        $errorMsg = $_.Exception.Message
        Write-Host "  [FAIL] Failed to add pytest: $errorMsg" -ForegroundColor Red
        $failed++
    }
}

# Add python exclusion
if ($pythonPath) {
    try {
        Add-MpPreference -ExclusionPath $pythonPath -ErrorAction Stop
        Write-Host "  [OK] Added python exclusion" -ForegroundColor Green
        $added++
    } catch {
        $errorMsg = $_.Exception.Message
        Write-Host "  [FAIL] Failed to add python: $errorMsg" -ForegroundColor Red
        $failed++
    }
}

# Add project directory exclusion (RECOMMENDED)
try {
    Add-MpPreference -ExclusionPath $projectPath -ErrorAction Stop
    Write-Host "  [OK] Added project directory exclusion" -ForegroundColor Green
    $added++
} catch {
    $errorMsg = $_.Exception.Message
    Write-Host "  [FAIL] Failed to add project directory: $errorMsg" -ForegroundColor Red
    $failed++
}

Write-Host ""
Write-Host "[4/4] Verification:" -ForegroundColor Yellow

try {
    $newExclusions = (Get-MpPreference).ExclusionPath
    $count = $newExclusions.Count
    Write-Host "  Total exclusions now: $count" -ForegroundColor Cyan
    
    if ($pytestPath -and ($newExclusions -contains $pytestPath)) {
        Write-Host "  [OK] pytest verified in exclusions" -ForegroundColor Green
    }
    if ($pythonPath -and ($newExclusions -contains $pythonPath)) {
        Write-Host "  [OK] python verified in exclusions" -ForegroundColor Green
    }
    if ($newExclusions -contains $projectPath) {
        Write-Host "  [OK] project directory verified in exclusions" -ForegroundColor Green
    }
} catch {
    $errorMsg = $_.Exception.Message
    Write-Host "  Could not verify exclusions: $errorMsg" -ForegroundColor Red
}

Write-Host ""
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  Summary: Added $added exclusion(s), $failed failed" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

if ($added -gt 0) {
    Write-Host "SUCCESS! You can now run pytest without security popups." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next step: Run your tests" -ForegroundColor Yellow
    Write-Host "  pytest tests/unit/guwu/test_decorators.py -v" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "WARNING: No exclusions were added. Check errors above." -ForegroundColor Yellow
    Write-Host ""
}