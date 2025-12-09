import unittest
from core.excel_handler import ExcelHandler

class TestExcelHandler(unittest.TestCase):
    """Test Excel Handler."""
    
    def test_handler_init(self):
        """Test ExcelHandler initialization."""
        handler = ExcelHandler()
        self.assertIsNotNone(handler)

if __name__ == '__main__':
    unittest.main()