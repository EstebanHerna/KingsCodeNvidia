# CLAUDE.md — KingsCode (Hackathon 2026, derecho colombiano)

Contexto para Claude Code. Idioma de trabajo: español. Leer completo antes de tocar código.

@AGENTS.md

## 1. Qué es esto en una línea

RAG para responder 992 preguntas ciegas de derecho colombiano el sábado 3 de octubre de 2026 (09:00–15:00) con un decoder abierto de ≤ 8B, encoder abierto, temperatura 0, índice congelado. `scripts/evaluate.py` (oficial, no se modifica) califica 80 de 100 puntos; los otros 20 son interfaz, corpus/bitácora, video y reproducibilidad (sección 6.2 del enunciado).

## 2. Protocolo de trabajo para Claude Code

1. **Razonar antes de editar.** Para cualquier tarea no trivial: leer los archivos implicados, escribir el plan con criterio de aceptación medible y esperar aprobación antes de tocar código que ya está probado.
2. **Medir antes y después.** Toda tarea que toque la calidad termina con una corrida sobre `data/sample_50.jsonl` y la tabla antes/después (cerradas, citas, abstención y, si se autorizó, RAGAS). Una variable por experimento.
3. **No romper lo verificado.** Correr `python -m unittest discover -s tests -v` antes de declarar terminado. 91 tests viven en el repo (5 se saltan sin un `corpus/` local). Si un test falla porque la regla cambió a propósito, actualizar el test y explicar por qué en `docs/DECISION_LOG.md`.
4. **Cambios de arquitectura → revisión cruzada.** `kingscode/reasoning/` y `kingscode/generation/` son código real de A (Luis), muy probado (60+ tests). No reescribir su semántica de coincidencia de citas u otras decisiones ya probadas sin dejarlo escrito en `docs/DECISION_LOG.md` para que él lo revise; preferir salvaguardas aditivas (ver el fix de `Pipeline.run` del 2026-09-28) sobre reescrituras.
5. **Cerrar el turno** actualizando `docs/KINGSCODE_STATE.json` (next_action) si cambia el siguiente paso, `docs/DECISION_LOG.md` si hubo decisión, y dejando el siguiente comando exacto.
6. **Preguntar** antes de gastar créditos de OpenRouter (`--ragas`, 20 USD por equipo para toda la semana), descargar pesos grandes o tocar la capa de A (`kingscode/acquisition.py`, `corpus.py`, `retrieval.py`, `neural.py`, `CORPUS.md`, `corpus_manifest.json`).

## 3. Reglas duras (descalifican si se violan)

- Ningún modelo cerrado (OpenAI, Anthropic, Google, Cohere…) dentro del sistema: generación, reformulación, reranking, datos sintéticos. Claude Code puede escribir código; **ninguna salida del sistema puede pasar por Claude/GPT/Gemini**. No generar ejemplos, respuestas, paráfrasis de normas ni datos de entrenamiento con un modelo cerrado.
- No indexar ni meter en prompts `sample_50` ni nada con respuestas esperadas (`legal_basis`, `respuesta_esperada`, `respuesta_correcta`, `texto_respuesta_correcta`). Solo `tools/analyze_*.py` y `scripts/evaluate.py` pueden leer etiquetas, y solo para medir.
- No editar manualmente respuestas después de ejecutar. Los post-procesos automáticos (guarda de citas, salvaguarda de abstención) son código versionado y se declaran en el informe.
- Temperatura 0, `do_sample=False`, semilla fija. Índice congelado en la entrega.
- No modificar archivos oficiales (`scripts/`, `schema/`, `data/`, `entregables/`, `Ejemplo de entrega/`). Sus hashes están en `docs/OFFICIAL_SHA256.txt`.
- Nunca versionar `scripts/.env` (llave de OpenRouter, solo para el evaluador).

## 4. Cómo puntúa el evaluador (leído del código, no de la documentación)

| Componente | Pts | Mecánica real | Campos que lee |
|---|---:|---|---|
| Cerradas | 20 | aciertos / 289 en el test | `respuesta_correcta` |
| RAGAS | 30 | juez `z-ai/glm-5.3-flash` vs respuesta esperada; abstención = 0 | semi: solo `respuesta`; open: los 4 campos |
| Citas | 20 | `recall ponderado − 2 × tasa_sin_respaldo` | MC: `justificacion`; semi: `respuesta`+`referencia_legal`; open: 4 campos |
| Abstención | 10 | acierto 1, abstención 0,5, error 0 | `abstencion` |

Consecuencias que deben guiar el diseño:

- Las citas se comparan **por cuerpo normativo** (`(kind, numero, año)`, ver `scripts/citations.py::bodies`), **sin artículo**. Una cita "artículo 5 de la Ley 1010 de 2006" puntúa igual que "Ley 1010 de 2006" a secas, siempre que el cuerpo aparezca en el texto de alguno de los **10 primeros** `pasajes_recuperados`.
- Cita correcta y respaldada = 1; correcta sin respaldo = 0,5; **incorrecta pero respaldada = 0, sin penalización**; incorrecta y sin respaldo = penalización doble. Por eso nunca conviene omitir un pasaje relevante solo porque no coincide con el `legal_basis`.
- `referencia_legal` y `justificacion`/`marco_normativo` puntúan citas pero **no** los ve el juez RAGAS (que solo lee `respuesta` en semiabiertas, o los 4 campos en abiertas): ahí conviene concentrar las normas.
- Abstenerse casi nunca conviene: en cerradas solo si P(acierto) < ~7 %; en texto libre se pierde RAGAS entero. El enunciado dice explícitamente que la abstención sistemática da 5/100.
- Alias del extractor oficial que causan citas fantasma: `C.P.`/`CP` = Constitución (no Código Penal), `CC`/`C.C.` = Código Civil, `ET`/`E.T.` = Estatuto Tributario. Los prompts deben prohibir abreviaturas (ya lo hace `kingscode/generation/prompts.py`).
- La verificación en vivo (sábado 15:00–17:00) regenera 2–3 preguntas: normas citadas y pasajes deben coincidir con lo entregado. Determinismo real, no solo `temperature=0` — revisar que `torch.use_deterministic_algorithms(True)` se mantenga.

## 5. Estado real

- **2026-09-29, prevalece:** A+B integrados en `main` (ver la última entrada de `docs/DECISION_LOG.md` y `member_b_v2` en `docs/KINGSCODE_STATE.json`). B ya no hace fan-out propio en modo PLAN: usa `retrieve(..., query_views=...)` de A, cuyo locator solo resuelve Q0. Sesión GPU: `tools/lab_gpu_session.ps1`. Lo que sigue abajo es el historial del 28-sep.

- **A (corpus + retrieval):** 163 documentos, 26.558 pasajes, grafo 59k nodos/75k aristas, BM25 activo, Recall@10 a nivel artículo 0,525. Dense/reranker Qwen3-0.6B implementados, sin benchmark neuronal completo (pendiente GPU). `corpus/` está en `.gitignore`: se construye localmente con `tools/member_a.py acquire` + `reproduce` (ver `docs/MEMBER_A_RUNBOOK.md`) o se copia el snapshot conservado.
- **B (razonamiento):** Gate 1B histórico (`DummyDecoder`, siempre se abstiene) = 5/50 sin RAGAS; sigue como piso de referencia. Gate 2-Prep (`a179af7`) ya agregó `kingscode/generation/hf_decoder.py` (backend real Transformers, lazy, con locks/hashes de modelo, prompts `grounded-formats-v2`) y `config/decoder_bakeoff.json`/`config/models.lock.json` (Qwen3-8B, ALIA Legal 7B, Salamandra 7B, Llama 3.1 8B opcional). **Nada de esto se ha ejecutado en GPU real todavía** (`gate2_prep.decoder_weights_downloaded: false`).
- **Corrección del 2026-09-28 (esta sesión):** `Pipeline.run` (`kingscode/reasoning/pipeline.py`) ya no deja que una sola cita sin respaldo aborte la corrida completa de 992 preguntas; la convierte en abstención para ese ítem y sigue. Ver el detalle y lo que queda pendiente para revisión cruzada en `docs/DECISION_LOG.md` (entrada "Corrección del abort-on-citation").
- **T3/T5/T7 (misma sesión, PR #1 en `IngSeb0/KingsCodeNvidia`):** política de abstención nunca bloquea `multiple_choice`, texto libre solo bloquea con evidencia vacía/en conflicto/no vigente (`policy.py::blocking_reasons`); `multiple_choice` con opciones ahora dispara una consulta por opción y fusiona por RRF (`pipeline.py::query_variants`/`rrf_merge`); `run.sh` + `Dockerfile` dan el comando único de reproducción sobre `sample_50`. T6 (concurrencia/ensayo de 992) se dejó bloqueado a propósito: no hay cómo medirlo sin GPU/corpus reales.
- **Interfaz:** `interfaz/app.py` (Streamlit) conectado al pipeline real, con identidad visual de Software Colombia. No se ha probado con corpus real en esta máquina (no hay GPU/CUDA ni `corpus/` local aquí).
- **Hallazgo de citas aún vigente** (`tools/analyze_citation_ceiling.py`, medido sobre la corrida de A): con la evidencia BM25 actual, el 82 % de los cuerpos del `legal_basis` de la muestra ya aparece en los 8 pasajes recuperados. Detalle en `docs/B_FINDINGS_2026-09-28.md` (marcado con notas de vigencia).

## 6. Mapa del código

```
kingscode/                 capa A (no tocar sin coordinar con A/Luis)
  acquisition.py corpus.py retrieval.py neural.py evaluation.py validation.py
  gpu_environment.py model_assets.py    preparación de entorno GPU (Gate 2, la posee B)
kingscode/reasoning/       capa B — núcleo determinista, sin modelo
  contracts.py   Question pública (id, pregunta, formato, opciones)
  legal.py       reconocimiento propio de referencias (más estricto que citations.py; ver DECISION_LOG)
  query.py       normalize_query
  routing.py     route_graph OFF/AUTO/ON + adaptador booleano para A
  policy.py      assess_evidence → abstención
  decoder.py     contrato Decoder, DummyDecoder, abstention_row
  guards.py      validate_submission, citation_guard (nunca se debilita sin revisión cruzada)
  pipeline.py    Pipeline.run: retrieve → router → policy → decoder → guard → (fallback de citas, 2026-09-28)
  experiments.py run_experiment, registro por corrida
kingscode/generation/       capa B — decoder real (Gate 2-Prep, Luis)
  hf_decoder.py  HFDecoder: Transformers local, lazy, bf16/int8/int4, locks de modelo
  prompts.py     build_messages/parse_response, grounded-formats-v2, valida oraciones/palabras
  config.py      load_bakeoff/select_decoder contra config/decoder_bakeoff.json
  experiments.py run_generation (modo sample/decoder-smoke), retrieval freeze
tools/member_b.py          CLI: smoke (Gate 1B) | decoder-smoke | sample | bakeoff
tools/analyze_citation_ceiling.py   análisis de estrategias de cita (desarrollo, no entra al pipeline)
interfaz/app.py             Streamlit, identidad Software Colombia, contra el pipeline real
docs/reference_b_prototype/         prototipo del 2026-09-27 (Claude Code): prompts/guardas por formato. Referencia, no se importa.
docs/reference_esteban_prototype/   prototipo independiente de Esteban (`kingscode_b/`): mismo propósito, backend vLLM/Ollama. Referencia, no se importa.
config/reasoning.json      config de Gate 1B (fuerza dummy + BM25, ver validate_config)
config/decoder_bakeoff.json config de Gate 2 (decoders reales, bf16, prompts v2)
```

## 7. Comandos

Windows (máquina del equipo):
```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe tools/member_b.py smoke
.venv/Scripts/python.exe tools/analyze_citation_ceiling.py
.venv/Scripts/python.exe scripts/evaluate.py --submission <run>/submissions.jsonl --split sample
streamlit run interfaz/app.py   # requiere corpus/ construido; pip install -r requirements-ui.txt
```
Linux/WSL: igual con `python`. RAGAS (`--ragas`) solo con autorización explícita: hay 20 USD para toda la semana.

## 8. Siguiente paso real (no confundir con el plan T1–T7 original de Esteban, ya parcialmente superado)

1. Cross-review con Luis de la entrada "Corrección del abort-on-citation" en `docs/DECISION_LOG.md`, en particular si vale la pena bajar `citation_guard` a coincidencia por cuerpo (como el evaluador) en vez de cuerpo+artículo.
2. Probar `interfaz/app.py` end-to-end en cuanto haya `corpus/` local o en la máquina con GPU.
3. Día de GPU: seguir `docs/GPU_DAY_RUNBOOK.md` tal cual (B posee el entorno CUDA/PyTorch/model cache; A toma la máquina después con `GPU_READY`).
4. `run.sh`/Dockerfile de un solo comando y sección `## Corpus e índice` en el README siguen pendientes (rúbrica 6.2, reproducibilidad 2 pts + corpus publicado 5 pts).

## 9. Corpus v0.2 y locator (desde 2026-09-28 noche)

Plan revisado con evidencia: `docs/CORPUS_V02_PLAN.md`. Comando: `/corpus-tarea C1` (y C0–C8).
Puntos que no se discuten sin nuevos datos:
- Los 37 fallos de R6 en dev son de parser y ranking: `diversify.parse_reference` no reconoce códigos, la Constitución, abreviaturas ni listas, y R6 solo reordena el pool de BM25. Arreglar esto es anterior a añadir documentos.
- El benchmark v1 es 100 % explícito; la muestra oficial tiene solo 4/50 preguntas con artículo en el enunciado. No elegir pesos BM25/denso con v1.
- El banco no cubre derecho internacional (§4.2 del enunciado).
- v0.1 es inmutable hasta que el equipo apruebe el freeze de v0.2 en `DECISION_LOG.md`.

## 10. B después de la RTX 4090 (desde 2026-09-28 noche)

Plan vigente de B: `docs/B_PLAN_POST_GPU.md` (tareas B0–B8, comando `/b2-tarea`). Sustituye el orden de `docs/B_EXTENSION_PLAN.md` donde se contradigan.
- El locator exacto es de A; B solo llama `retrieve()`.
- Guarda: reparar antes de verificar (aceptar / reescribir a cuerpo / suprimir). No abstenerse por una cita.
- Qwen3-8B sigue en el bakeoff: el enunciado §3.1 lo sugiere expresamente; la confirmación por correo está pendiente.
- Prioridad sin GPU: B7 (checkpoint, resume, escritura atómica, 992/992).
