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

## 2026-09-28 — T3/T5/T7 de `docs/B_EXTENSION_PLAN.md`

- **T3, política de abstención mínima:** `kingscode/reasoning/policy.py` gana `blocking_reasons(assessment, format)`, que separa razones "duras" (vacío/conflicto/evidencia no vigente) de razones blandas (referencia exacta ausente, consulta ambigua, vigencia no certificada, solapamiento léxico débil). `multiple_choice` nunca bloquea antes del decoder — adivinar entre opciones dadas supera a abstenerse incluso al azar, según la propia aritmética del enunciado (sección 6.1). Texto libre conserva el bloqueo solo para las razones duras; el resto pasa a `trace["warnings"]` y el decoder lo intenta, protegido por la red de seguridad de citas del punto anterior. `assess_evidence(...).sufficient` y `route_graph` (que lo consume para decidir expansión de grafo) no se tocaron: siguen considerando todas las razones, es un concepto distinto al de bloqueo de abstención.
- **T5, recuperación con opciones en cerradas:** `pipeline.py` gana `query_variants()` (una consulta por opción para `multiple_choice`, orden determinista) y `rrf_merge()` (fusión por rango recíproco sobre los pasajes que A ya devolvió, sin tocar sus internals ni mutar los pasajes). Con una sola variante (cualquier formato sin opciones) la llamada a `retrieve()` es idéntica byte a byte a la de antes. No se pudo medir el efecto real en recall/exactitud: requiere el corpus real, no disponible en esta máquina.
- **T7, entregables sin GPU:** `run.sh` (comando único: instala dependencias, exige o construye `corpus/`, corre tests, Gate 1B smoke y `scripts/evaluate.py --split sample`), `Dockerfile` + `.dockerignore` para la verificación de reproducibilidad en contenedor limpio, y secciones nuevas en el README (`## Comando único de reproducción`, `## Corpus e índice`). No se pudo ejecutar de punta a punta en esta máquina por falta de `corpus/` local — se verificó sintaxis de bash y del snippet Python embebido únicamente.
- **T6, throughput/concurrencia, deliberadamente no implementado:** requiere medición real (GPU + corpus) para no introducir bugs silenciosos en la guarda/citas deterministas; se deja documentado como bloqueado en vez de escribir concurrencia sin poder correrla, siguiendo la regla propia de `CLAUDE.md` de medir antes/después de cualquier cambio de calidad.
- Verificado con `python -m unittest discover -s tests -v`: 91 tests, OK (5 se saltan sin `corpus/` local). Nuevos tests: `test_multiple_choice_never_pre_blocks_on_soft_evidence_reasons`, `test_free_text_still_hard_blocks_on_empty_retrieval`, `test_query_variants_one_per_option_sorted_else_base_only`, `test_rrf_merge_boosts_passages_ranked_in_more_lists`, `test_multiple_choice_fans_out_one_retrieve_per_option_and_fuses_rrf`.

## 2026-09-28 — A v0.2 después del freeze GPU (60ebf7e)

Se reconoce el freeze RTX 4090 y se cierra validation v1 al tuning. Search V2 muestra empates con locator incluso sin boost de metadatos. Se productiviza parsing → identidad canónica → fragmentos → unión de candidatos antes del reranker; no se selecciona metadata_scale=1.25. La clase Retriever conserva defaults históricos para replay; la función pública añade locator y desactiva expansión AUTO en su perfil CPU; ON explícito conserva la expansión acotada del contrato. Los pesos neuronales siguen siendo explícitos.

Se preserva corpus-v0.1 byte a byte; corpus-v0.2 será un árbol separado. Benchmark v2 empieza con schema/piloto técnico determinista y una cola humana para escenarios/temporalidad/excepciones. Ningún modelo cerrado redacta preguntas competitivas. R0–R8 siguen siendo ablaciones, no un catálogo excluyente de arquitecturas finales. Composición, selección inmutable, confirmaciones autorizadas y freeze top 8 se decidirán con nueva evidencia v2. No se cambian B ni sus prompts.


## 2026-09-29 — Benchmark v2 independent source gate and international layer

- Se cierra benchmark v1 a tuning. El piloto v2 derivado de captions del corpus es solo smoke técnico: seis exposiciones DEV registradas, cero preguntas independientes, cero gold v2 independiente y cero SEALED_EVAL. Sus métricas no seleccionan arquitectura.
- El schema v2 admite RETRIEVAL_GOLD con conjuntos mínimos alternativos y END_TO_END_ONLY sin etiquetas de retrieval; las filas actuales se identifican como TECHNICAL_PILOT_ONLY. La recuperación no recibe gold.
- Las URLs oficiales de los PDFs ICFES localizados retornaron 404 en verificación directa; SIRNA confirma que existe una guía, sin banco público de ítems verificado. No se inventan preguntas para cumplir cuotas.
- Se añade inventario internacional selectivo de candidatos CAN/OIT/interamericano. Ratificación o aplicabilidad permanece pendiente de verificación para cada instrumento; no se indexa automáticamente. Benchmark internacional: cero ítems.
- Corpus-v0.1 queda inmutable. Corpus-v0.2 tiene cuatro documentos provisionales y las remediaciones G01/G02/C01/P02/P01/D01 aún no están completas; cada cambio requiere fuente primaria, fixture y prueba.
- Sin gold independiente no existe baseline útil ni distribución de fallos para escoger experimento. La siguiente ejecución será un baseline no ajustado sobre DEV externo revisado.

## 2026-09-29 — Diagnósticos de vistas y estado de remediación A v0.2

- El checkout remoto de `feat/member-a-corpus-v02-locator` estaba limpio en 790bf85. La suite completa pasó con 210 tests después de proporcionar `jsonschema==4.26.0` desde un directorio temporal ignorado; la primera invocación sin esa dependencia falló al importar siete módulos/casos.
- Se implementan métricas puras para Oracle Multi-View Recall, Fusion Loss y Graph Recovery Rate sobre `minimal_evidence_sets`, incluyendo alternativas. Las pruebas verifican alternativas, pérdida de fusión y recuperación condicionada a misses iniciales. No hay ranking/gold independiente; no se reportan valores empíricos ni baseline.
- Los seis hallazgos G01/G02/C01/P02/P01/D01 siguen pendientes. Se registra explícitamente qué evidencias no están en el snapshot. No se cambia v0.1 ni se intenta arreglar el parser por heurística. El grafo v0.2 permanece provisional: 29 `CONTIENE`, cero aristas semánticas activas y cero relaciones revisadas.
- El piloto existente contiene 12 casos corpus-derivados, no independientes ni seleccionables. No se amplía a 20–30 hasta revisar la estructura de las fuentes v0.2; esto evita convertir errores potenciales de parsing en diagnósticos supuestamente correctos.
- No se autoriza un experimento de retrieval: todavía no hay preguntas independientes aceptadas en DEV ni distribución de fallos. Próximo paso recomendado: obtener fuentes oficiales faltantes para las correcciones estructurales y continuar intake de assessment externo accesible; luego revisar bytes/fixtures antes de parser y benchmark.


## 2026-09-29 — Corpus v0.2 source-backed parser repairs and assessment intake update

- Preserve four primary legal sources in `corpora/corpus-v0.2/raw/` with URL, TLS/HTTP metadata and SHA-256 recorded in the v0.2 manifest. These are audit sources; the existing four-document/72-passage v0.2 snapshot was not rebuilt. Corpus v0.1 remains unchanged.
- Add v0.2-only corrections for publisher TOC rows (G02), repeated decision headings (C01), split statute headings (P02), and article termination at a major hierarchy heading (P01). Regression fixtures are checked against exact extracted blocks from the preserved bytes. The parser keeps PDF-specific safeguards when operating through the sanitized-block path.
- Leave G01 semantic relationships and D01 document identity review open; no semantic edges or automatic content-based document merges are activated.
- Official ICFES PDF origins remained unavailable; record indexed-only evidence without ingesting questions. The current SIRNA guide contains illustrative examples but its terms prohibit reproduction/transformation; no assessment examples are copied into benchmark assets. An ICFES 2021 source-rendering exposure is logged as validation candidate only.
- No independent retrieval gold was admitted. The baseline gate remains closed until at least 10 reviewed independent items exist.


## 2026-09-29 — Member A official-source runtime block and G01 candidate review

- The original ICFES Gestión del Conflicto 2026 and Comunicación Jurídica 2021 PDFs, current official module candidates, and the official toolbox landing URL were retried using browser navigation and browser-compatible headers. HTTP 404 in this runtime is recorded as `RUNTIME_ACQUISITION_BLOCKED`, because official ICFES index entries confirm the resources exist; indexed content is not accepted as original bytes.
- Added a hash-gated local intake helper targeting ignored `tmp/official-source-intake/`. It checks the recorded source ID, official ICFES host, input path, PDF signature and SHA-256 before indicating that local extraction may begin. Hash verification alone does not establish authenticity or usage rights.
- Reviewed the seven G01 candidate edges against the exact official containing-source text and recorded source URLs/hashes. Rejected the seven wrong containing-passage targets. The corrected target/modifier claims remain unresolved until their referenced legal instrument bytes are acquired; zero semantic edges are active.
- Added a D01 regression for equal content hashes across distinct canonical legal identities; broader provenance audit remains open.
- Independent extracted questions and retrieval-gold remain zero; no baseline or retrieval experiment is justified. No v0.1 or Member B files changed.

- Validación de esta continuación (segunda pasada final): 226 tests PASS; `python tools/benchmark_v2.py check` PASS con 10 hashes y holdout sin parsear; `python tools/verify_member_a_v02.py` PASS con 19 archivos oficiales, 326 archivos raw/clean v0.1 y 18 hashes v0.2. Sin GPU ni baseline.
- Precisión de adquisición: el PDF ICFES Gestión del Conflicto 2026-2 de mayo es una guía de orientación listada en el catálogo oficial, no un cuadernillo de preguntas. Se excluye de la intake de ítems; la fuente de preguntas original de febrero permanece confirmada por indexación oficial pero bloqueada por 404.
- Validación tras separar el PDF de orientación: tercera suite completa de esta continuación, 226 tests PASS; `benchmark_v2.py check` PASS (10 hashes, no holdout); verificador de snapshot PASS.


## 2026-09-29 — KC-COL-IR-v0.1 institution-family isolation

- Create a separate cross-institution benchmark: Externado DEV; Universidad Libre validation-only; ICFES/SIRNA sealed/future. Never use institution family to fill another split. Topic guides count for coverage only.
- Mechanical acquisition of the official 2011 Externado Civil Procedure bank yields 270 numbered candidates, but extraction glyph damage means exact wording remains unverified. Do not accept or run retrieval on them until human transcription/option QA and independent primary-law/temporal review.
- Hash-sample 30 before retrieval. Freeze the >=10 accepted DEV retrieval-gold gate. First comparison uses C0 BM25/C1 Qwen dense/C2 RRF/C3 hybrid+Qwen reranker, same candidate depth, graph OFF. No GPU execution in this acquisition session.
- Historical Universidad Libre sources are `VALIDATION_CANDIDATE`; URLs currently return HTML, not verified PDF bytes. Do not parse/score until DEV architecture selection.


## 2026-09-29 — Prioridad de fuentes recientes para KC-COL-IR-v0.1

- Reorientar DEV candidato hacia JEP: la página oficial de preguntas contiene 62 ítems de la tercera edición (2025), aunque la página institucional ya anuncia la cuarta edición 2026. No fechar los ítems 2025 como 2026. La edición JEP 2026 queda discovery-only hasta que publique preguntas verificables.
- Congelar 30 ítems JEP por hash antes de retrieval, con texto/respuesta en pool local ignorado. Todos siguen `NEEDS_HUMAN_REVIEW` y `UNCERTAIN`; primero separar aclaraciones puramente fácticas, cuestiones jurídicas no respondidas y casos útiles para retrieval implícito. Sin gold admitido.
- Mover el muestreo Externado 2011 a reproducibilidad-only, preservando los 30 IDs, selección y pool sin reemplazarlo ni mezclarlo con DEV.
- Registrar Javeriana Moot Seguros 2026 como validation candidate. Solo se verificó firma/hash de un PDF oficial de respuestas; no se parseó ni se inspeccionó rendimiento. La publicación advierte que algunas respuestas pueden inferirse del caso o reservarse al análisis de los equipos.
- Mantener baseline/CUDA bloqueados hasta >=10 gold DEV recientes aceptados con evidencia primaria y revisión temporal. No seleccionar ítems por métricas de retrieval.


## 2026-09-29 — KC-COL-IR gold is corpus-independent

**Decision:** establish accepted gold only from independently verified external primary evidence and frozen minimal evidence sets; evaluate frozen-corpus coverage as a separate annotation. A valid accepted gold may be COMPLETE, PARTIAL, MISSING, or AMBIGUOUS. Ranking metrics use only COMPLETE cases; coverage and failure taxonomy use all accepted gold. `corpus_missing` is never converted into a ranking failure. No retrieval output may guide item selection, evidence-set design, or review.

**Current review:** all 30 deterministic JEP 2025 items were dispositioned from exact local frozen question/response bytes. Thirteen remain retrieval-gold candidates pending exact primary sources; five are explicit-reference; three factual-only; six strategy/legal questions receive no substantive official answer; three answers are insufficient. No packets accepted because sources cited by the questions were not independently verified. The acquired Case 01 Resolution No. 02 (2022) and official JEP 2025 expediente archive were hashed and identity-checked but are not substitutes for the referenced SRVR-012/voluntary-version/Auto 023 materials. Gold remains 0, no corpus coverage denominator exists, and the baseline/CUDA gate remains closed.


## 2026-09-29 — Corrección de procedencia CUJ 2026 y revisión de gold KC-COL-IR

- La página oficial actual `/preguntas` y el paquete SeRVR corresponden a la cuarta edición CUJ 2026. La tercera edición CUJ 2025 fue SDSJ; el ZIP 2025 adquirido se conserva solo como prueba de procedencia y queda marcado `NOT_SOURCE_FOR_CUJ_2026_GOLD`.
- Caveat de procedencia: `/preguntas` es contenido mixto y conserva boilerplate obsoleto “2025 / Tercera Edición”. La atribución a CUJ 2026 se basa en la identidad del caso y la coincidencia de materiales exactos con el paquete oficial 2026; el paquete SDSJ 2025 no coincide. Se conservan los mismos 30 IDs/números originales, sin remuestreo.
- Se migraron los 30 IDs a `JEP-CUJ-2026-Qnnn`, conservando `legacy_question_id`, los mismos números de ítem y el SHA original de selección. No se volvió a muestrear. Externado 2011 continúa solo para reproducibilidad y Javeriana 2026 sigue sin parsear ni inspeccionar.
- El ZIP oficial CUJ 2026 (157,859,322 bytes, SHA-256 `3f9dc1765e8ea18588c13a48e1785b506f6a0c06eef3743057e2d34097d9b101`) contiene 18 miembros hash-verificados, incluida la resolución hipotética SRVR-012 de 147 páginas y las versiones voluntarias de Ainhoa y Laureano. No sustituirla por la Resolución real No. 02 de 2022. El Auto 023 independiente no aparece como miembro separado.
- Disposición de los 30 ítems: 9 `ACCEPTED_RETRIEVAL_GOLD`, 7 `PENDING_PRIMARY_EVIDENCE`, 8 `REJECTED_INSUFFICIENT_AUTHORITATIVE_ANSWER`, 6 `REJECTED_NOT_RETRIEVAL`. Q045/Q049 quedan en el grupo duplicado `EL_BILLAR_DATE`. El objetivo de 10 no justifica aceptar evidencia incompleta.
- Los 9 gold tienen evidencia externa primaria separada de IDs del corpus; el inventario/texto completo de los 26,558 pasajes de corpus-v0.1 no contiene las fuentes/personas del caso. Cobertura: 0 COMPLETE, 0 PARTIAL, 9 MISSING, 0 AMBIGUOUS; ranking_n=0.
- Se corrigió el runner para exigir >=10 gold y, separadamente, >=10 gold COMPLETE antes de ranking/CUDA. El test cubre 30 candidatos, 10 gold válidos y 20 candidatos pendientes, así como exclusión de IDs de evidencia externa de métricas puras. Solo verificaciones CPU; retrieval y CUDA no ejecutados.

## 2026-09-29 — CUJ expansion and controlled corpus profile

- Preserved the original 30 selected CUJ item numbers and froze `EXPANSION_BATCH_1` as the next 10 IDs by the same SHA-256 ordering before reading their content. The pool hash is `af07237db321115562da4d64527c675d2bb99fe49c730b5f1ebcf2ac3bf85476`; expansion selection hash is `dc1332cb1477f96ea2652f2699befc317f4e053b67e8b8d987ef9397ecf13131`. All 10 received separate dispositions; only Q025 was accepted.
- Gold now totals 10 and GOLD_GATE is unlocked. IDs: Q009, Q012, Q013, Q025, Q030, Q031, Q037, Q043, Q045 and Q049. Competitive corpus-v0.1 independently remains MISSING for all 10 (100% missing rate).
- Defined `KC-COL-IR-CUJ2026-CONTROLLED-v1` from all six textual PDFs in the complete official 2026 ZIP, not from the gold-document list. The 18-member archive inventory includes two excluded MP3s and all metadata members; extraction verified 191 physical pages and 190 nonempty page passages. Archive SHA-256: `3f9dc1765e8ea18588c13a48e1785b506f6a0c06eef3743057e2d34097d9b101`; in-memory passage hash: `019dee8a805e87fbacfce45cd448f4b538b921d6d7c5aa7ff3a82a5472a894ef`.
- Separate external evidence units, controlled page mappings, and competitive corpus coverage in independent ledgers. Controlled mappings are page/source verified for 10/10, but passage file is not materialized in this worktree; ranking execution remains locked, ranking_n=0 in the manifest, and CUDA_READY=false. No retrieval, neural ranking, CUDA or validation inspection was performed.

## 2026-09-29 — Materialized CUJ controlled profile (pre-ranking freeze)

- Materialized the already-frozen six-PDF CUJ 2026 corpus under ignored `tmp/kc_col_ir_v0.1/controlled_cuj2026_v1/`; the 18-member archive was fully inventoried, including two excluded MP3s and archive metadata. No source bytes are tracked.
- Verified 191 physical PDF pages and 190 nonempty page passages. `passages.jsonl` SHA-256 is `c942cdfe6ec7f0c88ea0ebe4977540a99b93d98d3404b2972f9609b4499b3a7c`; runtime manifest SHA-256 is `5bcb56f772c6f502d79c41cfef684e61e82b7cd13c7c3c442e35c73730974d3f`; BM25 index SHA-256 is `277184f3a954de79746589b1e28c932cd2d557bfc2a3e52fe9ab130d7e406a87`; corpus fingerprint is `9569be4855bc9223eb346280de21d14b080da8e9b73aa9353175d59345492056`.
- The previously reported `019dee8a...` hash is reproduced exactly by serializing the same passage rows without the explicit `member_index` provenance field. The new canonical JSONL hash includes `member_index`; the earlier value was preserved as a distinct schema/hash record, not overwritten.
- All 24 external-evidence mappings across 10 accepted questions resolve to 18 unique real passages with matching source member, document and physical page; all 10 minimal evidence sets resolve. Competitive corpus-v0.1 remains 10/10 MISSING (Missing Rate 1.0).
- CPU BM25 construction and reopen through `Retriever` passed; tokenizer version is `accent-fold-unicode-words-1`. `GOLD_GATE=UNLOCKED`, `RANKING_GATE=UNLOCKED` (ranking_n=10), `retrieval_benchmark_ready=true`; `CUDA_READY=false` and `cuda_execution_started=false`. No retrieval query, C0-C3, dense model, reranker, CUDA or validation inspection ran.
