"""
Test Server for API Playground

Serves the API Playground UI and provides discovery endpoint.
This also registers the Feature Manager API so it can be tested.

Run with: python test_api_playground.py
Then open: http://localhost:5002/playground
"""

from flask import Flask, send_file, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import modules using direct paths
sys.path.insert(0, str(Path(__file__).parent / 'modules' / 'api-playground' / 'backend'))
sys.path.insert(0, str(Path(__file__).parent / 'modules' / 'feature-manager' / 'backend'))

from playground_service import PlaygroundService
from api import api as feature_manager_api
from feature_flags import FeatureFlags

# Create Flask app
app = Flask(__name__)
CORS(app)

# Register Feature Manager API (so we can test it!)
app.register_blueprint(feature_manager_api)

# Initialize playground service
playground = PlaygroundService()


@app.route('/playground')
def serve_playground():
    """Serve the API Playground HTML interface."""
    html_path = Path(__file__).parent / 'modules' / 'api-playground' / 'templates' / 'playground.html'
    return send_file(html_path)


@app.route('/api/playground/discover')
def discover_apis():
    """
    Discover all module APIs.
    
    Returns JSON with discovered APIs and statistics.
    """
    try:
        apis = playground.get_all_apis()
        stats = playground.get_summary_stats()
        
        return jsonify({
            'success': True,
            'apis': apis,
            'stats': stats
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/')
def home():
    """Redirect to playground."""
    return """
    <html>
    <head><title>API Playground Server</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🎯 API Playground Server</h1>
        <p>Universal API testing tool is running!</p>
        <p><a href="/playground" style="font-size: 20px; color: #0070f2;">Open API Playground →</a></p>
        <hr style="margin: 40px auto; width: 200px;">
        <p style="color: #666;">
            Auto-discovered: {} module(s) with {} endpoint(s)
        </p>
    </body>
    </html>
    """.format(
        len(playground.get_all_apis()),
        playground.get_endpoint_count()
    )


if __name__ == '__main__':
    print("=" * 60)
    print("🎯 API PLAYGROUND SERVER")
    print("=" * 60)
    print()
    print("✅ Server starting...")
    print()
    print("📍 Open API Playground: http://localhost:5002/playground")
    print("📍 Home page: http://localhost:5002")
    print()
    print("🔧 Discovered APIs:")
    for module_name, config in playground.get_all_apis().items():
        print(f"   - {config['displayName']}: {len(config['endpoints'])} endpoints")
    print()
    print("⏹️  Press CTRL+C to stop")
    print()
    print("=" * 60)
    print()
    
    # Run server
    app.run(debug=True, port=5002, host='0.0.0.0')