# Plan de B después de los resultados de la RTX 4090

Fecha: 2026-09-28 (noche). Fuente: resultados de `upstream/feat/member-a-gpu-results-4090-20260928` (commit `60ebf7e`, 5 commits por delante de `main` y 0 por detrás) y revisión del código de B en `main`.
Uso: una sesión de Claude Code por tarea, con `/b2-tarea B7` (o la que toque). Cada tarea planea primero y espera aprobación.

> Verificado el 2026-09-29 sobre `main` (`a3548a1`): `SEARCH_V2_DEV_BEST.txt` da `HYB120_LOC_META_1p25` EC@8 0,99167 (delta contra R6 +0,15, IC 95 % [0,0917; 0,2167], 10.000 remuestreos, semilla 0); `SEARCH_V2_VALIDATION_BEST.txt` da 1,0. `dense.npy` (106.741.888 bytes, SHA-256 `0c156c5e9…`) no está en ninguna rama de git. La rama GPU no toca archivos de B (`kingscode/reasoning/`, `kingscode/generation/`, `interfaz/`, `tests/test_reasoning.py`), así que el trabajo de B no choca con su merge.

---

## 0. Qué cambió y qué significa para B

- **Retrieval explícito quedó resuelto.** Con `locator_injection=true`: dev `HYB120_LOC_META_1p25` EC@8 0,9917 (IC 95 % del delta contra R6: +0,09 a +0,22). En validación, todas las variantes con locator dan 1,0. Fuente: `reports/gpu_freeze_4090/SEARCH_V2_*_BEST.txt` en esa rama.
- **Eso no demuestra calidad en preguntas semánticas.** El benchmark v1 es 200/200 `EXPLICIT` y la muestra oficial solo tiene 4/50 preguntas con artículo en el enunciado. Para B, la palanca pendiente ahora es la generación.
- **El locator es de A.** B no lo implementa: sigue llamando `retrieve(question, k, graph_mode)`.
- **El mayor hueco del proyecto es que no existe ni una respuesta generada por un decoder real.** Todo lo que B puede hacer sin GPU tiene que quedar listo antes de conseguirla.

## 1. Correcciones al plan recibido (aplicar tal cual)

| Punto del plan | Corrección | Motivo |
|---|---|---|
| B2: guarda en tres niveles, con "rechazo / abstención" si el cuerpo no está | Si el cuerpo no está, **se suprime la cita**, no se abstiene el ítem. Solo se abstiene si, tras suprimir, queda vacío un campo obligatorio de texto libre | Una cita sin respaldo resta el doble; abstenerse pierde además los 30 puntos de RAGAS del ítem y la exactitud en cerradas. El enunciado (anexo B.5) dice "corrige o suprime la citación" |
| B2: "cuerpo presente pero artículo no → warning / fallback" | Concretar el fallback: **reescribir la cita a nivel de cuerpo** (quitar el número de artículo), registrar el warning y conservar la oración | No se afirma un artículo que no está en la evidencia, que es el rigor buscado, y el evaluador puntúa por cuerpo, así que no se pierde la cita |
| B5: "mientras tanto, opciones seguras ALIA y Salamandra; Qwen3-8B condicionado" | **Qwen3-8B sigue en el bakeoff.** El enunciado (§3.1) lista textualmente `Qwen/Qwen3-8B` y `meta-llama/Llama-3.1-8B-Instruct` como "opciones sugeridas", aunque tengan 8.190.735.360 y 8.030.261.248 parámetros. Pedir la confirmación por escrito igual | Descartarlo sin respuesta de la organización sacrifica al candidato más fuerte por un riesgo que el propio enunciado desactiva |
| B4: medir T5 "sobre las 15 cerradas" | Reportar con intervalo de confianza y como indicativo. 15 ítems no bastan para decidir; la decisión final sale del puntaje end-to-end en cerradas | Muestra pequeña |
| B7 antes que la concurrencia | De acuerdo. Además, **la escritura atómica y el chequeo 992/992 son requisitos** para el sábado | — |

## 2. Reglas para Claude Code en estas tareas

1. No tocar `kingscode/` fuera de `reasoning/`, `generation/` e `interfaz/`. Nada de A: locator, retrieval, corpus, manifest, benchmark.
2. No cambiar la semántica de `legal.py` ni de `guards.py` sin una entrada en `docs/DECISION_LOG.md` marcada "requiere revisión de Luis" (regla 4 de `CLAUDE.md`). Preferir capas nuevas y aditivas.
3. Ningún texto de respuesta, ejemplo, prompt de few-shot ni dato lo genera un modelo cerrado. Los tests usan pasajes oficiales de `tests/fixtures/` o decoders falsos deterministas.
4. Solo se reportan números de archivos generados en la sesión, con su ruta; lo no ejecutado se marca "no ejecutado".
5. `--ragas` y descargas de pesos solo con aprobación explícita.
6. Suite completa verde antes de cerrar la tarea; hashes oficiales intactos.

---

## 3. Tareas de B

### B0 — Base única (hoy, antes de todo)

**Quién ejecuta el merge:** A (Luis). B verifica.
- La rama GPU está 5 por delante y 0 por detrás de `main`: el merge es fast-forward. Nadie arranca B1–B8 sobre otra base.
- Parches de Esteban pendientes (`esteban/claude-code-context`, ya integrado vía PR; `esteban/corpus-v02-plan` y este): aplicarlos sobre `main` después del merge.
- **Artefacto denso fuera de git:** `dense.npy` (106.741.888 bytes, SHA-256 `0c156c…`) y el `.tar.gz` de unos 97 MB (SHA-256 `968D2515…`) solo existen en el PC de la 4090 y el repo tiene 0 releases. Copiarlo hoy a Drive/OneDrive con enlace público de lectura y registrar URL y hash en `reports/gpu_freeze_4090/`. B es dueño de la entrega, así que B verifica que el enlace abre en una ventana privada.

**Aceptación (B):** en `main` actualizado, `python -m unittest discover -s tests -v` pasa (salvo los tests que requieren `corpus/` local, que se reportan aparte), `docs/OFFICIAL_SHA256.txt` coincide y el enlace del artefacto denso existe en el repo.

### B1 — Tests de integración A↔B sobre preservación de referencias

**Objetivo:** que la normalización de B nunca destruya lo que el locator de A necesita.
**Hacer:** `tests/test_integration_references.py` con casos: `Ley 1564 de 2012`, `Art. 90`, `arts. 90 y 91`, `artículo 2A`, `artículo 2.2.1.1`, `parágrafo 1`, `numeral 4`, `inciso segundo`, `C-355/06`, `SU-214/16`, `SL3385-2022`, `Decreto 1072` (sin año: debe quedar intacto y marcado incompleto), `Constitución`, `CGP`, `CST`, `Estatuto Tributario`, y varias referencias en una misma pregunta.
Para cada caso comprobar tres cosas: (a) `normalize_query(q).retrieval_text` contiene el texto original de la referencia sin alterar; (b) `legal.references` y `scripts/citations.extract` coinciden en el cuerpo canónico cuando la referencia es completa; (c) las variantes por opción de `query_variants` conservan la referencia de la pregunta.
Cuando A publique el locator productivo, añadir un test que llame `retrieve()` con un corpus mínimo de fixtures y verifique que el pasaje exacto llega al top‑8.
**Aceptación:** tests nuevos verdes; ningún cambio en `query.py` salvo que un caso falle. Si falla, arreglarlo con un cambio mínimo y registrarlo.

### B2 — Guarda en tres niveles (requiere revisión de Luis)

**Diseño:**

```
por cada cita extraída de un campo de texto
 ├─ cuerpo y artículo presentes en los 10 pasajes        → aceptar
 ├─ cuerpo presente, artículo ausente                     → reescribir a nivel de cuerpo + warning
 └─ cuerpo ausente                                        → suprimir la oración (o solo el fragmento si vacía el campo) + warning
tras la guarda
 ├─ campos obligatorios completos                         → entregar
 └─ campo obligatorio vacío en texto libre                → abstención de ese ítem, con motivo
cerradas: nunca se abstienen; `justificacion` vacía se rellena con las referencias del citation builder (B3)
```

- "Presente" usa el criterio del evaluador para el cuerpo (`citations.bodies` sobre el texto de los 10 primeros pasajes) y el de `legal.py` para el artículo.
- Eliminar el error `non_abstaining_answer_without_verifiable_citation` como bloqueante: pasa a warning. Con B3 casi nunca ocurrirá.
- Implementar como `kingscode/reasoning/citation_repair.py` que se aplica **antes** de `citation_guard`. Así la guarda actual queda intacta como verificación final: si algo llega a ella sin respaldo, es un bug.
- El `except CitationGuardError` de `Pipeline.run` se conserva como red de seguridad.

**Aceptación:**
- Tests: los tres niveles con pasajes oficiales de fixtures; abreviaturas peligrosas (`C.P.`, `CC`, `E.T.`) se suprimen; en cerradas no hay abstención.
- Tras la reparación, `citation_guard` nunca lanza sobre 50 filas de un decoder falso que mezcla citas buenas, de artículo equivocado e inventadas.
- Evaluador oficial sobre esas filas: `tasa_sin_respaldo = 0`.

### B3 — Citation builder determinista

**Objetivo:** que el formato de cita no dependa del decoder.
**Hacer:** `kingscode/reasoning/citation_builder.py`:
- `build_references(passages, used_ids, max_refs) -> list[str]` a partir de `norm_name` y `article` de A. Ejemplo: `artículo 90 del Código General del Proceso (Ley 1564 de 2012)`. Para sentencias: `Sentencia C-355 de 2006`.
- El prompt pide al decoder los ids de los pasajes usados (`pasajes_usados`). Si no los devuelve, se usan los 3 primeros.
- Destino: `referencia_legal` (semiabiertas), cola de `justificacion` (cerradas), `marco_normativo` con un máximo de 3 (abiertas, porque las lee el juez RAGAS).
- `max_refs` en config. Referencia de implementación: `docs/reference_b_prototype/citerender.py` y `guard.py::build_refs`.

**Aceptación:** test de ida y vuelta para los 163 `norm_name` del manifest (o fixtures si no hay corpus local): cada referencia construida pasa `citation_guard` con su pasaje de origen y `citations.extract` recupera el cuerpo. Medición con `tools/analyze_citation_ceiling.py` para `max_refs` 3 y 6 sobre la corrida más reciente.

### B4 — Medir T5 (consultas por opción en cerradas)

**Requisito:** `corpus/` local de v0.1 (o correr en el PC de A).
**Hacer:** `tools/measure_option_queries.py`: para las 15 cerradas de la muestra, base contra variantes por opción. Métricas: cuerpos del `legal_basis` presentes en el top‑8 (a nivel cuerpo, como el evaluador), documento correcto en el top‑8, tokens de contexto y latencia. Bootstrap pareado, semilla 0.
Leer `legal_basis` solo en el script de medición, nunca en el pipeline (mismo patrón que `analyze_citation_ceiling.py`).
**Aceptación:** reporte en `reports/member_b/option_queries/` con IC 95 % y la recomendación: mantener, quitar o dejar solo si el locator no disparó.

### B5 — Elegibilidad del decoder (hoy, correo)

**Hacer (humano, no Claude Code):** responder al hilo de la organización:

> Asunto: [Hackathon 2026] Consulta límite de parámetros — KingsCode
> Profesor Manrique, el enunciado (§3.1) sugiere Qwen/Qwen3-8B y meta-llama/Llama-3.1-8B-Instruct, que según sus model cards tienen 8.190.735.360 y 8.030.261.248 parámetros. ¿Podemos confirmar que ambos cumplen el límite de 8.000 millones? Gracias. Equipo KingsCode.

**Claude Code:** registrar la pregunta y, cuando llegue, la respuesta en `docs/DECISION_LOG.md` y `docs/MODEL_LOCKS_GATE2.md`. Mientras no haya respuesta, Qwen3-8B sigue en el bakeoff.

### B6 — Bakeoff de decoders (primer uso de la próxima GPU)

**Preparar sin GPU:**
- `artifacts/retrieval_freeze.json` (hoy no existe): las 50 preguntas con los 8–10 pasajes de la configuración de A congelada (locator + BM25 como mínimo), con hashes de corpus e índices. Mismos pasajes para todos los modelos.
- Ensayo del comando `tools/member_b.py bakeoff` con un decoder falso: produce filas, trazas, métricas y una tabla comparativa.
- Checklist de GPU en `docs/GPU_DAY_RUNBOOK.md` para B: descargar pesos → `decoder-smoke` → bakeoff → **medir segundos por pregunta con el ensayo de 992 (B7)**.

**En GPU:** Qwen3-8B, ALIA 7B y Salamandra 7B en bf16, temperatura 0, una sola variable (el decoder). Métricas: puntaje oficial sin RAGAS, JSON válido, citas sin respaldo antes y después de la reparación, abstenciones, latencia p50/p95, VRAM máxima y tokens. RAGAS solo para los 2 finalistas, una corrida cada uno.
**Criterio:** mayor puntaje automático con 992 preguntas que quepan en menos de 3 horas medidas. Si ninguno cabe con `transformers` y `batch_size=1`, el siguiente experimento es vLLM, no otro modelo.

### B7 — Robustez para las 992 (prioridad 1 sin GPU)

**Hacer** en `kingscode/reasoning/experiments.py` (o un runner nuevo `kingscode/reasoning/batch.py`, preferible para no romper Gate 1B):
- Checkpoint por pregunta: `runs/<id_corrida>/items/<id>.json` escrito de forma atómica (archivo temporal + `os.replace`).
- `--resume`: salta los ítems con checkpoint válido, que pasan `validate_submission`.
- Error por ítem: excepción → `errors/<id>.json` con traza; la corrida sigue.
- Reintento controlado: `--retry-errors` con máximo 2 intentos y la misma configuración (determinista).
- Respaldo final: si un ítem sigue en error, se entrega una fila de abstención válida con motivo `pipeline_error` (en cerradas, la mejor letra del respaldo léxico determinista) y se registra.
- Ensamblado final: `submissions.jsonl` ordenado por id, escrito de forma atómica, con chequeo de completitud (todos los ids de entrada, sin duplicados, 0 errores de schema) y hash.
- Modo verificación en vivo: `--only 17,203,815 --concurrency 1` que regenera ítems y los compara con la entrega (normas citadas y pasajes idénticos).

**Aceptación:** test con un decoder falso que falla en ids fijos y un corte simulado a mitad de corrida. Reanudar produce un `submissions.jsonl` idéntico byte a byte al de una corrida sin fallos. Ensayo de 992 filas (la muestra repetida con ids sintéticos) con el decoder dummy en menos de 10 minutos en CPU.

### B8 — Interfaz y entrega

**Interfaz (`interfaz/app.py`):** pregunta → respuesta; lista explícita de normas citadas en los tres formatos (la rúbrica 6.2 da 3 puntos por "visualización de los pasajes recuperados y de las normas citadas"); pasajes con fuente y enlace; aviso de abstención con motivo; identidad de Software Colombia. Probar con el corpus real en el PC de A.
**Reproducibilidad (2 puntos, verificación automática "desde cero, un único comando, contenedor limpio, sobre las preguntas de muestra"):**
- `run.sh` descarga el corpus e índice congelados desde el enlace público (verificando hashes), instala y ejecuta la muestra.
- Probar desde un clon limpio en un contenedor sin caché.
- README: sección `## Corpus e índice` con enlace, tamaño, licencia y fecha de vigencia (30 días).
**Paquete de corpus (entregable 5):** `corpus_kingscode.zip` con `LICENSE`, `corpus_manifest.json`, `corpus/` e `indice/` (BM25 + `dense.npy` + `chunks.jsonl`), según `entregables/sabado/README.md`.

---

## 4. Orden y calendario de B

| Cuándo | B |
|---|---|
| Lun 28 noche | B0 (verificar merge + artefacto denso a la nube), B5 (correo) |
| Mar 29 | B7 robustez → B2 reparación de citas → B3 builder → B1 tests |
| Mié 30 | Workshop NVIDIA todo el día. Si hay un rato: B4 con corpus local |
| Jue 1 | B6 bakeoff en GPU con `retrieval_freeze.json` congelado; ensayo cronometrado de 992 |
| Vie 2 | B8 interfaz + `run.sh` en contenedor limpio + paquete del corpus; reporte de avance 17:00 con el puntaje real |
| Sáb 3 | Ejecución con B7 (`--resume` listo), verificación en vivo con `--only` |

## 5. Puntos de sincronización con A

1. **Ahora:** merge de la rama GPU a `main` y actualización de la documentación de estado (A). B no avanza sobre otra base.
2. **Locator productivo:** A entrega `retrieve()` con locator, sus tests y la procedencia. B corre B1 contra él y regenera `retrieval_freeze.json`.
3. **Freeze de corpus v0.2 (o decisión de quedarse en v0.1 + locator):** a partir de ahí retrieval no cambia y B compara solo decoders.

---

## 6. Estado al 2026-09-29 (rama `feat/b-planner-batch-citations`)

| Tarea | Estado | Evidencia |
|---|---|---|
| B0 | BLOQUEADO (humano/A) | merge de la rama GPU, subida de `dense.npy`/`.tar.gz`, correo B5 |
| B1 | DIFERIDO | espera el locator productivo de A; la preservación de Q0 y de referencias del planner ya tiene tests |
| B2 | HECHO, requiere revisión de Luis | `kingscode/reasoning/citation_repair.py`; `tasa_sin_respaldo` 0,0 sobre 50 filas con citas mezcladas |
| B3 | HECHO (parcial: el decoder aún no devuelve `pasajes_usados`, se usan los 3 primeros) | `kingscode/reasoning/citation_builder.py`; ida y vuelta en las 5 fixtures |
| B4 | NO EJECUTADO | requiere `corpus/` local |
| B6 | PREPARADO, no ejecutado | sin GPU; `retrieval_freeze.json` aún no existe |
| B7 | HECHO | `kingscode/reasoning/batch.py`, `tools/member_b.py batch|verify`; resume idéntico byte a byte; 992 fixtures en 41,6 s |
| B8 | PARCIAL | interfaz y `run.sh` existen; probar con corpus real |
| Planner | HECHO sin ejecución real | `planner.py`, `plan_store.py`, `planner_backend.py`, `tools/analyze_query_plans.py`; NO GENERALIZATION CLAIM hasta el DEV independiente de A |

## 7. Estado al 2026-09-29, tarde (continuación de B)

| Elemento | Estado |
|---|---|
| `pasajes_usados` (prompt v3, validación, builder) | IMPLEMENTED_AND_CPU_VERIFIED |
| Normalizador de sobre JSON (solo v3) | IMPLEMENTED_AND_CPU_VERIFIED |
| Diagnósticos por pregunta y agregados del batch | IMPLEMENTED_AND_CPU_VERIFIED |
| Contrato del bakeoff con freeze de fixtures | IMPLEMENTED_AND_CPU_VERIFIED (fixture, no competitivo) |
| Tests de inyección en pregunta/opciones/pasajes | IMPLEMENTED_AND_CPU_VERIFIED |
| Respaldo del batch vs evaluador oficial ("A" formal no puntúa) | IMPLEMENTED_AND_CPU_VERIFIED |
| Interfaz: evidencia escapada, citado vs recuperado, depuración separada | IMPLEMENTED_AND_CPU_VERIFIED (helpers); UI con corpus real PREPARED_NOT_EXECUTED |
| `run.sh --fixture` | IMPLEMENTED_AND_CPU_VERIFIED |
| `docker run -e FIXTURE=1` | PREPARED_NOT_EXECUTED (daemon apagado) |
| Experimento BASE vs PLAN (`docs/experiments/B_BASE_VS_PLAN_v1.json`) | PREPARED_NOT_EXECUTED · BLOCKED_ON_A_FREEZE |
| Freeze de retrieval real y bakeoff de decoders | BLOCKED_ON_A_FREEZE · BLOCKED_ON_GPU |
| Planes Qwen congelados | BLOCKED_ON_A_FREEZE (solo para el experimento BASE vs PLAN; ya no se generan en la sesión GPU) |
| Primera generación real | BLOCKED_ON_A_FREEZE · BLOCKED_ON_GPU |
| Runners GPU (`run_b_gpu_4090.ps1 -Phase prep` / `-Phase decoder`, `kingscode_gpu_todo.ps1`) alineados con el runbook §8 (2026-09-30) | IMPLEMENTED_AND_DRY_RUN_VERIFIED · fase `decoder` BLOCKED_ON_A_FREEZE · requiere merge del PR #6 |
| Elegibilidad del decoder | ALIA (7.768.117.248) por defecto; Qwen3-8B (8.190.735.360) solo con `-IncludePendingEligibility`, marcado no competitivo hasta confirmación escrita (correo B5 pendiente) |
| Elegibilidad del decoder (2026-10-01) | Qwen3-8B elegible por decisión del equipo (sugerido en enunciado §3.1); por defecto `qwen3-8b,alia-legal-7b`. Sustituye la fila anterior |
| RAGAS | EN PAUSA: sin gastar crédito hasta autorización de Esteban |

## 8. Estado al 2026-10-01 (primer decoder real)

| Elemento | Estado |
|---|---|
| Smoke Qwen3-8B en la 4090 (Luis y `turing`) | PASSED en `turing` tras el arreglo de longitud (PR #11); BF16, 18,9 GB, ~27 tok/s |
| Longitud de oraciones/palabras | Advertencia (`format_warnings`), no rechazo, en v3 (PR #11) |
| Reintentos deterministas | Eliminados para `INVALID_MODEL_OUTPUT`/`CONTEXT_LIMIT_EXCEEDED` (PR #11) |
| Atención del decoder | `sdpa` (antes `eager`: 46 GB reservados, desborde a RAM, 93 s/pregunta) (PR #18) |
| Evidencia que no cabe en 8192 | El prompt omite los pasajes de menor rango; la fila conserva los 8 (PR #18) |
| Progreso del batch | Una línea por pregunta en stderr (PR #17) |
| PC nueva | `tools/kingscode_pc_nueva_diagnostico.ps1`: instala, obtiene corpus (archivo/release/descarga oficial), combina v0.1+v0.2, smoke, `sample_50`, evaluador; `-ExactLocator`, `-RetrieverMode`, `-Rerank`, `-Ragas` |
| Corpus de `turing` | Descarga oficial: 163/191 objetivos, 96/163 idénticos a v0.1 — solo diagnóstico |
| `sample_50` con SDPA | PENDIENTE de medir: s/pregunta, proyección 992, abstenciones, puntaje sin RAGAS |
| Freeze de A y bakeoff | BLOCKED_ON_A_FREEZE |
| RAGAS | EN PAUSA hasta autorización |
