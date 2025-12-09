"""
Code analysis endpoint
Phase 1: Generate pandas code from user prompts
"""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
from core.gemini_handler import GeminiHandler
from core.code_executor import CodeExecutor
from utils.session_manager import session_manager
from utils.logger import setup_logger

logger = setup_logger(__name__)
analyze_bp = Blueprint('analyze', __name__, url_prefix='/api')

# Initialize services
gemini_handler = GeminiHandler()
executor = CodeExecutor()


@analyze_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Analyze user prompt and generate pandas code.
    
    Expected request:
    {
        'session_id': str,
        'file_id': str,
        'sheet_name': str (optional),
        'prompt': str (user instruction)
    }
    """
    try:
        logger.info("Analyze endpoint called")
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        required_fields = ['session_id', 'file_id', 'prompt']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'Missing required field: {field}'}), 400
        
        session_id = data['session_id']
        file_id = data['file_id']
        sheet_name = data.get('sheet_name', None)
        prompt = data['prompt']
        
        logger.info(f"Analyzing prompt: {prompt[:50]}...")
        
        # Get session
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Get file from session
        if file_id not in session['files']:
            return jsonify({'success': False, 'error': 'File not found in session'}), 404
        
        # Get DataFrame info
        file_info = session['files'][file_id]
        dataframe_info = file_info.get('dataframe_info')
        if not dataframe_info:
            return jsonify({'success': False, 'error': 'DataFrame info not available'}), 400
        
        # Generate code with Gemini
        gen_result = gemini_handler.generate_code(prompt, dataframe_info, sheet_name or 'Sheet1')
        
        if not gen_result['success']:
            return jsonify({
                'success': False,
                'error': gen_result['error']
            }), 400
        
        code = gen_result['code']
        
        # Validate code syntax
        code_validation = GeminiHandler.validate_code(code)
        
        # Safety check
        is_safe, safety_msg = executor.validate_code_safety(code)
        safety_risks = [safety_msg] if not is_safe else []
        
        # Combine risks
        all_risks = gen_result.get('risks', []) + safety_risks
        
        # Store code in session
        if session_id in session_manager.sessions:
            session_manager.sessions[session_id]['files'][file_id]['last_code'] = code
        
        # Record operation
        session_manager.record_operation(session_id, {
            'type': 'analyze',
            'file_id': file_id,
            'prompt': prompt,
            'code_generated': True
        })
        
        logger.info(f"✅ Analysis complete: {len(code)} chars generated")
        
        return jsonify({
            'success': True,
            'code': code,
            'explanation': gen_result.get('explanation', 'N/A'),
            'risks': all_risks,
            'estimated_rows_affected': gen_result.get('estimated_rows_affected', 'unknown'),
            'code_valid': code_validation['valid'],
            'is_safe': is_safe
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Analyze error: {str(e)}")
        return jsonify({'success': False, 'error': f'Analysis failed: {str(e)}'}), 500
