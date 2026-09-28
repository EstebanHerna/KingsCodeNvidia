"""Convierte tuplas canonicas de citations.py de vuelta a texto que el mismo
extractor vuelve a reconocer igual (ida y vuelta verificada en tests)."""
from __future__ import annotations

CODE_NAMES = {
    "constitucion": "Constitución Política",
    "codigo_civil": "Código Civil",
    "codigo_penal": "Código Penal",
    "codigo_procedimiento_penal": "Código de Procedimiento Penal",
    "codigo_comercio": "Código de Comercio",
    "codigo_sustantivo_trabajo": "Código Sustantivo del Trabajo",
    "codigo_procesal_trabajo": "Código Procesal del Trabajo",
    "codigo_general_proceso": "Código General del Proceso",
    "cpaca": "Código de Procedimiento Administrativo y de lo Contencioso Administrativo",
    "estatuto_tributario": "Estatuto Tributario",
    "codigo_infancia": "Código de la Infancia y la Adolescencia",
    "codigo_nacional_policia": "Código Nacional de Seguridad y Convivencia Ciudadana",
    "codigo_disciplinario": "Código General Disciplinario",
    "estatuto_consumidor": "Estatuto del Consumidor",
    "decision_andina_486": "Decisión 486 de la Comisión de la Comunidad Andina",
}
KIND_NAMES = {"ley": "Ley", "decreto": "Decreto", "acto_legislativo": "Acto Legislativo",
              "resolucion": "Resolución", "circular": "Circular", "acuerdo": "Acuerdo"}


def render_body(b: tuple) -> str:
    kind, num, year = b[0], b[1], b[2]
    if kind in CODE_NAMES:
        return CODE_NAMES[kind]
    if kind == "jurisprudencia":
        return f"Sentencia {num} de {year}"
    return f"{KIND_NAMES.get(kind, kind.title())} {num} de {year}"


def render_cite(c: tuple) -> str:
    base = render_body(c)
    art = c[3] if len(c) > 3 else None
    if art and c[0] != "jurisprudencia":
        art_det = "la" if base.startswith(("Ley", "Constitución", "Decisión", "Resolución", "Circular")) else "el"
        return f"artículo {art} de {art_det} {base}"
    return base
