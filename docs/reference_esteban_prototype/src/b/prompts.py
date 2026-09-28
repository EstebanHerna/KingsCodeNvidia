"""Plantillas de prompt por formato y sub_tarea. Todo en espanol y enfocado en
derecho colombiano. El LLM devuelve un JSON interno; el esquema oficial lo arma
el codigo (answer.py), no el modelo."""
from __future__ import annotations

SYSTEM = (
    "Eres un abogado colombiano experto que responde preguntas de derecho colombiano. "
    "Reglas obligatorias:\n"
    "1. Responde solo con base en la EVIDENCIA numerada [P1], [P2], ... y en conocimiento jurídico colombiano general. "
    "Nunca cites legislación de otro país.\n"
    "2. Solo puedes citar normas, artículos o sentencias que aparezcan en la EVIDENCIA. Escríbelas igual que en el encabezado del pasaje "
    "(por ejemplo 'artículo 60 del Código Sustantivo del Trabajo', 'Ley 1010 de 2006', 'Sentencia C-145 de 2018'). "
    "Si una norma no está en la evidencia, no la nombres.\n"
    "3. No uses abreviaturas de códigos (no escribas C.P., C.C., CST, CGP, E.T.): escribe el nombre completo.\n"
    "4. Sé preciso y concreto. No agregues afirmaciones que no puedas sustentar.\n"
    "5. Devuelve únicamente un objeto JSON válido, sin texto antes ni después."
)

SUBTAREA_HINTS = {
    "Definición básica": "Da la definición legal en 1-2 oraciones y luego sus elementos, citando el artículo que la contiene.",
    "Elemento esencial": "Enumera los elementos esenciales exactamente como los fija la norma y cita el artículo.",
    "Requisitos legales": "Enumera todos los requisitos en orden, de forma completa y numerada dentro de la prosa, y cita la fuente.",
    "Existencia normativa": "Empieza con 'Sí' o 'No'. Si existe, nombra la norma (tipo, número y año) y su objeto en una oración.",
    "Reproducción literal": "Copia textualmente el fragmento pertinente del pasaje, entre comillas, e indica artículo y numeral. No parafrasees.",
    "Precedente jurisprudencial": "Indica qué decidió la corte y la regla que fijó, citando la sentencia tal como aparece en la evidencia.",
    "Fundamento jurídico central (ratio decidendi)": "Formula la subregla o ratio decidendi en una oración clara y luego sus condiciones.",
    "Antecedentes fácticos": "Enumera los hechos relevantes en orden cronológico según la evidencia.",
    "Conflicto normativo": "Identifica las normas en tensión, aplica jerarquía (Constitución > ley > decreto > resolución), especialidad y temporalidad, y concluye cuál prevalece.",
    "Jerarquía legal": "Ubica la norma o decisión en la jerarquía del ordenamiento colombiano y explica sus efectos (erga omnes, inter partes).",
    "Distinción conceptual": "Contrasta los conceptos punto por punto: naturaleza, requisitos, efectos.",
    "Problema jurídico": "Identifica el problema jurídico, la regla aplicable, aplícala a los hechos y concluye.",
}

MC_SCHEMA_HINT = ('{"pasajes_usados": [1, 2], "analisis_opciones": {"A": "...", "B": "...", "C": "...", "D": "..."}, '
                  '"respuesta": "C", "justificacion": "..."}')
SEMI_SCHEMA_HINT = '{"pasajes_usados": [1, 3], "respuesta": "...", "palabras_clave": ["...", "..."]}'
OPEN_SCHEMA_HINT = ('{"pasajes_usados": [1, 2], "marco_normativo": "...", "analisis": "...", '
                    '"jurisprudencia": "...", "conclusion": "..."}')


def evidence_block(passages: list[dict], max_chars: int) -> str:
    parts = []
    for i, p in enumerate(passages, 1):
        t = (p.get("texto") or "").strip()
        if len(t) > max_chars:
            t = t[:max_chars] + " [...]"
        parts.append(f"[P{i}] {t}")
    return "\n\n".join(parts) if parts else "(sin evidencia)"


def _header(item: dict) -> str:
    h = []
    if item.get("area"):
        h.append(f"Área: {item['area']}")
    if item.get("tema"):
        h.append(f"Tema: {str(item['tema']).strip()}")
    return "\n".join(h)


def build_messages(item: dict, passages: list[dict], max_chars: int) -> list[dict]:
    f = item["formato"]
    ev = evidence_block(passages, max_chars)
    hint = SUBTAREA_HINTS.get((item.get("sub_tarea") or "").strip(), "")
    head = _header(item)
    if f == "multiple_choice":
        ops = "\n".join(f"{k}) {v}" for k, v in sorted((item.get("opciones") or {}).items()))
        user = (f"{head}\n\nEVIDENCIA:\n{ev}\n\nPREGUNTA DE SELECCIÓN MÚLTIPLE:\n{item['pregunta'].strip()}\n\n{ops}\n\n"
                "Instrucciones: analiza cada opción contra la evidencia y el derecho colombiano en 'analisis_opciones' "
                "(una oración por opción), luego elige UNA sola letra en 'respuesta'. "
                "En 'justificacion' (2-4 oraciones) explica por qué es correcta citando las normas de la evidencia. "
                f"Formato exacto:\n{MC_SCHEMA_HINT}")
    elif f == "semi_open":
        user = (f"{head}\n\nEVIDENCIA:\n{ev}\n\nPREGUNTA:\n{item['pregunta'].strip()}\n\n"
                f"{('Indicación: ' + hint) if hint else ''}\n"
                "Instrucciones: 'respuesta' de 3 a 5 oraciones y máximo 150 palabras, directa, empezando por la respuesta "
                "a lo que se pregunta y mencionando la norma o sentencia principal de la evidencia. "
                "'palabras_clave': 3 a 6 términos jurídicos. "
                f"Formato exacto:\n{SEMI_SCHEMA_HINT}")
    else:
        user = (f"{head}\n\nEVIDENCIA:\n{ev}\n\nCASO:\n{item['pregunta'].strip()}\n\n"
                "Instrucciones: 'marco_normativo': normas aplicables de la evidencia (1-3 oraciones). "
                "'analisis': 5 a 8 oraciones aplicando las normas a los hechos. "
                "'jurisprudencia': sentencias de la evidencia que apliquen; si la evidencia no trae ninguna, escribe "
                "'No se identificó jurisprudencia específica en la evidencia recuperada.' sin inventar sentencias. "
                "'conclusion': 1-2 oraciones que respondan la pregunta. "
                f"Formato exacto:\n{OPEN_SCHEMA_HINT}")
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def json_schema_for(formato: str) -> dict:
    """JSON schema para decodificacion guiada (vLLM guided_json / response_format)."""
    used = {"type": "array", "items": {"type": "integer"}, "maxItems": 10}
    if formato == "multiple_choice":
        props = {"pasajes_usados": used,
                 "analisis_opciones": {"type": "object", "properties": {k: {"type": "string"} for k in "ABCD"},
                                       "required": list("ABCD")},
                 "respuesta": {"type": "string", "enum": list("ABCD")},
                 "justificacion": {"type": "string"}}
    elif formato == "semi_open":
        props = {"pasajes_usados": used, "respuesta": {"type": "string"},
                 "palabras_clave": {"type": "array", "items": {"type": "string"}}}
    else:
        props = {"pasajes_usados": used, **{k: {"type": "string"} for k in
                 ("marco_normativo", "analisis", "jurisprudencia", "conclusion")}}
    return {"type": "object", "properties": props, "required": list(props)}
