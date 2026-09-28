# Prototipo independiente de Esteban (referencia, no se importa)

Implementación completa y autocontenida de la capa B, escrita el 27-sep-2026 fuera de este repositorio (paquete propio `b.*`, backend OpenAI-compatible para vLLM/Ollama/llama.cpp, interfaz Streamlit). Probada con backend mock: 0 errores de validación, 0 citas sin respaldo, 16,33/50 de partida (ver `GUIA_B.md`).

**No se ejecuta desde este árbol.** Sus imports (`from . import llm`, `from b.answer import answer_item`, etc.) apuntan a su paquete original `src/b/`, no a `kingscode.reasoning`. El pipeline competitivo real es `kingscode/reasoning/` + `kingscode/generation/` (implementado por Luis, ver `CLAUDE.md`). Esta carpeta se conserva para portar ideas puntuales, principalmente:

| Archivo | Qué portar |
|---|---|
| `src/b/guard.py`, `citerender.py` | Enfoque de "suprimir en vez de abortar" (ya aplicado de forma más acotada, ver `docs/DECISION_LOG.md` T1) y render de citas canónicas a texto reconocible por `scripts/citations.py`. |
| `src/b/query.py`, `router.py` | Ideas de fusión RRF entre pregunta y opciones para cerradas (T5 de `docs/B_EXTENSION_PLAN.md`). |
| `src/b/prompts.py`, `llm.py` | Comparar contra `kingscode/generation/prompts.py`/`hf_decoder.py`, que ya cubren ese rol en el pipeline real con más guardas (locks de modelo, determinismo verificado, parser tolerante). |
| `interfaz/app.py` | Boceto original de la interfaz Streamlit. La interfaz real y en uso es `interfaz/app.py` en la raíz del repo, conectada al pipeline real con identidad de Software Colombia. |

No se copió la carpeta `oficial/` del prototipo (copia local de `scripts/`, `schema/`, `data/`): esos archivos ya existen canónicamente en la raíz del repositorio y mantener una segunda copia solo arriesga que alguien edite la copia equivocada.
