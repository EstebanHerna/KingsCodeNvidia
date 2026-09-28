import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import b  # noqa: E402,F401
import citations  # noqa: E402
from b.citerender import render_body, render_cite  # noqa: E402
from b.guard import citation_guard, clean_text, supported_bodies  # noqa: E402
from b.query import normalize_query  # noqa: E402

CASOS = [("ley", "1010", "2006", None), ("ley", "472", "1998", "3"), ("codigo_civil", None, None, "1502"),
         ("constitucion", None, None, "88"), ("codigo_sustantivo_trabajo", None, None, "60"),
         ("jurisprudencia", "C-145", "2018", None), ("decreto", "1072", "2015", None),
         ("estatuto_consumidor", None, None, "23"), ("codigo_general_proceso", None, None, None),
         ("decision_andina_486", None, None, None), ("cpaca", None, None, "137")]


def test_ida_y_vuelta():
    for c in CASOS:
        txt = render_cite(c)
        assert c[:3] in citations.bodies(citations.extract(txt)), (c, txt, citations.extract(txt))


def test_guarda_elimina_sin_respaldo():
    pas = [{"doc_id": "x", "texto": "Ley 1010 de 2006. ARTICULO 1. Objeto."}]
    supp = supported_bodies(pas)
    t, n = clean_text("La Ley 1010 de 2006 regula el acoso. Tambien la Ley 50 de 1990 aplica.", supp)
    assert n == 1 and "50 de 1990" not in t and "1010" in t


def test_guarda_fila():
    pas = [{"doc_id": "x", "texto": "Código Civil. ARTICULO 1502. Requisitos."}]
    row = {"formato": "semi_open", "respuesta": "Según el artículo 1502 del Código Civil hay cuatro requisitos. "
           "La Sentencia C-100 de 2020 lo confirma.", "referencia_legal": "Código Civil"}
    st = citation_guard(row, pas)
    assert st["sin_respaldo_despues"] == 0 and "C-100" not in row["respuesta"]


def test_alias_peligrosos():
    # 'C.P.' se interpreta como Constitucion, no como Codigo Penal
    assert ("constitucion", None, None) in citations.bodies(citations.extract("el art. 239 del C.P."))


def test_normalizer():
    nq = normalize_query("Cité un fragmento de el artículo 60 del código sustantivo del trabajo")
    assert ("codigo_sustantivo_trabajo", None, None) in nq.bodies
    nq = normalize_query("¿Qué definió la Corte en la Sentencia C 145 de 2018?")
    assert ("jurisprudencia", "C-145", "2018") in nq.bodies
    assert normalize_query("derecho constitucional").clean == "derecho constitucional"
