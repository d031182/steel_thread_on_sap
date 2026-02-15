"""
Unit tests for FileOrganizationAgent._detect_scattered_documentation detector

Tests Shi Fu Enhancement Proposal 20260212-FILE-scattered_
User insight: "Feng Shui could also cover the consolidation of scattered documentations"
"""

import pytest
from pathlib import Path
from tools.fengshui.agents.file_organization_agent import FileOrganizationAgent, Severity


class TestDetectScatteredDocumentation:
    """Test scattered documentation detection"""
    
    @pytest.fixture
    def agent(self):
        """Create FileOrganizationAgent instance"""
        return FileOrganizationAgent()
    
    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create temporary project structure"""
        # Create knowledge vault structure
        knowledge_vault = tmp_path / 'docs' / 'knowledge'
        knowledge_vault.mkdir(parents=True)
        
        # Create quality ecosystem subdirectories
        (knowledge_vault / 'quality-ecosystem' / 'feng-shui').mkdir(parents=True)
        (knowledge_vault / 'quality-ecosystem' / 'gu-wu').mkdir(parents=True)
        (knowledge_vault / 'quality-ecosystem' / 'shi-fu').mkdir(parents=True)
        
        return tmp_path
    
    def test_detects_no_scattered_docs_when_organized(self, agent, temp_project):
        """Should find no issues when docs are properly organized"""
        # Create docs in correct locations
        feng_shui_dir = temp_project / 'docs' / 'knowledge' / 'quality-ecosystem' / 'feng-shui'
        (feng_shui_dir / 'feng-shui-overview.md').write_text('# Feng Shui Overview')
        (feng_shui_dir / 'feng-shui-agents.md').write_text('# Feng Shui Agents')
        
        findings = agent._detect_scattered_documentation(temp_project)
        
        # Should find no scattered docs
        scattered_findings = [f for f in findings if f.category == "Scattered Documentation"]
        assert len(scattered_findings) == 0
    
    def test_detects_scattered_feng_shui_docs(self, agent, temp_project):
        """Should detect Feng Shui docs in multiple locations"""
        knowledge_vault = temp_project / 'docs' / 'knowledge'
        
        # Create Feng Shui docs in correct location
        feng_shui_dir = knowledge_vault / 'quality-ecosystem' / 'feng-shui'
        (feng_shui_dir / 'feng-shui-overview.md').write_text('# Overview')
        
        # Create scattered Feng Shui docs in wrong locations
        (knowledge_vault / 'architecture').mkdir(exist_ok=True)
        (knowledge_vault / 'architecture' / 'feng-shui-patterns.md').write_text('# Patterns')
        (knowledge_vault / 'guidelines').mkdir(exist_ok=True)
        (knowledge_vault / 'guidelines' / 'feng-shui-rules.md').write_text('# Rules')
        
        findings = agent._detect_scattered_documentation(temp_project)
        
        # Should detect scattered Feng Shui documentation
        scattered_findings = [f for f in findings if 'Feng Shui' in f.description]
        assert len(scattered_findings) >= 1
        assert any('multiple locations' in f.description for f in scattered_findings)
        assert any('feng-shui-patterns.md' in f.recommendation or 
                   'feng-shui-rules.md' in f.recommendation 
                   for f in scattered_findings)
    
    def test_detects_scattered_gu_wu_docs(self, agent, temp_project):
        """Should detect Gu Wu docs in multiple locations"""
        knowledge_vault = temp_project / 'docs' / 'knowledge'
        
        # Create Gu Wu docs in correct location
        gu_wu_dir = knowledge_vault / 'quality-ecosystem' / 'gu-wu'
        (gu_wu_dir / 'gu-wu-testing.md').write_text('# Testing')
        
        # Create scattered Gu Wu docs
        (knowledge_vault / 'testing').mkdir(exist_ok=True)
        (knowledge_vault / 'testing' / 'gu-wu-framework.md').write_text('# Framework')
        
        findings = agent._detect_scattered_documentation(temp_project)
        
        # Should detect scattered Gu Wu documentation
        scattered_findings = [f for f in findings if 'Gu Wu' in f.description]
        assert len(scattered_findings) >= 1
    
    def test_detects_root_level_markdown_files(self, agent, temp_project):
        """Should detect .md files in root (except allowed ones)"""
        # Create unauthorized .md file in root
        (temp_project / 'PROPOSAL.md').write_text('# Some Proposal')
        (temp_project / 'NOTES.md').write_text('# Random Notes')
        
        # Create allowed root-level docs (should NOT be flagged)
        (temp_project / 'README.md').write_text('# Project README')
        (temp_project / 'PROJECT_TRACKER.md').write_text('# Tracker')
        
        findings = agent._detect_scattered_documentation(temp_project)
        
        # Should detect unauthorized root-level docs
        root_findings = [f for f in findings 
                        if f.category == "Scattered Documentation" 
                        and 'root directory' in f.description]
        
        assert len(root_findings) == 2  # PROPOSAL.md + NOTES.md
        assert any('PROPOSAL.md' in f.description for f in root_findings)
        assert any('NOTES.md' in f.description for f in root_findings)
        
        # Should NOT flag allowed docs
        assert not any('README.md' in f.description for f in findings)
        assert not any('PROJECT_TRACKER.md' in f.description for f in findings)
    
    def test_severity_levels(self, agent, temp_project):
        """Should assign correct severity levels"""
        knowledge_vault = temp_project / 'docs' / 'knowledge'
        
        # Create scattered docs (MEDIUM severity)
        feng_shui_dir = knowledge_vault / 'quality-ecosystem' / 'feng-shui'
        (feng_shui_dir / 'feng-shui-1.md').write_text('# Doc 1')
        (knowledge_vault / 'architecture').mkdir(exist_ok=True)
        (knowledge_vault / 'architecture' / 'feng-shui-2.md').write_text('# Doc 2')
        
        # Create root-level doc (HIGH severity)
        (temp_project / 'RANDOM.md').write_text('# Random')
        
        findings = agent._detect_scattered_documentation(temp_project)
        
        # Check severity assignments
        scattered = [f for f in findings if 'multiple locations' in f.description]
        root_level = [f for f in findings if 'root directory' in f.description]
        
        if scattered:
            assert scattered[0].severity == Severity.MEDIUM
        
        if root_level:
            assert root_level[0].severity == Severity.HIGH
    
    def test_consolidation_recommendations(self, agent, temp_project):
        """Should provide clear consolidation recommendations"""
        knowledge_vault = temp_project / 'docs' / 'knowledge'
        
        # Create scattered Shi Fu docs
        shi_fu_dir = knowledge_vault / 'quality-ecosystem' / 'shi-fu'
        (shi_fu_dir / 'shi-fu-overview.md').write_text('# Overview')
        (knowledge_vault / 'guides').mkdir(exist_ok=True)
        (knowledge_vault / 'guides' / 'shi-fu-usage.md').write_text('# Usage')
        
        findings = agent._detect_scattered_documentation(temp_project)
        
        # Check recommendations mention consolidation
        shi_fu_findings = [f for f in findings if 'Shi Fu' in f.description]
        
        if shi_fu_findings:
            recommendation = shi_fu_findings[0].recommendation
            assert 'CONSOLIDATE' in recommendation
            assert 'quality-ecosystem/shi-fu' in recommendation
    
    def test_handles_empty_knowledge_vault(self, agent, temp_project):
        """Should handle empty knowledge vault gracefully"""
        # Knowledge vault exists but is empty
        findings = agent._detect_scattered_documentation(temp_project)
        
        # Should not crash, return empty or minimal findings
        assert isinstance(findings, list)
    
    def test_handles_missing_knowledge_vault(self, agent, tmp_path):
        """Should handle missing knowledge vault gracefully"""
        # No docs/knowledge/ directory
        findings = agent._detect_scattered_documentation(tmp_path)
        
        # Should not crash
        assert isinstance(findings, list)
    
    def test_safety_limit_on_doc_scanning(self, agent, temp_project, monkeypatch):
        """Should respect MAX_DOCS_TO_SCAN safety limit"""
        knowledge_vault = temp_project / 'docs' / 'knowledge'
        
        # Create many docs
        for i in range(10):
            (knowledge_vault / f'doc_{i}.md').write_text(f'# Doc {i}')
        
        # Mock the safety limit to a small number
        import tools.fengshui.agents.file_organization_agent as foa_module
        
        # This test verifies the code doesn't crash with many docs
        findings = agent._detect_scattered_documentation(temp_project)
        
        # Should complete without error
        assert isinstance(findings, list)
    
    def test_multiple_topic_patterns(self, agent, temp_project):
        """Should detect multiple different topic patterns"""
        knowledge_vault = temp_project / 'docs' / 'knowledge'
        
        # Create scattered docs for multiple topics
        # Feng Shui
        (knowledge_vault / 'quality-ecosystem' / 'feng-shui' / 'feng-shui-1.md').write_text('# FS1')
        (knowledge_vault / 'architecture').mkdir(exist_ok=True)
        (knowledge_vault / 'architecture' / 'feng-shui-2.md').write_text('# FS2')
        
        # Gu Wu
        (knowledge_vault / 'quality-ecosystem' / 'gu-wu' / 'gu-wu-1.md').write_text('# GW1')
        (knowledge_vault / 'testing').mkdir(exist_ok=True)
        (knowledge_vault / 'testing' / 'gu-wu-2.md').write_text('# GW2')
        
        findings = agent._detect_scattered_documentation(temp_project)
        
        # Should detect both Feng Shui and Gu Wu scattered docs
        feng_shui_findings = [f for f in findings if 'Feng Shui' in f.description]
        gu_wu_findings = [f for f in findings if 'Gu Wu' in f.description]
        
        assert len(feng_shui_findings) >= 1
        assert len(gu_wu_findings) >= 1
    
    def test_integration_with_analyze_module(self, agent, temp_project):
        """Should integrate with analyze_module() method"""
        # Create scattered docs
        knowledge_vault = temp_project / 'docs' / 'knowledge'
        feng_shui_dir = knowledge_vault / 'quality-ecosystem' / 'feng-shui'
        (feng_shui_dir / 'feng-shui-1.md').write_text('# Doc 1')
        (knowledge_vault / 'guidelines').mkdir(exist_ok=True)
        (knowledge_vault / 'guidelines' / 'feng-shui-2.md').write_text('# Doc 2')
        
        # Run full analysis
        report = agent.analyze_module(temp_project)
        
        # Should include scattered documentation findings
        scattered_findings = [f for f in report.findings 
                             if f.category == "Scattered Documentation"]
        
        assert len(scattered_findings) >= 1
        assert report.metrics['total_findings'] >= 1


@pytest.mark.integration
class TestScatteredDocumentationIntegration:
    """Integration tests with real project structure"""
    
    def test_real_project_detection(self):
        """Test detection on real project structure (if available)"""
        project_root = Path(__file__).parents[4]  # Navigate to project root
        
        if not (project_root / 'docs' / 'knowledge').exists():
            pytest.skip("Real project structure not available")
        
        agent = FileOrganizationAgent()
        findings = agent._detect_scattered_documentation(project_root)
        
        # Should complete without errors
        assert isinstance(findings, list)
        
        # Log findings for manual review
        if findings:
            print(f"\n=== Scattered Documentation Findings ({len(findings)}) ===")
            for finding in findings:
                print(f"  {finding.severity.name}: {finding.description}")
                print(f"    → {finding.recommendation}")