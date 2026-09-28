# KingsCode Decision Log

## 2026-09-27 — v0.1
- Validar starter pack antes de GPU.
- No instalar CUDA/PyTorch a ciegas.

## 2026-09-27 — v0.2
- Equipo de 2 dividido por subsistemas.
- Baseline retrieval: BM25 + Qwen3-Embedding-0.6B + Qwen3-Reranker-0.6B.
- Qwen3-8B como decoder prior inicial.
- Decoder fine-tuning pospuesto; reranker hard-negative FT como primer candidato.
- RTX 4090 24 GB como hardware objetivo; probar BF16 antes de cuantización.

## 2026-09-27 — v0.3 (literatura)
- Retrieval pasa a ser explícitamente la prioridad #1 por evidencia de Legal RAG Bench 2026 y otros benchmarks legales.
- Se añade RRF como fusión baseline.
- Chunking pasa de “por artículo” simple a “structure-aware/adaptive”, preservando jerarquía legal.
- Se añade expansión terminológica controlada para español jurídico, no multi-query libre por defecto.
- Se añade `citation_guard` post-generation como componente obligatorio.
- Se añade ALIA-es-legal-administrative-7B-Instruct al bakeoff de decoders.
- GraphRAG queda como experimento opcional, no baseline.
- Se formaliza gate de fine-tuning: no decoder FT hasta tener retrieval alto.
- Siguiente acción congelada: Corpus v0 + benchmark BM25/retrieval antes de CUDA.

## 2026-09-27 — v0.4 (Graph-aware desde Corpus v0)
- Se corrige la decisión anterior de dejar GraphRAG solo para después del baseline.
- El corpus nace con jerarquía y grafo jurídico desde la ingesta.
- No se adopta GraphRAG pesado para todas las consultas: BM25+dense+RRF sigue siendo el fast path.
- El grafo se usa selectivamente para relaciones jerárquicas/normativas (`REMITE_A`, `MODIFICA`, `DEROGA`, `REGLAMENTA`, etc.).
- Se confirma al iniciar Integrante A que el ZIP oficial **no contiene los textos jurídicos completos**; contiene `seed_targets.json` con 186 objetivos y ubicaciones de búsqueda.
- Se crean schema canónico de pasajes/grafo y plan operativo del Integrante A.

## 2026-09-27 — v0.5 (Agent-ready + roles A/B revisados)
- Se corrige la división antigua: B ya no es solo inferencia/evaluación; ahora posee Query/Reasoning Layer, `graph_router`, generación, guards, evaluación y delivery.
- A pasa a ser explícitamente Knowledge Layer: corpus + provenance + graph + retrieval + reranking + métricas.
- Se crea `AGENTS.md` como protocolo operativo para cualquier agente/humano que continúe el proyecto.
- Se formalizan contratos `retrieve(..., graph_mode)` y `answer(...)`.
- Se crea `MEMBER_B_REASONING_EVAL_PLAN.md`, `INTEGRATION_CONTRACTS.md` y `ARCHITECTURE_V05.md`.
- Roadmap pasa a trabajo paralelo: A construye Corpus v0/BM25 mientras B construye harness pre-GPU/router/citation guard/evaluator.
- CUDA deja de ser un gate que bloquee a ambos; se aborda cuando el harness de B esté listo y haya máquina real.

## 2026-09-27 — Implementación de A / Corpus v0.1

- Se materializa el corpus desde fuentes oficiales: Función Pública, Corte Constitucional, SENA, Comunidad Andina y Corte Suprema. El inventario conserva 28 objetivos sin resolver, en vez de reemplazar años/números por coincidencias aproximadas. HTTPS valida certificados; raw y metadatos quedan disponibles para reconstrucción offline.
- Parser `legal-blocks-1.2`: artículos, numeración compuesta, reformas citadas, jerarquía, parágrafos y numerales; decisiones por estructura explícita. Se preservan páginas PDF y offsets exactos del clean. La portada CAN 486 sin texto utilizable se omite del clean; raw permanece completo.
- La revisión adicional detectó anexos/versiones con el mismo número de artículo. Se excluye de recuperación el grupo ambiguo completo, conservándolo para auditoría. No se decide automáticamente la versión vigente. Este cambio reduce el riesgo de atribuir un anexo al artículo de la norma principal.
- BM25 es el backend activo local pre-GPU. Dense Qwen3, RRF y reranker Qwen3 están implementados con commits fijos y prueba real; no se afirma benchmark neuronal completo. La máquina examinada tiene PyTorch 2.12.0+cpu, CUDA no disponible; 4090 sigue siendo objetivo externo.
- Grafo acotado: un salto, cinco semillas, dos pasajes por vecino, diez expansiones. Se emiten solo CONTIENE, CITA, REMITE_A y patrones explícitos MODIFICA/DEROGA; los demás tipos/tags quedan reservados a evidencia futura. AUTO es una política provisional inyectable por B. Su ausencia de disparos en el sample impide inferir que AUTO mejora OFF; ON se mide como ablation.
- Métricas: identidad canónica de fuente/artículo, no coincidencia de citas mencionadas en fuentes ajenas. `legal_basis` original se audita por separado y nunca llega al índice. MRR se trunca en 10 y nDCG cuenta objetivos distintos; no se afirma score oficial de QA.
- No se cambia decoder ni se inicia fine-tuning: la recuperación baseline aún requiere mejora. El siguiente paso compartido es integrar B y ejecutar comparaciones neuronales en la 4090 bajo el mismo snapshot.

## 2026-09-27 — Gate 1B / integración pre-GPU

- Se añade `kingscode/reasoning` sobre la API pública de A. La integración hace una recuperación OFF, decide con pregunta+evidencia y solicita expansión si corresponde. El adaptador devuelve bool porque A no recibe el contexto plano ni interpreta strings OFF/AUTO/ON en su callback. No se cambian internals de A.
- El límite de entrada del sistema proyecta exclusivamente ID, pregunta, formato y opciones. Las etiquetas solo se leen en el proceso del evaluador oficial; alterar etiquetas no modifica entradas públicas, fingerprint ni resultados del sistema.
- El backend dummy siempre se abstiene. Se verifica el pipeline completo sin producir supuestas respuestas jurídicas de prueba. La CLI bloquea backends reales, retrieval neuronal y RAGAS en este gate; temperatura prevista 0 y muestreo deshabilitado.
- Contradicción del schema oficial: la descripción de `respuesta_correcta` dice «Con abstencion true se admite null», pero su enum solo admite A/B/C/D. Sin modificar el archivo, el dummy usa A como marcador formal, declara que no representa una elección y mantiene abstención true. No se elige la letra según el banco.
- Citation guard más conservador que la puntuación documental del evaluador: comprueba número, año, artículo, identidad primaria de fuente y presencia literal en la evidencia emitida. No usa alias por número ignorando año ni atribuye artículos de un código a todas las leyes mencionadas en su título. No certifica implicación semántica de conclusiones.
- JSON/schema/citas inválidos abortan la corrida y se registran; no hay reparación manual ni publicación de un JSONL final parcial. Evidencia histórica/ambigua, conflictos fuertes o referencias insuficientes disparan abstención.
- Cada corrida conserva directorio nuevo, configuración/hashes/fingerprint, trazas, tiempos y evaluación oficial sin RAGAS. El JSONL y las decisiones son deterministas; las rutas/timestamps/latencias no se comparan como contenido reproducible. Cero citas del dummy no constituye evidencia de calidad de citación.

## 2026-09-28 — Gate 2-Prep, ejecución diferida por el usuario

- Se fija la revisión real de Qwen3-8B, ALIA Legal, Salamandra y Llama opcional desde el Hub oficial; las entradas originales del encoder/reranker permanecen iguales. Salamandra/Llama requieren acceso manual y no se presume autorización. Los conteos reales de los modelos nominales 8B requieren aclarar elegibilidad antes de entrega competitiva.
- La generación real se prepara en `kingscode/generation/` para conservar los módulos, salida y fingerprint del dummy. El backend implementa el protocolo existente, es lazy, usa snapshots locales con hashes, prohíbe remote code y conserva las guardas. No se descargaron decoders.
- Prompts lógicos `grounded-formats-v2`, template nativo de cada tokenizer, Qwen sin thinking; parámetros greedy explícitos comunes. Formato/JSON/citas/contexto inválidos abortan el experimento, sin truncar ni editar la respuesta. El router sigue basado en reglas, sin prompt/modelo generativo.
- Se separa la medición de retrieval de la comparación de decoders: rankings públicos medidos → freeze de ocho evidencias por pregunta → mismos datos para D1–D4. Se evita mantener retrieval y decoder juntos en VRAM. Los tiempos de generación no se presentan como latencia end-to-end en vivo.
- BF16 primero, contexto total 8192 y batch 1 preparados; fit/latencia no verificados. INT8/4-bit requieren registro de OOM BF16 de la misma configuración y evidencia, y nunca se activan automáticamente. El plan de entorno no escoge una build CUDA sin diagnóstico ni instala paquetes.
- La última instrucción del usuario reemplazó la ejecución de verificaciones por preparación sin pruebas. Se añaden 28 tests y dos comandos de verificación, **no ejecutados**. No se declara Gate 2A/2B ni bakeoff completado; los resultados previos A/1B se conservan como históricos.

## 2026-09-28 — v0.6 (Member A knowledge layer: metadata + retrieval)

- Se agrega una capa de derivación determinista (`kingscode/metadata.py`) con identidad canónica independiente de la URL: `canonical_document_id` (p. ej. `ley:1564:2012`, `decreto:410:1971`, `codigo_civil`, `constitucion:1991`, `corte_constitucional:c355:2006`, `corte_suprema:sl3385:2022`) y `canonical_fragment_id` en un espacio de nombres separado (p. ej. `ley:1564:2012:articulo:391`). Las variantes históricas o los encabezados de artículo repetidos se mantienen distintos. No cambia `corpus.py` ni el build; el corpus se reconstruye byte a byte idéntico (mismos hashes que v0.1).
- Metadatos v0.6 aditivos y opcionales: `content_hash` (solo cuerpo semántico, excluye `text_prefix`), `status_assertion`/`status_source_passage_id`/`effective_from`/`effective_to`/`version_date`. La validez legal nunca se infiere: por defecto `unknown`/`null` salvo evidencia explícita de la fuente. No se introduce ningún puntaje de autoridad arbitrario. La procedencia técnica (hash, HTTP, ruta, timestamp) se mantiene fuera del texto de embedding.
- Se separan explícitamente tres planos: metadatos de documento, metadatos de pasaje y **scores de recuperación en tiempo de ejecución** (`bm25_score`, `dense_score`, `rrf_score`, `reranker_score`, `graph_score`, `final_score`), que no se persisten como metadatos del corpus.
- Fase 1: se clasifican los 28 objetivos de adquisición no resueltos (`kingscode/acquisition_backlog.py`) en `resolved`/`not_found`/`ambiguous`/`source_unavailable`/`identifier_suspect`, conservando procedencia y notas. Nunca se sustituye una norma/año/número/decisión similar ni se corrige un identificador dudoso; los sospechosos se marcan para revisión humana. Resultado: 14 `source_unavailable` (Corte Suprema sin resolver verificado), 11 `not_found`, 2 `identifier_suspect`, 1 `ambiguous`.
- Fase 4: deduplicación y diversificación (`kingscode/diversify.py`) agrupables por `canonical_document_id`/`canonical_fragment_id`/`content_hash`. La diversificación es configurable, apta para ablación y **no** se activa por defecto; la procedencia de espejos duplicados se conserva, no se descarta.
- Fase 5: taxonomía de fallos de recuperación (`kingscode/failure_analysis.py`): `corpus_missing`, `correct_document_wrong_passage`, `wrong_document`, `ranking_failure`, `graph_failure`, `ambiguous_ground_truth`, más `success`. No se fuerza una clasificación cuando `legal_basis` es incompleto o contradictorio. Se añade `document_mismatch_rate` (definición propia; no se afirma equivalencia con una métrica académica DRM).
- Fase 6: experimentos R6/R7/R8 opcionales (`kingscode/metadata_experiments.py`) sobre la API pública `retrieve(...)`, sin tocar R0–R5 de B ni cambiar la ruta por defecto. Para referencias explícitas se usa localizador estructurado exacto + recuperación general → unión de candidatos → ranking; los rasgos de metadatos son priores suaves, nunca filtros duros. Registrados en `config/experiment_matrix.json`.
- Fase 7: representación de embedding experimental (`metadata.embedding_representation`) con encabezado Norma/Ley/Artículo/Título; excluye sha256, ruta, HTTP, bytes y `retrieved_at`. Es un experimento, no un reemplazo medido de la representación actual.
- Fase 8: se confirma que toda relación normativa del grafo conserva `source`, `target`, `relation`, `evidence_passage_id` y procedencia (`method`); 0 aristas sin evidencia. Estados temporales `current/historical/repealed/modified/unknown` solo con evidencia; por defecto `unknown`.
- Fase 9: reporte de cobertura v0.6 (`reports/corpus_coverage_v06.json`) que no usa el conteo de documentos como proxy de calidad.
- Verificación: 132 tests (16 A históricos + 44 nuevos v0.6 + 44 B + 28 GPU) en verde; dos verificaciones independientes con reconstrucción byte a byte y recomputación de métricas. Archivos oficiales (19) intactos; implementación de B intacta; sin GPU/bakeoff/RAGAS/fine-tuning; sin indexar `expected_answer`/`legal_basis`.
- La hipótesis de que el corpus deba responder casi cualquier pregunta del dominio se trata solo como hipótesis de diseño, no como requisito oficial del reto.

## 2026-09-28 — Internal retrieval benchmark v1 (Member A)

- Se crea un benchmark interno de recuperación separado del sample oficial: 200 casos deterministas derivados de metadata/pasajes oficiales (120 dev, 40 validation, 40 holdout; 20 por área). Preguntas y gold se guardan en archivos separados; `retrieve` recibe exclusivamente el texto de pregunta y los gold se cargan solo después de capturar rankings. No se usó un modelo cerrado ni se fabricaron preguntas semánticas: 20 paquetes de autoría quedan para revisión humana.
- Se definen métricas de evidencia a k=1/3/5/8/10, MRR/MAP/nDCG, recuperación documental, mismatch documental (definición propia), completitud de evidencia, spans, costo de contexto, subgrupos y bootstrap pareado determinista (seed 0, 10.000 muestras). Holdout tiene declaración preautorizada únicamente para R0 baseline; selección posterior exige registro de validation y cada variante se consume una vez.
- R0 BM25 se ejecuta sobre los tres splits. En validation: Evidence Completeness@8=0.575, Recall@10=0.625, MRR@10=0.3739, nDCG@10=0.4331, Document Mismatch=0.10. El holdout R0 es baseline predeclarado, no tuning ni confirmación de selección.
- R0 graph AUTO/ON y R6/R7/R8 con backend BM25 se registran solo como diagnósticos: no cumplen la definición R3-based y no pueden seleccionar arquitectura. AUTO no cambia Recall/Completeness; ON no mejora Recall/Completeness. El diagnóstico R6-BM25 mejora dev, pero requiere repetición correcta sobre R3 antes de cualquier conclusión. R8-BM25 degrada las métricas del diagnóstico.
- No existe reporte/configuración/index BGE-M3 reproducible en el repo; los valores proporcionados por el usuario se conservan como `user-reported`, no evidencia reproducida. Qwen dense, BGE, híbridos, reranker y R3–R8 reales quedan `GPU_BLOCKED` con prerequisitos exactos. Por tanto no se selecciona arquitectura ni se congela evidencia para B; tampoco se ejecuta confirmación oficial-50 posterior a selección.
- Se preservan resultados negativos/bloqueados y se prohíbe usar el sample oficial para desarrollo del benchmark interno. La siguiente decisión depende de comparaciones same-ID en la 4090, no de preferencia previa.
## 2026-09-28 — Corrección del abort-on-citation en `Pipeline.run`, consolidación de contexto de B

- **Hallazgo (Esteban, verificado contra el código real, no contra documentación):** con un decoder real conectado (`HFDecoder`, ya preparado en Gate 2-Prep), la primera cita sin respaldo generada por el modelo hace que `citation_guard` levante `CitationGuardError`. Esa excepción se propaga sin capturar a través de `Pipeline.run` hasta el bucle `for question in questions` de `run_experiment`, que la deja subir sin publicar `submissions.jsonl` para NINGUNA de las 992 preguntas (política registrada el 2026-09-27: "JSON/schema/citas inválidos abortan la corrida... no hay publicación de un JSONL final parcial"). El sábado, con un decoder real generando texto libre, esto es virtualmente seguro que ocurra al menos una vez en 992 ítems y dejaría al equipo sin entrega.
- **Corrección de arquitectura (requiere revisión cruzada de Luis, integrante A, antes del día de GPU):** se modifica únicamente `Pipeline.run` (`kingscode/reasoning/pipeline.py`) para capturar `CitationGuardError` y, solo ahí, sustituir la fila rechazada por una abstención construida con `abstention_row` sobre la misma evidencia — exactamente el mecanismo que el anexo B.5 del enunciado pide ("verificar que toda norma citada aparece en la evidencia y, si no, suprimir la citación"). **No se toca** `citation_guard`, `_answer` ni la función pública `answer()`: siguen lanzando `CitationGuardError` exactamente igual que antes para cualquier llamador directo, por lo que las pruebas de integridad de evidencia (`test_decoder_cannot_mutate_evidence_to_create_support`, todas las de `GuardSchemaTests`) no cambian. Tampoco se toca el comportamiento ante `SubmissionValidationError` (JSON/schema inválido sigue abortando la corrida sin publicar; ver `test_failed_run_is_registered_without_final_submission`), porque esa es una señal de bug del decoder, no de una cita jurídica cuestionable, y el equipo no ha revisado si debe tratarse igual.
- Se añade `test_unsupported_citation_falls_back_to_abstention_instead_of_aborting_batch` en `tests/test_reasoning.py` y `citation_guard_fallbacks` a las métricas de `run_experiment`, para que quede medible cuántas veces se activa esta salvaguarda en una corrida real.
- **Pendiente, NO aplicado en esta sesión (dejar para revisión de Luis):** `citation_guard` exige, cuando la cita incluye artículo, que ese artículo aparezca también de forma literal en el texto del pasaje (`kingscode/reasoning/guards.py`, filtro extra sobre `supporting_passages`). El evaluador oficial (`scripts/citations.py::score`) solo compara a nivel de cuerpo normativo (`bodies()`), ignorando el artículo por completo. Eso significa que hoy rechazamos como "sin respaldo" citas que el evaluador SÍ pagaría (ej. "artículo 5 de la Ley 1010 de 2006" cuando el pasaje recuperado es el artículo 1 de esa misma ley). Bajar esa exigencia a nivel de cuerpo aumentaría el techo de puntaje de citas sin debilitar la protección real, pero es un cambio a la semántica de coincidencia que Luis diseñó y probó extensamente (16+ tests en `GuardSchemaTests`); se documenta aquí para decidirlo en conjunto, no se aplica unilateralmente.
- **Consolidación de contexto de B:** se integran al árbol canónico los materiales sueltos que traía Esteban en `kingscode_b/` y `kingscode_claude_context_files/` (ambos sin commitear, fuera de la estructura del repo): `CLAUDE.md`, `.claude/commands/`, `docs/B_FINDINGS_2026-09-28.md`, `docs/B_EXTENSION_PLAN.md`, `tools/analyze_citation_ceiling.py` y dos carpetas de prototipos de referencia (`docs/reference_b_prototype/`, `docs/reference_esteban_prototype/`) que documentan ideas pero no se importan al pipeline competitivo. Se construye `interfaz/app.py` (Streamlit) contra el pipeline real (`kingscode.reasoning.Pipeline` + `kingscode.Retriever`), con la identidad visual de Software Colombia, cubriendo el entregable de interfaz que seguía en cero. Se corrige `docs/TEAM_SPLIT.md`, que describía tareas de A/B ya completadas como si fueran "ahora".
