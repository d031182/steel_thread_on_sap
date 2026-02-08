# Feng Shui + Gu Wu Integration Plan (Phase 8.3)

**Date**: February 8, 2026  
**Goal**: Enable Gu Wu to consume Feng Shui's multi-agent analysis and generate pytest tests  
**Effort**: 4-6 hours  
**Status**: 📋 READY TO IMPLEMENT

---

## 🎯 Overview

**Current State**:
- ✅ Feng Shui: Has 6-agent multi-agent system (Phase 4-17)
- ✅ Gu Wu: Has ReAct agent for test optimization  
- ❌ Integration: Gu Wu cannot consume Feng Shui's analysis

**Target State**:
- ✅ Feng Shui validator returns structured JSON
- ✅ Gu Wu test generator reads JSON and creates pytest tests
- ✅ Complete pipeline: Feng Shui analyze → Gu Wu generate → pytest run

---

## 📐 Architecture

```
Feng Shui Multi-Agent Analysis
         ↓
    JSON Report
    {
      "checks": [...],
      "issues": [...],
      "summary": {...}
    }
         ↓
Gu Wu Test Generator
         ↓
    pytest Tests
    tests/e2e/app_v2/test_<module>.py
         ↓
    pytest Execution
    (1-5 seconds vs 60-300 seconds browser)
```

---

## 🔨 Implementation Steps

### **Step 1: Refactor Feng Shui Validator** (1-2 hours)

**File**: `tools/fengshui/validators/app_v2_validator.py`

**Changes**:
1. Add `to_dict()` method to `Issue` class ✅ (already has attributes)
2. Add `validate_to_json()` method to `AppV2ModuleValidator`
3. Keep existing `validate()` + `print_summary()` for CLI usage
4. Return structured dict with:
   ```python
   {
       "module_name": "knowledge_graph_v2",
       "checks": [
           {"name": "Scripts Accessible", "status": "PASS", "issues": []},
           {"name": "Navigation", "status": "FAIL", "issues": [...]},
           ...
       ],
       "issues": [
           {"type": "...", "severity": "...", "description": "...", ...},
           ...
       ],
       "summary": {
           "total_checks": 5,
           "passed": 3,
           "failed": 2,
           "total_issues": 7,
           "by_severity": {"CRITICAL": 2, "HIGH": 3, ...}
       }
   }
   ```

**Implementation**:
```python
def to_dict(self) -> Dict[str, Any]:
    """Convert validation results to JSON-serializable dict"""
    checks = [
        {
            "name": "Scripts Accessible",
            "status": "PASS" if not any(i.type == "SCRIPTS_NOT_ACCESSIBLE" for i in self.issues) else "FAIL",
            "issues": [i.to_dict() for i in self.issues if i.type == "SCRIPTS_NOT_ACCESSIBLE"]
        },
        # ... repeat for all 5 checks
    ]
    
    return {
        "module_name": self.module_name,
        "checks": checks,
        "issues": [i.to_dict() for i in self.issues],
        "summary": {
            "total_checks": len(checks),
            "passed": sum(1 for c in checks if c["status"] == "PASS"),
            "failed": sum(1 for c in checks if c["status"] == "FAIL"),
            "total_issues": len(self.issues),
            "by_severity": {
                "CRITICAL": sum(1 for i in self.issues if i.severity == "CRITICAL"),
                "HIGH": sum(1 for i in self.issues if i.severity == "HIGH"),
                "MEDIUM": sum(1 for i in self.issues if i.severity == "MEDIUM"),
                "LOW": sum(1 for i in self.issues if i.severity == "LOW"),
            }
        }
    }

# Add to Issue class
def to_dict(self) -> Dict[str, Any]:
    """Convert issue to dict"""
    return {
        "type": self.type,
        "severity": self.severity,
        "description": self.description,
        "location": self.location,
        "suggestion": self.suggestion,
        "detected_at": self.detected_at
    }
```

---

### **Step 2: Create Gu Wu Test Generator** (2-3 hours)

**New Files**:
1. `tools/guwu/generators/__init__.py`
2. `tools/guwu/generators/base_generator.py`
3. `tools/guwu/generators/app_v2_test_generator.py`

#### **File 1: `tools/guwu/generators/__init__.py`**
```python
"""
Gu Wu Test Generators

Generate pytest tests from Feng Shui analysis reports.
"""

from .base_generator import BaseTestGenerator
from .app_v2_test_generator import AppV2TestGenerator

__all__ = ['BaseTestGenerator', 'AppV2TestGenerator']
```

#### **File 2: `tools/guwu/generators/base_generator.py`**
```python
"""
Base Test Generator

Abstract class for all test generators.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List


class BaseTestGenerator(ABC):
    """
    Base class for test generators
    
    Subclasses generate pytest tests from Feng Shui reports.
    """
    
    def __init__(self, output_dir: Path = None):
        """
        Initialize generator
        
        Args:
            output_dir: Directory to write generated tests (default: tests/e2e/app_v2/)
        """
        self.output_dir = output_dir or Path("tests/e2e/app_v2")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @abstractmethod
    def generate_from_report(self, report: Dict[str, Any]) -> Path:
        """
        Generate pytest tests from Feng Shui report
        
        Args:
            report: Feng Shui validation report (JSON dict)
            
        Returns:
            Path to generated test file
        """
        pass
    
    def _generate_test_header(self, module_name: str) -> str:
        """Generate standard pytest test file header"""
        return f'''"""
Auto-generated E2E tests for {module_name}

Generated by: Gu Wu (顾武) Test Generator
Source: Feng Shui (风水) Multi-Agent Analysis
Date: {{datetime.now().isoformat()}}

DO NOT EDIT - Regenerate from Feng Shui report if validation changes.
"""

import pytest
from pathlib import Path
import json


# Module under test
MODULE_NAME = "{module_name}"
MODULE_PATH = Path(f"modules/{{MODULE_NAME}}")

'''
    
    def _generate_test_footer(self) -> str:
        """Generate standard test file footer"""
        return """

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
"""
```

#### **File 3: `tools/guwu/generators/app_v2_test_generator.py`**
```python
"""
App V2 Test Generator

Generates pytest tests for App V2 modules from Feng Shui validation reports.
"""

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from .base_generator import BaseTestGenerator


class AppV2TestGenerator(BaseTestGenerator):
    """
    Generate pytest tests for App V2 modules
    
    Converts Feng Shui validation checks into pytest tests.
    """
    
    def generate_from_report(self, report: Dict[str, Any]) -> Path:
        """
        Generate pytest tests from Feng Shui report
        
        Creates tests for:
        1. Scripts accessibility
        2. Navigation consistency
        3. Interface compliance
        4. Dynamic loading compatibility
        5. SAPUI5 rendering safety
        
        Args:
            report: Feng Shui validation report dict
            
        Returns:
            Path to generated test file
        """
        module_name = report['module_name']
        checks = report['checks']
        
        # Generate test file
        test_content = self._generate_test_header(module_name)
        
        # Add fixtures
        test_content += self._generate_fixtures(module_name)
        
        # Generate tests for each check
        for check in checks:
            test_content += self._generate_test_for_check(check, module_name)
        
        # Add footer
        test_content += self._generate_test_footer()
        
        # Write to file
        output_file = self.output_dir / f"test_{module_name}.py"
        output_file.write_text(test_content)
        
        return output_file
    
    def _generate_fixtures(self, module_name: str) -> str:
        """Generate pytest fixtures"""
        return f'''

@pytest.fixture
def module_config():
    """Load module.json configuration"""
    config_path = MODULE_PATH / "module.json"
    return json.loads(config_path.read_text())


@pytest.fixture
def app_v2_base_url():
    """Base URL for App V2 (assumes local development)"""
    return "http://localhost:5000"

'''
    
    def _generate_test_for_check(self, check: Dict[str, Any], module_name: str) -> str:
        """Generate pytest test for a specific check"""
        check_name = check['name']
        status = check['status']
        issues = check['issues']
        
        # Map check names to test methods
        test_mapping = {
            "Scripts Accessible": self._generate_scripts_test,
            "Navigation Consistency": self._generate_navigation_test,
            "Interface Compliance": self._generate_interface_test,
            "Dynamic Loading Compatibility": self._generate_loading_test,
            "SAPUI5 Rendering Safety": self._generate_rendering_test,
        }
        
        generator = test_mapping.get(check_name)
        if generator:
            return generator(check, module_name, issues)
        else:
            return f"\n# TODO: Test for {check_name} not yet implemented\n"
    
    def _generate_scripts_test(self, check: Dict, module_name: str, issues: List[Dict]) -> str:
        """Generate test for scripts accessibility"""
        return f'''

@pytest.mark.e2e
@pytest.mark.app_v2
def test_scripts_accessible(module_config, app_v2_base_url):
    """
    Test: Frontend scripts are accessible via HTTP
    
    Feng Shui Check: Scripts Accessible
    Status: {check['status']}
    Issues Found: {len(issues)}
    """
    import requests
    
    if 'frontend' not in module_config:
        pytest.skip("Module has no frontend configuration")
    
    scripts = module_config['frontend'].get('scripts', [])
    
    for script in scripts:
        script_url = f"{{app_v2_base_url}}/v2/{{script}}"
        response = requests.get(script_url, timeout=5)
        
        assert response.status_code == 200, \\
            f"Script not accessible: {{script}} ({{response.status_code}})"
'''
    
    def _generate_navigation_test(self, check: Dict, module_name: str, issues: List[Dict]) -> str:
        """Generate test for navigation consistency"""
        return f'''

@pytest.mark.e2e
@pytest.mark.app_v2
def test_navigation_consistency(module_config):
    """
    Test: Navigation structure is consistent
    
    Feng Shui Check: Navigation Consistency
    Status: {check['status']}
    Issues Found: {len(issues)}
    """
    if 'frontend' not in module_config:
        pytest.skip("Module has no frontend configuration")
    
    frontend_config = module_config['frontend']
    
    # Verify module has required navigation fields
    assert 'entry_point' in frontend_config, "Missing entry_point in frontend config"
    assert 'scripts' in frontend_config, "Missing scripts in frontend config"
    
    # If category is declared, ensure it's valid
    if 'category' in frontend_config:
        category = frontend_config['category']
        valid_categories = ['infrastructure', 'features', 'analytics']
        assert category in valid_categories, \\
            f"Invalid category: {{category}}. Must be one of {{valid_categories}}"
'''
    
    def _generate_interface_test(self, check: Dict, module_name: str, issues: List[Dict]) -> str:
        """Generate test for interface compliance"""
        return f'''

@pytest.mark.e2e
@pytest.mark.app_v2
def test_interface_compliance():
    """
    Test: Implementations match their interfaces
    
    Feng Shui Check: Interface Compliance
    Status: {check['status']}
    Issues Found: {len(issues)}
    """
    # Check NoOpLogger implements complete ILogger interface
    noop_logger = Path("app_v2/static/js/adapters/NoOpLogger.js")
    ilogger = Path("app_v2/static/js/interfaces/ILogger.js")
    
    assert noop_logger.exists(), "NoOpLogger.js not found"
    assert ilogger.exists(), "ILogger.js not found"
    
    # Extract methods from interface
    import re
    ilogger_content = ilogger.read_text()
    interface_methods = set(re.findall(r'^\\s*(\\w+)\\s*\\([^)]*\\)\\s*{{', ilogger_content, re.MULTILINE))
    
    # Extract methods from implementation
    noop_content = noop_logger.read_text()
    impl_methods = set(re.findall(r'^\\s*(\\w+)\\s*\\([^)]*\\)\\s*{{', noop_content, re.MULTILINE))
    
    # Verify all interface methods are implemented
    missing_methods = interface_methods - impl_methods
    assert not missing_methods, \\
        f"NoOpLogger missing methods: {{', '.join(missing_methods)}}"
'''
    
    def _generate_loading_test(self, check: Dict, module_name: str, issues: List[Dict]) -> str:
        """Generate test for dynamic loading compatibility"""
        return f'''

@pytest.mark.e2e
@pytest.mark.app_v2
def test_dynamic_loading_compatibility(module_config):
    """
    Test: Module exports are compatible with dynamic loading
    
    Feng Shui Check: Dynamic Loading Compatibility
    Status: {check['status']}
    Issues Found: {len(issues)}
    """
    if 'frontend' not in module_config:
        pytest.skip("Module has no frontend configuration")
    
    scripts = module_config['frontend'].get('scripts', [])
    
    for script in scripts:
        script_path = Path(script)
        
        if not script_path.exists():
            pytest.skip(f"Script not found: {{script}}")
        
        content = script_path.read_text()
        
        # Check for problematic ES6 exports
        problematic_patterns = ['export function', 'export const', 'export class']
        found_patterns = [p for p in problematic_patterns if p in content]
        
        assert not found_patterns, \\
            f"ES6 exports detected in {{script}}: {{found_patterns}} " \\
            f"(incompatible with dynamic <script> loading). " \\
            f"Use window.FunctionName = ... instead."
'''
    
    def _generate_rendering_test(self, check: Dict, module_name: str, issues: List[Dict]) -> str:
        """Generate test for SAPUI5 rendering safety"""
        return f'''

@pytest.mark.e2e
@pytest.mark.app_v2
def test_sapui5_rendering_safety():
    """
    Test: SAPUI5 rendering follows safe patterns
    
    Feng Shui Check: SAPUI5 Rendering Safety
    Status: {check['status']}
    Issues Found: {len(issues)}
    """
    router_service = Path("app_v2/static/js/core/RouterService.js")
    
    assert router_service.exists(), "RouterService.js not found"
    
    content = router_service.read_text()
    
    # Check for problematic patterns
    problematic_patterns = {{
        'document.createElement': 'Temp DOM element creation',
        'placeAt': 'placeAt() usage (can cause lifecycle issues)',
    }}
    
    warnings = []
    for pattern, description in problematic_patterns.items():
        if pattern in content:
            warnings.append(f"{{description}} detected in RouterService")
    
    # This is a warning, not a failure (may be intentional)
    if warnings:
        pytest.warn(Warning(
            "Potential SAPUI5 rendering issues detected:\\n" + 
            "\\n".join(f"  - {{w}}" for w in warnings)
        ))
'''


# CLI interface for standalone usage
if __name__ == '__main__':
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python -m tools.guwu.generators.app_v2_test_generator <report.json>")
        sys.exit(1)
    
    report_path = Path(sys.argv[1])
    report = json.loads(report_path.read_text())
    
    generator = AppV2TestGenerator()
    output_file = generator.generate_from_report(report)
    
    print(f"✅ Generated tests: {output_file}")
```

---

### **Step 3: Create Integration Script** (30 min)

**New File**: `tools/guwu/feng_shui_integration.py`

```python
"""
Feng Shui + Gu Wu Integration Script

Complete pipeline:
1. Run Feng Shui validator on module
2. Get JSON report
3. Generate pytest tests via Gu Wu
4. Run tests
5. Report results
"""

import sys
import json
from pathlib import Path
from tools.fengshui.validators.app_v2_validator import AppV2ModuleValidator
from tools.guwu.generators.app_v2_test_generator import AppV2TestGenerator
import subprocess


def integrate_feng_shui_guwu(module_name: str, run_tests: bool = True):
    """
    Complete Feng Shui → Gu Wu → pytest pipeline
    
    Args:
        module_name: Name of module to analyze
        run_tests: Whether to run generated tests (default True)
    """
    print("=" * 70)
    print("🔬 Feng Shui + Gu Wu Integration Pipeline")
    print("=" * 70)
    
    # Step 1: Run Feng Shui validator
    print("\n📊 Step 1: Running Feng Shui validator...")
    validator = AppV2ModuleValidator(module_name)
    validator.validate()
    
    # Get JSON report
    report = validator.to_dict()
    
    print(f"   ✅ Feng Shui analysis complete: {len(report['issues'])} issues found")
    
    # Save report (for debugging)
    report_file = Path(f"feng_shui_report_{module_name}.json")
    report_file.write_text(json.dumps(report, indent=2))
    print(f"   📄 Report saved: {report_file}")
    
    # Step 2: Generate tests via Gu Wu
    print("\n🧪 Step 2: Generating pytest tests via Gu Wu...")
    generator = AppV2TestGenerator()
    test_file = generator.generate_from_report(report)
    
    print(f"   ✅ Tests generated: {test_file}")
    
    # Step 3: Run tests (optional)
    if run_tests:
        print("\n🏃 Step 3: Running generated tests...")
        result = subprocess.run(
            ['pytest', str(test_file), '-v'],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed (see output above)")
            return False
    
    print("\n" + "=" * 70)
    print("✅ Pipeline complete!")
    print("=" * 70)
    
    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python -m tools.guwu.feng_shui_integration <module_name>")
        print("\nExample:")
        print("  python -m tools.guwu.feng_shui_integration knowledge_graph_v2")
        sys.exit(1)
    
    module_name = sys.argv[1]
    success = integrate_feng_shui_guwu(module_name)
    
    sys.exit(0 if success else 1)
```

---

## 🧪 Testing the Pipeline

### **Test 1: Generate Tests** (Dry Run)
```bash
# Run Feng Shui validator
python tools/fengshui/validators/app_v2_validator.py knowledge_graph_v2

# Generate tests from report
python -m tools.guwu.generators.app_v2_test_generator feng_shui_report_knowledge_graph_v2.json

# Verify test file created
ls -lh tests/e2e/app_v2/test_knowledge_graph_v2.py
```

### **Test 2: Full Pipeline**
```bash
# Run complete pipeline
python -m tools.guwu.feng_shui_integration knowledge_graph_v2

# Verify tests pass
pytest tests/e2e/app_v2/test_knowledge_graph_v2.py -v
```

---

## 📊 Success Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| **Speed** | < 5 seconds | pytest execution time |
| **Coverage** | 5 test types | All 5 Feng Shui checks tested |
| **Automation** | 100% | No manual steps required |
| **Reliability** | Tests pass | All generated tests executable |

---

## 🎯 Benefits

**Before (Manual Browser Testing)**:
- ❌ 30-180 minutes per module
- ❌ Tedious, repetitive clicking
- ❌ Hard to reproduce issues
- ❌ No automation

**After (Feng Shui + Gu Wu Pipeline)**:
- ✅ 1-5 seconds per module (60-180x faster!)
- ✅ Automated, repeatable
- ✅ Easy to debug (pytest output)
- ✅ CI/CD ready

---

## 🚀 Next Steps (After Phase 8.3)

1. **Phase 8.4**: Extend to all 7 pending modules
2. **Phase 8.5**: Add Gu Wu intelligent test evolution (learns from failures)
3. **Phase 8.6**: Integrate into CI/CD pipeline

---

**Status**: 📋 READY TO IMPLEMENT  
**Estimated Time**: 4-6 hours  
**Priority**: HIGH (unblocks App V2 migration)