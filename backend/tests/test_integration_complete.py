import unittest
import json
import pandas as pd
import io
from main import app



class TestCompleteWorkflow(unittest.TestCase):
    """Test complete user workflow."""
    
    def setUp(self):
        """Setup test client."""
        self.client = app.test_client()
    
    def test_workflow_upload_analyze_execute_download(self):
        """Test complete workflow: upload → analyze → execute → download."""
        
        # Step 1: Create session
        session_response = self.client.post('/api/session/create')
        self.assertEqual(session_response.status_code, 200)
        session_id = json.loads(session_response.data)['session_id']
        
        # Step 2: Create and upload Excel file
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'status': ['Active', 'Inactive', 'Active', 'Active', 'Inactive'],
            'amount': [100, 200, 300, 400, 500]
        })
        
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        upload_response = self.client.post('/api/upload', data={
            'file': (excel_file, 'workflow_test.xlsx'),
            'session_id': session_id
        })
        
        self.assertEqual(upload_response.status_code, 200)
        upload_data = json.loads(upload_response.data)
        file_id = upload_data['file_id']
        
        self.assertTrue(upload_data['success'])
        self.assertEqual(upload_data['metadata']['total_rows'], 5)
        
        # Step 3: Analyze - Generate code for filtering
        analyze_response = self.client.post('/api/analyze',
            json={
                'session_id': session_id,
                'file_id': file_id,
                'prompt': 'Filter rows where status is Active and amount is greater than 200'
            },
            content_type='application/json'
        )
        
        self.assertEqual(analyze_response.status_code, 200)
        analyze_data = json.loads(analyze_response.data)
        
        self.assertTrue(analyze_data['success'])
        self.assertIn('code', analyze_data)
        code = analyze_data['code']
        
        # Step 4: Preview execution
        preview_response = self.client.post('/api/execute/preview',
            json={
                'session_id': session_id,
                'file_id': file_id,
                'code': code
            },
            content_type='application/json'
        )
        
        self.assertEqual(preview_response.status_code, 200)
        preview_data = json.loads(preview_response.data)
        
        self.assertTrue(preview_data['success'])
        self.assertTrue(preview_data['is_preview'])
        
        # Step 5: Execute code
        execute_response = self.client.post('/api/execute',
            json={
                'session_id': session_id,
                'file_id': file_id,
                'code': code
            },
            content_type='application/json'
        )
        
        self.assertEqual(execute_response.status_code, 200)
        execute_data = json.loads(execute_response.data)
        
        self.assertTrue(execute_data['success'])
        self.assertIn('execution_id', execute_data)
        
        # Step 6: Download modified file
        download_response = self.client.get(
            f'/api/download/{file_id}',
            query_string={
                'session_id': session_id,
                'version': 'modified'
            }
        )
        
        self.assertEqual(download_response.status_code, 200)
        content_type = download_response.headers['content-type'].lower()
        self.assertTrue('spreadsheet' in content_type or 'xlsx' in content_type,
                        f"Expected spreadsheet MIME type, got: {content_type}")
        
        # Step 7: List files
        list_response = self.client.get(f'/api/download/session/{session_id}/files')
        self.assertEqual(list_response.status_code, 200)
        
        list_data = json.loads(list_response.data)
        self.assertTrue(list_data['success'])
        self.assertGreater(len(list_data['files']), 0)
    
    def test_workflow_multiple_operations(self):
        """Test multiple operations on same file."""
        
        # Setup
        session_response = self.client.post('/api/session/create')
        session_id = json.loads(session_response.data)['session_id']
        
        df = pd.DataFrame({
            'id': range(1, 11),
            'value': range(10, 110, 10)
        })
        
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        upload_response = self.client.post('/api/upload', data={
            'file': (excel_file, 'multi_ops.xlsx'),
            'session_id': session_id
        })
        
        file_id = json.loads(upload_response.data)['file_id']
        
        # Operation 1: Filter
        code1 = "df = df[df['value'] > 50]"
        execute_response1 = self.client.post('/api/execute',
            json={
                'session_id': session_id,
                'file_id': file_id,
                'code': code1
            },
            content_type='application/json'
        )
        
        self.assertEqual(execute_response1.status_code, 200)
        execution1 = json.loads(execute_response1.data)
        self.assertEqual(execution1['rows_after'], 5)
        
        # Operation 2: Add column
        code2 = "df['doubled'] = df['value'] * 2"
        execute_response2 = self.client.post('/api/execute',
            json={
                'session_id': session_id,
                'file_id': file_id,
                'code': code2
            },
            content_type='application/json'
        )
        
        self.assertEqual(execute_response2.status_code, 200)
        execution2 = json.loads(execute_response2.data)
        self.assertEqual(execution2['columns_after'], 3)  # id, value, doubled
    
    def test_workflow_error_handling(self):
        """Test error scenarios in workflow."""
        
        session_response = self.client.post('/api/session/create')
        session_id = json.loads(session_response.data)['session_id']
        
        # Try to analyze without file
        analyze_response = self.client.post('/api/analyze',
            json={
                'session_id': session_id,
                'file_id': 'nonexistent',
                'prompt': 'Test'
            },
            content_type='application/json'
        )
        
        self.assertEqual(analyze_response.status_code, 404)
        
        # Try to execute on nonexistent file
        execute_response = self.client.post('/api/execute',
            json={
                'session_id': session_id,
                'file_id': 'nonexistent',
                'code': 'df = df'
            },
            content_type='application/json'
        )
        
        self.assertEqual(execute_response.status_code, 404)



class TestErrorScenarios(unittest.TestCase):
    """Test error handling."""
    
    def setUp(self):
        """Setup."""
        self.client = app.test_client()
    
    def test_invalid_json(self):
        """Test invalid JSON in requests."""
        response = self.client.post('/api/analyze',
            data='invalid json',
            content_type='application/json'
        )
        
        # Should return 400 or similar error
        self.assertIn(response.status_code, [400, 500])
    
    def test_missing_required_fields(self):
        """Test missing required fields."""
        response = self.client.post('/api/execute',
            json={
                'session_id': 'test'
                # Missing file_id and code
            },
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    def test_file_not_found(self):
        """Test operations on nonexistent files."""
        response = self.client.get(
            '/api/download/nonexistent',
            query_string={'session_id': 'nonexistent'}
        )
        
        self.assertEqual(response.status_code, 404)



class TestSessionManagement(unittest.TestCase):
    """Test session management functionality."""
    
    def setUp(self):
        """Setup."""
        self.client = app.test_client()
    
    def test_create_session(self):
        """Test session creation."""
        response = self.client.post('/api/session/create')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertTrue(data['success'])
        self.assertIn('session_id', data)
        self.assertTrue(len(data['session_id']) > 0)
    
    def test_get_session(self):
        """Test getting session data."""
        # Create
        create_response = self.client.post('/api/session/create')
        session_id = json.loads(create_response.data)['session_id']
        
        # Get
        get_response = self.client.get(f'/api/session/{session_id}')
        
        self.assertEqual(get_response.status_code, 200)
        data = json.loads(get_response.data)
        
        self.assertTrue(data['success'])
        self.assertEqual(data['session']['user_id'], 'default')
    
    def test_session_persistence(self):
        """Test that session data persists across requests."""
        # Create session
        session_response = self.client.post('/api/session/create')
        session_id = json.loads(session_response.data)['session_id']
        
        # Upload file
        df = pd.DataFrame({'id': [1, 2, 3]})
        excel_file = io.BytesIO()
        df.to_excel(excel_file, index=False)
        excel_file.seek(0)
        
        upload_response = self.client.post('/api/upload', data={
            'file': (excel_file, 'test.xlsx'),
            'session_id': session_id
        })
        
        file_id = json.loads(upload_response.data)['file_id']
        
        # Get session - file should still be there
        get_response = self.client.get(f'/api/session/{session_id}')
        session_data = json.loads(get_response.data)
        
        self.assertIn(file_id, session_data['session']['files'])



if __name__ == '__main__':
    unittest.main()