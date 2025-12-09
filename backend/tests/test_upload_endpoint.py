"""Integration tests for upload endpoint"""

import unittest
import json
import pandas as pd
import io
from main import app


class TestUploadEndpoint(unittest.TestCase):
    """Test upload endpoint."""
    
    def setUp(self):
        """Setup test client."""
        self.client = app.test_client()
        
        # Create sample Excel file
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['A', 'B', 'C'],
            'value': [10, 20, 30]
        })
        
        self.excel_file = io.BytesIO()
        df.to_excel(self.excel_file, index=False)
        self.excel_file.seek(0)
    
    def test_upload_valid_file(self):
        """Test uploading valid Excel file."""
        response = self.client.post('/api/upload', data={
            'file': (self.excel_file, 'test.xlsx')
        })
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('session_id', data)
        self.assertIn('file_id', data)
        self.assertIn('metadata', data)
    
    def test_upload_no_file(self):
        """Test upload without file."""
        response = self.client.post('/api/upload')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_create_session(self):
        """Test session creation."""
        response = self.client.post('/api/session/create')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('session_id', data)
    
    def test_get_session(self):
        """Test getting session."""
        # Create session
        create_response = self.client.post('/api/session/create')
        create_data = json.loads(create_response.data)
        session_id = create_data['session_id']
        
        # Get session
        response = self.client.get(f'/api/session/{session_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('session', data)


if __name__ == '__main__':
    unittest.main()
