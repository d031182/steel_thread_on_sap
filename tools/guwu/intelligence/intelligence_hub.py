"""
Gu Wu Phase 7.5: Intelligence Hub - Integration Layer

Unified interface for all intelligence capabilities.
"""

from typing import Dict, List, Optional
from .recommendations import RecommendationEngine
from .dashboard import DashboardGenerator
from .predictive import PredictiveEngine, PreflightChecker


class IntelligenceHub:
    """
    Unified intelligence interface for Gu Wu.
    
    Combines all Phase 7 capabilities into single API:
    - Recommendations (actionable insights)
    - Dashboard (visual health overview)
    - Predictive Analytics (failure forecasting)
    """
    
    def __init__(self, db_path: str = "tools/guwu/guwu_metrics.db"):
        self.db_path = db_path
        
        # Initialize all engines
        self.recommendation_engine = RecommendationEngine(db_path)
        self.dashboard_generator = DashboardGenerator(db_path)
        self.predictive_engine = PredictiveEngine(db_path)
        self.preflight_checker = PreflightChecker(db_path)
    
    def get_full_intelligence_report(self) -> str:
        """
        Generate comprehensive intelligence report.
        
        Combines dashboard, recommendations, and predictions.
        """
        sections = []
        
        # Header
        sections.append(self._generate_header())
        
        # Dashboard
        sections.append(self.dashboard_generator.generate())
        
        # Recommendations
        recommendations = self.recommendation_engine.get_recommendations()
        if recommendations:
            sections.append(self._format_recommendations_summary(recommendations))
        
        # Predictions
        predictions = self.predictive_engine.predict_failures()
        if predictions:
            sections.append(self._format_predictions_summary(predictions))
        
        # Footer
        sections.append(self._generate_footer())
        
        return "\n\n".join(sections)
    
    def run_preflight_check(self) -> str:
        """Run pre-flight check for CI/CD"""
        return self.preflight_checker.run_preflight()
    
    def get_quick_status(self) -> Dict:
        """
        Get quick status overview (for programmatic access).
        
        Returns:
            Dict with health score, risk level, and key metrics
        """
        try:
            # Get health metrics
            health = self.dashboard_generator._get_health_metrics()
            
            # Get preflight report
            preflight = self.predictive_engine.get_preflight_report()
            
            # Get recommendations count
            recommendations = self.recommendation_engine.get_recommendations()
            
            return {
                'health_score': health.health_score,
                'health_rating': self._get_health_rating(health.health_score),
                'total_tests': health.total_tests,
                'passing_tests': health.passing_tests,
                'flaky_tests': health.flaky_tests,
                'slow_tests': health.slow_tests,
                'coverage_pct': health.coverage_pct,
                'risk_level': preflight['risk_level'],
                'pending_recommendations': len(recommendations),
                'likely_failures': len(preflight['likely_failures'])
            }
        except Exception:
            return {
                'health_score': 0.0,
                'health_rating': 'UNKNOWN',
                'total_tests': 0,
                'passing_tests': 0,
                'flaky_tests': 0,
                'slow_tests': 0,
                'coverage_pct': 0.0,
                'risk_level': 'UNKNOWN',
                'pending_recommendations': 0,
                'likely_failures': 0
            }
    
    def _generate_header(self) -> str:
        """Generate report header"""
        return """
{'=' * 70}
  GU WU INTELLIGENCE HUB
  Comprehensive Test Suite Intelligence Report
{'=' * 70}
"""
    
    def _generate_footer(self) -> str:
        """Generate report footer"""
        return f"""
{'=' * 70}
  
  For detailed analysis:
  - Dashboard:        python -m tests.guwu.intelligence.dashboard
  - Recommendations:  python -m tests.guwu.intelligence.recommendations
  - Pre-flight:       python -m tests.guwu.intelligence.predictive
  
{'=' * 70}
"""
    
    def _format_recommendations_summary(self, recommendations: List[Dict]) -> str:
        """Format recommendations summary"""
        critical = sum(1 for r in recommendations if r['priority'] == 'CRITICAL')
        high = sum(1 for r in recommendations if r['priority'] == 'HIGH')
        
        return f"""
[RECOMMENDATIONS SUMMARY]

  Total:    {len(recommendations)}
  Critical: {critical}
  High:     {high}
  
  Run for details: python -m tests.guwu.intelligence.recommendations
"""
    
    def _format_predictions_summary(self, predictions: List) -> str:
        """Format predictions summary"""
        high_conf = sum(1 for p in predictions if p.confidence > 0.8)
        
        return f"""
[PREDICTION SUMMARY]

  Likely Failures: {len(predictions)}
  High Confidence: {high_conf} (>80%)
  
  Run for details: python -m tests.guwu.intelligence.predictive
"""
    
    def _get_health_rating(self, score: float) -> str:
        """Convert health score to rating"""
        if score >= 0.9:
            return "EXCELLENT"
        elif score >= 0.8:
            return "GOOD"
        elif score >= 0.7:
            return "FAIR"
        else:
            return "NEEDS ATTENTION"


def main():
    """CLI entry point"""
    import sys
    import io
    
    # Ensure UTF-8 encoding for Windows
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    
    hub = IntelligenceHub()
    report = hub.get_full_intelligence_report()
    print(report)


if __name__ == "__main__":
    main()