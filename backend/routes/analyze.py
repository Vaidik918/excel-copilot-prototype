"""
Code analysis endpoint
Phase 1: Generate pandas code from user prompts
"""

from flask import Blueprint, request, jsonify
from core.gemini_handler import GeminiHandler
from core.code_executor import CodeExecutor
from utils.session_manager import session_manager
from utils.logger import setup_logger

logger = setup_logger(__name__)
analyze_bp = Blueprint('analyze', __name__, url_prefix='/api')

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
        'sheet_name': str (optional, defaults to first sheet),
        'prompt': str (user instruction)
    }
    
    Returns:
    {
        'success': bool,
        'code': Generated pandas code,
        'explanation': What will happen,
        'risks': [Risk warnings],
        'estimated_rows_affected': Estimate,
        'code_valid': bool (syntax check),
        'error': Error if failed
    }
    """
    try:
        logger.info("Analyze endpoint called")
        
        # Get request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['session_id', 'file_id', 'prompt']
        for field in required_fields:
            if not data.get(field):
                logger.warning(f"Missing field: {field}")
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        session_id = data['session_id']
        file_id = data['file_id']
        sheet_name = data.get('sheet_name', None)
        prompt = data['prompt']
        
        logger.info(f"Analyzing prompt: {prompt[:50]}...")
        
        # Get session
        session = session_manager.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        # Get file from session
        if file_id not in session['files']:
            logger.warning(f"File not in session: {file_id}")
            return jsonify({
                'success': False,
                'error': 'File not found in session'
            }), 404
        
        # Get DataFrame info
        dataframe_info = session['files'][file_id]['dataframe_info']
        if not dataframe_info:
            return jsonify({
                'success': False,
                'error': 'DataFrame info not available'
            }), 400
        
        # Use provided sheet or default
        if not sheet_name:
            sheet_name = dataframe_info.get('sheets', ['Sheet1'])[0]
        
        # Generate code
        gen_result = gemini_handler.generate_code(prompt, dataframe_info, sheet_name)
        
        if not gen_result['success']:
            logger.warning(f"Code generation failed: {gen_result['error']}")
            return jsonify({
                'success': False,
                'error': gen_result['error']
            }), 400
        
        code = gen_result['code']
        
        # SECURITY FIX: Strip any import statements from generated code
        # Imports are disabled for security, all needed imports are pre-loaded in executor
        lines = code.split('\n')
        filtered_lines = [
            line for line in lines 
            if not line.strip().startswith('import ') and not line.strip().startswith('from ')
        ]
        code = '\n'.join(filtered_lines).strip()
        
        logger.info(f"Code after security filtering: {len(code)} chars")
        
        # Validate code syntax
        code_validation = GeminiHandler.validate_code(code)
        
        # Check for forbidden patterns (safety)
        safety_check = CodeExecutor.validate_code_safety(code)
        is_safe = safety_check[0]
        
        if not is_safe:
            safety_risks = [safety_check[1]]
        else:
            safety_risks = []
        
        # Combine risks
        all_risks = gen_result.get('risks', []) + safety_risks
        
        # Record operation
        session_manager.record_operation(session_id, {
            'type': 'analyze',
            'file_id': file_id,
            'prompt': prompt,
            'code_generated': True
        })
        
        # Store code in session for later execution
        session_manager.sessions[session_id]['files'][file_id]['last_code'] = code
        
        logger.info(f"✅ Analysis complete: {len(code)} chars of code generated")
        
        return jsonify({
            'success': True,
            'code': code,
            'explanation': gen_result.get('explanation', 'N/A'),
            'risks': all_risks,
            'estimated_rows_affected': gen_result.get('estimated_rows_affected', 'unknown'),
            'code_valid': code_validation['valid'],
            'code_syntax_error': code_validation.get('error', None) if not code_validation['valid'] else None,
            'is_safe': is_safe,
            'safety_warning': safety_check[1] if not is_safe else None
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Analyze error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Analysis failed: {str(e)}'
        }), 500