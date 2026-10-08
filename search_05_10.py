import pandas as pd
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

fname = '6. PREGÃO ELETRONICO e DISP. ELETRÔNICA.xlsx'
df = pd.read_excel(fname, sheet_name='CONTROLE PEs e DEs', header=3)

# Search for any date in October 2026 across all date columns
date_cols = [c for c in df.columns if any(k in str(c).upper() for k in ['DATA', 'SESSÃO', 'PUBLIC', 'ABERTURA', 'REABERTURA'])]
print("Date columns:", date_cols)

found = []
for idx, r in df.iterrows():
    for c in df.columns:
        val = str(r[c])
        if '2026-10-05' in val or '05/10/2026' in val or '05/10' in val:
            found.append((idx, r.get('ANO'), r.get('Nº DA LICITAÇÃO'), r.get('Nº PROCESSO SIGA'), c, val))
        elif '2026-10' in val or '/10/2026' in val:
            found.append((idx, r.get('ANO'), r.get('Nº DA LICITAÇÃO'), r.get('Nº PROCESSO SIGA'), c, val))

print(f"Total matches for October 2026 in CONTROLE PEs e DEs: {len(found)}")
for item in found:
    print("Match:", item)
