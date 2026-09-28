"""Interfaz grafica (entregable 8). Ejecutar desde la raiz del repo:
    streamlit run interfaz/app.py -- --config configs/qwen3_vllm.json
Ajustar los colores de :root a la identidad visual de Software Colombia."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from b.answer import answer_item  # noqa: E402
from b.config import Config  # noqa: E402
from b.contract import load_retriever  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--config", default=None)
args, _ = ap.parse_known_args()
cfg = Config.load(args.config) if args.config else Config()

st.set_page_config(page_title="KingsCode · Derecho colombiano", layout="wide")
st.markdown("""<style>
:root { --primario:#0B3D91; --acento:#F2A900; --fondo:#F7F8FA; }
.stApp { background: var(--fondo); }
h1, h2, h3 { color: var(--primario); }
.stButton>button { background: var(--primario); color: white; border: 0; }
.cita { border-left: 4px solid var(--acento); padding: .4rem .8rem; background: white; margin-bottom: .5rem; }
</style>""", unsafe_allow_html=True)

st.title("KingsCode · Consulta de derecho colombiano")
st.caption(f"Decoder: {cfg.model if cfg.backend != 'mock' else 'mock'} · temperatura {cfg.temperature} · índice congelado")

retrieve = load_retriever(cfg.retriever)
formato = st.radio("Formato", ["semi_open", "open_ended", "multiple_choice"], horizontal=True,
                   format_func={"semi_open": "Respuesta breve", "open_ended": "Caso",
                                "multiple_choice": "Selección múltiple"}.get)
pregunta = st.text_area("Pregunta", height=120)
opciones = {}
if formato == "multiple_choice":
    cols = st.columns(2)
    for i, L in enumerate("ABCD"):
        opciones[L] = cols[i % 2].text_input(f"Opción {L}")

if st.button("Responder") and pregunta.strip():
    item = {"id": 0, "formato": formato, "pregunta": pregunta, "opciones": opciones or None}
    with st.spinner("Recuperando evidencia y generando..."):
        row, log = answer_item(item, cfg, retrieve)
    izq, der = st.columns([3, 2])
    with izq:
        if row["abstencion"]:
            st.warning("El sistema se abstiene: evidencia insuficiente en el corpus.")
        elif formato == "multiple_choice":
            st.subheader(f"Respuesta: {row['respuesta_correcta']}")
            st.write(row["justificacion"])
            for k, v in row["descarte_opciones"].items():
                st.markdown(f"**{k}** — {v}")
        elif formato == "semi_open":
            st.write(row["respuesta"])
            st.markdown(f"**Referencia legal:** {row['referencia_legal']}")
        else:
            for k, t in [("marco_normativo", "Marco normativo"), ("analisis", "Análisis"),
                         ("jurisprudencia", "Jurisprudencia"), ("conclusion", "Conclusión")]:
                st.markdown(f"**{t}**")
                st.write(row[k])
        st.caption(f"{row['latencia_ms']} ms · grafo: {log.get('graph')} · guarda: {log.get('guard')}")
    with der:
        st.subheader("Evidencia")
        for i, p in enumerate(row["pasajes_recuperados"], 1):
            st.markdown(f"<div class='cita'><b>[P{i}] {p['doc_id']}</b> · score {p.get('score', '')}<br>"
                        f"{p['texto'][:600]}</div>", unsafe_allow_html=True)
    with st.expander("JSON de la entrega"):
        st.json(row)
