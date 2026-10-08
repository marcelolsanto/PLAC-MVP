import os
import openpyxl

path = os.path.expanduser('~/Documentos/6. PREGÃO ELETRONICO e DISP. ELETRÔNICA.xlsx')
if not os.path.exists(path):
    # Try current dir or Z:
    path = '6. PREGÃO ELETRONICO e DISP. ELETRÔNICA.xlsx'

print("Checking file:", path)
if os.path.exists(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    print("Sheets:", wb.sheetnames)
    for sheet in wb.sheetnames:
        ws = wb[sheet]
        for idx, row in enumerate(ws.iter_rows(values_only=True)):
            row_str = ' | '.join([str(c) for c in row if c is not None])
            if '38' in row_str or '038' in row_str:
                print(f"Row {idx} in {sheet}: {row_str[:300]}")
else:
    print("File not found locally, testing other files...")
    # List Documentos
    docs = os.path.expanduser('~/Documentos')
    if os.path.exists(docs):
        print(os.listdir(docs))
