"""
DDD Pattern Visualizer - Architecture Maturity Dashboard
=========================================================

Visualizes DDD pattern adoption with ASCII art charts for terminal output.
No external dependencies - pure Python terminal graphics.

Philosophy:
"A picture is worth a thousand numbers. Show the journey, not just the score."
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class VisualizationConfig:
    """Configuration for visualization output"""
    width: int = 60  # Chart width in characters
    show_trend: bool = True
    show_recommendations: bool = True
    ascii_only: bool = False  # If True, avoid Unicode characters


class DDDVisualizer:
    """
    Visualize DDD pattern adoption with terminal-friendly charts
    """
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        """
        Initialize visualizer
        
        Args:
            config: Visualization configuration
        """
        self.config = config or VisualizationConfig()
    
    def render_maturity_dashboard(
        self,
        overall_score: float,
        maturity_level: str,
        pattern_scores: List[Dict],
        modules_analyzed: int
    ) -> str:
        """
        Render complete DDD maturity dashboard
        
        Args:
            overall_score: Overall DDD maturity (0-100)
            maturity_level: Maturity level text
            pattern_scores: List of pattern adoption scores
            modules_analyzed: Total modules analyzed
        
        Returns:
            Formatted dashboard string
        """
        output = []
        
        # Header
        output.append("╔" + "═"*68 + "╗")
        output.append("║" + " "*68 + "║")
        output.append("║" + "  DDD Architecture Maturity Dashboard".center(68) + "║")
        output.append("║" + " "*68 + "║")
        output.append("╚" + "═"*68 + "╝")
        output.append("")
        
        # Overall Score with visual bar
        output.append("Overall Maturity:")
        output.append(self._render_score_bar(overall_score, maturity_level))
        output.append("")
        output.append(f"Modules Analyzed: {modules_analyzed}")
        output.append("")
        
        # Pattern Adoption Details
        output.append("─" * 70)
        output.append("Pattern Adoption Breakdown")
        output.append("─" * 70)
        output.append("")
        
        for ps in pattern_scores:
            output.append(self._render_pattern_row(ps))
            output.append("")
        
        return "\n".join(output)
    
    def _render_score_bar(self, score: float, level: str) -> str:
        """
        Render horizontal bar chart for score
        
        Args:
            score: Score value (0-100)
            level: Maturity level text
        
        Returns:
            ASCII bar chart
        """
        bar_width = 50
        filled = int((score / 100.0) * bar_width)
        empty = bar_width - filled
        
        # Color codes (use emojis as visual indicators)
        if score >= 80:
            indicator = "🟢"  # Master/Skilled
        elif score >= 60:
            indicator = "🟡"  # Practicing
        elif score >= 40:
            indicator = "🟠"  # Learning
        else:
            indicator = "🔴"  # Beginner
        
        bar = "█" * filled + "░" * empty
        
        return f"{indicator} [{bar}] {score:.1f}/100 ({level})"
    
    def _render_pattern_row(self, pattern_score: Dict) -> str:
        """
        Render a single pattern adoption row
        
        Args:
            pattern_score: Pattern score dictionary
        
        Returns:
            Formatted row with bar chart
        """
        name = pattern_score['pattern_name']
        adoption = pattern_score['adoption_percentage']
        using = pattern_score['modules_using']
        total = pattern_score['modules_total']
        maturity = pattern_score['maturity_level']
        recommendation = pattern_score.get('recommendation', '')
        
        # Status indicator
        if maturity == "Excellent":
            status = "✅"
        elif maturity == "Good":
            status = "🔄"
        elif maturity == "Partial":
            status = "⚠️"
        else:
            status = "🔴"
        
        # Mini bar (20 chars)
        mini_bar_width = 20
        filled = int((adoption / 100.0) * mini_bar_width)
        empty = mini_bar_width - filled
        mini_bar = "█" * filled + "░" * empty
        
        # Format row
        output = []
        output.append(f"{status} {name}")
        output.append(f"   [{mini_bar}] {adoption:.0f}% ({using}/{total} modules) - {maturity}")
        
        # Add recommendation for non-excellent patterns
        if maturity in ["Not Started", "Partial"] and recommendation:
            # Extract priority from recommendation (⭐⭐ START HERE, etc.)
            priority_marker = ""
            if "⭐⭐ START HERE" in recommendation:
                priority_marker = "🎯 PRIORITY: "
            elif "⭐ Start with" in recommendation:
                priority_marker = "💡 NEXT: "
            
            # Truncate long recommendations
            rec_text = recommendation.replace("⭐⭐ START HERE", "").replace("⭐", "").strip()
            if len(rec_text) > 60:
                rec_text = rec_text[:57] + "..."
            
            output.append(f"   {priority_marker}{rec_text}")
        
        return "\n".join(output)
    
    def render_historical_trend(
        self,
        snapshots: List[Dict],
        pattern_name: Optional[str] = None
    ) -> str:
        """
        Render historical trend chart
        
        Args:
            snapshots: List of historical snapshots with DDD scores
            pattern_name: Specific pattern to show, or None for overall
        
        Returns:
            ASCII trend chart
        """
        if not snapshots:
            return "No historical data available"
        
        output = []
        
        # Header
        title = f"DDD Maturity Trend" if not pattern_name else f"{pattern_name} Adoption Trend"
        output.append("─" * 70)
        output.append(title)
        output.append("─" * 70)
        output.append("")
        
        # Extract scores
        if pattern_name:
            scores = [
                s.get('ddd_pattern_scores', {}).get(pattern_name, 0)
                for s in snapshots
                if s.get('ddd_pattern_scores')
            ]
        else:
            scores = [
                s.get('ddd_maturity_score', 0)
                for s in snapshots
                if s.get('ddd_maturity_score') is not None
            ]
        
        if not scores:
            output.append("No DDD scores recorded yet")
            return "\n".join(output)
        
        # Render sparkline (mini chart)
        sparkline = self._render_sparkline(scores)
        output.append(f"Trend: {sparkline}")
        output.append("")
        
        # Calculate stats
        first = scores[0]
        last = scores[-1]
        change = last - first
        avg = sum(scores) / len(scores)
        
        # Direction indicator
        if change > 5:
            direction = "📈 IMPROVING"
        elif change > 0:
            direction = "↗️  Rising"
        elif change < -5:
            direction = "📉 DECLINING"
        elif change < 0:
            direction = "↘️  Falling"
        else:
            direction = "→  Stable"
        
        output.append(f"First: {first:.1f}/100")
        output.append(f"Last:  {last:.1f}/100")
        output.append(f"Change: {change:+.1f} points ({direction})")
        output.append(f"Average: {avg:.1f}/100")
        output.append(f"Snapshots: {len(scores)}")
        
        return "\n".join(output)
    
    def _render_sparkline(self, values: List[float]) -> str:
        """
        Render sparkline chart (mini trend visualization)
        
        Args:
            values: List of numeric values
        
        Returns:
            Sparkline string
        """
        if not values:
            return ""
        
        # Sparkline characters (low to high)
        chars = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        
        # Normalize to 0-7 range
        min_val = min(values)
        max_val = max(values)
        
        if max_val == min_val:
            # All same value
            return chars[4] * len(values)
        
        sparkline = []
        for val in values:
            normalized = (val - min_val) / (max_val - min_val)
            index = min(7, int(normalized * 8))
            sparkline.append(chars[index])
        
        return "".join(sparkline)
    
    def render_pattern_comparison(
        self,
        pattern_scores: List[Dict]
    ) -> str:
        """
        Render side-by-side pattern comparison
        
        Args:
            pattern_scores: List of pattern adoption scores
        
        Returns:
            Comparison chart
        """
        output = []
        
        output.append("─" * 70)
        output.append("Pattern Adoption Comparison")
        output.append("─" * 70)
        output.append("")
        
        # Sort by adoption (descending)
        sorted_patterns = sorted(
            pattern_scores,
            key=lambda p: p['adoption_percentage'],
            reverse=True
        )
        
        # Find max adoption for scaling
        max_adoption = max(ps['adoption_percentage'] for ps in sorted_patterns)
        if max_adoption == 0:
            max_adoption = 100  # Avoid division by zero
        
        # Render bars
        for ps in sorted_patterns:
            name = ps['pattern_name'][:25]  # Truncate long names
            adoption = ps['adoption_percentage']
            
            # Scale bar relative to max
            bar_width = 30
            filled = int((adoption / max_adoption) * bar_width)
            bar = "█" * filled
            
            output.append(f"{name:25s} │{bar:<30s}│ {adoption:5.1f}%")
        
        return "\n".join(output)
    
    def render_module_heatmap(
        self,
        modules: List[str],
        pattern_adoption: Dict[str, Dict[str, bool]]
    ) -> str:
        """
        Render module-pattern adoption heatmap
        
        Args:
            modules: List of module names
            pattern_adoption: Dict[module_name][pattern_name] = adopted (bool)
        
        Returns:
            Heatmap visualization
        """
        output = []
        
        output.append("─" * 70)
        output.append("Module-Pattern Adoption Heatmap")
        output.append("─" * 70)
        output.append("")
        
        # Pattern names (abbreviated)
        patterns = [
            ("Repository", "Repo"),
            ("Service Layer", "Service"),
            ("Unit of Work", "UoW"),
            ("Aggregate Pattern", "Aggregate"),
            ("Domain Events", "Events")
        ]
        
        # Header
        header = "Module".ljust(20) + " │ "
        header += " ".join(p[1].center(9) for p in patterns)
        output.append(header)
        output.append("─" * 70)
        
        # Rows
        for module in modules:
            row = module[:19].ljust(20) + " │ "
            
            for pattern_full, _ in patterns:
                adopted = pattern_adoption.get(module, {}).get(pattern_full, False)
                symbol = "   ✅   " if adopted else "   ░░   "
                row += symbol + " "
            
            output.append(row)
        
        output.append("")
        output.append("Legend: ✅ = Adopted   ░░ = Not Yet")
        
        return "\n".join(output)
    
    def render_celebration_banner(self, celebrations: List[Dict]) -> str:
        """
        Render celebrations as banner
        
        Args:
            celebrations: List of celebration dictionaries
        
        Returns:
            Celebration banner
        """
        if not celebrations:
            return ""
        
        output = []
        
        output.append("")
        output.append("🎉" + "="*68 + "🎉")
        output.append("║" + " "*68 + "║")
        output.append("║" + "  CELEBRATIONS!".center(68) + "║")
        output.append("║" + " "*68 + "║")
        output.append("🎉" + "="*68 + "🎉")
        output.append("")
        
        for cel in celebrations:
            emoji = cel.get('emoji', '🎉')
            achievement = cel.get('achievement', '')
            description = cel.get('description', '')
            impact = cel.get('impact', '')
            
            output.append(f"{emoji} {achievement}")
            output.append(f"   {description}")
            output.append(f"   Impact: {impact}")
            output.append("")
        
        return "\n".join(output)


def render_ddd_dashboard(report: Dict, include_recommendations: bool = True) -> str:
    """
    Render complete DDD dashboard from report
    
    Args:
        report: DDD maturity report dictionary
        include_recommendations: Whether to show AI recommendations
    
    Returns:
        Complete dashboard visualization
    """
    viz = DDDVisualizer()
    
    output = []
    
    # Main dashboard
    output.append(viz.render_maturity_dashboard(
        overall_score=report['overall_score'],
        maturity_level=report['maturity_level'],
        pattern_scores=report['pattern_scores'],
        modules_analyzed=report['modules_analyzed']
    ))
    
    output.append("")
    
    # Pattern comparison
    output.append(viz.render_pattern_comparison(report['pattern_scores']))
    
    # AI Recommendations (NEW)
    if include_recommendations:
        output.append("")
        output.append("─" * 70)
        output.append("🤖 AI Recommendations (Top 2)")
        output.append("─" * 70)
        output.append("")
        
        from tools.shifu.ddd_recommendations import DDDRecommendationsEngine
        
        engine = DDDRecommendationsEngine()
        recommendations = engine.generate_recommendations(report, max_recommendations=2)
        
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                priority_emoji = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}
                emoji = priority_emoji.get(rec.priority.value, "⚪")
                
                output.append(f"{i}. {emoji} {rec.pattern_name} ({rec.priority.value})")
                output.append(f"   Effort: {rec.effort_hours[0]}-{rec.effort_hours[1]}h | Gain: +{rec.expected_maturity_gain:.1f} points")
                output.append(f"   💡 {rec.business_value[:60]}...")
                output.append("")
            
            output.append("Run: python -m tools.shifu.ddd_recommendations --top 3")
            output.append("     for detailed implementation guidance")
        else:
            output.append("All patterns at excellent level! 🎉")
    
    return "\n".join(output)


def render_growth_with_ddd(
    trend_snapshots: List[Dict],
    celebrations: List[Dict]
) -> str:
    """
    Render growth trends including DDD maturity
    
    Args:
        trend_snapshots: Historical snapshots
        celebrations: Celebrations to display
    
    Returns:
        Growth visualization with DDD trends
    """
    viz = DDDVisualizer()
    
    output = []
    
    # Historical trend
    output.append(viz.render_historical_trend(trend_snapshots))
    output.append("")
    
    # Per-pattern trends (if available)
    if trend_snapshots and trend_snapshots[0].get('ddd_pattern_scores'):
        patterns = trend_snapshots[0]['ddd_pattern_scores'].keys()
        
        for pattern in patterns:
            output.append(viz.render_historical_trend(trend_snapshots, pattern_name=pattern))
            output.append("")
    
    # Celebrations
    if celebrations:
        output.append(viz.render_celebration_banner(celebrations))
    
    return "\n".join(output)


def main():
    """CLI entry point for DDD visualizer"""
    import argparse
    from pathlib import Path
    import json
    
    parser = argparse.ArgumentParser(
        description="DDD Pattern Visualizer - Dashboard & Charts"
    )
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Show current maturity dashboard'
    )
    parser.add_argument(
        '--trends',
        action='store_true',
        help='Show historical trends'
    )
    parser.add_argument(
        '--report-file',
        type=str,
        help='JSON report file to visualize'
    )
    
    args = parser.parse_args()
    
    if args.dashboard:
        # Run analysis and display dashboard
        from tools.shifu.ddd_pattern_tracker import DDDPatternTracker
        
        tracker = DDDPatternTracker()
        report = tracker.analyze_codebase()
        
        dashboard = render_ddd_dashboard(report.to_dict())
        print(dashboard)
    
    elif args.trends:
        # Load historical data and display trends
        from tools.shifu.growth_tracker import GrowthTracker
        
        tracker = GrowthTracker()
        trend = tracker.analyze_trends(period_days=90)
        
        if not trend:
            print("Insufficient historical data for trends")
            print("Run weekly analyses to build history")
            return
        
        # Extract DDD celebrations
        celebrations_raw = tracker.identify_celebrations(trend)
        celebrations = [
            {
                'emoji': c.emoji,
                'achievement': c.achievement,
                'description': c.description,
                'impact': c.impact
            }
            for c in celebrations_raw
            if 'DDD' in c.achievement or 'Pattern' in c.achievement
        ]
        
        # Convert snapshots for visualization
        snapshots = [
            {
                'timestamp': s.timestamp,
                'ddd_maturity_score': s.ddd_maturity_score,
                'ddd_pattern_scores': s.ddd_pattern_scores
            }
            for s in trend.snapshots
        ]
        
        viz_output = render_growth_with_ddd(snapshots, celebrations)
        print(viz_output)
    
    elif args.report_file:
        # Load and visualize from file
        with open(args.report_file, 'r') as f:
            report = json.load(f)
        
        dashboard = render_ddd_dashboard(report)
        print(dashboard)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()