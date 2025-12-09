"""Integration tests for download endpoint"""

import unittest
import json
import pandas as pd
import io
from main import app


class TestDownloadEndpoint(unittest.TestCase):
    """Test download endpoint."""
    
    def setUp(self):
        """Setup test client, session, file, and execute."""
        self.client = app.test_client()
        
        # Create session
        session_response = self.client.post('/api/session/create')
        self.session_id = json.loads(session_response.data)['session_id']
        
        # Create and upload Excel file
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['A', 'B', 'C', 'D', 'E'],
            'value': [10, 20, 30, 40, 50]
        })
        
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        upload_response = self.client.post('/api/upload', data={
            'file': (excel_file, 'test.xlsx'),
            'session_id': self.session_id
        })
        
        self.file_id = json.loads(upload_response.data)['file_id']
        
        # Execute code to create modified version
        execute_response = self.client.post('/api/execute',
            json={
                'session_id': self.session_id,
                'file_id': self.file_id,
                'code': "df = df[df['value'] > 20]"
            },
            content_type='application/json'
        )
        
        self.execution_id = json.loads(execute_response.data)['execution_id']
    
    def test_download_original(self):
        """Test downloading original file."""
        response = self.client.get(
            f'/api/download/{self.file_id}',
            query_string={
                'session_id': self.session_id,
                'version': 'original'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('content-type', response.headers)
        self.assertIn('spreadsheet', response.headers['content-type'].lower())

    
    def test_download_modified(self):
        """Test downloading modified file."""
        response = self.client.get(
            f'/api/download/{self.file_id}',
            query_string={
                'session_id': self.session_id,
                'version': 'modified'
            }
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('spreadsheet', response.headers['content-type'].lower())

    
    def test_download_default_modified(self):
        """Test download defaults to modified."""
        response = self.client.get(
            f'/api/download/{self.file_id}',
            query_string={'session_id': self.session_id}
        )
        
        self.assertEqual(response.status_code, 200)
    
    def test_list_session_files(self):
        """Test listing files in session."""
        response = self.client.get(f'/api/download/session/{self.session_id}/files')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertGreater(len(data['files']), 0)
        self.assertIn('versions', data['files'][0])
    
    def test_revert_to_original(self):
        """Test reverting to original file."""
        response = self.client.post(
            f'/api/download/{self.file_id}/revert',
            json={'session_id': self.session_id},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
    
    def test_download_invalid_session(self):
        """Test download with invalid session."""
        response = self.client.get(
            f'/api/download/{self.file_id}',
            query_string={'session_id': 'invalid'}
        )
        
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
