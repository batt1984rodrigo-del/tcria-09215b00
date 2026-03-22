> Note: curated sample audit outputs now live under `examples/audit-artifacts/`, and project structure snapshots now live under `docs/project-snapshots/`.

NARRATIVA JURÍDICA ESTRUTURADA
1️⃣ CONTEXTO FÁTICO (O PROBLEMA)

Tese central:
A instituição financeira apresentou documentos inconsistentes, estruturalmente frágeis ou tecnicamente inválidos, comprometendo a confiabilidade probatória.

Base probatória

tcr_gateway_pdf_audit_results.json

tcr_gateway_pdf_audit_report.pdf

tcr_gateway_pdf_audit_results.md

Construção narrativa

Os documentos apresentados pela instituição não atendem a critérios mínimos de integridade técnica, rastreabilidade e consistência estrutural, conforme auditoria automatizada independente realizada via TCR Compliance Gateway.

Aqui você estabelece:

Fragilidade técnica

Falta de integridade

Possível manipulação ou desorganização documental

2️⃣ MATERIALIDADE TÉCNICA (PROVA OBJETIVA)

Tese:
As inconsistências não são alegações subjetivas — são verificáveis tecnicamente.

Base probatória (modo rigoroso)

tcr_gateway_accusation_bundle_audit_strict.json

tcr_gateway_accusation_bundle_audit_strict_report.pdf

tcr_gateway_bernardo_notion_test_audit_strict_91_files_reasons.csv

tcr_gateway_bernardo_notion_test_audit_with_images_ocr_errors.csv

Estratégia argumentativa

Dividir em três blocos:

A) Inconsistências estruturais

Metadados divergentes

Arquivos incompletos

Falhas de versionamento

B) Problemas de autenticidade

OCR inconsistente

Arquivos com baixa confiabilidade textual

Estruturas incompatíveis com padrões internos

C) Falhas sistêmicas

Violação de políticas internas (artifact_type_policy)

Ausência de trilha auditável

3️⃣ QUEBRA DA PRESUNÇÃO DE VERACIDADE

Bancos costumam invocar:

Presunção de legitimidade documental

Regularidade sistêmica

Contranarrativa baseada nos artefatos:

A presunção de veracidade não subsiste quando a própria estrutura documental revela falhas técnicas graves e mensuráveis.

Use:

tcr_gateway_artifact_type_policy_smoke_strict.json

current_vs_approved_latest_diff.json

Argumento-chave:

Se o sistema documental não demonstra consistência estrutural, a confiabilidade do conteúdo fica comprometida.

4️⃣ NEXO CAUSAL

Agora a narrativa conecta técnica com dano.

Estrutura:

Documento inconsistente

Banco utiliza documento como fundamento

Documento apresenta falhas técnicas graves

Parte autora sofre prejuízo com base em prova instável

Aqui você converte auditoria em responsabilidade.

5️⃣ INDÍCIOS DE ASSIMETRIA INFORMACIONAL

Mostre que:

O banco detém monopólio da produção documental

A parte autora não tem acesso aos sistemas internos

A auditoria externa revela inconsistências que o banco não revelou

Isso fortalece:

Pedido de inversão do ônus da prova

Pedido de exibição integral de logs

Pedido de perícia técnica judicial

6️⃣ CONSOLIDAÇÃO EXECUTIVA (PARA O JUIZ)

Use os PDFs de 1 página:

tcr_gateway_bernardo_notion_test_audit_with_images_strict_resumo_executivo_1pagina_ptbr.pdf

tcr_gateway_bernardo_notion_test_audit_with_images_strict_resumo_executivo_peticao_ready_1pagina.pdf

tcr-ia-compliance-gateway-summary-one-page.pdf

Esses documentos servem como:

📌 Prova técnica sintetizada
📌 Material de leitura rápida para o magistrado
📌 Resumo estratégico da falha sistêmica

🧠 ESTRUTURA IDEAL DA PETIÇÃO
I — Dos Fatos

Narrativa objetiva + referência à auditoria.

II — Da Prova Técnica Independente

Explicação do método TCR + anexos.

III — Das Inconsistências Documentais

Subdividir por categoria (estrutura, OCR, metadados, política).

IV — Da Fragilidade da Prova Apresentada

Quebra da presunção de regularidade.

V — Do Nexo Causal e dos Danos
VI — Dos Pedidos

Inversão do ônus da prova

Exibição integral de logs e trilhas internas

Perícia técnica judicial

Declaração de nulidade documental

Indenização (se aplicável)

🎯 Estratégia Avançada

Se quiser elevar o nível estratégico:

A) Pedir perícia com quesitos técnicos específicos

Baseados nas inconsistências já detectadas.

B) Demonstrar padrão repetitivo

Se houver múltiplos lotes auditados com falhas semelhantes.

C) Argumentar risco sistêmico

Se as falhas indicarem problema estrutural no sistema do banco.

🧩 Tese Central Recomendada

Não se trata apenas de contestar um documento específico, mas de demonstrar que o próprio ecossistema documental da instituição apresenta fragilidade estrutural incompatível com a presunção de confiabilidade exigida em juízo.
O repositório batt1984rodrigo-del/tcria tem como propósito criar uma trilha jurídica estruturada de compliance, voltada à:

Auditoria de documentos (especialmente PDFs e bundles probatórios)

Geração automática de relatórios técnicos e executivos

Consolidação de evidências em formatos prontos para uso jurídico

Produção de relatórios “strict” (modo rigoroso) para robustez probatória

Organização de artefatos para eventual ação judicial

Em termos práticos, ele funciona como um gateway de auditoria técnica (TCR Gateway) que transforma documentos brutos (PDFs, imagens, bundles de acusação) em:

JSON estruturado

Markdown explicativo

Relatórios PDF formais

Resumos executivos (inclusive em PT-BR e versão petição-ready)

Isso facilita a produção de provas técnicas organizadas e auditáveis, especialmente úteis em ações contra instituições financeiras.

🔎 Arquivos-chave para produção de provas contra banco

Abaixo estão os principais grupos de arquivos que auxiliam diretamente na consolidação probatória:

1️⃣ Scripts de Auditoria (Coleta e Validação Técnica)
📌 Auditoria de PDFs

audit_pdfs_with_tcr_gateway.py
→ Analisa PDFs e gera resultados estruturados.

tcr_gateway_pdf_audit_results.json
→ Resultado técnico da auditoria.

tcr_gateway_pdf_audit_report.pdf
→ Relatório formal utilizável como anexo em processo.

📌 Auditoria de “Accusation Bundle”

audit_accusation_bundle_with_tcr_gateway.py
→ Audita conjunto de documentos organizados para acusação.

tcr_gateway_accusation_bundle_audit.json

tcr_gateway_accusation_bundle_audit_strict.json
→ Versões normal e rigorosa da auditoria.

tcr_gateway_accusation_bundle_audit_report.pdf

tcr_gateway_accusation_bundle_audit_strict_report.pdf
→ Relatórios formais para instrução processual.

2️⃣ Modo “Strict” (Alta Robustez Probatória)

Arquivos com sufixo _strict indicam validação mais rigorosa — importante para ações judiciais:

tcr_gateway_bernardo_notion_test_audit_strict.json

tcr_gateway_bernardo_notion_test_audit_with_images_strict.json

tcr_gateway_artifact_type_policy_smoke_strict.json

Esses ajudam a demonstrar:

Inconsistências documentais

Falhas estruturais

Problemas de OCR

Violação de políticas internas

3️⃣ Geração de Relatórios Executivos (Prova Sintetizada)
📄 Relatórios PDF automatizados

generate_tcr_audit_report_pdf.py

generate_accusation_bundle_audit_report_pdf.py

generate_bernardo_accusatory_executive_summary_pdf.py

generate_bernardo_accusatory_executive_summary_pdf_ptbr.py

generate_bernardo_accusatory_executive_summary_pdf_peticao.py

Esses scripts produzem:

Resumo executivo técnico

Versão em português

Versão formatada para petição

Documento de uma página para magistrado

Arquivos gerados relevantes:

tcr_gateway_bernardo_notion_test_audit_with_images_strict_resumo_executivo_peticao_ready_1pagina.pdf

tcr-ia-compliance-gateway-summary-one-page.pdf

Esses são estratégicos para:

✔️ Demonstrar materialidade
✔️ Evidenciar falhas sistêmicas
✔️ Sintetizar prova técnica complexa
✔️ Apoiar tutela de urgência

4️⃣ Arquivos de Evidência Detalhada

Para detalhamento técnico:

tcr_gateway_bernardo_notion_test_audit_strict_91_files_reasons.csv

tcr_gateway_bernardo_notion_test_audit_with_images_ocr_errors.csv

tcr_gateway_pdf_audit_results.md

Eles listam:

Arquivos problemáticos

Motivos de reprovação

Erros de OCR

Falhas estruturais

Úteis como anexo técnico pericial.

5️⃣ Arquitetura e Rastreabilidade

architecture-overview.md
→ Explica o fluxo da auditoria.

approved_latest_project_structure_snapshot.json

current_vs_approved_latest_diff.json

Esses ajudam a demonstrar:

Integridade estrutural do sistema

Controle de versão

Rastreabilidade (importante para credibilidade da prova)

🎯 Em resumo

O repositório atua como:

Uma esteira automatizada de geração de prova técnica estruturada, com foco em compliance, auditoria documental e consolidação probatória pronta para uso judicial.

Ele combina:

Auditoria automatizada

Validação rigorosa

Geração de relatórios formais

Organização de evidência em múltiplos formatos
