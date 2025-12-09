"""
File upload endpoint
Phase 1: Handle Excel file uploads with validation
"""

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import io
from typing import Dict, Any
from core.excel_handler import ExcelHandler
from core.file_manager import FileManager
from utils.session_manager import session_manager
from utils.logger import setup_logger

logger = setup_logger(__name__)
upload_bp = Blueprint('upload', __name__, url_prefix='/api')

# Initialize services
file_manager = FileManager()
excel_handler = ExcelHandler()


@upload_bp.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload and load Excel file.
    
    Expected request:
    - Method: POST
    - Content-Type: multipart/form-data
    - Body:
      - file: Excel file (.xlsx or .xls)
      - session_id: (optional) Existing session ID
    
    Returns:
    {
        'success': bool,
        'session_id': str,
        'file_id': str,
        'metadata': {
            'filename': str,
            'total_rows': int,
            'total_columns': int,
            'total_sheets': int,
            'sheet_info': {...}
        },
        'sheets': [sheet names],
        'error': Error message if failed
    }
    """
    try:
        logger.info("Upload endpoint called")
        
        # Validate request
        if 'file' not in request.files:
            logger.warning("No file in request")
            return jsonify({
                'success': False,
                'error': 'No file provided'
            }), 400
        
        file = request.files['file']
        
        if not file:
            logger.warning("Empty file object")
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        filename = file.filename
        if not filename:
            logger.warning("Empty filename")
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Read file bytes
        file_bytes = file.read()
        
        if len(file_bytes) == 0:
            logger.warning("Empty file content")
            return jsonify({
                'success': False,
                'error': 'File is empty'
            }), 400
        
        # Validate file extension
        allowed_extensions = {'xlsx', 'xls'}
        file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        
        if file_ext not in allowed_extensions:
            logger.warning(f"Invalid file extension: {file_ext}")
            return jsonify({
                'success': False,
                'error': f'Invalid file type. Allowed: {allowed_extensions}'
            }), 400
        
        logger.info(f"File received: {filename} ({len(file_bytes)} bytes)")
        
        # Validate Excel file
        validation = excel_handler.validate_file(file_bytes, filename)
        if not validation['valid']:
            logger.warning(f"Validation failed: {validation['error']}")
            return jsonify({
                'success': False,
                'error': validation['error']
            }), 400
        
        # Load Excel
        load_result = excel_handler.load_excel(file_bytes, filename)
        if not load_result['success']:
            logger.error(f"Load failed: {load_result['error']}")
            return jsonify({
                'success': False,
                'error': load_result['error']
            }), 400
        
        # Get or create session
        session_id = request.form.get('session_id')
        if not session_id:
            session_id = session_manager.create_session()
        
        # Save file with FileManager
        save_result = file_manager.save_upload(file_bytes, filename)
        if not save_result['success']:
            logger.error(f"File save failed: {save_result['error']}")
            return jsonify({
                'success': False,
                'error': save_result['error']
            }), 500
        
        file_id = save_result['file_id']
        
        # Add to session (use first sheet as default)
        sheet_name = load_result['sheets'][0] if load_result['sheets'] else 'Sheet1'
        session_manager.add_file(session_id, file_id, filename, sheet_name)
        
        # Store DataFrame metadata
        session_manager.update_dataframe_info(session_id, file_id, load_result['metadata'])
        
        # Record operation
        session_manager.record_operation(session_id, {
            'type': 'upload',
            'file_id': file_id,
            'filename': filename,
            'sheets': load_result['sheets']
        })
        
        logger.info(f"✅ Upload successful: session={session_id}, file={file_id}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'file_id': file_id,
            'metadata': load_result['metadata'],
            'sheets': load_result['sheets']
        }), 200
    
    except Exception as e:
        logger.error(f"❌ Upload error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500


@upload_bp.route('/session/create', methods=['POST'])
def create_session():
    """
    Create new session.
    
    Returns:
    {
        'success': bool,
        'session_id': str
    }
    """
    try:
        session_id = session_manager.create_session()
        logger.info(f"✅ Session created: {session_id}")
        return jsonify({
            'success': True,
            'session_id': session_id
        }), 200
    
    except Exception as e:
        logger.error(f"Session creation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@upload_bp.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    """
    Get session information.
    
    Returns:
    {
        'success': bool,
        'session': Session data,
        'error': Error if not found
    }
    """
    try:
        session = session_manager.get_session(session_id)
        if not session:
            logger.warning(f"Session not found: {session_id}")
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        logger.info(f"✅ Session retrieved: {session_id}")
        return jsonify({
            'success': True,
            'session': session
        }), 200
    
    except Exception as e:
        logger.error(f"Get session error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
