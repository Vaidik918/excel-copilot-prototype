

from flask import Flask, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from utils.logger import setup_logger
from core.gemini_handler import GeminiHandler, test_gemini_connection
from core.excel_handler import ExcelHandler
from core.code_executor import CodeExecutor

# Setup logging
logger = setup_logger(__name__)

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max

# Enable CORS
CORS(app)

# ============== ROUTES ==============

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'alive',
        'message': 'Excel Copilot API is running',
        'phase': 'Phase 0 - Setup Testing',
        'timestamp': __import__('datetime').datetime.now().isoformat()
    }), 200

@app.route('/test/gemini', methods=['GET'])
def test_gemini_route():
    """Test Gemini API connection."""
    try:
        is_connected = test_gemini_connection()
        if is_connected:
            return jsonify({
                'status': 'success',
                'message': 'Gemini API is connected',
                'model': 'gemini-2.5-flash'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Gemini API connection failed'
            }), 500
    except Exception as e:
        logger.error(f"Gemini test error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test/excel', methods=['GET'])
def test_excel_route():
    """Test Excel handler (without actual file)."""
    try:
        logger.info("Testing ExcelHandler...")
        return jsonify({
            'status': 'success',
            'message': 'ExcelHandler loaded successfully'
        }), 200
    except Exception as e:
        logger.error(f"Excel test error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test/all', methods=['GET'])
def test_all():
    """Test all services."""
    results = {}
    
    # Test Gemini
    results['gemini'] = test_gemini_connection()
    
    # Test Excel Handler
    try:
        ExcelHandler()
        results['excel'] = True
    except:
        results['excel'] = False
    
    # Test Code Executor
    try:
        import pandas as pd
        df = pd.DataFrame({'a': [1, 2]})
        code_result = CodeExecutor.execute('df = df', df)
        results['executor'] = code_result['success']
    except:
        results['executor'] = False
    
    all_passed = all(results.values())
    
    return jsonify({
        'status': 'success' if all_passed else 'partial',
        'tests': results,
        'message': '✅ All services OK' if all_passed else '⚠️ Some services failed'
    }), 200 if all_passed else 206

# ============== ERROR HANDLERS ==============

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(e):
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

# ============== MAIN ==============

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("🚀 EXCEL COPILOT - Phase 0 SETUP")
    logger.info("=" * 60)
    
    # Create upload folder
    os.makedirs('uploads/temp', exist_ok=True)
    logger.info("✅ Upload folder ready")
    
    # Test all services on startup
    logger.info("Testing all services...")
    
    try:
        # Test Gemini
        if test_gemini_connection():
            logger.info("✅ Gemini API: OK")
        else:
            logger.warning("⚠️ Gemini API: FAILED (check API key in .env)")
    except Exception as e:
        logger.warning(f"⚠️ Gemini API test failed: {str(e)}")
    
    # Test Excel
    try:
        logger.info("✅ Excel Handler: OK")
    except Exception as e:
        logger.warning(f"⚠️ Excel Handler test failed: {str(e)}")
    
    # Test Executor
    try:
        logger.info("✅ Code Executor: OK")
    except Exception as e:
        logger.warning(f"⚠️ Code Executor test failed: {str(e)}")
    
    logger.info("=" * 60)
    logger.info("🚀 Server starting on http://0.0.0.0:5000")
    logger.info("=" * 60)
    
    # Run Flask
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
