"""
Unit tests for SQL Execution Service

Tests SQL validation and execution with safety checks
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path

from modules.ai_assistant.backend.services.sql_execution_service import (
    SQLValidator,
    SQLExecutionService,
    SQLExecutionResult
)


class TestSQLValidator:
    """Test SQL query validation"""
    
    def test_valid_select_query(self):
        """Test: Valid SELECT query passes validation"""
        # ARRANGE
        sql = "SELECT * FROM suppliers WHERE rating > 4.5"
        
        # ACT
        is_valid, error = SQLValidator.validate_query(sql)
        
        # ASSERT
        assert is_valid is True
        assert error is None
    
    def test_select_with_joins(self):
        """Test: SELECT with JOINs passes validation"""
        # ARRANGE
        sql = """
        SELECT s.name, COUNT(i.id) as invoice_count
        FROM suppliers s
        LEFT JOIN supplier_invoices i ON s.id = i.supplier_id
        GROUP BY s.name
        """
        
        # ACT
        is_valid, error = SQLValidator.validate_query(sql)
        
        # ASSERT
        assert is_valid is True
        assert error is None
    
    def test_rejects_insert(self):
        """Test: INSERT query is rejected"""
        # ARRANGE
        sql = "INSERT INTO suppliers (name) VALUES ('Test')"
        
        # ACT
        is_valid, error = SQLValidator.validate_query(sql)
        
        # ASSERT
        assert is_valid is False
        assert "Only SELECT queries allowed" in error
    
    def test_rejects_update(self):
        """Test: UPDATE query is rejected"""
        # ARRANGE
        sql = "UPDATE suppliers SET rating = 5.0 WHERE id = 1"
        
        # ACT
        is_valid, error = SQLValidator.validate_query(sql)
        
        # ASSERT
        assert is_valid is False
        assert "SELECT" in error
    
    def test_rejects_delete(self):
        """Test: DELETE query is rejected"""
        # ARRANGE
        sql = "DELETE FROM suppliers WHERE rating < 2.0"
        
        # ACT
        is_valid, error = SQLValidator.validate_query(sql)
        
        # ASSERT
        assert is_valid is False
        assert "SELECT" in error
    
    def test_rejects_drop_table(self):
        """Test: DROP TABLE is rejected"""
        # ARRANGE
        sql = "SELECT * FROM suppliers; DROP TABLE suppliers;"
        
        # ACT
        is_valid, error = SQLValidator.validate_query(sql)
        
        # ASSERT
        assert is_valid is False
        assert "Multiple statements" in error or "DROP" in error
    
    def test_rejects_create_table(self):
        """Test: CREATE TABLE is rejected"""
        # ARRANGE
        sql = "SELECT * FROM test; CREATE TABLE test (id INT);"
        
        # ACT
        is_valid, error = SQLValidator.validate_query(sql)
        
        # ASSERT
        assert is_valid is False
        assert "Multiple statements" in error
    
    def test_rejects_multiple_statements(self):
        """Test: Multiple statements are rejected"""
        # ARRANGE
        sql = "SELECT * FROM suppliers; SELECT * FROM invoices;"
        
        # ACT
        is_valid, error = SQLValidator.validate_query(sql)
        
        # ASSERT
        assert is_valid is False
        assert "Multiple statements" in error
    
    def test_rejects_sql_comments(self):
        """Test: SQL comments are rejected"""
        # ARRANGE
        sql = "SELECT * FROM suppliers -- WHERE rating > 4.5"
        
        # ACT
        is_valid, error = SQLValidator.validate_query(sql)
        
        # ASSERT
        assert is_valid is False
        assert "comments" in error.lower()
    
    def test_rejects_pragma(self):
        """Test: PRAGMA statements are rejected"""
        # ARRANGE
        sql = "PRAGMA table_info(suppliers)"
        
        # ACT
        is_valid, error = SQLValidator.validate_query(sql)
        
        # ASSERT
        assert is_valid is False
        assert "SELECT" in error or "PRAGMA" in error
    
    def test_rejects_empty_query(self):
        """Test: Empty query is rejected"""
        # ARRANGE
        sql = ""
        
        # ACT
        is_valid, error = SQLValidator.validate_query(sql)
        
        # ASSERT
        assert is_valid is False
        assert "Empty" in error
    
    def test_rejects_query_without_from(self):
        """Test: SELECT without FROM is rejected"""
        # ARRANGE
        sql = "SELECT 1 + 1"
        
        # ACT
        is_valid, error = SQLValidator.validate_query(sql)
        
        # ASSERT
        assert is_valid is False
        assert "FROM" in error
    
    def test_sanitize_adds_limit(self):
        """Test: Sanitize adds LIMIT if missing"""
        # ARRANGE
        sql = "SELECT * FROM suppliers"
        
        # ACT
        sanitized = SQLValidator.sanitize_query(sql, max_rows=100)
        
        # ASSERT
        assert "LIMIT 100" in sanitized
    
    def test_sanitize_enforces_max_limit(self):
        """Test: Sanitize enforces maximum LIMIT"""
        # ARRANGE
        sql = "SELECT * FROM suppliers LIMIT 5000"
        
        # ACT
        sanitized = SQLValidator.sanitize_query(sql, max_rows=1000)
        
        # ASSERT
        assert "LIMIT 1000" in sanitized
        assert "LIMIT 5000" not in sanitized
    
    def test_sanitize_preserves_smaller_limit(self):
        """Test: Sanitize preserves LIMIT smaller than max"""
        # ARRANGE
        sql = "SELECT * FROM suppliers LIMIT 50"
        
        # ACT
        sanitized = SQLValidator.sanitize_query(sql, max_rows=1000)
        
        # ASSERT
        assert "LIMIT 50" in sanitized
    
    def test_allows_column_named_update(self):
        """Test: Allows column named 'update_date' (not a SQL UPDATE)"""
        # ARRANGE
        sql = "SELECT update_date, created_date FROM suppliers"
        
        # ACT
        is_valid, error = SQLValidator.validate_query(sql)
        
        # ASSERT
        assert is_valid is True  # Column name should be OK


class TestSQLExecutionService:
    """Test SQL execution with real database"""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary test database"""
        # ARRANGE
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Create test table and data
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE suppliers (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                rating REAL
            )
        """)
        
        cursor.execute("""
            INSERT INTO suppliers (id, name, rating) VALUES
            (1, 'Supplier A', 4.5),
            (2, 'Supplier B', 4.8),
            (3, 'Supplier C', 3.2)
        """)
        
        conn.commit()
        conn.close()
        
        yield db_path
        
        # Cleanup
        Path(db_path).unlink()
    
    def test_execute_valid_query(self, temp_db):
        """Test: Execute valid SELECT query returns results"""
        # ARRANGE
        service = SQLExecutionService(temp_db)
        sql = "SELECT * FROM suppliers"
        
        # ACT
        result = service.execute_query(sql)
        
        # ASSERT
        assert result.success is True
        assert result.row_count == 3
        assert len(result.rows) == 3
        assert 'name' in result.columns
        assert result.execution_time_ms >= 0  # Allow 0 for very fast queries
    
    def test_execute_filtered_query(self, temp_db):
        """Test: Execute query with WHERE clause"""
        # ARRANGE
        service = SQLExecutionService(temp_db)
        sql = "SELECT * FROM suppliers WHERE rating > 4.0"
        
        # ACT
        result = service.execute_query(sql)
        
        # ASSERT
        assert result.success is True
        assert result.row_count == 2
        assert all(row['rating'] > 4.0 for row in result.rows)
    
    def test_execute_aggregation(self, temp_db):
        """Test: Execute aggregation query"""
        # ARRANGE
        service = SQLExecutionService(temp_db)
        sql = "SELECT COUNT(*) as count, AVG(rating) as avg_rating FROM suppliers"
        
        # ACT
        result = service.execute_query(sql)
        
        # ASSERT
        assert result.success is True
        assert result.row_count == 1
        assert result.rows[0]['count'] == 3
        assert 'avg_rating' in result.rows[0]
    
    def test_rejects_unsafe_query(self, temp_db):
        """Test: Unsafe query returns error"""
        # ARRANGE
        service = SQLExecutionService(temp_db)
        sql = "DROP TABLE suppliers"
        
        # ACT
        result = service.execute_query(sql)
        
        # ASSERT
        assert result.success is False
        assert result.error is not None
        assert "SELECT" in result.error or "DROP" in result.error
        assert result.row_count == 0
    
    def test_handles_sql_error(self, temp_db):
        """Test: SQL errors are handled gracefully"""
        # ARRANGE
        service = SQLExecutionService(temp_db)
        sql = "SELECT * FROM nonexistent_table"
        
        # ACT
        result = service.execute_query(sql)
        
        # ASSERT
        assert result.success is False
        assert result.error is not None
        assert "no such table" in result.error.lower()
    
    def test_enforces_result_limit(self, temp_db):
        """Test: Result limit is enforced"""
        # ARRANGE
        service = SQLExecutionService(temp_db, max_rows=2)
        sql = "SELECT * FROM suppliers"
        
        # ACT
        result = service.execute_query(sql)
        
        # ASSERT
        assert result.success is True
        assert result.row_count == 2  # Limited to max_rows
        assert result.warnings is not None
        assert "LIMIT" in result.warnings[0]
    
    def test_raises_for_missing_database(self):
        """Test: Raises error if database doesn't exist"""
        # ARRANGE/ACT/ASSERT
        with pytest.raises(FileNotFoundError):
            SQLExecutionService("/nonexistent/path/db.db")


@pytest.mark.unit
@pytest.mark.ai_assistant
class TestSQLExecutionIntegration:
    """Integration tests with real P2P database"""
    
    def test_can_query_real_database(self):
        """Test: Can query real P2P database if it exists"""
        # ARRANGE
        db_path = "modules/sqlite_connection/database/p2p_data.db"
        
        if not Path(db_path).exists():
            pytest.skip("P2P database not found")
        
        service = SQLExecutionService(db_path)
        sql = "SELECT name FROM sqlite_master WHERE type='table' LIMIT 5"
        
        # ACT
        result = service.execute_query(sql)
        
        # ASSERT
        assert result.success is True
        assert result.row_count > 0