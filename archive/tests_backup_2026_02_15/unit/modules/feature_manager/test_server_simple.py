"""
Simple Test Server for Feature Manager

Run with: python test_server_simple.py
Then open: http://localhost:5001
"""

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import sys
from pathlib import Path
import pytest

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

# Import directly
sys.path.insert(0, str(Path(__file__).parent / 'modules' / 'feature-manager' / 'backend'))
from feature_flags import FeatureFlags

# Create Flask app
app = Flask(__name__)
CORS(app)

# Initialize feature flags
ff = FeatureFlags()


@app.route('/configurator')
def serve_configurator():
    """Serve the Feature Manager Configurator UI."""
    html_path = Path(__file__).parent / 'modules' / 'feature-manager' / 'templates' / 'configurator_simple.html'
    return send_file(html_path)


@app.route('/')
def home():
    """Home page with test buttons."""
    return """
    <html>
    <head>
        <title>Feature Manager Test</title>
        <style>
            body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
            h1 { color: #0070f2; }
            button { background: #0070f2; color: white; border: none; padding: 10px 20px; 
                     cursor: pointer; border-radius: 5px; margin: 5px; }
            button:hover { background: #0056b3; }
            .output { background: #f5f5f5; padding: 15px; margin: 20px 0; border: 1px solid #ddd; 
                      min-height: 100px; white-space: pre-wrap; font-family: monospace; }
        </style>
    </head>
    <body>
        <h1>🎯 Feature Manager Test Server</h1>
        <p>Server running on <strong>http://localhost:5001</strong></p>
        
        <h2>Test API Endpoints:</h2>
        <button onclick="test('GET', '/api/features')">Get All Features</button>
        <button onclick="test('POST', '/api/features/application-logging/toggle')">Toggle Logging</button>
        <button onclick="test('GET', '/api/features/export')">Export Config</button>
        <button onclick="test('POST', '/api/features/reset')">Reset to Defaults</button>
        
        <h2>Output:</h2>
        <div class="output" id="output">Click a button to test...</div>
        
        <script>
            async function test(method, url) {
                const output = document.getElementById('output');
                output.textContent = 'Loading...';
                
                try {
                    const response = await fetch(url, { method });
                    const data = await response.json();
                    output.textContent = `${method} ${url}\\n\\nStatus: ${response.status}\\n\\n${JSON.stringify(data, null, 2)}`;
                } catch (error) {
                    output.textContent = 'Error: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    """


@app.route('/api/features', methods=['GET'])
def get_all():
    """Get all features."""
    try:
        features = ff.get_all()
        return jsonify({'success': True, 'count': len(features), 'features': features}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/features/<name>', methods=['GET'])
def get_feature(name):
    """Get specific feature."""
    try:
        feature = ff.get(name)
        if feature:
            return jsonify({'success': True, 'feature': feature}), 200
        return jsonify({'success': False, 'error': f'Feature not found: {name}'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/features/<name>/toggle', methods=['POST'])
def toggle(name):
    """Toggle a feature."""
    try:
        new_state = ff.toggle(name)
        if new_state is not None:
            return jsonify({'success': True, 'message': f'Feature toggled: {name}', 'enabled': new_state, 'feature': ff.get(name)}), 200
        return jsonify({'success': False, 'error': f'Feature not found: {name}'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/features/export', methods=['GET'])
def export():
    """Export configuration."""
    try:
        config = ff.export_config()
        return jsonify({'success': True, 'config': config}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/features/reset', methods=['POST'])
def reset():
    """Reset to defaults."""
    try:
        success = ff.reset_to_defaults()
        return jsonify({'success': success, 'count': ff.get_feature_count()}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("🎯 FEATURE MANAGER TEST SERVER")
    print("=" * 60)
    print("\n✅ Server starting...")
    print("\n📍 Open in browser: http://localhost:5001")
    print("\n🔧 Test the API with the buttons on the page!")
    print("\n⏹️  Press CTRL+C to stop\n")
    print("=" * 60 + "\n")
    
    app.run(debug=True, port=5001, host='0.0.0.0')