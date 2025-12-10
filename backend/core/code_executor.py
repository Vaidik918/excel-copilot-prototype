"""
Execute generated pandas code safely with sandboxing and error handling
Phase 1: Full implementation
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from utils.logger import setup_logger
import traceback
import builtins as _builtins
logger = setup_logger(__name__)


class CodeExecutor:
    """Execute pandas code safely with restricted namespace."""
    
    # Allowed operations (whitelist approach)
    ALLOWED_BUILTINS = [
    # Common functions
    'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set',
    'tuple', 'range', 'enumerate', 'zip', 'map', 'filter',
    'sum', 'min', 'max', 'sorted', 'abs', 'round',
    'all', 'any', 'isinstance', 'type',  # NEW additions
    
    # Exceptions
    'KeyError', 'ValueError', 'TypeError', 'IndexError',
    'AttributeError', 'RuntimeError', 'Exception',
    'NameError', 'ZeroDivisionError',
    ]

    
    # Forbidden patterns in code
    FORBIDDEN_PATTERNS = [
        'import', 'exec', 'eval', '__import__',
        'open', 'input', 'compile', 'globals', 'locals',
        'vars', 'dir', 'getattr', 'setattr', 'delattr',
        'reload', 'breakpoint', 'exit', 'quit'
    ]
    
    @staticmethod
    def validate_code_safety(code: str) -> Tuple[bool, str]:
        """
        Check code for dangerous patterns.
        
        Args:
            code: Python code string
        
        Returns:
            (is_safe, error_message)
        """
        try:
            code_lower = code.lower()
            
            for pattern in CodeExecutor.FORBIDDEN_PATTERNS:
                if pattern in code_lower:
                    return False, f"Forbidden pattern detected: '{pattern}'"
            
            # Check for shell commands
            if '`' in code or '$' in code:
                return False, "Shell command syntax detected"
            
            return True, ""
        
        except Exception as e:
            return False, f"Safety check error: {str(e)}"
    
    @staticmethod
    def execute(code: str,
               df: pd.DataFrame,
               max_execution_seconds: int = 30) -> Dict[str, Any]:
        """
        Execute pandas code on DataFrame safely.
        
        Args:
            code: Python code string
            df: Input DataFrame
            max_execution_seconds: Max execution time (safety)
        
        Returns:
            {
                'success': bool,
                'df': Modified DataFrame (if success),
                'rows_before': int,
                'rows_after': int,
                'columns_before': int,
                'columns_after': int,
                'changes': Description of changes,
                'error': Error message if failed,
                'warning': Any warnings
            }
        """
        try:
            logger.info("Executing pandas code...")
            
            # Safety check first
            is_safe, error_msg = CodeExecutor.validate_code_safety(code)
            if not is_safe:
                logger.warning(f"⚠️ Code safety check failed: {error_msg}")
                return {
                    'success': False,
                    'error': f"Code safety violation: {error_msg}"
                }
            
            # Create restricted namespace
            safe_builtins = {name: getattr(_builtins, name) for name in CodeExecutor.ALLOWED_BUILTINS if hasattr(_builtins, name)}
            
            namespace = {
                'df': df.copy(),  # Use copy to preserve original
                'pd': pd,
                'np': np,
                '__builtins__': safe_builtins,
            }
            
            # Record before state
            rows_before = len(df)
            cols_before = len(df.columns)
            sample_before = df.head(2).to_dict('records')
            
            # Execute code
            exec(code, namespace)
            
            # Get result
            result_df = namespace.get('df')
            
            if result_df is None:
                return {
                    'success': False,
                    'error': 'Code did not modify df or return a DataFrame'
                }
            
            if not isinstance(result_df, pd.DataFrame):
                return {
                    'success': False,
                    'error': f'Code result is {type(result_df)}, not DataFrame'
                }
            
            # Record after state
            rows_after = len(result_df)
            cols_after = len(result_df.columns)
            sample_after = result_df.head(2).to_dict('records')
            
            # Calculate changes
            row_change = rows_after - rows_before
            col_change = cols_after - cols_before
            
            if row_change > 0:
                change_desc = f"Added {row_change} rows"
            elif row_change < 0:
                change_desc = f"Removed {abs(row_change)} rows"
            else:
                change_desc = "Row count unchanged"
            
            if col_change > 0:
                change_desc += f", Added {col_change} columns"
            elif col_change < 0:
                change_desc += f", Removed {abs(col_change)} columns"
            
            logger.info(f"✅ Code executed. {change_desc}")
            
            return {
                'success': True,
                'df': result_df,
                'rows_before': rows_before,
                'rows_after': rows_after,
                'columns_before': cols_before,
                'columns_after': cols_after,
                'row_change': row_change,
                'column_change': col_change,
                'changes': change_desc,
                'sample_before': sample_before,
                'sample_after': sample_after
            }
        
        except SyntaxError as e:
            logger.error(f"❌ Syntax error: {str(e)}")
            return {
                'success': False,
                'error': f"Syntax error in code: {str(e)}"
            }
        
        except ValueError as e:
            logger.error(f"❌ Value error: {str(e)}")
            return {
                'success': False,
                'error': f"Value error: {str(e)}"
            }
        
        except KeyError as e:
            logger.error(f"❌ Column not found: {str(e)}")
            return {
                'success': False,
                'error': f"Column not found: {str(e)}"
            }
        
        except Exception as e:
            logger.error(f"❌ Execution error: {str(e)}\n{traceback.format_exc()}")
            return {
                'success': False,
                'error': f"Code execution error: {str(e)}"
            }


def test_code_executor():
    """Test CodeExecutor with sample operations."""
    logger.info("Testing CodeExecutor...")
    
    try:
        # Create sample DataFrame
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'value': [10, 20, 30, 40, 50],
            'status': ['Active', 'Inactive', 'Active', 'Active', 'Inactive']
        })
        
        executor = CodeExecutor()
        
        # Test 1: Filter operation
        code1 = "df = df[df['value'] > 15]"
        result1 = executor.execute(code1, df)
        
        if result1['success']:
            logger.info(f"✅ Test 1 passed: {result1['changes']}")
        else:
            logger.error(f"❌ Test 1 failed: {result1['error']}")
        
        # Test 2: Add column
        code2 = "df['doubled'] = df['value'] * 2"
        result2 = executor.execute(code2, df)
        
        if result2['success']:
            logger.info(f"✅ Test 2 passed: {result2['changes']}")
        else:
            logger.error(f"❌ Test 2 failed: {result2['error']}")
        
        # Test 3: Dangerous code (should fail)
        code3 = "df = __import__('os').system('ls')"
        result3 = executor.execute(code3, df)
        
        if not result3['success']:
            logger.info(f"✅ Test 3 passed (safety caught dangerous code)")
        else:
            logger.warning(f"⚠️ Test 3: Dangerous code was not caught!")
    
    except Exception as e:
        logger.error(f"❌ Test error: {str(e)}")


if __name__ == "__main__":
    test_code_executor()
