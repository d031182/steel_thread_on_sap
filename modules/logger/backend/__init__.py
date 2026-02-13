"""
Logger Backend Module
====================
Backend services for dual-mode logging system
"""

from flask import Blueprint

# Create Flask blueprint
logger_api = Blueprint('logger', __name__)

# Import routes to register them
from . import api

__all__ = ['logger_api']