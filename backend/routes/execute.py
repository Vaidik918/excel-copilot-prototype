"""
Code execution endpoint
Phase 1: Execute generated pandas code on Excel data
"""

from flask import Blueprint, request, jsonify
import pandas as pd
import io
from typing import Dict, Any
from core.excel_handler import ExcelHandler
from core.code_executor import CodeExecutor
from core.file_manager import FileManager
from utils.session_manager import session_manager
from utils.logger import setup_logger

logger = setup_logger(__name__)
execute_bp = Blueprint('execute', __name__, url_prefix='/api')

# Initialize services
code_executor = CodeExecutor()
file_manager = FileManager()
excel_handler = ExcelHandler()


@execute_bp.route('/execute', methods=['POST'])
def execute():
    """
    Execute generated pandas code on Excel data.
    
    Expected request:
    {
        'session_id': str,
        'file_id': str,
        'code': str (pandas code to execute),
        'confirm': bool (user confirmation for execution)
    }
    
    Returns:
    {
        'success': bool,
        'execution_id': str (for tracking),
        'rows_before': int,
        'rows_after': int,
        'columns_before': int,
        'columns_after': int,
        'changes': str (description of changes),
        'sample_before': [rows],
        'sample_after': [rows],
        'preview_data': {sheet_name: [rows]},
        'error': Error if failed
    }
    """
    try:
        logger.info("Execute endpoint called")
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        required_fields = ['session_id', 'file_id', 'code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        session_id = data['session_id']
        file_id = data['file_id']
        code = data['code']
        confirm = data.get('confirm', False)
        
        logger.info(f"Execute request: session={session_id[:8]}..., file={file_id}")
        
        # Get session
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Get file from session
        if file_id not in session['files']:
            return jsonify({'success': False, 'error': 'File not found in session'}), 404
        
        # Get original file bytes from FileManager
        file_info = session['files'][file_id]
        retrieved = file_manager.get_file(file_id, file_info['filename'])
        
        if not retrieved['success']:
            logger.error("Could not retrieve original file")
            return jsonify({
                'success': False,
                'error': 'Could not retrieve original file'
            }), 500
        
        # Load Excel into DataFrame
        original_bytes = retrieved['data']
        load_result = excel_handler.load_excel(original_bytes, file_info['filename'])
        
        if not load_result['success']:
            return jsonify({
                'success': False,
                'error': 'Could not load Excel file'
            }), 400
        
        # Get the sheet being worked on
        sheet_name = file_info['sheet_name']
        df = load_result['data'].get(sheet_name)
        
        if df is None:
            return jsonify({
                'success': False,
                'error': f'Sheet "{sheet_name}" not found'
            }), 400
        
        # Execute code
        execution_result = code_executor.execute(code, df)
        
        if not execution_result['success']:
            logger.warning(f"Execution failed: {execution_result['error']}")
            return jsonify({
                'success': False,
                'error': execution_result['error']
            }), 400
        
        # Get modified DataFrame
        modified_df = execution_result['df']
        
        # Generate execution ID for tracking
        import uuid
        execution_id = str(uuid.uuid4())[:8]
        
        # Save modified file
        modified_data = load_result['data'].copy()
        modified_data[sheet_name] = modified_df
        modified_bytes = excel_handler.save_excel(modified_data, f"{file_id}_modified.xlsx")
        
        # Save to FileManager (keep original, save modified separately)
        save_result = file_manager.save_processed_file(
            modified_bytes,
            file_id,
            f"{file_id}_modified.xlsx"
        )
        
        if not save_result['success']:
            logger.warning(f"Could not save modified file: {save_result['error']}")
        
        # Update session with execution result
        session_manager.sessions[session_id]['files'][file_id]['last_execution'] = {
            'execution_id': execution_id,
            'code': code,
            'result': execution_result,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        # Record operation
        session_manager.record_operation(session_id, {
            'type': 'execute',
            'file_id': file_id,
            'execution_id': execution_id,
            'code': code[:100],  # First 100 chars
            'changes': execution_result['changes']
        })
        
        # Prepare preview data (first 5 rows)
        preview_data = {
            sheet_name: modified_df.head(5).to_dict('records')
        }
        
        logger.info(f"✅ Execution successful: {execution_id}")
        
        return jsonify({
            'success': True,
            'execution_id': execution_id,
            'rows_before': execution_result['rows_before'],
            'rows_after': execution_result['rows_after'],
            'columns_before': execution_result['columns_before'],
            'columns_after': execution_result['columns_after'],
            'row_change': execution_result.get('row_change', 0),
            'column_change': execution_result.get('column_change', 0),
            'changes': execution_result['changes'],
            'sample_before': execution_result.get('sample_before', []),
            'sample_after': execution_result.get('sample_after', []),
            'preview_data': preview_data
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Execute error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Execution failed: {str(e)}'
        }), 500


@execute_bp.route('/execute/preview', methods=['POST'])
def execute_preview():
    """
    Preview execution without saving (dry run).
    Same as /execute but doesn't save the file.
    
    Expected request:
    {
        'session_id': str,
        'file_id': str,
        'code': str
    }
    """
    try:
        logger.info("Execute preview requested")
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data provided'}), 400
        
        required_fields = ['session_id', 'file_id', 'code']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        session_id = data['session_id']
        file_id = data['file_id']
        code = data['code']
        
        # Get session
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        # Get file from session
        if file_id not in session['files']:
            return jsonify({'success': False, 'error': 'File not found in session'}), 404
        
        file_info = session['files'][file_id]
        retrieved = file_manager.get_file(file_id, file_info['filename'])
        
        if not retrieved['success']:
            return jsonify({'success': False, 'error': 'Could not retrieve file'}), 500
        
        # Load Excel
        load_result = excel_handler.load_excel(retrieved['data'], file_info['filename'])
        if not load_result['success']:
            return jsonify({'success': False, 'error': 'Could not load file'}), 400
        
        # Get DataFrame
        sheet_name = file_info['sheet_name']
        df = load_result['data'].get(sheet_name)
        if df is None:
            return jsonify({'success': False, 'error': f'Sheet "{sheet_name}" not found'}), 400
        
        # Execute code (preview only, no save)
        execution_result = code_executor.execute(code, df)
        
        if not execution_result['success']:
            return jsonify({
                'success': False,
                'error': execution_result['error']
            }), 400
        
        logger.info("✅ Preview successful")
        
        return jsonify({
            'success': True,
            'is_preview': True,
            'rows_before': execution_result['rows_before'],
            'rows_after': execution_result['rows_after'],
            'columns_before': execution_result['columns_before'],
            'columns_after': execution_result['columns_after'],
            'changes': execution_result['changes'],
            'sample_before': execution_result.get('sample_before', []),
            'sample_after': execution_result.get('sample_after', []),
            'preview_data': {
                sheet_name: execution_result['df'].head(5).to_dict('records')
            }
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Preview error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Preview failed: {str(e)}'
        }), 500
