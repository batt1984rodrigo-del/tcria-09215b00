from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from tcria.engine import TCRIAEngine
from tcria.institutional_output import render_institutional_markdown
from tcria.openai_responses import (
    list_available_institutional_chat_profiles,
    list_audit_prompt_presets,
    run_audit_prompt,
    run_institutional_output_prompt,
)
from tcria.settings import load_env


load_env()


def render() -> None:
    st.set_page_config(page_title="TCRIA", layout="wide")
    st.title("TCRIA — Legal Evidence Governance Platform")
    st.caption("Engine + Governance Gates + Audit Bundle")

    engine = TCRIAEngine()

    input_path = st.text_input("Document folder path", value=str(Path.home() / "Downloads"))
    out_dir = st.text_input("Output folder", value="output/audit")
    output_stem = st.text_input("Output name", value="audit")
    strict = st.checkbox("Strict compliance mode", value=True)
    include_pdf = st.checkbox("Generate PDF report", value=True)
    use_official_pipeline = st.checkbox("Use official governance pipeline scripts", value=False)
    use_openai_summary = st.checkbox("Run Responses API analysis", value=False)
    use_institutional_gpt = st.checkbox("Run institutional drafting module via API", value=False)
    institutional_input = st.text_area(
        "Structured institutional data (JSON)",
        value="",
        disabled=not use_institutional_gpt,
        help=(
            "Optional, but recommended when the institutional drafting module is enabled. "
            "Paste `audit_data` here to generate the institutional output through the OpenAI Responses API."
        ),
    )
    institutional_profiles = list_available_institutional_chat_profiles()
    institutional_profile_map = {profile["label"]: profile for profile in institutional_profiles}
    institutional_profile_labels = list(institutional_profile_map)
    selected_institutional_profile_label = st.selectbox(
        "Institutional chat profile",
        institutional_profile_labels,
        index=0,
        disabled=not use_institutional_gpt,
    )
    selected_institutional_profile = institutional_profile_map[selected_institutional_profile_label]
    st.caption(selected_institutional_profile["description"])

    presets = list_audit_prompt_presets()
    preset_map = {preset["label"]: preset for preset in presets}
    preset_labels = list(preset_map)
    selected_preset_label = st.selectbox(
        "Audit prompt preset",
        preset_labels,
        index=0,
        disabled=not use_openai_summary,
    )
    selected_preset = preset_map[selected_preset_label]
    st.caption(selected_preset["description"])
    openai_model = st.text_input(
        "OpenAI model",
        value="gpt-4.1-mini",
        disabled=not (use_openai_summary or use_institutional_gpt),
    )
    openai_context = st.text_area(
        "Override prompt context",
        value="",
        disabled=not (use_openai_summary or use_institutional_gpt),
        help="Optional. Leave empty to use the preset default prompt.",
    )

    if st.button("Run TCRIA Audit", type="primary"):
        try:
            with st.spinner("Running..."):
                if use_official_pipeline:
                    result = engine.run_official_pipeline(
                        input_path=input_path,
                        strict=strict,
                        output_stem=output_stem,
                    )
                else:
                    result = engine.run_audit(
                        input_path=input_path,
                        strict=strict,
                        out_dir=out_dir,
                        output_stem=output_stem,
                        include_pdf=include_pdf,
                    )
        except Exception as exc:
            st.error(f"Audit failed: {exc}")
            return

        st.success("Audit completed.")

        institutional_result = None
        if use_institutional_gpt:
            if not institutional_input.strip():
                st.warning("Institutional drafting module enabled, but no `audit_data` JSON was provided.")
            else:
                try:
                    parsed_institutional_input = json.loads(institutional_input)
                    if not isinstance(parsed_institutional_input, dict):
                        raise ValueError("The JSON must be an object.")
                    with st.spinner("Running institutional drafting module..."):
                        institutional_result = run_institutional_output_prompt(
                            parsed_institutional_input,
                            model=openai_model,
                            user_context=openai_context or None,
                            chat_profile=selected_institutional_profile["slug"],
                        )
                except Exception as exc:
                    st.warning(f"Institutional drafting module failed: {exc}")

        tab_labels = ["Resumo executivo", "Bundle bruto"]
        if use_institutional_gpt:
            tab_labels.insert(1, "Saída institucional")
        tabs = st.tabs(tab_labels)
        tab_summary = tabs[0]
        tab_institutional = tabs[1] if use_institutional_gpt else None
        tab_bundle = tabs[2] if use_institutional_gpt else tabs[1]

        with tab_summary:
            bundle = result.get("bundle") if isinstance(result, dict) else None
            if isinstance(bundle, dict):
                col1, col2, col3 = st.columns(3)
                col1.metric("Arquivos auditados", bundle.get("total_files_scanned", 0))
                col2.metric("Registros acusatórios", bundle.get("accusation_set_count", 0))
                col3.metric("Modo", bundle.get("mode", "não informado"))
                st.write("**Classificações**")
                st.json(bundle.get("classification_counts", {}))
                st.write("**Rotas identificadas**")
                st.json(bundle.get("route_counts", {}))
            else:
                st.info("O bundle não foi retornado em formato estruturado.")

        if tab_institutional is not None:
            with tab_institutional:
                institutional_output = (
                    institutional_result.get("institutional_output") if isinstance(institutional_result, dict) else None
                )
                if isinstance(institutional_output, dict):
                    identification = institutional_output.get("identificacao_do_caso", {})
                    response_metadata = institutional_result.get("response_metadata", {})
                    st.caption(
                        f"Responses API model: {response_metadata.get('model')} | "
                        f"chat_profile: {response_metadata.get('chat_profile')} | "
                        f"response_id: {response_metadata.get('response_id')}"
                    )
                    st.subheader("Identificação do caso")
                    st.table(
                        [
                            {"Campo": "Processo", "Valor": identification.get("processo")},
                            {"Campo": "Tipo", "Valor": identification.get("tipo")},
                            {"Campo": "Interessado", "Valor": identification.get("interessado")},
                            {"Campo": "Tema", "Valor": identification.get("tema")},
                            {"Campo": "Unidade de origem", "Valor": identification.get("unidade_origem")},
                            {"Campo": "Fase", "Valor": identification.get("fase")},
                            {
                                "Campo": "Unidade competente sugerida",
                                "Valor": identification.get("unidade_competente_sugerida"),
                            },
                        ]
                    )

                    for title, key in [
                        ("Achados objetivos", "achados_objetivos"),
                        ("Enquadramento", "enquadramento"),
                        ("Riscos ou lacunas", "riscos_ou_lacunas"),
                    ]:
                        st.subheader(title)
                        for item in institutional_output.get(key, []):
                            st.markdown(f"- {item}")

                    st.subheader("Conclusão operacional")
                    st.write(institutional_output.get("conclusao_operacional"))
                    st.caption(f"Ato sugerido: {institutional_output.get('tipo_de_ato_sugerido')}")

                    st.subheader("Minuta sugerida")
                    st.code(institutional_output.get("minuta_sugerida", ""), language="markdown")
                    st.download_button(
                        "Baixar saída institucional (.md)",
                        data=render_institutional_markdown(institutional_output),
                        file_name=f"{output_stem}_institutional.md",
                        mime="text/markdown",
                    )
                    st.write("**JSON estruturado**")
                    st.json(institutional_output)
                else:
                    st.info("A saída institucional só é gerada quando o módulo extra via API é solicitado com `audit_data` válido.")

        with tab_bundle:
            st.subheader("Result")
            st.json(result)

        if not use_official_pipeline:
            artifacts = result.get("artifacts", {})
            st.subheader("Artifacts")
            for label, path_value in artifacts.items():
                path = Path(str(path_value))
                st.write(f"{label}: {path}")
                if path.exists():
                    st.download_button(
                        f"Download {path.name}",
                        data=path.read_bytes(),
                        file_name=path.name,
                        key=f"dl-{label}-{path.name}",
                    )

            bundle = result.get("bundle")
            if isinstance(bundle, dict):
                st.subheader("Bundle summary")
                st.code(json.dumps(
                    {
                        "total_files_scanned": bundle.get("total_files_scanned"),
                        "accusation_set_count": bundle.get("accusation_set_count"),
                        "classification_counts": bundle.get("classification_counts"),
                    },
                    ensure_ascii=False,
                    indent=2,
                ))

                if use_openai_summary:
                    st.subheader("Responses API Analysis")
                    try:
                        with st.spinner("Running preset analysis with OpenAI..."):
                            responses_result = run_audit_prompt(
                                bundle,
                                audit_type=selected_preset["slug"],
                                model=openai_model,
                                user_context=openai_context or None,
                            )
                    except Exception as exc:
                        st.error(f"Responses API analysis failed: {exc}")
                    else:
                        st.write(responses_result["response_text"])
                        st.caption(
                            f"audit_type={responses_result['audit_type']} | "
                            f"model={responses_result['response_metadata'].get('model')}"
                        )


if __name__ == "__main__":
    render()
