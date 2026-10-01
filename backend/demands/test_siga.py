from demands.services_siga import RoboSigaService

def test_siga_service():
    print("Iniciando testes do Robô de Monitoramento do SIGA...")

    # 1. Testar listagem dos processos vigentes
    processos = RoboSigaService.listar_processos_vigentes()
    assert len(processos) >= 6, f"Esperado >= 6 processos, obtido {len(processos)}"
    print(f"[OK] 1. Total de {len(processos)} processos vigentes carregados do SIGA.")

    # 2. Testar se todos os processos possuem os campos essenciais
    for p in processos:
        assert p['numero_processo_siga'].startswith(("53000.", "TLB-PRO-")), f"Processo inválido: {p['numero_processo_siga']}"
        assert p['fase_siga'] in ['nova', 'planejamento', 'juridico', 'licitacao', 'contrato'], f"Fase inválida: {p['fase_siga']}"
        assert p['modelo_contratacao'] in ['Inexigibilidade de Licitação', 'Dispensa de Licitação', 'Credenciamento', 'Pregão Eletrônico'], f"Modelo inválido: {p['modelo_contratacao']}"
        assert len(p['documentos']) > 0, f"Processo sem documentos: {p['numero_processo_siga']}"
    print("[OK] 2. Todos os processos validados com campos e documentos estruturados.")

    # 3. Testar extração de documentos do processo Oracle
    docs_oracle = RoboSigaService.obter_documentos_processo("53000.002814/2026-31")
    assert docs_oracle['total_documentos'] == 5, f"Esperado 5 documentos, obtido {docs_oracle['total_documentos']}"
    assert any("Atestado_Exclusividade" in d['titulo'] for d in docs_oracle['documentos']), "Atestado de exclusividade não encontrado!"
    print(f"[OK] 3. Documentos do processo Oracle recuperados ({docs_oracle['total_documentos']} arquivos).")

    # 4. Testar execução da varredura do robô
    varredura = RoboSigaService.executar_varredura_siga()
    assert varredura['sucesso'] is True
    assert len(varredura['logs']) >= 5
    print(f"[OK] 4. Varredura do robô executada com {len(varredura['logs'])} logs gerados.")

    # 6. Testar processo TLB-PRO-2024/03820 e ciclo de vida contratual
    proc_dispensa = RoboSigaService.obter_rastreamento_processo("TLB-PRO-2024/03820")
    assert proc_dispensa["numero_contrato"] == "TLB-CTR-2026/00038"
    assert len(proc_dispensa["volumes_detalhes"]) == 2
    assert len(proc_dispensa["gargalos_operacao_resumo"]) == 4
    assert len(proc_dispensa["etapas_fluxo_dispensa"]) == 32
    assert "reajuste" in proc_dispensa["ciclo_vida_contratual"]
    assert "prorrogacao" in proc_dispensa["ciclo_vida_contratual"]
    assert "alteracao" in proc_dispensa["ciclo_vida_contratual"]
    assert "encerramento" in proc_dispensa["ciclo_vida_contratual"]
    print("[OK] 6. Processo TLB-PRO-2024/03820 e Ciclo de Vida Contratual validados com sucesso.")

    print("\n[SUCESSO] TODOS OS TESTES DO ROBO SIGA PASSARAM COM SUCESSO!")

if __name__ == '__main__':
    test_siga_service()
