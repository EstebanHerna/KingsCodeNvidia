# División de trabajo — KingsCode v0.5 — 2 integrantes

La división anterior se actualiza porque el sistema ahora es **Graph-Aware desde Corpus v0** y porque B no solo hace inferencia: también controla el análisis de consulta, routing y evaluación.

## Integrante A — Knowledge Layer / Corpus / Graph / Retrieval
Responsable principal de:
- inventario y priorización de fuentes oficiales;
- descarga, checksum y trazabilidad;
- normalización de leyes, códigos, decretos y sentencias;
- chunking jurídico estructural/adaptativo;
- metadatos de norma, artículo, parágrafo, inciso, vigencia y fuente;
- grafo jurídico desde la ingesta;
- edges `CONTIENE`, `REMITE_A`, `CITA`, `MODIFICA`, `DEROGA`, `REGLAMENTA`, `DESARROLLA`, `EXCEPCIONA` solo con evidencia;
- índice BM25;
- embeddings;
- RRF;
- reranking;
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
- normalización de consulta y expansión terminológica controlada;
- detector de señales jurídicas exactas: ley, decreto, artículo, sentencia, autoridad, vigencia;
- política `graph_mode=off|auto|on`;
- decoder bakeoff: Qwen3-8B, ALIA Legal 7B, Salamandra 7B y control opcional Llama 8B;
- prompts por formato de pregunta;
- salida estricta compatible con schema;
- `citation_guard` determinista;
- política de abstención;
- harness de `evaluate.py` y RAGAS;
- experiment tracking;
- latencia, VRAM y extrapolación a 992 preguntas;
- interfaz;
- comando único de reproducción;
- ensamblaje de entregables, informe y video.

### Entregable de B
```text
answer(question, passages, format) -> submission_row
```

## Trabajo compartido
- definición de experimentos y criterios de aceptación;
- pruebas Graph OFF vs AUTO;
- congelación de configuraciones;
- revisión de errores del sample de 50;
- decisión final de decoder;
- validación de reproducibilidad;
- ejecución del sábado.

## División paralela inmediata
### A ahora
1. construir Corpus v0 con fuentes oficiales prioritarias;
2. producir `passages.jsonl`, `graph/nodes.jsonl`, `graph/edges.jsonl`;
3. crear BM25 baseline;
4. medir retrieval sobre sample_50.

### B ahora
1. crear harness que consuma passages mock/reales sin depender de CUDA;
2. implementar normalizador de consultas y `graph_router` determinista inicial;
3. implementar validador de schema + citation guard;
4. preparar runner del evaluador y registro de experimentos;
5. dejar el bakeoff de modelos parametrizado para cuando se valide la 4090.

## Regla de carga
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
