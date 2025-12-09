"""Unit tests for ExcelHandler"""

import unittest
import pandas as pd
import io
from core.excel_handler import ExcelHandler


class TestExcelHandler(unittest.TestCase):
    """Test Excel Handler."""
    
    def setUp(self):
        """Setup test data."""
        self.handler = ExcelHandler()
        self.test_df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['A', 'B', 'C', 'D', 'E'],
            'value': [10, 20, 30, 40, 50]
        })
    
    def test_save_excel(self):
        """Test save_excel method."""
        file_bytes = self.handler.save_excel(
            {'TestSheet': self.test_df},
            'test.xlsx'
        )
        self.assertIsInstance(file_bytes, bytes)
        self.assertGreater(len(file_bytes), 0)
    
    def test_load_excel(self):
        """Test load_excel method."""
        # Save first
        file_bytes = self.handler.save_excel(
            {'Sheet1': self.test_df},
            'test.xlsx'
        )
        
        # Load
        result = self.handler.load_excel(file_bytes, 'test.xlsx')
        
        self.assertTrue(result['success'])
        self.assertIn('Sheet1', result['sheets'])
        self.assertEqual(result['metadata']['total_rows'], 5)
    
    def test_validate_file_invalid_extension(self):
        """Test file validation with invalid extension."""
        result = self.handler.validate_file(b'dummy', 'test.txt')
        self.assertFalse(result['valid'])
    
    def test_validate_file_too_large(self):
        """Test file validation with oversized file."""
        # Create fake large file
        large_bytes = b'x' * (60 * 1024 * 1024)  # 60MB
        result = self.handler.validate_file(large_bytes, 'test.xlsx')
        self.assertFalse(result['valid'])
    
    def test_get_sheet_schema(self):
        """Test schema extraction."""
        schema = self.handler.get_sheet_schema(self.test_df, 'TestSheet')
        
        self.assertEqual(schema['sheet_name'], 'TestSheet')
        self.assertEqual(schema['rows'], 5)
        self.assertEqual(schema['columns'], 3)
        self.assertIn('id', schema['column_info'])
    
    def test_validate_data_missing_columns(self):
        """Test data validation with missing columns."""
        result = self.handler.validate_data(
            self.test_df,
            required_columns=['id', 'name', 'missing_col']
        )
        
        self.assertFalse(result['valid'])
        self.assertGreater(len(result['errors']), 0)


if __name__ == '__main__':
    unittest.main()
