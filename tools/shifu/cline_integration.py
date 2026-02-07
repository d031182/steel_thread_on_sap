"""
Shi Fu Cline Integration: Automatic Workflow Integration
=========================================================

Integrates Shi Fu's weekly analysis into Cline's development workflow.

Key Features:
1. Automatic analysis at session start
2. Insight notification system
3. PROJECT_TRACKER.md auto-update
4. Priority-based recommendations
5. Teaching file management

Philosophy: "The master guides without interfering."
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from .shifu import ShiFu
from .wisdom_generator import Teaching


logger = logging.getLogger(__name__)


class ClineIntegration:
    """
    Integrates Shi Fu insights into Cline's workflow
    
    Provides automatic analysis, notifications, and tracker updates
    without being intrusive to the development process.
    """
    
    def __init__(
        self,
        project_root: Optional[Path] = None,
        auto_update_tracker: bool = True,
        verbose: bool = False
    ):
        """
        Initialize Cline Integration
        
        Args:
            project_root: Root directory of project
            auto_update_tracker: Whether to auto-update PROJECT_TRACKER.md
            verbose: Enable detailed logging
        """
        self.project_root = project_root or Path.cwd()
        self.auto_update_tracker = auto_update_tracker
        self.verbose = verbose
        
        # Initialize Shi Fu
        self.shifu = ShiFu(project_root=self.project_root, verbose=verbose)
        
        # State tracking
        self.state_file = self.project_root / ".shifu_state.json"
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load Shi Fu state from file"""
        if self.state_file.exists():
            try:
                return json.loads(self.state_file.read_text())
            except Exception as e:
                logger.warning(f"Failed to load state: {e}")
        
        return {
            'last_analysis': None,
            'last_notification': None,
            'suppressed_patterns': [],
            'acknowledged_teachings': []
        }
    
    def _save_state(self):
        """Save Shi Fu state to file"""
        try:
            self.state_file.write_text(
                json.dumps(self.state, indent=2)
            )
        except Exception as e:
            logger.warning(f"Failed to save state: {e}")
    
    def should_run_analysis(self) -> bool:
        """
        Determine if analysis should run
        
        Runs weekly or on-demand, not every session
        
        Returns:
            True if analysis should run
        """
        if not self.state['last_analysis']:
            return True
        
        # Check if 7 days have passed
        last_analysis = datetime.fromisoformat(self.state['last_analysis'])
        days_since = (datetime.now() - last_analysis).days
        
        return days_since >= 7
    
    def run_session_start_check(self) -> Dict:
        """
        Run at Cline session start
        
        Performs weekly analysis if needed, provides recommendations
        
        Returns:
            Dictionary with status and recommendations
        """
        if self.verbose:
            logger.info("[Shi Fu Integration] Session start check...")
        
        result = {
            'analysis_performed': False,
            'recommendations': [],
            'urgent_count': 0,
            'high_count': 0,
            'should_notify': False,
            'message': None
        }
        
        # Check if analysis needed
        if self.should_run_analysis():
            if self.verbose:
                logger.info("[Shi Fu Integration] Running weekly analysis...")
            
            try:
                report = self.shifu.weekly_analysis(save_teachings=True)
                
                # Update state
                self.state['last_analysis'] = datetime.now().isoformat()
                self._save_state()
                
                result['analysis_performed'] = True
                result['report'] = report
                
                # Extract key metrics
                teachings = report['teachings']
                result['urgent_count'] = sum(1 for t in teachings if t.severity == 'URGENT')
                result['high_count'] = sum(1 for t in teachings if t.severity == 'HIGH')
                
                # Should we notify?
                if result['urgent_count'] > 0 or result['high_count'] >= 3:
                    result['should_notify'] = True
                    result['message'] = self._generate_notification_message(report)
                
                # Auto-update tracker if enabled
                if self.auto_update_tracker and (result['urgent_count'] > 0 or result['high_count'] > 0):
                    self._update_project_tracker(teachings)
                
                # Generate recommendations
                result['recommendations'] = self._generate_recommendations(teachings)
                
            except Exception as e:
                logger.error(f"Analysis failed: {e}")
                result['error'] = str(e)
        else:
            # Analysis not needed yet
            days_until = 7 - (datetime.now() - datetime.fromisoformat(self.state['last_analysis'])).days
            result['message'] = f"Next Shi Fu analysis in {days_until} days"
        
        return result
    
    def _generate_notification_message(self, report: Dict) -> str:
        """
        Generate notification message for Cline
        
        Args:
            report: Shi Fu analysis report
        
        Returns:
            Formatted notification message
        """
        teachings = report['teachings']
        urgent = [t for t in teachings if t.severity == 'URGENT']
        high = [t for t in teachings if t.severity == 'HIGH']
        
        message = "🧘‍♂️ **Shi Fu's Weekly Analysis Complete**\n\n"
        
        if urgent:
            message += f"🔴 **{len(urgent)} URGENT patterns detected:**\n"
            for t in urgent[:3]:  # Top 3
                message += f"- {t.title} (Priority: {t.priority_score:.0f}/100)\n"
            message += "\n"
        
        if high:
            message += f"🟠 **{len(high)} HIGH priority patterns detected:**\n"
            for t in high[:3]:  # Top 3
                message += f"- {t.title} (Priority: {t.priority_score:.0f}/100)\n"
            message += "\n"
        
        message += f"📄 Full report: {report.get('teachings_file', 'N/A')}\n\n"
        message += "**Should I add high-priority items to PROJECT_TRACKER.md?**"
        
        return message
    
    def _generate_recommendations(self, teachings: List[Teaching]) -> List[Dict]:
        """
        Generate actionable recommendations for Cline
        
        Args:
            teachings: List of Teaching objects
        
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        
        # Get top 5 by priority
        top_teachings = sorted(teachings, key=lambda t: t.priority_score, reverse=True)[:5]
        
        for teaching in top_teachings:
            rec = {
                'title': teaching.title,
                'severity': teaching.severity,
                'priority_score': teaching.priority_score,
                'affected_modules': teaching.affected_modules,
                'effort': teaching.estimated_effort,
                'value': teaching.expected_value,
                'quick_action': self._extract_first_step(teaching.action_plan)
            }
            recommendations.append(rec)
        
        return recommendations
    
    def _extract_first_step(self, action_plan: str) -> str:
        """Extract first actionable step from action plan"""
        lines = action_plan.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('1.') or line.startswith('- '):
                return line.lstrip('1.- ')
        return "See full action plan in teaching file"
    
    def _update_project_tracker(self, teachings: List[Teaching]):
        """
        Auto-update PROJECT_TRACKER.md with high-priority items
        
        Args:
            teachings: List of Teaching objects
        """
        try:
            tracker_path = self.project_root / "PROJECT_TRACKER.md"
            if not tracker_path.exists():
                logger.warning("PROJECT_TRACKER.md not found")
                return
            
            # Get URGENT and HIGH teachings
            priority_teachings = [
                t for t in teachings 
                if t.severity in ['URGENT', 'HIGH']
            ]
            
            if not priority_teachings:
                return
            
            # Read current tracker
            content = tracker_path.read_text()
            
            # Find insertion point (after "### 🟠 HIGH" section)
            lines = content.split('\n')
            insert_idx = None
            
            for i, line in enumerate(lines):
                if '### 🟠 HIGH' in line:
                    # Find the table end
                    for j in range(i + 1, len(lines)):
                        if lines[j].startswith('###') or lines[j].startswith('##'):
                            insert_idx = j
                            break
                    break
            
            if insert_idx is None:
                logger.warning("Could not find insertion point in PROJECT_TRACKER.md")
                return
            
            # Generate new tasks
            new_tasks = []
            timestamp = datetime.now().strftime('%Y-%m-%d')
            
            for teaching in priority_teachings[:5]:  # Top 5 only
                task_line = (
                    f"| **P1** | {teaching.title} | {teaching.estimated_effort} | "
                    f"🟡 NEW | Shi Fu analysis {timestamp} |"
                )
                new_tasks.append(task_line)
            
            # Insert tasks (above the next section)
            if new_tasks:
                lines.insert(insert_idx, '')
                lines.insert(insert_idx, '**New from Shi Fu Analysis**:')
                for task in reversed(new_tasks):
                    lines.insert(insert_idx, task)
                
                # Write back
                tracker_path.write_text('\n'.join(lines))
                
                if self.verbose:
                    logger.info(f"Added {len(new_tasks)} tasks to PROJECT_TRACKER.md")
        
        except Exception as e:
            logger.error(f"Failed to update PROJECT_TRACKER.md: {e}")
    
    def acknowledge_teaching(self, teaching_id: str):
        """
        Mark a teaching as acknowledged
        
        Args:
            teaching_id: ID of the teaching
        """
        if teaching_id not in self.state['acknowledged_teachings']:
            self.state['acknowledged_teachings'].append(teaching_id)
            self._save_state()
    
    def suppress_pattern(self, pattern_name: str, duration_days: int = 30):
        """
        Suppress a pattern for a duration
        
        Args:
            pattern_name: Name of pattern to suppress
            duration_days: How long to suppress
        """
        until = (datetime.now() + timedelta(days=duration_days)).isoformat()
        self.state['suppressed_patterns'].append({
            'pattern': pattern_name,
            'until': until
        })
        self._save_state()
    
    def get_active_recommendations(self) -> List[Dict]:
        """
        Get currently active recommendations (non-suppressed)
        
        Returns:
            List of active recommendation dictionaries
        """
        # TODO: Implement filtering based on suppressed patterns
        # For now, return empty (will be populated after analysis)
        return []
    
    def format_for_cline_chat(self, result: Dict) -> str:
        """
        Format result for display in Cline chat
        
        Args:
            result: Result from run_session_start_check
        
        Returns:
            Formatted message string
        """
        if result.get('error'):
            return f"⚠️ Shi Fu analysis failed: {result['error']}"
        
        if not result['analysis_performed']:
            return f"ℹ️ {result['message']}"
        
        if result['should_notify']:
            return result['message']
        
        # No urgent issues
        return (
            "✅ **Shi Fu's Weekly Analysis Complete**\n\n"
            f"Ecosystem health looks good!\n"
            f"- {result.get('high_count', 0)} patterns detected (none urgent)\n"
            f"- Continue current work\n"
        )


def session_start_hook(project_root: Optional[Path] = None) -> Dict:
    """
    Hook function to call at Cline session start
    
    Args:
        project_root: Root directory of project
    
    Returns:
        Analysis result dictionary
    """
    integration = ClineIntegration(project_root=project_root, verbose=True)
    return integration.run_session_start_check()


def format_for_chat(result: Dict) -> str:
    """
    Format result for Cline chat display
    
    Args:
        result: Result from session_start_hook
    
    Returns:
        Formatted message
    """
    integration = ClineIntegration()
    return integration.format_for_cline_chat(result)