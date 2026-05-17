# Analise complementar dos bloqueados

Camada adicional: o status oficial do gate permanece inalterado.

- Gerado em: `2026-05-17T00:48:38`
- Fonte: `<repo>/examples/institutional-demo-case/output/institutional_demo_strict.json`
- Bloqueados analisados: `1`

## relatorio_ungoverned_claim.txt
- Resultado oficial: `BLOCKED (complianceGate)`
- Motivo do bloqueio: DecisionRecord header not found in strict mode.
- Identity: sha256=f0fbed8211586df2..., engine=tcria@0.1.0, policy=unknown
- Tipo de documento: `analytical_narrative`
- Conteudo: Accusatory terms: fraude=1. Theme entities: bradesco=1. Traceability markers: dates=1, currency=1, pix=1.
- Relacao com o tema: `True`
- Problema de organizacao/governanca: `True`
- Razoes de organizacao/governanca: `['falta_metadado_governanca', 'sem_objetivo_explicito', 'sem_autor_responsavel_explicito']`
- Impacto potencial no caso: `mixed`
- Acao recomendada: Add explicit DecisionRecord metadata: responsibleHuman, declaredPurpose, approved.

