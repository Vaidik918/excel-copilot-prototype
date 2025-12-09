"""Unit tests for Gemini Handler"""

import unittest
from core.gemini_handler import GeminiHandler, test_gemini_connection


class TestGeminiHandler(unittest.TestCase):
    """Test Gemini Handler."""
    
    def setUp(self):
        """Setup."""
        self.handler = GeminiHandler()
        self.sample_dataframe_info = {
            'total_rows': 100,
            'sheet_info': {
                'Sheet1': {
                    'column_names': ['id', 'name', 'status', 'amount'],
                    'dtypes': {
                        'id': 'int64',
                        'name': 'object',
                        'status': 'object',
                        'amount': 'float64'
                    },
                    'sample': [
                        {'id': 1, 'name': 'Alice', 'status': 'Active', 'amount': 1000}
                    ]
                }
            }
        }
    
    def test_gemini_connection(self):
        """Test Gemini API connection."""
        result = test_gemini_connection()
        self.assertTrue(result)
    
    def test_validate_code_valid_syntax(self):
        """Test code validation with valid code."""
        code = "df = df[df['id'] > 5]"
        result = self.handler.validate_code(code)
        self.assertTrue(result['valid'])
    
    def test_validate_code_invalid_syntax(self):
        """Test code validation with invalid code."""
        code = "df = df[df['id'] >"  # Missing closing bracket
        result = self.handler.validate_code(code)
        self.assertFalse(result['valid'])
    
    def test_parse_gemini_response_valid_json(self):
        """Test response parsing with valid JSON."""
        response = '''{
            "code": "df = df[df['status'] == 'Active']",
            "explanation": "Filter active records",
            "risks": [],
            "estimated_rows_affected": "~50"
        }'''
        
        result = self.handler._parse_gemini_response(response)
        self.assertTrue(result['success'])
        self.assertIn('df =', result['code'])


if __name__ == '__main__':
    unittest.main()
