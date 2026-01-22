#!/usr/bin/env python3
"""
P2P Data Products - Flask Server Launcher
==========================================
Simple script to start the Flask backend server from project root.

Usage:
    python server.py

The server will start on http://localhost:5000
"""

import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import and run the Flask app
from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("P2P Data Products - Flask Backend Server")
    print("=" * 60)
    print()
    print("Starting server...")
    print("Server will be available at: http://localhost:5000")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    print()
    
    # Run the app
    app.run(host='0.0.0.0', port=5000, debug=True)
