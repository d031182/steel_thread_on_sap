"""
Unit Tests for Feng Shui Log Intelligence Integration
======================================================
Tests Phase 2 integration of log intelligence with Feng Shui agents.

Author: P2P Development Team
Version: 1.0.0
Date: 2026-02-07
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from tools.fengshui.agents.architect_agent import ArchitectAgent
from tools.fengshui.agents.orchestrator import AgentOrchestrator
from core.interfaces.log_intelligence import NullLogAdapter, LogAdapterInterface


class TestArchitectAgentLogIntegration:
    """Test ArchitectAgent with log intelligence"""
    
    def test_architect_works_without_logs(self):
        """ArchitectAgent works without log adapter (backward compatibility)"""
        # Create agent without log adapter
        agent = ArchitectAgent()
        
        # Should work fine (graceful degradation)
        assert agent is not None
        assert agent.log_adapter is None
        
        # Capabilities should not include runtime detection
        capabilities = agent.get_capabilities()
        assert "static" in str(capabilities)
        assert "runtime from logs" not in str(capabilities)
    
    def test_architect_with_null_adapter(self):
        """ArchitectAgent with NullLogAdapter (no runtime detection)"""
        # Create agent with null adapter
        null_adapter = NullLogAdapter()
        agent = ArchitectAgent(log_adapter=null_adapter)
        
        # Should work fine
        assert agent is not None
        assert agent.log_adapter is not None
        assert not agent.log_adapter.is_available()
        
        # Capabilities should not include runtime detection
        capabilities = agent.get_capabilities()
        assert "runtime from logs" not in str(capabilities)
    
    def test_architect_with_mock_adapter(self):
        """ArchitectAgent with mock log adapter (runtime detection enabled)"""
        # Create mock adapter that reports available
        mock_adapter = Mock(spec=LogAdapterInterface)
        mock_adapter.is_available.return_value = True
        mock_adapter.detect_error_patterns.return_value = []
        
        agent = ArchitectAgent(log_adapter=mock_adapter)
        
        # Should have runtime capability
        assert agent.log_adapter is not None
        assert agent.log_adapter.is_available()
        
        capabilities = agent.get_capabilities()
        assert "runtime from logs" in str(capabilities).lower()
    
    def test_runtime_detection_with_di_errors(self, tmp_path):
        """Runtime DI detection finds violations from logs"""
        # Create mock adapter with DI violation patterns
        mock_adapter = Mock(spec=LogAdapterInterface)
        mock_adapter.is_available.return_value = True
        mock_adapter.detect_error_patterns.return_value = [
            {
                'pattern': "AttributeError: NoneType has no attribute 'connection'",
                'count': 15,
                'locations': ['test_module/api.py:45', 'test_module/service.py:123'],
                'severity': 'CRITICAL',
                'first_seen': '2026-02-07T10:00:00',
                'last_seen': '2026-02-07T12:00:00'
            }
        ]
        
        # Create test module structure
        test_module = tmp_path / "test_module"
        test_module.mkdir()
        
        # Create agent with mock adapter
        agent = ArchitectAgent(log_adapter=mock_adapter)
        
        # Run analysis
        report = agent.analyze_module(test_module)
        
        # Should have called detect_error_patterns
        mock_adapter.detect_error_patterns.assert_called_once()
        
        # Should have runtime DI findings
        runtime_findings = [f for f in report.findings if 'Runtime' in f.category]
        assert len(runtime_findings) > 0
        
        # Findings should be CRITICAL severity
        for finding in runtime_findings:
            assert finding.severity.value == 'critical'


class TestOrchestratorLogIntegration:
    """Test AgentOrchestrator with log intelligence"""
    
    def test_orchestrator_without_adapter(self):
        """Orchestrator works without log adapter"""
        # Create orchestrator without adapter (auto-detect)
        orchestrator = AgentOrchestrator()
        
        # Should work fine
        assert orchestrator is not None
        assert 'architect' in orchestrator.agents
    
    def test_orchestrator_with_null_adapter(self):
        """Orchestrator with NullLogAdapter"""
        null_adapter = NullLogAdapter()
        orchestrator = AgentOrchestrator(log_adapter=null_adapter)
        
        # Should work fine
        assert orchestrator is not None
        
        # ArchitectAgent should have null adapter
        architect = orchestrator.agents['architect']
        assert architect.log_adapter is not None
        assert not architect.log_adapter.is_available()
    
    def test_orchestrator_with_mock_adapter(self):
        """Orchestrator with mock log adapter"""
        mock_adapter = Mock(spec=LogAdapterInterface)
        mock_adapter.is_available.return_value = True
        
        orchestrator = AgentOrchestrator(log_adapter=mock_adapter)
        
        # ArchitectAgent should have mock adapter
        architect = orchestrator.agents['architect']
        assert architect.log_adapter is not None
        assert architect.log_adapter.is_available()


class TestGracefulDegradation:
    """Test graceful degradation when log intelligence fails"""
    
    def test_runtime_detection_handles_errors(self, tmp_path):
        """Runtime detection handles errors gracefully"""
        # Create mock adapter that throws exceptions
        mock_adapter = Mock(spec=LogAdapterInterface)
        mock_adapter.is_available.return_value = True
        mock_adapter.detect_error_patterns.side_effect = Exception("DB error")
        
        # Create test module
        test_module = tmp_path / "test_module"
        test_module.mkdir()
        
        # Create agent
        agent = ArchitectAgent(log_adapter=mock_adapter)
        
        # Should not crash (graceful degradation)
        report = agent.analyze_module(test_module)
        
        # Should still return valid report (without runtime findings)
        assert report is not None
        assert isinstance(report.findings, list)


# Pytest markers
pytestmark = [
    pytest.mark.unit,
    pytest.mark.fast
]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])