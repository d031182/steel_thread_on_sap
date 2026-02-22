# Feng Shui + Gu Wu Integration Bridge

**Version**: 1.0  
**Date**: 2026-02-22  
**Task**: MED-25 - Feng Shui + Gu Wu Integration  
**Status**: ✅ Complete

## Overview

The Feng Shui + Gu Wu Integration Bridge connects Feng Shui's architecture analysis capabilities with Gu Wu's automated resolution system, creating an end-to-end quality improvement pipeline.

**Pipeline Flow**:
```
Feng Shui Analysis → Adapter → Gu Wu Resolvers → Automated Fixes
     (Findings)      (Format)   (Resolution)      (Actions)
```

## Architecture

### Components

1. **FengShuiAdapter** (`tools/guwu/adapters/feng_shui_adapter.py`)
   - Converts Feng Shui `AgentReport` → Gu Wu dict format
   - Provides filtering (severity, category)
   - Adds helper methods (grouping, summary statistics)

2. **ResolverRegistry Integration** (`tools/guwu/resolvers/resolver_registry.py`)
   - `process_feng_shui_report()` method for end-to-end processing
   - Dispatches findings to appropriate resolvers
   - Returns structured resolution results

3. **CLI Tool** (`tools/guwu/cli_feng_shui.py`)
   - Command-line interface for the full pipeline
   - Supports dry-run mode for safe validation
   - JSON output for automation

## Usage

### Basic Usage

```bash
# Analyze and resolve HIGH+ severity issues
python -m tools.guwu.cli_feng_shui --agent file_organization --severity high

# Dry run (show what would be fixed)
python -m tools.guwu.cli_feng_shui --agent file_organization --dry-run

# Resolve specific categories only
python -m tools.guwu.cli_feng_shui --agent file_organization \
  --categories "Root Directory Clutter" "Misplaced Script"

# Output as JSON for automation
python -m tools.guwu.cli_feng_shui --agent file_organization --json
```

### Programmatic Usage

```python
from pathlib import Path
from tools.fengshui.agents.file_organization_agent import FileOrganizationAgent
from tools.guwu.resolvers.resolver_registry import ResolverRegistry

# Step 1: Run Feng Shui analysis
agent = FileOrganizationAgent()
report = agent.analyze_module(Path("."))

# Step 2: Process with Gu Wu
registry = ResolverRegistry()
results = registry.process_feng_shui_report(
    report,
    min_severity='high',
    dry_run=False  # Set True for safe preview
)

# Step 3: Check results
print(f"Resolved: {results['resolved']}")
print(f"Failed: {results['failed']}")
print(f"Skipped: {results['skipped']}")
```

### Adapter Usage (Advanced)

```python
from tools.guwu.adapters import FengShuiAdapter

# Convert report to Gu Wu format
adapter = FengShuiAdapter()
findings = adapter.parse_report(
    report,
    min_severity='high',
    categories=['Root Directory Clutter']
)

# Get summary statistics
summary = adapter.get_summary(findings)
print(f"Critical: {summary['critical']}, High: {summary['high']}")

# Group by category
grouped = adapter.group_by_category(findings)
for category, cat_findings in grouped.items():
    print(f"{category}: {len(cat_findings)} findings")
```

## FengShuiAdapter API

### Methods

#### `parse_report(report, min_severity=None, categories=None)`
Parse Feng Shui AgentReport into Gu Wu format.

**Args**:
- `report`: Feng Shui AgentReport object
- `min_severity`: Minimum severity ('critical', 'high', 'medium', 'low')
- `categories`: List of categories to include

**Returns**: List of finding dicts

#### `filter_by_category(findings, category)`
Filter findings by category.

#### `filter_by_severity(findings, min_severity='low')`
Filter findings by minimum severity.

#### `group_by_category(findings)`
Group findings by category.

**Returns**: Dict[category → findings]

#### `get_summary(findings)`
Get summary statistics.

**Returns**: Dict with counts by severity

## Data Format

### Feng Shui Finding (Input)
```python
Finding(
    category="Root Directory Clutter",
    severity=Severity.HIGH,
    file_path=Path("temp.py"),
    line_number=None,
    description="Unauthorized file: temp.py",
    recommendation="DELETE",
    code_snippet=None
)
```

### Gu Wu Finding (Output)
```python
{
    'category': 'Root Directory Clutter',
    'severity': 'high',
    'file_path': Path('temp.py'),
    'line_number': None,
    'description': 'Unauthorized file: temp.py',
    'recommendation': 'DELETE',
    'code_snippet': None,
    'agent_name': 'file_organization',
    'module_path': Path('.')
}
```

### Resolution Result
```python
{
    'total_findings': 10,
    'resolved': 7,
    'failed': 1,
    'skipped': 2,
    'results': [
        {
            'category': 'Root Directory Clutter',
            'status': 'resolved',
            'description': 'Unauthorized file: temp.py'
        },
        ...
    ]
}
```

## Supported Agents

### File Organization Agent
**Categories**:
- Root Directory Clutter
- Misplaced Script
- Obsolete File

**Resolver**: FileOrganizationResolver

## Testing

### Unit Tests
```bash
# Test adapter
pytest tests/unit/tools/guwu/test_feng_shui_adapter.py -v

# Test integration
pytest tests/unit/tools/guwu/ -v
```

**Test Coverage**: 13 tests, all passing
- Adapter initialization
- Report parsing (basic, filtered)
- Severity filtering
- Category filtering
- Combined filters
- Grouping and summary
- Enhanced fields preservation (v4.34+)
- GoF pattern fields preservation (v4.36+)

## Safety Features

### Dry Run Mode
```bash
# Safe preview without making changes
python -m tools.guwu.cli_feng_shui --agent file_organization --dry-run
```

**Benefits**:
- ✅ See what would be fixed
- ✅ No actual file modifications
- ✅ Verify resolver logic
- ✅ Safe for production environments

### Severity Filtering
```python
# Only process CRITICAL issues
results = registry.process_feng_shui_report(report, min_severity='critical')

# Process HIGH and above
results = registry.process_feng_shui_report(report, min_severity='high')
```

### Category Filtering
```python
# Only resolve specific categories
findings = adapter.parse_report(
    report,
    categories=['Root Directory Clutter']
)
```

## Integration Points

### 1. Quality Ecosystem
- **Feng Shui**: Architecture analysis (7 agents)
- **Gu Wu**: Automated resolution (expanding resolver library)
- **Shi Fu**: Ecosystem insights and pattern tracking

### 2. CI/CD Pipeline
```yaml
# .github/workflows/quality.yml
- name: Run Feng Shui + Gu Wu
  run: |
    python -m tools.guwu.cli_feng_shui \
      --agent file_organization \
      --severity high \
      --json > quality-report.json
```

### 3. Pre-Commit Hooks
```bash
# scripts/pre-commit-feng-shui.py
python -m tools.guwu.cli_feng_shui --agent file_organization --dry-run
```

## Future Enhancements

### Phase 2: More Agents
- [x] FileOrganizationAgent
- [ ] ArchitectAgent (DI violations, GoF patterns)
- [ ] SecurityAgent (SQL injection, XSS)
- [ ] PerformanceAgent (N+1 queries, caching)

### Phase 3: Interactive Mode
```bash
# Prompt for confirmations
python -m tools.guwu.cli_feng_shui --interactive
```

### Phase 4: Batch Processing
```python
# Process multiple modules
for module_path in module_paths:
    report = agent.analyze_module(module_path)
    results = registry.process_feng_shui_report(report)
```

## Design Decisions

### Why Adapter Pattern?
**Problem**: Feng Shui uses dataclass Finding, Gu Wu uses dicts  
**Solution**: FengShuiAdapter converts between formats  
**Benefit**: Each system remains independent, adapter handles conversion

### Why process_feng_shui_report()?
**Problem**: CLI needs end-to-end pipeline  
**Solution**: Single method in ResolverRegistry  
**Benefit**: Simple API, handles full workflow internally

### Why Separate CLI?
**Problem**: `tools.guwu` has own CLI, Feng Shui has own CLI  
**Solution**: New `cli_feng_shui.py` for integrated pipeline  
**Benefit**: Clear separation, focused tool for this workflow

## Key Learnings

### 1. Format Conversion is Critical
- Feng Shui Finding → Gu Wu dict mapping must be exact
- Preserve all fields (including enhanced v4.34+ and GoF v4.36+)
- Test with real Feng Shui output

### 2. Filtering at Multiple Levels
- Adapter level: Parse-time filtering (efficient)
- Post-parse level: Helper methods for flexibility
- Both approaches useful for different scenarios

### 3. Dry Run is Essential
- Production code shouldn't delete files without confirmation
- Dry run mode enables safe validation
- Critical for CI/CD integration

### 4. Error Handling Matters
- Resolvers may fail (file permissions, etc.)
- Graceful degradation: Continue with other findings
- Detailed error reporting in results

## Documentation References

- [[Feng Shui Architecture Audit]] - Feng Shui capabilities
- [[Gu Wu Resolver Expansion]] - Resolver architecture
- [[Guwu API Contract Testing Foundation]] - Testing methodology
- [[Module Federation Standard]] - Project architecture

## Version History

### v1.0 (2026-02-22) - Initial Release
**Completed**:
- FengShuiAdapter implementation
- ResolverRegistry integration
- CLI tool
- Comprehensive unit tests (13 tests, all passing)
- Documentation

**Key Metrics**:
- Test Coverage: 100% of adapter methods
- Performance: < 1 second for 100+ findings
- Compatibility: Feng Shui v4.36+, Gu Wu v2.0+

---

**Task Reference**: MED-25  
**Implementation Time**: ~2 hours  
**Files Created**: 4 (adapter, tests, CLI, docs)  
**Lines of Code**: ~800 (including tests and docs)