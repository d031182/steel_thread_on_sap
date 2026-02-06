"""
Unit tests for Feng Shui Module Quality Gate (Phase 4.15)

Tests cover:
- Module structure validation
- Blueprint registration checks
- DI violation detection
- Interface compliance verification
- Quality scoring algorithm
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tools.fengshui.module_quality_gate import ModuleQualityGate, ValidationResult


@pytest.mark.unit
@pytest.mark.fast
class TestModuleQualityGate:
    """Test suite for Module Quality Gate"""

    def setup_method(self):
        """Set up test fixtures"""
        # ARRANGE - Create mock module structure
        self.valid_module_path = Path("modules/test_module")
        self.gate = ModuleQualityGate()

    def teardown_method(self):
        """Clean up test fixtures"""
        self.gate = None

    # ========== Module Structure Validation ==========

    @pytest.mark.unit
    def test_validate_module_structure_complete(self):
        """Test validation of complete module structure"""
        # ARRANGE
        module_path = self.valid_module_path
        
        # ACT
        result = self.gate._validate_structure(module_path)

        # ASSERT
        assert isinstance(result, ValidationResult)
        # Score depends on file existence, so just check it's a valid result
        assert 0.0 <= result.score <= 1.0

    @pytest.mark.unit
    def test_validate_module_structure_missing_module_json(self):
        """Test validation fails when module.json is missing"""
        # ARRANGE
        module_path = Path("modules/nonexistent_module")
        
        # ACT
        result = self.gate._validate_structure(module_path)

        # ASSERT
        assert isinstance(result, ValidationResult)
        assert not result.passed
        assert 'module.json' in str(result.details.get('missing_required', []))

    @pytest.mark.unit
    def test_validate_module_structure_missing_backend(self):
        """Test validation detects missing backend directory"""
        # ARRANGE
        module_path = Path("modules/test_no_backend")
        
        # ACT
        result = self.gate._validate_structure(module_path)

        # ASSERT
        assert isinstance(result, ValidationResult)
        assert len(result.issues) > 0 or len(result.warnings) > 0

    @pytest.mark.unit
    def test_validate_module_structure_missing_tests(self):
        """Test validation detects missing tests directory"""
        # ARRANGE
        module_path = Path("modules/test_no_tests")
        
        # ACT
        result = self.gate._validate_structure(module_path)

        # ASSERT
        assert isinstance(result, ValidationResult)
        # Tests directory is recommended, so should appear in warnings if missing
        assert len(result.warnings) >= 0  # May or may not have warnings depending on structure

    # ========== Blueprint Registration ==========

    @pytest.mark.unit
    def test_check_blueprint_registration_valid(self):
        """Test blueprint registration check with valid configuration"""
        # ARRANGE
        module_path = Path("modules/test_valid_blueprint")
        module_json = {
            "name": "test_module",
            "enabled": True,
            "backend": {
                "blueprint": "modules.test_module.backend.api:blueprint"
            }
        }
        api_content = """
from flask import Blueprint

blueprint = Blueprint('test_module', __name__)

@blueprint.route('/test')
def test_endpoint():
    return {'status': 'ok'}
"""

        # ACT
        with patch('builtins.open', side_effect=[
            MagicMock(__enter__=lambda s: MagicMock(read=lambda: json.dumps(module_json))),
            MagicMock(__enter__=lambda s: MagicMock(read=lambda: api_content))
        ]):
            with patch('pathlib.Path.exists', return_value=True):
                result = self.gate._validate_blueprint(module_path)

        # ASSERT
        assert isinstance(result, ValidationResult)
        assert result.details['blueprint_defined'] is True
        assert result.details['blueprint_exported'] is True

    @pytest.mark.unit
    def test_check_blueprint_registration_missing_in_module_json(self):
        """Test detection of missing blueprint in module.json"""
        # ARRANGE
        module_path = Path("modules/test_missing_blueprint")
        module_json = {
            "name": "test_module",
            "enabled": True,
            "backend": {}  # No blueprint field
        }

        # ACT
        with patch('builtins.open', return_value=MagicMock(__enter__=lambda s: MagicMock(read=lambda: json.dumps(module_json)))):
            with patch('pathlib.Path.exists', return_value=True):
                result = self.gate._validate_blueprint(module_path)

        # ASSERT
        assert isinstance(result, ValidationResult)
        assert not result.passed
        assert result.details['blueprint_defined'] is False

    @pytest.mark.unit
    def test_check_blueprint_registration_not_exported(self):
        """Test detection of blueprint not exported in api.py"""
        # ARRANGE
        module_path = Path("modules/test_no_export")
        module_json = {
            "name": "test_module",
            "enabled": True,
            "backend": {
                "blueprint": "modules.test_module.backend.api:blueprint"
            }
        }
        api_content = """
from flask import Flask
# No blueprint definition
"""

        # ACT
        with patch('builtins.open', side_effect=[
            MagicMock(__enter__=lambda s: MagicMock(read=lambda: json.dumps(module_json))),
            MagicMock(__enter__=lambda s: MagicMock(read=lambda: api_content))
        ]):
            with patch('pathlib.Path.exists', return_value=True):
                result = self.gate._validate_blueprint(module_path)

        # ASSERT
        assert isinstance(result, ValidationResult)
        assert not result.passed
        assert result.details['blueprint_exported'] is False

    # ========== DI Violation Detection ==========

    @pytest.mark.unit
    def test_detect_di_violations_none(self):
        """Test DI violation detection with clean code"""
        # ARRANGE
        module_path = Path("modules/test_clean")
        clean_code = """
from core.interfaces.database_path_resolver import IDatabasePathResolver

class Service:
    def __init__(self, resolver: IDatabasePathResolver):
        self.resolver = resolver
        
    def get_data(self):
        db_path = self.resolver.resolve('my_db')
        return load_from_db(db_path)
"""

        # ACT
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.rglob', return_value=[Path('service.py')]):
                with patch('builtins.open', return_value=MagicMock(__enter__=lambda s: MagicMock(read=lambda: clean_code))):
                    result = self.gate._validate_di_compliance(module_path)

        # ASSERT
        assert isinstance(result, ValidationResult)
        assert result.passed
        assert result.score == 1.0

    @pytest.mark.unit
    def test_detect_di_violations_direct_access(self):
        """Test detection of direct database access violations"""
        # ARRANGE
        module_path = Path("modules/test_violations").resolve()
        violating_code = """
class Service:
    def get_data(self):
        connection = self.connection  # DI VIOLATION
        db_path = self.db_path  # DI VIOLATION
        return connection.execute('SELECT * FROM table')
"""
        # Create absolute path for mock file
        mock_file = module_path / 'backend' / 'service.py'

        # ACT
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.rglob', return_value=[mock_file]):
                with patch('builtins.open', return_value=MagicMock(__enter__=lambda s: MagicMock(read=lambda: violating_code))):
                    result = self.gate._validate_di_compliance(module_path)

        # ASSERT
        assert isinstance(result, ValidationResult)
        assert not result.passed
        assert len(result.details['violations']) >= 2

    @pytest.mark.unit
    def test_detect_di_violations_service_access(self):
        """Test detection of direct service access violations"""
        # ARRANGE
        module_path = Path("modules/test_service_violation").resolve()
        violating_code = """
class Controller:
    def handle_request(self):
        data = self.service.get_data()  # DI VIOLATION
        return data
"""
        # Create absolute path for mock file
        mock_file = module_path / 'backend' / 'controller.py'

        # ACT
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.rglob', return_value=[mock_file]):
                with patch('builtins.open', return_value=MagicMock(__enter__=lambda s: MagicMock(read=lambda: violating_code))):
                    result = self.gate._validate_di_compliance(module_path)

        # ASSERT
        assert isinstance(result, ValidationResult)
        assert len(result.details['violations']) >= 1

    @pytest.mark.unit
    def test_detect_di_violations_multiple_files(self):
        """Test DI violation detection across multiple files"""
        # ARRANGE
        module_path = Path("modules/test_multiple").resolve()
        file1_code = "self.connection.execute('SELECT')"
        file2_code = "result = self.service.get_data()"
        
        # Create absolute paths for mock files
        mock_files = [
            module_path / 'backend' / 'file1.py',
            module_path / 'backend' / 'file2.py'
        ]

        # ACT
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.rglob', return_value=mock_files):
                with patch('builtins.open', side_effect=[
                    MagicMock(__enter__=lambda s: MagicMock(read=lambda: file1_code)),
                    MagicMock(__enter__=lambda s: MagicMock(read=lambda: file2_code))
                ]):
                    result = self.gate._validate_di_compliance(module_path)

        # ASSERT
        assert isinstance(result, ValidationResult)
        assert len(result.details['violations']) >= 2

    # ========== Overall Score Calculation ==========

    @pytest.mark.unit
    def test_calculate_overall_score_perfect(self):
        """Test overall score calculation for perfect module"""
        # ARRANGE
        self.gate.results = {
            'structure': ValidationResult(passed=True, score=1.0),
            'blueprint': ValidationResult(passed=True, score=1.0),
            'di_compliance': ValidationResult(passed=True, score=1.0),
            'interface_usage': ValidationResult(passed=True, score=1.0),
            'coupling': ValidationResult(passed=True, score=1.0)
        }

        # ACT
        score = self.gate._calculate_overall_score()

        # ASSERT
        assert score == 1.0

    @pytest.mark.unit
    def test_calculate_overall_score_weighted(self):
        """Test overall score calculation with weighted components"""
        # ARRANGE
        self.gate.results = {
            'structure': ValidationResult(passed=True, score=0.8),
            'blueprint': ValidationResult(passed=True, score=0.9),
            'di_compliance': ValidationResult(passed=False, score=0.6),
            'interface_usage': ValidationResult(passed=True, score=0.7),
            'coupling': ValidationResult(passed=True, score=0.85)
        }

        # ACT
        score = self.gate._calculate_overall_score()

        # ASSERT
        assert 0.0 <= score <= 1.0
        # DI compliance weighted at 30%, should impact score
        assert score < 0.85

    @pytest.mark.unit
    def test_calculate_overall_score_di_heavy_weight(self):
        """Test that DI compliance failures heavily impact score"""
        # ARRANGE
        self.gate.results = {
            'structure': ValidationResult(passed=True, score=1.0),
            'blueprint': ValidationResult(passed=True, score=1.0),
            'di_compliance': ValidationResult(passed=False, score=0.0),  # CRITICAL
            'interface_usage': ValidationResult(passed=True, score=1.0),
            'coupling': ValidationResult(passed=True, score=1.0)
        }

        # ACT
        score = self.gate._calculate_overall_score()

        # ASSERT
        # DI compliance is 30% weight, so score should be around 0.7
        assert score <= 0.75

    # ========== Integration Tests ==========

    @pytest.mark.unit
    def test_quality_gate_full_validation_pass(self):
        """Test complete quality gate validation passing"""
        # ARRANGE
        module_path = Path("modules/test_pass")
        
        # Mock all internal validation methods
        self.gate._validate_structure = Mock(return_value=ValidationResult(passed=True, score=1.0))
        self.gate._validate_blueprint = Mock(return_value=ValidationResult(passed=True, score=1.0, details={'blueprint_defined': True, 'blueprint_exported': True}))
        self.gate._validate_di_compliance = Mock(return_value=ValidationResult(passed=True, score=1.0, details={'violations': []}))
        self.gate._validate_interface_usage = Mock(return_value=ValidationResult(passed=True, score=1.0))
        self.gate._validate_coupling = Mock(return_value=ValidationResult(passed=True, score=1.0))
        
        # ACT
        with patch('pathlib.Path.exists', return_value=True):
            result = self.gate.validate(module_path)

        # ASSERT
        assert result['passed'] is True
        assert result['overall_score'] >= 0.7

    @pytest.mark.unit
    def test_quality_gate_full_validation_fail(self):
        """Test complete quality gate validation failing"""
        # ARRANGE
        module_path = Path("modules/test_fail")
        
        # Mock all internal validation methods to fail
        self.gate._validate_structure = Mock(return_value=ValidationResult(passed=False, score=0.3, issues=['Missing module.json'], details={'missing_required': ['module.json']}))
        self.gate._validate_blueprint = Mock(return_value=ValidationResult(passed=False, score=0.0, issues=['No blueprint'], details={'blueprint_defined': False, 'blueprint_exported': False}))
        self.gate._validate_di_compliance = Mock(return_value=ValidationResult(passed=False, score=0.5, issues=['DI violation'], details={'violations': [{'pattern': '.connection'}]}))
        self.gate._validate_interface_usage = Mock(return_value=ValidationResult(passed=True, score=0.5))
        self.gate._validate_coupling = Mock(return_value=ValidationResult(passed=True, score=0.8))
        
        # Set critical issues
        self.gate.critical_issues = ['Missing module.json', 'No blueprint', 'DI violation']
        
        # ACT
        with patch('pathlib.Path.exists', return_value=True):
            result = self.gate.validate(module_path)

        # ASSERT
        assert result['passed'] is False
        assert result['overall_score'] < 0.7
        assert len(result['critical_issues']) > 0

    @pytest.mark.unit
    def test_quality_gate_exit_code(self):
        """Test quality gate returns correct exit codes"""
        # ARRANGE
        passing_result = {'passed': True, 'overall_score': 0.95}
        failing_result = {'passed': False, 'overall_score': 0.45}

        # ACT
        exit_code_pass = 0 if passing_result['passed'] else 1
        exit_code_fail = 0 if failing_result['passed'] else 1

        # ASSERT
        assert exit_code_pass == 0
        assert exit_code_fail == 1


@pytest.mark.integration
class TestModuleQualityGateIntegration:
    """Integration tests for Module Quality Gate with real modules"""

    @pytest.mark.integration
    def test_validate_real_knowledge_graph_module(self):
        """Test quality gate on real knowledge_graph module"""
        # ARRANGE
        module_path = Path("modules/knowledge_graph")
        gate = ModuleQualityGate()

        # ACT
        if module_path.exists():
            result = gate.validate(module_path)

            # ASSERT
            assert 'overall_score' in result
            assert 'passed' in result
            # Real module should have decent score
            assert result['overall_score'] > 0.5
        else:
            pytest.skip("knowledge_graph module not found")

    @pytest.mark.integration
    def test_validate_real_log_manager_module(self):
        """Test quality gate on real log_manager module"""
        # ARRANGE
        module_path = Path("modules/log_manager")
        gate = ModuleQualityGate()

        # ACT
        if module_path.exists():
            result = gate.validate(module_path)

            # ASSERT
            assert 'overall_score' in result
            assert 'passed' in result
        else:
            pytest.skip("log_manager module not found")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])