"""Integration tests for execute endpoint"""

import unittest
import json
import pandas as pd
import io
from main import app


class TestExecuteEndpoint(unittest.TestCase):
    """Test execute endpoint."""
    
    def setUp(self):
        """Setup test client, session, and file."""
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
    
    def test_execute_filter(self):
        """Test executing filter code."""
        code = "df = df[df['value'] > 20]"
        
        response = self.client.post('/api/execute',
            json={
                'session_id': self.session_id,
                'file_id': self.file_id,
                'code': code
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('execution_id', data)
        self.assertEqual(data['rows_before'], 5)
        self.assertEqual(data['rows_after'], 3)
    
    def test_execute_add_column(self):
        """Test executing add column code."""
        code = "df['doubled'] = df['value'] * 2"
        
        response = self.client.post('/api/execute',
            json={
                'session_id': self.session_id,
                'file_id': self.file_id,
                'code': code
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['columns_after'], 4)
    
    def test_execute_preview(self):
        """Test execute preview (dry run)."""
        code = "df = df[df['value'] > 25]"
        
        response = self.client.post('/api/execute/preview',
            json={
                'session_id': self.session_id,
                'file_id': self.file_id,
                'code': code
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertTrue(data.get('is_preview', False))
    
    def test_execute_invalid_session(self):
        """Test execute with invalid session."""
        response = self.client.post('/api/execute',
            json={
                'session_id': 'invalid',
                'file_id': 'invalid',
                'code': 'df = df'
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 404)
    
    def test_execute_missing_code(self):
        """Test execute without code."""
        response = self.client.post('/api/execute',
            json={
                'session_id': self.session_id,
                'file_id': self.file_id
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
