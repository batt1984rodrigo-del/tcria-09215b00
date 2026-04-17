export const pipelineSteps = [
  'Entrada',
  'Classificação',
  'Rastreabilidade',
  'Governança',
  'Saída institucional'
];

export const gateDescriptions = [
  {
    title: 'Prescriptive Gate',
    description: 'Bloqueia linguagem prescritiva ou condenatória sem fundamentação adequada.'
  },
  {
    title: 'Compliance Gate',
    description: 'Exige responsável declarado, propósito explícito e aprovação registrada antes da liberação.'
  },
  {
    title: 'Traceability Check',
    description: 'Conecta cada conclusão a cadeias de evidência auditáveis e verificáveis.'
  },
  {
    title: 'Maturity Gate',
    description: 'Avalia o nível de prontidão institucional antes da utilização em decisões.'
  },
  {
    title: 'Ledger Runtime Check',
    description: 'Valida integridade de execução e consistência da cadeia de registros.'
  }
];

export const sampleStats = [
  { label: 'Arquivos varridos', value: '673' },
  { label: 'Candidatos acusatórios', value: '91' },
  { label: 'Bloqueados pelo Compliance Gate', value: '89' },
  { label: 'Sinais financeiros em um PDF', value: '138' }
];

export const demoFlow = [
  {
    id: 'entrada',
    title: 'Entrada',
    detail:
      'Arquivos PDF, DOCX, HTML e XLSX são normalizados e estruturados com metadados antes da análise.'
  },
  {
    id: 'classificacao',
    title: 'Classificação',
    detail:
      'Cada documento recebe interpretação de contexto, intenção e enquadramento institucional.'
  },
  {
    id: 'rastreabilidade',
    title: 'Rastreabilidade',
    detail:
      'Trechos e evidências são conectados diretamente a cada afirmação e conclusão.'
  },
  {
    id: 'governanca',
    title: 'Governança',
    detail:
      'Os gates do TCR executam validações e bloqueiam conteúdos não conformes.'
  },
  {
    id: 'saida',
    title: 'Saída',
    detail:
      'São gerados artefatos institucionais em Markdown, JSON e PDF prontos para uso.'
  }
];
