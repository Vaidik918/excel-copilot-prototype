import unittest
from core.gemini_handler import GeminiHandler, test_gemini_connection

class TestGeminiHandler(unittest.TestCase):
    """Test Gemini Handler."""
    
    def test_api_connection(self):
        """Test Gemini API connection."""
        result = test_gemini_connection()
        self.assertIsNotNone(result)

if __name__ == '__main__':
    unittest.main()