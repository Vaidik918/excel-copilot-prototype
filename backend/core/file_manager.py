"""
File management for uploaded and processed Excel files
Phase 1: Full implementation
"""

import os
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any
from pathlib import Path
import uuid
from utils.logger import setup_logger

logger = setup_logger(__name__)


class FileManager:
    """Manage temporary file uploads and cleanup."""
    
    def __init__(self, upload_folder: str = "uploads/temp", max_age_hours: int = 24):
        """
        Initialize FileManager.
        
        Args:
            upload_folder: Path to upload directory
            max_age_hours: Max file age before cleanup
        """
        self.upload_folder = Path(upload_folder)
        self.max_age_hours = max_age_hours
        
        # Create folder if not exists
        self.upload_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ FileManager initialized: {self.upload_folder}")
    
    def save_upload(self, file_bytes: bytes, original_filename: str) -> Dict[str, Any]:
        """
        Save uploaded file with unique ID.
        
        Args:
            file_bytes: File content
            original_filename: Original filename
        
        Returns:
            {
                'success': bool,
                'file_id': Unique ID,
                'path': File path,
                'filename': Saved filename,
                'size': File size,
                'error': Error if failed
            }
        """
        try:
            # Generate unique ID
            file_id = str(uuid.uuid4())[:8]
            
            # Create session folder
            session_folder = self.upload_folder / file_id
            session_folder.mkdir(exist_ok=True)
            
            # Save file
            file_path = session_folder / original_filename
            with open(file_path, 'wb') as f:
                f.write(file_bytes)
            
            size_mb = len(file_bytes) / (1024 * 1024)
            
            logger.info(f"✅ File saved: {file_id} ({size_mb:.2f}MB)")
            
            return {
                'success': True,
                'file_id': file_id,
                'path': str(file_path),
                'filename': original_filename,
                'size': len(file_bytes),
                'size_mb': round(size_mb, 2),
                'saved_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"❌ File save error: {str(e)}")
            return {
                'success': False,
                'error': f"File save failed: {str(e)}"
            }
    
    def save_processed_file(self, 
                           file_bytes: bytes,
                           file_id: str,
                           filename: str) -> Dict[str, Any]:
        """
        Save processed file in same session folder.
        
        Args:
            file_bytes: Processed file content
            file_id: Session file ID
            filename: Output filename
        
        Returns:
            {
                'success': bool,
                'path': File path,
                'filename': Saved filename,
                'error': Error if failed
            }
        """
        try:
            session_folder = self.upload_folder / file_id
            session_folder.mkdir(exist_ok=True)
            
            file_path = session_folder / filename
            with open(file_path, 'wb') as f:
                f.write(file_bytes)
            
            logger.info(f"✅ Processed file saved: {file_id}/{filename}")
            
            return {
                'success': True,
                'path': str(file_path),
                'filename': filename,
                'size': len(file_bytes)
            }
        
        except Exception as e:
            logger.error(f"❌ Processed file save error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_file(self, file_id: str, filename: str) -> Dict[str, Any]:
        """
        Read file bytes.
        
        Args:
            file_id: Session file ID
            filename: Filename
        
        Returns:
            {
                'success': bool,
                'data': File bytes,
                'error': Error if failed
            }
        """
        try:
            file_path = self.upload_folder / file_id / filename
            
            if not file_path.exists():
                return {
                    'success': False,
                    'error': 'File not found'
                }
            
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            
            logger.info(f"✅ File retrieved: {file_id}/{filename}")
            
            return {
                'success': True,
                'data': file_bytes,
                'size': len(file_bytes)
            }
        
        except Exception as e:
            logger.error(f"❌ File read error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_session(self, file_id: str) -> Dict[str, Any]:
        """
        Delete session folder and all files.
        
        Args:
            file_id: Session file ID
        
        Returns:
            {
                'success': bool,
                'deleted_files': Number of files deleted,
                'error': Error if failed
            }
        """
        try:
            session_folder = self.upload_folder / file_id
            
            if not session_folder.exists():
                return {
                    'success': True,
                    'deleted_files': 0
                }
            
            # Count files before deletion
            files = list(session_folder.glob('*'))
            count = len(files)
            
            # Delete folder
            shutil.rmtree(session_folder)
            
            logger.info(f"✅ Session cleaned: {file_id} ({count} files deleted)")
            
            return {
                'success': True,
                'deleted_files': count
            }
        
        except Exception as e:
            logger.error(f"❌ Cleanup error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_old_files(self) -> Dict[str, Any]:
        """
        Clean up files older than max_age_hours.
        
        Returns:
            {
                'success': bool,
                'folders_deleted': Number of folders deleted,
                'error': Error if failed
            }
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)
            deleted_count = 0
            
            for folder in self.upload_folder.iterdir():
                if not folder.is_dir():
                    continue
                
                folder_time = datetime.fromtimestamp(folder.stat().st_mtime)
                
                if folder_time < cutoff_time:
                    shutil.rmtree(folder)
                    deleted_count += 1
            
            logger.info(f"✅ Old files cleanup: {deleted_count} folders deleted")
            
            return {
                'success': True,
                'folders_deleted': deleted_count
            }
        
        except Exception as e:
            logger.error(f"❌ Cleanup old files error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


def test_file_manager():
    """Test FileManager."""
    logger.info("Testing FileManager...")
    
    try:
        fm = FileManager()
        
        # Test 1: Save file
        test_bytes = b"Test file content"
        result = fm.save_upload(test_bytes, "test.xlsx")
        
        if result['success']:
            logger.info(f"✅ Save test passed: {result['file_id']}")
            file_id = result['file_id']
            
            # Test 2: Retrieve file
            result2 = fm.get_file(file_id, "test.xlsx")
            if result2['success']:
                logger.info(f"✅ Retrieve test passed")
            
            # Test 3: Cleanup
            result3 = fm.cleanup_session(file_id)
            if result3['success']:
                logger.info(f"✅ Cleanup test passed")
        else:
            logger.error(f"❌ Save test failed: {result['error']}")
    
    except Exception as e:
        logger.error(f"❌ Test error: {str(e)}")


if __name__ == "__main__":
    test_file_manager()
