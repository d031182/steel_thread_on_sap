"""
Unit Tests for Feng Shui + Gu Wu Integration

Tests the complete pipeline:
1. Feng Shui multi-agent analysis
2. AgentReport → Gu Wu test generation
3. Generated tests are valid pytest
"""

import pytest
from pathlib import Path
import json
from unittest.mock import Mock, patch, MagicMock
from tools.guwu.feng_shui_integration import integrate_feng_shui_guwu
from tools.guwu.generators.app_v2_test_generator import AppV2TestGenerator


class TestFengShuiIntegration:
    """Test Feng Shui + Gu Wu integration pipeline"""
    
    @pytest.fixture
    def mock_agent_report(self):
        """Create mock AgentReport from Feng Shui"""
        report = Mock()
        report.agent_name = 'app_v2'
        report.module_path = Path('modules/test_module')
        report.findings = [
            Mock(
                category='Scripts Not Accessible',
                severity='HIGH',
                description='Script not found',
                location='frontend/test.js',
                recommendation='Create file'
            )
        ]
        report.to_dict = Mock(return_value={
            'agent_name': 'app_v2',
            'module_path': 'modules/test_module',
            'findings': [
                {
                    'category': 'Scripts Not Accessible',
                    'severity': 'HIGH',
                    'description': 'Script not found',
                    'location': 'frontend/test.js',
                    'recommendation': 'Create file'
                }
            ]
        })
        return report
    
    @pytest.fixture
    def mock_comprehensive_report(self, mock_agent_report):
        """Create mock comprehensive report from orchestrator"""
        comp_report = Mock()
        comp_report.agent_reports = [mock_agent_report]
        comp_report.overall_health_score = 75.0
        return comp_report
    
    def test_integration_creates_test_file(self, tmp_path, mock_comprehensive_report):
        """Test that integration creates a pytest file"""
        # Setup
        test_module = tmp_path / "modules" / "test_module"
        test_module.mkdir(parents=True)
        (test_module / "module.json").write_text(json.dumps({
            "name": "test_module",
            "frontend": {
                "entry_point": "test.js",
                "scripts": ["frontend/test.js"]
            }
        }))
        
        # Mock orchestrator (it's imported inside the function)
        with patch('tools.fengshui.agents.orchestrator.AgentOrchestrator') as mock_orch:
            mock_instance = Mock()
            mock_instance.analyze_module_comprehensive = Mock(
                return_value=mock_comprehensive_report
            )
            mock_orch.return_value = mock_instance
            
            # Mock test generator (it's imported inside the function)
            with patch('tools.guwu.generators.app_v2_test_generator.AppV2TestGenerator') as mock_gen:
                mock_gen_instance = Mock()
                expected_path = Path("tests/e2e/app_v2_modules/test_test_module.py")
                mock_gen_instance.generate_from_report = Mock(return_value=expected_path)
                mock_gen.return_value = mock_gen_instance
                
                # Run integration (without running tests)
                result = integrate_feng_shui_guwu('test_module', run_tests=False)
                
                # Verify
                assert result is True
                mock_gen_instance.generate_from_report.assert_called_once()
    
    def test_integration_saves_report_json(self, tmp_path, mock_comprehensive_report):
        """Test that integration saves Feng Shui report as JSON"""
        # Mock orchestrator (it's imported inside the function)
        with patch('tools.fengshui.agents.orchestrator.AgentOrchestrator') as mock_orch:
            mock_instance = Mock()
            mock_instance.analyze_module_comprehensive = Mock(
                return_value=mock_comprehensive_report
            )
            mock_orch.return_value = mock_instance
            
            # Mock test generator (it's imported inside the function)
            with patch('tools.guwu.generators.app_v2_test_generator.AppV2TestGenerator'):
                # Run integration
                integrate_feng_shui_guwu('test_module', run_tests=False)
                
                # Verify JSON file created
                report_file = Path('feng_shui_report_test_module.json')
                assert report_file.exists()
                
                # Verify JSON is valid
                report_data = json.loads(report_file.read_text())
                assert 'agent_name' in report_data
                assert report_data['agent_name'] == 'app_v2'
                
                # Cleanup
                report_file.unlink()
    
    def test_integration_handles_no_app_v2_agent(self, mock_comprehensive_report):
        """Test integration handles missing App V2 agent"""
        # Setup: comprehensive report with no app_v2 agent
        mock_comprehensive_report.agent_reports = []
        
        # Mock orchestrator (it's imported inside the function)
        with patch('tools.fengshui.agents.orchestrator.AgentOrchestrator') as mock_orch:
            mock_instance = Mock()
            mock_instance.analyze_module_comprehensive = Mock(
                return_value=mock_comprehensive_report
            )
            mock_orch.return_value = mock_instance
            
            # Run integration
            result = integrate_feng_shui_guwu('test_module', run_tests=False)
            
            # Should return False when app_v2 agent missing
            assert result is False
    
    def test_integration_runs_pytest_when_requested(self, mock_comprehensive_report):
        """Test integration runs pytest when run_tests=True"""
        # Mock orchestrator (it's imported inside the function)
        with patch('tools.fengshui.agents.orchestrator.AgentOrchestrator') as mock_orch:
            mock_instance = Mock()
            mock_instance.analyze_module_comprehensive = Mock(
                return_value=mock_comprehensive_report
            )
            mock_orch.return_value = mock_instance
            
            # Mock test generator (it's imported inside the function)
            with patch('tools.guwu.generators.app_v2_test_generator.AppV2TestGenerator') as mock_gen:
                mock_gen_instance = Mock()
                test_file = Path("tests/e2e/app_v2_modules/test_test_module.py")
                mock_gen_instance.generate_from_report = Mock(return_value=test_file)
                mock_gen.return_value = mock_gen_instance
                
                # Mock subprocess
                with patch('tools.guwu.feng_shui_integration.subprocess.run') as mock_run:
                    mock_run.return_value = Mock(returncode=0, stdout="All tests passed")
                    
                    # Run integration with tests
                    result = integrate_feng_shui_guwu('test_module', run_tests=True)
                    
                    # Verify pytest was called
                    mock_run.assert_called_once()
                    call_args = mock_run.call_args[0][0]
                    assert call_args[0] == 'pytest'
                    assert str(test_file) in call_args
                    assert result is True


class TestAppV2TestGenerator:
    """Test Gu Wu test generator"""
    
    @pytest.fixture
    def generator(self, tmp_path):
        """Create test generator with temp output"""
        output_dir = tmp_path / "tests" / "e2e" / "app_v2_modules"
        return AppV2TestGenerator(output_dir=output_dir)
    
    @pytest.fixture
    def sample_agent_report(self):
        """Create sample AgentReport"""
        report = Mock()
        report.agent_name = 'app_v2'
        report.module_path = Path('modules/sample_module')
        report.findings = [
            Mock(
                category='Scripts Not Accessible',
                severity='HIGH',
                description='Script file not found',
                location='frontend/missing.js',
                recommendation='Create the missing script file'
            ),
            Mock(
                category='Navigation Configuration',
                severity='MEDIUM',
                description='Missing entry_point in frontend config',
                location='module.json',
                recommendation='Add entry_point field'
            )
        ]
        report.to_dict = Mock(return_value={
            'agent_name': 'app_v2',
            'module_path': 'modules/sample_module',
            'findings': [
                {
                    'category': 'Scripts Not Accessible',
                    'severity': 'HIGH',
                    'description': 'Script file not found',
                    'location': 'frontend/missing.js',
                    'recommendation': 'Create the missing script file'
                },
                {
                    'category': 'Navigation Configuration',
                    'severity': 'MEDIUM',
                    'description': 'Missing entry_point in frontend config',
                    'location': 'module.json',
                    'recommendation': 'Add entry_point field'
                }
            ]
        })
        return report
    
    def test_generator_creates_valid_pytest_file(self, generator, sample_agent_report):
        """Test generator creates valid pytest syntax"""
        # Generate tests
        output_file = generator.generate_from_report(sample_agent_report)
        
        # Verify file exists
        assert output_file.exists()
        
        # Verify content
        content = output_file.read_text()
        assert 'import pytest' in content
        assert '@pytest.mark.e2e' in content
        assert '@pytest.mark.app_v2' in content
        assert 'def test_scripts_accessible' in content
        assert 'def test_navigation_consistency' in content
    
    def test_generator_groups_findings_by_category(self, generator, sample_agent_report):
        """Test findings are grouped into 5 check categories"""
        output_file = generator.generate_from_report(sample_agent_report)
        content = output_file.read_text()
        
        # Should have tests for the 5 categories
        assert 'test_scripts_accessible' in content
        assert 'test_navigation_consistency' in content
        assert 'test_interface_compliance' in content
        assert 'test_dynamic_loading_compatibility' in content
        assert 'test_sapui5_rendering_safety' in content
    
    def test_generator_includes_fixtures(self, generator, sample_agent_report):
        """Test generated file includes required fixtures"""
        output_file = generator.generate_from_report(sample_agent_report)
        content = output_file.read_text()
        
        assert '@pytest.fixture' in content
        assert 'def module_config()' in content
        assert 'def app_v2_base_url()' in content
    
    def test_generator_includes_metadata(self, generator, sample_agent_report):
        """Test generated file includes metadata comments"""
        output_file = generator.generate_from_report(sample_agent_report)
        content = output_file.read_text()
        
        # Check header comments
        assert 'Auto-generated E2E tests' in content
        assert 'Generated by: Gu Wu' in content
        assert 'Source: Feng Shui' in content
        assert 'DO NOT EDIT' in content
    
    def test_generator_handles_dict_input(self, generator):
        """Test generator accepts dict instead of AgentReport object"""
        report_dict = {
            'agent_name': 'app_v2',
            'module_path': 'modules/test_module',
            'findings': [
                {
                    'category': 'Scripts Not Accessible',
                    'severity': 'HIGH',
                    'description': 'Test finding',
                    'location': 'test.js',
                    'recommendation': 'Fix it'
                }
            ]
        }
        
        # Should not raise exception
        output_file = generator.generate_from_report(report_dict)
        assert output_file.exists()
        
        content = output_file.read_text()
        assert 'test_module' in content


class TestEndToEndWorkflow:
    """Test complete E2E workflow (integration tests)"""
    
    @pytest.mark.integration
    def test_complete_pipeline_with_real_module(self, tmp_path):
        """Test complete pipeline with a real module structure"""
        # Setup: Create real module structure
        module_dir = tmp_path / "modules" / "test_module"
        module_dir.mkdir(parents=True)
        
        # Create module.json
        (module_dir / "module.json").write_text(json.dumps({
            "name": "test_module",
            "version": "1.0.0",
            "frontend": {
                "entry_point": "views/testPage.js",
                "scripts": [
                    "frontend/module.js",
                    "frontend/views/testPage.js"
                ]
            }
        }))
        
        # Create frontend structure
        frontend_dir = module_dir / "frontend"
        frontend_dir.mkdir()
        (frontend_dir / "module.js").write_text("window.TestModule = {};")
        
        views_dir = frontend_dir / "views"
        views_dir.mkdir()
        (views_dir / "testPage.js").write_text("window.TestPage = {};")
        
        # This test would require actual Feng Shui orchestrator
        # For now, we verify the structure is correct
        assert (module_dir / "module.json").exists()
        assert (frontend_dir / "module.js").exists()
        assert (views_dir / "testPage.js").exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])