import os, glob
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

fname = [f for f in os.listdir('.') if 'PREG' in f.upper() and f.endswith('.xlsx')][0]
xls = pd.ExcelFile(fname)
print("File:", fname)
print("Sheets:", xls.sheet_names)

for s in xls.sheet_names:
    try:
        df = pd.read_excel(fname, sheet_name=s)
        # Check if any cell contains 'provis' or 'vencedor'
        match_prov = df.astype(str).apply(lambda x: x.str.contains('provis', case=False, na=False))
        if match_prov.any().any():
            print(f"--> Found 'provis' in sheet [{s}]: {match_prov.sum().sum()} matches")
            # print matching rows
            rows, cols = match_prov.values.nonzero()
            for r, c in zip(rows[:10], cols[:10]):
                print(f"    Row {r}, Col [{df.columns[c]}]: {df.iat[r, c]}")
    except Exception as e:
        print(f"Error reading {s}: {e}")
