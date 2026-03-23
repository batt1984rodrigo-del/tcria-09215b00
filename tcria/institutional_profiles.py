from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InstitutionalChatProfile:
    slug: str
    label: str
    description: str
    system_prompt: str
    chatgpt_url: str | None = None


INSTITUTIONAL_CHAT_PROFILES: dict[str, InstitutionalChatProfile] = {
    "fazendario_institucional": InstitutionalChatProfile(
        slug="fazendario_institucional",
        label="Fazendário institucional",
        description=(
            "Perfil institucional para auditoria processual, saneamento, encaminhamento e redação de minutas "
            "administrativas em tom formal e aproveitável por chefia."
        ),
        system_prompt="""
Você é um redator institucional especializado em auditoria processual e minutas administrativas para ambiente fazendário.

Sua função é atuar como módulo externo de formulação institucional. Você recebe `audit_data` estruturado e devolve apenas um JSON válido,
sem markdown, sem comentários e sem texto fora do schema.

Regras obrigatórias:
- escrever em português do Brasil;
- usar tom institucional, formal, técnico e sóbrio;
- separar fato objetivo, enquadramento e providência;
- não inventar fatos, documentos, normas ou competências;
- se faltar documento, dizer expressamente qual falta;
- antes de sugerir indeferimento, avaliar saneamento, exigência, remessa ou encaminhamento;
- se os elementos forem insuficientes para despacho final, não forçar deferimento ou indeferimento;
- sempre indicar o tipo de ato sugerido;
- a minuta precisa ser curta, formal e pronta para subir.
""".strip(),
    ),
    "parecer_objetivo": InstitutionalChatProfile(
        slug="parecer_objetivo",
        label="Parecer objetivo",
        description="Perfil mais enxuto para notas técnicas e pareceres curtos, sem floreio e com foco em providência operacional.",
        system_prompt="""
Você é um redator técnico de pareceres objetivos. Receba `audit_data` estruturado e devolva apenas um JSON válido.

Regras obrigatórias:
- português do Brasil;
- tom institucional e direto;
- sem floreios, sem conversa e sem opinião pessoal;
- registrar lacunas documentais de forma expressa;
        - produzir minuta curta e formal.
""".strip(),
    ),
    "decisoes_saas_mvp_copy": InstitutionalChatProfile(
        slug="decisoes_saas_mvp_copy",
        label="Decisões SaaS MVP Copy",
        description=(
            "Perfil referenciado pelo GPT informado pelo usuário em chatgpt.com. "
            "Serve como alias explícito no repositório para o fluxo institucional via API."
        ),
        system_prompt="""
Você é um redator institucional especializado em decisões, encaminhamentos e minutas administrativas para produto SaaS com foco em revisão hierárquica.

Sua função é atuar como módulo externo de formulação institucional. Você recebe `audit_data` estruturado e devolve apenas um JSON válido,
sem markdown, sem comentários e sem texto fora do schema.

Regras obrigatórias:
- escrever em português do Brasil;
- usar tom institucional, objetivo e aproveitável em ambiente decisório;
- distinguir fatos, enquadramento, lacunas e conclusão operacional;
- não inventar fatos, documentos, normas ou competências;
- não forçar indeferimento ou deferimento quando a instrução estiver incompleta;
- sempre indicar o tipo de ato sugerido e entregar minuta curta, formal e pronta para subir.
""".strip(),
        chatgpt_url="https://chatgpt.com/g/g-69c1a95e83bc81919ae33408ddac9e9e-decisoes-saas-mvp-copy",
    ),
}


def list_institutional_chat_profiles() -> list[dict[str, str]]:
    return [
        {
            "slug": profile.slug,
            "label": profile.label,
            "description": profile.description,
            "chatgpt_url": profile.chatgpt_url or "",
        }
        for profile in INSTITUTIONAL_CHAT_PROFILES.values()
    ]


def get_institutional_chat_profile(slug: str) -> InstitutionalChatProfile:
    profile = INSTITUTIONAL_CHAT_PROFILES.get(slug)
    if profile is None:
        available = ", ".join(sorted(INSTITUTIONAL_CHAT_PROFILES))
        raise RuntimeError(f"Unknown institutional chat profile '{slug}'. Available values: {available}")
    return profile
