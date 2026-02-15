"""
SQL Execution Service - Safe SQL execution with validation

Phase 4.5: SQL Execution from Chat

SECURITY CRITICAL:
- Only SELECT queries allowed
- Query validation before execution
- Result limits enforced
- No DDL/DML operations
"""

import re
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SQLExecutionResult:
    """Result of SQL execution"""
    success: bool
    rows: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    execution_time_ms: float
    error: Optional[str] = None
    warnings: List[str] = None


class SQLValidator:
    """
    SQL Query Validator - Security-first approach
    
    Validates SQL queries to prevent:
    - Data modification (INSERT, UPDATE, DELETE)
    - Schema changes (DROP, ALTER, CREATE)
    - Multiple statements (SQL injection)
    - Dangerous functions (ATTACH, PRAGMA)
    """
    
    # Forbidden keywords (case-insensitive)
    FORBIDDEN_KEYWORDS = {
        # Data modification
        'INSERT', 'UPDATE', 'DELETE', 'REPLACE', 'MERGE',
        # Schema changes
        'DROP', 'CREATE', 'ALTER', 'TRUNCATE', 'RENAME',
        # Database operations
        'ATTACH', 'DETACH',
        # Dangerous PRAGMA
        'PRAGMA',
        # Transaction control (could lock database)
        'BEGIN', 'COMMIT', 'ROLLBACK', 'SAVEPOINT',
        # Access control
        'GRANT', 'REVOKE'
    }
    
    # Allowed keywords (whitelist approach)
    ALLOWED_KEYWORDS = {
        'SELECT', 'FROM', 'WHERE', 'JOIN', 'LEFT', 'RIGHT', 'INNER',
        'OUTER', 'ON', 'AS', 'AND', 'OR', 'NOT', 'IN', 'LIKE',
        'BETWEEN', 'IS', 'NULL', 'ORDER', 'BY', 'GROUP', 'HAVING',
        'LIMIT', 'OFFSET', 'DISTINCT', 'COUNT', 'SUM', 'AVG',
        'MIN', 'MAX', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END',
        'CAST', 'COALESCE', 'NULLIF', 'IFNULL'
    }
    
    @classmethod
    def validate_query(cls, sql: str) -> Tuple[bool, Optional[str]]:
        """
        Validate SQL query for safety
        
        Args:
            sql: SQL query to validate
            
        Returns:
            (is_valid, error_message)
            
        Raises:
            ValueError: If query is unsafe
        """
        if not sql or not sql.strip():
            return False, "Empty SQL query"
        
        sql_upper = sql.upper().strip()
        
        # Check 1: Must start with SELECT
        if not sql_upper.startswith('SELECT'):
            return False, "Only SELECT queries allowed. No data modification permitted."
        
        # Check 2: No multiple statements (SQL injection prevention)
        if ';' in sql.strip()[:-1]:  # Allow trailing semicolon only
            return False, "Multiple statements not allowed. Single SELECT query only."
        
        # Check 3: No forbidden keywords
        for keyword in cls.FORBIDDEN_KEYWORDS:
            # Use word boundaries to avoid false positives (e.g., "update_date" column)
            pattern = r'\b' + keyword + r'\b'
            if re.search(pattern, sql_upper):
                return False, f"Forbidden keyword detected: {keyword}. Only read-only queries allowed."
        
        # Check 4: No comments (could hide malicious code)
        if '--' in sql or '/*' in sql or '*/' in sql:
            return False, "SQL comments not allowed for security reasons."
        
        # Check 5: Basic structure validation (FROM clause optional - SQLite supports SELECT without FROM)
        # Examples: SELECT 1, SELECT DATE('now'), SELECT RANDOM()
        
        return True, None
    
    @classmethod
    def sanitize_query(cls, sql: str, max_rows: int = 1000) -> str:
        """
        Sanitize query by adding safety limits
        
        Args:
            sql: Original SQL query
            max_rows: Maximum rows to return
            
        Returns:
            Sanitized SQL with LIMIT clause
        """
        sql = sql.strip()
        
        # Remove trailing semicolon if present
        if sql.endswith(';'):
            sql = sql[:-1].strip()
        
        # Add LIMIT if not present
        sql_upper = sql.upper()
        if 'LIMIT' not in sql_upper:
            sql += f" LIMIT {max_rows}"
        else:
            # Ensure LIMIT doesn't exceed max_rows
            limit_match = re.search(r'LIMIT\s+(\d+)', sql_upper)
            if limit_match:
                limit_value = int(limit_match.group(1))
                if limit_value > max_rows:
                    # Replace with max_rows
                    sql = re.sub(
                        r'LIMIT\s+\d+',
                        f'LIMIT {max_rows}',
                        sql,
                        flags=re.IGNORECASE
                    )
        
        return sql


class SQLExecutionService:
    """
    SQL Execution Service - Execute safe SQL queries
    
    Features:
    - Query validation (security checks)
    - Result limiting (prevent large result sets)
    - Error handling (user-friendly messages)
    - Performance tracking (execution time)
    
    DI Pattern:
    - Constructor injection for database paths (from module.json)
    - No Service Locator pattern
    """
    
    def __init__(self, p2p_data_db: str, p2p_graph_db: str, max_rows: int = 1000):
        """
        Initialize SQL execution service
        
        Args:
            p2p_data_db: Path to P2P data database (from module.json)
            p2p_graph_db: Path to P2P graph database (from module.json)
            max_rows: Maximum rows to return (default 1000)
        """
        self.p2p_data_db = Path(p2p_data_db)
        self.p2p_graph_db = Path(p2p_graph_db)
        self.max_rows = max_rows
        self.validator = SQLValidator()
        
        # Validate both databases exist
        if not self.p2p_data_db.exists():
            raise FileNotFoundError(f"P2P data database not found: {p2p_data_db}")
        if not self.p2p_graph_db.exists():
            raise FileNotFoundError(f"P2P graph database not found: {p2p_graph_db}")
    
    def execute_query(self, sql: str, datasource: str = "p2p_data") -> SQLExecutionResult:
        """
        Execute SQL query with validation
        
        Args:
            sql: SQL query to execute
            datasource: Database to query ("p2p_data" or "p2p_graph")
            
        Returns:
            SQLExecutionResult with rows, columns, metadata
        """
        import time
        
        # Select database path based on datasource
        if datasource == "p2p_data":
            db_path = self.p2p_data_db
        elif datasource == "p2p_graph":
            db_path = self.p2p_graph_db
        else:
            return SQLExecutionResult(
                success=False,
                rows=[],
                columns=[],
                row_count=0,
                execution_time_ms=0,
                error=f"Unknown datasource: {datasource}. Use 'p2p_data' or 'p2p_graph'."
            )
        
        # Validate query
        is_valid, error = self.validator.validate_query(sql)
        if not is_valid:
            return SQLExecutionResult(
                success=False,
                rows=[],
                columns=[],
                row_count=0,
                execution_time_ms=0,
                error=error
            )
        
        # Sanitize query (add LIMIT)
        sanitized_sql = self.validator.sanitize_query(sql, self.max_rows)
        
        warnings = []
        if sanitized_sql != sql.strip().rstrip(';'):
            warnings.append(f"Query modified to enforce LIMIT {self.max_rows}")
        
        # Execute query
        try:
            start_time = time.time()
            
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute(sanitized_sql)
                
                # Get column names
                columns = [desc[0] for desc in cursor.description]
                
                # Fetch all rows
                rows = []
                for row in cursor.fetchall():
                    rows.append(dict(row))
                
                execution_time_ms = (time.time() - start_time) * 1000
                
                return SQLExecutionResult(
                    success=True,
                    rows=rows,
                    columns=columns,
                    row_count=len(rows),
                    execution_time_ms=round(execution_time_ms, 2),
                    warnings=warnings if warnings else None
                )
                
        except sqlite3.Error as e:
            return SQLExecutionResult(
                success=False,
                rows=[],
                columns=[],
                row_count=0,
                execution_time_ms=0,
                error=f"SQL execution error: {str(e)}"
            )
        except Exception as e:
            return SQLExecutionResult(
                success=False,
                rows=[],
                columns=[],
                row_count=0,
                execution_time_ms=0,
                error=f"Unexpected error: {str(e)}"
            )


