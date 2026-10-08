import openpyxl

path = r'Z:\6. PREGÃO ELETRONICO e DISP. ELETRÔNICA.xlsx'
wb = openpyxl.load_workbook(path, data_only=True)
ws = wb['CONTROLE PEs e DEs']

for idx, row in enumerate(ws.iter_rows(values_only=True)):
    row_vals = [str(c).strip() for c in row if c is not None]
    row_text = " | ".join(row_vals)
    if '900' in row_text or '2026' in row_text:
        # print if it looks like a PE row
        pe_candidates = [v for v in row_vals if '900' in v or '/2026' in v or '/2025' in v]
        if pe_candidates:
            print(f"Row {idx}: {pe_candidates} -> {row_text[:180]}")
