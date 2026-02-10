"""
SQL Execution Module
===================
SQL query execution engine with history tracking and execution analysis.

Quick Start:
    from modules.sql_execution.frontend.sqlExecutionAPI import SQLExecutionAPI
    
    # Create API instance
    api = SQLExecutionAPI()
    
    # Execute query
    result = await api.executeQuery(
        instanceId='my-instance',
        sql='SELECT * FROM TABLE',
        options={'maxRows': 100}
    )
    
    # Check result
    if result.success:
        print(f"Rows: {result.rowCount}")
        print(f"Time: {result.executionTime}ms")

Features:
- Execute SQL queries against HANA instances
- Batch query execution
- Query history with filtering
- Execution plan analysis
- Active query monitoring
- Query cancellation support
- Automatic query type detection
- Simulated mode for testing

Author: P2P Development Team
Version: 1.0.0
"""

__version__ = '1.0.0'