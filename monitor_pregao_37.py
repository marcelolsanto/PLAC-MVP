# -*- coding: utf-8 -*-
import os
import sys
import json
import requests
from datetime import datetime

LOG_FILE = r"Z:\PLAC-MVP\monitor_pregao_37_log.txt"
STATE_FILE = r"Z:\PLAC-MVP\monitor_pregao_37_state.json"

LOTES_SAMPLE = {
    "Lote 1 (Centro-Oeste)": 1,
    "Lote 2 (Nordeste/Norte)": 79,
    "Lote 3 (Norte/Interior)": 157,
    "Lote 4 (Sudeste)": 239,
    "Lote 5 (Sul)": 321
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Connection': 'close',
    'Accept': 'application/json'
}

def log(msg):
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    formatted = f"[{now_str}] {msg}"
    try:
        print(formatted, flush=True)
    except Exception:
        pass
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

def run_check():
    log("==================================================================")
    log("VARREDURA EM TEMPO REAL: PREGAO ELETRONICO SRP N 37/2026 (TELEBRAS)")
    log("==================================================================")

    # 1. Arquivos / Atas
    url_atas = "https://pncp.gov.br/api/pncp/v1/orgaos/37753638000103/compras/2026/85/arquivos"
    try:
        r = requests.get(url_atas, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            arquivos = r.json()
            log(f"Documentos anexados no PNCP: {len(arquivos)}")
            for a in arquivos:
                log(f"  * [{a.get('tipoDocumentoNome')}] {a.get('titulo')} ({a.get('dataPublicacaoPncp')})")
        else:
            log(f"Consulta de arquivos retornou status {r.status_code}")
            arquivos = []
    except Exception as e:
        log(f"Erro ao buscar arquivos: {e}")
        arquivos = []

    # 2. Status dos 5 Lotes
    lote_status = {}
    tr_revelado = False
    fase_alterada = False

    for lote_nome, item_id in LOTES_SAMPLE.items():
        url_item = f"https://pncp.gov.br/api/pncp/v1/orgaos/37753638000103/compras/2026/85/itens/{item_id}"
        try:
            r = requests.get(url_item, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                item = r.json()
                sit = item.get("situacaoCompraItemNome", "Em andamento")
                sigilo = item.get("orcamentoSigiloso", True)
                val_unit = item.get("valorUnitarioEstimado", 0)
                val_tot = item.get("valorTotal", 0)
                tem_res = item.get("temResultado", False)

                lote_status[lote_nome] = {
                    "item_id": item_id,
                    "situacao": sit,
                    "sigiloso": sigilo,
                    "valor_unitario": val_unit,
                    "valor_total": val_tot,
                    "tem_resultado": tem_res
                }

                if not sigilo or (val_unit and val_unit > 0):
                    tr_revelado = True
                    log(f"[ALERTA] TR OFICIAL REVELADO no {lote_nome}! Item {item_id}: R$ {val_unit:,.2f}")
                
                if sit != "Em andamento":
                    fase_alterada = True
                    log(f"[AVISO] MUDANCA DE FASE no {lote_nome}! Nova situacao: '{sit}'")
                else:
                    log(f"  [OK] {lote_nome} (Item {item_id}): Status='{sit}' | Sigilo={sigilo} | TR={val_unit} | Resultado={tem_res}")
            else:
                log(f"Item {item_id} retornou HTTP {r.status_code}")
        except Exception as e:
            log(f"Erro item {item_id}: {e}")

    # Atualiza JSON de estado
    state = {
        "ultimo_check": datetime.now().isoformat(),
        "total_arquivos": len(arquivos),
        "tr_revelado": tr_revelado,
        "fase_alterada": fase_alterada,
        "lotes": lote_status
    }

    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    log("Varredura concluida com sucesso no Servidor Z.")
    return state

if __name__ == "__main__":
    run_check()
