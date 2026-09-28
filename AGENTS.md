# AGENTS.md — KingsCode Hackathon 2026

Este archivo es la guía operativa para cualquier agente humano o de IA que trabaje sobre este repositorio.

## 1. Orden obligatorio de lectura
Antes de hacer cambios:
1. `START_HERE.md`
2. `docs/KINGSCODE_MASTER_KNOWLEDGE.md`
3. `docs/KINGSCODE_STATE.json`
4. `docs/DECISION_LOG.md`
5. `docs/TEAM_SPLIT.md`
6. `docs/ARCHITECTURE_V05.md`
7. `config/strategy.json`

Si existe contradicción, manda este orden:
**enunciado oficial > archivos oficiales del starter pack > MASTER_KNOWLEDGE > STATE > DECISION_LOG > docs auxiliares**.

## 2. Reglas que no se negocian
- No modificar los archivos oficiales del starter pack salvo copia explícita en otra ruta.
- No introducir modelos cerrados en el pipeline competitivo, reformulación, reranking, generación ni creación de datos sintéticos.
- No usar respuestas esperadas ni el banco de evaluación como material indexado.
- No editar manualmente respuestas finales después de ejecutar el pipeline.
- La salida final debe cumplir `schema/submission.schema.json`.
- Temperatura final: `0`; ejecución determinista y reproducible.
- Toda cita emitida debe estar sustentada en `pasajes_recuperados`.
- El corpus debe provenir de fuentes jurídicas públicas/oficiales y conservar trazabilidad.
- No guardar secretos/API keys en Git, docs o artefactos.

## 3. Arquitectura vigente: v0.5 Graph-Aware Hybrid RAG
Fast path:
`query -> normalización -> BM25 + dense -> RRF -> reranker -> decoder -> citation_guard -> JSON`

Graph path selectivo:
`query/pasajes -> detección de relación -> expansión del grafo -> reranker -> decoder`

El grafo existe desde Corpus v0. No se obliga a recorrerlo para todas las preguntas.

## 4. Roles actuales
### Integrante A — Knowledge Layer / Corpus / Graph / Retrieval
Owner de:
- adquisición y trazabilidad de fuentes;
- parsing y normalización;
- chunking jurídico estructural;
- nodos/edges del grafo;
- BM25, embeddings, RRF, reranker;
- métricas de retrieval y cobertura;
- `CORPUS.md` y `corpus_manifest.json`.

Interfaz que debe ofrecer:
`retrieve(question, k, graph_mode="auto") -> passages`

### Integrante B — Query/Reasoning Layer / Generation / Evaluation / Delivery
Owner de:
- normalizador de consulta y expansión terminológica controlada;
- política de routing para activar o no el grafo;
- bakeoff de decoders;
- prompts por formato;
- JSON estricto;
- citation guard y abstención;
- `evaluate.py`, latencia, VRAM y experiment tracking;
- UI, reproducibilidad, comando único y entregables.

Interfaz principal:
`answer(question, passages, format) -> submission_row`

### Compartido
- criterios de evaluación;
- integración A↔B;
- experimentos end-to-end;
- freeze de versiones;
- revisión cruzada antes de aceptar cambios de arquitectura.

## 5. Contratos entre A y B
Cada passage debe incluir como mínimo:
- `passage_id`
- `doc_id`
- `text`
- `norm_name`
- `article` si aplica
- `source_url`
- `hierarchy_path`
- `graph_node_ids`
- scores de retrieval disponibles

B no debe depender de detalles internos del índice. A no debe depender del decoder.

## 6. Política de experimentos
- Cambiar una variable por experimento siempre que sea posible.
- Registrar: versión corpus, retrieval config, decoder, prompt, score, Recall@k, MRR, latencia y observaciones.
- No hacer fine-tuning de decoder hasta que retrieval sea suficientemente alto y el error residual sea realmente generativo.
- Primer fine-tuning candidato si hace falta: reranker con hard negatives.
- Comparar Graph off vs Graph auto antes de mantener cualquier expansión costosa.

## 7. Definición de hecho completado
Una tarea no se considera terminada hasta que:
1. pase validación/smoke test;
2. no rompa los hashes oficiales;
3. tenga resultado reproducible;
4. actualice documentación si cambia una decisión;
5. actualice `KINGSCODE_STATE.json` si cambia el siguiente paso;
6. registre decisiones en `DECISION_LOG.md` si son arquitectónicas.

## 8. Qué debe hacer un agente al terminar un turno de trabajo
Actualizar, si aplica:
- `docs/KINGSCODE_MASTER_KNOWLEDGE.md`
- `docs/KINGSCODE_STATE.json`
- `docs/DECISION_LOG.md`
- `config/strategy.json`
- el documento específico del rol.

Dejar explícito:
- qué cambió;
- qué se verificó;
- qué falta;
- cuál es el siguiente comando/tarea exacta.

## 9. Estado actual
Versión: **v0.5**.
Fase: **Gate 2-Prep preparado; pruebas nuevas y ejecución GPU pendientes**.
- A: Corpus v0 + grafo + retrieval baseline.
- B: Gate 1B con dummy verificado históricamente; backend real, prompts, modelos fijados y comandos de bakeoff preparados en Gate 2-Prep, aún sin ejecutar.

Protocolo para continuar en la GPU: leer `docs/GPU_DAY_RUNBOOK.md`, `docs/MODEL_LOCKS_GATE2.md`, `config/decoder_bakeoff.json` y `config/experiment_matrix.json`. No sustituir `smoke` (dummy). Los experimentos reales usan evidencia congelada, snapshots locales verificados y BF16 primero; un fallback exige registrar el OOM y mantener las demás variables.

En esta entrega el usuario pidió expresamente no ejecutar pruebas. Se dejan preparadas dos verificaciones para el siguiente entorno; no presentar los 60 tests históricos como validación de Gate 2-Prep ni marcar CUDA/bakeoff completados sin resultados reales.

No asumir que CUDA ya está configurado.
