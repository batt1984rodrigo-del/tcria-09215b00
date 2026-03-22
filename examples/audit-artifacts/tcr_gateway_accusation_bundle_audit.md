# Nova Auditoria - Conjunto de Arquivos que Levantam Acusacao (TCR-IA style)

Base: gates do projeto (prescriptive/compliance) adaptados para arquivos estaticos.

- Modo de complianceGate: `default-heuristic`
- Gerado em: `2026-02-23T17:13:58`
- Arquivos varridos: `42`
- Arquivos no conjunto acusatorio auditado: `18`
- Contagens por classificacao: `{'ACCUSATORY_CANDIDATE': 18, 'SUPPORTING_EVIDENCE': 18, 'SUPPORTING_EVIDENCE_RELEVANT': 4, 'UNREADABLE_OR_EMPTY': 1, 'SENSITIVE_EXCLUDED': 1}`

## Resultado resumido (conjunto acusatorio)

### # 📘 Dossiê Ampliado — Caso Vinícius Carvalho.docx
- Resultado: `PARTIAL_PASS (static document audit; maturity/ledger not evaluated)`
- Tipo: `.docx` | texto extraido: `10539` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=16 (filename=4, content=12)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `PASS` - Heuristic check found actor, purpose, and approval indicators in file text.
  Evidence: actor=Named individual(s) found in document body (heuristic, not explicit responsibility field). | purpose=Este dossiê visa documentar e esclarecer, de forma técnica e narrativa, o conjunto de fraudes bancárias, violações digitais e danos pessoais sofridos por Rodrigo Baptista da Silva, auditor fiscal da Receita Estadual d | approval=aprovado
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: dates=16, currency=6, evidence_markers=12
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=16, currency=6, pix=2, emails=0

### Cópia de Dossie_Expandido_Final_Robson_2025.docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `4306` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=13 (filename=2, content=11)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose, approved).
  Evidence: actor=Named individual(s) found in document body (heuristic, not explicit responsibility field).
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: currency=2, evidence_markers=5
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=0, currency=2, pix=0, emails=0

### Documento (1).docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `43292` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=11 (filename=0, content=11)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose, approved).
  Evidence: actor=Responsável: Rodrigo Baptista da Silva Banco: Bradesco Período analisado: novembro de 2022 a março de 2024 Agência: 1699 | Conta-corrente: 775823-5
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: dates=79, currency=58, evidence_markers=106
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=79, currency=58, pix=26, emails=0

### Documento (4).docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `2729` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=5 (filename=0, content=5)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose).
  Evidence: actor=Named individual(s) found in document body (heuristic, not explicit responsibility field). | approval=Assinatura
- `traceabilityCheck`: `WARN` - Document has limited traceability/evidence signals.
  Evidence: evidence_markers=7
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=0, currency=0, pix=2, emails=0

### Dossie_Consolidado_Correcao_Tecnica_Logs_Fraudes.docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `4877` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=15 (filename=4, content=11)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose, approved).
  Evidence: actor=Autor: Rodrigo Baptista da Silva
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: dates=1, currency=2, evidence_markers=21
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=1, currency=2, pix=9, emails=0

### Dossie_Final_Unificado_Com_Grafico.docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `11363` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=13 (filename=2, content=11)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose, approved).
  Evidence: actor=Autor: Rodrigo Baptista da Silva
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: dates=2, currency=5, evidence_markers=46
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=2, currency=5, pix=10, emails=0

### Dossie_Final_Unificado_Com_Imagens.docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `11604` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=13 (filename=2, content=11)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose, approved).
  Evidence: actor=Autor: Rodrigo Baptista da Silva
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: dates=2, currency=5, evidence_markers=48
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=2, currency=5, pix=10, emails=0

### Dossie_Rastreavel_Etico_Golpe_Bradesco.docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `2971` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=15 (filename=5, content=10)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose, approved).
  Evidence: actor=Autor: Rodrigo Baptista da Silva
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: dates=1, evidence_markers=5
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=1, currency=0, pix=0, emails=0

### dossiê Bradesco revisado adv final.docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `8102` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=13 (filename=3, content=10)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose, approved).
  Evidence: actor=Named individual(s) found in document body (heuristic, not explicit responsibility field).
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: dates=8, currency=61, evidence_markers=16
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=8, currency=61, pix=0, emails=0

### Dossiê Fraude Bradesco — Caso Vinícius.docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `3880` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=12 (filename=5, content=7)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing responsibleHuman, declaredPurpose).
  Evidence: approval=aprovado
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: dates=1, currency=7, evidence_markers=14
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=1, currency=7, pix=4, emails=0

### E-mails Bradesco .txt
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.txt` | texto extraido: `337621` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=6 (filename=1, content=5)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose, approved).
  Evidence: actor=Named individual(s) found in document body (heuristic, not explicit responsibility field).
- `traceabilityCheck`: `WARN` - Document has limited traceability/evidence signals.
  Evidence: evidence_markers=162
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=0, currency=0, pix=10, emails=52

### encaminhamento ao MP.docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `4406` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=12 (filename=2, content=10)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose).
  Evidence: actor=Named individual(s) found in document body (heuristic, not explicit responsibility field). | approval=Assinatura
- `traceabilityCheck`: `WARN` - Document has limited traceability/evidence signals.
  Evidence: evidence_markers=7
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=0, currency=0, pix=1, emails=0

### Faturas relatório .docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `43292` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=11 (filename=0, content=11)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose, approved).
  Evidence: actor=Responsável: Rodrigo Baptista da Silva Banco: Bradesco Período analisado: novembro de 2022 a março de 2024 Agência: 1699 | Conta-corrente: 775823-5
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: dates=79, currency=58, evidence_markers=106
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=79, currency=58, pix=26, emails=0

### Memoria_Conceitual_Projetos_Rodrigo.docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `2346` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=9 (filename=0, content=9)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose, approved).
  Evidence: actor=Named individual(s) found in document body (heuristic, not explicit responsibility field).
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: dates=1, evidence_markers=3
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=1, currency=0, pix=0, emails=0

### Partes_Reescritas_Projeto_Golpe_Bradesco.docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `1447` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=11 (filename=3, content=8)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose, approved).
  Evidence: actor=Named individual(s) found in document body (heuristic, not explicit responsibility field).
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: dates=1, evidence_markers=1
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=1, currency=0, pix=0, emails=0

### Reclamacao_Etica_OAB_Advogada_Bradesco.docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `2645` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=19 (filename=7, content=12)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose, approved).
  Evidence: actor=Named individual(s) found in document body (heuristic, not explicit responsibility field).
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: currency=1, evidence_markers=13
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=0, currency=1, pix=2, emails=0

### Sumario_Analitico_Golpe_Bradesco.docx
- Resultado: `BLOCKED (complianceGate)`
- Tipo: `.docx` | texto extraido: `1892` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=14 (filename=3, content=11)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord incomplete (missing declaredPurpose, approved).
  Evidence: actor=Autor: Rodrigo Baptista da Silva
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: dates=1, currency=1, evidence_markers=14
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=1, currency=1, pix=1, emails=0

### 📘 Dossiê Ampliado — Caso Vinícius Carvalho.docx
- Resultado: `PARTIAL_PASS (static document audit; maturity/ledger not evaluated)`
- Tipo: `.docx` | texto extraido: `10539` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=16 (filename=4, content=12)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `PASS` - Heuristic check found actor, purpose, and approval indicators in file text.
  Evidence: actor=Named individual(s) found in document body (heuristic, not explicit responsibility field). | purpose=Este dossiê visa documentar e esclarecer, de forma técnica e narrativa, o conjunto de fraudes bancárias, violações digitais e danos pessoais sofridos por Rodrigo Baptista da Silva, auditor fiscal da Receita Estadual d | approval=aprovado
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: dates=16, currency=6, evidence_markers=12
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=16, currency=6, pix=2, emails=0

## Arquivos nao auditados como acusatorios (resumo)

- `2023-11-18T12[]48[]14-7.csv` -> `SUPPORTING_EVIDENCE` (CSV dataset treated primarily as supporting evidence/data source.)
- `8690501546.txt` -> `SUPPORTING_EVIDENCE_RELEVANT` (Numeric text export/log with relevant terms.)
- `8690501555.txt` -> `SUPPORTING_EVIDENCE_RELEVANT` (Numeric text export/log with relevant terms.)
- `8690735559.txt` -> `SUPPORTING_EVIDENCE` (Numeric text export/log file.)
- `8690735581.txt` -> `SUPPORTING_EVIDENCE` (Numeric text export/log file.)
- `8690739017.txt` -> `SUPPORTING_EVIDENCE` (Numeric text export/log file.)
- `8690739188.txt` -> `SUPPORTING_EVIDENCE` (Numeric text export/log file.)
- `8690742446.txt` -> `SUPPORTING_EVIDENCE` (Numeric text export/log file.)
- `8690751458.txt` -> `SUPPORTING_EVIDENCE` (Numeric text export/log file.)
- `8690754060.txt` -> `SUPPORTING_EVIDENCE_RELEVANT` (Numeric text export/log with relevant terms.)
- `8690756540.txt` -> `SUPPORTING_EVIDENCE` (Numeric text export/log file.)
- `8690757903.txt` -> `SUPPORTING_EVIDENCE` (Numeric text export/log file.)
- `8690760366.txt` -> `SUPPORTING_EVIDENCE` (Numeric text export/log file.)
- `8690760912.txt` -> `SUPPORTING_EVIDENCE` (Numeric text export/log file.)
- `8690764434.txt` -> `SUPPORTING_EVIDENCE` (Numeric text export/log file.)
- `8690764830.txt` -> `SUPPORTING_EVIDENCE` (Numeric text export/log file.)
- `8690767288.txt` -> `SUPPORTING_EVIDENCE` (Numeric text export/log file.)
- `artist_nodes.csv` -> `SUPPORTING_EVIDENCE_RELEVANT` (CSV dataset treated primarily as supporting evidence/data source.)
- `Faturas_Extra_das_para_Diagn_stico.csv` -> `SUPPORTING_EVIDENCE` (CSV dataset treated primarily as supporting evidence/data source.)
- `Informações Positivas bradesco.webarchive` -> `UNREADABLE_OR_EMPTY` (File is empty or yielded no extractable text.)
- `Senhas.csv` -> `SENSITIVE_EXCLUDED` (Sensitive credentials file; content intentionally not read.)
- `Todas_as_Transa__es_Bradesco__Extra__o_Completa_ 2.csv` -> `SUPPORTING_EVIDENCE` (CSV dataset treated primarily as supporting evidence/data source.)
- `Todas_as_Transa__es_Bradesco__Extra__o_Completa_.csv` -> `SUPPORTING_EVIDENCE` (CSV dataset treated primarily as supporting evidence/data source.)
- `Transa__es_Faturas_Bradesco.csv` -> `SUPPORTING_EVIDENCE` (CSV dataset treated primarily as supporting evidence/data source.)

## Observacoes

- Esta auditoria nao verifica veracidade juridica/fatica das alegacoes; avalia forma/documentacao textual.
- `maturityGate` e controles de ledger/hash/HMAC exigem runtime/sistema e nao sao inferiveis de arquivos estaticos.
- `Senhas.csv` foi tratado como sensivel e nao teve conteudo exibido/lido para esta auditoria.
