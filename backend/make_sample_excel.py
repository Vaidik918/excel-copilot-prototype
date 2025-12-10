# make_sample_excel.py
import pandas as pd

data = {
    "id": [1, 2, 3, 4, 5],
    "name": ["Alice", "Bob", "Charlie", "David", "Eve"],
    "status": ["Pending", "Completed", "Pending", "In Progress", "Completed"],
    "amount": [1000, 5000, 2000, 3000, 4000],
}

df = pd.DataFrame(data)
df.to_excel("test_sample.xlsx", index=False)
print("✅ Sample Excel file created: test_sample.xlsx")
