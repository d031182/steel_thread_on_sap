"""
Tests for Service Locator Anti-Pattern Detection in ArchitectAgent

Tests the _detect_service_locator_violations() method which detects:
1. Flask config access for database paths
2. db_path string parameters in constructors
3. db_path string parameters in factory methods
4. Missing IDatabasePathResolver imports
5. Global registry lookups

Based on: docs/knowledge/service-locator-antipattern-solution.md
"""

import pytest
from pathlib import Path
from tools.fengshui.agents.architect_agent import ArchitectAgent
from tools.fengshui.agents.base_agent import Severity


@pytest.fixture
def temp_module_dir(tmp_path):
    """Create temporary module directory structure"""
    module_path = tmp_path / "test_module"
    module_path.mkdir()
    
    backend_dir = module_path / "backend"
    backend_dir.mkdir()
    
    facade_dir = module_path / "facade"
    facade_dir.mkdir()
    
    repositories_dir = module_path / "repositories"
    repositories_dir.mkdir()
    
    return module_path


@pytest.fixture
def architect_agent():
    """Create ArchitectAgent instance"""
    return ArchitectAgent()


class TestFlaskConfigAccess:
    """Test detection of Flask config access for database paths"""
    
    def test_detects_current_app_config_sqlite_path(self, temp_module_dir, architect_agent):
        """Should detect current_app.config.get('SQLITE_DB_PATH')"""
        api_file = temp_module_dir / "backend" / "api.py"
        api_file.write_text("""
from flask import current_app

def get_facade():
    db_path = current_app.config.get('SQLITE_DB_PATH')
    return DataProductsFacade('sqlite', db_path=db_path)
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        assert len(findings) > 0
        flask_config_findings = [f for f in findings if 'Flask config access' in f.description]
        assert len(flask_config_findings) == 1
        assert flask_config_findings[0].severity == Severity.HIGH
        assert 'SQLITE_DB_PATH' in flask_config_findings[0].code_snippet
    
    def test_detects_app_config_database_path(self, temp_module_dir, architect_agent):
        """Should detect app.config['DATABASE_PATH']"""
        api_file = temp_module_dir / "backend" / "api.py"
        api_file.write_text("""
def init_db(app):
    db_path = app.config['DATABASE_PATH']
    return setup_database(db_path)
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        flask_config_findings = [f for f in findings if 'Flask config access' in f.description]
        assert len(flask_config_findings) == 1
        assert 'DATABASE_PATH' in flask_config_findings[0].code_snippet
    
    def test_detects_hana_config_access(self, temp_module_dir, architect_agent):
        """Should detect HANA_HOST, HANA_PORT config access"""
        api_file = temp_module_dir / "backend" / "api.py"
        api_file.write_text("""
from flask import current_app

def get_hana_connection():
    host = current_app.config.get('HANA_HOST')
    port = current_app.config.get('HANA_PORT')
    return connect_hana(host, port)
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        flask_config_findings = [f for f in findings if 'Flask config access' in f.description]
        assert len(flask_config_findings) >= 2  # One for HANA_HOST, one for HANA_PORT
    
    def test_ignores_non_database_config(self, temp_module_dir, architect_agent):
        """Should NOT detect non-database config access"""
        api_file = temp_module_dir / "backend" / "api.py"
        api_file.write_text("""
from flask import current_app

def get_settings():
    debug = current_app.config.get('DEBUG')
    secret = current_app.config.get('SECRET_KEY')
    return {'debug': debug}
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        flask_config_findings = [f for f in findings if 'Flask config access' in f.description]
        assert len(flask_config_findings) == 0


class TestDbPathConstructorParameter:
    """Test detection of db_path string parameters in constructors"""
    
    def test_detects_db_path_string_in_init(self, temp_module_dir, architect_agent):
        """Should detect __init__(self, db_path: str)"""
        repo_file = temp_module_dir / "repositories" / "sqlite_repository.py"
        repo_file.write_text("""
class SQLiteDataProductRepository:
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._service = SQLiteDataProductsService(db_path)
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        constructor_findings = [f for f in findings if 'Constructor accepts' in f.description]
        assert len(constructor_findings) == 1
        assert constructor_findings[0].severity == Severity.HIGH
        assert 'IDatabasePathResolver' in constructor_findings[0].recommendation
    
    def test_detects_db_path_without_type_hint(self, temp_module_dir, architect_agent):
        """Should detect __init__(self, db_path) without type hint"""
        facade_file = temp_module_dir / "facade" / "data_products_facade.py"
        facade_file.write_text("""
class DataProductsFacade:
    def __init__(self, source_type, db_path):
        self._repository = create_repository(source_type, db_path)
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        constructor_findings = [f for f in findings if 'Constructor accepts' in f.description]
        assert len(constructor_findings) == 1
    
    def test_ignores_interface_type_hint(self, temp_module_dir, architect_agent):
        """Should NOT detect path_resolver: IDatabasePathResolver"""
        repo_file = temp_module_dir / "repositories" / "sqlite_repository.py"
        repo_file.write_text("""
from core.interfaces.database_path_resolver import IDatabasePathResolver

class SQLiteDataProductRepository:
    def __init__(self, path_resolver: IDatabasePathResolver):
        db_path = path_resolver.resolve_path('data_products_v2')
        self._service = SQLiteDataProductsService(db_path)
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        constructor_findings = [f for f in findings if 'Constructor accepts' in f.description]
        assert len(constructor_findings) == 0


class TestDbPathFactoryParameter:
    """Test detection of db_path string parameters in factory methods"""
    
    def test_detects_db_path_in_create_method(self, temp_module_dir, architect_agent):
        """Should detect create(source_type, db_path: str)"""
        factory_file = temp_module_dir / "repositories" / "repository_factory.py"
        factory_file.write_text("""
class DataProductRepositoryFactory:
    @staticmethod
    def create(source_type: str, db_path: str):
        if source_type == 'sqlite':
            return SQLiteDataProductRepository(db_path)
        return HANADataProductRepository()
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        factory_findings = [f for f in findings if 'Factory method' in f.description]
        assert len(factory_findings) == 1
        assert factory_findings[0].severity == Severity.HIGH
        assert 'create' in factory_findings[0].description
    
    def test_detects_db_path_in_build_method(self, temp_module_dir, architect_agent):
        """Should detect build(db_path: str) factory method"""
        builder_file = temp_module_dir / "repositories" / "repository_builder.py"
        builder_file.write_text("""
class RepositoryBuilder:
    def build(self, db_path: str):
        return SQLiteRepository(db_path)
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        factory_findings = [f for f in findings if 'Factory method' in f.description]
        assert len(factory_findings) == 1
        assert 'build' in factory_findings[0].description


class TestMissingInterfaceImport:
    """Test detection of db_path usage without IDatabasePathResolver import"""
    
    def test_detects_missing_import_in_backend(self, temp_module_dir, architect_agent):
        """Should detect db_path usage in backend/ without interface import"""
        api_file = temp_module_dir / "backend" / "api.py"
        api_file.write_text("""
from flask import Blueprint

def get_facade():
    db_path = '/path/to/database.db'
    return DataProductsFacade('sqlite', db_path=db_path)
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        import_findings = [f for f in findings if "doesn't import IDatabasePathResolver" in f.description]
        assert len(import_findings) == 1
        assert import_findings[0].severity == Severity.MEDIUM
    
    def test_detects_missing_import_in_facade(self, temp_module_dir, architect_agent):
        """Should detect db_path usage in facade/ without interface import"""
        facade_file = temp_module_dir / "facade" / "data_products_facade.py"
        facade_file.write_text("""
class DataProductsFacade:
    def __init__(self, source_type, db_path):
        self.db_path = db_path
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        import_findings = [f for f in findings if "doesn't import IDatabasePathResolver" in f.description]
        assert len(import_findings) == 1
    
    def test_ignores_when_interface_imported(self, temp_module_dir, architect_agent):
        """Should NOT detect when IDatabasePathResolver is imported"""
        api_file = temp_module_dir / "backend" / "api.py"
        api_file.write_text("""
from core.interfaces.database_path_resolver import IDatabasePathResolver

def get_facade(path_resolver: IDatabasePathResolver):
    db_path = path_resolver.resolve_path('module_name')
    return DataProductsFacade('sqlite', db_path=db_path)
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        import_findings = [f for f in findings if "doesn't import IDatabasePathResolver" in f.description]
        assert len(import_findings) == 0


class TestGlobalRegistryLookups:
    """Test detection of Service Locator global registry patterns"""
    
    def test_detects_get_service_call(self, temp_module_dir, architect_agent):
        """Should detect get_service() calls"""
        service_file = temp_module_dir / "backend" / "service.py"
        service_file.write_text("""
def process_data():
    db_service = get_service('database')
    return db_service.query('SELECT * FROM data')
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        registry_findings = [f for f in findings if 'Global registry lookup' in f.description]
        assert len(registry_findings) == 1
        assert registry_findings[0].severity == Severity.MEDIUM
        assert 'get_service() call' in registry_findings[0].description
    
    def test_detects_service_registry_get(self, temp_module_dir, architect_agent):
        """Should detect ServiceRegistry.get() calls"""
        service_file = temp_module_dir / "backend" / "service.py"
        service_file.write_text("""
from app.services import ServiceRegistry

def get_database():
    return ServiceRegistry.get('database')
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        registry_findings = [f for f in findings if 'ServiceRegistry.get() call' in f.description]
        assert len(registry_findings) == 1
    
    def test_detects_services_dict_access(self, temp_module_dir, architect_agent):
        """Should detect app.services['...'] dictionary access"""
        api_file = temp_module_dir / "backend" / "api.py"
        api_file.write_text("""
from flask import current_app

def get_db():
    return current_app.services['database']
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        registry_findings = [f for f in findings if 'services dictionary access' in f.description]
        assert len(registry_findings) == 1
    
    def test_detects_service_locator_class(self, temp_module_dir, architect_agent):
        """Should detect ServiceLocator class usage (import and instantiation)"""
        locator_file = temp_module_dir / "backend" / "locator.py"
        locator_file.write_text("""
from utils.service_locator import ServiceLocator

class DatabaseService:
    def __init__(self):
        self.locator = ServiceLocator()
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        registry_findings = [f for f in findings if 'ServiceLocator usage' in f.description]
        # Should detect both import statement and instantiation
        assert len(registry_findings) >= 1
        assert any('import' in f.code_snippet.lower() or 'from' in f.code_snippet.lower() 
                   for f in registry_findings)


class TestComplexScenarios:
    """Test complex real-world scenarios"""
    
    def test_multiple_violations_in_same_file(self, temp_module_dir, architect_agent):
        """Should detect multiple Service Locator violations in one file"""
        api_file = temp_module_dir / "backend" / "api.py"
        api_file.write_text("""
from flask import Blueprint, current_app

data_products_api = Blueprint('data_products', __name__)

class DataProductsFacade:
    def __init__(self, source_type, db_path: str):
        self.db_path = db_path

@data_products_api.route('/products')
def get_products():
    db_path = current_app.config.get('SQLITE_DB_PATH')
    facade = DataProductsFacade('sqlite', db_path=db_path)
    return facade.get_all_products()
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        # Should find:
        # 1. Flask config access
        # 2. Constructor with db_path string
        # 3. Missing IDatabasePathResolver import
        assert len(findings) >= 3
        
        categories = [f.category for f in findings]
        assert 'Service Locator Anti-Pattern' in categories
    
    def test_clean_di_architecture_has_no_violations(self, temp_module_dir, architect_agent):
        """Clean DI architecture should have zero violations"""
        # API layer
        api_file = temp_module_dir / "backend" / "api.py"
        api_file.write_text("""
from flask import Blueprint, current_app
from core.interfaces.database_path_resolver import IDatabasePathResolver
from ..facade import DataProductsFacade

data_products_api = Blueprint('data_products', __name__)

def get_facade():
    path_resolver: IDatabasePathResolver = current_app.extensions['data_products_v2_path_resolver']
    return DataProductsFacade('sqlite', path_resolver=path_resolver)

@data_products_api.route('/products')
def get_products():
    facade = get_facade()
    return facade.get_all_products()
""")
        
        # Facade layer
        facade_file = temp_module_dir / "facade" / "data_products_facade.py"
        facade_file.write_text("""
from core.interfaces.database_path_resolver import IDatabasePathResolver
from ..repositories import DataProductRepositoryFactory

class DataProductsFacade:
    def __init__(self, source_type: str, path_resolver: IDatabasePathResolver):
        self._repository = DataProductRepositoryFactory.create(source_type, path_resolver)
""")
        
        # Repository factory
        factory_file = temp_module_dir / "repositories" / "repository_factory.py"
        factory_file.write_text("""
from core.interfaces.database_path_resolver import IDatabasePathResolver

class DataProductRepositoryFactory:
    @staticmethod
    def create(source_type: str, path_resolver: IDatabasePathResolver):
        if source_type == 'sqlite':
            return SQLiteDataProductRepository(path_resolver)
        return HANADataProductRepository()
""")
        
        # Repository
        repo_file = temp_module_dir / "repositories" / "sqlite_repository.py"
        repo_file.write_text("""
from core.interfaces.database_path_resolver import IDatabasePathResolver

class SQLiteDataProductRepository:
    def __init__(self, path_resolver: IDatabasePathResolver):
        db_path = path_resolver.resolve_path('data_products_v2')
        self._service = SQLiteDataProductsService(db_path)
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        # Clean architecture should have ZERO Service Locator violations
        service_locator_findings = [f for f in findings if 'Service Locator' in f.category]
        assert len(service_locator_findings) == 0


class TestRecommendations:
    """Test that recommendations are helpful and actionable"""
    
    def test_flask_config_recommendation_mentions_module_json(self, temp_module_dir, architect_agent):
        """Recommendation should mention module.json configuration"""
        api_file = temp_module_dir / "backend" / "api.py"
        api_file.write_text("""
from flask import current_app

db_path = current_app.config.get('SQLITE_DB_PATH')
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        flask_findings = [f for f in findings if 'Flask config access' in f.description]
        assert len(flask_findings) > 0
        assert 'module.json' in flask_findings[0].recommendation
        assert 'ModuleLoader' in flask_findings[0].recommendation
        assert 'IDatabasePathResolver' in flask_findings[0].recommendation
    
    def test_constructor_recommendation_includes_example(self, temp_module_dir, architect_agent):
        """Recommendation should include code example"""
        repo_file = temp_module_dir / "repositories" / "repository.py"
        repo_file.write_text("""
class Repository:
    def __init__(self, db_path: str):
        self.db_path = db_path
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        constructor_findings = [f for f in findings if 'Constructor accepts' in f.description]
        assert len(constructor_findings) > 0
        recommendation = constructor_findings[0].recommendation
        assert 'IDatabasePathResolver' in recommendation
        assert 'def __init__' in recommendation
        assert 'resolve_path' in recommendation


class TestFileFiltering:
    """Test that detector correctly filters files"""
    
    def test_ignores_test_files(self, temp_module_dir, architect_agent):
        """Should ignore files in tests/ directory"""
        tests_dir = temp_module_dir / "tests"
        tests_dir.mkdir()
        
        test_file = tests_dir / "test_api.py"
        test_file.write_text("""
from flask import current_app

def test_config():
    db_path = current_app.config.get('SQLITE_DB_PATH')
    assert db_path is not None
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        # Test files should be ignored
        test_findings = [f for f in findings if 'test_api.py' in str(f.file_path)]
        assert len(test_findings) == 0
    
    def test_checks_backend_facade_repository_dirs(self, temp_module_dir, architect_agent):
        """Should check backend/, facade/, repositories/ directories"""
        # Create violation in each directory
        (temp_module_dir / "backend" / "api.py").write_text("""
def get_db():
    db_path = 'path.db'
""")
        
        (temp_module_dir / "facade" / "facade.py").write_text("""
class Facade:
    def __init__(self, db_path):
        self.db_path = db_path
""")
        
        (temp_module_dir / "repositories" / "repo.py").write_text("""
class Repository:
    def __init__(self, db_path: str):
        self.db_path = db_path
""")
        
        findings = architect_agent._detect_service_locator_violations(temp_module_dir)
        
        # Should find violations in all three directories
        assert len(findings) >= 3
        file_paths = [str(f.file_path) for f in findings]
        assert any('backend' in path for path in file_paths)
        assert any('facade' in path for path in file_paths)
        assert any('repositories' in path for path in file_paths)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])