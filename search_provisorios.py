import os, glob
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

files = glob.glob('Z:/PLAC-MVP/*.xlsx')
print(f'Checking {len(files)} excel files...')

for f in files:
    try:
        xls = pd.ExcelFile(f)
        for s in xls.sheet_names:
            try:
                df = pd.read_excel(f, sheet_name=s)
                # check column names
                for col in df.columns:
                    col_str = str(col).lower()
                    if 'provis' in col_str or 'vencedor' in col_str or 'adjudica' in col_str:
                        print(f'MATCH COL in {os.path.basename(f)} -> {s} -> {col}')
                # check inside content
                matches = df.astype(str).apply(lambda x: x.str.contains('provisór|provisor', case=False, na=False))
                if matches.any().any():
                    match_count = matches.sum().sum()
                    print(f'MATCH CONTENT provisor in {os.path.basename(f)} -> {s}: {match_count} occurrences')
            except Exception as e:
                pass
    except Exception as e:
        pass

print("Search completed.")
