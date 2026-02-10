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

# Load environment variables from app/.env
from dotenv import load_dotenv
app_dir = os.path.join(os.path.dirname(__file__), 'app')
env_path = os.path.join(app_dir, '.env')
load_dotenv(env_path)

# Add app directory to Python path
sys.path.insert(0, app_dir)

# Import and run the Flask app
from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("P2P Data Products - Flask Application Server")
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