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
