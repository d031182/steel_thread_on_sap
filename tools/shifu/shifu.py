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
from .correlation_engine import CorrelationEngine, CorrelationPattern
from .wisdom_generator import WisdomGenerator, Teaching
from .growth_tracker import GrowthTracker


logger = logging.getLogger(__name__)


# ShiFuInsight is an alias for CorrelationPattern (same structure, different semantic meaning)
ShiFuInsight = CorrelationPattern


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
        self.wisdom_generator = WisdomGenerator(verbose=verbose)
        self.growth_tracker = GrowthTracker(verbose=verbose)
        
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
    
    def teach_through_insight(
        self,
        insights: List[ShiFuInsight],
        fengshui_score: float,
        guwu_score: float
    ) -> List[Teaching]:
        """
        Share wisdom through the Wisdom Generator (Phase 3)
        
        Args:
            insights: Correlations found
            fengshui_score: Overall code quality score
            guwu_score: Overall test quality score
        
        Returns:
            List of Teaching objects with prioritized wisdom
        """
        # Use Wisdom Generator to transform correlations into teachings
        teachings = self.wisdom_generator.generate_teachings(
            patterns=insights,
            fengshui_score=fengshui_score,
            guwu_score=guwu_score
        )
        
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
    
    def weekly_analysis(self, save_teachings: bool = True) -> Dict:
        """
        Run Shi Fu's weekly quality analysis (Phase 3+5 Enhanced)
        
        Args:
            save_teachings: Whether to save teachings to markdown file
        
        Returns:
            Complete analysis report with prioritized teachings + growth insights
        """
        if self.verbose:
            logger.info("[Shi Fu 师傅] Beginning weekly observation...")
        
        # Observe disciples
        observations = self.observe_disciples()
        
        # Find correlations
        insights = self.find_correlations(observations)
        
        # Get scores for wisdom generation
        fengshui_score = self.fengshui.get_overall_score()
        guwu_score = self.guwu.get_overall_score()
        
        # Generate teachings (Phase 3: With Wisdom Generator)
        teachings = self.teach_through_insight(insights, fengshui_score, guwu_score)
        
        # Generate summary teaching
        summary_teaching = self.wisdom_generator.generate_summary_teaching(
            teachings,
            fengshui_score,
            guwu_score
        )
        
        # Save teachings to file if requested
        teachings_file = None
        if save_teachings and teachings:
            teachings_file = self.wisdom_generator.save_teachings_to_file(teachings)
        
        # Assess ecosystem health
        health = self.assess_ecosystem_health()
        
        # Generate quick summary
        quick_summary = self.wisdom_generator.generate_quick_summary(teachings)
        
        # Phase 5: Record snapshot for growth tracking
        urgent_count = sum(1 for i in insights if i.severity == 'URGENT')
        self.growth_tracker.record_snapshot(
            fengshui_score=fengshui_score,
            guwu_score=guwu_score,
            ecosystem_score=health.ecosystem_score,
            pattern_count=len(insights),
            urgent_count=urgent_count
        )
        
        # Phase 5: Analyze trends (if enough data)
        trend = self.growth_tracker.analyze_trends(period_days=30)
        
        # Phase 5: Celebrations (if trends available)
        celebrations = []
        if trend:
            celebrations = self.growth_tracker.identify_celebrations(trend)
        
        # Phase 5: Growth suggestions
        growth_suggestions = []
        if trend:
            insights_dict = [
                {'pattern_name': i.pattern_name}
                for i in insights
            ]
            growth_suggestions = self.growth_tracker.suggest_growth_opportunities(
                trend,
                insights_dict
            )
        
        # Phase 5: Predictions
        prediction = None
        if trend:
            prediction = self.growth_tracker.predict_trajectory(trend, weeks_ahead=4)
        
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
            'teachings': teachings,  # Now List[Teaching] objects
            'summary_teaching': summary_teaching,
            'quick_summary': quick_summary,
            'teachings_file': teachings_file,
            'health': {
                'ecosystem_score': health.ecosystem_score,
                'fengshui_score': health.fengshui_score,
                'guwu_score': health.guwu_score,
                'correlation_count': health.correlation_count,
                'teaching': health.teaching
            },
            # Phase 5: Growth tracking
            'growth': {
                'trend': trend,
                'celebrations': celebrations,
                'growth_suggestions': growth_suggestions,
                'prediction': prediction
            }
        }
        
        if self.verbose:
            logger.info("[Shi Fu 师傅] Analysis complete. Wisdom + Growth insights generated.")
            if teachings_file:
                logger.info(f"[Shi Fu 师傅] Teachings saved to: {teachings_file}")
            if celebrations:
                logger.info(f"[Shi Fu 师傅] {len(celebrations)} celebrations identified! 🎉")
        
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
        '--session-start',
        action='store_true',
        help='Run session start check (Cline integration)'
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
        report = shifu.weekly_analysis(save_teachings=True)
        
        # Print summary teaching (formatted beautifully) with Unicode support
        try:
            print(report['summary_teaching'])
        except UnicodeEncodeError:
            # Windows cmd.exe can't print Unicode, encode safely
            print(report['summary_teaching'].encode('ascii', 'ignore').decode('ascii'))
        
        # Print quick summary stats
        print("\n" + "="*70)
        print("Quick Summary")
        print("="*70)
        summary = report['quick_summary']
        print(f"Total Patterns: {summary['total']}")
        print(f"  🔴 URGENT: {summary.get('urgent', 0)}")
        print(f"  🟠 HIGH: {summary.get('high', 0)}")
        print(f"  🟢 MEDIUM: {summary.get('medium', 0)}")
        print(f"  🔵 LOW: {summary.get('low', 0)}")
        
        if summary.get('top_recommendations'):
            print("\nTop Recommendations:")
            for i, rec in enumerate(summary['top_recommendations'], 1):
                print(f"\n{i}. {rec['title']}")
                print(f"   Severity: {rec['severity']} | Confidence: {rec['confidence']}")
                print(f"   Effort: {rec['effort']} | Priority: {rec['priority_score']}")
        
        if report.get('teachings_file'):
            print(f"\n📄 Full teachings saved to: {report['teachings_file']}")
        
        print("\n" + "="*70)
        print("Ecosystem Health")
        print("="*70)
        health = report['health']
        print(f"Overall Score: {health['ecosystem_score']:.1f}/100")
        print(f"Feng Shui (Code): {health['fengshui_score']:.1f}/100")
        print(f"Gu Wu (Tests): {health['guwu_score']:.1f}/100")
        print(f"Cross-domain Issues: {health['correlation_count']}")
    
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
    
    elif args.session_start:
        # Cline integration: session start check
        from .cline_integration import session_start_hook, format_for_chat
        
        result = session_start_hook()
        message = format_for_chat(result)
        
        try:
            print(message)
        except UnicodeEncodeError:
            print(message.encode('ascii', 'ignore').decode('ascii'))
        
        # If recommendations exist, show them
        if result.get('recommendations'):
            print("\n" + "="*70)
            print("Top Recommendations")
            print("="*70)
            for i, rec in enumerate(result['recommendations'][:3], 1):
                print(f"\n{i}. {rec['title']}")
                print(f"   Priority: {rec['priority_score']:.0f}/100")
                print(f"   Effort: {rec['effort']}")
                print(f"   Quick Action: {rec['quick_action']}")
    
    elif args.query:
        answer = shifu.query(args.query)
        print(answer)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()