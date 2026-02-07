"""
Gu Wu Phase 7.2: ASCII Intelligence Dashboard

Provides visual overview of test suite health, trends, and hotspots.
"""

import sqlite3
import sys
import io
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


@dataclass
class HealthMetrics:
    """Overall test suite health metrics"""
    total_tests: int
    passing_tests: int
    flaky_tests: int
    slow_tests: int
    coverage_pct: float
    health_score: float  # 0.0-1.0


@dataclass
class TrendData:
    """Trend analysis over time"""
    period: str  # "7d", "30d", etc.
    pass_rate_trend: str  # "UP", "DOWN", "STABLE"
    coverage_trend: str
    performance_trend: str


class DashboardGenerator:
    """
    Generates ASCII-based intelligence dashboard.
    
    Provides at-a-glance understanding of test suite health.
    """
    
    def __init__(self, db_path: str = "tools/guwu/guwu_metrics.db"):
        self.db_path = db_path
    
    def generate(self) -> str:
        """Generate complete dashboard"""
        sections = []
        
        # Header
        sections.append(self._generate_header())
        
        # Health overview
        health = self._get_health_metrics()
        sections.append(self._generate_health_section(health))
        
        # Trends
        trends = self._get_trends()
        sections.append(self._generate_trends_section(trends))
        
        # Hotspots (problem areas)
        hotspots = self._get_hotspots()
        sections.append(self._generate_hotspots_section(hotspots))
        
        # Recommendations preview
        sections.append(self._generate_recommendations_preview())
        
        return "\n\n".join(sections)
    
    def _generate_header(self) -> str:
        """Generate dashboard header"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"""
{'=' * 70}
  GU WU INTELLIGENCE DASHBOARD
  "Attending to martial affairs with discipline"
  
  Generated: {now}
{'=' * 70}
"""
    
    def _generate_health_section(self, health: HealthMetrics) -> str:
        """Generate health overview section"""
        # Calculate health indicator
        if health.health_score >= 0.9:
            indicator = "[EXCELLENT]"
            bar = "████████████████████"  # 20 blocks
        elif health.health_score >= 0.8:
            indicator = "[GOOD]"
            bar = "████████████████░░░░"  # 16 blocks
        elif health.health_score >= 0.7:
            indicator = "[FAIR]"
            bar = "████████████░░░░░░░░"  # 12 blocks
        else:
            indicator = "[NEEDS ATTENTION]"
            bar = "████████░░░░░░░░░░░░"  # 8 blocks
        
        return f"""
[HEALTH OVERVIEW] {indicator}

  Overall Health:  {bar} {health.health_score:.1%}
  
  Test Metrics:
    Total Tests:   {health.total_tests:>6}
    Passing:       {health.passing_tests:>6} ({health.passing_tests/max(health.total_tests,1)*100:.1f}%)
    Flaky:         {health.flaky_tests:>6} ({health.flaky_tests/max(health.total_tests,1)*100:.1f}%)
    Slow (>5s):    {health.slow_tests:>6}
    
  Coverage:        {health.coverage_pct:>5.1f}%
"""
    
    def _generate_trends_section(self, trends: TrendData) -> str:
        """Generate trends section"""
        # Trend indicators
        trend_map = {
            "UP": "↑ IMPROVING",
            "DOWN": "↓ DECLINING", 
            "STABLE": "→ STABLE"
        }
        
        return f"""
[TRENDS] Last {trends.period}

  Pass Rate:       {trend_map.get(trends.pass_rate_trend, '→ STABLE')}
  Coverage:        {trend_map.get(trends.coverage_trend, '→ STABLE')}
  Performance:     {trend_map.get(trends.performance_trend, '→ STABLE')}
"""
    
    def _generate_hotspots_section(self, hotspots: List[Dict]) -> str:
        """Generate problem areas section"""
        if not hotspots:
            return "[HOTSPOTS] No critical issues detected"
        
        lines = ["[HOTSPOTS] Areas Needing Attention\n"]
        
        for i, spot in enumerate(hotspots[:5], 1):  # Top 5
            lines.append(
                f"  {i}. {spot['name']}: {spot['issue']} "
                f"(Priority: {spot['priority']})"
            )
        
        return "\n".join(lines)
    
    def _generate_recommendations_preview(self) -> str:
        """Generate recommendations preview"""
        # Check if recommendations exist
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM recommendations 
                WHERE status = 'pending'
            """)
            
            count = cursor.fetchone()[0]
            conn.close()
            
            if count == 0:
                return "[RECOMMENDATIONS] No pending recommendations"
            
            return f"""
[RECOMMENDATIONS] {count} Pending

  Run for details: python -m tests.guwu.intelligence.recommendations
"""
        except Exception:
            return "[RECOMMENDATIONS] Run recommendation engine to get started"
    
    def _get_health_metrics(self) -> HealthMetrics:
        """Calculate current health metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get test counts
            cursor.execute("""
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN outcome = 'passed' THEN 1 ELSE 0 END) as passed
                FROM test_executions
                WHERE timestamp > ?
            """, (datetime.now().timestamp() - 86400,))  # Last 24 hours
            
            row = cursor.fetchone()
            total = row[0] if row[0] else 0
            passed = row[1] if row[1] else 0
            
            # Get flaky tests
            cursor.execute("""
                SELECT COUNT(*) FROM test_metrics 
                WHERE flakiness_score > 0.2
            """)
            flaky = cursor.fetchone()[0]
            
            # Get slow tests
            cursor.execute("""
                SELECT COUNT(*) FROM test_metrics 
                WHERE avg_duration > 5.0
            """)
            slow = cursor.fetchone()[0]
            
            # Get coverage (from latest)
            cursor.execute("""
                SELECT coverage_pct FROM test_sessions 
                ORDER BY timestamp DESC LIMIT 1
            """)
            coverage_row = cursor.fetchone()
            coverage = coverage_row[0] if coverage_row else 0.0
            
            conn.close()
            
            # Calculate health score
            pass_rate = passed / max(total, 1)
            flaky_penalty = (flaky / max(total, 1)) * 0.2
            slow_penalty = (slow / max(total, 1)) * 0.1
            coverage_factor = coverage / 100.0
            
            health_score = (pass_rate * 0.5 + coverage_factor * 0.5) - flaky_penalty - slow_penalty
            health_score = max(0.0, min(1.0, health_score))  # Clamp to 0-1
            
            return HealthMetrics(
                total_tests=total,
                passing_tests=passed,
                flaky_tests=flaky,
                slow_tests=slow,
                coverage_pct=coverage,
                health_score=health_score
            )
            
        except Exception as e:
            # Return default metrics if database not ready
            return HealthMetrics(
                total_tests=0,
                passing_tests=0,
                flaky_tests=0,
                slow_tests=0,
                coverage_pct=0.0,
                health_score=0.0
            )
    
    def _get_trends(self) -> TrendData:
        """Analyze trends over time"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get pass rate trend (last 7 days)
            week_ago = (datetime.now() - timedelta(days=7)).timestamp()
            
            cursor.execute("""
                SELECT 
                    AVG(CASE WHEN outcome = 'passed' THEN 1.0 ELSE 0.0 END) as pass_rate
                FROM test_executions
                WHERE timestamp > ?
                GROUP BY CAST(timestamp / 86400 AS INTEGER)
                ORDER BY timestamp
            """, (week_ago,))
            
            pass_rates = [row[0] for row in cursor.fetchall()]
            
            # Determine trend
            if len(pass_rates) >= 2:
                if pass_rates[-1] > pass_rates[0] + 0.05:
                    pass_trend = "UP"
                elif pass_rates[-1] < pass_rates[0] - 0.05:
                    pass_trend = "DOWN"
                else:
                    pass_trend = "STABLE"
            else:
                pass_trend = "STABLE"
            
            conn.close()
            
            return TrendData(
                period="7d",
                pass_rate_trend=pass_trend,
                coverage_trend="STABLE",  # TODO: Implement coverage tracking
                performance_trend="STABLE"  # TODO: Implement perf tracking
            )
            
        except Exception:
            return TrendData(
                period="7d",
                pass_rate_trend="STABLE",
                coverage_trend="STABLE",
                performance_trend="STABLE"
            )
    
    def _get_hotspots(self) -> List[Dict]:
        """Identify problem areas"""
        hotspots = []
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Find flaky tests
            cursor.execute("""
                SELECT test_name, flakiness_score 
                FROM test_metrics 
                WHERE flakiness_score > 0.3
                ORDER BY flakiness_score DESC
                LIMIT 3
            """)
            
            for row in cursor.fetchall():
                hotspots.append({
                    'name': row[0],
                    'issue': f"Flaky ({row[1]:.1%})",
                    'priority': 'HIGH'
                })
            
            # Find slow tests
            cursor.execute("""
                SELECT test_name, avg_duration 
                FROM test_metrics 
                WHERE avg_duration > 10.0
                ORDER BY avg_duration DESC
                LIMIT 2
            """)
            
            for row in cursor.fetchall():
                hotspots.append({
                    'name': row[0],
                    'issue': f"Slow ({row[1]:.1f}s)",
                    'priority': 'MEDIUM'
                })
            
            conn.close()
            
        except Exception:
            pass
        
        return hotspots


def main():
    """CLI entry point for dashboard"""
    generator = DashboardGenerator()
    dashboard = generator.generate()
    print(dashboard)


if __name__ == "__main__":
    main()