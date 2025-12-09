
import pandas as pd
import openpyxl
import io
from datetime import datetime
from utils.logger import setup_logger

logger = setup_logger(__name__)

class ExcelHandler:
    """Handle Excel file operations."""
    
    @staticmethod
    def load_excel(file_bytes, filename=""):
        """
        Load Excel file aur return structured data.
        
        Args:
            file_bytes: Binary file content
            filename: Original filename
        
        Returns:
            {
                'success': bool,
                'sheets': [sheet names],
                'data': {sheet_name: DataFrame},
                'metadata': {...}
            }
        """
        try:
            logger.info(f"Loading Excel file: {filename}")
            
            file_obj = io.BytesIO(file_bytes)
            excel_file = pd.ExcelFile(file_obj)
            sheets = excel_file.sheet_names
            
            data = {}
            total_rows = 0
            
            for sheet in sheets:
                file_obj.seek(0)
                df = pd.read_excel(file_obj, sheet_name=sheet)
                data[sheet] = df
                total_rows += len(df)
            
            metadata = {
                'filename': filename,
                'upload_time': datetime.now().isoformat(),
                'total_sheets': len(sheets),
                'total_rows': total_rows,
                'total_columns': max(len(data[s].columns) for s in sheets) if sheets else 0,
            }
            
            logger.info(f"✅ Excel loaded: {len(sheets)} sheets, {total_rows} rows")
            
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
    def save_excel(dataframes_dict, filename="output.xlsx"):
        """
        Save DataFrames as Excel file.
        
        Args:
            dataframes_dict: {'sheet_name': DataFrame}
            filename: Output filename
        
        Returns:
            bytes (Excel file content)
        """
        try:
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                for sheet_name, df in dataframes_dict.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            output.seek(0)
            logger.info(f"✅ Excel saved: {filename}")
            return output.getvalue()
        
        except Exception as e:
            logger.error(f"❌ Excel save error: {str(e)}")
            raise Exception(f"Excel save failed: {str(e)}")

# Test function
def test_excel_handler():
    """Test if ExcelHandler works (without actual files)"""
    logger.info("Testing ExcelHandler...")
    logger.info("✅ ExcelHandler class loaded successfully")

if __name__ == "__main__":
    test_excel_handler()
