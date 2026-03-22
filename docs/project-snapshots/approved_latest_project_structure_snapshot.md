# Approved Project Structure Snapshot (Latest)

- Created at: `2026-02-23T19:28:51`
- Project root: `/Users/rodrigobaptistadasilva/Documents/New project`
- Tree depth captured: `4`

## Approved State Summary

- Source JSON: `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict.json`
- Total scanned: `1011`
- Accusatory set: `92`

### Accusatory Outcomes
- `BLOCKED (complianceGate)`: `36`
- `BLOCKED (prescriptiveGate)`: `4`
- `PARTIAL_PASS (static document audit; maturity/ledger not evaluated)`: `32`
- `PARTIAL_PASS (traceability warning; static audit)`: `20`

### Artifact Types (Accusatory Set)
- `ANALYTICAL_ARTIFACT`: `54`
- `DECISION_ARTIFACT`: `38`

### Gate Status Counts (Accusatory Set)
- `prescriptiveGate`: BLOCKED=4, PASS=88
- `complianceGate`: BLOCKED=38, PASS=4, WARN=50
- `traceabilityCheck`: PASS=50, WARN=42

## Key Scripts

- `scripts/audit_accusation_bundle_with_tcr_gateway.py` | exists=`True` | size=`37641`
- `scripts/generate_accusation_bundle_audit_report_pdf.py` | exists=`True` | size=`14188`
- `scripts/generate_bernardo_accusatory_executive_summary_pdf.py` | exists=`True` | size=`8525`
- `scripts/generate_bernardo_accusatory_executive_summary_pdf_ptbr.py` | exists=`True` | size=`9069`
- `scripts/generate_bernardo_accusatory_executive_summary_pdf_peticao.py` | exists=`True` | size=`7778`
- `scripts/generate_tcr_signals_gateway_file.py` | exists=`True` | size=`20168`

## Key Artifacts

- `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict.json` | exists=`True` | size=`1856915`
- `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict.md` | exists=`True` | size=`202103`
- `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict_report.pdf` | exists=`True` | size=`253914`
- `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict_92_files_reasons.md` | exists=`True` | size=`45589`
- `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict_92_files_reasons.csv` | exists=`True` | size=`58241`
- `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_ocr_errors.md` | exists=`True` | size=`322`
- `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_ocr_errors.csv` | exists=`True` | size=`119`
- `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict_executive_summary_1page.pdf` | exists=`True` | size=`3281`
- `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict_resumo_executivo_1pagina_ptbr.pdf` | exists=`True` | size=`3429`
- `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict_resumo_executivo_peticao_ready_1pagina.pdf` | exists=`True` | size=`3514`

## Project Tree (Depth <= 4)

- [F] `.DS_Store` (14340 B)
- [D] `.codex`
  - [D] `.codex/environments`
    - [F] `.codex/environments/environment.toml` (100 B)
- [D] `.git`
  - [F] `.git/HEAD` (21 B)
  - [F] `.git/config` (137 B)
  - [F] `.git/description` (73 B)
  - [D] `.git/hooks`
    - [F] `.git/hooks/applypatch-msg.sample` (478 B)
    - [F] `.git/hooks/commit-msg.sample` (896 B)
    - [F] `.git/hooks/fsmonitor-watchman.sample` (4726 B)
    - [F] `.git/hooks/post-update.sample` (189 B)
    - [F] `.git/hooks/pre-applypatch.sample` (424 B)
    - [F] `.git/hooks/pre-commit.sample` (1649 B)
    - [F] `.git/hooks/pre-merge-commit.sample` (416 B)
    - [F] `.git/hooks/pre-push.sample` (1374 B)
    - [F] `.git/hooks/pre-rebase.sample` (4898 B)
    - [F] `.git/hooks/pre-receive.sample` (544 B)
    - [F] `.git/hooks/prepare-commit-msg.sample` (1492 B)
    - [F] `.git/hooks/push-to-checkout.sample` (2783 B)
    - [F] `.git/hooks/sendemail-validate.sample` (2308 B)
    - [F] `.git/hooks/update.sample` (3650 B)
  - [D] `.git/info`
    - [F] `.git/info/exclude` (240 B)
  - [D] `.git/objects`
    - [D] `.git/objects/info`
    - [D] `.git/objects/pack`
  - [D] `.git/refs`
    - [D] `.git/refs/heads`
    - [D] `.git/refs/tags`
- [D] `output`
  - [F] `output/.DS_Store` (14340 B)
  - [D] `output/audit`
    - [F] `output/audit/tcr_gateway_accusation_bundle_audit.json` (93168 B)
    - [F] `output/audit/tcr_gateway_accusation_bundle_audit.md` (22143 B)
    - [F] `output/audit/tcr_gateway_accusation_bundle_audit_report.pdf` (53315 B)
    - [F] `output/audit/tcr_gateway_accusation_bundle_audit_strict.json` (91691 B)
    - [F] `output/audit/tcr_gateway_accusation_bundle_audit_strict.md` (20426 B)
    - [F] `output/audit/tcr_gateway_accusation_bundle_audit_strict_report.pdf` (52252 B)
    - [F] `output/audit/tcr_gateway_artifact_type_policy_smoke_strict.json` (5989 B)
    - [F] `output/audit/tcr_gateway_artifact_type_policy_smoke_strict.md` (2061 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit.json` (1214381 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit.md` (168298 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_strict.json` (1209946 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_strict.md` (163068 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_strict_91_files_reasons.csv` (50807 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_strict_91_files_reasons.md` (18730 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_strict_report.pdf` (250719 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_ocr_errors.csv` (119 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_ocr_errors.md` (322 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict.json` (1856915 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict.md` (202103 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict_92_files_reasons.csv` (58241 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict_92_files_reasons.md` (45589 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict_executive_summary_1page.pdf` (3281 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict_report.pdf` (253914 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict_resumo_executivo_1pagina_ptbr.pdf` (3429 B)
    - [F] `output/audit/tcr_gateway_bernardo_notion_test_audit_with_images_strict_resumo_executivo_peticao_ready_1pagina.pdf` (3514 B)
    - [F] `output/audit/tcr_gateway_pdf_audit_report.pdf` (11490 B)
    - [F] `output/audit/tcr_gateway_pdf_audit_results.json` (7486 B)
    - [F] `output/audit/tcr_gateway_pdf_audit_results.md` (4627 B)
  - [D] `output/gateway`
    - [F] `output/gateway/tcr_signals_gateway_file.json` (219504 B)
  - [D] `output/pdf`
    - [F] `output/pdf/tcr-ia-compliance-gateway-summary-one-page.pdf` (3675 B)
    - [F] `output/pdf/tcr_gateway_bernardo_notion_test_audit_with_images_strict_executive_summary_1page.pdf` (3285 B)
  - [D] `output/project_snapshot`
- [D] `scripts`
  - [F] `scripts/.audit_accusation_bundle_with_tcr_gateway.py.swp` (16384 B)
  - [F] `scripts/audit_accusation_bundle_with_tcr_gateway.py` (37641 B)
  - [F] `scripts/audit_pdfs_with_tcr_gateway.py` (12914 B)
  - [F] `scripts/generate_accusation_bundle_audit_report_pdf.py` (14188 B)
  - [F] `scripts/generate_app_summary_pdf.py` (16269 B)
  - [F] `scripts/generate_bernardo_accusatory_executive_summary_pdf.py` (8525 B)
  - [F] `scripts/generate_bernardo_accusatory_executive_summary_pdf_peticao.py` (7778 B)
  - [F] `scripts/generate_bernardo_accusatory_executive_summary_pdf_ptbr.py` (9069 B)
  - [F] `scripts/generate_tcr_audit_report_pdf.py` (13930 B)
  - [F] `scripts/generate_tcr_signals_gateway_file.py` (20168 B)
- [D] `tmp`
  - [F] `tmp/.DS_Store` (8196 B)
  - [D] `tmp/pdfs`

## Notes

- Snapshot generated after strict+OCR rerun with artifact-type compliance policy and HEIC OCR fix.
- Use this file as a baseline for future diffs/versioning.