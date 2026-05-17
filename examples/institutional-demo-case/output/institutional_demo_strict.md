# TCRIA Audit Report

- Generated at: `2026-05-17T00:48:38`
- Input path: `<repo>/examples/institutional-demo-case/input`
- Mode: `strict-explicit-decision-record`
- Total files scanned: `2`
- Accusation set count: `1`
- Classification counts: `{'ACCUSATORY_CANDIDATE': 1, 'SUPPORTING_EVIDENCE_RELEVANT': 1}`
- Route counts: `{'CIVIL_CRIMINAL_INVESTIGATIVE': 1, 'EVIDENTIARY_SUPPORT_GENERAL': 1}`
- Document role counts: `{'ANALYTICAL_SUMMARY': 1, 'SUPPORTING_PROOF': 1}`

## Accusation Set

### relatorio_ungoverned_claim.txt
- Outcome: `BLOCKED (complianceGate)`
- Classification: `ACCUSATORY_CANDIDATE`
- Route: `CIVIL_CRIMINAL_INVESTIGATIVE`
- Document role: `ANALYTICAL_SUMMARY`
- Discursive posture: `ACCUSATORY`
- Reasons: Audit route=CIVIL_CRIMINAL_INVESTIGATIVE (HIGH), Document role=ANALYTICAL_SUMMARY, Discursive posture=ACCUSATORY, High-severity accusation terms=1, Investigative markers=1, Target entity hits=1, Evidence markers=0
- `prescriptiveGate`: `PASS` - No prescriptive patterns detected.
- `complianceGate`: `BLOCKED` - DecisionRecord header not found in strict mode.
- `traceabilityCheck`: `PASS` - Multiple traceability signals found.
- `maturityGate`: `NOT_EVALUATED` - KnowledgeCore.maturityScore is not available in static file content.
- `ledgerRuntimeCheck`: `NOT_APPLICABLE` - Static files do not expose runtime ledger events or hash-chain state.
