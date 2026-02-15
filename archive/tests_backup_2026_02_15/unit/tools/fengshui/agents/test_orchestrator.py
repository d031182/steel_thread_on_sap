"""
Unit tests for Agent Orchestrator

Tests multi-agent coordination:
- Parallel execution
- Sequential execution  
- Report synthesis
- Conflict detection
- Health score calculation
- Agent selection
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from tools.fengshui.agents.orchestrator import (
    AgentOrchestrator,
    ComprehensiveReport,
    SynthesizedPlan
)
from tools.fengshui.agents.base_agent import AgentReport, Finding, Severity


class TestOrchestratorInitialization:
    """Test orchestrator initialization"""
    
    def test_orchestrator_initializes_with_all_agents(self):
        # ARRANGE & ACT
        orchestrator = AgentOrchestrator()
        
        # ASSERT
        assert len(orchestrator.agents) == 6
        assert 'architect' in orchestrator.agents
        assert 'security' in orchestrator.agents
        assert 'ux_architect' in orchestrator.agents
        assert 'file_organization' in orchestrator.agents
        assert 'performance' in orchestrator.agents
        assert 'documentation' in orchestrator.agents
    
    def test_get_agent_capabilities_returns_all_agents(self):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        
        # ACT
        capabilities = orchestrator.get_agent_capabilities()
        
        # ASSERT
        assert len(capabilities) == 6
        assert all(isinstance(caps, list) for caps in capabilities.values())


class TestParallelExecution:
    """Test parallel agent execution"""
    
    def test_parallel_execution_runs_all_agents(self, tmp_path):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        (module_path / "README.md").write_text("# Test Module")
        
        # ACT
        report = orchestrator.analyze_module_comprehensive(
            module_path,
            parallel=True,
            max_workers=6
        )
        
        # ASSERT
        assert len(report.agent_reports) == 6
        assert report.execution_time_seconds > 0
        assert report.module_path == module_path
    
    def test_parallel_execution_handles_agent_failure_gracefully(self, tmp_path):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        
        # Mock one agent to fail
        with patch.object(
            orchestrator.agents['architect'],
            'analyze_module',
            side_effect=Exception("Mock agent failure")
        ):
            # ACT
            report = orchestrator.analyze_module_comprehensive(
                module_path,
                parallel=True
            )
            
            # ASSERT
            # Should still get reports from other agents
            assert len(report.agent_reports) == 5  # 6 - 1 failed


class TestSequentialExecution:
    """Test sequential agent execution"""
    
    def test_sequential_execution_runs_all_agents(self, tmp_path):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        (module_path / "README.md").write_text("# Test Module")
        
        # ACT
        report = orchestrator.analyze_module_comprehensive(
            module_path,
            parallel=False
        )
        
        # ASSERT
        assert len(report.agent_reports) == 6
        assert report.execution_time_seconds > 0
    
    def test_sequential_execution_handles_agent_failure(self, tmp_path):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        
        # Mock one agent to fail
        with patch.object(
            orchestrator.agents['security'],
            'analyze_module',
            side_effect=Exception("Mock agent failure")
        ):
            # ACT
            report = orchestrator.analyze_module_comprehensive(
                module_path,
                parallel=False
            )
            
            # ASSERT
            assert len(report.agent_reports) == 5  # 6 - 1 failed


class TestAgentSelection:
    """Test selective agent execution"""
    
    def test_can_run_selected_agents_only(self, tmp_path):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        
        # ACT
        report = orchestrator.analyze_module_comprehensive(
            module_path,
            parallel=True,
            selected_agents=['architect', 'security']
        )
        
        # ASSERT
        assert len(report.agent_reports) == 2
        agent_names = [r.agent_name for r in report.agent_reports]
        assert 'architect' in agent_names
        assert 'security' in agent_names
        assert 'performance' not in agent_names
    
    def test_empty_selection_runs_no_agents(self, tmp_path):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        
        # ACT
        report = orchestrator.analyze_module_comprehensive(
            module_path,
            selected_agents=[]
        )
        
        # ASSERT
        assert len(report.agent_reports) == 0


class TestReportSynthesis:
    """Test report synthesis from multiple agents"""
    
    def test_synthesize_reports_combines_findings(self):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        
        # Create mock reports
        report1 = AgentReport(
            agent_name="agent1",
            module_path=Path("."),
            execution_time_seconds=1.0,
            findings=[
                Finding(
                    category="Issue1",
                    severity=Severity.CRITICAL,
                    file_path=Path("file1.py"),
                    line_number=10,
                    description="Critical issue",
                    recommendation="Fix it"
                )
            ],
            metrics={},
            summary="Agent 1 summary"
        )
        
        report2 = AgentReport(
            agent_name="agent2",
            module_path=Path("."),
            execution_time_seconds=1.5,
            findings=[
                Finding(
                    category="Issue2",
                    severity=Severity.HIGH,
                    file_path=Path("file2.py"),
                    line_number=20,
                    description="High priority issue",
                    recommendation="Address this"
                )
            ],
            metrics={},
            summary="Agent 2 summary"
        )
        
        # ACT
        synthesized = orchestrator.synthesize_reports([report1, report2])
        
        # ASSERT
        assert len(synthesized.prioritized_actions) == 2
        assert synthesized.metrics_summary['total_findings'] == 2
        assert synthesized.metrics_summary['by_agent'] == {'agent1': 1, 'agent2': 1}
    
    def test_synthesize_sorts_by_severity(self):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        
        reports = [
            AgentReport(
                agent_name="agent1",
                module_path=Path("."),
                execution_time_seconds=1.0,
                findings=[
                    Finding(
                        category="Low",
                        severity=Severity.LOW,
                        file_path=Path("file.py"),
                        line_number=1,
                        description="Low priority",
                        recommendation="Fix when convenient"
                    ),
                    Finding(
                        category="Critical",
                        severity=Severity.CRITICAL,
                        file_path=Path("file.py"),
                        line_number=2,
                        description="Critical issue",
                        recommendation="Fix immediately"
                    )
                ],
                metrics={},
                summary="Test"
            )
        ]
        
        # ACT
        synthesized = orchestrator.synthesize_reports(reports)
        
        # ASSERT
        # CRITICAL should come first
        assert synthesized.prioritized_actions[0]['severity'] == 'critical'
        assert synthesized.prioritized_actions[1]['severity'] == 'low'


class TestConflictDetection:
    """Test detection of conflicting agent recommendations"""
    
    def test_detects_conflicts_same_location_different_recommendations(self):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        
        finding1 = Finding(
            category="Issue1",
            severity=Severity.HIGH,
            file_path=Path("file.py"),
            line_number=10,
            description="Problem A",
            recommendation="Solution A"
        )
        
        finding2 = Finding(
            category="Issue2",
            severity=Severity.HIGH,
            file_path=Path("file.py"),
            line_number=10,  # Same line
            description="Problem B",
            recommendation="Solution B"  # Different recommendation
        )
        
        # ACT
        conflicts = orchestrator._detect_conflicts([finding1, finding2])
        
        # ASSERT
        assert len(conflicts) == 1
        assert conflicts[0]['file'] == 'file.py'
        assert conflicts[0]['line'] == 10
        assert len(conflicts[0]['findings']) == 2
    
    def test_no_conflicts_when_recommendations_match(self):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        
        finding1 = Finding(
            category="Issue1",
            severity=Severity.HIGH,
            file_path=Path("file.py"),
            line_number=10,
            description="Problem",
            recommendation="Same solution"
        )
        
        finding2 = Finding(
            category="Issue2",
            severity=Severity.HIGH,
            file_path=Path("file.py"),
            line_number=10,  # Same line
            description="Problem",
            recommendation="Same solution"  # Same recommendation
        )
        
        # ACT
        conflicts = orchestrator._detect_conflicts([finding1, finding2])
        
        # ASSERT
        assert len(conflicts) == 0
    
    def test_skips_file_level_findings_in_conflict_detection(self):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        
        finding1 = Finding(
            category="Issue1",
            severity=Severity.MEDIUM,
            file_path=Path("README.md"),
            line_number=None,  # File-level finding
            description="Missing README",
            recommendation="Add README"
        )
        
        finding2 = Finding(
            category="Issue2",
            severity=Severity.MEDIUM,
            file_path=Path("README.md"),
            line_number=None,  # File-level finding
            description="Incomplete README",
            recommendation="Expand README"
        )
        
        # ACT
        conflicts = orchestrator._detect_conflicts([finding1, finding2])
        
        # ASSERT
        # File-level findings should not create conflicts
        assert len(conflicts) == 0


class TestHealthScoreCalculation:
    """Test overall health score calculation"""
    
    def test_perfect_score_with_no_findings(self):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        
        # ACT
        score = orchestrator._calculate_health_score([])
        
        # ASSERT
        assert score == 100.0
    
    def test_score_decreases_with_critical_findings(self):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        
        findings = [
            Finding(
                category="Critical1",
                severity=Severity.CRITICAL,
                file_path=Path("file.py"),
                line_number=1,
                description="Critical issue",
                recommendation="Fix"
            )
        ]
        
        # ACT
        score = orchestrator._calculate_health_score(findings)
        
        # ASSERT
        assert score == 90.0  # 100 - 10 (CRITICAL weight)
    
    def test_score_weighted_by_severity(self):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        
        findings = [
            Finding(category="C", severity=Severity.CRITICAL, file_path=Path("f"),
                   line_number=1, description="", recommendation=""),  # -10
            Finding(category="H", severity=Severity.HIGH, file_path=Path("f"),
                   line_number=2, description="", recommendation=""),     # -5
            Finding(category="M", severity=Severity.MEDIUM, file_path=Path("f"),
                   line_number=3, description="", recommendation=""),    # -2
            Finding(category="L", severity=Severity.LOW, file_path=Path("f"),
                   line_number=4, description="", recommendation="")      # -1
        ]
        
        # ACT
        score = orchestrator._calculate_health_score(findings)
        
        # ASSERT
        assert score == 82.0  # 100 - 10 - 5 - 2 - 1 = 82
    
    def test_score_clamped_to_zero_minimum(self):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        
        # Create many critical findings (would go negative without clamping)
        findings = [
            Finding(category=f"C{i}", severity=Severity.CRITICAL, file_path=Path("f"),
                   line_number=i, description="", recommendation="")
            for i in range(20)  # 20 * -10 = -200, but should clamp to 0
        ]
        
        # ACT
        score = orchestrator._calculate_health_score(findings)
        
        # ASSERT
        assert score == 0.0


class TestVisualization:
    """Test ASCII report visualization"""
    
    def test_visualize_report_formats_correctly(self, tmp_path):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        
        report = ComprehensiveReport(
            module_path=module_path,
            agent_reports=[
                AgentReport(
                    agent_name="agent1",
                    module_path=module_path,
                    execution_time_seconds=1.0,
                    findings=[
                        Finding(
                            category="Issue",
                            severity=Severity.HIGH,
                            file_path=Path("file.py"),
                            line_number=10,
                            description="Test issue",
                            recommendation="Test recommendation"
                        )
                    ],
                    metrics={},
                    summary="Test"
                )
            ],
            synthesized_plan=SynthesizedPlan(
                prioritized_actions=[
                    {
                        'agent': 'agent1',
                        'category': 'Issue',
                        'severity': 'high',
                        'file': 'file.py',
                        'line': 10,
                        'description': 'Test issue',
                        'recommendation': 'Test recommendation'
                    }
                ],
                conflicts=[],
                metrics_summary={
                    'total_findings': 1,
                    'by_severity': {'high': 1},
                    'by_agent': {'agent1': 1},
                    'agents_run': 1
                },
                overall_health_score=95.0
            ),
            execution_time_seconds=1.5
        )
        
        # ACT
        visualization = orchestrator.visualize_report(report)
        
        # ASSERT
        assert "COMPREHENSIVE MODULE ANALYSIS" in visualization
        assert "95/100" in visualization
        assert "EXCELLENT" in visualization
        assert "Agent1" in visualization  # Title case (agent_name.title())
        assert "Test recommendation" in visualization  # Shows recommendation, not description
    
    def test_visualize_report_shows_conflicts_when_present(self, tmp_path):
        # ARRANGE
        orchestrator = AgentOrchestrator()
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        
        report = ComprehensiveReport(
            module_path=module_path,
            agent_reports=[],
            synthesized_plan=SynthesizedPlan(
                prioritized_actions=[],
                conflicts=[
                    {
                        'file': 'conflict.py',
                        'line': 50,
                        'findings': [
                            {'category': 'Issue1', 'severity': 'high', 'recommendation': 'Fix A'},
                            {'category': 'Issue2', 'severity': 'high', 'recommendation': 'Fix B'}
                        ]
                    }
                ],
                metrics_summary={
                    'total_findings': 0,
                    'by_severity': {},
                    'by_agent': {},
                    'agents_run': 0
                },
                overall_health_score=100.0
            ),
            execution_time_seconds=1.0
        )
        
        # ACT
        visualization = orchestrator.visualize_report(report)
        
        # ASSERT
        assert "Conflicts Detected: 1" in visualization
        assert "conflict.py:50" in visualization


class TestSerialization:
    """Test report serialization"""
    
    def test_comprehensive_report_to_dict(self, tmp_path):
        # ARRANGE
        module_path = tmp_path / "test_module"
        module_path.mkdir()
        
        report = ComprehensiveReport(
            module_path=module_path,
            agent_reports=[],
            synthesized_plan=SynthesizedPlan(
                prioritized_actions=[],
                conflicts=[],
                metrics_summary={},
                overall_health_score=85.0
            ),
            execution_time_seconds=2.5
        )
        
        # ACT
        report_dict = report.to_dict()
        
        # ASSERT
        assert report_dict['module_path'] == str(module_path)
        assert report_dict['execution_time_seconds'] == 2.5
        assert report_dict['synthesized_plan']['overall_health_score'] == 85.0
    
    def test_synthesized_plan_to_dict(self):
        # ARRANGE
        plan = SynthesizedPlan(
            prioritized_actions=[{'test': 'action'}],
            conflicts=[{'test': 'conflict'}],
            metrics_summary={'total_findings': 5},
            overall_health_score=75.0
        )
        
        # ACT
        plan_dict = plan.to_dict()
        
        # ASSERT
        assert 'prioritized_actions' in plan_dict
        assert 'conflicts' in plan_dict
        assert 'metrics_summary' in plan_dict
        assert plan_dict['overall_health_score'] == 75.0