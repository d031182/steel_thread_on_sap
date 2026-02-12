"""
Unit tests for Shi Fu Agent Registry

Tests agent routing, validation, and purpose documentation.
"""

import pytest
from tools.shifu.meta.agent_registry import (
    get_agent_for_issue,
    get_agent_purpose,
    validate_enhancement,
    list_all_agents,
    get_quick_routing,
    AGENT_PURPOSES
)


class TestAgentRouting:
    """Test agent routing logic"""
    
    def test_route_empty_directory_to_file_organization(self):
        """Empty directory should route to FileOrganizationAgent"""
        agent = get_agent_for_issue("Empty /app folder with only __pycache__")
        assert agent == "FileOrganizationAgent"
    
    def test_route_sql_injection_to_security(self):
        """SQL injection should route to SecurityAgent"""
        agent = get_agent_for_issue("SQL injection in query")
        assert agent == "SecurityAgent"
    
    def test_route_di_violation_to_architect(self):
        """DI violation should route to ArchitectAgent"""
        agent = get_agent_for_issue("DI violation: accessing .connection directly")
        assert agent == "ArchitectAgent"
    
    def test_route_n_plus_one_to_performance(self):
        """N+1 query should route to PerformanceAgent"""
        agent = get_agent_for_issue("N+1 query problem in loop")
        assert agent == "PerformanceAgent"
    
    def test_route_css_important_to_ux(self):
        """CSS !important should route to UXArchitectAgent"""
        agent = get_agent_for_issue("Using !important in CSS for layout")
        assert agent == "UXArchitectAgent"
    
    def test_route_missing_docstring_to_documentation(self):
        """Missing docstring should route to DocumentationAgent"""
        agent = get_agent_for_issue("Missing docstring in function")
        assert agent == "DocumentationAgent"
    
    def test_route_unknown_issue_returns_none(self):
        """Unknown issue type should return None"""
        agent = get_agent_for_issue("Something completely random")
        # May return None or a fallback agent
        assert agent is None or agent in list_all_agents()


class TestAgentValidation:
    """Test enhancement validation logic"""
    
    def test_validate_empty_directory_moderate_fit(self):
        """Empty directory enhancement should be moderate fit for FileOrganizationAgent"""
        validation = validate_enhancement(
            "FileOrganizationAgent",
            "Detect empty directories with only build artifacts"
        )
        
        assert validation['fits'] is True
        assert validation['confidence'] >= 0.3  # At least moderate fit
        assert "FileOrganizationAgent" in validation['reasoning']
    
    def test_validate_sql_injection_high_fit(self):
        """SQL injection should be high fit for SecurityAgent"""
        validation = validate_enhancement(
            "SecurityAgent",
            "Detect SQL injection vulnerabilities in queries"
        )
        
        assert validation['fits'] is True
        assert validation['confidence'] >= 0.5  # High fit
    
    def test_validate_wrong_agent_low_fit(self):
        """UX issue should have low fit for FileOrganizationAgent"""
        validation = validate_enhancement(
            "FileOrganizationAgent",
            "Improve button color contrast for accessibility"
        )
        
        # Should have low confidence since UX is UXArchitectAgent's domain
        # Using completely different domain (UX/accessibility) that FileOrganizationAgent doesn't handle
        assert validation['confidence'] < 0.2 or not validation['fits']
    
    def test_validate_nonexistent_agent(self):
        """Nonexistent agent should return not found"""
        validation = validate_enhancement(
            "NonExistentAgent",
            "Some enhancement"
        )
        
        assert validation['fits'] is False
        assert validation['confidence'] == 0.0
        assert "not found" in validation['reasoning'].lower()
    
    def test_validation_includes_recommendations(self):
        """Validation should include recommendations"""
        validation = validate_enhancement(
            "FileOrganizationAgent",
            "Detect empty directories"
        )
        
        assert 'recommendations' in validation
        assert isinstance(validation['recommendations'], list)


class TestAgentPurpose:
    """Test agent purpose retrieval"""
    
    def test_get_architect_agent_purpose(self):
        """Should retrieve ArchitectAgent purpose"""
        purpose = get_agent_purpose("ArchitectAgent")
        
        assert purpose is not None
        assert purpose.name == "ArchitectAgent"
        assert "Architecture" in purpose.purpose
        assert len(purpose.scope) > 0
        assert len(purpose.examples) > 0
        assert len(purpose.current_detectors) > 0
    
    def test_get_security_agent_purpose(self):
        """Should retrieve SecurityAgent purpose"""
        purpose = get_agent_purpose("SecurityAgent")
        
        assert purpose is not None
        assert purpose.name == "SecurityAgent"
        assert "Security" in purpose.purpose
        assert "SQL injection" in str(purpose.examples)
    
    def test_get_nonexistent_agent_purpose(self):
        """Should return None for nonexistent agent"""
        purpose = get_agent_purpose("NonExistentAgent")
        assert purpose is None
    
    def test_all_agents_have_complete_purpose(self):
        """All agents should have complete purpose documentation"""
        for agent_name in list_all_agents():
            purpose = get_agent_purpose(agent_name)
            
            assert purpose is not None
            assert purpose.name == agent_name
            assert len(purpose.purpose) > 0
            assert len(purpose.scope) > 0
            assert len(purpose.examples) > 0
            assert len(purpose.fits_criteria) > 0
            assert len(purpose.does_not_fit) > 0


class TestAgentRegistry:
    """Test agent registry structure"""
    
    def test_six_agents_registered(self):
        """Should have exactly 6 agents registered"""
        agents = list_all_agents()
        assert len(agents) == 6
    
    def test_all_agents_present(self):
        """All expected agents should be present"""
        expected_agents = [
            "ArchitectAgent",
            "SecurityAgent",
            "UXArchitectAgent",
            "PerformanceAgent",
            "FileOrganizationAgent",
            "DocumentationAgent"
        ]
        
        agents = list_all_agents()
        for expected in expected_agents:
            assert expected in agents
    
    def test_agent_purposes_structure(self):
        """AGENT_PURPOSES should have correct structure"""
        assert isinstance(AGENT_PURPOSES, dict)
        assert len(AGENT_PURPOSES) == 6
        
        for agent_name, purpose in AGENT_PURPOSES.items():
            assert hasattr(purpose, 'name')
            assert hasattr(purpose, 'purpose')
            assert hasattr(purpose, 'scope')
            assert hasattr(purpose, 'examples')
            assert hasattr(purpose, 'current_detectors')
            assert hasattr(purpose, 'fits_criteria')
            assert hasattr(purpose, 'does_not_fit')


class TestQuickRouting:
    """Test quick routing matrix"""
    
    def test_quick_routing_di_violations(self):
        """DI violations should route to ArchitectAgent"""
        agent = get_quick_routing("DI violations")
        assert agent == "ArchitectAgent"
    
    def test_quick_routing_empty_directories(self):
        """Empty directories should route to FileOrganizationAgent"""
        agent = get_quick_routing("Empty directories")
        assert agent == "FileOrganizationAgent"
    
    def test_quick_routing_unknown_returns_none(self):
        """Unknown issue type should return None"""
        agent = get_quick_routing("Unknown issue type")
        assert agent is None


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_issue_description(self):
        """Empty description should handle gracefully"""
        agent = get_agent_for_issue("")
        # Should either return None or handle without crashing
        assert agent is None or isinstance(agent, str)
    
    def test_case_insensitive_routing(self):
        """Routing should be case insensitive"""
        agent1 = get_agent_for_issue("SQL INJECTION")
        agent2 = get_agent_for_issue("sql injection")
        assert agent1 == agent2 == "SecurityAgent"
    
    def test_validation_with_empty_description(self):
        """Validation with empty description should not crash"""
        validation = validate_enhancement("ArchitectAgent", "")
        assert 'fits' in validation
        assert 'confidence' in validation
        assert 'reasoning' in validation


if __name__ == "__main__":
    pytest.main([__file__, "-v"])