"""
Log Module Backend
==================
Dual-mode logging system with REST API endpoints.

Exports:
    - logger_api: Flask Blueprint for /api/log endpoints

Author: P2P Development Team
Version: 1.0.0
"""

from flask import Blueprint

# Create Flask Blueprint (this is what gets registered with Flask app)
logger_api = Blueprint('log', __name__)

# Import routes to register them with the blueprint
# This must come after blueprint creation
from modules.log.backend import api

__all__ = ['logger_api']