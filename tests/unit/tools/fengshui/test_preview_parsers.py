"""
Tests for Feng Shui Preview Mode Design Document Parsers

Tests extraction of module specifications from:
- module.json files
- README.md files
- Combined parsing and merging
"""

import json
import pytest
from pathlib import Path
from tools.fengshui.preview.parsers import (
    ModuleJsonParser,
    ReadmeParser,
    DesignDocumentParser,
    ExtractedModuleSpec,
    parse_module_design
)


class TestModuleJsonParser:
    """Test parsing of module.json files"""
    
    def test_parse_complete_module_json(self, tmp_path):
        """Test: Parse module.json with all fields"""
        # ARRANGE
        module_json = tmp_path / "module.json"
        module_json.write_text(json.dumps({
            "id": "test_module",
            "routes": ["/test-route"],
            "factory": "TestModuleFactory",
            "dependencies": ["core", "database"],
            "backend": {
                "api": "backend/api.py"
            }
        }))
        
        # ACT
        spec = ModuleJsonParser.parse(module_json)
        
        # ASSERT
        assert spec is not None
        assert spec.module_id == "test_module"
        assert spec.routes == ["/test-route"]
        assert spec.factory_name == "TestModuleFactory"
        assert spec.dependencies == ["core", "database"]
        assert spec.backend_api_path == "backend/api.py"
        assert spec.confidence_score == 1.0
        assert len(spec.extraction_warnings) == 0
    
    def test_parse_minimal_module_json(self, tmp_path):
        """Test: Parse module.json with minimal fields"""
        # ARRANGE
        module_json = tmp_path / "module.json"
        module_json.write_text(json.dumps({
            "id": "minimal_module"
        }))
        
        # ACT
        spec = ModuleJsonParser.parse(module_json)
        
        # ASSERT
        assert spec is not None
        assert spec.module_id == "minimal_module"
        assert spec.routes == []
        assert spec.factory_name is None
        assert spec.confidence_score < 1.0
        assert len(spec.extraction_warnings) > 0
    
    def test_parse_missing_file(self, tmp_path):
        """Test: Handle missing module.json"""
        # ARRANGE
        missing_path = tmp_path / "nonexistent.json"
        
        # ACT
        spec = ModuleJsonParser.parse(missing_path)
        
        # ASSERT
        assert spec is None
    
    def test_parse_invalid_json(self, tmp_path):
        """Test: Handle invalid JSON"""
        # ARRANGE
        module_json = tmp_path / "module.json"
        module_json.write_text("{ invalid json }")
        
        # ACT
        spec = ModuleJsonParser.parse(module_json)
        
        # ASSERT
        assert spec is None


class TestReadmeParser:
    """Test parsing of README.md files"""
    
    def test_parse_readme_with_structure(self, tmp_path):
        """Test: Extract structure from README"""
        # ARRANGE
        readme = tmp_path / "README.md"
        readme.write_text("""
# Test Module

## Structure
```
test_module/
├── backend/
│   ├── api.py
│   ├── services/
│   └── repositories/
├── frontend/
│   ├── module.js
│   └── views/
└── tests/
```

## API Endpoints

- POST /api/test-module/endpoint1
- GET /api/test-module/endpoint2
""")
        
        # ACT
        spec = ReadmeParser.parse(readme)
        
        # ASSERT
        assert spec is not None
        assert spec.module_id == "test"  # "Test Module" → "test" (Module stripped)
        assert "api.py" in spec.required_files
        assert "module.js" in spec.required_files
        assert "backend" in spec.required_directories
        assert "frontend" in spec.required_directories
        assert "services" in spec.required_directories
        assert "/api/test-module/endpoint1" in spec.api_endpoints
        assert "/api/test-module/endpoint2" in spec.api_endpoints
    
    def test_parse_readme_with_route_decorators(self, tmp_path):
        """Test: Extract routes from code examples"""
        # ARRANGE
        readme = tmp_path / "README.md"
        readme.write_text("""
# Example Module

## Implementation

```python
@blueprint.route('/api/example/test', methods=['POST'])
def test_endpoint():
    pass
```
""")
        
        # ACT
        spec = ReadmeParser.parse(readme)
        
        # ASSERT
        assert spec is not None
        assert "/api/example/test" in spec.api_endpoints
    
    def test_parse_minimal_readme(self, tmp_path):
        """Test: Parse README with minimal content"""
        # ARRANGE
        readme = tmp_path / "README.md"
        readme.write_text("# Minimal Module\n\nJust a title.")
        
        # ACT
        spec = ReadmeParser.parse(readme)
        
        # ASSERT
        assert spec is not None
        assert spec.module_id == "minimal"  # "Minimal Module" → "minimal" (Module stripped)
        assert spec.confidence_score < 1.0
        assert len(spec.extraction_warnings) > 0
    
    def test_parse_missing_readme(self, tmp_path):
        """Test: Handle missing README"""
        # ARRANGE
        missing_path = tmp_path / "README.md"
        
        # ACT
        spec = ReadmeParser.parse(missing_path)
        
        # ASSERT
        assert spec is None


class TestDesignDocumentParser:
    """Test combined parsing and merging"""
    
    def test_parse_complete_module(self, tmp_path):
        """Test: Parse module with both module.json and README"""
        # ARRANGE
        module_json = tmp_path / "module.json"
        module_json.write_text(json.dumps({
            "id": "complete_module",
            "routes": ["/complete-route"],
            "factory": "CompleteModuleFactory",
            "dependencies": ["core"]
        }))
        
        readme = tmp_path / "README.md"
        readme.write_text("""
# Complete Module

## Structure
```
complete_module/
├── backend/
│   └── api.py
└── frontend/
    └── module.js
```

## API Endpoints

- POST /api/complete-module/test
""")
        
        parser = DesignDocumentParser(tmp_path)
        
        # ACT
        spec = parser.parse()
        
        # ASSERT
        assert spec is not None
        assert spec.module_id == "complete_module"
        assert spec.routes == ["/complete-route"]
        assert spec.factory_name == "CompleteModuleFactory"
        assert "api.py" in spec.required_files
        assert "module.js" in spec.required_files
        assert "/api/complete-module/test" in spec.api_endpoints
        assert len(spec.source_files) == 2
    
    def test_parse_module_json_only(self, tmp_path):
        """Test: Parse with only module.json (README missing)"""
        # ARRANGE
        module_json = tmp_path / "module.json"
        module_json.write_text(json.dumps({
            "id": "json_only_module",
            "routes": ["/json-route"],
            "factory": "JsonOnlyFactory"
        }))
        
        parser = DesignDocumentParser(tmp_path)
        
        # ACT
        spec = parser.parse()
        
        # ASSERT
        assert spec is not None
        assert spec.module_id == "json_only_module"
        assert len(spec.source_files) == 1
    
    def test_parse_missing_module_json(self, tmp_path):
        """Test: Fail gracefully when module.json missing"""
        # ARRANGE
        readme = tmp_path / "README.md"
        readme.write_text("# Test Module")
        
        parser = DesignDocumentParser(tmp_path)
        
        # ACT
        spec = parser.parse()
        
        # ASSERT
        assert spec is None
    
    def test_to_preview_spec(self, tmp_path):
        """Test: Convert to PreviewEngine format"""
        # ARRANGE
        module_json = tmp_path / "module.json"
        module_json.write_text(json.dumps({
            "id": "preview_test",
            "routes": ["/preview-route"],
            "factory": "PreviewTestFactory"
        }))
        
        parser = DesignDocumentParser(tmp_path)
        spec = parser.parse()
        
        # ACT
        preview_spec = parser.to_preview_spec(spec)
        
        # ASSERT
        assert preview_spec['module_id'] == "preview_test"
        assert preview_spec['routes'] == ["/preview-route"]
        assert preview_spec['factory_name'] == "PreviewTestFactory"
        assert '_extracted_from' in preview_spec
        assert '_confidence' in preview_spec
        assert '_warnings' in preview_spec


class TestParseModuleDesign:
    """Test convenience function"""
    
    def test_parse_existing_module(self):
        """Test: Parse real module (ai_assistant)"""
        # ARRANGE
        module_path = "modules/ai_assistant"
        
        # ACT
        spec = parse_module_design(module_path)
        
        # ASSERT
        if spec:  # Only test if module exists
            assert spec['module_id'] == 'ai_assistant'
            assert isinstance(spec['routes'], list)
            assert '_confidence' in spec
    
    def test_parse_nonexistent_module(self, tmp_path):
        """Test: Handle nonexistent module"""
        # ARRANGE
        nonexistent = tmp_path / "nonexistent_module"
        
        # ACT
        spec = parse_module_design(str(nonexistent))
        
        # ASSERT
        assert spec is None


class TestMergeSpecs:
    """Test specification merging logic"""
    
    def test_merge_no_duplicates(self, tmp_path):
        """Test: Merge without duplicating entries"""
        # ARRANGE
        module_json = tmp_path / "module.json"
        module_json.write_text(json.dumps({
            "id": "merge_test",
            "routes": ["/route1"]
        }))
        
        readme = tmp_path / "README.md"
        readme.write_text("""
# Merge Test Module

## Structure
```
merge_test/
├── api.py
└── module.js
```

## API Endpoints
- GET /api/merge-test/endpoint1
- POST /api/merge-test/endpoint2
""")
        
        parser = DesignDocumentParser(tmp_path)
        
        # ACT
        spec = parser.parse()
        
        # ASSERT
        assert len(spec.routes) == 1  # No duplicates
        assert len(spec.required_files) == 2
        assert len(spec.api_endpoints) == 2
    
    def test_merge_confidence_calculation(self, tmp_path):
        """Test: Calculate merged confidence score"""
        # ARRANGE
        module_json = tmp_path / "module.json"
        module_json.write_text(json.dumps({
            "id": "confidence_test",
            "routes": ["/test"],
            "factory": "TestFactory"
        }))
        
        readme = tmp_path / "README.md"
        readme.write_text("""
# Confidence Test Module

## Structure
```
confidence_test/
└── api.py
```
""")
        
        parser = DesignDocumentParser(tmp_path)
        
        # ACT
        spec = parser.parse()
        
        # ASSERT
        assert 0 < spec.confidence_score <= 1.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])