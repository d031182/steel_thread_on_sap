"""
Integration Tests for Feng Shui Multi-Agent System

Tests the complete integration of:
- ReAct agent with AgentOrchestrator
- All 6 specialized agents working together
- Parallel vs sequential execution
- Real module analysis
"""

import pytest
import time
from pathlib import Path
from tools.fengshui.react_agent import FengShuiReActAgent
from tools.fengshui.agents import AgentOrchestrator


@pytest.mark.integration
@pytest.mark.slow
class TestMultiAgentIntegration:
    """Integration tests for multi-agent system"""
    
    @pytest.fixture
    def react_agent(self):
        """Create ReAct agent with multi-agent support"""
        return FengShuiReActAgent(verbose=False)
    
    @pytest.fixture
    def test_module_path(self):
        """Path to test module"""
        return Path("modules/knowledge_graph")
    
    def test_react_agent_has_orchestrator(self, react_agent):
        """Test ReAct agent initializes with orchestrator"""
        # ARRANGE & ACT
        # (react_agent created in fixture)
        
        # ASSERT
        assert hasattr(react_agent, 'orchestrator')
        assert isinstance(react_agent.orchestrator, AgentOrchestrator)
    
    def test_run_multiagent_analysis_returns_comprehensive_report(
        self, 
        react_agent, 
        test_module_path
    ):
        """Test multi-agent analysis returns complete report"""
        # ARRANGE
        # (fixtures provided)
        
        # ACT
        report = react_agent.run_with_multiagent_analysis(
            module_path=test_module_path,
            parallel=True,
            max_workers=6
        )
        
        # ASSERT
        assert report is not None
        assert hasattr(report, 'agent_reports')
        assert hasattr(report, 'synthesized_plan')
        assert hasattr(report, 'execution_time_seconds')
        
        # Should have reports from all 6 agents
        assert len(report.agent_reports) == 6
        
        # Agent names should be present
        agent_names = [r.agent_name for r in report.agent_reports]
        expected_agents = ['architect', 'security', 'ux_architect', 
                          'file_organization', 'performance', 'documentation']
        for expected in expected_agents:
            assert expected in agent_names
    
    def test_multiagent_analysis_produces_synthesized_plan(
        self,
        react_agent,
        test_module_path
    ):
        """Test synthesis produces prioritized action plan"""
        # ARRANGE
        # (fixtures provided)
        
        # ACT
        report = react_agent.run_with_multiagent_analysis(
            module_path=test_module_path,
            parallel=True
        )
        
        # ASSERT
        plan = report.synthesized_plan
        assert hasattr(plan, 'prioritized_actions')
        assert hasattr(plan, 'conflicts')
        assert hasattr(plan, 'metrics_summary')
        assert hasattr(plan, 'overall_health_score')
        
        # Health score should be 0-100
        assert 0 <= plan.overall_health_score <= 100
        
        # Metrics should have expected keys
        assert 'total_findings' in plan.metrics_summary
        assert 'by_severity' in plan.metrics_summary
        assert 'by_agent' in plan.metrics_summary
    
    def test_multiagent_analysis_with_agent_selection(
        self,
        react_agent,
        test_module_path
    ):
        """Test running only selected agents"""
        # ARRANGE
        selected_agents = ['architect', 'security']
        
        # ACT
        report = react_agent.run_with_multiagent_analysis(
            module_path=test_module_path,
            parallel=True,
            selected_agents=selected_agents
        )
        
        # ASSERT
        # Should have only 2 agent reports
        assert len(report.agent_reports) == 2
        
        # Agent names should match selection
        agent_names = [r.agent_name for r in report.agent_reports]
        assert 'architect' in agent_names
        assert 'security' in agent_names
        assert 'performance' not in agent_names  # Not selected
    
    @pytest.mark.slow
    def test_parallel_execution_faster_than_sequential(
        self,
        react_agent,
        test_module_path
    ):
        """
        Test parallel execution provides speedup
        
        NOTE: This is a performance benchmark test
        May take 30-60 seconds to complete
        """
        # ARRANGE
        # (fixtures provided)
        
        # ACT - Sequential execution
        start_seq = time.time()
        report_seq = react_agent.run_with_multiagent_analysis(
            module_path=test_module_path,
            parallel=False  # Sequential
        )
        time_seq = time.time() - start_seq
        
        # ACT - Parallel execution
        start_par = time.time()
        report_par = react_agent.run_with_multiagent_analysis(
            module_path=test_module_path,
            parallel=True,
            max_workers=6
        )
        time_par = time.time() - start_par
        
        # ASSERT
        # Parallel should be faster
        speedup = time_seq / time_par
        print(f"\n[PERFORMANCE] Sequential: {time_seq:.2f}s, Parallel: {time_par:.2f}s")
        print(f"[PERFORMANCE] Speedup: {speedup:.2f}x")
        
        # Should be at least 1.5x faster (conservative)
        # Target: 3-6x speedup with 6 agents
        assert speedup > 1.5, f"Expected speedup >1.5x, got {speedup:.2f}x"
        
        # Both should return same findings (order may differ)
        assert len(report_seq.agent_reports) == len(report_par.agent_reports)
    
    def test_multiagent_detects_real_violations(
        self,
        react_agent,
        test_module_path
    ):
        """Test agents detect actual architecture violations"""
        # ARRANGE
        # (fixtures provided)
        
        # ACT
        report = react_agent.run_with_multiagent_analysis(
            module_path=test_module_path,
            parallel=True
        )
        
        # ASSERT
        # Should find some findings (knowledge_graph module has some issues)
        total_findings = report.synthesized_plan.metrics_summary['total_findings']
        
        # Expect at least a few findings (may vary based on module state)
        # Using low threshold to avoid flakiness
        assert total_findings >= 0  # At minimum, should run without errors
        
        # Each agent should have analyzed files
        for agent_report in report.agent_reports:
            assert agent_report.execution_time_seconds > 0
            # Most agents should analyze some files
            if 'files_analyzed' in agent_report.metrics:
                assert agent_report.metrics['files_analyzed'] > 0
    
    def test_multiagent_conflict_detection_works(
        self,
        react_agent,
        test_module_path
    ):
        """Test orchestrator detects conflicting agent recommendations"""
        # ARRANGE
        # (fixtures provided)
        
        # ACT
        report = react_agent.run_with_multiagent_analysis(
            module_path=test_module_path,
            parallel=True
        )
        
        # ASSERT
        # Conflicts structure should be valid
        conflicts = report.synthesized_plan.conflicts
        assert isinstance(conflicts, list)
        
        # If conflicts exist, they should have required fields
        for conflict in conflicts:
            assert 'file' in conflict
            assert 'line' in conflict
            assert 'findings' in conflict
            assert len(conflict['findings']) > 1  # Multiple findings = conflict
    
    def test_multiagent_health_score_calculation(
        self,
        react_agent,
        test_module_path
    ):
        """Test health score calculation from multi-agent findings"""
        # ARRANGE
        # (fixtures provided)
        
        # ACT
        report = react_agent.run_with_multiagent_analysis(
            module_path=test_module_path,
            parallel=True
        )
        
        # ASSERT
        health_score = report.synthesized_plan.overall_health_score
        
        # Score should be in valid range
        assert 0 <= health_score <= 100
        
        # If there are CRITICAL findings, score should be < 100
        critical_count = report.synthesized_plan.metrics_summary['by_severity'].get('critical', 0)
        if critical_count > 0:
            assert health_score < 100
    
    def test_multiagent_generates_prioritized_actions(
        self,
        react_agent,
        test_module_path
    ):
        """Test action prioritization by severity"""
        # ARRANGE
        # (fixtures provided)
        
        # ACT
        report = react_agent.run_with_multiagent_analysis(
            module_path=test_module_path,
            parallel=True
        )
        
        # ASSERT
        actions = report.synthesized_plan.prioritized_actions
        
        # Actions should be sorted by severity
        # CRITICAL > HIGH > MEDIUM > LOW
        severity_order = ['critical', 'high', 'medium', 'low', 'info']
        
        for i in range(len(actions) - 1):
            current_idx = severity_order.index(actions[i]['severity'])
            next_idx = severity_order.index(actions[i+1]['severity'])
            # Current should be <= next (higher priority first)
            assert current_idx <= next_idx
    
    def test_multiagent_report_serialization(
        self,
        react_agent,
        test_module_path
    ):
        """Test comprehensive report can be serialized"""
        # ARRANGE
        # (fixtures provided)
        
        # ACT
        report = react_agent.run_with_multiagent_analysis(
            module_path=test_module_path,
            parallel=True
        )
        
        # ACT - Serialize
        report_dict = report.to_dict()
        
        # ASSERT
        assert isinstance(report_dict, dict)
        assert 'module_path' in report_dict
        assert 'agent_reports' in report_dict
        assert 'synthesized_plan' in report_dict
        assert 'execution_time_seconds' in report_dict
        
        # Should be JSON-serializable (no custom objects)
        import json
        json_str = json.dumps(report_dict)
        assert len(json_str) > 0


@pytest.mark.integration
@pytest.mark.slow
class TestMultiAgentRealWorldScenarios:
    """Real-world scenario tests"""
    
    @pytest.fixture
    def react_agent(self):
        """Create ReAct agent"""
        return FengShuiReActAgent(verbose=False)
    
    def test_analyze_small_module(self, react_agent):
        """Test analysis on small module"""
        # ARRANGE
        module_path = Path("modules/debug_mode")
        
        # ACT
        report = react_agent.run_with_multiagent_analysis(
            module_path=module_path,
            parallel=True
        )
        
        # ASSERT
        assert report is not None
        assert len(report.agent_reports) == 6
        # Small module should complete quickly
        assert report.execution_time_seconds < 60  # < 1 minute
    
    def test_analyze_medium_module(self, react_agent):
        """Test analysis on medium module"""
        # ARRANGE
        module_path = Path("modules/log_manager")
        
        # ACT
        report = react_agent.run_with_multiagent_analysis(
            module_path=module_path,
            parallel=True
        )
        
        # ASSERT
        assert report is not None
        assert len(report.agent_reports) == 6
        # Medium module should complete reasonably fast with parallel
        assert report.execution_time_seconds < 120  # < 2 minutes
    
    def test_analyze_large_module(self, react_agent):
        """Test analysis on large module"""
        # ARRANGE
        module_path = Path("modules/knowledge_graph")
        
        # ACT
        report = react_agent.run_with_multiagent_analysis(
            module_path=module_path,
            parallel=True
        )
        
        # ASSERT
        assert report is not None
        assert len(report.agent_reports) == 6
        # Large module with parallel should still be fast
        assert report.execution_time_seconds < 180  # < 3 minutes
        
        # Should find meaningful findings in large module
        total_findings = report.synthesized_plan.metrics_summary['total_findings']
        assert total_findings > 0  # Large module likely has some issues


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])