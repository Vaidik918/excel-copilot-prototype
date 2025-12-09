from flask import Blueprint, request, jsonify, send_file
from core.file_manager import FileManager
from utils.session_manager import session_manager
from utils.logger import setup_logger
import io
import os

logger = setup_logger(__name__)
download_bp = Blueprint('download', __name__, url_prefix='/api')

file_manager = FileManager()


@download_bp.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Download file (modified by default, original if specified)."""
    try:
        logger.info(f"Download endpoint called: file={file_id}")
        
        session_id = request.args.get('session_id')
        version = request.args.get('version', 'modified')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Missing session_id'}), 400
        
        if version not in ['original', 'modified']:
            return jsonify({'success': False, 'error': "version must be 'original' or 'modified'"}), 400
        
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        if file_id not in session['files']:
            return jsonify({'success': False, 'error': 'File not found in session'}), 404
        
        file_info = session['files'][file_id]
        original_filename = file_info['filename']
        
        # Determine which file to get
        if version == 'original':
            # Original file - need file_id and filename
            filename_in_storage = original_filename
            download_name = f"original_{original_filename}"
        else:
            # Modified file
            filename_in_storage = f"{file_id}_modified.xlsx"
            download_name = f"modified_{original_filename}"
        
        logger.info(f"Downloading {version}: {file_id}/{filename_in_storage}")
        
        # FIXED: Use correct signature - get_file(file_id, filename)
        retrieval = file_manager.get_file(file_id, filename_in_storage)
        if not retrieval['success']:
            logger.error(f"File retrieval failed: {retrieval['error']}")
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # FIXED: data is returned in retrieval['data'], not file_bytes
        file_bytes = retrieval['data']
        
        session_manager.record_operation(session_id, {
            'type': 'download',
            'file_id': file_id,
            'version': version
        })
        
        logger.info(f"✅ Download successful: {download_name}")
        
        return send_file(
            io.BytesIO(file_bytes),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=download_name
        )
    
    except Exception as e:
        logger.error(f"❌ Download error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@download_bp.route('/download/session/<session_id>/files', methods=['GET'])
def list_session_files(session_id):
    """List all files in a session."""
    try:
        logger.info(f"List session files: {session_id}")
        
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        files_list = []
        for file_id, file_info in session['files'].items():
            files_list.append({
                'file_id': file_id,
                'filename': file_info['filename'],
                'added_at': file_info['added_at'],
                'sheet_name': file_info['sheet_name'],
                'has_modified': file_info.get('last_code') is not None,
                'versions': ['original'] + (['modified'] if file_info.get('last_code') else [])
            })
        
        logger.info(f"✅ Listed {len(files_list)} files")
        return jsonify({
            'success': True,
            'session_id': session_id,
            'files': files_list
        })
    
    except Exception as e:
        logger.error(f"❌ List files error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@download_bp.route('/download/<file_id>/revert', methods=['POST'])
def revert_to_original(file_id):
    """Revert file to original state (no actual delete needed for temp files)."""
    try:
        data = request.get_json()
        if not data or 'session_id' not in data:
            return jsonify({'success': False, 'error': 'Missing session_id'}), 400
        
        session_id = data['session_id']
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        if file_id not in session['files']:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Clear session state (modified flag)
        session['files'][file_id]['last_code'] = None
        
        # Note: We don't actually delete files from disk since they're in temp storage
        # and will be cleaned up by session cleanup
        
        session_manager.record_operation(session_id, {'type': 'revert', 'file_id': file_id})
        
        logger.info(f"✅ Reverted to original: {file_id}")
        return jsonify({'success': True, 'message': 'Reverted to original'})
    
    except Exception as e:
        logger.error(f"❌ Revert error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500