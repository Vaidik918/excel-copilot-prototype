from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# Enable CORS
CORS(app)

# Simple health check route
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'alive',
        'message': 'Excel Copilot API is running',
        'phase': 'Phase 0 - Setup Testing'
    }), 200

# Simple test route
@app.route('/test', methods=['GET'])
def test():
    return jsonify({
        'status': 'success',
        'message': 'All basic imports working'
    }), 200

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 EXCEL COPILOT - Phase 0 Starting...")
    print("=" * 50)
    
    # Create upload folder if not exists
    os.makedirs('uploads/temp', exist_ok=True)
    print("✅ Upload folder ready")
    
    # Run Flask
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )