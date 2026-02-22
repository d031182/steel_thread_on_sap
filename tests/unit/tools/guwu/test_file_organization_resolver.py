"""
Tests for File Organization Resolver

Tests the FileOrganizationResolver's ability to process Feng Shui findings
and resolve file organization issues.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from tools.guwu.resolvers.file_organization_resolver import FileOrganizationResolver
from tools.guwu.resolvers.base_resolver import ResolutionStatus


class TestFileOrganizationResolver:
    """Test FileOrganizationResolver capabilities"""
    
    @pytest.fixture
    def resolver(self):
        """Create resolver instance"""
        return FileOrganizationResolver()
    
    def test_initialization(self, resolver):
        """Test resolver initializes correctly"""
        assert resolver.name == "file_organization"
        assert len(resolver.supported_categories) > 0
        assert "Root Directory Clutter" in resolver.supported_categories
    
    def test_get_capabilities(self, resolver):
        """Test capabilities list"""
        capabilities = resolver.get_capabilities()
        assert len(capabilities) > 0
        assert any("move" in cap.lower() for cap in capabilities)
    
    def test_can_resolve_supported_category(self, resolver):
        """Test can_resolve returns True for supported categories"""
        finding = Mock()
        finding.category = "Root Directory Clutter"
        
        assert resolver.can_resolve(finding) is True
    
    def test_can_resolve_unsupported_category(self, resolver):
        """Test can_resolve returns False for unsupported categories"""
        finding = Mock()
        finding.category = "Unknown Category"
        
        assert resolver.can_resolve(finding) is False
    
    def test_extract_action_move(self, resolver):
        """Test extracting MOVE action from recommendation"""
        recommendation = "MOVE to tests/ai_assistant/"
        action = resolver._extract_action(recommendation)
        
        assert action == "MOVE"
    
    def test_extract_action_delete(self, resolver):
        """Test extracting DELETE action from recommendation"""
        recommendation = "DELETE (temporary file)"
        action = resolver._extract_action(recommendation)
        
        assert action == "DELETE"
    
    def test_extract_action_none(self, resolver):
        """Test extracting action returns None for unknown format"""
        recommendation = "Review this file manually"
        action = resolver._extract_action(recommendation)
        
        assert action is None
    
    def test_resolve_finding_dry_run(self, resolver):
        """Test resolve_finding in dry-run mode"""
        finding = Mock()
        finding.category = "Root Directory Clutter"
        finding.file_path = "test_file.txt"
        finding.recommendation = "MOVE to docs/"
        
        result = resolver.resolve_finding(finding, dry_run=True)
        
        assert result.status == ResolutionStatus.SUCCESS
        assert len(result.dry_run_actions) > 0
        assert any("WOULD move" in action for action in result.dry_run_actions)
    
    def test_resolve_finding_no_action(self, resolver):
        """Test resolve_finding with unclear recommendation"""
        finding = Mock()
        finding.category = "Root Directory Clutter"
        finding.file_path = "test_file.txt"
        finding.recommendation = "Unclear recommendation"
        
        result = resolver.resolve_finding(finding, dry_run=True)
        
        assert result.status == ResolutionStatus.FAILED
        assert len(result.errors) > 0
    
    def test_simulate_move_action(self, resolver):
        """Test _simulate_resolution for MOVE action"""
        finding = Mock()
        finding.file_path = "test_file.py"
        finding.recommendation = "MOVE to tests/unit/"
        
        result = Mock()
        result.dry_run_actions = []
        result.add_dry_run_action = lambda action: result.dry_run_actions.append(action)
        
        resolver._simulate_resolution(finding, "MOVE", result)
        
        assert len(result.dry_run_actions) >= 1
        assert any("WOULD move" in action for action in result.dry_run_actions)
    
    def test_simulate_delete_action(self, resolver):
        """Test _simulate_resolution for DELETE action"""
        finding = Mock()
        finding.file_path = "temp_file.txt"
        finding.recommendation = "DELETE (obsolete)"
        
        result = Mock()
        result.dry_run_actions = []
        result.add_dry_run_action = lambda action: result.dry_run_actions.append(action)
        
        resolver._simulate_resolution(finding, "DELETE", result)
        
        assert len(result.dry_run_actions) > 0
        assert any("WOULD delete" in action for action in result.dry_run_actions)
    
    def test_get_supported_categories(self, resolver):
        """Test get_supported_categories returns complete set"""
        categories = resolver.get_supported_categories()
        
        assert isinstance(categories, set)
        assert len(categories) > 0
        assert "Root Directory Clutter" in categories
        assert "Misplaced Script" in categories


if __name__ == "__main__":
    pytest.main([__file__, "-v"])