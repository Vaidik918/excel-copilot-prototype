

import pandas as pd
import openpyxl
import io
from datetime import datetime
from typing import Dict, List, Any, Optional
from utils.logger import setup_logger

logger = setup_logger(__name__)


class ExcelHandler:
    """Handle Excel file operations with full validation and error handling."""
    
    # Allowed file types
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    MAX_FILE_SIZE_MB = 50
    MAX_ROWS = 100000
    MAX_COLUMNS = 500
    
    @staticmethod
    def validate_file(file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Validate Excel file before processing.
        
        Args:
            file_bytes: Binary file content
            filename: Original filename
        
        Returns:
            {
                'valid': bool,
                'error': Error message if invalid
            }
        """
        try:
            # Check file extension
            ext = filename.split('.')[-1].lower()
            if ext not in ExcelHandler.ALLOWED_EXTENSIONS:
                return {
                    'valid': False,
                    'error': f'Invalid file type: {ext}. Allowed: {ExcelHandler.ALLOWED_EXTENSIONS}'
                }
            
            # Check file size
            size_mb = len(file_bytes) / (1024 * 1024)
            if size_mb > ExcelHandler.MAX_FILE_SIZE_MB:
                return {
                    'valid': False,
                    'error': f'File too large: {size_mb:.2f}MB (max {ExcelHandler.MAX_FILE_SIZE_MB}MB)'
                }
            
            # Check if it's valid Excel
            try:
                io.BytesIO(file_bytes)
                pd.ExcelFile(io.BytesIO(file_bytes))
            except Exception as e:
                return {
                    'valid': False,
                    'error': f'Invalid Excel file: {str(e)}'
                }
            
            return {'valid': True}
        
        except Exception as e:
            logger.error(f"File validation error: {str(e)}")
            return {'valid': False, 'error': str(e)}
    
    @staticmethod
    def load_excel(file_bytes: bytes, filename: str = "") -> Dict[str, Any]:
        """
        Load Excel file and extract data with metadata.
        
        Args:
            file_bytes: Binary file content
            filename: Original filename
        
        Returns:
            {
                'success': bool,
                'sheets': [sheet names],
                'data': {sheet_name: DataFrame},
                'metadata': {
                    'filename': str,
                    'upload_time': ISO string,
                    'total_sheets': int,
                    'total_rows': int,
                    'total_columns': int,
                    'sheet_info': {
                        'Sheet1': {
                            'rows': int,
                            'columns': int,
                            'column_names': [names],
                            'dtypes': {col: dtype}
                        }
                    }
                },
                'error': Error message if failed
            }
        """
        try:
            logger.info(f"Loading Excel file: {filename}")
            
            # Validate first
            validation = ExcelHandler.validate_file(file_bytes, filename)
            if not validation['valid']:
                logger.warning(f"Validation failed: {validation['error']}")
                return {
                    'success': False,
                    'error': validation['error']
                }
            
            # Load Excel
            file_obj = io.BytesIO(file_bytes)
            excel_file = pd.ExcelFile(file_obj)
            sheets = excel_file.sheet_names
            
            if not sheets:
                return {
                    'success': False,
                    'error': 'Excel file has no sheets'
                }
            
            data = {}
            total_rows = 0
            total_columns = 0
            sheet_info = {}
            
            for sheet_name in sheets:
                file_obj.seek(0)
                df = pd.read_excel(file_obj, sheet_name=sheet_name)
                
                # Validate sheet size
                if len(df) > ExcelHandler.MAX_ROWS:
                    logger.warning(f"Sheet {sheet_name} has {len(df)} rows, exceeds limit {ExcelHandler.MAX_ROWS}")
                    return {
                        'success': False,
                        'error': f'Sheet "{sheet_name}" exceeds max rows ({ExcelHandler.MAX_ROWS})'
                    }
                
                if len(df.columns) > ExcelHandler.MAX_COLUMNS:
                    return {
                        'success': False,
                        'error': f'Sheet "{sheet_name}" exceeds max columns ({ExcelHandler.MAX_COLUMNS})'
                    }
                
                data[sheet_name] = df
                total_rows += len(df)
                total_columns = max(total_columns, len(df.columns))
                
                # Store sheet info
                sheet_info[sheet_name] = {
                    'rows': len(df),
                    'columns': len(df.columns),
                    'column_names': df.columns.tolist(),
                    'dtypes': df.dtypes.astype(str).to_dict(),
                    'sample': df.head(3).to_dict('records')  # First 3 rows for preview
                }
            
            metadata = {
                'filename': filename,
                'upload_time': datetime.now().isoformat(),
                'total_sheets': len(sheets),
                'total_rows': total_rows,
                'total_columns': total_columns,
                'sheet_info': sheet_info
            }
            
            logger.info(f"✅ Excel loaded: {len(sheets)} sheets, {total_rows} total rows")
            
            return {
                'success': True,
                'sheets': sheets,
                'data': data,
                'metadata': metadata
            }
        
        except Exception as e:
            logger.error(f"❌ Excel load error: {str(e)}")
            return {
                'success': False,
                'error': f"Excel load failed: {str(e)}"
            }
    
    @staticmethod
    def save_excel(dataframes_dict: Dict[str, pd.DataFrame], 
                   filename: str = "output.xlsx") -> bytes:
        """
        Save DataFrames as Excel file and return bytes.
        
        Args:
            dataframes_dict: {'sheet_name': DataFrame}
            filename: Output filename (for reference only)
        
        Returns:
            bytes: Excel file content
        
        Raises:
            Exception: If save fails
        """
        try:
            logger.info(f"Saving Excel: {filename}")
            
            if not dataframes_dict:
                raise ValueError("No DataFrames to save")
            
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for sheet_name, df in dataframes_dict.items():
                    if not isinstance(df, pd.DataFrame):
                        raise ValueError(f"Item '{sheet_name}' is not a DataFrame")
                    
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            output.seek(0)
            file_bytes = output.getvalue()
            
            logger.info(f"✅ Excel saved: {filename} ({len(file_bytes)} bytes)")
            return file_bytes
        
        except Exception as e:
            logger.error(f"❌ Excel save error: {str(e)}")
            raise Exception(f"Excel save failed: {str(e)}")
    
    @staticmethod
    def get_sheet_schema(df: pd.DataFrame, sheet_name: str = "Sheet1") -> Dict[str, Any]:
        """
        Extract schema information from DataFrame.
        
        Args:
            df: DataFrame
            sheet_name: Sheet name
        
        Returns:
            {
                'sheet_name': str,
                'rows': int,
                'columns': int,
                'column_info': {
                    'col_name': {
                        'type': dtype,
                        'non_null': count,
                        'unique': count,
                        'sample_values': [values]
                    }
                }
            }
        """
        try:
            column_info = {}
            
            for col in df.columns:
                column_info[col] = {
                    'type': str(df[col].dtype),
                    'non_null': int(df[col].notna().sum()),
                    'null': int(df[col].isna().sum()),
                    'unique': int(df[col].nunique()),
                    'sample_values': df[col].dropna().head(3).tolist()
                }
            
            return {
                'sheet_name': sheet_name,
                'rows': len(df),
                'columns': len(df.columns),
                'column_info': column_info
            }
        
        except Exception as e:
            logger.error(f"Schema extraction error: {str(e)}")
            raise
    
    @staticmethod
    def validate_data(df: pd.DataFrame, 
                     required_columns: List[str] = None,
                     dtypes_expected: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Validate DataFrame structure and content.
        
        Args:
            df: DataFrame to validate
            required_columns: List of mandatory columns
            dtypes_expected: Expected data types
        
        Returns:
            {
                'valid': bool,
                'errors': [error messages],
                'warnings': [warning messages]
            }
        """
        errors = []
        warnings = []
        
        # Check required columns
        if required_columns:
            missing = set(required_columns) - set(df.columns)
            if missing:
                errors.append(f"Missing columns: {missing}")
        
        # Check data types if specified
        if dtypes_expected:
            for col, expected_type in dtypes_expected.items():
                if col in df.columns:
                    actual_type = str(df[col].dtype)
                    if actual_type != expected_type:
                        warnings.append(f"Column '{col}' type mismatch: expected {expected_type}, got {actual_type}")
        
        # Check for null values in important columns
        null_counts = df.isnull().sum()
        if (null_counts > 0).any():
            for col in null_counts[null_counts > 0].index:
                warnings.append(f"Column '{col}' has {null_counts[col]} null values")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }


# Test function
def test_excel_handler():
    """Test ExcelHandler with sample data."""
    logger.info("Testing ExcelHandler...")
    
    try:
        # Create sample data
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'status': ['Active', 'Inactive', 'Active']
        })
        
        # Test save
        handler = ExcelHandler()
        file_bytes = handler.save_excel({'TestSheet': df}, 'test.xlsx')
        logger.info(f"✅ Save successful: {len(file_bytes)} bytes")
        
        # Test load
        result = handler.load_excel(file_bytes, 'test.xlsx')
        if result['success']:
            logger.info(f"✅ Load successful: {result['metadata']['total_rows']} rows")
        else:
            logger.error(f"❌ Load failed: {result['error']}")
    
    except Exception as e:
        logger.error(f"❌ Test error: {str(e)}")


if __name__ == "__main__":
    test_excel_handler()
