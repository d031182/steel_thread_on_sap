"""
Agent Orchestrator - Coordinate Multiple Specialized Agents

Manages:
- Parallel agent execution
- Report synthesis
- Conflict resolution
- Comprehensive recommendations
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
import time

from .base_agent import AgentReport, Finding, Severity
from .architect_agent import ArchitectAgent
from .security_agent import SecurityAgent
from .ux_architect_agent import UXArchitectAgent
from .file_organization_agent import FileOrganizationAgent
from .performance_agent import PerformanceAgent
from .documentation_agent import DocumentationAgent


@dataclass
class SynthesizedPlan:
    """Unified action plan from multiple agents"""
    prioritized_actions: List[Dict]  # Actions sorted by priority
    conflicts: List[Dict]             # Conflicting recommendations
    metrics_summary: Dict             # Aggregated metrics
    overall_health_score: float       # 0-100
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            'prioritized_actions': self.prioritized_actions,
            'conflicts': self.conflicts,
            'metrics_summary': self.metrics_summary,
            'overall_health_score': self.overall_health_score
        }


@dataclass
class ComprehensiveReport:
    """Combined report from all agents"""
    module_path: Path
    agent_reports: List[AgentReport]
    synthesized_plan: SynthesizedPlan
    execution_time_seconds: float
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'module_path': str(self.module_path),
            'agent_reports': [r.to_dict() for r in self.agent_reports],
            'synthesized_plan': self.synthesized_plan.to_dict(),
            'execution_time_seconds': self.execution_time_seconds
        }


class AgentOrchestrator:
    """
    Coordinate multiple specialized agents
    
    Features:
    - Parallel agent execution (6x faster with 6 agents)
    - Report synthesis
    - Conflict resolution
    - Priority reconciliation
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agents = {
            'architect': ArchitectAgent(),
            'security': SecurityAgent(),
            'ux_architect': UXArchitectAgent(),
            'file_organization': FileOrganizationAgent(),
            'performance': PerformanceAgent(),
            'documentation': DocumentationAgent()
        }
    
    def analyze_module_comprehensive(
        self,
        module_path: Path,
        parallel: bool = True,
        max_workers: int = 6,
        selected_agents: Optional[List[str]] = None
    ) -> ComprehensiveReport:
        """
        Run all agents on module
        
        Args:
            module_path: Path to module directory
            parallel: Enable parallel execution (default True)
            max_workers: Max parallel threads (default 6 for 6 agents)
            selected_agents: Specific agents to run (None = all)
            
        Returns:
            ComprehensiveReport combining all agent findings
        """
        start_time = time.time()
        
        self.logger.info(f"Starting comprehensive analysis of {module_path}")
        self.logger.info(f"Parallel execution: {parallel} (max_workers: {max_workers})")
        
        # Filter agents if specified
        agents_to_run = self.agents
        if selected_agents is not None:
            agents_to_run = {k: v for k, v in self.agents.items() if k in selected_agents}
            self.logger.info(f"Running selected agents: {', '.join(agents_to_run.keys())}")
        
        if parallel:
            agent_reports = self._run_agents_parallel(module_path, agents_to_run, max_workers)
        else:
            agent_reports = self._run_agents_sequential(module_path, agents_to_run)
        
        # Synthesize reports
        synthesized_plan = self.synthesize_reports(agent_reports)
        
        execution_time = time.time() - start_time
        
        self.logger.info(f"Comprehensive analysis complete in {execution_time:.2f}s")
        
        return ComprehensiveReport(
            module_path=module_path,
            agent_reports=agent_reports,
            synthesized_plan=synthesized_plan,
            execution_time_seconds=execution_time
        )
    
    def _run_agents_parallel(
        self,
        module_path: Path,
        agents: Dict,
        max_workers: int
    ) -> List[AgentReport]:
        """Run agents in parallel using ThreadPoolExecutor"""
        reports = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all agents
            future_to_agent = {
                executor.submit(agent.analyze_module, module_path): agent_name
                for agent_name, agent in agents.items()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_agent):
                agent_name = future_to_agent[future]
                try:
                    report = future.result()
                    reports.append(report)
                    self.logger.info(
                        f"Agent '{agent_name}' completed: {len(report.findings)} findings "
                        f"in {report.execution_time_seconds:.2f}s"
                    )
                except Exception as e:
                    self.logger.error(f"Agent '{agent_name}' failed: {str(e)}")
        
        return reports
    
    def _run_agents_sequential(
        self,
        module_path: Path,
        agents: Dict
    ) -> List[AgentReport]:
        """Run agents sequentially (fallback for debugging)"""
        reports = []
        
        for agent_name, agent in agents.items():
            try:
                self.logger.info(f"Running agent: {agent_name}")
                start = time.time()
                report = agent.analyze_module(module_path)
                elapsed = time.time() - start
                reports.append(report)
                self.logger.info(
                    f"Agent '{agent_name}' completed: {len(report.findings)} findings "
                    f"in {elapsed:.2f}s"
                )
            except Exception as e:
                self.logger.error(f"Agent '{agent_name}' failed: {str(e)}")
        
        return reports
    
    def synthesize_reports(
        self,
        reports: List[AgentReport]
    ) -> SynthesizedPlan:
        """
        Combine agent reports into unified action plan
        
        Handles:
        - Priority reconciliation (Critical → High → Medium → Low)
        - Conflict detection (agents disagreeing)
        - Metrics aggregation
        - Overall health score calculation
        """
        all_findings = []
        for report in reports:
            all_findings.extend(report.findings)
        
        # Sort findings by severity
        severity_order = [
            Severity.CRITICAL,
            Severity.HIGH,
            Severity.MEDIUM,
            Severity.LOW
        ]
        all_findings.sort(key=lambda f: severity_order.index(f.severity))
        
        # Create prioritized actions
        prioritized_actions = []
        for finding in all_findings:
            # Find which agent produced this finding
            agent_name = "unknown"
            for report in reports:
                if finding in report.findings:
                    agent_name = report.agent_name
                    break
            
            prioritized_actions.append({
                'agent': agent_name,
                'category': finding.category,
                'severity': finding.severity.value,
                'file': str(finding.file_path),
                'line': finding.line_number,
                'description': finding.description,
                'recommendation': finding.recommendation
            })
        
        # Detect conflicts (same file/line, different recommendations)
        conflicts = self._detect_conflicts(all_findings)
        
        # Aggregate metrics
        metrics_summary = {
            'total_findings': len(all_findings),
            'by_severity': {
                severity.value: sum(1 for f in all_findings if f.severity == severity)
                for severity in Severity
            },
            'by_agent': {
                report.agent_name: len(report.findings)
                for report in reports
            },
            'total_execution_time': sum(r.execution_time_seconds for r in reports),
            'agents_run': len(reports)
        }
        
        # Calculate overall health score (0-100)
        health_score = self._calculate_health_score(all_findings)
        
        return SynthesizedPlan(
            prioritized_actions=prioritized_actions,
            conflicts=conflicts,
            metrics_summary=metrics_summary,
            overall_health_score=health_score
        )
    
    def _detect_conflicts(self, findings: List[Finding]) -> List[Dict]:
        """
        Detect conflicting recommendations from different agents
        
        Conflicts occur when:
        - Same file + line number
        - Different recommendations
        """
        conflicts = []
        
        # Group findings by file + line
        by_location = {}
        for finding in findings:
            if finding.line_number is None:
                continue  # Skip file-level findings
            
            key = (str(finding.file_path), finding.line_number)
            if key not in by_location:
                by_location[key] = []
            by_location[key].append(finding)
        
        # Find locations with multiple findings
        for location, location_findings in by_location.items():
            if len(location_findings) > 1:
                # Check if recommendations differ
                recommendations = set(f.recommendation for f in location_findings)
                if len(recommendations) > 1:
                    conflicts.append({
                        'file': location[0],
                        'line': location[1],
                        'findings': [
                            {
                                'category': f.category,
                                'severity': f.severity.value,
                                'recommendation': f.recommendation
                            }
                            for f in location_findings
                        ]
                    })
        
        return conflicts
    
    def _calculate_health_score(self, findings: List[Finding]) -> float:
        """
        Calculate overall health score (0-100)
        
        Formula:
        - Start at 100
        - Deduct points per finding (weighted by severity)
        - CRITICAL: -10 points
        - HIGH: -5 points
        - MEDIUM: -2 points
        - LOW: -1 point
        """
        score = 100.0
        
        severity_weights = {
            Severity.CRITICAL: 10,
            Severity.HIGH: 5,
            Severity.MEDIUM: 2,
            Severity.LOW: 1
        }
        
        for finding in findings:
            score -= severity_weights.get(finding.severity, 0)
        
        # Clamp to 0-100
        return max(0.0, min(100.0, score))
    
    def visualize_report(self, report: ComprehensiveReport) -> str:
        """
        Generate ASCII visualization of comprehensive report
        
        Returns formatted string with:
        - Overall health score
        - Findings by agent
        - Top priority actions
        - Conflicts (if any)
        """
        lines = []
        
        lines.append("\n" + "=" * 70)
        lines.append("COMPREHENSIVE MODULE ANALYSIS")
        lines.append("=" * 70)
        lines.append(f"Module: {report.module_path.name}")
        lines.append(f"Execution Time: {report.execution_time_seconds:.1f}s ({len(report.agent_reports)} agents in parallel)")
        lines.append("")
        
        # Health score
        score = report.synthesized_plan.overall_health_score
        if score >= 90:
            score_label = "EXCELLENT ✅"
        elif score >= 70:
            score_label = "GOOD ✅"
        elif score >= 50:
            score_label = "NEEDS IMPROVEMENT ⚠️"
        else:
            score_label = "CRITICAL ❌"
        
        lines.append(f"Overall Health Score: {score:.0f}/100 ({score_label})")
        lines.append("")
        
        # Findings by agent
        lines.append("Findings by Agent:")
        for agent_report in report.agent_reports:
            critical = sum(1 for f in agent_report.findings if f.severity == Severity.CRITICAL)
            high = sum(1 for f in agent_report.findings if f.severity == Severity.HIGH)
            medium = sum(1 for f in agent_report.findings if f.severity == Severity.MEDIUM)
            low = sum(1 for f in agent_report.findings if f.severity == Severity.LOW)
            
            lines.append(
                f"  [{agent_report.agent_name.title():18}] "
                f"{len(agent_report.findings):3d} findings "
                f"({critical} CRIT, {high} HIGH, {medium} MED, {low} LOW)"
            )
        lines.append("")
        
        # Top priority actions
        actions = report.synthesized_plan.prioritized_actions
        if actions:
            lines.append(f"Top Priority Actions (showing {min(10, len(actions))} of {len(actions)}):")
            for i, action in enumerate(actions[:10], 1):
                severity = action['severity'].upper()
                category = action['category']
                file_path = Path(action['file']).name  # Just filename
                line = action['line'] or 0
                
                lines.append(f"  {i:2d}. [{severity:8}] {category:30} @ {file_path}:{line}")
                lines.append(f"      → {action['recommendation'][:60]}")
        else:
            lines.append("No issues found! ✅")
        
        lines.append("")
        
        # Conflicts
        if report.synthesized_plan.conflicts:
            lines.append(f"⚠️ Conflicts Detected: {len(report.synthesized_plan.conflicts)}")
            for conflict in report.synthesized_plan.conflicts[:5]:  # Show max 5
                lines.append(f"  - {Path(conflict['file']).name}:{conflict['line']}: "
                           f"{len(conflict['findings'])} agents have different recommendations")
            lines.append("")
        
        # Metrics summary
        metrics = report.synthesized_plan.metrics_summary
        lines.append("Metrics Summary:")
        lines.append(f"  Total Findings: {metrics['total_findings']}")
        lines.append(f"  By Severity: "
                    f"CRIT={metrics['by_severity'].get('critical', 0)}, "
                    f"HIGH={metrics['by_severity'].get('high', 0)}, "
                    f"MED={metrics['by_severity'].get('medium', 0)}, "
                    f"LOW={metrics['by_severity'].get('low', 0)}")
        lines.append(f"  Agents Run: {metrics['agents_run']}")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """
        Get capabilities of all registered agents
        
        Returns:
            Dictionary mapping agent name to list of capabilities
        """
        return {
            agent_name: agent.get_capabilities()
            for agent_name, agent in self.agents.items()
        }