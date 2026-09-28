# Plan de extensión de B para Claude Code

> **Nota de vigencia (28-sep-2026, tarde):** escrito originalmente contra el commit `254fa3a` (Gate 1B, `DummyDecoder`, sin `kingscode/generation/`). `a179af7` (Luis, Gate 2-Prep) ya implementó la mayor parte de lo que aquí se llamaba T4 (decoder real). Esta versión marca qué sigue vigente, qué ya se hizo y qué cambió de alcance. Base de comparación: corrida dummy = 5,00/50 sin RAGAS.

Cada tarea es una sesión de Claude Code: primero leer y proponer, luego implementar, luego medir. Orden pensado para que cada paso sume puntos medibles.

---

## T1 — Guarda que no aborte la corrida completa — ✅ hecho (2026-09-28)

**Alcance real aplicado (más acotado que el original):** no se reescribió `citation_guard`. Se modificó únicamente `Pipeline.run` (`kingscode/reasoning/pipeline.py`) para capturar `CitationGuardError` y sustituir esa fila por una abstención construida con `abstention_row` sobre la misma evidencia, sin abortar el resto del lote. `citation_guard`, `_answer` y la función pública `answer()` siguen lanzando la excepción exactamente igual que antes para cualquier llamador directo — así se conservan las ~16 pruebas de integridad de evidencia de `GuardSchemaTests` y la prueba de manipulación de evidencia (`test_decoder_cannot_mutate_evidence_to_create_support`) sin tocarlas.

**Por qué el alcance es más chico que el propuesto originalmente:** el plan original pedía que la guarda misma "suprima la oración con la cita" en vez de abortar. Eso exige reescribir la lógica de coincidencia cuerpo/artículo de `citation_guard`, que Luis ya probó extensamente. Se prefirió la salvaguarda aditiva (nunca abortar el lote) y se dejó la reescritura de la guarda como una tarea separada (T1b) que requiere su revisión, no la de Claude Code solo.
**Verificado:** `python -m unittest discover -s tests -v` → 86 tests, 5 se saltan (requieren `corpus/`). Nuevo test: `test_unsupported_citation_falls_back_to_abstention_instead_of_aborting_batch`.
**Detalle completo:** `docs/DECISION_LOG.md`, entrada "Corrección del abort-on-citation".

## T1b — Bajar el criterio de coincidencia de `citation_guard` a nivel de cuerpo — pendiente, requiere revisión de Luis

**Por qué:** `citation_guard` (`kingscode/reasoning/guards.py`) exige, cuando la cita trae artículo, que ese artículo aparezca también de forma literal en el texto del pasaje. El evaluador oficial (`scripts/citations.py::bodies`) descarta el artículo por completo al puntuar. Resultado: rechazamos (ahora: convertimos en abstención) citas que el evaluador sí pagaría — ver el ejemplo "artículo 5 de la Ley 1010 de 2006" con pasaje del artículo 1, en `docs/B_FINDINGS_2026-09-28.md`.
**Archivos:** `kingscode/reasoning/guards.py` (función interna de `citation_guard`, líneas del filtro extra sobre `supporting_passages`), `tests/test_reasoning.py::GuardSchemaTests`.
**Aceptación propuesta:** bajar el filtro adicional de `citation_guard` a solo cuerpo (`ref.body`), eliminando la exigencia de coincidencia literal de artículo en el texto del pasaje; medir el techo de citas con `tools/analyze_citation_ceiling.py` antes/después; todos los tests de `GuardSchemaTests` deben seguir pasando o actualizarse con justificación explícita en `DECISION_LOG.md`.
**Por qué no se aplicó ya:** es un cambio a semántica de scoring que Luis diseñó y probó a propósito (ver DECISION_LOG 2026-09-27, "Citation guard más conservador que la puntuación documental del evaluador... No usa alias por número ignorando año"). Se documenta para decidirlo en conjunto antes del día de GPU.

## T2 — Referencias construidas por código como fallback determinista — reducido de alcance

**Estado real:** no hace falta un `citations_builder.py` nuevo separado del decoder: `kingscode/generation/prompts.py` ya instruye al modelo a citar la evidencia directamente en los campos del formato, y `HFDecoder.generate` devuelve la fila ya validada. Lo que sigue teniendo valor de `tools/analyze_citation_ceiling.py` es medir el TECHO alcanzable sin modelo (ver B_FINDINGS §2) para decidir si conviene un post-proceso que complete `referencia_legal`/`marco_normativo` cuando el modelo no citó nada (fila no abstenida pero sin citas → hoy dispara `non_abstaining_answer_without_verifiable_citation` en `citation_guard`, que con el fix de T1 se convierte en abstención). Si se decide implementarlo, debe vivir en `kingscode/generation/` junto al decoder, no como módulo aparte, para no duplicar lógica de citas.
**Prioridad:** baja mientras el decoder real no se haya probado en GPU — medir primero si el modelo ya cita razonablemente bien antes de construir un fallback.

## T3 — Política de abstención mínima — pendiente, sin cambios desde el 27-sep

**Aceptación (sin cambios respecto al plan original):**
- `multiple_choice`: nunca se abstiene.
- Texto libre: abstención solo con retrieval vacío o conflicto fuerte. El resto de razones actuales (`policy.py:62–72`) pasan a `warnings` en la traza.
- Medición: abstenciones por razón antes/después, con la fórmula de `score_abstention` de `scripts/evaluate.py` como justificación.
**Archivos:** `kingscode/reasoning/policy.py`, `pipeline.py`, `tests/test_reasoning.py::RoutingPolicyTests`.

## T4 — Decoder real — ✅ hecho por A/Luis en Gate 2-Prep (`a179af7`), sin ejecutar en GPU todavía

`kingscode/generation/hf_decoder.py` (`HFDecoder`) implementa el protocolo `Decoder` existente: Transformers local, lazy, bf16 con fallback explícito a int8/int4, locks de modelo (`config/models.lock.json`), prompts `grounded-formats-v2` (`kingscode/generation/prompts.py`) con parser tolerante y validación de oraciones/palabras por formato. `config/decoder_bakeoff.json` fija Qwen3-8B, ALIA Legal 7B, Salamandra 7B y Llama 3.1 8B (opcional). **Nada de esto se ejecutó contra pesos reales todavía** (`gate2_prep.decoder_weights_downloaded: false` en `docs/KINGSCODE_STATE.json`). Pendiente: correr `tools/member_b.py decoder-smoke --model qwen3-8b --dry-run` primero, luego con GPU real.

## T5 — Recuperación con opciones en cerradas — pendiente, sin cambios

**Aceptación:** para `multiple_choice`, consultas adicionales `pregunta + opción` por cada opción vía la API pública de A, fusión RRF en B, 10 pasajes finales. Medir recall a nivel cuerpo y exactitud en cerradas con y sin.

## T6 — Throughput y robustez del sábado — parcialmente cubierto

`kingscode/generation/experiments.py` ya separa el freeze de retrieval del bakeoff de decoders (evita mantener retrieval y decoder juntos en VRAM) y corre cada decoder en un proceso nuevo (`tools/member_b.py bakeoff`). Falta: ensayo real de 992 preguntas cronometrado en la máquina objetivo (< 90 min), y modo de verificación con concurrencia 1 para el sábado 15:00–17:00.

## T7 — Entregables — parcialmente cubierto en esta sesión

- **Interfaz:** ✅ `interfaz/app.py` (Streamlit), identidad de Software Colombia (turquesa/negro/azul), conectado al pipeline real (`kingscode.reasoning.Pipeline` + `kingscode.Retriever`), muestra pasajes y normas citadas por separado. Pendiente: probarlo con `corpus/` real (no hay corpus local en esta máquina) y con un decoder real.
- **Pendiente:** `run.sh`/Dockerfile de un solo comando (rúbrica: reproducibilidad, 2 pts) y sección `## Corpus e índice` en el README con el enlace de descarga (rúbrica: bitácora y corpus publicado, 5 pts).

---

## Qué no hacer

- No fine‑tuning del decoder esta semana.
- No multi‑agente de 4–5 pasadas por pregunta: no cabe en el presupuesto de ~22 s/pregunta del sábado.
- No usar las 50 de muestra como few‑shot hasta que los organizadores lo autoricen.
- No cambiar retrieval y decoder en el mismo experimento.
- No reescribir la semántica de `citation_guard`/`legal.py` sin que Luis lo revise (ver T1b): son ~60 tests de A/B compartiendo esa capa.
