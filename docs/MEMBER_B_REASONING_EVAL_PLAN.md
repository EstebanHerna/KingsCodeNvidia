# Integrante B — Query / Reasoning / Generation / Evaluation / Delivery — v0.5

## Objetivo
Convertir evidencia recuperada por A en respuestas válidas, grounded, reproducibles y competitivas, y medir cada cambio con el evaluador oficial.

## B0 — harness independiente de GPU
Construir interfaces que funcionen primero con passages mock o fixtures reales:
- `normalize_query(question)`
- `route_graph(question, flat_passages) -> off|auto|on`
- `answer(question, passages, format)`
- `validate_submission(row)`
- `citation_guard(row, passages)`
- `run_eval(submission)`

## B1 — query normalizer
Normalizar sin destruir términos jurídicos exactos. Detectar y preservar:
- `Ley X de YYYY`;
- `Decreto X de YYYY`;
- `Artículo N`;
- sentencias y radicados;
- nombres de códigos;
- autoridades/corporaciones;
- expresiones de vigencia, derogación, modificación y remisión.

Expansión terminológica controlada, no multi-query libre por defecto.

## B2 — graph router v0
Determinista al comienzo. Activar grafo cuando existan señales como:
- remisiones;
- cambios normativos/temporalidad;
- modificación/derogación/reglamentación;
- necesidad explícita de jerarquía;
- insuficiencia del fast path.

Medir Graph OFF vs AUTO antes de sofisticarlo.

## B3 — decoder bakeoff
Con retrieval congelado, comparar:
1. Qwen3-8B;
2. ALIA-es-legal-administrative-7B-Instruct;
3. Salamandra-7B;
4. Llama 3.1 8B solo como control si hay tiempo.

Mismas preguntas, mismos passages, mismo prompt base, temperatura 0.

## B4 — salida y guardas
- JSON estricto según schema;
- no permitir citas fuera de `pasajes_recuperados`;
- abstener si evidencia insuficiente;
- no editar manualmente output del modelo.

## B5 — evaluación
Registrar por experimento:
- score oficial;
- RAGAS cuando corresponda;
- errores de schema;
- citas no respaldadas;
- abstenciones;
- latencia;
- VRAM;
- tokens de contexto;
- config exacta.

## B6 — entrega
Owner de:
- interfaz;
- comando único;
- README de ejecución;
- artefactos de reproducibilidad;
- empaquetado final;
- video/informe junto con A.

## Contrato con A
B consume el contrato de passage; no lee estructuras internas de BM25/FAISS/grafo directamente salvo para debugging acordado.
