#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


WORKSPACE = Path("/Users/rodrigobaptistadasilva/Documents/New project")
DOWNLOADS = Path("/Users/rodrigobaptistadasilva/Downloads")
OUTPUT_DIR = WORKSPACE / "output" / "audit"
JSON_OUT = OUTPUT_DIR / "tcr_gateway_accusation_bundle_audit.json"
MD_OUT = OUTPUT_DIR / "tcr_gateway_accusation_bundle_audit.md"

ENGINE_NAME = "tcria"
ENGINE_VERSION = "0.1.0"


# Scope resolver for the exact user-provided bundle (via patterns + exact names).
DISCOVERY_PATTERNS = [
    "8690*.txt",
    "*Bradesco*.csv",
    "*Bradesco*.docx",
    "*Bradesco*.txt",
    "*Dossie*.docx",
    "*dossie*.docx",
    "*Golpe*.docx",
    "*Vinícius*.docx",
    "*Vinicius*.docx",
    "*MP*.docx",
    "*OAB*.docx",
    "*Memoria*Rodrigo*.docx",
    "Documento (*.docx",
    "Faturas*.csv",
    "Faturas*.docx",
    "artist_nodes.csv",
    "Senhas.csv",
]

EXACT_FILES = [
    DOWNLOADS / "2023-11-18T12[]48[]14-7.csv",
    DOWNLOADS / "Informações Positivas bradesco.webarchive",
    DOWNLOADS / "# 📘 Dossiê Ampliado — Caso Vinícius Carvalho.docx",
    DOWNLOADS / "📘 Dossiê Ampliado — Caso Vinícius Carvalho.docx",
]

SENSITIVE_FILENAMES = {"senhas.csv"}
SUPPORTED_SUFFIXES = {".pdf", ".docx", ".rtf", ".webarchive", ".txt", ".csv", ".md", ".png", ".jpg", ".jpeg", ".heic"}

# Project-derived prescriptive gate (from the RTF).
PRESCRIPTIVE_PATTERNS = [
    "você deve",
    "deve-se",
    "é obrigatório",
    "é necessario",
    "é necessário",
    "a única solução é",
]

ACCUSATION_KEYWORDS = [
    "fraude",
    "golpe",
    "acusação",
    "acusacao",
    "denúncia",
    "denuncia",
    "reclamação",
    "reclamacao",
    "ressarcimento",
    "prejuízo",
    "prejuizo",
    "negligência",
    "negligencia",
    "omissão",
    "omissao",
    "não autorizado",
    "nao autorizado",
    "réu",
    "reu",
    "ação civil",
    "acao civil",
    "ministério público",
    "ministerio publico",
    "oab",
    "ético",
    "etico",
]

# Regex patterns for legal-office refinement (v1).
LEGAL_STRONG_PATTERNS = [
    r"\bart\.?\s*\d+[a-zA-Z]?\b",
    r"§\s*\d+º?",
    r"\binciso\s+[IVXLC]+\b",
    r"\bal[ií]nea\s+[a-z]\b",
    r"\bcaput\b",
    r"\blei\s*(n[ºo]\.?\s*)?\d{1,5}[./]\d{2,4}\b",
    r"\blei\s*(n[ºo]\.?\s*)?\d{1,5}\b",
    r"\bs[úu]mula\s*\d+\b",
    r"\btema\s*\d+\b",
    r"\bresp\s*\d+",
    r"\baresp\s*\d+",
    r"\bagint\b",
    r"\badi\b",
    r"\badc\b",
    r"\badpf\b",
    r"\bresolu[cç][aã]o\s*\d+",
    r"\bcircular\s*\d+",
    r"\binstru[cç][aã]o\s+normativa\s*\d+",
    r"\bportaria\s*\d+",
]

LEGAL_MEDIUM_PATTERNS = [
    r"\bcdc\b",
    r"c[oó]digo\s+de\s+defesa\s+do\s+consumidor",
    r"\bcpc\b",
    r"c[oó]digo\s+de\s+processo\s+civil",
    r"c[oó]digo\s+civil",
    r"\blgpd\b",
    r"lei\s+geral\s+de\s+prote[cç][aã]o\s+de\s+dados",
    r"constitui[cç][aã]o\s+federal",
    r"responsabilidade\s+objetiva",
    r"dano\s+moral",
    r"[ôo]nus\s+da\s+prova",
    r"invers[aã]o\s+do\s+[ôo]nus",
    r"tutela\s+de\s+urg[eê]ncia",
    r"nexo\s+causal",
    r"verossimilhan[cç]a",
    r"hipossufici[eê]ncia",
]

ACCUSATION_PATTERNS = [
    r"\bfraude\b",
    r"\bgolpe\b",
    r"\bestelionat",
    r"n[aã]o\s+reconhe[cç]o",
    r"n[aã]o\s+autorizei",
    r"\bindevid",
    r"\bclonad",
    r"\bphishing\b",
    r"engenharia\s+social",
    r"acesso\s+indevido",
    r"invas[aã]o",
    r"movimenta[cç][aã]o\s+at[ií]pica",
    r"pix\s+n[aã]o\s+autorizad",
    r"transfer[eê]ncia\s+n[aã]o\s+autorizad",
    r"\bpreju[ií]zo\b",
]

EVIDENCE_MARKER_KEYWORDS = [
    "provas",
    "extratos",
    "faturas",
    "comprovante",
    "comprovantes",
    "pix",
    "transferência",
    "transferencia",
    "e-mail",
    "emails",
    "logs",
    "timeline",
    "linha do tempo",
    "anexo",
    "anexos",
]

TARGET_ENTITY_KEYWORDS = [
    "bradesco",
    "vinícius",
    "vinicius",
    "rodrigo baptista",
    "banco",
]


@dataclass
class GateResult:
    status: str
    reason: str
    evidence: Optional[str] = None


@dataclass
class FileRecord:
    file_name: str
    file_path: str
    suffix: str
    size_bytes: int
    sha256: str
    extraction_status: str
    extraction_method: str
    text_chars: int
    text_quality: str
    sensitive_handling: str
    classification: str
    artifact_type: str
    artifact_type_reason: str
    raises_accusation: bool
    classification_reasons: List[str]
    artifact_identity: Dict[str, object]
    key_signals: Dict[str, object]
    gates: Optional[Dict[str, Dict[str, object]]]
    overall_outcome: Optional[str]


@dataclass
class AuditMode:
    strict_explicit_decision_record: bool = False

    @property
    def slug(self) -> str:
        return "strict" if self.strict_explicit_decision_record else "default"

    @property
    def label(self) -> str:
        return "strict-explicit-decision-record" if self.strict_explicit_decision_record else "default-heuristic"

    @property
    def gate_policy_version(self) -> str:
        if self.strict_explicit_decision_record:
            return "strict-explicit-decision-record-v1"
        return "default-heuristic-v1"


def discover_files() -> List[Path]:
    seen: List[Path] = []
    for pattern in DISCOVERY_PATTERNS:
        for path in DOWNLOADS.glob(pattern):
            if path.exists() and path not in seen:
                seen.append(path)
    for path in EXACT_FILES:
        if path.exists() and path not in seen:
            seen.append(path)
    return sorted(seen, key=lambda p: p.name.lower())


def resolve_input_paths(inputs: Optional[List[str]]) -> List[Path]:
    if not inputs:
        return discover_files()

    seen: List[Path] = []
    for raw in inputs:
        p = Path(raw).expanduser()
        if not p.exists():
            continue
        if p.is_dir():
            for child in sorted(p.rglob("*")):
                if child.is_file() and child.suffix.lower() in SUPPORTED_SUFFIXES and child not in seen:
                    seen.append(child)
            continue
        if p.is_file() and p.suffix.lower() in SUPPORTED_SUFFIXES and p not in seen:
            seen.append(p)
    return sorted(seen, key=lambda path: (path.name.lower(), str(path).lower()))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def lower_norm(text: str) -> str:
    return normalize(text).lower()


def classify_text_quality(chars: int, suffix: str) -> str:
    if chars == 0:
        return "none"
    thresholds = {
        ".csv": (600, 150),
        ".txt": (1200, 250),
        ".docx": (1200, 300),
        ".webarchive": (1000, 200),
    }
    hi, mid = thresholds.get(suffix, (1000, 250))
    if chars >= hi:
        return "high"
    if chars >= mid:
        return "medium"
    return "low"


def decode_bytes(raw: bytes) -> Tuple[str, str]:
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin1"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin1", errors="replace"), "latin1-replace"


def extract_text_with_textutil(path: Path) -> Tuple[str, str, str]:
    cp = subprocess.run(
        ["textutil", "-convert", "txt", "-stdout", str(path)],
        capture_output=True,
        text=True,
    )
    if cp.returncode != 0:
        return "", "error", "textutil"
    return cp.stdout or "", "ok", "textutil"


def extract_text_from_pdf(path: Path) -> Tuple[str, str, str]:
    pdftotext = None
    try:
        pdftotext = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            capture_output=True,
            text=True,
        )
        if pdftotext.returncode == 0 and (pdftotext.stdout or "").strip():
            return pdftotext.stdout, "ok", "pdftotext"
    except FileNotFoundError:
        pdftotext = None

    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(path))
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        text = "\n".join(pages)
        return text, "ok", "pypdf"
    except Exception:
        if pdftotext is not None and pdftotext.returncode != 0:
            return "", "error", "pdftotext"
        if pdftotext is None:
            return "", "error", "pdf_no_extractor"
        return "", "ok", "pdftotext"


def extract_text_from_image(path: Path) -> Tuple[str, str, str]:
    # Optional local OCR via tesseract. If unavailable, classify as OCR-unavailable without crashing the batch.
    target_path = path
    cleanup_tmp: Optional[Path] = None

    # Tesseract often fails on HEIC directly; convert to PNG first using macOS `sips` when available.
    if path.suffix.lower() == ".heic" and shutil.which("sips"):
        fd, tmp_name = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        tmp = Path(tmp_name)
        try:
            cp_conv = subprocess.run(
                ["sips", "-s", "format", "png", str(path), "--out", str(tmp)],
                capture_output=True,
                text=True,
            )
            if cp_conv.returncode == 0 and tmp.exists() and tmp.stat().st_size > 0:
                target_path = tmp
                cleanup_tmp = tmp
        except Exception:
            try:
                if tmp.exists():
                    tmp.unlink()
            except Exception:
                pass

    try:
        cp = subprocess.run(
            ["tesseract", str(target_path), "stdout", "-l", "por+eng"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        if cleanup_tmp and cleanup_tmp.exists():
            cleanup_tmp.unlink(missing_ok=True)
        return "", "ocr_unavailable", "tesseract_missing"

    if cp.returncode != 0:
        # Try without language pack selection as a fallback.
        cp2 = subprocess.run(["tesseract", str(target_path), "stdout"], capture_output=True, text=True)
        if cleanup_tmp and cleanup_tmp.exists():
            cleanup_tmp.unlink(missing_ok=True)
        if cp2.returncode != 0:
            return "", "error", "tesseract"
        return cp2.stdout or "", "ok", "tesseract"
    if cleanup_tmp and cleanup_tmp.exists():
        cleanup_tmp.unlink(missing_ok=True)
    return cp.stdout or "", "ok", "tesseract"


def extract_text(path: Path) -> Tuple[str, str, str]:
    suffix = path.suffix.lower()
    if path.name.lower() in SENSITIVE_FILENAMES:
        return "", "skipped_sensitive", "none"

    if suffix in {".docx", ".rtf", ".webarchive"}:
        return extract_text_with_textutil(path)

    if suffix in {".txt", ".csv", ".md"}:
        raw = path.read_bytes()
        text, enc = decode_bytes(raw)
        return text, "ok", enc

    if suffix == ".pdf":
        return extract_text_from_pdf(path)

    if suffix in {".png", ".jpg", ".jpeg", ".heic"}:
        return extract_text_from_image(path)

    return "", "unsupported", "none"


def detect_prescriptive(text_l: str) -> GateResult:
    hits = [p for p in PRESCRIPTIVE_PATTERNS if p in text_l]
    if hits:
        return GateResult(
            status="BLOCKED",
            reason="Prescriptive language detected by project compliance layer.",
            evidence=", ".join(hits[:5]),
        )
    return GateResult(status="PASS", reason="No project-defined prescriptive patterns detected.")


def detect_declared_purpose(text: str) -> Tuple[bool, Optional[str]]:
    patterns = [
        r"\bobjetivo\s*:\s*([^\n]{0,180})",
        r"\bfinalidade\s*:\s*([^\n]{0,180})",
        r"\b(?:este|essa|o presente)\s+(?:documento|dossi[eê]|sum[áa]rio|relat[óo]rio)\s+visa\s+([^\n]{0,200})",
        r"\bencaminhamento\s+ao\s+mp\b",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            snippet = normalize(m.group(0))[:220]
            return True, snippet
    return False, None


def detect_declared_purpose_explicit(text: str) -> Tuple[bool, Optional[str]]:
    patterns = [
        r"\bobjetivo\s*:\s*([^\n]{1,200})",
        r"\bfinalidade\s*:\s*([^\n]{1,200})",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return True, normalize(m.group(0))[:220]
    return False, None


def detect_responsible_actor(text: str) -> Tuple[bool, Optional[str]]:
    patterns = [
        r"\brespons[áa]vel(?:\s+humano)?\s*:\s*([^\n]{1,140})",
        r"\bautor\s*:\s*([^\n]{1,140})",
        r"\bassinado por\s*:\s*([^\n]{1,140})",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return True, normalize(m.group(0))[:180]

    if re.search(r"\bRodrigo Baptista da Silva\b", text, flags=re.IGNORECASE) or re.search(
        r"\bVin[ií]cius Carvalho\b", text, flags=re.IGNORECASE
    ):
        return True, "Named individual(s) found in document body (heuristic, not explicit responsibility field)."
    return False, None


def detect_responsible_actor_explicit(text: str) -> Tuple[bool, Optional[str]]:
    patterns = [
        r"\brespons[áa]vel(?:\s+humano)?\s*:\s*([^\n]{1,160})",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return True, normalize(m.group(0))[:220]
    return False, None


def detect_explicit_approval(text: str) -> Tuple[bool, Optional[str]]:
    patterns = [
        r"\baprovad[oa]\b",
        r"\baprova[cç][aã]o\b",
        r"\bassinatura\b",
        r"\bassinado\b",
        r"\bvalidado\b",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return True, normalize(m.group(0))
    return False, None


def detect_explicit_approval_labeled(text: str) -> Tuple[bool, Optional[str]]:
    patterns = [
        r"\baprovad[oa]\s*:\s*([^\n]{0,120})",
        r"\baprova[cç][aã]o\s*:\s*([^\n]{0,120})",
    ]
    for pat in patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return True, normalize(m.group(0))[:180]
    return False, None


def infer_artifact_type(path: Path, text: str) -> Tuple[str, str]:
    name_l = path.name.lower()
    text_l = lower_norm(text) if text else ""

    analytical_name_markers = [
        "dossie",
        "dossiê",
        "analise",
        "análise",
        "painel",
        "bloco",
        "sumario",
        "sumário",
        "comparativo",
        "timeline",
        "linha do tempo",
        "_chat",
        "chat",
        "tcr-ia",
        "manual",
        "narrativa",
        "capítulo",
        "capitulo",
    ]
    decision_name_markers = [
        "peticao",
        "petição",
        "recurso",
        "pedido",
        "requerimento",
        "manifestacao",
        "manifestação",
        "encaminhamento",
        "contestacao",
        "contestação",
        "reclamacao",
        "reclamação",
        "oficio",
        "ofício",
        "consideracao",
        "consideração",
        "relato",
        "diligencia",
        "diligência",
    ]
    decision_text_markers = [
        "processo nº",
        "processo n°",
        "processo no",
        "vara de",
        "juíz",
        "juiz",
        "juíza",
        "juiza",
        "requeiro",
        "solicito",
        "solicitação",
        "solicitacao",
        "encaminhamento",
        "protocolo",
        "petição",
        "peticao",
        "recurso",
    ]

    if any(m in name_l for m in analytical_name_markers):
        return "ANALYTICAL_ARTIFACT", "Filename matches analytical/reporting markers (heuristic)."

    if any(m in name_l for m in decision_name_markers):
        return "DECISION_ARTIFACT", "Filename matches procedural/filing markers (heuristic)."

    if any(m in text_l for m in decision_text_markers):
        return "DECISION_ARTIFACT", "Content includes procedural/filing language (heuristic)."

    if path.suffix.lower() == ".md":
        return "ANALYTICAL_ARTIFACT", "Markdown page defaulted to analytical artifact."

    return "DECISION_ARTIFACT", "Fallback default for accusatory candidate documents."


def warn_if_missing_responsibility(text: str, mode: AuditMode) -> GateResult:
    if mode.strict_explicit_decision_record:
        has_actor, ev_actor = detect_responsible_actor_explicit(text)
        mode_label = "strict explicit"
    else:
        has_actor, ev_actor = detect_responsible_actor(text)
        mode_label = "heuristic"

    if not has_actor:
        return GateResult(
            status="WARN",
            reason=f"Analytical artifact: missing responsibleHuman indicator ({mode_label} check).",
            evidence=ev_actor,
        )
    return GateResult(
        status="PASS",
        reason=f"Analytical artifact: responsibility indicator found ({mode_label} check).",
        evidence=ev_actor,
    )


def compliance_gate(text: str, mode: AuditMode) -> GateResult:
    if mode.strict_explicit_decision_record:
        has_actor, ev_actor = detect_responsible_actor_explicit(text)
        has_purpose, ev_purpose = detect_declared_purpose_explicit(text)
        has_approval, ev_approval = detect_explicit_approval_labeled(text)
        mode_reason_prefix = "Strict explicit-label check"
    else:
        has_actor, ev_actor = detect_responsible_actor(text)
        has_purpose, ev_purpose = detect_declared_purpose(text)
        has_approval, ev_approval = detect_explicit_approval(text)
        mode_reason_prefix = "Heuristic check"

    missing = []
    if not has_actor:
        missing.append("responsibleHuman")
    if not has_purpose:
        missing.append("declaredPurpose")
    if not has_approval:
        missing.append("approved")

    evidence_parts = []
    if ev_actor:
        evidence_parts.append(f"actor={ev_actor}")
    if ev_purpose:
        evidence_parts.append(f"purpose={ev_purpose}")
    if ev_approval:
        evidence_parts.append(f"approval={ev_approval}")
    evidence = " | ".join(evidence_parts) if evidence_parts else None

    if missing:
        return GateResult(
            status="BLOCKED",
            reason=f"DecisionRecord incomplete (missing {', '.join(missing)}).",
            evidence=evidence,
        )
    return GateResult(
        status="PASS",
        reason=f"{mode_reason_prefix} found actor, purpose, and approval indicators in file text.",
        evidence=evidence,
    )


def compliance_gate_by_artifact_type(text: str, mode: AuditMode, artifact_type: str) -> GateResult:
    if artifact_type == "DECISION_ARTIFACT":
        return compliance_gate(text, mode)
    if artifact_type == "ANALYTICAL_ARTIFACT":
        return warn_if_missing_responsibility(text, mode)
    return compliance_gate(text, mode)


def maturity_gate() -> GateResult:
    return GateResult(
        status="NOT_EVALUATED",
        reason="KnowledgeCore.maturityScore is not available in static file content.",
    )


def ledger_runtime_gate() -> GateResult:
    return GateResult(
        status="NOT_APPLICABLE",
        reason="Static files do not expose runtime ledger events or hash-chain state.",
    )


def regex_count(pattern: str, text: str, flags: int = re.IGNORECASE) -> int:
    return len(re.findall(pattern, text, flags=flags))


def _count_patterns(text: str, patterns: List[str]) -> int:
    if not text:
        return 0
    total = 0
    for pat in patterns:
        total += len(re.findall(pat, text, flags=re.IGNORECASE))
    return total


def compute_densities(text: str) -> Dict[str, Dict[str, float]]:
    text_len = max(1, len(text))
    strong = _count_patterns(text, LEGAL_STRONG_PATTERNS)
    medium = _count_patterns(text, LEGAL_MEDIUM_PATTERNS)
    accus = _count_patterns(text, ACCUSATION_PATTERNS)

    strong_d = strong / (text_len / 1000.0)
    medium_d = medium / (text_len / 1000.0)
    accus_d = accus / (text_len / 1000.0)

    legal_refs_density = min(1.0, (0.10 * strong_d) + (0.05 * medium_d))
    accusation_density = min(1.0, 0.08 * accus_d)

    return {
        "counts": {
            "legal_strong": strong,
            "legal_medium": medium,
            "accusation": accus,
        },
        "densities": {
            "legal_refs_density": round(float(legal_refs_density), 6),
            "accusation_density": round(float(accusation_density), 6),
        },
    }


def infer_dataset_shape(text: str, suffix: str) -> Dict[str, object]:
    if suffix != ".csv":
        return {}
    lines = text.splitlines()
    row_count = len(lines)
    col_count = 0
    header = ""
    if lines:
        try:
            parsed = list(csv.reader(lines[:3]))
            col_count = max((len(r) for r in parsed), default=0)
            header = ",".join(parsed[0][:8]) if parsed else ""
        except Exception:
            header = lines[0][:200]
    return {"csv_rows_est": row_count, "csv_cols_est": col_count, "csv_header_preview": header[:200]}


def collect_signals(path: Path, text: str) -> Dict[str, object]:
    text_l = lower_norm(text) if text else ""
    density_bundle = compute_densities(text)
    density_counts = density_bundle["counts"]
    density_scores = density_bundle["densities"]
    signals: Dict[str, object] = {
        "dates_found": regex_count(r"\b\d{2}/\d{2}/\d{4}\b", text),
        "currency_values_found": regex_count(r"R\$\s*[\d\.,]+", text, flags=0),
        "pix_mentions": text_l.count("pix"),
        "email_mentions": regex_count(r"[\w\.-]+@[\w\.-]+\.\w+", text),
        "transaction_terms": sum(text_l.count(k) for k in ["transa", "fatura", "extrato", "lançamento", "lancamento"]),
        "accusation_keyword_hits": {k: text_l.count(k) for k in ACCUSATION_KEYWORDS if text_l.count(k) > 0},
        "evidence_marker_hits": {k: text_l.count(k) for k in EVIDENCE_MARKER_KEYWORDS if text_l.count(k) > 0},
        "target_entity_hits": {k: text_l.count(k) for k in TARGET_ENTITY_KEYWORDS if text_l.count(k) > 0},
        "contains_objetivo_label": bool(re.search(r"\bobjetivo\s*:", text, flags=re.IGNORECASE)),
        "contains_autor_label": bool(re.search(r"\bautor\s*:", text, flags=re.IGNORECASE)),
        "contains_summary_label": bool(re.search(r"\bresumo\b|\bsum[áa]rio\b", text, flags=re.IGNORECASE)),
        "legal_pattern_counts": density_counts,
        "density_scores": density_scores,
        # Canonical aliases for downstream gateway/scoring compatibility.
        "legal_refs_density": density_scores["legal_refs_density"],
        "legal_terms_density": density_scores["legal_refs_density"],
        "accusation_density": density_scores["accusation_density"],
    }
    signals.update(infer_dataset_shape(text, path.suffix.lower()))
    return signals


def classify_file(path: Path, extraction_status: str, text: str, signals: Dict[str, object]) -> Tuple[str, bool, List[str]]:
    name_l = path.name.lower()
    suffix = path.suffix.lower()
    reasons: List[str] = []

    if name_l in SENSITIVE_FILENAMES:
        return "SENSITIVE_EXCLUDED", False, ["Sensitive credentials file; content intentionally not read."]

    if extraction_status == "unsupported":
        return "UNSUPPORTED", False, ["Unsupported file type for this audit script."]

    if extraction_status == "error":
        return "UNREADABLE", False, ["Text extraction failed."]

    if extraction_status == "ocr_unavailable":
        return "OCR_UNAVAILABLE", False, ["Image OCR unavailable in local environment (tesseract not installed)."]

    if extraction_status == "ok" and len(text.strip()) == 0:
        return "UNREADABLE_OR_EMPTY", False, ["File is empty or yielded no extractable text."]

    accusation_terms = signals.get("accusation_keyword_hits", {}) or {}
    pattern_counts = (signals.get("legal_pattern_counts") or {})
    target_terms = signals.get("target_entity_hits", {}) or {}
    evidence_terms = signals.get("evidence_marker_hits", {}) or {}
    accusation_hits_keyword = sum(int(v) for v in accusation_terms.values())
    accusation_hits_pattern = int((pattern_counts or {}).get("accusation", 0) or 0)
    accusation_hits = max(accusation_hits_keyword, accusation_hits_pattern)
    target_hits = sum(int(v) for v in target_terms.values())
    evidence_hits = sum(int(v) for v in evidence_terms.values())
    legal_refs_density = float(signals.get("legal_refs_density", 0.0) or 0.0)

    filename_score = 0
    for kw in ["dossie", "dossiê", "fraude", "golpe", "reclamacao", "reclamação", "oab", "mp", "etica", "ético"]:
        if kw in name_l:
            filename_score += 2
    for kw in ["bradesco", "vinícius", "vinicius"]:
        if kw in name_l:
            filename_score += 1

    content_score = 0
    content_score += min(accusation_hits, 8)
    content_score += 2 if ("bradesco" in target_terms or "banco" in target_terms) and accusation_hits > 0 else 0
    content_score += 1 if signals.get("contains_objetivo_label") else 0
    content_score += 1 if signals.get("contains_autor_label") else 0
    if legal_refs_density >= 0.15:
        content_score += 2
    elif legal_refs_density >= 0.05:
        content_score += 1

    total_score = filename_score + content_score

    if suffix == ".csv":
        if "senha" in name_l:
            return "SENSITIVE_EXCLUDED", False, ["Sensitive credentials CSV."]
        reasons.append("CSV dataset treated primarily as supporting evidence/data source.")
        if accusation_hits >= 2 and target_hits > 0:
            reasons.append("CSV contains accusation-related terms; classified as supporting but relevant.")
            return "SUPPORTING_EVIDENCE_RELEVANT", False, reasons
        return "SUPPORTING_EVIDENCE", False, reasons

    if re.fullmatch(r"8690\d+\.txt", name_l):
        if accusation_hits + target_hits + evidence_hits >= 2:
            return "SUPPORTING_EVIDENCE_RELEVANT", False, ["Numeric text export/log with relevant terms."]
        return "SUPPORTING_EVIDENCE", False, ["Numeric text export/log file."]

    if suffix == ".webarchive":
        if len(text.strip()) == 0:
            return "UNREADABLE_OR_EMPTY", False, ["webarchive file appears empty."]

    if total_score >= 5 and (accusation_hits > 0 or any(k in name_l for k in ["dossie", "golpe", "fraude", "reclamacao", "mp", "oab"])):
        reasons.append(f"Accusatory score={total_score} (filename={filename_score}, content={content_score}).")
        if target_hits:
            reasons.append("Mentions target entity/person.")
        if evidence_hits:
            reasons.append("Contains evidence/documentation markers.")
        return "ACCUSATORY_CANDIDATE", True, reasons

    if evidence_hits > 0 or signals.get("transaction_terms", 0) > 0 or target_hits > 0:
        reasons.append("Relevant contextual/supporting content detected.")
        return "SUPPORTING_EVIDENCE_RELEVANT", False, reasons

    return "NEUTRAL_OR_CONTEXT", False, [f"Low accusation score={total_score}."]


def accusation_traceability_check(signals: Dict[str, object]) -> GateResult:
    dates = int(signals.get("dates_found", 0))
    money = int(signals.get("currency_values_found", 0))
    evidence_markers = sum((signals.get("evidence_marker_hits") or {}).values())
    pieces = []
    if dates > 0:
        pieces.append(f"dates={dates}")
    if money > 0:
        pieces.append(f"currency={money}")
    if evidence_markers > 0:
        pieces.append(f"evidence_markers={evidence_markers}")
    evidence = ", ".join(pieces) if pieces else None

    score = (1 if dates > 0 else 0) + (1 if money > 0 else 0) + (1 if evidence_markers > 0 else 0)
    if score >= 2:
        return GateResult(status="PASS", reason="Document contains multiple traceability/evidence signals.", evidence=evidence)
    if score == 1:
        return GateResult(status="WARN", reason="Document has limited traceability/evidence signals.", evidence=evidence)
    return GateResult(status="WARN", reason="No clear traceability/evidence signals detected in extracted text.", evidence=evidence)


def compute_gates(
    text: str,
    signals: Dict[str, object],
    mode: AuditMode,
    artifact_type: str,
) -> Tuple[Dict[str, Dict[str, object]], str]:
    prescriptive = detect_prescriptive(lower_norm(text))
    maturity = maturity_gate()
    compliance = compliance_gate_by_artifact_type(text, mode, artifact_type)
    ledger = ledger_runtime_gate()
    traceability = accusation_traceability_check(signals)

    if prescriptive.status == "BLOCKED":
        outcome = "BLOCKED (prescriptiveGate)"
    elif compliance.status == "BLOCKED":
        outcome = "BLOCKED (complianceGate)"
    elif traceability.status == "WARN":
        outcome = "PARTIAL_PASS (traceability warning; static audit)"
    else:
        outcome = "PARTIAL_PASS (static document audit; maturity/ledger not evaluated)"

    return {
        "prescriptiveGate": asdict(prescriptive),
        "maturityGate": asdict(maturity),
        "complianceGate": asdict(compliance),
        "ledgerRuntimeCheck": asdict(ledger),
        "traceabilityCheck": asdict(traceability),
    }, outcome


def build_markdown(payload: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append("# Nova Auditoria - Conjunto de Arquivos que Levantam Acusacao (TCR-IA style)")
    lines.append("")
    lines.append("Base: gates do projeto (prescriptive/compliance) adaptados para arquivos estaticos.")
    lines.append("")
    lines.append(f"- Modo de complianceGate: `{payload.get('compliance_gate_mode', 'default-heuristic')}`")
    lines.append(f"- Gerado em: `{payload['generated_at']}`")
    lines.append(f"- Arquivos varridos: `{payload['total_files_scanned']}`")
    lines.append(f"- Arquivos no conjunto acusatorio auditado: `{payload['accusation_set_count']}`")
    lines.append(f"- Contagens por classificacao: `{payload['classification_counts']}`")
    lines.append("")
    lines.append("## Resultado resumido (conjunto acusatorio)")
    lines.append("")

    for rec in payload["accusation_set"]:
        lines.append(f"### {rec['file_name']}")
        lines.append(f"- Resultado: `{rec['overall_outcome']}`")
        lines.append(f"- Tipo: `{rec['suffix']}` | texto extraido: `{rec['text_chars']}` chars | qualidade: `{rec['text_quality']}`")
        lines.append(f"- Classificacao: `{rec['classification']}`")
        lines.append(f"- Motivos da classificacao: {', '.join(rec['classification_reasons'])}")
        gates = rec["gates"] or {}
        for gate_name in ["prescriptiveGate", "complianceGate", "traceabilityCheck", "maturityGate", "ledgerRuntimeCheck"]:
            gate = gates.get(gate_name)
            if not gate:
                continue
            lines.append(f"- `{gate_name}`: `{gate['status']}` - {gate['reason']}")
            if gate.get("evidence"):
                lines.append(f"  Evidence: {gate['evidence']}")
        ks = rec["key_signals"]
        lines.append(
            f"- Sinais: dates={ks.get('dates_found',0)}, currency={ks.get('currency_values_found',0)}, "
            f"pix={ks.get('pix_mentions',0)}, emails={ks.get('email_mentions',0)}"
        )
        identity = rec.get("artifact_identity") or {}
        if identity:
            lines.append(
                "- Identity: "
                f"sha256={str(identity.get('file_sha256', '-'))[:16]}..., "
                f"engine={identity.get('engine','-')}@{identity.get('engine_version','-')}, "
                f"policy={identity.get('gate_policy_version','-')}"
            )
        lines.append("")

    lines.append("## Arquivos nao auditados como acusatorios (resumo)")
    lines.append("")
    for rec in payload["non_accusation_set"]:
        lines.append(
            f"- `{rec['file_name']}` -> `{rec['classification']}`"
            + (f" ({rec['classification_reasons'][0]})" if rec.get("classification_reasons") else "")
        )
    lines.append("")
    lines.append("## Observacoes")
    lines.append("")
    lines.append("- Esta auditoria nao verifica veracidade juridica/fatica das alegacoes; avalia forma/documentacao textual.")
    lines.append("- `maturityGate` e controles de ledger/hash/HMAC exigem runtime/sistema e nao sao inferiveis de arquivos estaticos.")
    lines.append("- `Senhas.csv` foi tratado como sensivel e nao teve conteudo exibido/lido para esta auditoria.")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit accusation-related file bundle using TCR-IA-style gates.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Require explicit labels for DecisionRecord fields (Responsavel, Finalidade/Objetivo, Aprovado/Aprovacao).",
    )
    parser.add_argument(
        "--path",
        action="append",
        dest="paths",
        help="File or directory to include in this audit (repeatable). If omitted, uses the legacy Bradesco bundle discovery.",
    )
    parser.add_argument(
        "--output-stem",
        default=None,
        help="Custom output filename stem (without extension).",
    )
    args = parser.parse_args()

    mode = AuditMode(strict_explicit_decision_record=args.strict)
    run_generated_at = datetime.now().isoformat(timespec="seconds")
    files = resolve_input_paths(args.paths)
    if not files:
        raise SystemExit("No files discovered for the configured scope.")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    records: List[FileRecord] = []
    for path in files:
        suffix = path.suffix.lower()
        size = path.stat().st_size
        digest = sha256_file(path)
        text, extraction_status, extraction_method = extract_text(path)

        sensitive_handling = "skipped_content" if path.name.lower() in SENSITIVE_FILENAMES else "normal"
        text_chars = len(text)
        text_quality = classify_text_quality(text_chars, suffix)
        signals = collect_signals(path, text) if extraction_status == "ok" and text else {
            "dates_found": 0,
            "currency_values_found": 0,
            "pix_mentions": 0,
            "email_mentions": 0,
            "transaction_terms": 0,
            "accusation_keyword_hits": {},
            "evidence_marker_hits": {},
            "target_entity_hits": {},
            "contains_objetivo_label": False,
            "contains_autor_label": False,
            "contains_summary_label": False,
            "legal_pattern_counts": {"legal_strong": 0, "legal_medium": 0, "accusation": 0},
            "density_scores": {"legal_refs_density": 0.0, "accusation_density": 0.0},
            "legal_refs_density": 0.0,
            "legal_terms_density": 0.0,
            "accusation_density": 0.0,
        }
        if suffix == ".csv":
            signals.update(infer_dataset_shape(text, suffix) if text else {"csv_rows_est": 0, "csv_cols_est": 0, "csv_header_preview": ""})

        classification, raises_accusation, reasons = classify_file(path, extraction_status, text, signals)
        artifact_type = "N/A"
        artifact_type_reason = "Not evaluated (non-accusatory or unreadable)."
        artifact_identity = {
            "file_sha256": digest,
            "engine": ENGINE_NAME,
            "engine_version": ENGINE_VERSION,
            "gate_policy_version": mode.gate_policy_version,
            "source_path": str(path),
            "generated_at": run_generated_at,
        }

        gates = None
        overall = None
        if raises_accusation and extraction_status == "ok" and text:
            artifact_type, artifact_type_reason = infer_artifact_type(path, text)
            gates, overall = compute_gates(text, signals, mode, artifact_type)

        records.append(
            FileRecord(
                file_name=path.name,
                file_path=str(path),
                suffix=suffix,
                size_bytes=size,
                sha256=digest,
                extraction_status=extraction_status,
                extraction_method=extraction_method,
                text_chars=text_chars,
                text_quality=text_quality,
                sensitive_handling=sensitive_handling,
                classification=classification,
                artifact_type=artifact_type,
                artifact_type_reason=artifact_type_reason,
                raises_accusation=raises_accusation,
                classification_reasons=reasons,
                artifact_identity=artifact_identity,
                key_signals=signals,
                gates=gates,
                overall_outcome=overall,
            )
        )

    accusation_set = [asdict(r) for r in records if r.raises_accusation]
    non_accusation_set = [asdict(r) for r in records if not r.raises_accusation]
    counts: Dict[str, int] = {}
    for r in records:
        counts[r.classification] = counts.get(r.classification, 0) + 1

    payload = {
        "generated_at": run_generated_at,
        "audit_basis": "TCR-IA project-style static document audit (prescriptiveGate, complianceGate, traceabilityCheck)",
        "compliance_gate_mode": mode.label,
        "engine": ENGINE_NAME,
        "engine_version": ENGINE_VERSION,
        "gate_policy_version": mode.gate_policy_version,
        "input_scope": args.paths or ["legacy_discovery_bundle"],
        "total_files_scanned": len(records),
        "accusation_set_count": len(accusation_set),
        "classification_counts": counts,
        "accusation_set": accusation_set,
        "non_accusation_set": non_accusation_set,
    }

    if args.output_stem:
        stem = args.output_stem + ("_strict" if mode.strict_explicit_decision_record else "")
        json_out = OUTPUT_DIR / f"{stem}.json"
        md_out = OUTPUT_DIR / f"{stem}.md"
    else:
        json_out = JSON_OUT if not mode.strict_explicit_decision_record else OUTPUT_DIR / "tcr_gateway_accusation_bundle_audit_strict.json"
        md_out = MD_OUT if not mode.strict_explicit_decision_record else OUTPUT_DIR / "tcr_gateway_accusation_bundle_audit_strict.md"

    json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    md_out.write_text(build_markdown(payload), encoding="utf-8")

    print(f"Mode: {mode.label}")
    print(f"JSON report: {json_out}")
    print(f"Markdown report: {md_out}")
    print(f"Total scanned: {len(records)}")
    print(f"Accusation set: {len(accusation_set)}")
    for rec in accusation_set:
        print(f"- {rec['file_name']}: {rec['overall_outcome']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
