FENG SHUI PRE-COMMIT VALIDATION
[1/2] File Organization Check...        # < 1 second
[2/2] Critical Security Check...         # < 1 second

✅ Pre-commit validation passed!
```

If violations are found, the commit is **blocked** and you must fix the issues first.
# Feng Shui + Gu Wu Intelligent Pre-Commit Hook Documentation

**Purpose**: Automated 5-tier quality gate that validates code, runs tests, and detects gaps before allowing commits  
**Speed**: < 25 seconds (typically 12-18s)  
**Philosophy**: "Prevent violations and catch bugs at commit time with intelligent analysis"  

Related: [[Feng Shui Phase 4-17]], [[Gu Wu Testing Framework]], [[Feng Shui + Gu Wu Pre-Commit Integration]]

---

## Overview

The pre-commit hook is now an **Intelligent 5-Tier Validation System** combining Feng Shui's architecture intelligence with Gu Wu's test execution:

- **Tier 1**: File Organization (< 1s) - File structure validation
- **Tier 2**: Critical Security (< 1s) - Hardcoded secrets, SQL injection detection
- **Tier 3**: Gu Wu Test Execution (< 10s) ⭐ **NEW** - Automated unit test running
- **Tier 4**: Feng Shui Orchestrator (< 10s) ⭐ **NEW** - 6-agent architecture analysis
- **Tier 5**: Test Gap Detection (< 2s) ⭐ **NEW** - Coverage gap identification

**Total**: < 25 seconds (typically 12-18s depending on file count)

---

## What Happens When You Commit

When you run `git commit`, the hook automatically runs **5 validation tiers**:

```bash
FENG SHUI + GU WU INTELLIGENT PRE-COMMIT VALIDATION
[1/5] File Organization Check...        # < 1 second
[2/5] Critical Security Check...         # < 1 second
[3/5] Gu Wu Test Execution...            # < 10 seconds ⭐ NEW
[4/5] Feng Shui Orchestrator Analysis... # < 10 seconds ⭐ NEW
[5/5] Test Coverage Gap Detection...     # < 2 seconds ⭐ NEW

✅ Pre-commit validation passed!
```

**What Gets Blocked**:
- File organization violations (Tier 1)
- Critical security issues (Tier 2)
- **Test failures** (Tier 3) ⭐ NEW
- **Critical architecture violations** (Tier 4) ⭐ NEW

**What Are Warnings Only**:
- Test coverage gaps (Tier 5) - Logged but don't block commits
- Architecture warnings (MEDIUM severity)

============================================================
FENG SHUI PRE-COMMIT VALIDATION
============================================================
[1/2] File Organization Check...        # < 1 second
[2/2] Critical Security Check...         # < 1 second

✅ Pre-commit validation passed!
============================================================
```

If violations are found, the commit is **blocked** and you must fix the issues first.

---

## Tier 3: Gu Wu Test Execution ⭐ NEW

**Purpose**: Automatically run tests for staged files  
**Speed**: < 10 seconds (unit tests only)  
**Tool**: `tools/guwu/pre_commit_test_runner.py`

### How It Works

1. **Detects staged Python files** via `git diff --cached`
2. **Discovers related tests** automatically:
   - `modules/data_products_v2/backend/api.py` → `tests/unit/modules/data_products_v2/test_api.py`
   - `core/services/module_loader.py` → `tests/unit/core/services/test_module_loader.py`
   - `tools/fengshui/agents/architect_agent.py` → `tests/unit/tools/fengshui/test_architect_agent.py`
3. **Runs pytest** with 10s timeout (unit tests only for speed)
4. **Parses results** and shows clear pass/fail status

### Example Output

**✅ All Tests Pass**:
```
[GU WU] Pre-Commit Test Execution
[>] Staged files: 3 Python file(s)
[>] Affected tests: 12 test file(s)

[OK] 12/12 tests passed (4.2s)
```

**❌ Tests Fail**:
```
[GU WU] Pre-Commit Test Execution
[>] Staged files: 3 Python file(s)
[>] Affected tests: 12 test file(s)

[X] TESTS FAILED
[RESULT] 10/12 tests passed (6.5s)

[FAILED TESTS]
  • tests/unit/modules/data_products_v2/test_api.py::test_create_product
    → AssertionError: Expected 200, got 500
  • tests/unit/core/services/test_module_loader.py::test_load_module
    → ModuleNotFoundError: No module named 'missing_dependency'

[FIX] Fix failing tests before committing:
   1. Run: pytest tests/unit/modules/data_products_v2/test_api.py -v
   2. Debug and fix issues
   3. Verify: python run_tests.py
   4. Commit again

[!] To bypass (NOT RECOMMENDED): git commit --no-verify
```

### Performance Limits

- **Max Files**: 20 staged Python files
- **Test Timeout**: 10 seconds
- **Auto-Skip**: If >20 files staged, skips test execution (run manually instead)

### Configuration

```bash
# Disable test execution
PRECOMMIT_RUN_TESTS=false git commit -m "Skip tests"

# Adjust timeout
PRECOMMIT_TEST_TIMEOUT=20 git commit -m "Longer timeout"
```

---

## Tier 4: Feng Shui Orchestrator ⭐ NEW

**Purpose**: Multi-agent architecture and security analysis  
**Speed**: < 10 seconds (6 agents in parallel)  
**Tool**: `tools/fengshui/pre_commit_orchestrator.py`

### The 6 Specialized Agents

1. **ArchitectAgent**: DI violations, Service Locator antipatterns, SOLID principles
2. **SecurityAgent**: Hardcoded secrets (deeper than Tier 2), SQL injection, auth issues
3. **PerformanceAgent**: N+1 queries, nested loops, caching opportunities
4. **UXArchitectAgent**: SAP Fiori compliance, UI/UX patterns
5. **FileOrganizationAgent**: File structure violations, misplaced files
6. **DocumentationAgent**: Docstring quality, comment coverage

### Example Output

**✅ No Critical Issues**:
```
[FENG SHUI] Orchestrator Analysis
[>] Analyzing 3 staged file(s)...

ArchitectAgent:    ✅ No DI violations
SecurityAgent:     ✅ No issues
PerformanceAgent:  ✅ No issues
UXArchitectAgent:  ✅ No issues
FileOrgAgent:      ✅ No issues
DocumentationAgent: ⚠️  1 warning

[!] WARNINGS DETECTED - Consider addressing
[INFO] Warnings don't block commit, but address when possible

[OK] No critical issues detected!
```

**❌ Critical Issues Found**:
```
[FENG SHUI] Orchestrator Analysis
[>] Analyzing 3 staged file(s)...

ArchitectAgent:    🔴 2 CRITICAL issue(s)
SecurityAgent:     🔴 1 CRITICAL issue(s)
PerformanceAgent:  ✅ No issues
UXArchitectAgent:  ⚠️  1 warning
FileOrgAgent:      ✅ No issues
DocumentationAgent: ✅ No issues

[X] CRITICAL ISSUES FOUND - Cannot commit
[FIX] Address critical issues above before committing
[!] To bypass (DANGEROUS): git commit --no-verify
```

### Performance Limits

- **Max Files**: 20 staged Python files
- **Agent Timeout**: 10 seconds total (parallel execution)
- **Auto-Skip**: If >20 files staged, skips orchestrator (run manually)

### Configuration

```bash
# Disable orchestrator
PRECOMMIT_RUN_ORCHESTRATOR=false git commit -m "Skip architecture check"
```

---

## Tier 5: Test Gap Detection ⭐ NEW

**Purpose**: Identify missing test coverage for staged files  
**Speed**: < 2 seconds (AST parsing)  
**Tool**: Feng Shui orchestrator generates `.fengshui_test_gaps.json`

### How It Works

1. **Parses staged files** using Python AST
2. **Counts functions/classes** in each file
3. **Checks for test file existence**
4. **Generates gap report** with recommendations
5. **Displays summary** (non-blocking)

### Example Output

```
[GU WU] Test Coverage Gaps Report
[GENERATED] 2026-02-09 10:03:00 UTC
[CONTEXT] 3 staged file(s)

[SUMMARY]
  Total Gaps: 2
  High Severity: 1
  Medium Severity: 1
  Low Severity: 0

[🔴 HIGH PRIORITY GAPS]
🔴 Gap #1: modules/new_feature/backend/service.py
   Type: missing_test_file
   Details: 5 function(s)/class(es) have no tests
   Recommendation: Create tests/unit/modules/new_feature/test_service.py

[⚠️  MEDIUM PRIORITY GAPS]
⚠️  Gap #2: modules/data_products_v2/backend/api.py
   Type: coverage_check_needed
   Details: 8 function(s)/class(es) - verify test coverage
   Recommendation: Review tests/unit/modules/data_products_v2/test_api.py

[REPORT] 2 test gap(s) detected
Gaps saved to: .fengshui_test_gaps.json

[NEXT ACTIONS]
1. Review gaps above and prioritize HIGH severity first
2. Create missing test files using Gu Wu generator:
   python -m tools.guwu.generators.test_generator <source_file>
3. Run tests to verify: pytest tests/unit/...
4. Commit again to re-validate

[TIP] Use --auto-generate flag to create test stubs automatically
```

### Gap Report File

**Location**: `.fengshui_test_gaps.json` (auto-generated, git-ignored)

**View Gaps Manually**:
```bash
# View all gaps
python -m tools.guwu.test_gap_display

# View all gaps including low priority
python -m tools.guwu.test_gap_display -v

# Auto-generate test stubs
python -m tools.guwu.test_gap_display --auto-generate
```

### Configuration

```bash
# Disable gap detection
PRECOMMIT_DETECT_GAPS=false git commit -m "Skip gap detection"
```

---

## Tier 1 & 2: File Organization + Critical Security

**(Documentation for these tiers remains unchanged - see sections below)**

---

## Check 1: File Organization (`pre_commit_check.py`)

**Purpose**: Enforce project file structure standards  
**Speed**: < 1 second  
**What it checks**:

### 1.1 Root Markdown Files

**Rule**: Only specific `.md` files allowed in project root

**Allowed Root Files**:
```
.clinerules
PROJECT_TRACKER.md
README.md
.gitignore
package.json
requirements.txt
setup.py
pyproject.toml
pytest.ini
conftest.py
server.py
playwright.config.js
```

**Violation Example**:
```
[X] my_notes.md: Markdown file not allowed in root
   -> Move to docs/knowledge/ or delete
```

**Why**: Keeps project root clean and organized. All documentation belongs in `docs/knowledge/`.

---

### 1.2 Test File Locations

**Rule**: Test files must be in `tests/` directory, NOT in `scripts/python/`

**Violations Detected**:
- Files starting with `test_`
- Files ending with `_test.py`
- Files starting with `check_` or `verify_`

**Violation Example**:
```
[X] scripts/python/test_something.py: Test/validation file in wrong location
   -> Move to tests/integration/ or tests/unit/
   -> See .clinerules Section 6 (Gu Wu Testing)
```

**Why**: Test files belong in `tests/` for proper organization and test discovery.

---

### 1.3 Documentation Location

**Rule**: Documentation files in `docs/` must be in `docs/knowledge/` subdirectory

**Allowed Locations**:
- `docs/knowledge/` ✅ (knowledge vault)
- `docs/archive/` ✅ (archived trackers)
- Specific audit files: `docs/FENG_SHUI_AUDIT_*.md` ✅

**Violation Example**:
```
[X] docs/my_doc.md: Documentation file in wrong location
   -> Move to docs/knowledge/ (see knowledge vault structure)
```

**Why**: Enforces knowledge vault structure for easy discovery and maintenance.

---

### 1.4 Temporary Files

**Rule**: Temporary/debug files should never be committed

**Violations Detected**:
- Files starting with `temp_`
- Files starting with `debug_`
- Files containing `_old`
- Files ending with `.bak` or `~`

**Violation Example**:
```
[X] temp_test.py: Temporary/backup file should not be committed
   -> Delete or add to .gitignore
```

**Why**: Temporary files clutter repository and aren't meant to be version controlled.

---

## Check 2: Critical Security (`critical_check.py`)

**Purpose**: Detect CRITICAL security issues in Python files  
**Speed**: < 1 second (regex-based pattern matching)  
**Files Scanned**: Only staged `.py` files

### 2.1 Security Patterns Detected

#### 🔴 Hardcoded Password
```python
# VIOLATION:
password = "mySecretPass123"

# CORRECT:
password = os.getenv('DATABASE_PASSWORD')
```

#### 🔴 Hardcoded API Key
```python
# VIOLATION:
api_key = "sk-1234567890abcdef"

# CORRECT:
api_key = os.getenv('OPENAI_API_KEY')
```

#### 🔴 Hardcoded Secret
```python
# VIOLATION:
secret = "my-secret-token-12345"

# CORRECT:
secret = os.getenv('JWT_SECRET')
```

#### 🔴 SQL Injection
```python
# VIOLATION:
cursor.execute("SELECT * FROM users WHERE id = %s" % user_id)

# CORRECT:
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
```

#### 🔴 Command Injection
```python
# VIOLATION:
os.system("ls " + user_input)

# CORRECT:
subprocess.run(["ls", user_input], check=True)
```

#### 🔴 Code Injection
```python
# VIOLATION:
eval(input("Enter code: "))

# CORRECT:
# Never use eval() with user input!
```

---

### 2.2 Security Check Output

When violations are found:

```
[X] CRITICAL SECURITY ISSUES FOUND
============================================================

📄 modules/example/backend/api.py
   Line 42: Hardcoded password detected
   → password = "supersecret123"

============================================================
[!] CANNOT COMMIT - Fix security issues first

[FIX] How to fix:
   1. Move secrets to environment variables (.env)
   2. Use parameterized queries (not string formatting)
   3. Avoid eval() with user input
   4. Review and fix issues above

[!] To bypass (DANGEROUS!): git commit --no-verify
============================================================
```

---

## Bypassing the Hook

**Command**: `git commit --no-verify`

**When to use**:
- ⚠️ Emergency hotfix deployment
- ⚠️ You've confirmed violations are false positives

**When NOT to use**:
- ❌ "I don't want to fix the violations"
- ❌ "I'm in a hurry"
- ❌ "The hook is annoying"

**Philosophy**: The hook exists to protect code quality and security. Bypassing should be rare and intentional.

---

## How to Fix Violations

### Quick Fix Workflow

```bash
# 1. See what violations exist
git commit -m "Your message"

# 2. Fix violations manually or use autofix (if available)
python tools/fengshui/autofix.py

# 3. Stage fixed files
git add <files>

# 4. Commit again
git commit -m "Your message"
```

---

## Integration with Development Workflow

### Before Committing (Best Practice)

1. **Stage your changes**: `git add <files>`
2. **Run manual check** (optional): `python tools/fengshui/pre_commit_check.py`
3. **Commit**: `git commit -m "Your message"`
4. **Hook runs automatically** ✅

### After Hook Blocks Commit

1. **Read violation messages carefully**
2. **Fix issues** (move files, remove secrets, etc.)
3. **Stage fixes**: `git add <files>`
4. **Commit again**: `git commit -m "Your message"`

---

## Technical Details

### Hook Location
`.git/hooks/pre-commit` (Bash script)

### Python Scripts
- `tools/fengshui/pre_commit_check.py` - File organization validation
- `tools/fengshui/critical_check.py` - Security pattern detection

### Exit Codes
- `0` = All checks passed (commit allowed)
- `1` = Violations found (commit blocked)

### Performance
- **File Organization Check**: < 1 second
- **Security Check**: < 1 second (regex-only, no AST parsing)
- **Total**: < 2 seconds

---

## Common Scenarios

### Scenario 1: Adding a New Markdown Document

**Wrong**:
```bash
git add my_notes.md                    # Root level
git commit -m "Add notes"              # ❌ BLOCKED
```

**Correct**:
```bash
mv my_notes.md docs/knowledge/
git add docs/knowledge/my_notes.md     # Knowledge vault
git commit -m "docs: Add notes"        # ✅ PASSES
```

---

### Scenario 2: Adding Test File in Wrong Location

**Wrong**:
```bash
git add scripts/python/test_api.py     # Wrong location
git commit -m "Add test"               # ❌ BLOCKED
```

**Correct**:
```bash
mv scripts/python/test_api.py tests/unit/
git add tests/unit/test_api.py         # Correct location
git commit -m "test: Add API test"     # ✅ PASSES
```

---

### Scenario 3: Committing with Hardcoded Secret

**Wrong**:
```python
# api.py
api_key = "sk-1234567890"              # Hardcoded
```

```bash
git add api.py
git commit -m "Add API integration"    # ❌ BLOCKED
```

**Correct**:
```python
# api.py
import os
api_key = os.getenv('API_KEY')         # Environment variable
```

```bash
git add api.py
git commit -m "Add API integration"    # ✅ PASSES
```

---

## Relationship to Other Quality Gates

### Pre-Commit vs Pre-Push

**Pre-Commit** (This Hook):
- ⚡ Fast (< 2s)
- 🎯 File organization + Critical security
- 🚫 Blocks commits
- 💡 Catches obvious issues early

**Pre-Push** ([[Three-Tier Quality Gate System]]):
- 🐢 Medium (< 30s)
- 🎯 Architecture + Deeper analysis
- 🚫 Blocks pushes
- 💡 Catches architectural issues

**Manual Quality Gate**:
- 🐌 Slow (minutes)
- 🎯 Full Feng Shui analysis with all agents
- 📊 Informational (doesn't block)
- 💡 Comprehensive code review

---

## Configuration

### Modifying Allowed Root Files

Edit `tools/fengshui/pre_commit_check.py`:

```python
ALLOWED_ROOT_FILES = {
    '.clinerules',
    'PROJECT_TRACKER.md',
    'README.md',
    # Add your file here
}
```

### Adding New Security Patterns

Edit `tools/fengshui/critical_check.py`:

```python
CRITICAL_PATTERNS = {
    'your_pattern': {
        'pattern': r'your_regex_here',
        'message': 'Description of violation',
        'severity': 'CRITICAL'
    }
}
```

---

## Troubleshooting

### Hook Not Running

**Symptom**: Commits succeed without running hook

**Fix**:
```bash
# Check if hook exists and is executable
ls -la .git/hooks/pre-commit

# Make executable (Linux/Mac)
chmod +x .git/hooks/pre-commit

# On Windows, Git should handle this automatically
```

---

### False Positives in Security Check

**Symptom**: Security check flags legitimate code

**Fix**:
1. Review the flagged line carefully
2. If truly a false positive, use `# noqa` comment
3. Consider adding exception to pattern
4. Or bypass commit: `git commit --no-verify` (document why)

---

### Python Not Found

**Symptom**: Hook fails with "python: command not found"

**Fix**:
- Ensure Python is in PATH
- Update hook shebang to use specific Python version
- Or use: `python3` instead of `python`

---

## Benefits

✅ **Prevents Technical Debt**: Catches organization issues before they accumulate  
✅ **Security First**: Blocks critical security issues at source  
✅ **Fast Feedback**: < 2 seconds - doesn't slow down workflow  
✅ **Automatic**: No manual checking needed  
✅ **Consistent**: Same rules for all developers  
✅ **Educational**: Violation messages teach best practices  

---

## Philosophy

> "A clean commit history starts with clean commits. Prevent violations from entering the repository, rather than cleaning them up later."

The pre-commit hook embodies Feng Shui's philosophy of **preventive quality control**. By catching issues at commit time:

- **Earlier Detection** = Easier to fix (you just wrote the code)
- **Lower Cost** = Fix in seconds, not hours
- **Better Habits** = Learn correct patterns immediately
- **Cleaner History** = No "oops, fix typo" commits

---

## See Also

- [[Feng Shui Phase 4-17]] - Full Feng Shui architecture intelligence
- [[Three-Tier Quality Gate System]] - Complete quality gate strategy
- [[Gu Wu Testing Framework]] - Test organization standards
- `.clinerules` - Project development standards

---

**Last Updated**: 2026-02-09  
**Version**: 2.0 (5-Tier Intelligent System)  
**Status**: ACTIVE (runs on every commit)

---

## Quick Reference Card

### Speed Targets
- Tier 1 (File Org): < 1s
- Tier 2 (Security): < 1s
- Tier 3 (Gu Wu Tests): < 10s
- Tier 4 (Feng Shui Orchestrator): < 10s
- Tier 5 (Gap Detection): < 2s
- **Total**: < 25s (typical: 12-18s)

### Configuration Environment Variables
```bash
PRECOMMIT_RUN_TESTS=true|false          # Enable/disable Tier 3
PRECOMMIT_RUN_ORCHESTRATOR=true|false   # Enable/disable Tier 4
PRECOMMIT_DETECT_GAPS=true|false        # Enable/disable Tier 5
PRECOMMIT_TEST_TIMEOUT=10               # Tier 3 timeout (seconds)
PRECOMMIT_MAX_FILES=20                  # Max files before auto-skip
```

### Manual Tools
```bash
# Run Gu Wu tests manually
python tools/guwu/pre_commit_test_runner.py

# Run Feng Shui orchestrator manually
python tools/fengshui/pre_commit_orchestrator.py

# View test gaps
python -m tools.guwu.test_gap_display -v

# Generate test stubs
python -m tools.guwu.test_gap_display --auto-generate
```

### Emergency Bypass
```bash
git commit --no-verify -m "Emergency fix"
```

**Use sparingly!** Bypassing defeats the purpose of quality gates.
