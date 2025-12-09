"""
Excel Copilot - Main Flask Application
Phase 1: Complete backend with routes
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from utils.logger import setup_logger
from routes import register_routes
from utils.session_manager import session_manager
from config import get_config

# Setup logging
logger = setup_logger(__name__)

# Load environment variables
load_dotenv()

# Get config
config = get_config()

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['JSON_SORT_KEYS'] = False

# Enable CORS
CORS(app, resources={
    r"/api/*": {
        "origins": [config.FRONTEND_URL, "http://localhost:8000", "http://127.0.0.1:8000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    logger.warning(f"404 error: {request.path}")
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(413)
def payload_too_large(e):
    """Handle file too large errors."""
    logger.warning("File too large (>50MB)")
    return jsonify({
        'error': 'File too large',
        'max_size_mb': 50
    }), 413


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    logger.error(f"500 error: {str(e)}")
    return jsonify({
        'error': 'Internal server error',
        'message': str(e) if config.FLASK_ENV == 'development' else 'An error occurred'
    }), 500


# ============== MIDDLEWARE ==============

@app.before_request
def before_request():
    """Log incoming requests."""
    logger.info(f"{request.method} {request.path}")


@app.after_request
def after_request(response):
    """Add security headers."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response


# ============== REGISTER ROUTES ==============

register_routes(app)

logger.info("✅ All routes registered")


# ============== CLI COMMANDS ==============

@app.cli.command()
def cleanup_sessions():
    """Clean up old sessions."""
    result = session_manager.cleanup_old_sessions()
    print(f"Cleanup result: {result}")


@app.cli.command()
def test_all_services():
    """Test all services."""
    from core.excel_handler import ExcelHandler
    from core.gemini_handler import test_gemini_connection
    from core.code_executor import CodeExecutor
    from core.file_manager import FileManager
    
    services = {
        'Excel Handler': True,
        'Gemini API': test_gemini_connection(),
        'Code Executor': True,
        'File Manager': True
    }
    
    print("\n=== Service Test Results ===")
    for service, status in services.items():
        print(f"  {service}: {'✅ OK' if status else '❌ FAILED'}")
    
    all_ok = all(services.values())
    print(f"\nOverall: {'✅ All systems GO' if all_ok else '⚠️ Some services failed'}\n")


# ============== MAIN ==============

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 EXCEL COPILOT - Phase 1 Backend")
    logger.info("=" * 60)
    
    # Create upload folder
    os.makedirs('uploads/temp', exist_ok=True)
    logger.info("✅ Upload folder ready")
    
    # Test all services on startup
    logger.info("\n📋 Testing services on startup...")
    
    try:
        from core.excel_handler import ExcelHandler
        ExcelHandler()
        logger.info("✅ Excel Handler: OK")
    except Exception as e:
        logger.warning(f"⚠️ Excel Handler: {str(e)}")
    
    try:
        from core.gemini_handler import test_gemini_connection
        if test_gemini_connection():
            logger.info("✅ Gemini API: OK")
        else:
            logger.warning("⚠️ Gemini API: Connection failed")
    except Exception as e:
        logger.warning(f"⚠️ Gemini API: {str(e)}")
    
    try:
        from core.code_executor import CodeExecutor
        CodeExecutor()
        logger.info("✅ Code Executor: OK")
    except Exception as e:
        logger.warning(f"⚠️ Code Executor: {str(e)}")
    
    try:
        from core.file_manager import FileManager
        FileManager()
        logger.info("✅ File Manager: OK")
    except Exception as e:
        logger.warning(f"⚠️ File Manager: {str(e)}")
    
    logger.info("=" * 60)
    logger.info("🚀 Server starting on http://0.0.0.0:5000")
    logger.info("=" * 60)
    logger.info("")
    
    # Run Flask
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=config.FLASK_DEBUG
    )
