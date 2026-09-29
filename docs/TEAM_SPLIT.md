# División de trabajo — KingsCode v0.5 — 2 integrantes

> **Actualizado 2026-09-28.** La versión anterior describía como "trabajo paralelo inmediato" tareas que ya están terminadas (Corpus v0, harness de B sin GPU). Esta versión refleja el estado real: ambas capas base existen (`kingscode/`, `kingscode/reasoning/`), Gate 2-Prep ya dejó preparado el entorno GPU y el decoder real, y lo que falta es ejecución en la 4090 + entregables de cierre. El detalle vivo de estado vive en `docs/KINGSCODE_STATE.json` y `docs/GPU_DAY_RUNBOOK.md`; este documento es la división de responsabilidades, no el estado.

## Integrante A (Luis) — Knowledge Layer / Corpus / Graph / Retrieval
Responsable principal de:
- inventario y priorización de fuentes oficiales; resolver los 28 objetivos pendientes;
- normalización de leyes, códigos, decretos y sentencias; metadatos de norma/artículo/parágrafo/vigencia;
- grafo jurídico (`CONTIENE`, `REMITE_A`, `CITA`, `MODIFICA`, `DEROGA`, `REGLAMENTA`, `DESARROLLA`, `EXCEPCIONA`), solo con evidencia;
- índice BM25, embeddings, RRF, reranking;
- Recall@1/3/5/10, MRR, legal_basis@10 y cobertura por área;
- `CORPUS.md` y `corpus_manifest.json`.

### Entregable de A a B
```text
retrieve(question, k, graph_mode="auto") -> passages
```

A debe poder devolver el mismo formato de passage independientemente de si vino del fast path o de expansión del grafo.

### Añadidos v0.6 de A (metadatos/recuperación)
- Identidad canónica determinista independiente de la URL (`canonical_document_id`, `canonical_fragment_id`) en `kingscode/metadata.py`.
- Clasificación del backlog de adquisición (`kingscode/acquisition_backlog.py`), sin sustituir identificadores.
- Deduplicación/diversificación configurable y apta para ablación (`kingscode/diversify.py`), off por defecto.
- Taxonomía de fallos de recuperación + `document_mismatch_rate` (`kingscode/failure_analysis.py`).
- Experimentos opcionales R6/R7/R8 (`kingscode/metadata_experiments.py`) sobre la API pública; no cambian R0–R5 de B ni la ruta por defecto.
- Reporte de cobertura v0.6 y auditoría grafo/temporal (`kingscode/coverage_report.py`).

El contrato público `retrieve(...)` se mantiene idéntico; B no necesita cambios. Los scores de recuperación en tiempo de ejecución no son metadatos persistentes del corpus.

## Integrante B — Query/Reasoning Layer / Generation / Evaluation / Delivery
Responsable principal de:
- normalización de consulta y expansión terminológica controlada (`kingscode/reasoning/query.py`);
- política `graph_mode=off|auto|on` (`routing.py`) y de abstención (`policy.py`);
- **entorno GPU/CUDA completo** (ver §2 abajo — antes ambiguo entre A y B, ahora explícito);
- decoder bakeoff: Qwen3-8B, ALIA Legal 7B, Salamandra 7B, Llama 3.1 8B opcional (`kingscode/generation/`);
- prompts por formato (`kingscode/generation/prompts.py`), salida estricta compatible con schema;
- `citation_guard` y su comportamiento ante fallos (`guards.py`, `pipeline.py`);
- harness de `evaluate.py` y RAGAS, experiment tracking;
- latencia, VRAM y extrapolación a 992 preguntas;
- interfaz (`interfaz/app.py`), comando único de reproducción;
- ensamblaje de entregables, informe y video.

### Entregable de B
```text
answer(question, passages, format) -> submission_row
```

## Regla que no cambia
`A no debe empezar a cambiar el decoder. B no debe empezar a cambiar cómo A indexa el corpus.` Se comunican solo por `retrieve(...)` / `answer(...)`. Cambios a la semántica de `kingscode/reasoning/legal.py` o `guards.py` (compartida, muy probada) requieren revisión cruzada antes de aplicarse — ver `docs/DECISION_LOG.md`.

## 2. Entorno GPU — B es dueño (aclaración del 28-sep-2026)

Gate 2-Prep ya puso bajo herramientas de B: `prepare_gpu_environment.py`, `prepare_models.py`, `gpu_smoke.py`, el backend del decoder y los locks de modelo. Formalizarlo evita que A y B toquen a la vez el mismo entorno CUDA/PyTorch el día de la 4090:

```text
B: máquina → driver → PyTorch → CUDA → dependencias → model cache → GPU smoke → "GPU_READY"
A: toma la máquina solo después de "GPU_READY" y ejecuta retrieval
```

## 3. Día de GPU como carrera de relevos

| Etapa | Quién | Qué hace | Resultado para el siguiente |
|---|---|---|---|
| GPU 0 | B | `git pull`, verificaciones Gate 2, GPU diagnose, PyTorch correcto, requirements GPU, model verify, GPU smoke | `GPU_READY` |
| GPU 1 | A | build dense index, R0 BM25 → R1 dense → R2 hybrid → R3 hybrid+reranker → R4 +Graph AUTO → R5 +Graph ON | Recall@1/3/5/10, MRR, coverage, latencia, efecto del grafo |
| Sync #1 | A + B | eligen juntos el mejor retrieval con evidencia (no automático); `freeze retrieval` | 8 pasajes fijos para todos los decoders siguientes |
| GPU 2 | B | decoder-smoke, luego D1 Qwen3-8B, D2 ALIA Legal 7B, D3 Salamandra 7B — mismas 50 preguntas, mismos 8 pasajes, misma temperatura, mismo contrato de salida | score oficial, RAGAS, valid JSON, citas, abstenciones, latencia, tokens, VRAM |
| GPU 3 | A + B | error analysis conjunto (ver tabla de categorías) | decoder final elegido, freeze de versiones |

Durante GPU 1, B puede analizar tablas/reportes pero **no cambia el pipeline** hasta el punto de sincronización.

## 4. Categorías de error y a quién vuelven

```text
FAIL
├── corpus_missing        → A
├── wrong_document        → A
├── wrong_passage         → A
├── reranking_failure     → A
├── graph_failure         → A
├── reasoning_failure     → B
├── citation_failure      → B
├── format_failure        → B
└── abstention_failure    → B
```

Este reparto evita que ambos intenten arreglar todo a la vez durante las pocas horas del sábado.

## 5. Tablero de ownership

| Trabajo | A | B |
|---|---:|---:|
| Corpus | ✅ Owner | revisión |
| Fuentes/28 pendientes | ✅ | ayuda puntual |
| Metadata jurídica | ✅ Owner | consume |
| Grafo | ✅ ejecución | router (consume) |
| BM25/dense/RRF/reranker | ✅ Owner | — |
| Retrieval metrics | ✅ | análisis compartido |
| Query parser | | ✅ Owner |
| Graph router | interfaz (`retrieve`) | ✅ Owner |
| CUDA/PyTorch/entorno GPU | | ✅ Owner |
| Model downloads/locks | | ✅ Owner |
| GPU smoke | | ✅ Owner |
| Prompts | | ✅ Owner |
| Decoder | | ✅ Owner |
| Citation guard | metadata (pasajes) | ✅ Owner |
| Abstención | evidence flags | ✅ Owner |
| Official evaluator / RAGAS | | ✅ Owner |
| Interfaz | apoyo | ✅ Owner |
| Error analysis | ✅ | ✅ |
| Freeze final | ✅ | ✅ |
| Sábado | ✅ | ✅ |

## 6. Regla de carga
Si A se bloquea por obtención de fuentes, B ayuda con adquisición/QA de corpus.
Si B se bloquea por GPU/modelos, A ayuda con evaluación y análisis de errores.
No se paraliza el proyecto porque una capa esté esperando a la otra.


### Benchmark interno v1 (A, con auditoría independiente)
A es owner de `benchmarks/kingscode_ir/`, su separación input/gold, el
evaluador de retrieval, métricas/bootstraps, complementarity y el loop de
fallos. B no recibe estos golds ni depende de sus internals. La selección
requiere validation + confirmación posterior; hasta entonces B no recibe un
nuevo freeze. El auditor revisa fuga, integridad de splits/golds, metodología y
provenance antes de aceptar cada checkpoint.

## Handoff vigente tras GPU — A v0.2

A: `feat/member-a-corpus-v02-locator` desde 60ebf7e. Responsable de locator productivo, snapshot histórico v0.1, benchmark v2, adquisición v0.2 y riesgos de parser/grafo. Las ramas de harness y auditoría anteriores se conservan como checkpoints; no se reejecutan R1–R8.

B: conservar referencias explícitas al normalizar la consulta, consumir `retrieve(question, k, graph_mode="auto")`, respetar provenance y estados temporales desconocidos. Seguir `docs/A_TO_B_V02_CONTRACT.md`. B decide y ejecuta su decoder con evidencia congelada de un perfil explícito; no inferir calidad del decoder a partir del 1.0 de retrieval v1. Revisión cruzada pendiente con Luis antes de aceptar arquitectura o freeze competitivo.


### Estado A actualizado — 2026-09-29

La rama A continúa parcial y separada. El benchmark-v2 independiente aún tiene cero ítems/golds/sealed eval; no ajustar retrieval contra el piloto corpus-derived. A expone query_views textual por RRF, con exact locator limitado a la pregunta original. No implementar Qwen ni reglas question→norm. Remediaciones corpus-v0.2 pendientes según docs/MEMBER_A_V02_PROGRESS.md.
