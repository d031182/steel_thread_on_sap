"""
Smoke Tests for Core Modules
=============================
Basic sanity checks to verify modules import and function.

Following Gu Wu standards:
- AAA pattern (Arrange, Act, Assert)
- pytest markers
- Descriptive docstrings
"""

import pytest


class TestModuleImports:
    """Verify all backend modules can be imported"""
    
    @pytest.mark.unit
    def test_import_ai_assistant(self):
        """Test: AI Assistant module imports successfully"""
        # ACT/ASSERT (import is the test)
        from modules.ai_assistant.backend import api
        assert api is not None
    
    @pytest.mark.unit
    def test_import_data_products_v2(self):
        """Test: Data Products V2 module imports successfully"""
        # ACT/ASSERT
        from modules.data_products_v2.backend import api
        assert api is not None
    
    @pytest.mark.unit
    def test_import_knowledge_graph_v2(self):
        """Test: Knowledge Graph V2 module imports successfully"""
        # ACT/ASSERT
        from modules.knowledge_graph_v2.backend import api
        assert api is not None
    
    @pytest.mark.unit
    def test_import_logger(self):
        """Test: Logger module imports successfully"""
        # ACT/ASSERT
        from modules.logger.backend import api
        assert api is not None


class TestCoreServices:
    """Verify core services can be instantiated"""
    
    @pytest.mark.unit
    def test_module_loader_exists(self):
        """Test: ModuleLoader service exists"""
        # ACT/ASSERT
        from core.services.module_loader import ModuleLoader
        assert ModuleLoader is not None
    
    @pytest.mark.unit
    def test_frontend_module_registry_exists(self):
        """Test: FrontendModuleRegistry service exists"""
        # ACT/ASSERT
        from core.services.frontend_module_registry import FrontendModuleRegistry
        assert FrontendModuleRegistry is not None


class TestToolsAvailable:
    """Verify quality tools are available"""
    
    @pytest.mark.unit
    def test_feng_shui_available(self):
        """Test: Feng Shui tool is available"""
        # ACT
        from pathlib import Path
        feng_shui_path = Path("tools/fengshui/__main__.py")
        
        # ASSERT
        assert feng_shui_path.exists()
    
    @pytest.mark.unit
    def test_gu_wu_available(self):
        """Test: Gu Wu tool is available"""
        # ACT
        from pathlib import Path
        gu_wu_path = Path("tools/guwu/__main__.py")
        
        # ASSERT
        assert gu_wu_path.exists()
    
    @pytest.mark.unit
    def test_shi_fu_available(self):
        """Test: Shi Fu tool is available"""
        # ACT
        from pathlib import Path
        shi_fu_path = Path("tools/shifu/shifu.py")
        
        # ASSERT
        assert shi_fu_path.exists()