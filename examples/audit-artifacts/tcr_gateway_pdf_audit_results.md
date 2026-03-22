# TCR-IA-style PDF Audit Results

Audit basis: project gates (prescriptive language, human responsibility) adapted to static PDF content.

Important: this is not legal verification of factual claims.

## Arquivos.pdf

- Path: `/Users/rodrigobaptistadasilva/Downloads/Arquivos.pdf`
- Pages: 9
- Extractable text chars: 23233
- Text extraction quality: `high`
- Content type guess: `financial_statement_or_invoice_records`
- Overall outcome: `BLOCKED (complianceGate)`
- Summary: Documento parece ser extrato/fatura com alta densidade transacional. Sem linguagem prescritiva bloqueante pelos padrões do projeto. Não atende integralmente ao gate de responsabilidade humana em formato verificável.

### Gate results
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected in extracted text.
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not present in PDF content and no repo runtime was provided.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose, approved).
  Evidence: actor=Named individual(s) found in document body (heuristic, not explicit responsibility field).
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static PDFs do not provide runtime ledger append events (LLM_RETURNED / DECISION_APPROVED / POSTCHECK_BLOCKED).

### Key signals
- Currency values found: 15
- Date values found: 3
- PIX mentions: 0
- Timeline markers: 1
- Contains `Objetivo:` label: False
- Contains `Resumo` label: True
- Risk keyword hits: {}

## Dossie_Fraude_Bradesco.pdf

- Path: `/Users/rodrigobaptistadasilva/Downloads/Dossie_Fraude_Bradesco.pdf`
- Pages: 1
- Extractable text chars: 1706
- Text extraction quality: `high`
- Content type guess: `case_dossier_or_report`
- Overall outcome: `BLOCKED (complianceGate)`
- Summary: Documento parece dossiê narrativo/estruturado de caso. Sem linguagem prescritiva bloqueante pelos padrões do projeto. Não atende integralmente ao gate de responsabilidade humana em formato verificável.

### Gate results
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected in extracted text.
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not present in PDF content and no repo runtime was provided.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing approved).
  Evidence: actor=Named individual(s) found in document body (heuristic, not explicit responsibility field). | purpose=Objetivo: subsidiar ação civil de ressarcimento contra o Banco Bradesco S.A.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static PDFs do not provide runtime ledger append events (LLM_RETURNED / DECISION_APPROVED / POSTCHECK_BLOCKED).

### Key signals
- Currency values found: 11
- Date values found: 8
- PIX mentions: 4
- Timeline markers: 7
- Contains `Objetivo:` label: True
- Contains `Resumo` label: True
- Risk keyword hits: {'fraude': 1, 'prejuízo': 3, 'ressarcimento': 1, 'não autorizado': 2, 'dano': 1}

## Cópia de 📘 Dossiê Ampliado — Caso Vinícius Carvalho.pdf

- Path: `/Users/rodrigobaptistadasilva/Downloads/Cópia de 📘 Dossiê Ampliado — Caso Vinícius Carvalho.pdf`
- Pages: 8
- Extractable text chars: 10844
- Text extraction quality: `high`
- Content type guess: `case_dossier_or_report`
- Overall outcome: `PARTIAL_PASS (static document only; maturity/ledger runtime not evaluated)`
- Summary: Documento parece dossiê narrativo/estruturado de caso. Sem linguagem prescritiva bloqueante pelos padrões do projeto. Tem sinais heurísticos de DecisionRecord (ator/finalidade/aprovação).

### Gate results
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected in extracted text.
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not present in PDF content and no repo runtime was provided.
- `complianceGate`: `PASS` - Heuristic check found actor, purpose, and approval indicators in document text.
  Evidence: actor=Named individual(s) found in document body (heuristic, not explicit responsibility field). | purpose=Este dossiê visa documentar e esclarecer, de forma técnica e narrativa, o | approval=aprovado
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static PDFs do not provide runtime ledger append events (LLM_RETURNED / DECISION_APPROVED / POSTCHECK_BLOCKED).

### Key signals
- Currency values found: 6
- Date values found: 16
- PIX mentions: 2
- Timeline markers: 0
- Contains `Objetivo:` label: False
- Contains `Resumo` label: False
- Risk keyword hits: {'fraude': 11, 'risco': 1, 'bloqueio': 1, 'prejuízo': 2, 'invasão': 3, 'não autorizado': 1, 'omissão': 1, 'dano': 4, 'auditoria': 2}

