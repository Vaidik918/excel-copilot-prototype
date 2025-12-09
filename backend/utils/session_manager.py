"""
Session management for file uploads and processing
Phase 1: Track user sessions and associated files
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from utils.logger import setup_logger
import json

logger = setup_logger(__name__)


class SessionManager:
    """
    Manage user sessions and track files.
    
    In production, this would use Redis/database.
    For now, we use in-memory dict (single process only).
    """
    
    def __init__(self):
        """Initialize session storage."""
        self.sessions = {}
        self.max_session_age_hours = 24
        logger.info("✅ SessionManager initialized")
    
    def create_session(self, user_id: str = "default") -> str:
        """
        Create new session.
        
        Args:
            user_id: User identifier
        
        Returns:
            session_id: Unique session ID
        """
        import uuid
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_accessed': datetime.now().isoformat(),
            'files': {},
            'operations': []
        }
        
        logger.info(f"✅ Session created: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.
        
        Args:
            session_id: Session ID
        
        Returns:
            Session data or None
        """
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        session['last_accessed'] = datetime.now().isoformat()
        
        return session
    
    def add_file(self, session_id: str, file_id: str, 
                 filename: str, sheet_name: str) -> Dict[str, Any]:
        """
        Track file in session.
        
        Args:
            session_id: Session ID
            file_id: File ID from FileManager
            filename: Original filename
            sheet_name: Active sheet name
        
        Returns:
            {
                'success': bool,
                'error': Error if failed
            }
        """
        try:
            if session_id not in self.sessions:
                return {'success': False, 'error': 'Session not found'}
            
            self.sessions[session_id]['files'][file_id] = {
                'filename': filename,
                'sheet_name': sheet_name,
                'added_at': datetime.now().isoformat(),
                'dataframe_info': None,
                'last_code': None
            }
            
            logger.info(f"File {file_id} added to session {session_id}")
            return {'success': True}
        
        except Exception as e:
            logger.error(f"Add file error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def update_dataframe_info(self, session_id: str, file_id: str,
                             dataframe_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store DataFrame metadata in session.
        
        Args:
            session_id: Session ID
            file_id: File ID
            dataframe_info: DataFrame metadata
        
        Returns:
            {'success': bool, 'error': str}
        """
        try:
            if session_id not in self.sessions:
                return {'success': False, 'error': 'Session not found'}
            
            if file_id not in self.sessions[session_id]['files']:
                return {'success': False, 'error': 'File not in session'}
            
            self.sessions[session_id]['files'][file_id]['dataframe_info'] = dataframe_info
            
            return {'success': True}
        
        except Exception as e:
            logger.error(f"Update dataframe info error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def record_operation(self, session_id: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record operation in session history.
        
        Args:
            session_id: Session ID
            operation: Operation details {type, file_id, code, result}
        
        Returns:
            {'success': bool, 'error': str}
        """
        try:
            if session_id not in self.sessions:
                return {'success': False, 'error': 'Session not found'}
            
            self.sessions[session_id]['operations'].append({
                'timestamp': datetime.now().isoformat(),
                **operation
            })
            
            logger.info(f"Operation recorded: {operation.get('type', 'unknown')}")
            return {'success': True}
        
        except Exception as e:
            logger.error(f"Record operation error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def cleanup_old_sessions(self) -> Dict[str, Any]:
        """
        Delete sessions older than max_session_age_hours.
        
        Returns:
            {'deleted': int, 'error': str}
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.max_session_age_hours)
            deleted = 0
            
            sessions_to_delete = []
            for session_id, session in self.sessions.items():
                created = datetime.fromisoformat(session['created_at'])
                if created < cutoff_time:
                    sessions_to_delete.append(session_id)
            
            for session_id in sessions_to_delete:
                del self.sessions[session_id]
                deleted += 1
            
            logger.info(f"✅ Cleanup: {deleted} old sessions deleted")
            return {'deleted': deleted}
        
        except Exception as e:
            logger.error(f"Cleanup error: {str(e)}")
            return {'error': str(e)}


# Global session manager instance
session_manager = SessionManager()
