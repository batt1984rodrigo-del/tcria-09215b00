from __future__ import annotations

from typing import Any


REQUIRED_LIST_FIELDS = [
    "achados_objetivos",
    "enquadramento",
    "riscos_ou_lacunas",
]

REQUIRED_STRING_FIELDS = [
    "conclusao_operacional",
    "tipo_de_ato_sugerido",
    "minuta_sugerida",
]


def _clean_text(value: Any, *, default: str = "") -> str:
    if value is None:
        return default
    text = str(value).strip()
    return text if text else default


def _clean_list(items: Any) -> list[str]:
    if not items:
        return []
    iterable = items if isinstance(items, (list, tuple, set)) else [items]
    cleaned: list[str] = []
    for item in iterable:
        text = _clean_text(item)
        if text:
            cleaned.append(text)
    return cleaned


def normalize_institutional_output(payload: dict[str, Any]) -> dict[str, Any]:
    identification_raw = payload.get("identificacao_do_caso")
    identification = identification_raw if isinstance(identification_raw, dict) else {}
    normalized = {
        "identificacao_do_caso": {
            "processo": _clean_text(identification.get("processo"), default="Não informado."),
            "tipo": _clean_text(identification.get("tipo"), default="Não informado."),
            "interessado": _clean_text(identification.get("interessado"), default="Não informado."),
            "tema": _clean_text(identification.get("tema"), default="Não informado."),
            "unidade_origem": _clean_text(identification.get("unidade_origem"), default="Não informada."),
            "fase": _clean_text(identification.get("fase"), default="Não informada."),
            "unidade_competente_sugerida": _clean_text(
                identification.get("unidade_competente_sugerida"),
                default="Não informada.",
            ),
        },
    }

    for field in REQUIRED_LIST_FIELDS:
        normalized[field] = _clean_list(payload.get(field))

    for field in REQUIRED_STRING_FIELDS:
        normalized[field] = _clean_text(payload.get(field), default="Não informado.")

    return normalized


INSTITUTIONAL_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "identificacao_do_caso",
        "achados_objetivos",
        "enquadramento",
        "riscos_ou_lacunas",
        "conclusao_operacional",
        "tipo_de_ato_sugerido",
        "minuta_sugerida",
    ],
    "properties": {
        "identificacao_do_caso": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "processo",
                "tipo",
                "interessado",
                "tema",
                "unidade_origem",
                "fase",
                "unidade_competente_sugerida",
            ],
            "properties": {
                "processo": {"type": "string"},
                "tipo": {"type": "string"},
                "interessado": {"type": "string"},
                "tema": {"type": "string"},
                "unidade_origem": {"type": "string"},
                "fase": {"type": "string"},
                "unidade_competente_sugerida": {"type": "string"},
            },
        },
        "achados_objetivos": {"type": "array", "items": {"type": "string"}},
        "enquadramento": {"type": "array", "items": {"type": "string"}},
        "riscos_ou_lacunas": {"type": "array", "items": {"type": "string"}},
        "conclusao_operacional": {"type": "string"},
        "tipo_de_ato_sugerido": {"type": "string"},
        "minuta_sugerida": {"type": "string"},
    },
}


def render_institutional_markdown(output: dict[str, Any]) -> str:
    normalized = normalize_institutional_output(output)
    identification = normalized["identificacao_do_caso"]

    lines = ["# TCRIA Institutional Output", ""]
    lines.append("## IDENTIFICAÇÃO DO CASO")
    lines.append("")
    for label, key in [
        ("Processo", "processo"),
        ("Tipo", "tipo"),
        ("Interessado", "interessado"),
        ("Tema", "tema"),
        ("Unidade de origem", "unidade_origem"),
        ("Fase", "fase"),
        ("Unidade competente sugerida", "unidade_competente_sugerida"),
    ]:
        lines.append(f"- **{label}:** {identification[key]}")
    lines.append("")

    for title, field in [
        ("ACHADOS OBJETIVOS", "achados_objetivos"),
        ("ENQUADRAMENTO", "enquadramento"),
        ("RISCOS OU LACUNAS", "riscos_ou_lacunas"),
    ]:
        lines.append(f"## {title}")
        lines.append("")
        items = normalized[field] or ["Não informado."]
        for item in items:
            lines.append(f"- {item}")
        lines.append("")

    lines.append("## CONCLUSÃO OPERACIONAL")
    lines.append("")
    lines.append(normalized["conclusao_operacional"])
    lines.append("")
    lines.append(f"**Tipo de ato sugerido:** {normalized['tipo_de_ato_sugerido']}")
    lines.append("")
    lines.append("## MINUTA SUGERIDA")
    lines.append("")
    lines.append(normalized["minuta_sugerida"])
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"
