#!/usr/bin/env python3
"""
Flask Backend Quick Start Script
=================================
Installs dependencies and starts the Flask server.

Usage:
    python run.py
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    print("🚀 P2P Data Products Flask Backend - Quick Start")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8+ required")
        print(f"   Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✓ Python version: {sys.version.split()[0]}")
    
    # Check if requirements are installed
    try:
        import flask
        import flask_cors
        from hdbcli import dbapi
        from dotenv import load_dotenv
        print("✓ Dependencies already installed")
    except ImportError:
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed")
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check HANA configuration
    hana_host = os.getenv('HANA_HOST')
    hana_user = os.getenv('HANA_USER')
    hana_password = os.getenv('HANA_PASSWORD')
    
    if not all([hana_host, hana_user, hana_password]):
        print("⚠️  WARNING: HANA connection not fully configured")
        print("   Please set HANA_HOST, HANA_USER, HANA_PASSWORD in .env file")
    else:
        print(f"✓ HANA configured: {hana_user}@{hana_host}")
    
    print("\n" + "=" * 60)
    print("🌐 Starting Flask server...")
    print("📱 Access application at: http://localhost:5000")
    print("📊 API endpoints at: http://localhost:5000/api/*")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    # Start Flask app
    os.system(f"{sys.executable} app.py")

if __name__ == '__main__':
    main()
