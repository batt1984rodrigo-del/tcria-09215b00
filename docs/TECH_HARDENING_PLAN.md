# Tech Hardening Plan (Issue #23)

Objetivo: execução do backlog técnico sem alterar governança/arquitetura, criando base de engenharia para produção.

## Escopo
- [ ] #35 Refatorar scripts em módulos/serviços reutilizáveis
- [ ] #36 Definir contratos tipados (Pydantic/BaseModel)
- [ ] #37 Logging estruturado (JSON + trace IDs)
- [ ] #38 Suite de testes (pytest, parametrização, snapshots)
- [ ] #39 Engine única de relatórios/PDFs (templates)
- [ ] #40 CI/CD (linters, type-check, coverage, SBOM, security scan)
- [ ] #41 Container hardening (multi-stage, non-root, healthcheck, deps pinned)
- [ ] #42 Config centralizada (BaseSettings/profiles, validação de secrets)
- [ ] #43 Observabilidade (métricas + traces + alerting)
- [ ] #44 APIs padronizadas (/v1, OpenAPI, paginação, idempotency)

## Entrega
- PR inicial cria esta âncora de planning e configura a branch para evoluir incrementalmente.
