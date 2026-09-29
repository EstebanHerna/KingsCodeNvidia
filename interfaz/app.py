"""Interfaz gráfica (entregable 8, sección 6.2 del enunciado).

Consulta de extremo a extremo sobre el pipeline real de KingsCode: A.retrieve()
-> B.Pipeline (router -> policy -> decoder -> citation_guard). No reimplementa
nada: usa exactamente kingscode.reasoning y kingscode.Retriever, el mismo
código que corre el sábado.

Ejecutar desde la raíz del repositorio, con el corpus ya construido:
    streamlit run interfaz/app.py

Sin GPU/decoder real disponible, usa DummyDecoder (siempre se abstiene) y lo
declara explícitamente en pantalla: la interfaz nunca simula una respuesta que
el sistema no produjo.
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from kingscode.reasoning.contracts import FORMATS, Question  # noqa: E402
from kingscode.reasoning.decoder import DummyDecoder  # noqa: E402
from kingscode.reasoning.pipeline import Pipeline  # noqa: E402
from kingscode.reasoning.routing import RetrieverGraphRouter  # noqa: E402
from kingscode.reasoning.presentation import debug_trace, view_model  # noqa: E402

st.set_page_config(page_title="KingsCode · Derecho colombiano", page_icon="⚖️", layout="wide")

# Identidad visual de Software Colombia: turquesa del logo, negro y azules de
# la portada del enunciado (sección 6.2: 3 de los 10 puntos de interfaz).
st.markdown("""<style>
:root {
    --sc-turquesa: #10A9A6;
    --sc-turquesa-oscuro: #0B7E7C;
    --sc-negro: #0B0B0B;
    --sc-azul: #1E4E8C;
    --sc-azul-claro: #6FB6E8;
    --sc-fondo: #F4FAFA;
}
.stApp { background: var(--sc-fondo); }
h1, h2, h3 { color: var(--sc-negro); }
h1 { border-bottom: 4px solid var(--sc-turquesa); padding-bottom: .3rem; }
.stButton>button {
    background: var(--sc-turquesa); color: white; border: 0; font-weight: 600;
}
.stButton>button:hover { background: var(--sc-turquesa-oscuro); color: white; }
div[data-testid="stRadio"] label { color: var(--sc-negro); }
.kc-banner {
    background: var(--sc-negro); color: white; padding: .5rem 1rem; border-radius: 6px;
    border-left: 6px solid var(--sc-turquesa); margin-bottom: 1rem; font-size: .9rem;
}
.kc-pasaje {
    border-left: 4px solid var(--sc-azul); background: white; padding: .5rem .9rem;
    margin-bottom: .6rem; border-radius: 0 6px 6px 0; font-size: .88rem;
}
.kc-pasaje b { color: var(--sc-azul); }
.kc-norma {
    display: inline-block; background: var(--sc-turquesa); color: white; border-radius: 999px;
    padding: .15rem .7rem; margin: .15rem .3rem .15rem 0; font-size: .82rem; font-weight: 600;
}
.kc-norma-sin-respaldo {
    background: white; color: var(--sc-negro); border: 1.5px dashed #C0392B;
}
</style>""", unsafe_allow_html=True)

st.title("KingsCode · Consulta de derecho colombiano")
st.caption("Hackathon 2026 · AI Week · Universidad de los Andes · patrocina Software Colombia")


@st.cache_resource(show_spinner="Cargando índice del corpus (A)...")
def load_retriever(corpus_dir: str | None):
    from kingscode import Retriever
    adapter = RetrieverGraphRouter()
    retriever = Retriever(corpus_dir or None, graph_router=adapter)
    return retriever, adapter


@st.cache_resource(show_spinner="Cargando decoder...")
def load_decoder(alias: str, precision: str):
    if alias == "dummy_abstain":
        return DummyDecoder(), "DummyDecoder: se abstiene siempre (Gate 1B). No hay razonamiento legal real."
    from kingscode.generation.hf_decoder import HFDecoder
    decoder = HFDecoder(alias, precision=precision)
    decoder.load()
    return decoder, f"HFDecoder real: {alias} ({precision}, temperatura 0)."


with st.sidebar:
    st.header("Configuración")
    corpus_dir = st.text_input("Directorio del corpus", value=str(ROOT / "corpus"))
    try:
        import torch
        cuda_ok = torch.cuda.is_available()
    except Exception:
        cuda_ok = False
    decoder_options = ["dummy_abstain"]
    if cuda_ok:
        try:
            from kingscode.generation.config import load_bakeoff
            decoder_options += sorted(a for a, c in load_bakeoff()["candidates"].items() if c["enabled"])
        except Exception as exc:
            st.warning(f"No se pudo leer config/decoder_bakeoff.json: {exc}")
    else:
        st.info("Sin CUDA disponible en esta máquina: solo DummyDecoder (abstención).")
    decoder_alias = st.selectbox("Decoder", decoder_options)
    precision = st.selectbox("Precisión", ["bf16", "int8", "int4"], disabled=decoder_alias == "dummy_abstain")
    k = st.slider("Pasajes recuperados (k)", 1, 10, 8)
    graph_policy = st.selectbox("Política de grafo", ["router", "off", "auto", "on"], index=0)
    debug_mode = st.checkbox("Modo depuración (traza técnica)", value=False)

try:
    retriever, adapter = load_retriever(corpus_dir)
    corpus_error = None
except Exception as exc:
    retriever = adapter = None
    corpus_error = exc

if corpus_error is not None:
    st.markdown(f'<div class="kc-banner">No se pudo cargar el corpus en <code>{corpus_dir}</code>: '
                f'{corpus_error}. Construya el índice de A (tools/member_a.py) o corrija la ruta.</div>',
                unsafe_allow_html=True)
    st.stop()

try:
    decoder, decoder_note = load_decoder(decoder_alias, precision)
except Exception as exc:
    st.markdown(f'<div class="kc-banner">No se pudo cargar el decoder "{decoder_alias}": {exc}. '
                f'Usando DummyDecoder.</div>', unsafe_allow_html=True)
    decoder, decoder_note = DummyDecoder(), "DummyDecoder de respaldo (el decoder solicitado falló al cargar)."

st.markdown(f'<div class="kc-banner">{decoder_note} · índice congelado: '
            f'<code>{Path(corpus_dir).name}</code></div>', unsafe_allow_html=True)

formato = st.radio("Formato de la pregunta", list(FORMATS), horizontal=True,
                    format_func={"multiple_choice": "Selección múltiple", "semi_open": "Respuesta breve",
                                 "open_ended": "Caso abierto"}.get)
pregunta = st.text_area("Pregunta", height=110, placeholder="¿Cuál es el término para contestar la demanda en el proceso verbal sumario?")
opciones = {}
if formato == "multiple_choice":
    cols = st.columns(2)
    for i, letra in enumerate("ABCD"):
        opciones[letra] = cols[i % 2].text_input(f"Opción {letra}")
    opciones = {k: v for k, v in opciones.items() if v.strip()}

if st.button("Responder") and pregunta.strip():
    question = Question(0, pregunta.strip(), formato, opciones)
    pipeline = Pipeline(retriever.retrieve, adapter=adapter, decoder=decoder, k=k, graph_policy=graph_policy)
    with st.spinner("Recuperando evidencia y generando..."):
        row, trace = pipeline.run(question)
    view = view_model(row, trace)

    izq, der = st.columns([3, 2])
    with izq:
        if view["abstained"]:
            st.warning(f"El sistema se abstiene. Motivo: {view['abstention_reason'] or 'sin especificar'} "
                       f"(origen: {view['abstention_source'] or 'n/d'}).")
        elif formato == "multiple_choice":
            st.subheader(f"Respuesta: {row['respuesta_correcta']}")
            st.write(row["justificacion"])
            for letra, texto in row["descarte_opciones"].items():
                st.markdown(f"**{letra}** — {texto}")
        elif formato == "semi_open":
            st.write(row["respuesta"])
            st.markdown(f"**Referencia legal:** {row['referencia_legal']}")
        else:
            for campo, titulo in [("marco_normativo", "Marco normativo"), ("analisis", "Análisis"),
                                   ("jurisprudencia", "Jurisprudencia"), ("conclusion", "Conclusión")]:
                st.markdown(f"**{titulo}**")
                st.write(row[campo])

        st.markdown("**Normas citadas**")
        if not view["cited_norms"]:
            st.caption("La respuesta no cita ninguna norma.")
        for norm in view["cited_norms"]:
            css = "kc-norma" if norm["supported"] else "kc-norma kc-norma-sin-respaldo"
            label = html.escape(" ".join(str(x) for x in norm["body"] if x))
            st.markdown(f'<span class="{css}">{label}{"" if norm["supported"] else " · sin respaldo en evidencia"}</span>',
                        unsafe_allow_html=True)

    def card(c):
        badge = " · <b>citado</b>" if c["cited"] else ""
        badge += " · usado por el decoder" if c["declared_used"] else ""
        art = f" · art. {html.escape(str(c['article']))}" if c.get("article") else ""
        text = c["texto"]
        st.markdown(f'<div class="kc-pasaje"><b>[P{c["rank"]}] {html.escape(c["norm_name"] or "")}</b>{art}{badge}'
                    f' · <a href="{html.escape(c["source_url"] or "", quote=True)}" target="_blank">fuente</a><br>'
                    f'{html.escape(text[:600])}{"…" if len(text) > 600 else ""}</div>', unsafe_allow_html=True)

    with der:
        st.subheader(f"Pasajes citados ({len(view['cited_passages'])})")
        for c in view["cited_passages"]:
            card(c)
        st.subheader(f"Otros pasajes recuperados ({len(view['other_passages'])})")
        for c in view["other_passages"]:
            card(c)
        st.caption(f"Estos {len(row['pasajes_recuperados'])} pasajes son exactamente los de pasajes_recuperados de la entrega.")

    with st.expander("JSON de la entrega (schema oficial)"):
        st.json(view["submission"])
    if debug_mode:
        with st.expander("Traza técnica (solo operador)"):
            st.json(debug_trace(trace))
elif pregunta.strip() == "":
    st.caption("Escriba una pregunta y presione Responder.")
