# Pytest Windows Setup Guide

**Version**: 1.0  
**Date**: 2026-02-06  
**Purpose**: Complete guide for setting up pytest on Windows with security configurations

---

## Overview

This guide provides step-by-step instructions for configuring pytest on Windows, including security best practices and PowerShell execution policy management. Use this when setting up a new Windows laptop for development.

---

## Prerequisites

- Windows 10/11
- Python 3.10+ installed
- Git for Windows installed
- Administrator access (for initial setup)
- PowerShell 5.1+ or PowerShell Core 7+

---

## Step 1: Verify Python Installation

```powershell
# Check Python version
python --version

# Should show: Python 3.10.x or higher

# Check pip
pip --version
```

---

## Step 2: Configure PowerShell Execution Policy

### Understanding Execution Policies

Windows restricts PowerShell script execution by default for security. We need to configure this properly.

### Check Current Policy

```powershell
# Open PowerShell as Administrator
Get-ExecutionPolicy -List
```

**Expected Output:**
```
Scope            ExecutionPolicy
-----            ---------------
MachinePolicy    Undefined
UserPolicy       Undefined
Process          Undefined
CurrentUser      Undefined
LocalMachine     Restricted  # <- This blocks scripts
```

### Set Secure Policy (Recommended)

```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Confirm when prompted: Y
```

**What This Does:**
- ✅ Allows local scripts you create to run
- ✅ Blocks downloaded scripts unless digitally signed
- ✅ Applies only to your user account (not system-wide)
- ✅ Safer than `Unrestricted` or `Bypass`

### Verify New Policy

```powershell
Get-ExecutionPolicy -Scope CurrentUser
# Should show: RemoteSigned
```

---

## Step 3: Install Pytest and Dependencies

### Create/Activate Virtual Environment (Recommended)

```powershell
# Navigate to project directory
cd c:\Users\[YourUsername]\gitrepo\steel_thread_on_sap

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1
```

**If you get execution policy error:**
```powershell
# Temporary bypass for this session only
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
.\venv\Scripts\Activate.ps1
```

### Install Pytest and Dependencies

```powershell
# Ensure pip is up to date
python -m pip install --upgrade pip

# Install pytest with all plugins
pip install pytest pytest-cov pytest-html pytest-xdist pytest-timeout

# Install project dependencies
pip install -r app/requirements.txt

# Verify installation
pytest --version
```

---

## Step 4: Configure Pytest (pytest.ini)

The project already has a `pytest.ini` file. Verify it contains:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests (fast, isolated)
    integration: Integration tests (module interactions)
    e2e: End-to-end tests (full workflows)
    slow: Tests that take more than 1 second
    fast: Tests that should complete quickly
```

**Verify Configuration:**
```powershell
pytest --version
pytest --markers
```

---

## Step 5: Security: Using the PowerShell Exclusion Script

### What is `add_pytest_exclusion.ps1`?

This script adds pytest to Windows Defender exclusions to prevent performance issues during test execution.

### Location

```
scripts/add_pytest_exclusion.ps1
```

### Review the Script First (Security Best Practice)

```powershell
# Read the script content before running
Get-Content scripts/add_pytest_exclusion.ps1

# OR open in editor
code scripts/add_pytest_exclusion.ps1
```

**What the script does:**
1. Checks if running as Administrator
2. Finds pytest.exe location in virtual environment
3. Adds it to Windows Defender exclusions
4. Verifies the exclusion was added

### Run the Script

```powershell
# Method 1: Run as Administrator from PowerShell
Start-Process powershell -Verb RunAs -ArgumentList "-File scripts/add_pytest_exclusion.ps1"

# Method 2: Right-click script in File Explorer
# → "Run with PowerShell"
# → Click "Yes" on UAC prompt
```

### Verify Exclusion Was Added

```powershell
# Check Windows Defender exclusions
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

**Should include:**
```
C:\Users\[YourUsername]\gitrepo\steel_thread_on_sap\venv\Scripts\pytest.exe
```

---

## Step 6: Verify Pytest Works

### Run Test Suite

```powershell
# Run all tests
pytest

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m fast          # Fast tests only

# Run with coverage
pytest --cov=modules --cov=core

# Run specific module tests
pytest tests/unit/modules/knowledge_graph/
```

### Expected Output

```
============================= test session starts =============================
platform win32 -- Python 3.10.x, pytest-8.x.x
rootdir: c:\Users\...\steel_thread_on_sap
configfile: pytest.ini
plugins: cov-5.x.x, html-4.x.x
collected X items

tests/unit/... PASSED
...

==================== X passed in X.XXs ====================
```

---

## Step 7: Configure Gu Wu (Self-Optimizing Tests)

Gu Wu is already integrated and runs automatically. Verify it's working:

```powershell
# Run pytest (Gu Wu hooks run automatically)
pytest

# Check Gu Wu metrics database
ls tools/guwu/guwu_metrics.db
# Should exist

# View gap analysis report
cat tools/guwu/gap_analysis_report.txt

# Run intelligence dashboard
python -m tests.guwu.intelligence.dashboard

# Get recommendations
python -m tests.guwu.intelligence.recommendations
```

---

## Troubleshooting

### Issue: "pytest: command not found"

**Solution:**
```powershell
# Ensure virtual environment is activated
.\venv\Scripts\Activate.ps1

# Re-install pytest
pip install pytest

# Verify
where.exe pytest
# Should show: C:\...\venv\Scripts\pytest.exe
```

### Issue: PowerShell Execution Policy Blocks Scripts

**Solution:**
```powershell
# Check current policy
Get-ExecutionPolicy -Scope CurrentUser

# Set to RemoteSigned
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# OR for current session only
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
```

### Issue: Windows Defender Slows Down Tests

**Solution:**
```powershell
# Run the exclusion script
Start-Process powershell -Verb RunAs -ArgumentList "-File scripts/add_pytest_exclusion.ps1"

# Verify exclusion
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

### Issue: UnicodeEncodeError on Windows

**Solution:**
This is already handled in Gu Wu intelligence modules with UTF-8 encoding:

```python
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

If you encounter this elsewhere, add this to the script.

### Issue: Tests Run Slowly

**Solutions:**
```powershell
# 1. Add Windows Defender exclusion (see Step 5)

# 2. Run tests in parallel
pip install pytest-xdist
pytest -n auto  # Uses all CPU cores

# 3. Run only fast tests during development
pytest -m fast

# 4. Check Gu Wu insights for slow tests
python -m tests.guwu.intelligence.recommendations
```

---

## New Laptop Setup Checklist

Use this checklist when setting up pytest on a new Windows laptop:

### [ ] Step 1: Install Prerequisites
- [ ] Install Python 3.10+
- [ ] Install Git for Windows
- [ ] Install VS Code (optional)

### [ ] Step 2: Configure PowerShell
- [ ] Check current execution policy: `Get-ExecutionPolicy -List`
- [ ] Set policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- [ ] Verify: `Get-ExecutionPolicy -Scope CurrentUser`

### [ ] Step 3: Clone Repository
```powershell
cd c:\Users\[YourUsername]\gitrepo
git clone https://github.com/d031182/steel_thread_on_sap.git
cd steel_thread_on_sap
```

### [ ] Step 4: Create Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### [ ] Step 5: Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install pytest pytest-cov pytest-html pytest-xdist pytest-timeout
pip install -r app/requirements.txt
```

### [ ] Step 6: Verify Pytest
```powershell
pytest --version
pytest --markers
```

### [ ] Step 7: Add Windows Defender Exclusion
```powershell
# Review script first
Get-Content scripts/add_pytest_exclusion.ps1

# Run as Administrator
Start-Process powershell -Verb RunAs -ArgumentList "-File scripts/add_pytest_exclusion.ps1"

# Verify
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
```

### [ ] Step 8: Run Test Suite
```powershell
pytest
```

### [ ] Step 9: Verify Gu Wu
```powershell
python -m tests.guwu.intelligence.dashboard
```

### [ ] Step 10: Configure VS Code (Optional)
- [ ] Install Python extension
- [ ] Install Pytest extension
- [ ] Configure settings.json with pytest path

---

## Security Best Practices

### 1. Execution Policy
- ✅ **Use**: `RemoteSigned` (recommended)
- ❌ **Avoid**: `Unrestricted` or `Bypass` (system-wide)
- ✅ **OK for session**: `Bypass -Scope Process` (temporary)

### 2. Windows Defender Exclusions
- ✅ **Only exclude**: Specific pytest.exe path
- ❌ **Don't exclude**: Entire project directory
- ✅ **Review**: Exclusions periodically

### 3. Virtual Environments
- ✅ **Always use**: Virtual environments for isolation
- ❌ **Don't install**: System-wide unless necessary
- ✅ **Separate**: Different projects in different venvs

### 4. Script Review
- ✅ **Always review**: PowerShell scripts before running
- ✅ **Use**: `Get-Content` to read scripts
- ✅ **Verify**: Script source and purpose

---

## Reference Links

- [[Gu Wu Testing Framework]] - Gu Wu overview
- [[Comprehensive Testing Strategy]] - Testing standards
- [[Windows Encoding Standard]] - UTF-8 handling on Windows
- `tests/README.md` - Project-specific testing guide
- `pytest.ini` - Pytest configuration
- `scripts/add_pytest_exclusion.ps1` - Windows Defender script

---

## Quick Command Reference

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Run all tests
pytest

# Run with coverage
pytest --cov=modules --cov=core

# Run specific markers
pytest -m unit
pytest -m integration
pytest -m fast

# Run in parallel
pytest -n auto

# Gu Wu intelligence
python -m tests.guwu.intelligence.dashboard
python -m tests.guwu.intelligence.recommendations
python -m tests.guwu.intelligence.predictive

# Check exclusions
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath

# Check execution policy
Get-ExecutionPolicy -Scope CurrentUser
```

---

**Last Updated**: 2026-02-06  
**Author**: AI Development Standards  
**Maintained By**: Project Team