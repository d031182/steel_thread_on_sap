#!/usr/bin/env python3
"""
Frontend Build & Deployment Script
===================================

Automatically discovers modules with frontend assets and deploys them
to app/static/modules/ based on module.json configuration.

This script can be run standalone or is automatically executed on server startup.

Usage:
    python scripts/build_frontend.py

Features:
    - Clean slate deployment (removes old, deploys enabled)
    - Detailed logging output
    - Exit code 0 on success, 1 on failure

@author P2P Development Team
@version 1.0.0
"""

import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from flask import Flask
from core.services.module_loader import ModuleLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

logger = logging.getLogger(__name__)


def build_frontend():
    """
    Build and deploy all frontend assets
    
    Returns:
        int: Exit code (0 = success, 1 = failure)
    """
    try:
        logger.info("=" * 60)
        logger.info("FRONTEND BUILD & DEPLOYMENT")
        logger.info("=" * 60)
        
        # Create Flask app (needed for ModuleLoader initialization)
        app = Flask(__name__)
        loader = ModuleLoader(app)
        
        # Deploy frontend assets
        deployed = loader.deploy_frontend_assets()
        
        logger.info("=" * 60)
        logger.info(f"✓ Deployment complete: {deployed} module(s)")
        logger.info("=" * 60)
        
        if deployed == 0:
            logger.warning("No modules deployed. Check module.json configurations.")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"✗ Deployment failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit_code = build_frontend()
    sys.exit(exit_code)