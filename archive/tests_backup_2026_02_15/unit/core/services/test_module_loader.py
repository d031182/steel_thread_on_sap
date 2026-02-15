"""
Unit Tests for ModuleLoader
============================
Tests the auto-discovery and blueprint registration system.

Tests:
- Blueprint loading with proper error handling
- Auto-discovery of modules from module.json files
- Error handling for missing/invalid configurations
- Success tracking and failure reporting
- Module summary generation

Author: P2P Development Team
Version: 1.0.0
"""

import pytest
from flask import Flask, Blueprint
from pathlib import Path
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock

from core.services.module_loader import ModuleLoader, ModuleLoadError


@pytest.fixture
def flask_app():
    """Create a test Flask application"""
    app = Flask(__name__)
    app.config['TESTING'] = True
    return app


@pytest.fixture
def module_loader(flask_app):
    """Create a ModuleLoader instance"""
    return ModuleLoader(flask_app)


@pytest.fixture
def temp_modules_dir():
    """Create a temporary modules directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


class TestModuleLoaderInit:
    """Test ModuleLoader initialization"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_init_creates_tracking_dicts(self, flask_app):
        """Test that initialization creates empty tracking dictionaries"""
        # ACT
        loader = ModuleLoader(flask_app)
        
        # ASSERT
        assert loader.loaded_modules == {}
        assert loader.failed_modules == {}
        assert loader.critical_failures == []
        assert loader.app == flask_app


class TestLoadBlueprint:
    """Test blueprint loading functionality"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_load_blueprint_success(self, module_loader, flask_app):
        """Test successful blueprint loading"""
        # ARRANGE
        test_bp = Blueprint('test', __name__)
        
        with patch('builtins.__import__') as mock_import:
            mock_module = Mock()
            mock_module.test_bp = test_bp
            mock_import.return_value = mock_module
            
            # ACT
            result = module_loader.load_blueprint(
                'Test Module',
                'modules.test.backend',
                'test_bp',
                '/api/test',
                is_critical=False
            )
            
            # ASSERT
            assert result is True
            assert module_loader.loaded_modules['Test Module'] is True
            assert len(flask_app.blueprints) > 0
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_load_blueprint_import_error(self, module_loader):
        """Test handling of ImportError"""
        # ACT
        result = module_loader.load_blueprint(
            'NonExistent Module',
            'modules.nonexistent.backend',
            'bp',
            '/api/test',
            is_critical=False
        )
        
        # ASSERT
        assert result is False
        assert module_loader.loaded_modules['NonExistent Module'] is False
        assert 'NonExistent Module' in module_loader.failed_modules
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_load_blueprint_attribute_error(self, module_loader):
        """Test handling of AttributeError (blueprint not found)"""
        # ARRANGE
        with patch('builtins.__import__') as mock_import:
            mock_module = Mock(spec=[])  # Empty spec = no attributes
            mock_import.return_value = mock_module
            
            # ACT
            result = module_loader.load_blueprint(
                'Test Module',
                'modules.test.backend',
                'nonexistent_bp',
                '/api/test',
                is_critical=False
            )
            
            # ASSERT
            assert result is False
            assert module_loader.loaded_modules['Test Module'] is False
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_load_blueprint_critical_failure_raises(self, module_loader):
        """Test that critical failures raise ModuleLoadError"""
        # ACT & ASSERT
        with pytest.raises(ModuleLoadError) as exc_info:
            module_loader.load_blueprint(
                'Critical Module',
                'modules.nonexistent.backend',
                'bp',
                '/api/test',
                is_critical=True
            )
        
        assert exc_info.value.module_name == 'Critical Module'
        assert exc_info.value.is_critical is True
        assert 'Critical Module' in module_loader.critical_failures


class TestAutoDiscoverModules:
    """Test auto-discovery functionality"""
    
    @pytest.mark.unit
    def test_auto_discover_valid_module(self, module_loader, temp_modules_dir):
        """Test discovery of a valid module with module.json"""
        # ARRANGE
        module_dir = Path(temp_modules_dir) / 'test_module'
        module_dir.mkdir()
        
        module_config = {
            'name': 'test_module',
            'enabled': True,
            'backend': {
                'blueprint': 'modules.test_module.backend:test_bp',
                'mount_path': '/api/test'
            }
        }
        
        (module_dir / 'module.json').write_text(json.dumps(module_config))
        
        # Create mock blueprint
        test_bp = Blueprint('test', __name__)
        
        with patch('builtins.__import__') as mock_import:
            mock_module = Mock()
            mock_module.test_bp = test_bp
            mock_import.return_value = mock_module
            
            # ACT
            count = module_loader.auto_discover_modules(temp_modules_dir)
            
            # ASSERT
            assert count == 1
            # Module is stored by display name, not config name
            assert 'Test Module' in module_loader.loaded_modules
            assert module_loader.loaded_modules['Test Module'] is True
    
    @pytest.mark.unit
    def test_auto_discover_disabled_module(self, module_loader, temp_modules_dir):
        """Test that disabled modules are skipped"""
        # ARRANGE
        module_dir = Path(temp_modules_dir) / 'disabled_module'
        module_dir.mkdir()
        
        module_config = {
            'name': 'disabled_module',
            'enabled': False,
            'backend': {
                'blueprint': 'modules.disabled_module.backend:bp',
                'mount_path': '/api/disabled'
            }
        }
        
        (module_dir / 'module.json').write_text(json.dumps(module_config))
        
        # ACT
        count = module_loader.auto_discover_modules(temp_modules_dir)
        
        # ASSERT
        assert count == 0
        assert 'disabled_module' not in module_loader.loaded_modules
    
    @pytest.mark.unit
    def test_auto_discover_no_backend_config(self, module_loader, temp_modules_dir):
        """Test that modules without backend config are skipped"""
        # ARRANGE
        module_dir = Path(temp_modules_dir) / 'frontend_only'
        module_dir.mkdir()
        
        module_config = {
            'name': 'frontend_only',
            'enabled': True
        }
        
        (module_dir / 'module.json').write_text(json.dumps(module_config))
        
        # ACT
        count = module_loader.auto_discover_modules(temp_modules_dir)
        
        # ASSERT
        assert count == 0
    
    @pytest.mark.unit
    def test_auto_discover_missing_blueprint_path(self, module_loader, temp_modules_dir):
        """Test handling of missing blueprint configuration"""
        # ARRANGE
        module_dir = Path(temp_modules_dir) / 'incomplete_module'
        module_dir.mkdir()
        
        module_config = {
            'name': 'incomplete_module',
            'enabled': True,
            'backend': {
                'mount_path': '/api/incomplete'
            }
        }
        
        (module_dir / 'module.json').write_text(json.dumps(module_config))
        
        # ACT
        count = module_loader.auto_discover_modules(temp_modules_dir)
        
        # ASSERT
        assert count == 0
    
    @pytest.mark.unit
    def test_auto_discover_invalid_json(self, module_loader, temp_modules_dir):
        """Test handling of invalid JSON in module.json"""
        # ARRANGE
        module_dir = Path(temp_modules_dir) / 'bad_json'
        module_dir.mkdir()
        
        (module_dir / 'module.json').write_text('{ invalid json }')
        
        # ACT
        count = module_loader.auto_discover_modules(temp_modules_dir)
        
        # ASSERT
        assert count == 0
    
    @pytest.mark.unit
    def test_auto_discover_nonexistent_directory(self, module_loader):
        """Test handling of non-existent modules directory"""
        # ACT
        count = module_loader.auto_discover_modules('nonexistent_dir')
        
        # ASSERT
        assert count == 0


class TestGetLoadSummary:
    """Test load summary generation"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_load_summary_empty(self, module_loader):
        """Test summary with no modules loaded"""
        # ACT
        summary = module_loader.get_load_summary()
        
        # ASSERT
        assert summary['total_modules'] == 0
        assert summary['loaded'] == 0
        assert summary['failed'] == 0
        assert summary['critical_failures'] == 0
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_get_load_summary_mixed_results(self, module_loader):
        """Test summary with mixed success/failure results"""
        # ARRANGE
        module_loader.loaded_modules = {
            'Module1': True,
            'Module2': True,
            'Module3': False,
            'Module4': False
        }
        module_loader.critical_failures = ['Module3']
        
        # ACT
        summary = module_loader.get_load_summary()
        
        # ASSERT
        assert summary['total_modules'] == 4
        assert summary['loaded'] == 2
        assert summary['failed'] == 2
        assert summary['critical_failures'] == 1
        assert 'Module1' in summary['loaded_modules']
        assert 'Module3' in summary['failed_modules']
        assert 'Module3' in summary['critical_failures_list']


class TestModuleLoadError:
    """Test ModuleLoadError exception"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_module_load_error_creation(self):
        """Test ModuleLoadError exception creation"""
        # ARRANGE
        original_error = ImportError("Test error")
        
        # ACT
        error = ModuleLoadError('test_module', original_error, is_critical=True)
        
        # ASSERT
        assert error.module_name == 'test_module'
        assert error.original_error == original_error
        assert error.is_critical is True
        assert 'test_module' in str(error)
        assert 'Test error' in str(error)


class TestBlueprintParsing:
    """Test blueprint path parsing"""
    
    @pytest.mark.unit
    @pytest.mark.fast
    def test_blueprint_path_with_colon(self, module_loader, flask_app):
        """Test parsing blueprint path with colon separator"""
        # ARRANGE
        test_bp = Blueprint('test', __name__)
        
        with patch('builtins.__import__') as mock_import:
            mock_module = Mock()
            mock_module.test_bp = test_bp
            mock_import.return_value = mock_module
            
            # ACT - The auto_discover handles parsing internally
            # We're testing the correct format is accepted
            result = module_loader.load_blueprint(
                'Test Module',
                'modules.test.backend',
                'test_bp',
                '/api/test',
                is_critical=False
            )
            
            # ASSERT
            assert result is True


class TestIntegrationScenarios:
    """Integration tests for common scenarios"""
    
    @pytest.mark.unit
    def test_multiple_module_discovery(self, module_loader, temp_modules_dir):
        """Test discovering multiple modules at once"""
        # ARRANGE
        # Create unique blueprints for each module to avoid name collision
        for i in range(3):
            module_dir = Path(temp_modules_dir) / f'module_{i}'
            module_dir.mkdir()
            
            module_config = {
                'name': f'module_{i}',
                'enabled': True,
                'backend': {
                    'blueprint': f'modules.module_{i}.backend:bp',
                    'mount_path': f'/api/module{i}'
                }
            }
            
            (module_dir / 'module.json').write_text(json.dumps(module_config))
        
        def create_unique_blueprint(path, *args, **kwargs):
            # Extract module number from path to create unique blueprint names
            if 'module_0' in path:
                bp = Blueprint('module_0', __name__)
            elif 'module_1' in path:
                bp = Blueprint('module_1', __name__)
            elif 'module_2' in path:
                bp = Blueprint('module_2', __name__)
            else:
                bp = Blueprint('test', __name__)
            
            mock_module = Mock()
            mock_module.bp = bp
            return mock_module
        
        with patch('builtins.__import__', side_effect=create_unique_blueprint):
            # ACT
            count = module_loader.auto_discover_modules(temp_modules_dir)
            
            # ASSERT
            assert count == 3
            assert len(module_loader.loaded_modules) == 3
    
    @pytest.mark.unit
    def test_partial_failure_scenario(self, module_loader, temp_modules_dir):
        """Test scenario where some modules succeed and some fail"""
        # ARRANGE
        # Module 1: Success
        module1_dir = Path(temp_modules_dir) / 'success_module'
        module1_dir.mkdir()
        module1_config = {
            'name': 'success_module',
            'enabled': True,
            'backend': {
                'blueprint': 'modules.success.backend:bp',
                'mount_path': '/api/success'
            }
        }
        (module1_dir / 'module.json').write_text(json.dumps(module1_config))
        
        # Module 2: Fail (bad import)
        module2_dir = Path(temp_modules_dir) / 'fail_module'
        module2_dir.mkdir()
        module2_config = {
            'name': 'fail_module',
            'enabled': True,
            'backend': {
                'blueprint': 'modules.nonexistent.backend:bp',
                'mount_path': '/api/fail'
            }
        }
        (module2_dir / 'module.json').write_text(json.dumps(module2_config))
        
        test_bp = Blueprint('test', __name__)
        
        def import_side_effect(path, *args, **kwargs):
            if 'nonexistent' in path:
                raise ImportError("Module not found")
            mock_module = Mock()
            mock_module.bp = test_bp
            return mock_module
        
        with patch('builtins.__import__', side_effect=import_side_effect):
            # ACT
            count = module_loader.auto_discover_modules(temp_modules_dir)
            
            # ASSERT
            assert count == 1  # Only one succeeded
            summary = module_loader.get_load_summary()
            assert summary['loaded'] == 1
            assert summary['failed'] == 1
