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
