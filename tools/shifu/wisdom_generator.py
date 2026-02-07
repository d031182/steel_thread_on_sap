"""
Wisdom Generator: Synthesizing Insights into Teachings
======================================================

Transforms raw correlations into Shi Fu's teachings.

Takes pattern matches from correlation engine and:
1. Prioritizes across multiple patterns
2. Calculates combined impact
3. Generates actionable wisdom
4. Formats as teaching messages

Philosophy: "Data becomes information, information becomes wisdom,
wisdom becomes action."
"""

import logging
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


logger = logging.getLogger(__name__)


@dataclass
class Teaching:
    """A complete teaching from Shi Fu"""
    id: str
    title: str
    severity: str  # URGENT/HIGH/MEDIUM/LOW
    confidence: float  # 0.0-1.0
    affected_modules: List[str]
    
    # The teaching itself
    observation: str  # What Shi Fu observes
    root_cause: str  # Why this happens
    wisdom: str  # Shi Fu's insight
    action_plan: str  # What to do
    
    # Metrics
    estimated_effort: str
    expected_value: str
    priority_score: float  # 0-100 (for sorting)
    
    # Metadata
    patterns_involved: List[str]
    timestamp: str


class WisdomGenerator:
    """
    Synthesizes raw correlation patterns into actionable teachings
    
    Shi Fu's role: Not just report problems, but teach understanding.
    """
    
    def __init__(self, verbose: bool = False):
        """Initialize wisdom generator"""
        self.verbose = verbose
    
    def generate_teachings(
        self,
        patterns: List,  # List[CorrelationPattern]
        fengshui_score: float,
        guwu_score: float
    ) -> List[Teaching]:
        """
        Transform patterns into teachings
        
        Args:
            patterns: Raw correlation patterns detected
            fengshui_score: Overall code quality score
            guwu_score: Overall test quality score
        
        Returns:
            List of Teaching objects, prioritized
        """
        if self.verbose:
            logger.info(f"[Wisdom Generator] Synthesizing {len(patterns)} patterns into teachings...")
        
        teachings = []
        
        for pattern in patterns:
            teaching = self._create_teaching_from_pattern(
                pattern,
                fengshui_score,
                guwu_score
            )
            teachings.append(teaching)
        
        # Sort by priority score (highest first)
        teachings.sort(key=lambda t: t.priority_score, reverse=True)
        
        if self.verbose:
            urgent = sum(1 for t in teachings if t.severity == 'URGENT')
            logger.info(f"[Wisdom Generator] Generated {len(teachings)} teachings ({urgent} URGENT)")
        
        return teachings
    
    def _create_teaching_from_pattern(
        self,
        pattern,
        fengshui_score: float,
        guwu_score: float
    ) -> Teaching:
        """
        Create a teaching from a single correlation pattern
        
        Adds Shi Fu's philosophical framing and actionable guidance.
        """
        # Calculate priority score
        priority_score = self._calculate_priority_score(
            pattern.severity,
            pattern.confidence,
            len(pattern.affected_modules) if hasattr(pattern, 'affected_modules') else 1
        )
        
        # Generate observation (what Shi Fu sees)
        observation = self._generate_observation(pattern)
        
        # Generate wisdom (Shi Fu's insight)
        wisdom = self._generate_wisdom(pattern, fengshui_score, guwu_score)
        
        # Generate action plan (structured steps)
        action_plan = self._generate_action_plan(pattern)
        
        return Teaching(
            id=pattern.id,
            title=f"Teaching: {pattern.pattern_name}",
            severity=pattern.severity,
            confidence=pattern.confidence,
            affected_modules=getattr(pattern, 'affected_modules', []),
            observation=observation,
            root_cause=pattern.root_cause,
            wisdom=wisdom,
            action_plan=action_plan,
            estimated_effort=pattern.estimated_effort,
            expected_value=pattern.combined_value,
            priority_score=priority_score,
            patterns_involved=[pattern.pattern_name],
            timestamp=datetime.now().isoformat()
        )
    
    def _calculate_priority_score(
        self,
        severity: str,
        confidence: float,
        affected_module_count: int
    ) -> float:
        """
        Calculate priority score (0-100) for sorting
        
        Factors:
        - Severity (40%): URGENT=100, HIGH=75, MEDIUM=50, LOW=25
        - Confidence (30%): How certain we are
        - Scope (30%): How many modules affected
        """
        # Severity contribution
        severity_map = {'URGENT': 100, 'HIGH': 75, 'MEDIUM': 50, 'LOW': 25}
        severity_score = severity_map.get(severity, 25)
        
        # Confidence contribution (already 0-1, scale to 0-100)
        confidence_score = confidence * 100
        
        # Scope contribution (normalize: 5+ modules = max)
        scope_score = min(100, (affected_module_count / 5.0) * 100)
        
        # Weighted combination
        priority = (
            severity_score * 0.4 +
            confidence_score * 0.3 +
            scope_score * 0.3
        )
        
        return priority
    
    def _generate_observation(self, pattern) -> str:
        """
        Generate Shi Fu's observation - what he sees
        
        Format: Clear statement of what's happening
        """
        return f"""
My children, I observe a pattern in your work:

**In your code** (Feng Shui reports):
{pattern.fengshui_evidence}

**In your tests** (Gu Wu reports):
{pattern.guwu_evidence}

These are not separate problems - they are connected.
"""
    
    def _generate_wisdom(
        self,
        pattern,
        fengshui_score: float,
        guwu_score: float
    ) -> str:
        """
        Generate Shi Fu's wisdom - the deeper insight
        
        Adds philosophical context beyond just "here's the problem"
        """
        # Determine ecosystem state
        ecosystem_balance = self._assess_balance(fengshui_score, guwu_score)
        
        wisdom = f"""
## Shi Fu's Insight

{pattern.root_cause}

**The Deeper Truth**:
Your ecosystem shows: {ecosystem_balance}

When code quality (Feng Shui: {fengshui_score:.1f}/100) and 
test quality (Gu Wu: {guwu_score:.1f}/100) are both suffering,
this tells me the root cause affects BOTH disciplines.

Fix the root, both branches heal.
"""
        
        # Add severity-specific wisdom
        if pattern.severity == 'URGENT':
            wisdom += """

**Urgency**: This pattern requires immediate attention.
Like a crack in the foundation, it will worsen if ignored.
Other issues may be symptoms of this root cause.
"""
        
        return wisdom
    
    def _generate_action_plan(self, pattern) -> str:
        """
        Generate structured action plan
        
        Breaks recommendation into clear, executable steps
        """
        # Parse recommendation into steps
        steps = self._parse_recommendation_to_steps(pattern.recommendation)
        
        action_plan = f"""
## Action Plan

**Estimated Effort**: {pattern.estimated_effort}  
**Expected Value**: {pattern.combined_value}

**Steps to Resolution**:

{steps}

**Validation Criteria**:
- [ ] Feng Shui score improves
- [ ] Gu Wu metrics stabilize
- [ ] Affected modules show improvement
- [ ] Pattern no longer detected in next analysis

**Measurement**:
Before: Run Shi Fu analysis, note current scores
After: Re-run analysis, compare improvements
Target: This pattern should not appear in next weekly analysis
"""
        return action_plan
    
    def _assess_balance(self, fengshui_score: float, guwu_score: float) -> str:
        """Assess balance between code and test quality"""
        diff = abs(fengshui_score - guwu_score)
        avg = (fengshui_score + guwu_score) / 2
        
        if diff < 10:
            if avg >= 80:
                return "Balanced harmony (both disciples excel)"
            elif avg >= 60:
                return "Balanced mediocrity (both need improvement)"
            else:
                return "Balanced weakness (both disciples struggle)"
        else:
            stronger = "Feng Shui" if fengshui_score > guwu_score else "Gu Wu"
            weaker = "Gu Wu" if fengshui_score > guwu_score else "Feng Shui"
            return f"Imbalance detected ({stronger} stronger, {weaker} needs attention)"
    
    def _parse_recommendation_to_steps(self, recommendation: str) -> str:
        """
        Parse recommendation text into numbered steps
        
        Looks for numbered lists, bullet points, or sections
        """
        # If already has structure, return as-is
        if any(marker in recommendation for marker in ['1.', '2.', '- ', '* ']):
            return recommendation
        
        # Otherwise, try to break into paragraphs as steps
        lines = [line.strip() for line in recommendation.split('\n') if line.strip()]
        
        if len(lines) <= 1:
            return f"1. {recommendation}"
        
        # Number the steps
        numbered = []
        for i, line in enumerate(lines, 1):
            numbered.append(f"{i}. {line}")
        
        return '\n'.join(numbered)
    
    def generate_summary_teaching(
        self,
        teachings: List[Teaching],
        fengshui_score: float,
        guwu_score: float
    ) -> str:
        """
        Generate overall summary teaching across all patterns
        
        Shi Fu's holistic view of the entire ecosystem
        """
        if not teachings:
            return self._generate_healthy_ecosystem_message(fengshui_score, guwu_score)
        
        # Categorize teachings
        urgent = [t for t in teachings if t.severity == 'URGENT']
        high = [t for t in teachings if t.severity == 'HIGH']
        
        summary = f"""
╔════════════════════════════════════════════════════════════════════╗
║                    Shi Fu's Weekly Teachings                       ║
║                    师傅的每周教诲                                    ║
╠════════════════════════════════════════════════════════════════════╣

## Ecosystem Assessment

**Feng Shui** (Code Quality): {fengshui_score:.1f}/100
**Gu Wu** (Test Quality): {guwu_score:.1f}/100
**Balance**: {self._assess_balance(fengshui_score, guwu_score)}

## Patterns Detected

Total: {len(teachings)} correlations found
- 🔴 URGENT: {len(urgent)} patterns
- 🟠 HIGH: {len(high)} patterns
- 🟢 MEDIUM/LOW: {len(teachings) - len(urgent) - len(high)} patterns

## Master's Guidance

"""
        
        if urgent:
            summary += f"""
**IMMEDIATE ATTENTION REQUIRED**:

The most urgent pattern is: {urgent[0].title}

{urgent[0].wisdom}

Start here. Other issues may resolve as symptoms of this root cause.

"""
        
        summary += f"""
**Holistic Approach**:

Do not treat these as {len(teachings)} separate problems.
They are {len(teachings)} symptoms of ecosystem imbalance.

The wise developer:
1. Addresses root causes, not symptoms
2. Fixes code AND tests together
3. Measures improvement holistically
4. Learns from patterns

╚════════════════════════════════════════════════════════════════════╝

Full teachings available in: docs/shifu-teachings/[date]-weekly.md
"""
        
        return summary
    
    def _generate_healthy_ecosystem_message(
        self,
        fengshui_score: float,
        guwu_score: float
    ) -> str:
        """Message when no patterns detected (healthy state)"""
        return f"""
╔════════════════════════════════════════════════════════════════════╗
║                    Shi Fu's Weekly Teachings                       ║
║                    师傅的每周教诲                                    ║
╠════════════════════════════════════════════════════════════════════╣

## Ecosystem Assessment

**Feng Shui** (Code Quality): {fengshui_score:.1f}/100
**Gu Wu** (Test Quality): {guwu_score:.1f}/100
**Balance**: {self._assess_balance(fengshui_score, guwu_score)}

## Master's Observation

The ecosystem flows harmoniously. No significant correlations detected.

Both disciples work in balance:
- Code architecture is sound
- Tests are reliable
- No cross-domain issues found

**The Teaching**:
This is the state to maintain. When new features are added,
ensure they follow the established patterns that create this harmony.

Continue your excellent work.

╚════════════════════════════════════════════════════════════════════╝
"""
    
    def format_teaching_as_markdown(self, teaching: Teaching) -> str:
        """
        Format a teaching as a complete markdown document
        
        Used for generating teaching files in docs/shifu-teachings/
        """
        markdown = f"""# {teaching.title}

**Date**: {teaching.timestamp}  
**Severity**: {teaching.severity}  
**Confidence**: {teaching.confidence:.0%}  
**Priority Score**: {teaching.priority_score:.1f}/100

---

{teaching.observation}

---

{teaching.wisdom}

---

{teaching.action_plan}

---

## Affected Modules

{chr(10).join(f"- {module}" for module in teaching.affected_modules)}

## Related Patterns

{chr(10).join(f"- {pattern}" for pattern in teaching.patterns_involved)}

---

*This teaching was generated by Shi Fu (师傅), the Master Teacher.*  
*"Code and Tests are Yin and Yang - when one is weak, both suffer."*
"""
        return markdown
    
    def save_teachings_to_file(
        self,
        teachings: List[Teaching],
        output_dir: str = "docs/shifu-teachings"
    ) -> str:
        """
        Save teachings to markdown file
        
        Args:
            teachings: List of teachings to save
            output_dir: Directory to save to
        
        Returns:
            Path to saved file
        """
        from pathlib import Path
        
        # Create output directory if needed
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d')
        filename = f"{timestamp}-weekly-teachings.md"
        filepath = output_path / filename
        
        # Generate content
        content = self._generate_teaching_file_content(teachings)
        
        # Write file
        filepath.write_text(content, encoding='utf-8')
        
        if self.verbose:
            logger.info(f"[Wisdom Generator] Teachings saved to: {filepath}")
        
        return str(filepath)
    
    def _generate_teaching_file_content(self, teachings: List[Teaching]) -> str:
        """Generate complete markdown file with all teachings"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        content = f"""# Shi Fu's Weekly Teachings

**Date**: {timestamp}  
**Teachings Count**: {len(teachings)}

---

## Summary

This document contains {len(teachings)} teachings from Shi Fu (师傅), the Master Teacher.

Each teaching reveals a correlation between code quality (Feng Shui) and test quality (Gu Wu).

**Priority Distribution**:
- 🔴 URGENT: {sum(1 for t in teachings if t.severity == 'URGENT')}
- 🟠 HIGH: {sum(1 for t in teachings if t.severity == 'HIGH')}
- 🟢 MEDIUM: {sum(1 for t in teachings if t.severity == 'MEDIUM')}
- 🔵 LOW: {sum(1 for t in teachings if t.severity == 'LOW')}

---

"""
        
        # Add each teaching
        for i, teaching in enumerate(teachings, 1):
            content += f"\n---\n\n## Teaching {i}: {teaching.title}\n\n"
            content += self.format_teaching_as_markdown(teaching)
            content += "\n"
        
        # Add footer
        content += """
---

## How to Use These Teachings

1. **Read in priority order** (URGENT first)
2. **Follow action plans** (step-by-step)
3. **Measure improvements** (before/after scores)
4. **Validate resolution** (pattern should disappear)

## Philosophy

*"The student sees problems. The master sees patterns.*  
*The student fixes symptoms. The master heals roots.*  
*The student works harder. The master works wiser."*

— Shi Fu (师傅)

---

*Generated by Shi Fu Quality Ecosystem Orchestrator*  
*tools/shifu/wisdom_generator.py*
"""
        
        return content
    
    def generate_quick_summary(self, teachings: List[Teaching]) -> Dict:
        """
        Generate quick summary for CLI output
        
        Returns:
            Dictionary with summary statistics and top recommendations
        """
        if not teachings:
            return {
                'total': 0,
                'urgent': 0,
                'high': 0,
                'message': 'No correlations detected. Ecosystem is healthy.'
            }
        
        # Get top 3 by priority
        top_3 = teachings[:3]
        
        summary = {
            'total': len(teachings),
            'urgent': sum(1 for t in teachings if t.severity == 'URGENT'),
            'high': sum(1 for t in teachings if t.severity == 'HIGH'),
            'medium': sum(1 for t in teachings if t.severity == 'MEDIUM'),
            'low': sum(1 for t in teachings if t.severity == 'LOW'),
            'avg_priority': sum(t.priority_score for t in teachings) / len(teachings),
            'top_recommendations': [
                {
                    'title': t.title,
                    'severity': t.severity,
                    'confidence': f"{t.confidence:.0%}",
                    'effort': t.estimated_effort,
                    'priority_score': f"{t.priority_score:.1f}/100"
                }
                for t in top_3
            ]
        }
        
        return summary