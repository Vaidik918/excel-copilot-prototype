"""
Health check endpoint
Phase 1: Basic status reporting
"""

from flask import Blueprint, jsonify
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)
health_bp = Blueprint('health', __name__, url_prefix='')

@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint.
    
    Returns:
        {
            'status': 'alive',
            'message': str,
            'timestamp': ISO datetime,
            'phase': str,
            'version': str
        }
    """
    try:
        logger.info("Health check requested")
        
        return jsonify({
            'status': 'alive',
            'message': 'Excel Copilot API is running',
            'timestamp': datetime.now().isoformat(),
            'phase': 'Phase 1 - Backend Engine',
            'version': '1.0.0-beta'
        }), 200
    
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@health_bp.route('/test/services', methods=['GET'])
def test_services():
    """
    Test all backend services.
    
    Returns:
        {
            'status': 'ok' | 'degraded' | 'error',
            'services': {
                'excel_handler': bool,
                'gemini_api': bool,
                'code_executor': bool,
                'file_manager': bool
            }
        }
    """
    try:
        logger.info("Service test requested")
        
        services = {}
        
        # Test Excel Handler
        try:
            from core.excel_handler import ExcelHandler
            ExcelHandler()
            services['excel_handler'] = True
        except Exception as e:
            logger.warning(f"Excel handler test failed: {str(e)}")
            services['excel_handler'] = False
        
        # Test Gemini API
        try:
            from core.gemini_handler import test_gemini_connection
            services['gemini_api'] = test_gemini_connection()
        except Exception as e:
            logger.warning(f"Gemini test failed: {str(e)}")
            services['gemini_api'] = False
        
        # Test Code Executor
        try:
            from core.code_executor import CodeExecutor
            CodeExecutor()
            services['code_executor'] = True
        except Exception as e:
            logger.warning(f"Code executor test failed: {str(e)}")
            services['code_executor'] = False
        
        # Test File Manager
        try:
            from core.file_manager import FileManager
            FileManager()
            services['file_manager'] = True
        except Exception as e:
            logger.warning(f"File manager test failed: {str(e)}")
            services['file_manager'] = False
        
        # Determine overall status
        all_passed = all(services.values())
        status = 'ok' if all_passed else ('degraded' if any(services.values()) else 'error')
        
        return jsonify({
            'status': status,
            'services': services
        }), 200
    
    except Exception as e:
        logger.error(f"Service test error: {str(e)}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
