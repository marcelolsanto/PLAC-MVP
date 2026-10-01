from demands.services_tribunal import julgar_enquadramento_legal, listar_amparos

def test_tribunal():
    print("Iniciando testes do Tribunal da IA...")

    # Teste 1: Fornecedor Exclusivo (Inexigibilidade Art. 74, I)
    cenario1 = {
        "objeto": "Suporte e atualização exclusiva de software proprietário Oracle Database",
        "valor_estimado": 650000.0,
        "regime_lei": "14.133/2021",
        "tipo_objeto": "SERVICO",
        "is_exclusivo": True
    }
    res1 = julgar_enquadramento_legal(cenario1)
    assert res1['veredito']['modalidade_id'] == 9, f"Esperado 9, obtido {res1['veredito']['modalidade_id']}"
    assert res1['veredito']['amparo_legal_artigo'] == "74"
    assert res1['veredito']['amparo_legal_inciso'] == "I"
    assert res1['auditoria_riscos_tcu']['nivel_risco'] == "ALTO"
    print("✅ Teste 1 (Inexigibilidade Fornecedor Exclusivo) PASSOU.")

    # Teste 2: Dispensa por Limite de Valor (Art. 75, II)
    cenario2 = {
        "objeto": "Aquisição de cadeiras ergonômicas para os operadores do NOC",
        "valor_estimado": 35000.0,
        "regime_lei": "14.133/2021",
        "tipo_objeto": "BEM",
        "is_exclusivo": False
    }
    res2 = julgar_enquadramento_legal(cenario2)
    assert res2['veredito']['modalidade_id'] == 8, f"Esperado 8, obtido {res2['veredito']['modalidade_id']}"
    assert res2['veredito']['amparo_legal_artigo'] == "75"
    assert res2['veredito']['amparo_legal_inciso'] == "II"
    assert "Fracionamento" in str(res2['auditoria_riscos_tcu']['alertas'])
    print("✅ Teste 2 (Dispensa por Valor) PASSOU.")

    # Teste 3: Credenciamento (Art. 79, I)
    cenario3 = {
        "objeto": "Credenciamento de clínicas médicas e psicológicas para exames periódicos",
        "valor_estimado": 180000.0,
        "regime_lei": "14.133/2021",
        "tipo_objeto": "SERVICO",
        "is_credenciamento": True
    }
    res3 = julgar_enquadramento_legal(cenario3)
    assert res3['veredito']['modalidade_id'] == 10, f"Esperado 10, obtido {res3['veredito']['modalidade_id']}"
    assert res3['veredito']['amparo_legal_artigo'] == "79"
    print("✅ Teste 3 (Credenciamento Art. 79) PASSOU.")

    # Teste 4: Lei das Estatais (13.303/2016) - Inexigibilidade Art. 30, II
    cenario4 = {
        "objeto": "Contratação de treinamento avançado de governança com notório jurista autor da tese",
        "valor_estimado": 45000.0,
        "regime_lei": "13.303/2016",
        "tipo_objeto": "SERVICO",
        "is_notoria_especializacao": True
    }
    res4 = julgar_enquadramento_legal(cenario4)
    assert res4['veredito']['modalidade_id'] == 9, f"Esperado 9, obtido {res4['veredito']['modalidade_id']}"
    assert res4['veredito']['amparo_legal_artigo'] == "30"
    assert res4['veredito']['amparo_legal_inciso'] == "II"
    print("✅ Teste 4 (Lei 13.303 Notória Especialização) PASSOU.")

    # Teste 5: Pregão Eletrônico (Licitação Ampla Concorrência)
    cenario5 = {
        "objeto": "Aquisição de 500 computadores portáteis tipo laptop para toda a estatal",
        "valor_estimado": 2500000.0,
        "regime_lei": "14.133/2021",
        "tipo_objeto": "BEM",
        "is_exclusivo": False
    }
    res5 = julgar_enquadramento_legal(cenario5)
    assert res5['veredito']['modalidade_id'] == 6, f"Esperado 6, obtido {res5['veredito']['modalidade_id']}"
    assert res5['veredito']['amparo_legal_artigo'] == "28"
    print("✅ Teste 5 (Pregão Eletrônico) PASSOU.")

    print("\n🎉 TODOS OS 5 TESTES DO TRIBUNAL DA IA PASSARAM COM SUCESSO!")

if __name__ == '__main__':
    test_tribunal()
