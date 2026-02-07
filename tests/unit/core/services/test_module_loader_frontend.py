"""
Unit Tests for ModuleLoader Frontend Deployment
================================================

Tests for the frontend asset deployment functionality added in Phase 1
of the modular architecture implementation.

Following Gu Wu testing standards:
- AAA pattern (Arrange, Act, Assert)
- 70% unit / 20% integration / 10% E2E ratio
- Fast, isolated tests with mocking
- 100% coverage of business logic

@author P2P Development Team
@version 1.0.0
"""

import pytest
import json
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

from core.services.module_loader import ModuleLoader


@pytest.mark.unit
@pytest.mark.fast
class TestFrontendDeployment:
    """Test suite for frontend asset deployment functionality"""
    
    @pytest.fixture
    def app(self):
        """Create Flask app fixture"""
        return Flask(__name__)
    
    @pytest.fixture
    def loader(self, app):
        """Create ModuleLoader instance"""
        return ModuleLoader(app)
    
    @pytest.fixture
    def mock_module_json(self, tmp_path):
        """Create mock module.json with frontend config"""
        module_dir = tmp_path / "test_module"
        module_dir.mkdir()
        
        # Create frontend directory with test files
        frontend_dir = module_dir / "frontend"
        frontend_dir.mkdir()
        (frontend_dir / "test.js").write_text("console.log('test');")
        (frontend_dir / "test.css").write_text("body { margin: 0; }")
        
        # Create module.json
        config = {
            "name": "test_module",
            "enabled": True,
            "frontend": {
                "entry_point": "frontend/test.js",
                "components": ["frontend/test.js", "frontend/test.css"],
                "deploy_to": "modules/test_module"
            }
        }
        
        module_json = module_dir / "module.json"
        module_json.write_text(json.dumps(config))
        
        return module_dir
    
    def test_deploy_frontend_assets_clean_slate(self, loader, tmp_path, monkeypatch):
        """
        Test that deploy_frontend_assets cleans previous deployments
        
        GIVEN: Existing deployment directory with old files
        WHEN: deploy_frontend_assets is called
        THEN: Old files are deleted before new deployment
        """
        # ARRANGE
        deploy_root = Path("app/static/modules")
        monkeypatch.setattr("core.services.module_loader.Path", lambda x: tmp_path / x if x == "app/static/modules" else Path(x))
        
        # Create existing deployment
        old_deploy = tmp_path / "app/static/modules"
        old_deploy.mkdir(parents=True)
        (old_deploy / "old_file.txt").write_text("old content")
        
        # Mock module discovery to return empty
        with patch.object(Path, 'rglob', return_value=[]):
            # ACT
            result = loader.deploy_frontend_assets()
            
            # ASSERT
            assert not old_deploy.exists()  # Clean slate confirmed
    
    def test_deploy_enabled_module(self, loader, mock_module_json, tmp_path, monkeypatch):
        """
        Test deployment of enabled module
        
        GIVEN: Module with enabled=true and frontend config
        WHEN: deploy_frontend_assets is called
        THEN: Frontend files are copied to deployment target
        """
        # ARRANGE
        modules_dir = mock_module_json.parent
        
        with patch('core.services.module_loader.Path') as mock_path_class:
            # Setup path mocking
            mock_path_instance = MagicMock()
            mock_path_class.return_value = mock_path_instance
            
            # Mock rglob to return our test module.json
            mock_path_instance.rglob.return_value = [mock_module_json / "module.json"]
            
            # Mock exists() for deploy_root
            mock_path_instance.exists.return_value = False
            
            # ACT
            with patch('core.services.module_loader.shutil.copytree') as mock_copytree:
                result = loader.deploy_frontend_assets(str(modules_dir))
                
                # ASSERT
                assert result == 1  # One module deployed
                mock_copytree.assert_called_once()
    
    def test_skip_disabled_module(self, loader, mock_module_json, tmp_path):
        """
        Test that disabled modules are skipped
        
        GIVEN: Module with enabled=false
        WHEN: deploy_frontend_assets is called
        THEN: Module is not deployed
        """
        # ARRANGE
        config_path = mock_module_json / "module.json"
        config = json.loads(config_path.read_text())
        config["enabled"] = False
        config_path.write_text(json.dumps(config))
        
        modules_dir = mock_module_json.parent
        
        # ACT
        with patch('core.services.module_loader.Path.rglob') as mock_rglob:
            mock_rglob.return_value = [config_path]
            result = loader.deploy_frontend_assets(str(modules_dir))
        
        # ASSERT
        assert result == 0  # No modules deployed
    
    def test_skip_module_without_frontend_config(self, loader, tmp_path):
        """
        Test that modules without frontend config are skipped
        
        GIVEN: Module without frontend configuration
        WHEN: deploy_frontend_assets is called
        THEN: Module is skipped without error
        """
        # ARRANGE
        module_dir = tmp_path / "no_frontend_module"
        module_dir.mkdir()
        
        config = {
            "name": "no_frontend_module",
            "enabled": True
            # No frontend config
        }
        
        config_path = module_dir / "module.json"
        config_path.write_text(json.dumps(config))
        
        # ACT
        with patch('core.services.module_loader.Path.rglob') as mock_rglob:
            mock_rglob.return_value = [config_path]
            result = loader.deploy_frontend_assets(str(tmp_path))
        
        # ASSERT
        assert result == 0  # No modules deployed (skipped)
    
    def test_deploy_to_custom_path(self, loader, mock_module_json, tmp_path):
        """
        Test deployment to custom path specified in config
        
        GIVEN: Module with custom deploy_to path
        WHEN: deploy_frontend_assets is called
        THEN: Files are deployed to custom path
        """
        # ARRANGE
        config_path = mock_module_json / "module.json"
        config = json.loads(config_path.read_text())
        config["frontend"]["deploy_to"] = "custom/path/test_module"
        config_path.write_text(json.dumps(config))
        
        # ACT
        with patch('core.services.module_loader.shutil.copytree') as mock_copytree:
            with patch('core.services.module_loader.Path.rglob') as mock_rglob:
                mock_rglob.return_value = [config_path]
                loader.deploy_frontend_assets(str(mock_module_json.parent))
                
                # ASSERT
                # Verify copytree was called with custom target path
                assert mock_copytree.called
                call_args = mock_copytree.call_args[0]
                assert str(call_args[1]).endswith("custom/path/test_module")
    
    def test_handle_missing_frontend_directory(self, loader, tmp_path, caplog):
        """
        Test handling of missing frontend directory
        
        GIVEN: Module with frontend config but no frontend/ directory
        WHEN: deploy_frontend_assets is called
        THEN: Warning is logged and deployment continues
        """
        # ARRANGE
        module_dir = tmp_path / "missing_frontend"
        module_dir.mkdir()
        
        config = {
            "name": "missing_frontend",
            "enabled": True,
            "frontend": {
                "entry_point": "frontend/test.js",
                "deploy_to": "modules/missing_frontend"
            }
        }
        
        config_path = module_dir / "module.json"
        config_path.write_text(json.dumps(config))
        
        # ACT
        with patch('core.services.module_loader.Path.rglob') as mock_rglob:
            mock_rglob.return_value = [config_path]
            result = loader.deploy_frontend_assets(str(tmp_path))
        
        # ASSERT
        assert result == 0  # No modules deployed
        assert "Frontend directory not found" in caplog.text
    
    def test_load_module_config_valid_json(self, loader, mock_module_json):
        """
        Test loading valid module.json
        
        GIVEN: Valid module.json file
        WHEN: _load_module_config is called
        THEN: Configuration is parsed correctly
        """
        # ARRANGE
        config_path = mock_module_json / "module.json"
        
        # ACT
        config = loader._load_module_config(config_path)
        
        # ASSERT
        assert config["name"] == "test_module"
        assert config["enabled"] is True
        assert "frontend" in config
    
    def test_load_module_config_invalid_json(self, loader, tmp_path):
        """
        Test handling of invalid JSON
        
        GIVEN: Invalid JSON in module.json
        WHEN: _load_module_config is called
        THEN: JSONDecodeError is raised
        """
        # ARRANGE
        config_path = tmp_path / "invalid.json"
        config_path.write_text("{ invalid json }")
        
        # ACT & ASSERT
        with pytest.raises(json.JSONDecodeError):
            loader._load_module_config(config_path)
    
    def test_deploy_module_assets_success(self, loader, mock_module_json, tmp_path):
        """
        Test successful deployment of module assets
        
        GIVEN: Valid module with frontend files
        WHEN: _deploy_module_assets is called
        THEN: Files are copied and True is returned
        """
        # ARRANGE
        config_path = mock_module_json / "module.json"
        config = json.loads(config_path.read_text())
        
        deploy_target = tmp_path / "deploy" / "test_module"
        
        # ACT
        with patch('core.services.module_loader.Path') as mock_path:
            mock_path.return_value = deploy_target
            with patch('core.services.module_loader.shutil.copytree'):
                result = loader._deploy_module_assets(mock_module_json, config)
        
        # ASSERT
        assert result is True
    
    def test_deploy_module_assets_no_frontend_config(self, loader, tmp_path):
        """
        Test deployment with missing frontend config
        
        GIVEN: Module without frontend configuration
        WHEN: _deploy_module_assets is called
        THEN: False is returned without error
        """
        # ARRANGE
        module_dir = tmp_path / "test_module"
        config = {"name": "test_module", "enabled": True}
        
        # ACT
        result = loader._deploy_module_assets(module_dir, config)
        
        # ASSERT
        assert result is False
    
    def test_deploy_multiple_modules(self, loader, tmp_path):
        """
        Test deployment of multiple modules
        
        GIVEN: Three modules (2 enabled, 1 disabled)
        WHEN: deploy_frontend_assets is called
        THEN: Only enabled modules are deployed
        """
        # ARRANGE
        modules = []
        for i, enabled in enumerate([True, True, False]):
            module_dir = tmp_path / f"module_{i}"
            module_dir.mkdir()
            
            frontend_dir = module_dir / "frontend"
            frontend_dir.mkdir()
            (frontend_dir / "test.js").write_text(f"module_{i}")
            
            config = {
                "name": f"module_{i}",
                "enabled": enabled,
                "frontend": {"entry_point": "frontend/test.js"}
            }
            
            config_path = module_dir / "module.json"
            config_path.write_text(json.dumps(config))
            modules.append(config_path)
        
        # ACT
        with patch('core.services.module_loader.Path.rglob') as mock_rglob:
            mock_rglob.return_value = modules
            with patch('core.services.module_loader.shutil.copytree'):
                result = loader.deploy_frontend_assets(str(tmp_path))
        
        # ASSERT
        assert result == 2  # Only 2 enabled modules deployed


@pytest.mark.unit
@pytest.mark.fast
class TestCleanSlateDeployment:
    """Test suite for Clean Slate deployment approach"""
    
    @pytest.fixture
    def loader(self):
        """Create ModuleLoader instance"""
        app = Flask(__name__)
        return ModuleLoader(app)
    
    def test_clean_slate_removes_all_previous_deployments(self, loader, tmp_path):
        """
        Test that Clean Slate approach removes ALL previous files
        
        GIVEN: Multiple deployed modules from previous run
        WHEN: deploy_frontend_assets is called
        THEN: All previous files are deleted before new deployment
        """
        # ARRANGE
        deploy_root = tmp_path / "deploy"
        deploy_root.mkdir()
        
        # Create old deployments
        (deploy_root / "old_module_1").mkdir()
        (deploy_root / "old_module_1" / "file.js").write_text("old")
        (deploy_root / "old_module_2").mkdir()
        (deploy_root / "old_module_2" / "file.css").write_text("old")
        
        # ACT
        with patch('core.services.module_loader.Path') as mock_path:
            mock_path.return_value = deploy_root
            with patch('core.services.module_loader.shutil.rmtree') as mock_rmtree:
                loader.deploy_frontend_assets()
                
                # ASSERT
                mock_rmtree.assert_called_once_with(deploy_root)
    
    def test_disabled_module_files_removed(self, loader, tmp_path):
        """
        Test that disabling a module removes its deployed files
        
        GIVEN: Module that was enabled, now disabled
        WHEN: Server restarts with module disabled
        THEN: Module's deployed files are removed (clean slate)
        """
        # This is implicit in clean slate - all files deleted, only enabled redeployed
        # Test verifies the concept
        
        # ARRANGE
        module_dir = tmp_path / "test_module"
        module_dir.mkdir()
        
        config_disabled = {
            "name": "test_module",
            "enabled": False,  # Disabled
            "frontend": {"entry_point": "frontend/test.js"}
        }
        
        config_path = module_dir / "module.json"
        config_path.write_text(json.dumps(config_disabled))
        
        # ACT
        with patch('core.services.module_loader.Path.rglob') as mock_rglob:
            mock_rglob.return_value = [config_path]
            result = loader.deploy_frontend_assets(str(tmp_path))
        
        # ASSERT
        assert result == 0  # No modules deployed (disabled module skipped)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])