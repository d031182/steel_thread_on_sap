# Tests Directory - Fresh Start

**Reset**: February 15, 2026
**Reason**: Persistent pytest I/O errors with previous test configuration

## Old Tests Location
- Archived to: `archive/tests_backup_2026_02_15/`
- Can be restored if needed

## New Test Structure
```
tests/
├── __init__.py
├── conftest.py (minimal configuration)
├── README.md (this file)
└── (future test files here)
```

## Running Tests
```bash
# Create new tests and run
pytest tests/ -v

# Run specific test file
pytest tests/test_example.py -v
```

## Note
Previous tests had 198 test items with pytest configuration issues.
Starting fresh with minimal configuration to avoid I/O errors.