import pandas as pd
import os

data_dir = "app/data"
for f in os.listdir(data_dir):
    if f.endswith(".xlsx"):
        path = os.path.join(data_dir, f)
        try:
            df = pd.read_excel(path, engine="openpyxl")
            print(f"File: {f}")
            print(f"Columns: {list(df.columns)}")
            
            # Check for group-like columns
            group_cols = [c for c in df.columns if "group" in c.lower()]
            print(f"Group-like columns: {group_cols}")
            
            for gc in group_cols:
                vals = df[gc].dropna().unique()
                print(f"Unique '{gc}' values (first 10): {vals[:10]}")
            
            # Specifically check 'CABA' and 'caba'
            caba_rows = df[df.iloc[:, 0].str.contains("caba", case=False, na=False)]
            if not caba_rows.empty:
                print("Rows matching 'caba':")
                print(caba_rows.to_string())
                
        except Exception as e:
            print(f"Error reading {f}: {e}")
        print("-" * 20)
