"""Unit tests for Code Executor"""

import unittest
import pandas as pd
from core.code_executor import CodeExecutor


class TestCodeExecutor(unittest.TestCase):
    """Test Code Executor."""
    
    def setUp(self):
        """Setup test data."""
        self.executor = CodeExecutor()
        self.df = pd.DataFrame({
            'id': [1, 2, 3],
            'value': [10, 20, 30],
            'status': ['A', 'B', 'C']
        })
    
    def test_filter_operation(self):
        """Test filtering."""
        code = "df = df[df['value'] > 15]"
        result = self.executor.execute(code, self.df)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['rows_before'], 3)
        self.assertEqual(result['rows_after'], 2)
    
    def test_add_column(self):
        """Test adding column."""
        code = "df['doubled'] = df['value'] * 2"
        result = self.executor.execute(code, self.df)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['columns_after'], 4)
    
    def test_dangerous_code_import(self):
        """Test safety: dangerous import."""
        code = "df = __import__('os')"
        result = self.executor.execute(code, self.df)
        
        self.assertFalse(result['success'])
        self.assertIn('forbidden', result['error'].lower())
    
    def test_syntax_error(self):
        """Test syntax error handling."""
        code = "df = df[df['value'] >"  # Incomplete
        result = self.executor.execute(code, self.df)
        
        self.assertFalse(result['success'])
        self.assertIn('syntax', result['error'].lower())
    
    def test_column_not_found(self):
        """Test missing column error."""
        code = "df = df[df['missing_col'] > 5]"
        result = self.executor.execute(code, self.df)
        
        self.assertFalse(result['success'])


if __name__ == '__main__':
    unittest.main()
