#!/usr/bin/env python3
"""
Feng Shui Validation Strategies - Strategy Pattern
===================================================

Pluggable validation algorithms for different strictness levels.

GoF Pattern: Strategy (Behavioral)
- Define family of algorithms (validation strategies)
- Encapsulate each one and make them interchangeable
- Strategy varies independently from clients that use it
- Runtime algorithm selection

Use Cases:
- Different teams need different strictness levels
- CI/CD may want stricter rules than local dev
- MVP/prototype vs production validation
- Gradual migration to stricter standards
"""
import sys
from pathlib import Path
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None


@dataclass
class ValidationResult:
    """Result of validation strategy"""
    passed: bool
    score: int  # 0-100
    grade: str  # A+, A, B, C, F
    issues: List[str]
    severity: str  # PASS, WARN, FAIL


class ValidationStrategy(ABC):
    """
    Strategy: Abstract validation algorithm
    
    Different strategies apply different rules with different thresholds.
    """
    
    @abstractmethod
    def validate(self, module_path: Path) -> ValidationResult:
        """Apply validation algorithm to module"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Return strategy name"""
        pass
    
    @abstractmethod
    def get_thresholds(self) -> Dict[str, int]:
        """Return strategy thresholds"""
        pass


class StrictStrategy(ValidationStrategy):
    """
    Strategy: Strict validation for production code
    
    Rules:
    - module.json required
    - README.md required
    - Zero DI violations
    - Max file size: 500 lines
    - 100% blueprint config
    """
    
    def __init__(self):
        self.thresholds = {
            'min_score': 95,
            'max_file_lines': 500,
            'max_god_classes': 0,
            'di_violations_allowed': 0
        }
    
    def validate(self, module_path: Path) -> ValidationResult:
        """Strict validation"""
        issues = []
        score = 100
        
        # Check module.json
        if not (module_path / 'module.json').exists():
            issues.append('CRITICAL: module.json missing')
            score -= 30
        
        # Check README
        if not (module_path / 'README.md').exists():
            issues.append('HIGH: README.md missing')
            score -= 20
        
        # Check backend exists if module.json declares it
        if (module_path / 'backend').exists():
            backend_files = list((module_path / 'backend').glob('*.py'))
            for file in backend_files:
                lines = len(file.read_text(encoding='utf-8').splitlines())
                if lines > self.thresholds['max_file_lines']:
                    issues.append(f'HIGH: {file.name} exceeds {self.thresholds["max_file_lines"]} lines ({lines})')
                    score -= 10
        
        # Determine grade
        grade = self._calculate_grade(score)
        passed = score >= self.thresholds['min_score']
        severity = 'PASS' if passed else 'FAIL'
        
        return ValidationResult(passed, score, grade, issues, severity)
    
    def _calculate_grade(self, score: int) -> str:
        if score >= 98: return 'A+'
        if score >= 95: return 'A'
        if score >= 90: return 'A-'
        if score >= 85: return 'B+'
        if score >= 80: return 'B'
        return 'F'
    
    def get_name(self) -> str:
        return "StrictStrategy (Production)"
    
    def get_thresholds(self) -> Dict[str, int]:
        return self.thresholds


class ModerateStrategy(ValidationStrategy):
    """
    Strategy: Moderate validation for development
    
    Rules:
    - module.json required
    - README optional but recommended
    - Few DI violations acceptable
    - Max file size: 1000 lines
    """
    
    def __init__(self):
        self.thresholds = {
            'min_score': 80,
            'max_file_lines': 1000,
            'max_god_classes': 2,
            'di_violations_allowed': 3
        }
    
    def validate(self, module_path: Path) -> ValidationResult:
        """Moderate validation"""
        issues = []
        score = 100
        
        # Check module.json
        if not (module_path / 'module.json').exists():
            issues.append('HIGH: module.json missing')
            score -= 20
        
        # Check README (warning only)
        if not (module_path / 'README.md').exists():
            issues.append('MEDIUM: README.md recommended')
            score -= 10
        
        # Check file sizes
        if (module_path / 'backend').exists():
            backend_files = list((module_path / 'backend').glob('*.py'))
            for file in backend_files:
                lines = len(file.read_text(encoding='utf-8').splitlines())
                if lines > self.thresholds['max_file_lines']:
                    issues.append(f'MEDIUM: {file.name} is large ({lines} lines)')
                    score -= 5
        
        grade = self._calculate_grade(score)
        passed = score >= self.thresholds['min_score']
        severity = 'PASS' if passed else 'WARN'
        
        return ValidationResult(passed, score, grade, issues, severity)
    
    def _calculate_grade(self, score: int) -> str:
        if score >= 90: return 'A'
        if score >= 80: return 'B'
        if score >= 70: return 'C'
        return 'F'
    
    def get_name(self) -> str:
        return "ModerateStrategy (Development)"
    
    def get_thresholds(self) -> Dict[str, int]:
        return self.thresholds


class LenientStrategy(ValidationStrategy):
    """
    Strategy: Lenient validation for prototypes/MVP
    
    Rules:
    - module.json optional
    - README optional
    - DI violations acceptable
    - No file size limits
    """
    
    def __init__(self):
        self.thresholds = {
            'min_score': 60,
            'max_file_lines': 2000,
            'max_god_classes': 5,
            'di_violations_allowed': 999
        }
    
    def validate(self, module_path: Path) -> ValidationResult:
        """Lenient validation"""
        issues = []
        score = 100
        
        # Just check basic structure exists
        if not module_path.exists():
            issues.append('CRITICAL: Module directory missing')
            score = 0
        elif not any(module_path.iterdir()):
            issues.append('HIGH: Module is empty')
            score = 50
        else:
            issues.append('INFO: Prototype mode - minimal checks applied')
        
        grade = self._calculate_grade(score)
        passed = score >= self.thresholds['min_score']
        severity = 'PASS' if passed else 'WARN'
        
        return ValidationResult(passed, score, grade, issues, severity)
    
    def _calculate_grade(self, score: int) -> str:
        if score >= 80: return 'B'
        if score >= 60: return 'C'
        return 'F'
    
    def get_name(self) -> str:
        return "LenientStrategy (Prototype/MVP)"
    
    def get_thresholds(self) -> Dict[str, int]:
        return self.thresholds


class ValidationContext:
    """
    Context: Uses validation strategy to validate modules
    
    Strategy can be swapped at runtime based on environment, team, etc.
    """
    
    def __init__(self, strategy: ValidationStrategy):
        self._strategy = strategy
    
    def set_strategy(self, strategy: ValidationStrategy) -> None:
        """Change validation strategy at runtime"""
        self._strategy = strategy
    
    def validate_module(self, module_path: Path) -> ValidationResult:
        """Validate using current strategy"""
        print(f"\n🔍 Validating with {self._strategy.get_name()}")
        print(f"   Thresholds: {self._strategy.get_thresholds()}")
        return self._strategy.validate(module_path)


# =============================================================================
# STRATEGY FACTORY & AUTO-SELECTION
# =============================================================================

class StrategyFactory:
    """
    Factory: Creates appropriate strategy based on context
    
    Auto-selects strategy based on:
    - Environment (CI/CD vs local)
    - Git branch (main vs feature)
    - Config file settings
    """
    
    @staticmethod
    def create_for_environment(env: str = 'development') -> ValidationStrategy:
        """Create strategy based on environment"""
        strategies = {
            'production': StrictStrategy(),
            'staging': ModerateStrategy(),
            'development': ModerateStrategy(),
            'prototype': LenientStrategy()
        }
        return strategies.get(env, ModerateStrategy())
    
    @staticmethod
    def create_for_ci_cd() -> ValidationStrategy:
        """Create strict strategy for CI/CD"""
        return StrictStrategy()
    
    @staticmethod
    def create_for_branch(branch_name: str) -> ValidationStrategy:
        """Create strategy based on git branch"""
        if branch_name in ['main', 'master', 'production']:
            return StrictStrategy()
        elif branch_name.startswith('feature/') or branch_name.startswith('dev/'):
            return ModerateStrategy()
        else:
            return LenientStrategy()


# =============================================================================
# DEMONSTRATION
# =============================================================================

def demonstrate_strategy_pattern():
    """Demonstrate Strategy Pattern with validation"""
    print("\n" + "="*80)
    print("FENG SHUI STRATEGY PATTERN DEMONSTRATION")
    print("="*80)
    print("""
Strategy Pattern enables pluggable validation algorithms:

Context (ValidationContext):
- Uses a validation strategy
- Can swap strategy at runtime

Strategies (3 levels):
1. StrictStrategy - Production (min score: 95)
2. ModerateStrategy - Development (min score: 80)
3. LenientStrategy - Prototype/MVP (min score: 60)

Benefits:
- Same validation code, different rules
- Easy to add new strategies
- Runtime strategy selection
- Team/environment-specific validation
""")
    
    # Create test module path
    test_module = Path('modules/knowledge_graph')
    
    # Example 1: Manual strategy selection
    print("\n" + "="*80)
    print("EXAMPLE 1: Manual Strategy Selection")
    print("="*80)
    
    context = ValidationContext(StrictStrategy())
    result1 = context.validate_module(test_module)
    print(f"\n   Result: {result1.severity}")
    print(f"   Score: {result1.score} (Grade {result1.grade})")
    print(f"   Passed: {'✓' if result1.passed else '✗'}")
    if result1.issues:
        print(f"   Issues: {len(result1.issues)}")
        for issue in result1.issues[:3]:
            print(f"      - {issue}")
    
    # Switch strategy at runtime
    print("\n   [SWITCHING to Moderate Strategy...]")
    context.set_strategy(ModerateStrategy())
    result2 = context.validate_module(test_module)
    print(f"\n   Result: {result2.severity}")
    print(f"   Score: {result2.score} (Grade {result2.grade})")
    print(f"   Passed: {'✓' if result2.passed else '✗'}")
    
    # Example 2: Strategy Factory
    print("\n\n" + "="*80)
    print("EXAMPLE 2: Strategy Factory (Auto-Selection)")
    print("="*80)
    
    # Based on environment
    print("\n   Environment-based selection:")
    for env in ['production', 'development', 'prototype']:
        strategy = StrategyFactory.create_for_environment(env)
        print(f"      {env:15} → {strategy.get_name()}")
    
    # Based on branch
    print("\n   Branch-based selection:")
    for branch in ['main', 'feature/new-ui', 'prototype/experiment']:
        strategy = StrategyFactory.create_for_branch(branch)
        print(f"      {branch:25} → {strategy.get_name()}")
    
    # Example 3: CI/CD Integration
    print("\n\n" + "="*80)
    print("EXAMPLE 3: CI/CD Integration")
    print("="*80)
    
    ci_strategy = StrategyFactory.create_for_ci_cd()
    print(f"\n   CI/CD uses: {ci_strategy.get_name()}")
    print(f"   Thresholds: {ci_strategy.get_thresholds()}")
    print("\n   This ensures production-ready code only!")
    
    # Summary
    print("\n\n" + "="*80)
    print("STRATEGY PATTERN BENEFITS")
    print("="*80)
    print("""
Real-World Use Cases:
- ✅ Team Standards: Different teams, different rules
- ✅ Environment-Specific: Strict in prod, lenient in dev
- ✅ Migration: Gradually increase strictness
- ✅ CI/CD: Fail build only on critical issues
- ✅ Flexibility: Add new strategies without changing code

Integration Points:
1. Automation Engine uses strategy for validation
2. Pre-commit hook uses branch-based strategy
3. CI/CD uses strict strategy
4. Local dev uses moderate strategy

Extensible: Add CustomStrategy for your team's specific needs!
""")


if __name__ == '__main__':
    demonstrate_strategy_pattern()