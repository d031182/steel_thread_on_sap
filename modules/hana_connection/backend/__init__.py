"""
HANA Connection Module
======================
SAP HANA Cloud connection management with pooling and query execution.

Exports:
    - HANAConnection: Core connection manager
    - HANADataSource: DataSource interface implementation
"""

from .hana_connection import HANAConnection
# HANADataSource removed - use core.repositories.HANARepository instead

__all__ = ['HANAConnection', 'HANADataSource']