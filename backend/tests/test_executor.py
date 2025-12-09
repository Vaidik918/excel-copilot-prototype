import unittest
import pandas as pd
from core.code_executor import CodeExecutor

class TestCodeExecutor(unittest.TestCase):
    """Test Code Executor."""
    
    def test_executor_simple(self):
        """Test simple code execution."""
        df = pd.DataFrame({'a': [1, 2, 3]})
        code = 'df = df'
        result = CodeExecutor.execute(code, df)
        self.assertTrue(result['success'])

if __name__ == '__main__':
    unittest.main()