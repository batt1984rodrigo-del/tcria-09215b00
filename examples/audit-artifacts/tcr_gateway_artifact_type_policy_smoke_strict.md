# Nova Auditoria - Conjunto de Arquivos que Levantam Acusacao (TCR-IA style)

Base: gates do projeto (prescriptive/compliance) adaptados para arquivos estaticos.

- Modo de complianceGate: `strict-explicit-decision-record`
- Gerado em: `2026-02-23T18:49:14`
- Arquivos varridos: `2`
- Arquivos no conjunto acusatorio auditado: `1`
- Contagens por classificacao: `{'SUPPORTING_EVIDENCE_RELEVANT': 1, 'ACCUSATORY_CANDIDATE': 1}`

## Resultado resumido (conjunto acusatorio)

### 📘 Dossiê Completo — Projeto Guarda e Convivência d d775939f06af419c81de91cbb28dbb82.md
- Resultado: `PARTIAL_PASS (static document audit; maturity/ledger not evaluated)`
- Tipo: `.md` | texto extraido: `20243` chars | qualidade: `high`
- Classificacao: `ACCUSATORY_CANDIDATE`
- Motivos da classificacao: Accusatory score=16 (filename=4, content=12)., Mentions target entity/person., Contains evidence/documentation markers.
- `prescriptiveGate`: `PASS` - No project-defined prescriptive patterns detected.
- `complianceGate`: `PASS` - Analytical artifact: responsibility indicator found (strict explicit check).
  Evidence: Responsável:** Rodrigo Baptista da Silva
- `traceabilityCheck`: `PASS` - Document contains multiple traceability/evidence signals.
  Evidence: dates=6, evidence_markers=9
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
- Sinais: dates=6, currency=0, pix=0, emails=0

## Arquivos nao auditados como acusatorios (resumo)

- `Pedido_de_informacao_ao_conselho_.pdf` -> `SUPPORTING_EVIDENCE_RELEVANT` (Relevant contextual/supporting content detected.)

## Observacoes

- Esta auditoria nao verifica veracidade juridica/fatica das alegacoes; avalia forma/documentacao textual.
- `maturityGate` e controles de ledger/hash/HMAC exigem runtime/sistema e nao sao inferiveis de arquivos estaticos.
- `Senhas.csv` foi tratado como sensivel e nao teve conteudo exibido/lido para esta auditoria.
