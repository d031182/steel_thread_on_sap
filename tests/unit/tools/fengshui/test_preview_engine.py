"""
Tests for Feng Shui Preview Mode Engine

Validates that the preview engine correctly orchestrates validators
and provides fast feedback during planning phase.
"""

import pytest
from tools.fengshui.preview.engine import (
    PreviewEngine,
    PreviewResult,
    PreviewFinding,
    Severity
)
from tools.fengshui.preview.validators import (
    NamingValidator,
    StructureValidator,
    IsolationValidator,
    DependencyValidator,
    PatternValidator
)


class TestPreviewEngine:
    """Test Preview Engine core functionality"""
    
    def test_engine_initialization(self):
        """Test: Engine initializes with validators"""
        validators = [NamingValidator(), StructureValidator()]
        engine = PreviewEngine(validators=validators)
        
        assert len(engine.validators) == 2
        assert isinstance(engine.validators[0], NamingValidator)
        assert isinstance(engine.validators[1], StructureValidator)
    
    def test_engine_validates_good_design(self):
        """Test: Engine validates compliant design without findings"""
        validators = [NamingValidator()]
        engine = PreviewEngine(validators=validators)
        
        design_spec = {
            'module_name': 'test_module',
            'module_id': 'test_module',
            'routes': ['/test-module'],
            'api_endpoints': [{'path': '/api/test-module/health'}],
            'factory_name': 'TestModuleModule'
        }
        
        result = engine.validate_design(design_spec)
        
        assert isinstance(result, PreviewResult)
        assert result.module_name == 'test_module'
        assert len(result.findings) == 0
        assert result.validation_time_seconds < 1.0
        assert 'NamingValidator' in result.validators_run
        assert not result.has_blockers
    
    def test_engine_detects_naming_violations(self):
        """Test: Engine detects naming convention violations"""
        validators = [NamingValidator()]
        engine = PreviewEngine(validators=validators)
        
        design_spec = {
            'module_name': 'test_module',
            'module_id': 'TestModule',  # Should be snake_case
            'routes': ['/TestModule'],  # Should be kebab-case
            'factory_name': 'testModule'  # Should be PascalCase + Module
        }
        
        result = engine.validate_design(design_spec)
        
        assert len(result.findings) == 3
        assert result.has_blockers  # HIGH severity findings
        
        # Check specific findings
        finding_messages = [f.message for f in result.findings]
        assert any('snake_case' in msg for msg in finding_messages)
        assert any('kebab-case' in msg for msg in finding_messages)
        assert any('PascalCase' in msg for msg in finding_messages)
    
    def test_engine_detects_structure_violations(self):
        """Test: Engine detects missing required files/directories"""
        validators = [StructureValidator()]
        engine = PreviewEngine(validators=validators)
        
        design_spec = {
            'module_name': 'test_module',
            'structure': {
                'files': [],  # Missing module.json, README.md
                'directories': ['backend'],  # Missing frontend, tests
                'backend_files': []  # Missing api.py
            }
        }
        
        result = engine.validate_design(design_spec)
        
        # Should find: module.json, README.md, frontend/, tests/, backend/api.py
        assert len(result.findings) >= 4
        assert result.has_blockers  # CRITICAL/HIGH findings
        
        # Check for CRITICAL findings
        critical_findings = [f for f in result.findings if f.severity == Severity.CRITICAL]
        assert len(critical_findings) >= 2  # module.json, README.md
    
    def test_engine_detects_isolation_violations(self):
        """Test: Engine detects cross-module imports"""
        validators = [IsolationValidator()]
        engine = PreviewEngine(validators=validators)
        
        design_spec = {
            'module_name': 'test_module',
            'dependencies': [
                'from modules.other_module import SomeClass',
                'import modules.another_module'
            ]
        }
        
        result = engine.validate_design(design_spec)
        
        assert len(result.findings) >= 2
        assert result.has_blockers  # CRITICAL severity
        
        # All isolation violations should be CRITICAL
        for finding in result.findings:
            if 'isolation' in finding.category.lower():
                assert finding.severity == Severity.CRITICAL
    
    def test_engine_multiple_validators(self):
        """Test: Engine runs multiple validators and aggregates findings"""
        validators = [
            NamingValidator(),
            StructureValidator(),
            IsolationValidator()
        ]
        engine = PreviewEngine(validators=validators)
        
        design_spec = {
            'module_name': 'test_module',
            'module_id': 'TestModule',  # Naming violation
            'structure': {
                'files': [],  # Structure violations
                'directories': []
            },
            'dependencies': ['from modules.other import X']  # Isolation violation
        }
        
        result = engine.validate_design(design_spec)
        
        # Should have findings from all 3 validators
        assert len(result.findings) >= 3
        assert len(result.validators_run) == 3
        assert 'NamingValidator' in result.validators_run
        assert 'StructureValidator' in result.validators_run
        assert 'IsolationValidator' in result.validators_run
    
    def test_engine_performance(self):
        """Test: Engine validates in < 1 second"""
        validators = [
            NamingValidator(),
            StructureValidator(),
            IsolationValidator(),
            DependencyValidator(),
            PatternValidator()
        ]
        engine = PreviewEngine(validators=validators)
        
        design_spec = {
            'module_name': 'test_module',
            'module_id': 'test_module',
            'routes': ['/test-module'],
            'structure': {
                'files': ['module.json', 'README.md'],
                'directories': ['backend', 'frontend', 'tests'],
                'backend_files': ['api.py', 'services.py', 'repositories.py']
            }
        }
        
        result = engine.validate_design(design_spec)
        
        # Performance requirement: < 1 second
        assert result.validation_time_seconds < 1.0
    
    def test_engine_format_output_clean(self):
        """Test: Engine formats clean result without findings"""
        validators = [NamingValidator()]
        engine = PreviewEngine(validators=validators)
        
        design_spec = {
            'module_name': 'test_module',
            'module_id': 'test_module'
        }
        
        result = engine.validate_design(design_spec)
        output = engine.format_output(result)
        
        assert 'test_module' in output
        assert 'No violations detected' in output
        assert 'Architecture looks good' in output
    
    def test_engine_format_output_with_findings(self):
        """Test: Engine formats result with findings"""
        validators = [NamingValidator()]
        engine = PreviewEngine(validators=validators)
        
        design_spec = {
            'module_name': 'test_module',
            'module_id': 'TestModule'  # Violation
        }
        
        result = engine.validate_design(design_spec)
        output = engine.format_output(result)
        
        assert 'test_module' in output
        assert 'BLOCKERS DETECTED' in output
        assert 'snake_case' in output
        assert 'Suggestion' in output


class TestNamingValidator:
    """Test Naming Convention Validator"""
    
    def test_valid_module_id(self):
        """Test: Valid snake_case module_id passes"""
        validator = NamingValidator()
        design_spec = {
            'module_name': 'test',
            'module_id': 'ai_assistant'
        }
        
        findings = validator.validate(design_spec)
        assert len(findings) == 0
    
    def test_invalid_module_id_camelcase(self):
        """Test: CamelCase module_id fails"""
        validator = NamingValidator()
        design_spec = {
            'module_name': 'test',
            'module_id': 'aiAssistant'
        }
        
        findings = validator.validate(design_spec)
        assert len(findings) == 1
        assert findings[0].severity == Severity.HIGH
        assert 'snake_case' in findings[0].message
    
    def test_valid_routes(self):
        """Test: Valid kebab-case routes pass"""
        validator = NamingValidator()
        design_spec = {
            'module_name': 'test',
            'routes': ['/ai-assistant', '/data-products']
        }
        
        findings = validator.validate(design_spec)
        assert len(findings) == 0
    
    def test_invalid_routes(self):
        """Test: Invalid routes fail"""
        validator = NamingValidator()
        design_spec = {
            'module_name': 'test',
            'routes': ['/AI_Assistant', '/dataProducts']
        }
        
        findings = validator.validate(design_spec)
        assert len(findings) == 2
        assert all(f.severity == Severity.MEDIUM for f in findings)


class TestStructureValidator:
    """Test Structure Validator"""
    
    def test_missing_required_files(self):
        """Test: Missing module.json and README.md"""
        validator = StructureValidator()
        design_spec = {
            'module_name': 'test',
            'structure': {
                'files': [],
                'directories': []
            }
        }
        
        findings = validator.validate(design_spec)
        
        # Should find missing module.json and README.md
        assert len(findings) >= 2
        critical_findings = [f for f in findings if f.severity == Severity.CRITICAL]
        assert len(critical_findings) == 2
    
    def test_missing_directories(self):
        """Test: Missing required directories"""
        validator = StructureValidator()
        design_spec = {
            'module_name': 'test',
            'structure': {
                'files': ['module.json', 'README.md'],
                'directories': []  # Missing backend, frontend, tests
            }
        }
        
        findings = validator.validate(design_spec)
        
        # Should find 3 missing directories
        assert len(findings) == 3
        assert all(f.severity == Severity.HIGH for f in findings)


class TestIsolationValidator:
    """Test Module Isolation Validator"""
    
    def test_no_dependencies_clean(self):
        """Test: No dependencies is clean"""
        validator = IsolationValidator()
        design_spec = {
            'module_name': 'test',
            'dependencies': []
        }
        
        findings = validator.validate(design_spec)
        assert len(findings) == 0
    
    def test_detects_cross_module_import(self):
        """Test: Detects from modules. import"""
        validator = IsolationValidator()
        design_spec = {
            'module_name': 'test',
            'dependencies': ['from modules.other_module import X']
        }
        
        findings = validator.validate(design_spec)
        # Validator returns 2 findings: 1 CRITICAL violation + 1 INFO recommendation
        assert len(findings) >= 1
        
        # Check that CRITICAL isolation violation is present
        critical_findings = [f for f in findings if f.severity == Severity.CRITICAL]
        assert len(critical_findings) == 1
        assert 'isolation' in critical_findings[0].category.lower()
    
    def test_core_interfaces_recommendation(self):
        """Test: Recommends core/interfaces for dependencies"""
        validator = IsolationValidator()
        design_spec = {
            'module_name': 'test',
            'dependencies': ['import requests', 'import flask']
        }
        
        findings = validator.validate(design_spec)
        
        # Should have INFO finding about using core/interfaces
        info_findings = [f for f in findings if f.severity == Severity.INFO]
        assert len(info_findings) == 1
        assert 'core/interfaces' in info_findings[0].message


class TestPreviewResultDataModel:
    """Test PreviewResult data model"""
    
    def test_has_blockers_true(self):
        """Test: has_blockers=True for CRITICAL/HIGH findings"""
        findings = [
            PreviewFinding(
                severity=Severity.HIGH,
                category='test',
                message='test',
                location='test',
                suggestion='test'
            )
        ]
        result = PreviewResult(
            module_name='test',
            findings=findings,
            validation_time_seconds=0.1,
            validators_run=['TestValidator']
        )
        
        assert result.has_blockers is True
    
    def test_has_blockers_false(self):
        """Test: has_blockers=False for MEDIUM/LOW/INFO findings"""
        findings = [
            PreviewFinding(
                severity=Severity.MEDIUM,
                category='test',
                message='test',
                location='test',
                suggestion='test'
            )
        ]
        result = PreviewResult(
            module_name='test',
            findings=findings,
            validation_time_seconds=0.1,
            validators_run=['TestValidator']
        )
        
        assert result.has_blockers is False
    
    def test_finding_counts(self):
        """Test: Counts findings by severity"""
        findings = [
            PreviewFinding(Severity.CRITICAL, 'test', 'test', 'test', 'test'),
            PreviewFinding(Severity.HIGH, 'test', 'test', 'test', 'test'),
            PreviewFinding(Severity.HIGH, 'test', 'test', 'test', 'test'),
            PreviewFinding(Severity.MEDIUM, 'test', 'test', 'test', 'test'),
        ]
        result = PreviewResult(
            module_name='test',
            findings=findings,
            validation_time_seconds=0.1,
            validators_run=['TestValidator']
        )
        
        counts = result.finding_counts
        assert counts['CRITICAL'] == 1
        assert counts['HIGH'] == 2
        assert counts['MEDIUM'] == 1
        assert counts['LOW'] == 0
        assert counts['INFO'] == 0
    
    def test_to_dict_serialization(self):
        """Test: Result serializes to JSON-compatible dict"""
        finding = PreviewFinding(
            severity=Severity.HIGH,
            category='test_category',
            message='test message',
            location='test/location',
            suggestion='test suggestion'
        )
        result = PreviewResult(
            module_name='test_module',
            findings=[finding],
            validation_time_seconds=0.123,
            validators_run=['TestValidator']
        )
        
        data = result.to_dict()
        
        assert data['module_name'] == 'test_module'
        assert len(data['findings']) == 1
        assert data['findings'][0]['severity'] == 'HIGH'
        assert data['validation_time_seconds'] == 0.123
        assert data['validators_run'] == ['TestValidator']
        assert data['has_blockers'] is True
        assert isinstance(data['finding_counts'], dict)