"""B1: normalizador de consultas.

No reescribe la pregunta con un LLM. Limpia ruido, conserva intactos los
terminos juridicos y extrae las referencias normativas explicitas con el mismo
extractor que usa el evaluador (citations.py), para que A pueda hacer busqueda
exacta ("lookup") del articulo mencionado."""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field

import citations

from .citerender import render_body, render_cite

TEMPORAL = re.compile(r"\b(vigen\w*|derog\w*|modific\w*|reform\w*|sustitu\w*|subrog\w*|"
                      r"reglament\w*|transici\w*|actualmente|hoy|antes de|despu[eé]s de|a partir de)\b", re.I)
REMISION = re.compile(r"\b(remite|remisi[oó]n|en concordancia|seg[uú]n lo dispuesto|conforme al?|"
                      r"de acuerdo con el art|al que se refiere)\b", re.I)
JERARQUIA = re.compile(r"\b(jerarqu\w*|conflicto normativo|prevalec\w*|excepci[oó]n de inconstitucionalidad|"
                       r"bloque de constitucionalidad|antinomia|competencia)\b", re.I)
SENTENCIA = re.compile(r"\b(sentencia|corte constitucional|corte suprema|consejo de estado|"
                       r"ratio decidendi|precedente|subregla|magistrad\w*|tutela)\b", re.I)

# Expansion controlada: sinonimos juridicos frecuentes. Se agregan, no reemplazan.
EXPANSION = {
    "cst": "Código Sustantivo del Trabajo",
    "cgp": "Código General del Proceso",
    "cpaca": "Código de Procedimiento Administrativo y de lo Contencioso Administrativo",
    "e.t.": "Estatuto Tributario",
    "dian": "Estatuto Tributario",
    "sic": "Superintendencia de Industria y Comercio Estatuto del Consumidor",
    "habeas data": "Ley 1581 de 2012 protección de datos personales",
    "datos personales": "Ley 1581 de 2012",
    "contratacion estatal": "Ley 80 de 1993",
    "accion popular": "Ley 472 de 1998",
    "accion de grupo": "Ley 472 de 1998",
    "acoso laboral": "Ley 1010 de 2006",
    "tutela": "Decreto 2591 de 1991",
    "marcas": "Decisión 486 de la Comisión de la Comunidad Andina",
    "patente": "Decisión 486 de la Comisión de la Comunidad Andina",
    "sociedad por acciones simplificada": "Ley 1258 de 2008",
    "sas": "Ley 1258 de 2008",
    "insolvencia": "Ley 1116 de 2006",
    "reorganizacion": "Ley 1116 de 2006",
    "garantias mobiliarias": "Ley 1676 de 2013",
    "competencia desleal": "Ley 256 de 1996",
    "divorcio": "Código Civil artículo 154",
    "alimentos": "Código Civil artículo 411",
    "sociedad conyugal": "Código Civil",
}


def _strip(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()


@dataclass
class NormalizedQuery:
    original: str
    clean: str
    cites: list = field(default_factory=list)       # tuplas canonicas con articulo
    bodies: list = field(default_factory=list)      # tuplas sin articulo
    cite_text: list = field(default_factory=list)   # las mismas, en texto
    expansion: list = field(default_factory=list)
    signals: dict = field(default_factory=dict)

    def retrieval_query(self) -> str:
        extra = " ".join(dict.fromkeys(self.cite_text + self.expansion))
        return f"{self.clean} {extra}".strip()


def normalize_query(question: str, tema: str | None = None) -> NormalizedQuery:
    q = re.sub(r"\s+", " ", (question or "")).strip()
    q = q.replace("“", '"').replace("”", '"').replace("’", "'")
    # errores de digitacion frecuentes en el banco que rompen el match exacto
    q = re.sub(r"(?i)\bconstitucip[oó]n\b", "Constitución", q)
    q = re.sub(r"(?i)\bart\.?\s*(\d)", r"artículo \1", q)
    q = re.sub(r"(?i)\bsentencia\s+([ctsu]{1,2})\s+(\d+)", r"Sentencia \1-\2", q)
    full = f"{q} {tema or ''}".strip()
    cites = sorted(citations.extract(full), key=str)
    bodies = sorted(citations.bodies(set(cites)), key=str)
    low = _strip(full)
    expansion = [v for k, v in EXPANSION.items() if re.search(r"(?<![\w.])" + re.escape(k) + r"(?!\w)", low)]
    signals = {
        "temporal": bool(TEMPORAL.search(full)),
        "remision": bool(REMISION.search(full)),
        "jerarquia": bool(JERARQUIA.search(full)),
        "sentencia": bool(SENTENCIA.search(full)),
        "articulo_explicito": any(c[3] for c in cites),
        "n_normas": len(bodies),
    }
    return NormalizedQuery(original=question, clean=q, cites=cites, bodies=bodies,
                           cite_text=[render_cite(c) for c in cites], expansion=expansion,
                           signals=signals)
