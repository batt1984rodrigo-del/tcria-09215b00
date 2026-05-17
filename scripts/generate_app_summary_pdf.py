#!/usr/bin/env python3
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

from pypdf import PdfReader
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas


WORKSPACE = Path("/Users/rodrigobaptistadasilva/Documents/New project")
RTF_PATH = Path("/Users/rodrigobaptistadasilva/Downloads/meu projeto de auditoria de 20k.rtf")
OUTPUT_PDF = WORKSPACE / "output" / "pdf" / "tcr-ia-compliance-gateway-summary-one-page.pdf"
TMP_PDF_DIR = WORKSPACE / "tmp" / "pdfs"

NOT_FOUND = "Not found in repo."
POLICY_SNIPPET = """
import { appendLedgerEvent } from "./ledger_service";

const POLICY_VERSION = "policy-v1.0.0";

export async function processOutputPersisted(
  tenantId: string,
  streamId: string,
  core: KnowledgeCore,
  output: CognitiveOutput,
  record?: DecisionRecord
) {
  await appendLedgerEvent({
    tenantId,
    streamId,
    event: "LLM_RETURNED",
    coreId: core.id,
    outputId: output.id,
    policyVersion: POLICY_VERSION,
    payload: { rawPreview: output.rawText.slice(0, 120) }
  });

  try {
    prescriptiveGate(output);
    maturityGate(core);
    complianceGate(record);

    await appendLedgerEvent({
      tenantId,
      streamId,
      event: "DECISION_APPROVED",
      coreId: core.id,
      outputId: output.id,
      actorId: record?.responsibleHuman,
      purpose: record?.declaredPurpose,
      policyVersion: POLICY_VERSION,
      payload: { approved: true }
    });

    return { status: "APPROVED_FOR_USE", outputId: output.id };
  } catch (err: any) {
    const reason = err?.message ?? "Unknown error";

    await appendLedgerEvent({
      tenantId,
      streamId,
      event: "POSTCHECK_BLOCKED",
      coreId: core.id,
      outputId: output.id,
      purpose: record?.declaredPurpose,
      policyVersion: POLICY_VERSION,
      reason,
      payload: { approved: false }
    });

    return { status: "BLOCKED", outputId: output.id, reason };
  }
}
""".strip()


@dataclass
class SummaryContent:
    title: str
    subtitle: str
    what_it_is: List[str]
    who_its_for: str
    what_it_does: List[str]
    how_it_works: List[Tuple[str, str]]
    how_to_run: List[str]
    evidence_note: str
    repo_note: str


@dataclass
class RenderMetrics:
    left_min_y: float
    right_min_y: float
    bottom_margin: float


def run_cmd(args: List[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def extract_rtf_text(rtf_path: Path) -> str:
    result = run_cmd(["textutil", "-convert", "txt", "-stdout", str(rtf_path)])
    return result.stdout


def inspect_repo(workspace: Path) -> str:
    if not (workspace / ".git").exists():
        return "Repo evidence check: .git directory not found."

    tracked = run_cmd(["git", "ls-files"], cwd=workspace, check=False)
    has_no_tracked_files = tracked.returncode == 0 and tracked.stdout.strip() == ""

    head = run_cmd(["git", "rev-parse", "--verify", "HEAD"], cwd=workspace, check=False)
    has_no_commits = head.returncode != 0

    if has_no_tracked_files and has_no_commits:
        return (
            "Repo evidence check: /Users/rodrigobaptistadasilva/Documents/New project "
            "is an empty git repo (no commits or tracked files)."
        )

    return (
        "Repo evidence check: repo exists, but this PDF intentionally marks architecture/run "
        "items as Not found in repo. for this request."
    )


def parse_snippet_evidence(snippet: str) -> Tuple[List[str], List[str]]:
    events = sorted(set(re.findall(r'event:\s*"([^"]+)"', snippet)))
    statuses = sorted(set(re.findall(r'status:\s*"([^"]+)"', snippet)))
    return events, statuses


def verify_rtf_markers(rtf_text: str) -> None:
    required_markers = [
        "detectPrescriptiveLanguage",
        "maturityGate",
        "complianceGate",
        "ledger_entries",
        "hmacSha256",
        "EvidencePack",
    ]
    missing = [marker for marker in required_markers if marker not in rtf_text]
    if missing:
        raise RuntimeError(f"RTF source is missing expected markers: {', '.join(missing)}")


def build_content(rtf_text: str, repo_note: str) -> SummaryContent:
    verify_rtf_markers(rtf_text)
    events, statuses = parse_snippet_evidence(POLICY_SNIPPET)
    if not {"LLM_RETURNED", "DECISION_APPROVED", "POSTCHECK_BLOCKED"}.issubset(set(events)):
        raise RuntimeError("Snippet evidence is missing expected ledger events.")
    if not {"APPROVED_FOR_USE", "BLOCKED"}.issubset(set(statuses)):
        raise RuntimeError("Snippet evidence is missing expected statuses.")

    events_text = ", ".join(events)
    return SummaryContent(
        title="TCR-IA Compliance Gateway",
        subtitle="One-page app summary (RTF + provided code snippet; repo evidence gap flagged)",
        what_it_is=[
            (
                "A compliance gateway pattern for AI outputs that applies governance checks before a "
                "result is considered usable in decision workflows."
            ),
            (
                "It combines policy gates, human accountability controls, and audit-grade evidence "
                "records (ledger + export pack) to support traceability and formal review."
            ),
        ],
        who_its_for=(
            "Primary users are AI governance/compliance teams, internal audit, and risk/platform teams "
            "operating AI-assisted decisions in regulated or high-accountability environments."
        ),
        what_it_does=[
            "Detects prescriptive language (for example, commands or mandatory wording) and blocks non-compliant outputs.",
            "Applies a maturity gate to the KnowledgeCore before decision-level output can proceed.",
            "Requires a human decision record with responsible actor, declared purpose, and explicit approval.",
            "Returns APPROVED_FOR_USE on success or BLOCKED with a reason when any post-check fails.",
            "Maintains append-only audit evidence with hash chaining and per-tenant HMAC signing.",
            f"Persists ledger events around output handling ({events_text}) and supports evidence-pack export (JSON + PDF).",
        ],
        how_it_works=[
            ("Components", NOT_FOUND),
            ("Services", NOT_FOUND),
            ("Data flow", NOT_FOUND),
        ],
        how_to_run=[
            f"Entry point / startup command: {NOT_FOUND}",
            f"Dependencies / install steps: {NOT_FOUND}",
            f"Environment variables / config: {NOT_FOUND}",
        ],
        evidence_note=(
            "Functional summary based on local RTF document and provided processOutputPersisted(...) snippet. "
            "Architecture and run instructions were not verifiable from repo contents."
        ),
        repo_note=repo_note,
    )


def string_width(text: str, font_name: str, font_size: float) -> float:
    return pdfmetrics.stringWidth(text, font_name, font_size)


def wrap_text(text: str, width: float, font_name: str, font_size: float) -> List[str]:
    words = text.split()
    if not words:
        return [""]
    lines: List[str] = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        if string_width(candidate, font_name, font_size) <= width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def draw_wrapped_text(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    text: str,
    *,
    font_name: str = "Helvetica",
    font_size: float = 9.0,
    leading: float | None = None,
    color_rgb: Tuple[float, float, float] | None = None,
) -> float:
    leading = leading or font_size * 1.25
    lines = wrap_text(text, width, font_name, font_size)
    c.setFont(font_name, font_size)
    if color_rgb:
        c.setFillColorRGB(*color_rgb)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    c.setFillColorRGB(0, 0, 0)
    return y


def draw_bullet_list(
    c: canvas.Canvas,
    x: float,
    y: float,
    width: float,
    items: Iterable[str],
    *,
    font_name: str = "Helvetica",
    font_size: float = 9.0,
    bullet_gap: float = 9.0,
    line_gap: float = 1.25,
    item_spacing: float = 1.5,
) -> float:
    leading = font_size * line_gap
    bullet_prefix = "- "
    bullet_width = string_width(bullet_prefix, font_name, font_size)
    indent = bullet_width + bullet_gap
    text_width = max(1.0, width - indent)

    c.setFont(font_name, font_size)
    for item in items:
        lines = wrap_text(item, text_width, font_name, font_size)
        c.drawString(x, y, bullet_prefix)
        c.drawString(x + indent, y, lines[0])
        y -= leading
        for line in lines[1:]:
            c.drawString(x + indent, y, line)
            y -= leading
        y -= item_spacing
    return y


def draw_section_header(c: canvas.Canvas, x: float, y: float, text: str, width: float) -> float:
    c.setFont("Helvetica-Bold", 10.5)
    c.setFillColorRGB(0.08, 0.14, 0.2)
    c.drawString(x, y, text)
    y -= 3
    c.setStrokeColorRGB(0.80, 0.85, 0.9)
    c.setLineWidth(0.6)
    c.line(x, y, x + width, y)
    c.setFillColorRGB(0, 0, 0)
    return y - 10


def generate_pdf(content: SummaryContent, out_path: Path) -> RenderMetrics:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    TMP_PDF_DIR.mkdir(parents=True, exist_ok=True)

    page_w, page_h = letter
    margin = 36.0  # 0.5 in
    gutter = 18.0
    usable_w = page_w - (2 * margin)
    left_w = usable_w * 0.58 - gutter / 2
    right_w = usable_w - left_w - gutter
    left_x = margin
    right_x = left_x + left_w + gutter

    c = canvas.Canvas(str(out_path), pagesize=letter)
    c.setTitle("TCR-IA Compliance Gateway - One-page Summary")
    c.setAuthor("OpenAI Codex")
    c.setSubject("One-page summary generated from RTF and provided code snippet")

    top_y = page_h - margin
    c.setFillColorRGB(0.05, 0.09, 0.15)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, top_y, content.title)
    y = top_y - 16
    y = draw_wrapped_text(
        c,
        margin,
        y,
        usable_w,
        content.subtitle,
        font_name="Helvetica",
        font_size=8.5,
        color_rgb=(0.30, 0.35, 0.40),
    )
    y -= 4
    c.setStrokeColorRGB(0.72, 0.77, 0.84)
    c.setLineWidth(0.8)
    c.line(margin, y, page_w - margin, y)
    col_top = y - 12

    left_y = col_top
    right_y = col_top

    left_y = draw_section_header(c, left_x, left_y, "What it is", left_w)
    for paragraph in content.what_it_is:
        left_y = draw_wrapped_text(c, left_x, left_y, left_w, paragraph, font_size=9.0)
        left_y -= 3
    left_y += 1

    left_y = draw_section_header(c, left_x, left_y, "Who it's for", left_w)
    left_y = draw_wrapped_text(c, left_x, left_y, left_w, content.who_its_for, font_size=9.0)
    left_y -= 4

    left_y = draw_section_header(c, left_x, left_y, "What it does", left_w)
    left_y = draw_bullet_list(c, left_x, left_y, left_w, content.what_it_does, font_size=9.0)

    right_y = draw_section_header(c, right_x, right_y, "How it works", right_w)
    right_y = draw_wrapped_text(
        c,
        right_x,
        right_y,
        right_w,
        "Based only on repo evidence (required by request).",
        font_size=8.5,
        color_rgb=(0.25, 0.30, 0.35),
    )
    right_y -= 2
    for label, value in content.how_it_works:
        c.setFont("Helvetica-Bold", 9.0)
        c.drawString(right_x, right_y, f"{label}:")
        right_y -= 11
        right_y = draw_wrapped_text(c, right_x + 8, right_y, right_w - 8, value, font_size=9.0)
        right_y -= 2

    right_y = draw_wrapped_text(
        c,
        right_x,
        right_y,
        right_w,
        content.repo_note,
        font_size=8.2,
        color_rgb=(0.35, 0.10, 0.10),
    )
    right_y -= 5

    right_y = draw_section_header(c, right_x, right_y, "How to run", right_w)
    right_y = draw_bullet_list(c, right_x, right_y, right_w, content.how_to_run, font_size=9.0)
    right_y -= 2

    right_y = draw_section_header(c, right_x, right_y, "Evidence basis", right_w)
    right_y = draw_wrapped_text(c, right_x, right_y, right_w, content.evidence_note, font_size=8.0)

    footer_y = margin - 2
    c.setStrokeColorRGB(0.85, 0.87, 0.90)
    c.setLineWidth(0.5)
    c.line(margin, footer_y + 10, page_w - margin, footer_y + 10)
    c.setFont("Helvetica", 7.8)
    c.setFillColorRGB(0.35, 0.35, 0.35)
    c.drawString(margin, footer_y, "Generated locally from provided artifacts. Missing repo-backed items are explicitly labeled.")
    c.setFillColorRGB(0, 0, 0)

    c.showPage()
    c.save()

    return RenderMetrics(left_min_y=left_y, right_min_y=right_y, bottom_margin=margin)


def render_preview_png(pdf_path: Path, tmp_dir: Path) -> Tuple[Path | None, str]:
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        return None, "pdftoppm not found; skipped PNG preview render."

    tmp_dir.mkdir(parents=True, exist_ok=True)
    prefix = tmp_dir / "tcr-ia-compliance-gateway-summary-one-page"
    run_cmd([pdftoppm, "-png", str(pdf_path), str(prefix)])
    png_path = tmp_dir / "tcr-ia-compliance-gateway-summary-one-page-1.png"
    if not png_path.exists():
        return None, "pdftoppm ran but preview PNG was not created."
    return png_path, "preview rendered"


def validate_pdf(pdf_path: Path, content: SummaryContent, metrics: RenderMetrics) -> List[str]:
    failures: List[str] = []
    if not pdf_path.exists():
        failures.append("PDF file was not created.")
        return failures

    if metrics.left_min_y < metrics.bottom_margin:
        failures.append(f"Left column overflow risk: min y {metrics.left_min_y:.1f} < margin {metrics.bottom_margin:.1f}.")
    if metrics.right_min_y < metrics.bottom_margin:
        failures.append(f"Right column overflow risk: min y {metrics.right_min_y:.1f} < margin {metrics.bottom_margin:.1f}.")

    reader = PdfReader(str(pdf_path))
    if len(reader.pages) != 1:
        failures.append(f"Expected 1 page, found {len(reader.pages)}.")

    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    for heading in ["What it is", "Who it's for", "What it does", "How it works", "How to run"]:
        if heading not in extracted:
            failures.append(f"Missing section heading in extracted text: {heading}")

    if not (5 <= len(content.what_it_does) <= 7):
        failures.append(f"What it does bullet count out of range: {len(content.what_it_does)}")

    if extracted.count(NOT_FOUND) < 6:
        failures.append("Expected multiple 'Not found in repo.' labels in extracted text.")

    if "APPROVED_FOR_USE" not in extracted or "BLOCKED" not in extracted:
        failures.append("Expected statuses APPROVED_FOR_USE and BLOCKED in summary text.")

    return failures


def main() -> int:
    if not RTF_PATH.exists():
        print(f"ERROR: RTF file not found: {RTF_PATH}", file=sys.stderr)
        return 1

    repo_note = inspect_repo(WORKSPACE)
    rtf_text = extract_rtf_text(RTF_PATH)
    content = build_content(rtf_text, repo_note)

    metrics = generate_pdf(content, OUTPUT_PDF)
    preview_path, preview_msg = render_preview_png(OUTPUT_PDF, TMP_PDF_DIR)
    failures = validate_pdf(OUTPUT_PDF, content, metrics)

    print(f"PDF: {OUTPUT_PDF}")
    print(f"Preview: {preview_path if preview_path else 'not generated'}")
    print(f"Preview status: {preview_msg}")
    print(f"Repo note: {repo_note}")

    if failures:
        print("VALIDATION: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 2

    print("VALIDATION: PASS")
    print(f"- Page count: 1")
    print(f"- Required sections: present")
    print(f"- What it does bullets: {len(content.what_it_does)}")
    print(f"- Repo-gap labels: present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
