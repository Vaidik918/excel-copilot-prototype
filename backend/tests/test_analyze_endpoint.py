"""Integration tests for analyze endpoint"""

import unittest
import json
import pandas as pd
import io
from main import app


class TestAnalyzeEndpoint(unittest.TestCase):
    """Test analyze endpoint."""
    
    def setUp(self):
        """Setup test client and session."""
        self.client = app.test_client()
        
        # Create session
        session_response = self.client.post('/api/session/create')
        session_data = json.loads(session_response.data)
        self.session_id = session_data['session_id']
        
        # Create and upload Excel file
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['A', 'B', 'C', 'D', 'E'],
            'status': ['Active', 'Inactive', 'Active', 'Active', 'Inactive'],
            'amount': [100, 200, 300, 400, 500]
        })
        
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        upload_response = self.client.post('/api/upload', data={
            'file': (excel_file, 'test.xlsx'),
            'session_id': self.session_id
        })
        
        upload_data = json.loads(upload_response.data)
        self.file_id = upload_data['file_id']
    
    def test_analyze_filter_prompt(self):
        """Test analyzing filter prompt."""
        response = self.client.post('/api/analyze', 
            json={
                'session_id': self.session_id,
                'file_id': self.file_id,
                'prompt': 'Filter rows where status is Active'
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('code', data)
        self.assertIn('explanation', data)
        self.assertIn('risks', data)
    
    def test_analyze_missing_prompt(self):
        """Test analyze without prompt."""
        response = self.client.post('/api/analyze',
            json={
                'session_id': self.session_id,
                'file_id': self.file_id
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_analyze_invalid_session(self):
        """Test analyze with invalid session."""
        response = self.client.post('/api/analyze',
            json={
                'session_id': 'invalid',
                'file_id': 'invalid',
                'prompt': 'Test'
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main()
