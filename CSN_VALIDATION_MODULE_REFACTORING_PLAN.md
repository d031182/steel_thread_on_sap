# CSN Validation Module - Refactoring Plan

**Date**: 2026-01-24  
**Purpose**: Transform CSN validation into a self-contained, reusable module  
**Status**: 📋 PLANNING

---

## 🎯 Module Vision

**Module Name**: `csn-validation`

**Core Capability**: Validate CSN (Core Schema Notation) definitions against any data source (HANA, SQLite, PostgreSQL, etc.) and generate target schemas from source reality.

**Key Principle**: **Source-First Validation** - Always validate against deployed reality, not documentation theory.

---

## 📦 Module Structure

```
backend/modules/csn-validation/
├── README.md                      # Module documentation
├── __init__.py                    # Module exports
├── requirements.txt               # Module dependencies
│
├── core/                          # Core validation logic
│   ├── __init__.py
│   ├── validator.py              # Abstract base validator
│   ├── csn_parser.py             # CSN file parser
│   ├── type_mapper.py            # Type mapping engine (pluggable)
│   └── schema_generator.py       # Schema generation (pluggable)
│
├── sources/                       # Data source connectors (pluggable)
│   ├── __init__.py
│   ├── base.py                   # Abstract source connector
│   ├── hana_connector.py         # HANA Cloud connector
│   ├── sqlite_connector.py       # SQLite connector
│   ├── postgres_connector.py     # PostgreSQL connector (future)
│   └── bigquery_connector.py     # BigQuery connector (future)
│
├── reporters/                     # Report generators (pluggable)
│   ├── __init__.py
│   ├── base.py                   # Abstract reporter
│   ├── json_reporter.py          # JSON format
│   ├── markdown_reporter.py      # Markdown format
│   └── html_reporter.py          # HTML format (future)
│
├── cli/                          # Command-line interface
│   ├── __init__.py
│   ├── main.py                   # CLI entry point
│   └── commands.py               # CLI command handlers
│
├── api/                          # REST API (Flask endpoints)
│   ├── __init__.py
│   ├── routes.py                 # API routes
│   └── schemas.py                # API request/response schemas
│
├── config/                       # Configuration
│   ├── __init__.py
│   ├── settings.py               # Module settings
│   └── type_mappings.yaml        # Type mapping configurations
│
├── tests/                        # Comprehensive tests
│   ├── __init__.py
│   ├── test_validator.py
│   ├── test_csn_parser.py
│   ├── test_type_mapper.py
│   ├── test_hana_connector.py
│   ├── test_sqlite_connector.py
│   └── fixtures/                 # Test data
│       ├── sample_csn.json
│       └── mock_schemas.json
│
└── scripts/                      # Helper scripts
    ├── run_validation.py         # Python wrapper
    └── run_validation.ps1        # PowerShell wrapper
```

---

## 🏗️ Core Architecture

### 1. Abstract Validator Pattern

```python
# core/validator.py
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class SchemaValidator(ABC):
    """
    Abstract base class for schema validation.
    Enforces Source-First validation principle.
    """
    
    def __init__(self, source_connector, csn_parser, type_mapper):
        self.source = source_connector
        self.csn_parser = csn_parser
        self.type_mapper = type_mapper
    
    def validate(self, csn_file: str, entity_names: List[str] = None) -> Dict:
        """
        Main validation workflow:
        1. Parse CSN file
        2. Query source for actual structures
        3. Compare CSN vs source
        4. Generate validation report
        """
        csn = self.csn_parser.parse(csn_file)
        results = []
        
        for entity_name in (entity_names or csn.get_entities()):
            csn_fields = csn.get_fields(entity_name)
            source_columns = self.source.get_table_structure(entity_name)
            
            comparison = self._compare(csn_fields, source_columns)
            results.append(comparison)
        
        return {
            'success': True,
            'entities': results,
            'summary': self._generate_summary(results)
        }
    
    @abstractmethod
    def _compare(self, csn_fields: List, source_columns: List) -> Dict:
        """Compare CSN fields against source columns"""
        pass
    
    @abstractmethod
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate validation summary statistics"""
        pass
```

### 2. Pluggable Source Connectors

```python
# sources/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Optional

class SourceConnector(ABC):
    """
    Abstract base class for data source connectors.
    Each source (HANA, SQLite, PostgreSQL) implements this interface.
    """
    
    @abstractmethod
    def connect(self, connection_config: Dict) -> bool:
        """Establish connection to data source"""
        pass
    
    @abstractmethod
    def discover_schemas(self, pattern: str) -> List[str]:
        """Discover available schemas matching pattern"""
        pass
    
    @abstractmethod
    def get_table_structure(self, schema: str, table: str) -> List[Dict]:
        """
        Get table structure from source.
        Returns list of column definitions with:
        - name: Column name
        - dataType: Native data type
        - length: Length/precision
        - scale: Scale (for decimals)
        - nullable: Is nullable
        - position: Column position
        """
        pass
    
    @abstractmethod
    def close(self):
        """Close connection"""
        pass
```

```python
# sources/hana_connector.py
from .base import SourceConnector
from hdbcli import dbapi

class HanaConnector(SourceConnector):
    """HANA Cloud connector implementation"""
    
    def __init__(self):
        self.connection = None
    
    def connect(self, connection_config: Dict) -> bool:
        self.connection = dbapi.connect(
            address=connection_config['host'],
            port=connection_config['port'],
            user=connection_config['user'],
            password=connection_config['password'],
            encrypt=True,
            sslValidateCertificate=False
        )
        return True
    
    def discover_schemas(self, pattern: str = '_SAP_DATAPRODUCT%') -> List[str]:
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT SCHEMA_NAME FROM SYS.SCHEMAS WHERE SCHEMA_NAME LIKE ? ORDER BY SCHEMA_NAME",
            (pattern,)
        )
        return [row[0] for row in cursor.fetchall()]
    
    def get_table_structure(self, schema: str, table: str) -> List[Dict]:
        # Handles schema-prefixed table names automatically
        cursor = self.connection.cursor()
        
        # Try exact match first
        cursor.execute(
            "SELECT TABLE_NAME FROM SYS.TABLES WHERE SCHEMA_NAME = ? AND TABLE_NAME = ? LIMIT 1",
            (schema, table)
        )
        result = cursor.fetchone()
        
        if not result:
            # Try wildcard (for prefixed table names)
            cursor.execute(
                "SELECT TABLE_NAME FROM SYS.TABLES WHERE SCHEMA_NAME = ? AND TABLE_NAME LIKE ? LIMIT 1",
                (schema, f'%.{table}')
            )
            result = cursor.fetchone()
        
        if not result:
            return []
        
        actual_table_name = result[0]
        
        # Get column structure
        cursor.execute("""
            SELECT 
                COLUMN_NAME,
                POSITION,
                DATA_TYPE_NAME,
                LENGTH,
                SCALE,
                IS_NULLABLE
            FROM SYS.TABLE_COLUMNS
            WHERE SCHEMA_NAME = ? AND TABLE_NAME = ?
            ORDER BY POSITION
        """, (schema, actual_table_name))
        
        return [
            {
                'name': row[0],
                'position': row[1],
                'dataType': row[2],
                'length': row[3],
                'scale': row[4],
                'nullable': row[5] == 'TRUE'
            }
            for row in cursor.fetchall()
        ]
    
    def close(self):
        if self.connection:
            self.connection.close()
```

### 3. Pluggable Type Mappers

```python
# core/type_mapper.py
from typing import Dict, Optional
import yaml

class TypeMapper:
    """
    Maps types between different systems.
    Configuration-driven for easy extension.
    """
    
    def __init__(self, config_file: str = 'config/type_mappings.yaml'):
        with open(config_file, 'r') as f:
            self.mappings = yaml.safe_load(f)
    
    def map_type(self, from_system: str, to_system: str, 
                 type_name: str, length: Optional[int] = None,
                 scale: Optional[int] = None) -> str:
        """
        Map type from one system to another.
        
        Example:
            map_type('HANA', 'SQLite', 'NVARCHAR', length=50)
            → 'TEXT'
        """
        mapping = self.mappings.get(from_system, {}).get(to_system, {})
        
        # Try exact match first
        if type_name in mapping:
            result = mapping[type_name]
            
            # Handle parametrized types
            if isinstance(result, dict):
                return result['base'] + self._format_params(result, length, scale)
            return result
        
        # Try pattern match (e.g., 'NVARCHAR' → 'VARCHAR' family)
        for pattern, target in mapping.items():
            if pattern in type_name:
                return target
        
        # Default fallback
        return mapping.get('_default', 'TEXT')
    
    def _format_params(self, result: Dict, length: Optional[int], 
                       scale: Optional[int]) -> str:
        if length and result.get('use_length'):
            if scale and result.get('use_scale'):
                return f"({length},{scale})"
            return f"({length})"
        return ""
```

```yaml
# config/type_mappings.yaml
HANA:
  SQLite:
    NVARCHAR: TEXT
    VARCHAR: TEXT
    DECIMAL:
      base: REAL
      use_length: false
    INTEGER: INTEGER
    TINYINT: INTEGER
    SMALLINT: INTEGER
    DATE: TEXT
    TIMESTAMP: TEXT
    BOOLEAN: INTEGER
    DOUBLE: REAL
    REAL: REAL
    VARBINARY: BLOB
    BLOB: BLOB
    _default: TEXT

  PostgreSQL:
    NVARCHAR:
      base: VARCHAR
      use_length: true
    DECIMAL:
      base: NUMERIC
      use_length: true
      use_scale: true
    INTEGER: INTEGER
    DATE: DATE
    TIMESTAMP: TIMESTAMP
    BOOLEAN: BOOLEAN
    _default: TEXT

CDS:  # Core Data Services types
  HANA:
    cds.String: NVARCHAR
    cds.Decimal: DECIMAL
    cds.Integer: INTEGER
    cds.Date: DATE
    cds.DateTime: TIMESTAMP
    cds.Boolean: BOOLEAN
```

---

## 🔌 Plugin System

### Registry Pattern for Extensibility

```python
# core/registry.py
class ConnectorRegistry:
    """Registry for data source connectors"""
    _connectors = {}
    
    @classmethod
    def register(cls, name: str, connector_class):
        cls._connectors[name] = connector_class
    
    @classmethod
    def get(cls, name: str):
        return cls._connectors.get(name)
    
    @classmethod
    def list(cls):
        return list(cls._connectors.keys())

# Auto-registration in each connector
from core.registry import ConnectorRegistry

@ConnectorRegistry.register('hana')
class HanaConnector(SourceConnector):
    pass

@ConnectorRegistry.register('sqlite')
class SQLiteConnector(SourceConnector):
    pass
```

---

## 🎨 CLI Interface

```python
# cli/main.py
import click
from core.validator import SchemaValidator
from core.registry import ConnectorRegistry
from core.csn_parser import CSNParser
from core.type_mapper import TypeMapper

@click.group()
def cli():
    """CSN Validation Tool - Validate CSN against any data source"""
    pass

@cli.command()
@click.argument('csn_file')
@click.option('--source', default='hana', help='Source type: hana, sqlite, postgres')
@click.option('--config', default='config.yaml', help='Connection config file')
@click.option('--entities', multiple=True, help='Specific entities to validate')
@click.option('--output', default='validation_report.json', help='Output file')
@click.option('--format', default='json', type=click.Choice(['json', 'markdown', 'html']))
def validate(csn_file, source, config, entities, output, format):
    """Validate CSN against data source"""
    
    # Get connector
    connector_class = ConnectorRegistry.get(source)
    if not connector_class:
        click.echo(f"Error: Unknown source '{source}'")
        click.echo(f"Available: {', '.join(ConnectorRegistry.list())}")
        return
    
    # Setup
    connector = connector_class()
    connector.connect(load_config(config))
    
    parser = CSNParser()
    mapper = TypeMapper()
    validator = SchemaValidator(connector, parser, mapper)
    
    # Validate
    click.echo(f"Validating {csn_file} against {source}...")
    result = validator.validate(csn_file, list(entities) if entities else None)
    
    # Report
    reporter = get_reporter(format)
    reporter.save(result, output)
    
    click.echo(f"✅ Validation complete: {output}")
    
    connector.close()

@cli.command()
@click.argument('csn_file')
@click.option('--source', default='hana', help='Source to generate from')
@click.option('--target', default='sqlite', help='Target system: sqlite, postgres')
@click.option('--output', help='Output file (default: auto-generated)')
def generate(csn_file, source, target, output):
    """Generate target schema from source reality"""
    
    click.echo(f"Generating {target} schema from {source}...")
    # Implementation
    click.echo(f"✅ Schema generated: {output}")

if __name__ == '__main__':
    cli()
```

**Usage Examples:**
```bash
# Validate PurchaseOrder CSN against HANA
python -m csn_validation validate data-products/sap-s4com-PurchaseOrder-v1.en.json --source hana

# Validate specific entities
python -m csn_validation validate PurchaseOrder.json --source hana --entities PurchaseOrder PurchaseOrderItem

# Generate SQLite schema from HANA
python -m csn_validation generate PurchaseOrder.json --source hana --target sqlite --output purchaseorder.sql

# Use different source
python -m csn_validation validate PurchaseOrder.json --source sqlite --config local.yaml

# Generate different report formats
python -m csn_validation validate PurchaseOrder.json --format markdown --output report.md
```

---

## 🌐 REST API Interface

```python
# api/routes.py
from flask import Blueprint, request, jsonify
from core.validator import SchemaValidator
from core.registry import ConnectorRegistry

api = Blueprint('csn_validation', __name__, url_prefix='/api/csn-validation')

@api.route('/validate', methods=['POST'])
def validate():
    """
    POST /api/csn-validation/validate
    
    Body:
    {
      "csnFile": "path/to/csn.json",
      "source": "hana",
      "entities": ["PurchaseOrder", "PurchaseOrderItem"],
      "config": {...}
    }
    """
    data = request.json
    
    # Setup validator
    connector = ConnectorRegistry.get(data['source'])()
    connector.connect(data.get('config', {}))
    
    validator = SchemaValidator(connector, CSNParser(), TypeMapper())
    
    # Validate
    result = validator.validate(
        data['csnFile'],
        data.get('entities')
    )
    
    connector.close()
    
    return jsonify(result)

@api.route('/generate-schema', methods=['POST'])
def generate_schema():
    """
    POST /api/csn-validation/generate-schema
    
    Body:
    {
      "csnFile": "path/to/csn.json",
      "source": "hana",
      "target": "sqlite",
      "config": {...}
    }
    """
    data = request.json
    
    # Implementation
    schema_sql = generate_schema_from_source(data)
    
    return jsonify({
        'success': True,
        'schema': schema_sql
    })

@api.route('/sources', methods=['GET'])
def list_sources():
    """GET /api/csn-validation/sources"""
    return jsonify({
        'sources': ConnectorRegistry.list()
    })
```

---

## 📚 Module Documentation

```markdown
# CSN Validation Module

## Quick Start

### Installation
```bash
pip install -r backend/modules/csn-validation/requirements.txt
```

### Basic Usage

#### Python
```python
from csn_validation import SchemaValidator, HanaConnector, CSNParser, TypeMapper

# Setup
connector = HanaConnector()
connector.connect({
    'host': 'your-instance.hanacloud.ondemand.com',
    'port': 443,
    'user': 'DBADMIN',
    'password': 'your-password'
})

validator = SchemaValidator(connector, CSNParser(), TypeMapper())

# Validate
result = validator.validate('PurchaseOrder.json')

print(f"Validated: {result['summary']['entities_count']} entities")
print(f"Success Rate: {result['summary']['success_rate']}%")

connector.close()
```

#### CLI
```bash
# Validate CSN
csn-validation validate PurchaseOrder.json --source hana

# Generate schema
csn-validation generate PurchaseOrder.json --source hana --target sqlite
```

#### REST API
```bash
curl -X POST http://localhost:5000/api/csn-validation/validate \
  -H "Content-Type: application/json" \
  -d '{
    "csnFile": "PurchaseOrder.json",
    "source": "hana",
    "entities": ["PurchaseOrder"]
  }'
```

## Adding New Source Connectors

1. Create connector class:
```python
from csn_validation.sources.base import SourceConnector
from csn_validation.core.registry import ConnectorRegistry

@ConnectorRegistry.register('bigquery')
class BigQueryConnector(SourceConnector):
    def connect(self, config):
        # Implementation
        pass
    
    def get_table_structure(self, schema, table):
        # Implementation
        pass
```

2. Add type mappings in `config/type_mappings.yaml`

3. Write tests in `tests/test_bigquery_connector.py`

4. Done! Connector is auto-discovered and available via CLI/API
```

---

## 🧪 Testing Strategy

### Unit Tests (Comprehensive)

```python
# tests/test_validator.py
import unittest
from csn_validation.core.validator import SchemaValidator
from csn_validation.sources.base import SourceConnector

class MockConnector(SourceConnector):
    """Mock connector for testing"""
    def connect(self, config): return True
    def get_table_structure(self, schema, table): 
        return [
            {'name': 'ID', 'dataType': 'NVARCHAR', 'length': 10, 'nullable': False},
            {'name': 'Name', 'dataType': 'NVARCHAR', 'length': 50, 'nullable': True}
        ]
    def close(self): pass

class TestValidator(unittest.TestCase):
    def setUp(self):
        self.validator = SchemaValidator(MockConnector(), MockParser(), MockMapper())
    
    def test_perfect_match(self):
        result = self.validator.validate('test.json')
        self.assertTrue(result['success'])
        self.assertEqual(result['summary']['success_rate'], 100)
    
    def test_missing_field(self):
        # Test handling of fields in CSN but not in source
        pass
    
    def test_type_mismatch(self):
        # Test handling of type differences
        pass
```

### Integration Tests

```python
# tests/test_hana_integration.py
@pytest.mark.integration
def test_hana_connection():
    """Test real HANA connection"""
    connector = HanaConnector()
    assert connector.connect(load_test_config())

@pytest.mark.integration
def test_full_validation_flow():
    """Test complete validation against test HANA instance"""
    result = validate_against_test_hana('test-data/PurchaseOrder.json')
    assert result['success']
```

---

## 🚀 Migration Strategy

### Phase 1: Extract Current Code (Week 1)
- [ ] Create module directory structure
- [ ] Move `validate_csn_against_hana.py` → `sources/hana_connector.py`
- [ ] Extract common logic → `core/validator.py`
- [ ] Create base classes and interfaces
- [ ] Add __init__.py files for proper imports

### Phase 2: Add Abstractions (Week 1-2)
- [ ] Implement SourceConnector base class
- [ ] Create TypeMapper with YAML config
- [ ] Add Reporter base class and JSON reporter
- [ ] Implement plugin registry system

### Phase 3: Add CLI (Week 2)
- [ ] Implement Click-based CLI
- [ ] Add validation command
- [ ] Add schema generation command
- [ ] Create PowerShell wrapper

### Phase 4: Add REST API (Week 2-3)
- [ ] Create Flask Blueprint
- [ ] Add validation endpoint
- [ ] Add schema generation endpoint
- [ ] Integrate with main Flask app

### Phase 5: Add SQLite Connector (Week 3)
- [ ] Implement SQLiteConnector
- [ ] Add SQLite-specific tests
- [ ] Update type mappings for SQLite

### Phase 6: Documentation & Tests (Week 3-4)
- [ ] Write comprehensive README
- [ ] Create usage examples
- [ ] Write unit tests (80%+ coverage)
- [ ] Write integration tests
- [ ] Create developer guide

### Phase 7: Production Hardening (Week 4)
- [ ] Add error handling
- [ ] Add logging throughout
- [ ] Performance optimization
- [ ] Security review
- [ ] Load testing

---

## 📊 Success Metrics

### Code Quality
- [ ] 80%+ test coverage
- [ ] Zero critical security issues
- [ ] < 10% code duplication
- [ ] All tests passing in CI/CD

### Performance
- [ ] Validation < 30 seconds for 500-column schema
- [ ] Memory usage < 100MB for typical validation
- [ ] CLI response time < 2 seconds

### Usability
- [ ] 3 ways to use: Python API, CLI, REST API
- [ ] Comprehensive documentation
- [ ] Easy to add new connectors (< 100 LOC)
- [ ] Clear error messages

### Extensibility
- [ ] Pluggable connectors
- [ ] Pluggable reporters
- [ ] Configurable type mappings
- [ ] Registry-based auto-discovery

---

## 🎓 Benefits of This Architecture

### 1. **Separation of Concerns**
- Core logic separate from connectors
- Clear interfaces between components
- Easy to understand and maintain

### 2. **Extensibility**
- Add new sources without changing core
- Add new reporters without changing validation
- Plugin system for auto-discovery

### 3. **Testability**
- Mock connectors for unit tests
- Integration tests with real sources
- Test each component in isolation

### 4. **Reusability**
- Use as Python library
- Use as CLI tool
- Use as REST API
- Embed in other applications

### 5. **Maintainability**
- Clear structure
- Self-contained module
- Comprehensive documentation
- Version control per module

### 6. **Enterprise-Ready**
- Configuration-driven
- Logging throughout
- Error handling
- Security considerations

---

## 🔄 Future Enhancements

### Additional Connectors
- [ ] PostgreSQL connector
- [ ] BigQuery connector
- [ ] Snowflake connector
- [ ] Oracle connector
- [ ] MySQL connector

### Additional Features
- [ ] Diff between two CSN versions
- [ ] Automatic schema migration scripts
- [ ] Data quality validation
- [ ] Performance profiling
- [ ] Schema visualization (graphical)

### Integration Options
- [ ] GitHub Action for CI/CD validation
- [ ] VS Code extension
- [ ] Web UI dashboard
- [ ] Slack/Teams notifications

---

## 📝 Next Steps

1. **Review this plan** with team
2. **Create module directory** structure
3. **Start Phase 1** migration
4. **Set up CI/CD** for module testing
5. **Document as you go**

**Estimated Timeline**: 4 weeks for complete modularization

**Status**: ✅ PLAN READY - Awaiting approval to begin implementation