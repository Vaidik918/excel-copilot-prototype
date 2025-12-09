
import pandas as pd
import numpy as np
from utils.logger import setup_logger

logger = setup_logger(__name__)

class CodeExecutor:
    """Execute pandas code safely."""
    
    @staticmethod
    def execute(code, df):
        """
        Execute pandas code on DataFrame.
        
        Args:
            code: Python code string
            df: Input DataFrame
        
        Returns:
            {
                'success': bool,
                'df': Modified DataFrame,
                'error': Error message if failed
            }
        """
        try:
            logger.info("Executing pandas code...")
            
            # Safe namespace
            namespace = {
                'df': df,
                'pd': pd,
                'np': np,
            }
            
            # Execute code
            exec(code, namespace)
            
            # Get result
            result_df = namespace.get('df', df)
            
            # Validate result
            if not isinstance(result_df, pd.DataFrame):
                return {
                    'success': False,
                    'error': 'Code did not return a DataFrame'
                }
            
            logger.info(f"✅ Code executed. Rows: {len(df)} → {len(result_df)}")
            
            return {
                'success': True,
                'df': result_df,
                'rows_before': len(df),
                'rows_after': len(result_df),
            }
        
        except Exception as e:
            logger.error(f"❌ Code execution error: {str(e)}")
            return {
                'success': False,
                'error': f"Code execution error: {str(e)}"
            }

# Test function
def test_code_executor():
    """Test CodeExecutor with sample data."""
    logger.info("Testing CodeExecutor...")
    
    # Create sample DataFrame
    df = pd.DataFrame({
        'id': [1, 2, 3],
        'name': ['A', 'B', 'C'],
        'value': [10, 20, 30]
    })
    
    # Test simple operation
    code = "df = df[df['value'] > 15]"
    
    result = CodeExecutor.execute(code, df)
    
    if result['success']:
        logger.info(f"✅ CodeExecutor working. Rows: {result['rows_before']} → {result['rows_after']}")
    else:
        logger.error(f"❌ CodeExecutor error: {result['error']}")

if __name__ == "__main__":
    test_code_executor()
