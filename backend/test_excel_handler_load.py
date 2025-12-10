# test_excel_handler_load.py
from core.excel_handler import ExcelHandler

with open("test_sample.xlsx", "rb") as f:
    file_bytes = f.read()

handler = ExcelHandler()
result = handler.load_excel(file_bytes, "test_sample.xlsx")

if result["success"]:
    print("✅ File loaded successfully")
    print("  Sheets:", result["sheets"])
    print("  Rows:", result["metadata"]["total_rows"])
    print("  Columns:", result["metadata"]["total_columns"])
else:
    print("❌ Error:", result["error"])
