import json
from datetime import datetime

# Substituímos a leitura de planilhas pela leitura das tabelas locais do PostgreSQL (Models).

def load_plac_demands():
    from .models import Demand
    print("[*] Carregando demandas do PLAC diretamente do banco de dados...")
    return list(Demand.objects.all())

def load_contracts():
    from .models import Contract
    print("[*] Carregando contratos diretamente do banco de dados...")
    return list(Contract.objects.all())

def gerar_auditoria_adesao():
    """
    Simula o cruzamento de PLAC vs. Contratos utilizando a base de dados real
    """
    demands = load_plac_demands()
    contracts = load_contracts()

    total_demands = len(demands)
    total_contracts = len(contracts)

    aderentes = 0
    nao_aderentes = 0

    for d in demands:
        # Se tem processo SIGA com contrato ou se gerou contrato
        siga = d.siga_processes.first() if hasattr(d, 'siga_processes') else None
        if siga and siga.contratos.exists():
            aderentes += 1
        else:
            nao_aderentes += 1

    return {
        "resumo": {
            "total_demandas": total_demands,
            "total_contratos": total_contracts,
            "aderentes": aderentes,
            "nao_aderentes": nao_aderentes,
            "percentual_adesao": (aderentes / total_demands * 100) if total_demands > 0 else 0
        },
        "timestamp": datetime.now().isoformat()
    }
