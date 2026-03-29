export const pipelineSteps = [
  'Input ingestion',
  'Classification',
  'Traceability',
  'Governance checks',
  'Institutional output'
];

export const gateDescriptions = [
  {
    title: 'Prescriptive Gate',
    description: 'Transforms legal and evidentiary analysis into enforceable action paths.'
  },
  {
    title: 'Compliance Gate',
    description: 'Blocks artifacts that violate procedural, legal, or governance constraints.'
  },
  {
    title: 'Traceability Check',
    description: 'Links every conclusion to auditable evidence chains and provenance anchors.'
  },
  {
    title: 'Maturity Gate',
    description: 'Grades institutional readiness before release into decision-making channels.'
  },
  {
    title: 'Ledger Runtime Check',
    description: 'Verifies ledger integrity and execution consistency for governance runtime.'
  }
];

export const sampleStats = [
  { label: 'Files Scanned', value: '673' },
  { label: 'Accusatory Candidates', value: '91' },
  { label: 'Blocked by Compliance Gate', value: '89' },
  { label: 'Financial Signals in One PDF', value: '138' }
];

export const demoFlow = [
  {
    id: 'input',
    title: 'Input',
    detail:
      'Raw PDF, DOCX, HTML and XLSX artifacts are normalized and chunked with metadata before analysis.'
  },
  {
    id: 'classification',
    title: 'Classification',
    detail: 'Each artifact receives legal intent, risk context and institutional profile mapping.'
  },
  {
    id: 'traceability',
    title: 'Traceability',
    detail: 'Evidence references and supporting snippets are linked to every argument and claim.'
  },
  {
    id: 'governance',
    title: 'Governance',
    detail: 'TCR Gateway gates execute policy checks, blocking non-compliant narratives and outputs.'
  },
  {
    id: 'output',
    title: 'Output',
    detail: 'Decision-ready bundles are generated as Markdown, JSON and PDF institutional artifacts.'
  }
];
