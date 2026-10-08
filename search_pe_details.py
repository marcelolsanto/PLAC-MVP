import pandas as pd
import warnings, os
warnings.filterwarnings('ignore')

# Search for PE 38, 42 or recent dates in all sheets of pregão file
fname = '6. PREGÃO ELETRONICO e DISP. ELETRÔNICA.xlsx'
xls = pd.ExcelFile(fname)
for s in xls.sheet_names:
    try:
        df = pd.read_excel(fname, sheet_name=s)
        # find rows where any cell has '38/2026' or '42/2026' or '05/10' or '2026-10'
        for col in df.columns:
            m = df[col].astype(str).str.contains('38/2026|42/2026|42|38|10/2026', case=False, na=False)
            if m.any():
                print(f"Sheet [{s}] Col [{col}] matches: {m.sum()}")
                sample = df.loc[m, [c for c in df.columns if any(k in str(c).upper() for k in ['OBJ','LIC','PROC','SESS','VENC','STAT'])]]
                print(sample.head(3))
                print()
    except Exception as e:
        pass
