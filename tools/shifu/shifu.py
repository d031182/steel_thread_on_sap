"""
Shi Fu (师傅): Main Orchestrator - The Master Teacher
======================================================

The wise elder who observes both disciples (Feng Shui + Gu Wu),
sees patterns they miss, and guides their growth with wisdom.

Core Responsibilities:
1. Observe both disciples' work (collect data)
2. Find correlations (code issues ↔ test issues)
3. Generate insights (holistic wisdom)
4. Guide growth (suggest improvements)

Philosophy:
"Code and Tests are not separate - they are Yin and Yang.
 When one is weak, the other suffers. Heal the root, both grow."
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from .disciples.fengshui_interface import FengShuiInterface
from .disciples.guwu_interface import GuWuInterface
from .ecosystem_analyzer import EcosystemAnalyzer
from .correlation_engine import CorrelationEngine


logger = logging.getLogger(__name__)


@dataclass
class EcosystemHealth:
    """Overall quality ecosystem assessment"""
    ecosystem_score: float  # 0-100
    fengshui_score: float   # 0-100
    guwu_score: float       # 0-100
    correlation_penalty: float
    correlation_count: int
    timestamp: str
    teaching: Optional[str] = None


@dataclass
class ShiFuInsight:
    """A teaching from Shi Fu based on observations"""
    id: str
    pattern_name: str
    confidence: float  # 0.0-1.0
    severity: str  # URGENT/HIGH/MEDIUM/LOW
    fengshui_evidence: str
    guwu_evidence: str
    root_cause: str
    recommendation: str
    estimated_effort: str
    combined_value: str
    timestamp: str


class ShiFu:
    """
    The Master Teacher - Quality Ecosystem Orchestrator
    
    Observes both Feng Shui (code quality) and Gu Wu (test quality),
    finds correlations, and provides holistic wisdom.
    """
    
    def __init__(
        self,
        project_root: Optional[Path] = None,
        verbose: bool = False
    ):
        """
        Initialize Shi Fu
        
        Args:
            project_root: Root directory of the project
            verbose: Enable detailed logging
        """
        self.project_root = project_root or Path.cwd()
        self.verbose = verbose
        
        # Initialize disciples (interfaces to child systems)
        self.fengshui = FengShuiInterface(self.project_root)
        self.guwu = GuWuInterface(self.project_root)
        
        # Initialize core components
        self.analyzer = EcosystemAnalyzer(self.fengshui, self.guwu)
        self.correlation_engine = CorrelationEngine()
        
        if self.verbose:
            logger.info("[Shi Fu 师傅] The Master Teacher awakens...")
    
    def observe_disciples(self) -> Dict:
        """
        Watch both disciples, gather their recent work
        
        Returns:
            Dictionary with Feng Shui and Gu Wu data
        """
        if self.verbose:
            logger.info("[Shi Fu 师傅] Observing disciples...")
        
        observations = self.analyzer.collect_recent_data(days=7)
        
        if self.verbose:
            logger.info(f"[Feng Shui] {observations['fengshui']['violation_count']} violations")
            logger.info(f"[Gu Wu] {observations['guwu']['test_count']} tests executed")
        
        return observations
    
    def find_correlations(self, observations: Dict) -> List[ShiFuInsight]:
        """
        Apply master's wisdom: Find cross-domain patterns
        
        Args:
            observations: Data from both disciples
        
        Returns:
            List of insights (correlations found)
        """
        if self.verbose:
            logger.info("[Shi Fu 师傅] Seeking patterns across disciples...")
        
        insights = self.correlation_engine.detect_patterns(
            fengshui_data=observations['fengshui'],
            guwu_data=observations['guwu']
        )
        
        if self.verbose:
            urgent = sum(1 for i in insights if i.severity == 'URGENT')
            logger.info(f"[Shi Fu 师傅] Found {len(insights)} correlations ({urgent} URGENT)")
        
        return insights
    
    def teach_through_insight(self, insights: List[ShiFuInsight]) -> List[str]:
        """
        Share wisdom, don't command
        
        Args:
            insights: Correlations found
        
        Returns:
            List of teaching messages
        """
        teachings = []
        
        for insight in insights:
            teaching = f"""
## Shi Fu's Teaching: {insight.pattern_name}

My children, I observe a connection you may not see:

**Feng Shui found** (in your code):
{insight.fengshui_evidence}

**Gu Wu found** (in your tests):
{insight.guwu_evidence}

**The connection is**:
{insight.root_cause}

**If you address the root cause, both will improve**:
{insight.recommendation}

This is not two problems - it is one problem seen from two angles.

**Priority**: {insight.severity}
**Effort**: {insight.estimated_effort}
**Value**: {insight.combined_value}

Reflect on this wisdom, then choose your path.

---
"""
            teachings.append(teaching)
        
        return teachings
    
    def assess_ecosystem_health(self) -> EcosystemHealth:
        """
        Holistic health assessment (not just separate scores)
        
        Returns:
            EcosystemHealth with combined analysis
        """
        if self.verbose:
            logger.info("[Shi Fu 师傅] Assessing quality ecosystem...")
        
        # Get individual scores
        fengshui_score = self.fengshui.get_overall_score()
        guwu_score = self.guwu.get_overall_score()
        
        # Gather recent observations
        observations = self.observe_disciples()
        
        # Find cross-domain issues
        insights = self.find_correlations(observations)
        
        # Calculate ecosystem penalty
        correlation_penalty = len(insights) * 3  # -3 points per correlation issue
        
        # Holistic score (weighted combination minus penalties)
        ecosystem_score = max(0, (
            (fengshui_score * 0.6) +  # Code weighted 60%
            (guwu_score * 0.4) -       # Tests weighted 40%
            correlation_penalty         # Cross-domain issues
        ))
        
        # Generate wisdom
        teaching = self._generate_health_wisdom(
            fengshui_score, guwu_score, insights
        )
        
        return EcosystemHealth(
            ecosystem_score=ecosystem_score,
            fengshui_score=fengshui_score,
            guwu_score=guwu_score,
            correlation_penalty=correlation_penalty,
            correlation_count=len(insights),
            timestamp=datetime.now().isoformat(),
            teaching=teaching
        )
    
    def _generate_health_wisdom(
        self,
        fengshui_score: float,
        guwu_score: float,
        insights: List[ShiFuInsight]
    ) -> str:
        """Generate wisdom based on ecosystem state"""
        
        if not insights:
            return "The ecosystem flows harmoniously. Both disciples work in balance."
        
        urgent_insights = [i for i in insights if i.severity == 'URGENT']
        
        if urgent_insights:
            top_insight = urgent_insights[0]
            return f"Focus on {top_insight.pattern_name} first. This one fix will heal both code and tests."
        
        return f"{len(insights)} patterns detected. Begin with highest priority for greatest impact."
    
    def weekly_analysis(self) -> Dict:
        """
        Run Shi Fu's weekly quality analysis
        
        Returns:
            Complete analysis report
        """
        if self.verbose:
            logger.info("[Shi Fu 师傅] Beginning weekly observation...")
        
        # Observe disciples
        observations = self.observe_disciples()
        
        # Find correlations
        insights = self.find_correlations(observations)
        
        # Generate teachings
        teachings = self.teach_through_insight(insights)
        
        # Assess ecosystem health
        health = self.assess_ecosystem_health()
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'observations': observations,
            'insights': [
                {
                    'pattern': i.pattern_name,
                    'severity': i.severity,
                    'confidence': i.confidence,
                    'root_cause': i.root_cause,
                    'recommendation': i.recommendation
                }
                for i in insights
            ],
            'teachings': teachings,
            'health': {
                'ecosystem_score': health.ecosystem_score,
                'fengshui_score': health.fengshui_score,
                'guwu_score': health.guwu_score,
                'correlation_count': health.correlation_count,
                'teaching': health.teaching
            }
        }
        
        if self.verbose:
            logger.info("[Shi Fu 师傅] Analysis complete. Wisdom generated.")
        
        return report
    
    def query(self, question: str) -> str:
        """
        Ask Shi Fu a specific question
        
        Args:
            question: User's question about quality
        
        Returns:
            Shi Fu's wisdom in response
        """
        if self.verbose:
            logger.info(f"[Shi Fu 师傅] Contemplating: {question}")
        
        # TODO: Implement Q&A system (Phase 2+)
        return f"""
[Shi Fu 师傅] My child, your question: "{question}"

This wisdom requires deeper implementation (Phase 2).
For now, run weekly analysis to see patterns:

    python -m tools.shifu.shifu --weekly-analysis

The Master rests, but will return with fuller wisdom soon.
"""


def main():
    """CLI entry point for Shi Fu"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Shi Fu (师傅): Quality Ecosystem Orchestrator"
    )
    parser.add_argument(
        '--weekly-analysis',
        action='store_true',
        help='Run weekly quality ecosystem analysis'
    )
    parser.add_argument(
        '--health-check',
        action='store_true',
        help='Get overall ecosystem health status'
    )
    parser.add_argument(
        '--query',
        type=str,
        help='Ask Shi Fu a specific question'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable detailed logging'
    )
    
    args = parser.parse_args()
    
    # Initialize Shi Fu
    shifu = ShiFu(verbose=args.verbose)
    
    if args.weekly_analysis:
        print("="*70)
        print("Shi Fu's Weekly Quality Analysis")
        print("="*70)
        
        report = shifu.weekly_analysis()
        
        print(f"\nTimestamp: {report['timestamp']}")
        print(f"\nInsights Found: {len(report['insights'])}")
        
        for teaching in report['teachings']:
            print(teaching)
        
        print("\n" + "="*70)
        print("Ecosystem Health")
        print("="*70)
        health = report['health']
        print(f"Overall Score: {health['ecosystem_score']:.1f}/100")
        print(f"Feng Shui (Code): {health['fengshui_score']:.1f}/100")
        print(f"Gu Wu (Tests): {health['guwu_score']:.1f}/100")
        print(f"Cross-domain Issues: {health['correlation_count']}")
        print(f"\nMaster's Guidance: {health['teaching']}")
    
    elif args.health_check:
        health = shifu.assess_ecosystem_health()
        
        print("╔" + "═"*68 + "╗")
        print("║  Shi Fu's Quality Ecosystem Assessment" + " "*29 + "║")
        print("╠" + "═"*68 + "╣")
        print(f"║  Ecosystem Health: {health.ecosystem_score:5.1f}/100" + " "*41 + "║")
        print(f"║  Feng Shui (Code): {health.fengshui_score:5.1f}/100" + " "*41 + "║")
        print(f"║  Gu Wu (Tests):    {health.guwu_score:5.1f}/100" + " "*41 + "║")
        print(f"║  Correlations:     {health.correlation_count:5d} patterns" + " "*40 + "║")
        print("║" + " "*68 + "║")
        print(f"║  {health.teaching[:64]:<64} ║")
        print("╚" + "═"*68 + "╝")
    
    elif args.query:
        answer = shifu.query(args.query)
        print(answer)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()