from __future__ import annotations

from pathlib import Path

import pytest

from tcria.engine import TCRIAEngine
from tcria.institutional_output import normalize_institutional_output, render_institutional_markdown
from tcria.ingestion.file_loader import load_documents
from tcria.openai_responses import list_available_institutional_chat_profiles


def test_engine_run_audit_smoke(tmp_path: Path) -> None:
    input_dir = tmp_path / "docs"
    input_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / "note.txt").write_text(
        "\n".join(
            [
                "[TCR-IA DECISION RECORD]",
                "responsibleHuman: Test Owner",
                "declaredPurpose: Governed evidence organization",
                "approved: YES",
                "[/TCR-IA DECISION RECORD]",
                "",
                "Fraude em transacao PIX no valor de R$ 1.000,00 em 05/03/2026.",
                "Anexo com comprovantes e extratos.",
            ]
        ),
        encoding="utf-8",
    )

    out_dir = tmp_path / "out"
    engine = TCRIAEngine(repo_root=tmp_path)
    result = engine.run_audit(
        input_path=str(input_dir),
        strict=True,
        out_dir=str(out_dir),
        output_stem="smoke",
        include_pdf=False,
    )

    bundle = result["bundle"]
    artifacts = result["artifacts"]
    assert bundle["total_files_scanned"] == 1
    assert bundle["accusation_set_count"] >= 0
    assert Path(artifacts["json"]).exists()
    assert Path(artifacts["markdown"]).exists()


def test_load_documents_respects_max_files(tmp_path: Path) -> None:
    input_dir = tmp_path / "docs"
    input_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / "a.txt").write_text("ok", encoding="utf-8")
    (input_dir / "b.txt").write_text("ok", encoding="utf-8")

    with pytest.raises(ValueError, match="max_files"):
        load_documents(str(input_dir), max_files=1)


def test_load_documents_respects_max_total_bytes(tmp_path: Path) -> None:
    input_dir = tmp_path / "docs"
    input_dir.mkdir(parents=True, exist_ok=True)
    (input_dir / "a.txt").write_text("0123456789", encoding="utf-8")

    with pytest.raises(ValueError, match="max_total_bytes"):
        load_documents(str(input_dir), max_total_bytes=5)


def test_normalize_institutional_output_fills_required_fields() -> None:
    output = normalize_institutional_output(
        {
            "identificacao_do_caso": {
                "processo": "SEI-000000/000000/2026",
                "tipo": "principal",
                "interessado": "Empresa XPTO",
                "tema": "pedido de inscrição estadual",
            },
            "achados_objetivos": ["Consta petição inicial."],
            "enquadramento": ["Aplica-se o rito de saneamento prévio da instrução."],
            "conclusao_operacional": "Recomenda-se remessa à unidade competente.",
            "tipo_de_ato_sugerido": "remessa",
            "minuta_sugerida": "Trata-se de pedido de inscrição estadual. Encaminhem-se os autos à Cefage.",
        }
    )

    assert output["identificacao_do_caso"]["processo"] == "SEI-000000/000000/2026"
    assert output["identificacao_do_caso"]["unidade_origem"] == "Não informada."
    assert output["riscos_ou_lacunas"] == []


def test_render_institutional_markdown_uses_normalized_fields() -> None:
    markdown = render_institutional_markdown(
        {
            "identificacao_do_caso": {
                "processo": "SEI-123",
                "tipo": "intercorrente",
                "interessado": "EMPRESA X",
                "tema": "inscrição estadual",
            },
            "achados_objetivos": ["Consta petição inicial."],
            "enquadramento": ["A matéria demanda análise especializada."],
            "riscos_ou_lacunas": ["Ausência de comprovante idôneo de recolhimento."],
            "conclusao_operacional": "Recomenda-se encaminhamento.",
            "tipo_de_ato_sugerido": "encaminhamento",
            "minuta_sugerida": "Trata-se de inscrição estadual. Encaminhem-se os autos.",
        }
    )

    assert "## IDENTIFICAÇÃO DO CASO" in markdown
    assert "SEI-123" in markdown
    assert "Encaminhem-se os autos." in markdown


def test_list_available_institutional_chat_profiles_returns_profiles() -> None:
    profiles = list_available_institutional_chat_profiles()

    assert profiles
    assert any(profile["slug"] == "fazendario_institucional" for profile in profiles)
    assert any(
        profile["slug"] == "decisoes_saas_mvp_copy" and profile["chatgpt_url"].startswith("https://chatgpt.com/g/")
        for profile in profiles
    )
