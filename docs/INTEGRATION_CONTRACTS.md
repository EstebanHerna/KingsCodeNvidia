# Contratos de integración A ↔ B

## Passage contract
El formato canónico se rige por `config/corpus_passage.schema.json` y debe ser estable.

Campos conceptuales mínimos:
`passage_id`, `doc_id`, `text`, `norm_name`, `article`, `source_url`, `hierarchy_path`, `graph_node_ids`, scores.

## Retrieval result
A entrega una lista ordenada y trazable. No debe incluir respuestas esperadas ni campos derivados del banco de evaluación.

Implementación disponible: `from kingscode import retrieve, Retriever`. El backend predeterminado es BM25; dense/hybrid y reranker son opciones explícitas. `graph_router` permite inyectar la política de B. La ausencia de pesos o un índice inconsistente es un error explícito.

El texto incluye `text_prefix` con norma/jerarquía tomada de la fuente. Los offsets `clean_start`/`clean_end` delimitan únicamente el contenido del archivo clean. Cada resultado incluye scores por etapa, hash del corpus, URL/hash de origen y nodos/evidencia del grafo. Solo devuelve pasajes elegibles: excluye históricos explícitos y numeraciones ambiguas. Véase `MEMBER_A_RUNBOOK.md` para la conversión al schema oficial.

## Generation result
B devuelve una fila válida para el schema oficial. Toda cita debe poder verificarse contra passages.

## Reproducibility contract
Cada corrida debe fijar:
- corpus version/hash;
- graph version/hash;
- retrieval config;
- decoder + revision;
- generation config;
- prompt version;
- timestamp/result path.

## Failure semantics
- evidencia insuficiente: abstención cuando corresponda;
- schema inválido: fallo bloqueante;
- cita sin respaldo: fallo bloqueante/corrección automática determinista;
- retrieval vacío: registrar y no inventar evidencia.

## Gate 1B disponible

Importar B desde `kingscode.reasoning`: `Question`, `normalize_query`, `route_graph`, `answer`, `citation_guard`, `validate_submission`, `run_eval`, `Pipeline`, `RetrieverGraphRouter`. El namespace original de A sigue intacto.

- `normalize_query(str)` devuelve un objeto con original/normalizado/texto de búsqueda, referencias, señales y expansiones. Solo `retrieval_text` se entrega a A.
- `route_graph(question, flat_passages)` devuelve un string. **No pasarlo directamente como callback de A**: `"off"` sería truthy. `RetrieverGraphRouter` enlaza la decisión al texto de consulta y devuelve un booleano; `Pipeline` coordina ambos pases.
- `answer(Question, passages, format)` conserva el ID real. Para consultas ad hoc, acepta texto y `question_id` (0 por defecto). No acepta registros del banco con etiquetas.
- El backend dummy siempre se abstiene. El enum oficial de opción múltiple exige un marcador A/B/C/D incluso con abstención: se usa A y se declara explícitamente que no es una respuesta elegida.
- `pasajes_recuperados` contiene el texto exacto y metadata de procedencia de A. Se omiten offsets oficiales opcionales para no atribuir `text_prefix` al intervalo clean. La guarda solo admite evidencia que coincida con los pasajes realmente suministrados.
- Las salidas/decisiones son deterministas. Los tiempos se guardan en la traza/registro para no alterar el JSONL final entre repeticiones.

Detalles y ejemplo completo: `MEMBER_B_RUNBOOK.md`.

## Gate 2-Prep — contrato preparado, sin ejecución real

`kingscode.generation.hf_decoder.HFDecoder` implementa el mismo `Decoder.generate(Question, passages, PromptSpec, generation)`. Importar el módulo no carga librerías neuronales ni pesos. El modelo emite un JSON intermedio con abstención/campos del formato; el adaptador adjunta identidad y evidencia literal, sin permitir al modelo fabricarlas. `answer` aplica después las guardas originales. Un output inválido/OOM detiene el experimento sin fallback automático.

El descriptor genérico de prompt de Gate 1B se conserva. El backend real materializa explícitamente `grounded-formats-v2`, registrado en su configuración/experimento. Las reglas del router no cambian ni se convierten en prompts.

Para comparar decoders, A produce rankings mediante su API pública y el experimento de retrieval congela ocho evidencias por pregunta. B consume ese archivo autenticado por hashes; no carga índices ni mantiene modelos de retrieval en VRAM durante generación. Sus tiempos de decoder y los de retrieval se reportan por separado. Mismo freeze, configuración y prompt para D1–D4; cambios de precisión/contexto son experimentos distintos.
