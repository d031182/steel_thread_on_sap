#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feng Shui Score Calculator
==========================
Calculates a holistic quality score for modules based on Quality Gate results.

Philosophy: Like Feng Shui itself, the score reflects harmony, balance, and flow.
- A/S: Excellent (90-100%) - Production-ready, exemplar module
- B: Good (75-89%) - Production-ready with minor improvements needed
- C: Acceptable (60-74%) - Functional but needs refactoring
- D: Poor (40-59%) - Major issues, not production-ready
- F: Critical (<40%) - Severe problems, requires immediate attention

Score Components:
1. Architecture (40%) - DI, interfaces, loose coupling, structure
2. Code Quality (30%) - Exception handling, logging, input validation
3. Security (20%) - SQL injection, secrets, resource cleanup
4. Documentation (10%) - README, integration docs, tests

@author P2P Development Team
@version 1.0.0
"""

from pathlib import Path
from typing import Dict, Tuple
from dataclasses import dataclass
import sys
import os

# Force UTF-8 encoding for Windows (see docs/knowledge/guidelines/windows-encoding-standard.md)
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from module_quality_gate import ModuleQualityGate


@dataclass
class FengShuiScore:
    """Feng Shui score breakdown"""
    total_score: int  # 0-100
    grade: str  # A/S, B, C, D, F
    architecture_score: int  # 0-40
    quality_score: int  # 0-30
    security_score: int  # 0-20
    documentation_score: int  # 0-10
    emoji: str  # Visual indicator
    status: str  # Human-readable status


class FengShuiScorer:
    """Calculate Feng Shui scores from Quality Gate results"""
    
    # Architecture checks (40 points max)
    ARCHITECTURE_CHECKS = [
        'Blueprint config present',
        'Blueprint definition found',
        'Blueprint .* exported in __init__.py',
        'Blueprint .* is registered in app.py',
        'No DI violations detected',
        'Uses interfaces from core.interfaces',
        'No direct module imports',
        'Constructor dependency injection detected'
    ]
    
    # Code Quality checks (30 points max)
    QUALITY_CHECKS = [
        'Exception handling follows best practices',
        'Uses proper logging',
        'Input validation detected in API endpoints',
        'No hardcoded paths detected',
        'Global state check passed'
    ]
    
    # Security checks (20 points max)
    SECURITY_CHECKS = [
        'No SQL injection risks detected',
        'No hardcoded secrets detected',
        'Resource cleanup issues'
    ]
    
    # Documentation checks (10 points max)
    DOCUMENTATION_CHECKS = [
        'README.md exists',
        'README documents integration with code examples',
        'Tests present'
    ]
    
    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.module_name = module_path.name
    
    def calculate_score(self) -> FengShuiScore:
        """
        Calculate Feng Shui score from Quality Gate results
        
        Returns:
            FengShuiScore with breakdown
        """
        # Run quality gate
        gate = ModuleQualityGate(self.module_path)
        passed, results = gate.validate()
        
        # Extract passed messages
        passed_messages = [r.message for r in results if r.passed]
        
        # Calculate component scores
        arch_score = self._score_category(passed_messages, self.ARCHITECTURE_CHECKS, 40)
        quality_score = self._score_category(passed_messages, self.QUALITY_CHECKS, 30)
        security_score = self._score_category(passed_messages, self.SECURITY_CHECKS, 20)
        doc_score = self._score_category(passed_messages, self.DOCUMENTATION_CHECKS, 10)
        
        # Calculate total (0-100)
        total = arch_score + quality_score + security_score + doc_score
        
        # Determine grade and emoji
        grade, emoji, status = self._grade_score(total)
        
        return FengShuiScore(
            total_score=total,
            grade=grade,
            architecture_score=arch_score,
            quality_score=quality_score,
            security_score=security_score,
            documentation_score=doc_score,
            emoji=emoji,
            status=status
        )
    
    def _score_category(self, passed_messages: list, check_patterns: list, max_points: int) -> int:
        """
        Score a category based on matching check patterns
        
        Args:
            passed_messages: List of passed check messages
            check_patterns: Regex patterns for checks in this category
            max_points: Maximum points for this category
            
        Returns:
            Score (0 to max_points)
        """
        import re
        
        matched = 0
        total_checks = len(check_patterns)
        
        for pattern in check_patterns:
            for message in passed_messages:
                if re.search(pattern, message):
                    matched += 1
                    break
        
        # Proportional scoring
        if total_checks == 0:
            return max_points
        
        return int((matched / total_checks) * max_points)
    
    def _grade_score(self, score: int) -> Tuple[str, str, str]:
        """
        Convert numeric score to letter grade, emoji, and status
        
        Args:
            score: Total score (0-100)
            
        Returns:
            (grade, emoji, status)
        """
        if score >= 95:
            return ('A/S', '🌟', 'Exceptional - Production exemplar')
        elif score >= 90:
            return ('A', '✅', 'Excellent - Production ready')
        elif score >= 85:
            return ('A-', '🟢', 'Very Good - Production ready')
        elif score >= 80:
            return ('B+', '🟢', 'Good - Production ready')
        elif score >= 75:
            return ('B', '🟡', 'Good - Minor improvements recommended')
        elif score >= 70:
            return ('B-', '🟡', 'Acceptable - Improvements needed')
        elif score >= 65:
            return ('C+', '🟡', 'Acceptable - Refactoring recommended')
        elif score >= 60:
            return ('C', '🟠', 'Marginal - Significant work needed')
        elif score >= 50:
            return ('D', '🔴', 'Poor - Not production-ready')
        elif score >= 40:
            return ('D-', '🔴', 'Poor - Major issues')
        else:
            return ('F', '⛔', 'Critical - Severe problems')
    
    def print_report(self):
        """Print detailed Feng Shui score report"""
        score = self.calculate_score()
        
        print(f"\n{'='*80}")
        print(f"FENG SHUI SCORE: {self.module_name}")
        print(f"{'='*80}\n")
        
        print(f"Overall Score: {score.total_score}/100 {score.emoji}")
        print(f"Grade: {score.grade}")
        print(f"Status: {score.status}\n")
        
        print("Component Breakdown:")
        print(f"  Architecture:   {score.architecture_score:2d}/40 {self._bar(score.architecture_score, 40)}")
        print(f"  Code Quality:   {score.quality_score:2d}/30 {self._bar(score.quality_score, 30)}")
        print(f"  Security:       {score.security_score:2d}/20 {self._bar(score.security_score, 20)}")
        print(f"  Documentation:  {score.documentation_score:2d}/10 {self._bar(score.documentation_score, 10)}")
        
        print(f"\n{'='*80}\n")
        
        # Recommendations
        if score.total_score >= 90:
            print("🌟 Exemplary module! Consider using as template for others.")
        elif score.total_score >= 75:
            print("✅ Production-ready. Address warnings to reach excellence.")
        elif score.total_score >= 60:
            print("⚠️  Functional but needs improvement. Review failed checks.")
        else:
            print("🔴 Not production-ready. Significant refactoring required.")
    
    def _bar(self, score: int, max_score: int) -> str:
        """Generate visual progress bar"""
        pct = (score / max_score) * 100
        filled = int(pct / 5)  # 20 chars max
        empty = 20 - filled
        
        if pct >= 90:
            color = '█'
        elif pct >= 75:
            color = '▓'
        elif pct >= 60:
            color = '▒'
        else:
            color = '░'
        
        return f"[{color * filled}{'·' * empty}] {pct:.0f}%"


def score_module(module_name: str):
    """Score a specific module"""
    module_path = Path('modules') / module_name
    
    if not module_path.exists():
        print(f"ERROR: Module '{module_name}' not found")
        return None
    
    scorer = FengShuiScorer(module_path)
    scorer.print_report()
    return scorer.calculate_score()


def score_all_modules() -> Dict[str, FengShuiScore]:
    """Score all modules and generate summary"""
    modules_dir = Path('modules')
    scores = {}
    
    print("="*80)
    print("FENG SHUI AUDIT - ALL MODULES")
    print("="*80)
    
    for module_dir in sorted(modules_dir.iterdir()):
        if not module_dir.is_dir() or module_dir.name.startswith('.') or module_dir.name == '__pycache__':
            continue
        
        scorer = FengShuiScorer(module_dir)
        score = scorer.calculate_score()
        scores[module_dir.name] = score
    
    # Print summary table
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}\n")
    print(f"{'Module':<25} {'Score':>6} {'Grade':>6} {'Status'}")
    print("-" * 80)
    
    for name, score in sorted(scores.items(), key=lambda x: x[1].total_score, reverse=True):
        print(f"{name:<25} {score.total_score:>3}/100 {score.emoji:>2} {score.grade:>4}  {score.status}")
    
    # Statistics
    avg_score = sum(s.total_score for s in scores.values()) / len(scores) if scores else 0
    excellent = sum(1 for s in scores.values() if s.total_score >= 90)
    good = sum(1 for s in scores.values() if 75 <= s.total_score < 90)
    needs_work = sum(1 for s in scores.values() if s.total_score < 75)
    
    print(f"\n{'='*80}")
    print(f"Average Score: {avg_score:.1f}/100")
    print(f"Excellent (A): {excellent}")
    print(f"Good (B): {good}")
    print(f"Needs Work (C/D/F): {needs_work}")
    print(f"{'='*80}\n")
    
    return scores


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Score specific module
        score_module(sys.argv[1])
    else:
        # Score all modules
        score_all_modules()