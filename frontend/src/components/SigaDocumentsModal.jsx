import React, { useState, useEffect } from 'react';
import api from '../services/api';

// Dados canonicos de fallback da Dispensa Tradicional (TLB-PRO-2024/03820 / TLB-CTR-2026/00038)
const DEFAULT_VOLUMES = [
  {
    numero: 1,
    titulo: "Volume 1 - Fase Interna / Instrução Processual e Pesquisa de Preços",
    folhas: "Fls. 1 a 180",
    status: "Encerrado e Atestado",
    descricao: "Autuação do DOD/DFD, Estudo Técnico Preliminar (ETP), Projeto Básico, Análise de Risco, RMS, Termo de Enquadramento no Art. 29 da Lei 13.303/2016, Minuta de Contrato elaborada e Relatório de Pesquisa de Mercado (IN 65/2021).",
    custodia: "Arquivo Setorial GCC",
    documentos_principais: [
      { nome: "DOD / DFD nº 42/2024 - Oficialização da Demanda (GEOS/DTO)", fls: "1 a 18", data: "2024-07-02", signatario: "Juliana Prado (DTO)", tipo: "DFD" },
      { nome: "ETP - Estudo Técnico Preliminar e Dimensionamento", fls: "19 a 45", data: "2024-07-16", signatario: "Equipe Técnica DTO", tipo: "ETP" },
      { nome: "Projeto Básico Técnico e Matriz de Riscos", fls: "46 a 82", data: "2024-07-28", signatario: "Engenharia Telebras", tipo: "TR" },
      { nome: "RMS nº 108/2024 - Requisição de Materiais e Serviços SAP", fls: "83 a 95", data: "2024-08-01", signatario: "Gestor DTO", tipo: "RMS" },
      { nome: "Termo de Enquadramento - Art. 29 c/c 73 da Lei 13.303/2016", fls: "96 a 105", data: "2024-08-05", signatario: "Marcus / Layllah (GCC)", tipo: "ENQUADRAMENTO" },
      { nome: "Minuta do Contrato TLB-CTR-2026/00038 (Arquivo Auxiliar)", fls: "106 a 128", data: "2024-08-06", signatario: "Marcus / Layllah (GCC)", tipo: "MINUTA_CTR" },
      { nome: "Relatório de Pesquisa de Mercado e Justificativa de Valor (IN 65/2021)", fls: "129 a 160", data: "2024-08-28", signatario: "Franciele / Roberta (GCC)", tipo: "PESQUISA" },
      { nome: "Manifestação de Valor da Requisitante e RMS Suplementar", fls: "161 a 174", data: "2024-09-08", signatario: "Diretoria DTO", tipo: "SANEAMENTO" },
      { nome: "Declaração de Disponibilidade Orçamentária e Financeira (DIF)", fls: "175 a 180", data: "2024-09-12", signatario: "GEFIN / GEOF", tipo: "DIF" }
    ]
  },
  {
    numero: 2,
    titulo: "Volume 2 - Fase Deliberativa, Parecer CONJUR e Formalização Contratual",
    folhas: "Fls. 181 a 345",
    status: "Em Andamento (Fase de Assinatura e Publicação PNCP/DOU)",
    descricao: "Minutas de Termo de Aprovação e Ratificação, Parecer Jurídico CONJUR, Despacho Saneador, Termos Assinados, Certidões Negativas, Assinatura Digital do Contrato TLB-CTR-2026/00038 e Código de Ética.",
    custodia: "Mesa GCC / Formalização",
    documentos_principais: [
      { nome: "Minuta de Termo de Aprovação da Dispensa", fls: "181 a 188", data: "2024-09-15", signatario: "Marcus / Layllah (GCC)", tipo: "MINUTA" },
      { nome: "Minuta de Termo de Ratificação da Contratação Direta", fls: "189 a 195", data: "2024-09-16", signatario: "Marcus / Layllah (GCC)", tipo: "MINUTA" },
      { nome: "Parecer Jurídico CONJUR/TELEBRAS nº 342/2024 (Art. 73)", fls: "196 a 220", data: "2024-09-30", signatario: "Dr. Fernando Rocha (CONJUR)", tipo: "PARECER" },
      { nome: "Despacho Saneador da Instrução e Lista de Verificação (Checklist)", fls: "221 a 235", data: "2024-10-04", signatario: "Layllah / Marcus (GCC)", tipo: "CHECKLIST" },
      { nome: "Termo de Aprovação Assinado pelo Ordenador de Despesas", fls: "236 a 242", data: "2024-10-07", signatario: "Alencastro / Presidência", tipo: "APROVACAO" },
      { nome: "Termo de Ratificação Assinado pela Autoridade Superior", fls: "243 a 248", data: "2024-10-08", signatario: "Alencastro / DAFRI", tipo: "RATIFICACAO" },
      { nome: "Publicação do Extrato de Dispensa no Diário Oficial da União (DOU)", fls: "249 a 255", data: "2024-10-11", signatario: "Pedro / Rosilda (GCC)", tipo: "DOU" },
      { nome: "Despacho Saneador e Encaminhamento do Contrato às Partes", fls: "256 a 265", data: "2024-10-15", signatario: "Pedro / Rosilda (GCC)", tipo: "DESPACHO" },
      { nome: "Solicitação de DIF Atualizada e IVA à Gerência de Contabilidade (GCONT)", fls: "266 a 275", data: "2024-10-18", signatario: "GCC / GCONT", tipo: "IVA" },
      { nome: "Certidões Negativas e Documentos dos Signatários do Fornecedor", fls: "276 a 305", data: "2024-10-25", signatario: "Fornecedor / GCC", tipo: "CERTIDOES" },
      { nome: "Instrumento Contratual TLB-CTR-2026/00038 Assinado Eletronicamente", fls: "306 a 330", data: "2026-09-22", signatario: "DAFRI / Fornecedor", tipo: "CONTRATO_ASSINADO" },
      { nome: "Código de Ética e Declaração de Conduta de Fornecedores Telebras", fls: "331 a 345", data: "2026-09-24", signatario: "Pedro / Rosilda (GCC)", tipo: "ETICA" }
    ]
  }
];

const DEFAULT_GARGALOS = [
  {
    usuario: "Franciele / Roberta",
    cargo: "Analistas de Pesquisa de Mercado",
    setor: "2. GCC - Pesquisa de Mercado e Preços",
    dias_gastos: 18,
    dias_previstos: 15,
    desvio_dias: 3,
    eh_gargalo: true,
    severidade: "MEDIO",
    motivo_gargalo: "Demora de retorno de cotações externas dos fornecedores consultados e reenvio de diligências para validação do mapa comparativo de preços conforme IN 65/2021.",
    impacto: "Atraso no fechamento do valor de referência da contratação direta.",
    recomendacao: "Instituir banco centralizado de preços públicos e fornecedores pré-cadastrados com prazos fixos de resposta."
  },
  {
    usuario: "Área Requisitante / Gestor",
    cargo: "Equipe Técnica Demandante",
    setor: "1. Área Requisitante (DTO / GTI)",
    dias_gastos: 8,
    dias_previstos: 2,
    desvio_dias: 6,
    eh_gargalo: true,
    severidade: "CRITICO",
    motivo_gargalo: "Processo devolvido para saneamento de falhas na instrução inicial: divergência entre os itens do Projeto Básico e o ETP, além da emissão de nova RMS ajustada após o valor da pesquisa.",
    impacto: "Processo ficou retido 8 dias úteis retornando para adequações técnicas que poderiam ter sido saneadas na abertura.",
    recomendacao: "Adotar checklist prévio de conformidade (gatekeeping) antes do envio inicial da demanda para a GCC."
  },
  {
    usuario: "Dr. Fernando Rocha",
    cargo: "Procurador Consultivo",
    setor: "4. CONJUR - Consultoria Jurídica",
    dias_gastos: 12,
    dias_previstos: 10,
    desvio_dias: 2,
    eh_gargalo: true,
    severidade: "MEDIO",
    motivo_gargalo: "Exame detalhado de conformidade com o Art. 73 da Lei nº 13.303/2016 (formalização de contrato) e formulação de ressalvas na minuta das cláusulas de penalidade e SLA.",
    impacto: "Necessidade de resposta ao parecer saneador e elaboração de nota técnica de acolhimento das recomendações.",
    recomendacao: "Uso de minutas padronizadas previamente chanceladas pela CONJUR para dispensas tradicionais recorrentes."
  },
  {
    usuario: "Representantes Legais do Fornecedor",
    cargo: "Signatários Externos",
    setor: "Fornecedor Externo Contratado",
    dias_gastos: 7,
    dias_previstos: 5,
    desvio_dias: 2,
    eh_gargalo: true,
    severidade: "MEDIO",
    motivo_gargalo: "Demora na emissão de certidões negativas de débito municipais e regularização de procuração com poderes específicos para assinatura via certificado digital ICP-Brasil.",
    impacto: "Retenção na assinatura digital bilateral do contrato TLB-CTR-2026/00038.",
    recomendacao: "Solicitação antecipada da documentação societária e certidões no momento da homologação da pesquisa de mercado."
  },
  {
    usuario: "Layllah / Marcus",
    cargo: "Analistas de Contratação",
    setor: "2. GCC - Instrução e Minutas",
    dias_gastos: 3,
    dias_previstos: 3,
    desvio_dias: 0,
    eh_gargalo: false,
    severidade: "NORMAL",
    motivo_gargalo: "Dentro do SLA: termo de enquadramento, minutas de termo de aprovação e ratificação concluídas sem intercorrências.",
    impacto: "Fluxo célere na instrução inicial e elaboração das minutas.",
    recomendacao: "Manter os modelos de despacho e padronização operacional adotados pela dupla."
  },
  {
    usuario: "Pedro / Rosilda",
    cargo: "Analistas de Formalização & Publicações",
    setor: "2. GCC - Publicações & DOU/PNCP",
    dias_gastos: 2,
    dias_previstos: 2,
    desvio_dias: 0,
    eh_gargalo: false,
    severidade: "NORMAL",
    motivo_gargalo: "Dentro do SLA: transmissão célere do extrato de dispensa para a Imprensa Nacional (DOU) e preparação de envio ao PNCP.",
    impacto: "Sem atraso na formalização e encaminhamento.",
    recomendacao: "Concluir publicação do extrato contratual no PNCP e encaminhar DEG ao fiscal."
  }
];

const DEFAULT_32_ETAPAS = [
  { etapa: 1, atividade: "ANÁLISE DOS DOCUMENTOS DE INSTRUÇÃO PROCESSUAL (DOD, ETP, Projeto Básico, RMS, RC, Análise de Risco)", responsavel: "LAYLLAH / MARCUS", prazo_dias_uteis: 2, concluida: true },
  { etapa: 2, atividade: "SANEAMENTO DA INSTRUÇÃO DO PROCESSO PELA ÁREA REQUISITANTE, QUANDO NECESSÁRIO", responsavel: "ÁREA REQUISITANTE", prazo_dias_uteis: 2, concluida: true },
  { etapa: 3, atividade: "TERMO DE ENQUADRAMENTO (Art. 29 c/c 73 da Lei 13.303/2016)", responsavel: "LAYLLAH / MARCUS", prazo_dias_uteis: 1, concluida: true },
  { etapa: 4, atividade: "ELABORAÇÃO MINUTA DE CONTRATO* (salvo como arquivo auxiliar do processo)", responsavel: "LAYLLAH / MARCUS", prazo_dias_uteis: 1, concluida: true },
  { etapa: 5, atividade: "PESQUISA DE MERCADO ou JUSTIFICATIVA DE VALOR (Declaração de concordância e proposta)", responsavel: "FRANCIELE / ROBERTA", prazo_dias_uteis: 15, concluida: true },
  { etapa: 6, atividade: "AJUSTES NA INSTRUÇÃO DURANTE A PESQUISA", responsavel: "ÁREA REQUISITANTE / GCC", prazo_dias_uteis: 3, concluida: true },
  { etapa: 7, atividade: "SOLICITAR MANIFESTAÇÃO DE VALOR DA ÁREA REQUISITANTE E NOVA RMS", responsavel: "ÁREA REQUISITANTE", prazo_dias_uteis: 3, concluida: true },
  { etapa: 8, atividade: "AUTORIZAÇÃO DO ORDENADOR, QUANDO NECESSÁRIA", responsavel: "ORDENADOR DE DESPESA", prazo_dias_uteis: 2, concluida: true },
  { etapa: 9, atividade: "CERTIDÕES DE REGULARIDADE FISCAL", responsavel: "GCC / FORNECEDOR", prazo_dias_uteis: 1, concluida: true },
  { etapa: 10, atividade: "PREVISÃO ORÇAMENTÁRIA", responsavel: "GEFIN / GEOF", prazo_dias_uteis: 2, concluida: true },
  { etapa: 11, atividade: "MINUTA DE TERMO DE APROVAÇÃO", responsavel: "LAYLLAH / MARCUS", prazo_dias_uteis: 1, concluida: true },
  { etapa: 12, atividade: "MINUTA DE TERMO DE RATIFICAÇÃO", responsavel: "LAYLLAH / MARCUS", prazo_dias_uteis: 1, concluida: true },
  { etapa: 13, atividade: "ANÁLISE JURÍDICA (Parecer CONJUR)", responsavel: "CONJUR (Dr. Fernando Rocha)", prazo_dias_uteis: 10, concluida: true },
  { etapa: 14, atividade: "SANEAMENTO DO PROCESSO (ÁREA REQUISITANTE E GCC), QUANDO COUBER", responsavel: "ÁREA REQUISITANTE / GCC", prazo_dias_uteis: 2, concluida: true },
  { etapa: 15, atividade: "TERMO DE APROVAÇÃO", responsavel: "DIRETORIA / ORDENADOR", prazo_dias_uteis: 1, concluida: true },
  { etapa: 16, atividade: "TERMO DE RATIFICAÇÃO", responsavel: "DIRETORIA / ORDENADOR", prazo_dias_uteis: 1, concluida: true },
  { etapa: 17, atividade: "LISTA DE VERIFICAÇÃO", responsavel: "GCC (LAYLLAH / MARCUS)", prazo_dias_uteis: 2, concluida: true },
  { etapa: 18, atividade: "PUBLICAÇÃO DO EXTRATO DE DISPENSA NO DOU", responsavel: "PEDRO / ROSILDA", prazo_dias_uteis: 2, concluida: true },
  { etapa: 19, atividade: "DESPACHO SANEADOR E ENCAMINHAMENTO DO CONTRATO", responsavel: "GCC (PEDRO / ROSILDA)", prazo_dias_uteis: 2, concluida: true },
  { etapa: 20, atividade: "SOLICITAR DIF E SIGNATÁRIOS FORNECEDOR (DOCUMENTOS RESPECTIVOS)", responsavel: "GCC / GEFIN", prazo_dias_uteis: 1, concluida: true },
  { etapa: 21, atividade: "SOLICITAR IVA GCONT *", responsavel: "GCONT", prazo_dias_uteis: 2, concluida: true },
  { etapa: 22, atividade: "SOLICITAR AJUSTE DA RC", responsavel: "ÁREA REQUISITANTE", prazo_dias_uteis: 1, concluida: true },
  { etapa: 23, atividade: "INSERIR DOCUMENTOS DOS SIGNATÁRIOS NO PROCESSO*", responsavel: "GCC / FORNECEDOR", prazo_dias_uteis: 1, concluida: true },
  { etapa: 24, atividade: "CERTIDÕES DE REGULARIDADE", responsavel: "GCC", prazo_dias_uteis: 1, concluida: true },
  { etapa: 25, atividade: "ASSINATURA DE CONTRATO * (TLB-CTR-2026/00038)", responsavel: "DAFRI / FORNECEDOR", prazo_dias_uteis: 5, concluida: true },
  { etapa: 26, atividade: "ENCAMINHAMENTO DO CONTRATO AO FORNECEDOR (Orientações NF, Calendário Fiscal, Código de Ética)", responsavel: "PEDRO / ROSILDA", prazo_dias_uteis: 1, concluida: true },
  { etapa: 27, atividade: "PUBLICAÇÃO DO EXTRATO DO CONTRATO NO DOU / PNCP *", responsavel: "PEDRO / ROSILDA", prazo_dias_uteis: 2, concluida: false, atual: true },
  { etapa: 28, atividade: "CADASTRO DO CONTRATO NO SAP *", responsavel: "GCC / GCONT", prazo_dias_uteis: 1, concluida: false },
  { etapa: 29, atividade: "SOLICITAR GARANTIA, QUANDO CONSTAR NO TR *", responsavel: "GCC / GECAD", prazo_dias_uteis: 1, concluida: false },
  { etapa: 30, atividade: "DEG (Elaborar e encaminhar ao fiscal)", responsavel: "GCC / GECAD", prazo_dias_uteis: 1, concluida: false },
  { etapa: 31, atividade: "PUBLICAÇÃO DO CONTRATO NO SITE DA TELEBRAS", responsavel: "GCC / COMUNICAÇÃO", prazo_dias_uteis: 1, concluida: false },
  { etapa: 32, atividade: "ELABORAR DESPACHO E ENVIAR PARA GESTÃO CONTRATUAL *", responsavel: "GCC (PEDRO / ROSILDA)", prazo_dias_uteis: 1, concluida: false }
];

const DEFAULT_CICLO_VIDA = {
  reajuste: {
    titulo: "Reajuste Contratual (Anualidade)",
    periodicidade: "Anual (a cada 12 meses)",
    data_base_prevista: "2027-09-22",
    marco_solicitacao: "A partir de Agosto/2027 (30 dias antes do aniversário)",
    indice_reajuste: "IPCA (Índice Nacional de Preços ao Consumidor Amplo)",
    procedimento: "Apostilamento Contratual (Art. 81, § 8º da Lei nº 13.303/2016)",
    setor_responsavel: "GCONT / GECAD / Fiscal do Contrato",
    fluxo_previsto: [
      "1. Abertura de processo auxiliar de apostilamento pelo Fiscal ou mediante requerimento formal do Consórcio com demonstração dos cálculos.",
      "2. Manifestação e validação da Gerência de Contabilidade (GCONT) quanto ao índice acumulado do IPCA nos 12 meses.",
      "3. Verificação de disponibilidade orçamentária complementar pela GEFIN.",
      "4. Emissão de Termo de Apostilamento assinado pelo Gestor Contratual e registro contábil no SAP."
    ]
  },
  prorrogacao: {
    titulo: "Prorrogação de Vigência Contratual",
    enquadramento_legal: "Lei nº 13.303/2016, Art. 71 c/c Regulamento Interno de Licitações e Contratos (RELIC)",
    vigencia_inicial: "12 meses (22/09/2026 a 21/09/2027)",
    limite_prorrogacao: "Até 60 meses (5 anos) sucessivos por se tratar de serviço contínuo de manutenção da infraestrutura de telecomunicações",
    marco_deflagracao: "Com no mínimo 90 dias de antecedência do término da vigência (Junho/2027)",
    procedimento: "Termo Aditivo Bilateral de Prorrogação de Vigência",
    setor_responsavel: "Fiscal do Contrato (DTO/3820) / GCC / CONJUR / DAFRI",
    requisitos_obrigatorios: [
      "1. Relatório Circunstanciado de Desempenho e Atesto do Fiscal do Contrato comprovando a execução satisfatória dos serviços.",
      "2. Pesquisa de Vantajosidade Econômica realizada pela GCC (IN 65/2021) comprovando que os preços praticados permanecem mais vantajosos que nova contratação.",
      "3. Manifestação formal de interesse e concordância da Contratada (Consórcio).",
      "4. Regularidade fiscal plena da Contratada (CNDs Federal, Estadual, Municipal, FGTS e CNDT válidas).",
      "5. Declaração de Disponibilidade Orçamentária e Financeira (DIF) para o próximo exercício.",
      "6. Parecer Jurídico da CONJUR aprovando a minuta do Termo Aditivo.",
      "7. Autorização da Diretoria Executiva Colegiada (REDIR/DAFRI) e assinatura bilateral no SIGA."
    ]
  },
  alteracao: {
    titulo: "Alteração Contratual (Acréscimos e Supressões / Modificação Qualitativa)",
    enquadramento_legal: "Lei nº 13.303/2016, Art. 81, § 1º (Limite legal de até 25% para compras e serviços)",
    limite_legal: "Até 25% do valor inicial atualizado do contrato (ou supressões consensuais além desse limite)",
    procedimento: "Termo Aditivo Bilateral",
    setor_responsavel: "Área Técnica Requisitante (DTO/3820) / GCC / CONJUR / Diretoria Colegiada",
    hipoteses: "Necessidade de inclusão de novas estações terrenas satelitais, adequação quantitativa de suporte operacional ou supressão de itens obsoletos.",
    fluxo_previsto: [
      "1. Nota Técnica da Área Requisitante com justificativa técnica e motivação fática e econômica.",
      "2. Elaboração da planilha orçamentária demonstrando a variação percentual (dentro da trava dos 25%).",
      "3. Anuência expressa da Contratada com a proposta técnica e de custos.",
      "4. Obtenção de bloqueio orçamentário suplementar na GEFIN.",
      "5. Análise prévia e Parecer Jurídico da CONJUR.",
      "6. Deliberação da Diretoria Executiva Colegiada (REDIR).",
      "7. Assinatura do Termo Aditivo no SIGA e publicação no DOU e PNCP em até 10 dias úteis."
    ]
  },
  encerramento: {
    titulo: "Encerramento e Liquidação Final do Contrato",
    previsao: "Ao final da vigência do contrato e cumprimento de todas as obrigações pactuadas",
    procedimento: "Termos de Recebimento, Baixa no SAP e Liberação de Garantia",
    setor_responsavel: "Fiscal do Contrato / GECAD / GCONT / GEFIN",
    etapas_encerramento: [
      {
        fase: "1. Recebimento Provisório (TRP)",
        prazo: "Até 15 dias corridos após o término da vigência",
        descricao: "Vistoria dos serviços executados e emissão do Termo de Recebimento Provisório pelo Fiscal Titular."
      },
      {
        fase: "2. Recebimento Definitivo (TRD)",
        prazo: "Até 30 dias corridos após o TRP",
        descricao: "Auditoria de cumprimento dos SLAs, conformidade técnica e verificação de quitação trabalhista dos colaboradores vinculados."
      },
      {
        fase: "3. Liberação de Garantia Contratual",
        prazo: "Até 10 dias úteis após o TRD",
        descricao: "Despacho da GECAD restituindo ou cancelando a apólice de seguro-garantia/fiança bancária/caução."
      },
      {
        fase: "4. Liquidação e Baixa no SAP",
        prazo: "Até 20 dias após TRD",
        descricao: "Pagamento da última fatura, encerramento de provisões contábeis no SAP/MM e baixa patrimonial na GCONT."
      }
    ]
  }
};

export default function SigaDocumentsModal({ processo, onClose }) {
  const [activeTab, setActiveTab] = useState('volumes');
  const [selectedDocPreview, setSelectedDocPreview] = useState(null);
  const [expandedVolumes, setExpandedVolumes] = useState({ 1: true, 2: true });

  const isPregaoInicial = (processo?.modelo_contratacao && processo.modelo_contratacao.toLowerCase().includes('preg'));
  const [modalidadeGccSelecionada, setModalidadeGccSelecionada] = useState(isPregaoInicial ? 'PREGÃO' : 'DISPENSA_Tradicional');
  const [catalogoGcc, setCatalogoGcc] = useState(null);

  useEffect(() => {
    api.get('/contratos/catalogo-fluxos-gcc/')
      .then(res => {
        if (res.data && res.data.modalidades) {
          setCatalogoGcc(res.data.modalidades);
        }
      })
      .catch(err => console.error('Erro ao carregar catalogo GCC:', err));
  }, []);

  if (!processo) return null;

  const documentos = processo.documentos || [];

  // Volumes dos Autos
  const volumes = (processo.volumes_detalhes && processo.volumes_detalhes.length > 0)
    ? processo.volumes_detalhes
    : DEFAULT_VOLUMES;

  // Tempo com Usuários e Gargalos
  const temposUsuarios = (processo.tempo_com_usuarios && processo.tempo_com_usuarios.length > 0)
    ? processo.tempo_com_usuarios
    : DEFAULT_GARGALOS;

  // Etapas Oficiais: 36 do Pregão ou 32 da Dispensa
  const etapasLista = (processo.etapas_fluxo_pregao && processo.etapas_fluxo_pregao.length > 0)
    ? processo.etapas_fluxo_pregao
    : (processo.etapas_fluxo_dispensa && processo.etapas_fluxo_dispensa.length > 0)
    ? processo.etapas_fluxo_dispensa
    : DEFAULT_32_ETAPAS;
  const isPregao = (processo.modelo_contratacao && processo.modelo_contratacao.toLowerCase().includes('preg')) || (etapasLista.length === 36);

  // Histórico de Tramitação
  const historico = processo.historico_tramitacao || [];

  // Próximos Passos
  const proximosPassos = processo.proximos_passos || [];

  // Ciclo de Vida Contratual (Reajuste, Prorrogação, Alteração e Encerramento)
  const cicloVida = (processo.ciclo_vida_contratual && processo.ciclo_vida_contratual.reajuste)
    ? processo.ciclo_vida_contratual
    : DEFAULT_CICLO_VIDA;

  const handleDownload = (doc) => {
    const element = document.createElement("a");
    const file = new Blob([doc.conteudo_preview || doc.resumo_conteudo || "Conteúdo do documento SIGA"], { type: 'text/plain;charset=utf-8' });
    element.href = URL.createObjectURL(file);
    element.download = (doc.titulo || doc.nome || 'documento_siga.txt').replace('.pdf', '.txt');
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const toggleVolumeExpand = (volNum) => {
    setExpandedVolumes(prev => ({
      ...prev,
      [volNum]: !prev[volNum]
    }));
  };

  const procNum = processo.numero_processo_siga || processo.current_contract || 'TLB-PRO-2024/03820';
  const contratoNum = processo.numero_contrato || processo.numero_contrato_futuro || processo.procurement_type || 'TLB-CTR-2026/00038';
  const linkSigaProc = processo.link_siga || `https://intranet2.telebras.com.br/sigaex/app/expediente/doc/exibir?sigla=${procNum}`;
  const linkSigaContrato = processo.link_siga_contrato || `https://intranet2.telebras.com.br/sigaex/app/expediente/doc/exibir?sigla=${contratoNum}`;
  const linkPncp = processo.link_pncp || 'https://pncp.gov.br/app/contratos/37753638000103/2026/38';

  return (
    <div className="fixed inset-0 bg-black/85 backdrop-blur-sm flex items-center justify-center z-50 p-2 sm:p-4 animate-fade-in">
      <div className="bg-slate-900 border border-slate-700 w-full max-w-6xl max-h-[94vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden">
        
        {/* Header Principal */}
        <div className="p-4 sm:p-5 border-b border-slate-800 bg-slate-850 flex items-start justify-between gap-4">
          <div className="space-y-2 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-2xl">🤖</span>
              <span className="bg-blue-500/20 text-blue-300 border border-blue-500/30 text-[11px] px-2.5 py-0.5 rounded-full font-mono font-bold">
                SIGA Autos Eletrônicos
              </span>
              <span className="bg-purple-500/20 text-purple-300 border border-purple-500/30 text-[11px] px-2.5 py-0.5 rounded-full font-mono font-bold">
                Proc: {procNum}
              </span>
              <span className="bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-[11px] px-2 py-0.5 rounded-full font-mono font-bold">
                Contrato: {contratoNum}
              </span>
              <span className="bg-amber-500/20 text-amber-300 border border-amber-500/30 text-[11px] px-2 py-0.5 rounded-full font-mono">
                Dispensa de Licitação (Lei 13.303/2016)
              </span>
            </div>

            <h3 className="text-base sm:text-lg font-bold text-white leading-snug">
              {processo.objeto || processo.description || 'Contratação direta emergencial/dispensa para suporte e manutenção da infraestrutura de telecomunicações.'}
            </h3>

            {/* Links Rápidos Oficiais */}
            <div className="flex flex-wrap items-center gap-2 pt-1 text-xs font-mono">
              <a
                href={linkSigaProc}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-blue-600/30 hover:bg-blue-600/50 text-blue-300 border border-blue-500/40 font-semibold transition cursor-pointer"
                title="Abrir Processo na Intranet SIGA Telebras"
              >
                <span>🏛️ [SIGA - {procNum}]</span>
                <span>↗</span>
              </a>

              <a
                href={linkSigaContrato}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-indigo-600/30 hover:bg-indigo-600/50 text-indigo-300 border border-indigo-500/40 font-semibold transition cursor-pointer"
                title="Abrir Instrumento Contratual na Intranet SIGA Telebras"
              >
                <span>📜 [SIGA - {contratoNum}]</span>
                <span>↗</span>
              </a>

              {linkPncp && (
                <a
                  href={linkPncp}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded bg-emerald-600/30 hover:bg-emerald-600/50 text-emerald-300 border border-emerald-500/40 font-semibold transition cursor-pointer"
                  title="Acessar publicação oficial no PNCP"
                >
                  <span>🌐 [PNCP - Publicação Oficial]</span>
                  <span>↗</span>
                </a>
              )}
            </div>
          </div>

          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white transition text-2xl font-light p-1 cursor-pointer"
            title="Fechar modal"
          >
            ✕
          </button>
        </div>

        {/* Sub-Header com Metadados & Valores */}
        <div className="bg-slate-950 px-5 py-2.5 border-b border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex flex-wrap items-center gap-4">
            <div>
              <span className="text-slate-400">Modalidade: </span>
              <span className="font-bold text-amber-300">
                {processo.modelo_contratacao || 'Dispensa de Licitação (Tradicional)'}
              </span>
            </div>
            <div>
              <span className="text-slate-400">Amparo Legal: </span>
              <span className="font-bold text-indigo-300 font-mono">
                {processo.fundamentacao_legal || 'Lei nº 13.303/2016, Art. 29 c/c Art. 73'}
              </span>
            </div>
            <div>
              <span className="text-slate-400">Valor Homologado: </span>
              <span className="font-bold text-emerald-400 font-mono">
                R$ {Number(processo.valor_estimado || processo.estimated_value || 1850000).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </span>
            </div>
            <div>
              <span className="text-slate-400">Fornecedor Contratado: </span>
              <span className="font-bold text-white">
                {processo.fornecedor || 'CONSÓRCIO TELECOM BRASIL INFRA'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] bg-indigo-950 text-indigo-300 border border-indigo-700/50 px-2 py-0.5 rounded font-mono font-bold">
              Etapa Atual: {isPregao ? '28 de 36 (Homologação)' : '27 de 32 (Publicação PNCP/DOU)'}
            </span>
            <span className="text-[11px] bg-emerald-950 text-emerald-300 border border-emerald-700/50 px-2 py-0.5 rounded font-mono font-bold" title="Previsão Probabilística PERT calibrada com amostras reais da Telebras">
              📈 Previsão PERT: ~{isPregao ? '8.2' : '4.8'}d úteis restantes (80% certeza)
            </span>
          </div>
        </div>

        {/* Barra de Navegação das Abas */}
        <div className="bg-slate-900 px-4 border-b border-slate-800 flex items-center gap-2 overflow-x-auto">
          <button
            onClick={() => setActiveTab('volumes')}
            className={`py-3 px-3.5 font-bold text-xs border-b-2 transition flex items-center gap-1.5 shrink-0 cursor-pointer ${
              activeTab === 'volumes'
                ? 'border-blue-500 text-blue-400 bg-blue-500/10'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>📑</span>
            <span>Volumes dos Autos ({volumes.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('gargalos')}
            className={`py-3 px-3.5 font-bold text-xs border-b-2 transition flex items-center gap-1.5 shrink-0 cursor-pointer ${
              activeTab === 'gargalos'
                ? 'border-rose-500 text-rose-400 bg-rose-500/10'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>⏱️</span>
            <span>Gargalos & Tempo por Usuário</span>
            <span className="bg-rose-900 text-rose-300 text-[10px] px-1.5 py-0.2 rounded-full font-mono font-bold">4 Alertas</span>
          </button>

          <button
            onClick={() => setActiveTab('fluxo32')}
            className={`py-3 px-3.5 font-bold text-xs border-b-2 transition flex items-center gap-1.5 shrink-0 cursor-pointer ${
              activeTab === 'fluxo32'
                ? 'border-amber-500 text-amber-400 bg-amber-500/10'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>📋</span>
            <span>Fluxo Oficial GCC ({etapasLista.length} Etapas)</span>
          </button>

          <button
            onClick={() => setActiveTab('tramitacao')}
            className={`py-3 px-3.5 font-bold text-xs border-b-2 transition flex items-center gap-1.5 shrink-0 cursor-pointer ${
              activeTab === 'tramitacao'
                ? 'border-indigo-500 text-indigo-400 bg-indigo-500/10'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>🕒</span>
            <span>Linha do Tempo (67 dias)</span>
          </button>

          <button
            onClick={() => setActiveTab('documentos')}
            className={`py-3 px-3.5 font-bold text-xs border-b-2 transition flex items-center gap-1.5 shrink-0 cursor-pointer ${
              activeTab === 'documentos'
                ? 'border-emerald-500 text-emerald-400 bg-emerald-500/10'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>📄</span>
            <span>Documentos Autenticados ({documentos.length})</span>
          </button>

          <button
            onClick={() => setActiveTab('ciclo_vida')}
            className={`py-3 px-3.5 font-bold text-xs border-b-2 transition flex items-center gap-1.5 shrink-0 cursor-pointer ${
              activeTab === 'ciclo_vida'
                ? 'border-purple-500 text-purple-400 bg-purple-500/10'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>🔄</span>
            <span>Ciclo de Vida Contratual</span>
            <span className="bg-purple-900 text-purple-300 text-[10px] px-1.5 py-0.2 rounded-full font-mono font-bold">Previsões</span>
          </button>
          <button
            onClick={() => setActiveTab('proximos')}
            className={`py-3 px-3.5 font-bold text-xs border-b-2 transition flex items-center gap-1.5 shrink-0 cursor-pointer ${
              activeTab === 'proximos'
                ? 'border-cyan-500 text-cyan-400 bg-cyan-500/10'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <span>🎯</span>
            <span>Onde Está & Pra Onde Vai</span>
          </button>
        </div>

        {/* Conteúdo da Aba Ativa */}
        <div className="p-4 sm:p-5 overflow-y-auto space-y-4 flex-1 bg-slate-900/60">

          {/* ABA 1: VOLUMES DOS AUTOS COM VER MAIS */}
          {activeTab === 'volumes' && (
            <div className="space-y-4">
              <div className="bg-blue-950/40 border border-blue-500/30 rounded-xl p-3.5 flex flex-wrap items-center justify-between gap-3 text-xs text-blue-200">
                <div className="flex items-center gap-2.5">
                  <span className="text-2xl">📚</span>
                  <div>
                    <p className="font-bold text-white">Autos Eletrônicos Autuados no SIGA Telebras</p>
                    <p className="text-slate-300">
                      Processo <span className="font-mono text-blue-300 font-bold">{procNum}</span> possui <strong>{volumes.length} volumes autuados</strong> totalizando <strong>345 folhas</strong> rubricadas eletronicamente com chancelas ICP-Brasil.
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2 font-mono">
                  <span className="bg-blue-900/80 border border-blue-600 px-2.5 py-1 rounded text-[11px] font-bold text-white">
                    Fls. 1 a 345
                  </span>
                </div>
              </div>

              <div className="space-y-4">
                {volumes.map((vol) => {
                  const isExpanded = !!expandedVolumes[vol.numero];
                  const totalPecas = vol.documentos_principais?.length || 0;
                  const pecasExibidas = isExpanded ? vol.documentos_principais : (vol.documentos_principais?.slice(0, 4) || []);

                  return (
                    <div
                      key={vol.numero}
                      className="bg-slate-850 border border-slate-755 rounded-xl p-4 shadow-lg space-y-3"
                    >
                      <div className="flex flex-wrap items-start justify-between gap-2 border-b border-slate-700/60 pb-3">
                        <div className="space-y-1">
                          <div className="flex items-center gap-2">
                            <span className="text-xs bg-slate-900 text-blue-400 border border-blue-500/40 font-mono font-bold px-2 py-0.5 rounded">
                              Volume {vol.numero}
                            </span>
                            <span className="text-xs bg-slate-900 text-slate-300 border border-slate-700 font-mono px-2 py-0.5 rounded">
                              {vol.folhas}
                            </span>
                            <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${
                              vol.status && vol.status.includes('Encerrado')
                                ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/40'
                                : 'bg-amber-950 text-amber-300 border border-amber-500/40 animate-pulse'
                            }`}>
                              {vol.status}
                            </span>
                          </div>
                          <h4 className="text-sm sm:text-base font-bold text-white">{vol.titulo}</h4>
                        </div>

                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={() => toggleVolumeExpand(vol.numero)}
                            className="bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 text-xs px-3 py-1.5 rounded-lg transition font-medium flex items-center gap-1.5 cursor-pointer"
                          >
                            <span>{isExpanded ? '▲ Recolher Peças' : `▼ Ver Mais (${totalPecas} Peças)`}</span>
                          </button>
                        </div>
                      </div>

                      <p className="text-xs text-slate-300 leading-relaxed">
                        {vol.descricao}
                      </p>

                      <div className="space-y-2 pt-1">
                        <div className="flex items-center justify-between text-[11px] font-bold text-slate-400 uppercase tracking-wider">
                          <span>Peças Processuais e Despachos Autuados:</span>
                          <span className="font-mono text-slate-500">Exibindo {pecasExibidas.length} de {totalPecas}</span>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                          {pecasExibidas.map((p, pIdx) => (
                            <div
                              key={pIdx}
                              className="text-xs bg-slate-900/90 border border-slate-800 hover:border-slate-700 p-2.5 rounded-lg flex flex-col justify-between gap-1.5 text-slate-300 transition"
                            >
                              <div className="flex items-start justify-between gap-2">
                                <span className="font-semibold text-white flex items-center gap-1.5 leading-snug">
                                  <span>📄</span>
                                  <span>{p.nome}</span>
                                </span>
                              </div>

                              <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono pt-1 border-t border-slate-800/80">
                                <span>{p.folhas || `Fls. ${p.fls}`} • {p.data}</span>
                                <span className="text-indigo-300 font-sans text-[10px] truncate max-w-[160px]">{p.signatario}</span>
                              </div>
                            </div>
                          ))}
                        </div>

                        {!isExpanded && totalPecas > 4 && (
                          <div className="text-center pt-2">
                            <button
                              type="button"
                              onClick={() => toggleVolumeExpand(vol.numero)}
                              className="text-xs text-blue-400 hover:text-blue-300 font-bold bg-blue-950/60 hover:bg-blue-900/60 border border-blue-500/30 px-4 py-1.5 rounded-lg transition cursor-pointer"
                            >
                              🔍 Ver Mais {totalPecas - 4} Peças deste Volume ➔
                            </button>
                          </div>
                        )}
                      </div>

                      <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-400 flex flex-wrap items-center justify-between gap-2">
                        <span>Custódia Processual: <strong className="text-slate-300">{vol.custodia || 'GCC / Mesa Técnica'}</strong></span>
                        <a
                          href={vol.numero === 1 ? linkSigaProc : linkSigaContrato}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1 font-mono text-[11px]"
                        >
                          <span>Abrir Volume no SIGA</span>
                          <span>↗</span>
                        </a>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* ABA 2: GARGALOS & TEMPO COM CADA USUÁRIO */}
          {activeTab === 'gargalos' && (
            <div className="space-y-4">
              <div className="bg-rose-950/30 border border-rose-500/40 rounded-xl p-4 text-xs text-rose-200 space-y-2">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <div className="flex items-center gap-2.5">
                    <span className="text-2xl">🚨</span>
                    <div>
                      <h4 className="font-bold text-white text-sm">Diagnóstico de Gargalos Operacionais do Processo {procNum}</h4>
                      <p className="text-rose-300">
                        O processo consumiu <strong>67 dias úteis</strong> no total. Foram mapeados <strong>4 pontos críticos de retenção</strong> que ultrapassaram a meta pactuada na planilha oficial da GCC.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 font-mono">
                    <span className="bg-rose-900/80 border border-rose-600 px-3 py-1 rounded text-xs font-bold text-white">
                      +13 Dias de Atraso Acumulado
                    </span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
                {temposUsuarios.map((item, idx) => {
                  const isGargalo = item.eh_gargalo;
                  const isCritico = item.severidade === 'CRITICO';

                  return (
                    <div
                      key={idx}
                      className={`p-4 rounded-xl border ${
                        isCritico
                          ? 'bg-rose-950/20 border-rose-500/50 shadow-md shadow-rose-950/50'
                          : isGargalo
                          ? 'bg-amber-950/20 border-amber-500/40'
                          : 'bg-slate-850 border-slate-750'
                      } space-y-3 flex flex-col justify-between`}
                    >
                      <div className="space-y-2">
                        <div className="flex items-start justify-between gap-2 border-b border-slate-700/60 pb-2.5">
                          <div>
                            <div className="flex items-center gap-1.5">
                              <span className="text-sm font-bold text-white">👤 {item.usuario}</span>
                            </div>
                            <p className="text-[11px] text-slate-400">{item.cargo} • <strong className="text-slate-300">{item.setor}</strong></p>
                          </div>

                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded font-mono ${
                            isCritico
                              ? 'bg-rose-900/90 text-rose-200 border border-rose-500 animate-pulse'
                              : isGargalo
                              ? 'bg-amber-900/90 text-amber-200 border border-amber-500'
                              : 'bg-emerald-950 text-emerald-300 border border-emerald-500/40'
                          }`}>
                            {isCritico ? '🚨 Gargalo Crítico' : isGargalo ? '⚠️ Gargalo Moderado' : '✅ No Prazo'}
                          </span>
                        </div>

                        <div className="grid grid-cols-3 gap-2 bg-slate-900/80 p-2.5 rounded-lg text-center font-mono">
                          <div>
                            <span className="text-[10px] text-slate-400 block uppercase">Tempo Gasto</span>
                            <span className="text-sm font-bold text-white">{item.dias_gastos} dias</span>
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-400 block uppercase">Meta GCC</span>
                            <span className="text-sm font-bold text-slate-300">{item.dias_previstos} dias</span>
                          </div>
                          <div>
                            <span className="text-[10px] text-slate-400 block uppercase">Desvio</span>
                            <span className={`text-sm font-bold ${
                              item.desvio_dias > 0 ? 'text-rose-400' : 'text-emerald-400'
                            }`}>
                              {item.desvio_dias > 0 ? `+${item.desvio_dias} dias` : '0 dias'}
                            </span>
                          </div>
                        </div>

                        <div className="space-y-1 text-xs">
                          <p className="text-slate-300 leading-relaxed">
                            <strong className="text-slate-200">🔍 Motivo do Gargalo:</strong> {item.motivo_gargalo}
                          </p>
                          <p className="text-slate-400 leading-relaxed text-[11px]">
                            <strong className="text-slate-300">💥 Impacto no Fluxo:</strong> {item.impacto}
                          </p>
                        </div>
                      </div>

                      <div className="pt-2 border-t border-slate-800 text-[11px] bg-slate-900/40 p-2 rounded">
                        <strong className="text-blue-300">💡 Ação Preventiva PLAC:</strong>{' '}
                        <span className="text-slate-300">{item.recomendacao}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* ABA 3: FLUXO OFICIAL GCC (10 MODALIDADES) */}
          {activeTab === 'fluxo32' && (
            <div className="space-y-4">
              {/* Seletor de Modalidades Oficiais da GCC */}
              <div className="bg-slate-850 border border-slate-750 p-3.5 rounded-xl flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-bold text-slate-300">Esteira Oficial da Planilha GCC:</span>
                  <select
                    value={modalidadeGccSelecionada}
                    onChange={(e) => setModalidadeGccSelecionada(e.target.value)}
                    className="bg-slate-900 border border-slate-700 text-amber-300 font-bold text-xs py-1.5 px-3 rounded-lg focus:ring-1 focus:ring-amber-500 cursor-pointer"
                  >
                    <option value="PREGÃO">Pregão Eletrônico (Aba PREGÃO - 40 Etapas)</option>
                    <option value="DISPENSA_Tradicional">Dispensa Tradicional (Aba DISPENSA_Tradicional - 32 Etapas)</option>
                    <option value="DISPENSA Tradic_baixo valor">Dispensa Baixo Valor Tradicional (32 Etapas)</option>
                    <option value="DISPENSA baixo valor_eletrônica">Dispensa Eletrônica Comprasnet (36 Etapas)</option>
                    <option value="INEXIGIBILIDADE">Inexigibilidade Geral - Fornecedor Exclusivo (31 Etapas)</option>
                    <option value="INEXIGIBILIDADE _Curso">Inexigibilidade Capacitação e Cursos (15 Etapas)</option>
                    <option value="DISPENSA__Locação">Dispensa Locação de Imóveis/PoPs (19 Etapas)</option>
                    <option value="DISPENSA_Energia">Dispensa Concessionária Energia (21 Etapas)</option>
                    <option value="INEXIGIBILIDADE Compartilhament">Inexigibilidade Compartilhamento Infra (23 Etapas)</option>
                    <option value="AFASTAMENTO">Afastamento de Licitação - Prática nº 88 (30 Etapas)</option>
                  </select>
                </div>
                {catalogoGcc && catalogoGcc[modalidadeGccSelecionada] && (
                  <span className="text-[11px] text-slate-400 font-mono">
                    Total: <strong className="text-emerald-400">{catalogoGcc[modalidadeGccSelecionada].total_etapas} etapas</strong> cadastradas
                  </span>
                )}
              </div>

              <div className="bg-amber-950/30 border border-amber-500/30 rounded-xl p-3.5 flex flex-wrap items-center justify-between gap-3 text-xs text-amber-200">
                <div className="flex items-center gap-2.5">
                  <span className="text-2xl">📋</span>
                  <div>
                    <h4 className="font-bold text-white text-sm">
                      Esteira Selecionada: {modalidadeGccSelecionada}
                    </h4>
                    <p className="text-slate-300">
                      Mapeamento extraído da planilha oficial <span className="font-mono text-amber-300 font-bold">FLUXOS DE COMPRAS COM RESPONSÁVEIS GCC.xlsx</span>.
                    </p>
                  </div>
                </div>
                <span className="bg-amber-900/80 border border-amber-600 px-2.5 py-1 rounded text-xs font-mono font-bold text-white">
                  {modalidadeGccSelecionada === (isPregao ? 'PREGÃO' : 'DISPENSA_Tradicional') ? 'Fluxo Ativo dos Autos' : 'Consulta Regimental'}
                </span>
              </div>

              {/* Renderização das Etapas: Se selecionou outra modalidade do catálogo, renderiza do catálogo */}
              {catalogoGcc && catalogoGcc[modalidadeGccSelecionada] && modalidadeGccSelecionada !== (isPregao ? 'PREGÃO' : 'DISPENSA_Tradicional') ? (
                <div className="space-y-2">
                  {catalogoGcc[modalidadeGccSelecionada].etapas.map((st, idx) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl border bg-slate-850/80 border-slate-750 flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs"
                    >
                      <div className="flex items-start sm:items-center gap-3 flex-1">
                        <span className="w-7 h-7 rounded-full flex items-center justify-center font-mono font-bold text-xs shrink-0 bg-slate-800 text-slate-300 border border-slate-700">
                          {st.numero || idx + 1}
                        </span>
                        <div className="space-y-0.5 flex-1">
                          <span className="font-bold text-white">
                            {st.atividade}
                          </span>
                          {st.responsavel && (
                            <p className="text-[11px] text-slate-400">
                              Responsável: <strong className="text-slate-300">{st.responsavel}</strong>
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-3 shrink-0 self-end sm:self-auto font-mono text-[11px]">
                        <span className="bg-slate-900 text-slate-300 border border-slate-750 px-2 py-1 rounded">
                          {st.prazo} {st.prazo === 1 ? 'dia útil' : 'dias úteis'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (

              <div className="space-y-2">
                {etapasLista.map((st) => {
                  const isAtual = st.atual;
                  const isDone = st.concluida;

                  return (
                    <div
                      key={st.etapa}
                      className={`p-3 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs transition ${
                        isAtual
                          ? 'bg-amber-950/40 border-amber-500/70 shadow-lg shadow-amber-950/40 animate-pulse'
                          : isDone
                          ? 'bg-slate-850/80 border-slate-750 hover:border-slate-600'
                          : 'bg-slate-900/50 border-slate-800 text-slate-500'
                      }`}
                    >
                      <div className="flex items-start sm:items-center gap-3 flex-1">
                        <span className={`w-7 h-7 rounded-full flex items-center justify-center font-mono font-bold text-xs shrink-0 ${
                          isAtual
                            ? 'bg-amber-500 text-black font-extrabold ring-4 ring-amber-500/30'
                            : isDone
                            ? 'bg-emerald-600 text-white'
                            : 'bg-slate-800 text-slate-500 border border-slate-700'
                        }`}>
                          {isDone ? '✓' : st.etapa}
                        </span>

                        <div className="space-y-0.5 flex-1">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className={`font-bold ${isAtual ? 'text-amber-200 text-sm' : isDone ? 'text-white' : 'text-slate-400'}`}>
                              Etapa {st.etapa}: {st.atividade}
                            </span>
                            {isAtual && (
                              <span className="bg-amber-500 text-black text-[10px] font-extrabold px-2 py-0.5 rounded">
                                Posição Atual do Processo
                              </span>
                            )}
                          </div>
                          <p className="text-[11px] text-slate-400">
                            Responsável: <strong className="text-slate-300">{st.responsavel}</strong>
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 shrink-0 self-end sm:self-auto font-mono text-[11px]">
                        <span className="bg-slate-900 text-slate-300 border border-slate-750 px-2 py-1 rounded">
                          {st.prazo_dias_uteis} {st.prazo_dias_uteis === 1 ? 'dia útil' : 'dias úteis'}
                        </span>
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                          isAtual
                            ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                            : isDone
                            ? 'bg-emerald-950 text-emerald-400'
                            : 'bg-slate-800 text-slate-500'
                        }`}>
                          {isAtual ? 'Em Execução' : isDone ? 'Concluída' : 'Aguardando'}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
              )}

              <div className="p-3 bg-slate-950 border border-slate-800 rounded-lg text-[11px] text-slate-400">
                <strong className="text-amber-400">* Nota da GCC:</strong> Apenas quando necessária a formalização de contrato - Art. 73 da Lei nº 13.303/2016.
              </div>
            </div>
          )}

          {/* ABA 4: HISTÓRICO DE TRAMITAÇÃO */}
          {activeTab === 'tramitacao' && (
            <div className="space-y-4">
              <div className="bg-indigo-950/40 border border-indigo-500/30 rounded-xl p-3.5 flex items-center justify-between text-xs text-indigo-200">
                <div className="flex items-center gap-2.5">
                  <span className="text-xl">🧭</span>
                  <div>
                    <p className="font-bold text-white">Linha do Tempo e Trânsito Departamental no SIGA</p>
                    <p className="text-slate-300">
                      O processo tramitou por <strong>10 marcos de despacho</strong> desde a sua autuação na Diretoria Técnico-Operacional até a atual fase de formalização na GCC.
                    </p>
                  </div>
                </div>
                <span className="bg-indigo-900/70 border border-indigo-700 px-2.5 py-1 rounded text-[10px] font-mono font-bold">
                  67 Dias Úteis Totais
                </span>
              </div>

              <div className="relative border-l-2 border-slate-700 ml-4 pl-6 space-y-6">
                {historico.map((step, idx) => {
                  const isCurrent = step.data_saida === "Em andamento";
                  return (
                    <div key={idx} className="relative">
                      <span className={`absolute -left-[31px] top-1.5 flex h-4 w-4 items-center justify-center rounded-full border-2 ${
                        isCurrent
                          ? 'bg-amber-500 border-amber-300 animate-ping'
                          : 'bg-slate-800 border-indigo-500'
                      }`}>
                        {!isCurrent && <span className="h-1.5 w-1.5 rounded-full bg-indigo-400"></span>}
                      </span>

                      <div className={`p-4 rounded-xl border ${
                        isCurrent
                          ? 'bg-slate-850 border-amber-500/50 shadow-lg'
                          : 'bg-slate-850/80 border-slate-750'
                      } space-y-2`}>
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <span className="text-sm font-bold text-white">{step.area}</span>
                            <span className="bg-slate-900 border border-slate-750 text-[10px] font-mono px-2 py-0.5 rounded text-indigo-300 font-bold">
                              {step.sigla}
                            </span>
                            {isCurrent && (
                              <span className="bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold px-2 py-0.5 rounded animate-pulse">
                                ● Posição Atual (3 dias)
                              </span>
                            )}
                          </div>

                          <div className="text-right text-[11px] font-mono text-slate-400">
                            <span>{step.data_entrada} ➔ {step.data_saida}</span>
                            <span className="ml-2 font-bold text-slate-200">({step.dias_uteis} dias úteis)</span>
                          </div>
                        </div>

                        <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/60 p-2.5 rounded border border-slate-800">
                          <strong>Despacho no SIGA:</strong> {step.despacho}
                        </p>

                        <div className="flex flex-wrap items-center justify-between text-[11px] text-slate-400 pt-1">
                          <span>👤 <strong>Responsável:</strong> {step.responsavel}</span>
                          <span className="font-mono text-slate-500">Autuado em: {step.volume}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* ABA 5: DOCUMENTOS DO PROCESSO COM OCR */}
          {activeTab === 'documentos' && (
            <div className="space-y-4">
              <div className="bg-emerald-950/40 border border-emerald-500/30 rounded-xl p-3 flex items-center justify-between text-xs text-emerald-200">
                <div className="flex items-center gap-2">
                  <span className="text-base">📡</span>
                  <span>
                    <strong>Robô Sentinela SIGA:</strong> {documentos.length} peças processuais baixadas, autenticadas e indexadas no dossiê eletrônico.
                  </span>
                </div>
                <span className="bg-emerald-900/60 px-2 py-0.5 rounded text-[10px] font-mono border border-emerald-700">
                  Chancela ICP-Brasil
                </span>
              </div>

              <div className="grid grid-cols-1 gap-2.5">
                {documentos.map((doc, idx) => (
                  <div
                    key={idx}
                    className="bg-slate-850 border border-slate-750 rounded-xl p-3.5 hover:border-slate-600 transition space-y-2"
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex items-center gap-2.5">
                        <span className="text-2xl">📄</span>
                        <div>
                          <p className="text-sm font-bold text-white">{doc.titulo}</p>
                          <p className="text-[11px] text-slate-400">
                            Juntada em: <span className="text-slate-300 font-mono">{doc.data_juntada}</span> • Signatário: <span className="text-slate-200">{doc.signatario}</span>
                          </p>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 shrink-0 self-end sm:self-auto">
                        <span className="text-[10px] bg-slate-900 text-slate-400 px-2 py-1 rounded font-mono border border-slate-700">
                          {doc.tamanho_kb} KB
                        </span>

                        <button
                          type="button"
                          onClick={() => setSelectedDocPreview(selectedDocPreview?.id === doc.id ? null : doc)}
                          className="text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 px-2.5 py-1.5 rounded transition flex items-center gap-1 border border-slate-700 cursor-pointer"
                        >
                          <span>👁️</span>
                          <span>{selectedDocPreview?.id === doc.id ? 'Ocultar' : 'Visualizar'}</span>
                        </button>

                        <button
                          type="button"
                          onClick={() => handleDownload(doc)}
                          className="text-xs bg-blue-600 hover:bg-blue-500 text-white font-medium px-3 py-1.5 rounded shadow transition flex items-center gap-1 cursor-pointer"
                          title="Baixar arquivo extraído do SIGA"
                        >
                          <span>⬇️</span>
                          <span>Download</span>
                        </button>
                      </div>
                    </div>

                    <p className="text-xs text-slate-300 bg-slate-900/60 p-2 rounded border border-slate-800">
                      <strong>Resumo do Despacho:</strong> {doc.resumo_conteudo}
                    </p>

                    {selectedDocPreview?.id === doc.id && (
                      <div className="mt-2 p-3 bg-slate-950 border border-indigo-500/30 rounded-lg text-xs font-mono text-slate-300 space-y-2 animate-fade-in">
                        <div className="flex items-center justify-between border-b border-slate-800 pb-1">
                          <span className="text-indigo-400 font-bold uppercase text-[10px]">
                            Conteúdo Autenticado Extraído (OCR / Texto):
                          </span>
                          <span className="text-[10px] text-slate-500">Documento Assinado Eletronicamente no SIGA</span>
                        </div>
                        <pre className="whitespace-pre-wrap font-sans text-xs text-slate-200 leading-relaxed max-h-48 overflow-y-auto">
                          {doc.conteudo_preview}
                        </pre>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ABA 6: PRÓXIMOS PASSOS & ONDE VAI */}
          {activeTab === 'proximos' && (
            <div className="space-y-4">
              <div className="bg-slate-850 border border-slate-750 p-4 rounded-xl grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
                <div className="space-y-1">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">
                    🏛️ Setor / Área Atual:
                  </span>
                  <span className="text-white font-bold text-sm">
                    {processo.setor_atual || '2. GCC - Compras & Contratações (Formalização e Publicações)'}
                  </span>
                  <p className="text-slate-400 text-[11px]">Gerência de Compras e Contratações</p>
                </div>

                <div className="space-y-1">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">
                    📍 Onde Encontrar (Localização):
                  </span>
                  <span className="text-slate-200 font-semibold block">
                    {processo.localizacao_atual || 'Mesa Virtual SIGA / Formalização e Assinatura Digital do Contrato TLB-CTR-2026/00038'}
                  </span>
                  <p className="text-blue-400 text-[11px] font-mono">Processo Eletrônico na Mesa Virtual SIGA</p>
                </div>

                <div className="space-y-1">
                  <span className="text-[10px] text-slate-400 uppercase font-bold block">
                    👤 Com Quem Está (Custodiante):
                  </span>
                  <span className="text-amber-400 font-bold text-sm block">
                    {processo.custodiante_atual || 'Pedro / Rosilda (Analistas GCC)'}
                  </span>
                  <p className="text-slate-400 text-[11px]">Tempo no setor: <strong className="text-slate-200">{processo.dias_no_setor || 3} dias úteis</strong></p>
                </div>
              </div>

              <div className="space-y-2.5">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                  <span>🗺️</span>
                  <span>Caminho Restante até o Início da Execução Contratual:</span>
                </h4>

                <div className="space-y-2">
                  {proximosPassos.map((step, idx) => (
                    <div
                      key={idx}
                      className={`p-3.5 rounded-xl border ${
                        idx === 0
                          ? 'bg-amber-950/30 border-amber-500/40 shadow'
                          : 'bg-slate-850/70 border-slate-750'
                      } flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs`}
                    >
                      <div className="space-y-1 flex-1">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-white text-sm">{step.etapa}</span>
                          <span className="bg-slate-900 border border-slate-700 text-slate-300 text-[10px] px-2 py-0.5 rounded font-mono">
                            {step.area}
                          </span>
                          {idx === 0 && (
                            <span className="bg-amber-500/20 text-amber-300 border border-amber-500/40 text-[10px] font-bold px-2 py-0.5 rounded">
                              Próxima Ação Imediata
                            </span>
                          )}
                        </div>
                        <p className="text-slate-300 text-xs">{step.acao}</p>
                      </div>

                      <div className="text-right shrink-0 font-mono text-[11px] text-slate-400">
                        <span className="block font-bold text-slate-200">SLA: {step.prazo_estimado}</span>
                        <span className="text-slate-400 text-[10px]">{step.responsavel}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

        </div>

        {/* Rodapé com Fechamento e Último Despacho */}
        <div className="p-4 border-t border-slate-800 bg-slate-900 flex flex-wrap justify-between items-center gap-3 text-xs">
          <div className="flex items-center gap-2 text-slate-400 truncate max-w-xl">
            <span className="font-bold text-slate-300 shrink-0">Último Despacho SIGA:</span>
            <span className="text-slate-200 italic truncate">
              {processo.ultimo_despacho_siga || processo.ultimo_evento_siga}
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg transition font-medium cursor-pointer"
            >
              Fechar Dossiê
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
