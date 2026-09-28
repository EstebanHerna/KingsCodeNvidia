# Roadmap KingsCode v0.5 — trabajo paralelo A/B

## Gate 0 — integridad [COMPLETADO]
Starter pack verificado y hashes oficiales conservados.

## Gate 1A — Corpus v0 [A, baseline completado]
- descargar fuentes oficiales prioritarias;
- raw + clean + passages;
- graph nodes/edges;
- manifest/provenance.

163 fuentes adquiridas; baseline y verificaciones en `../CORPUS.md` y `VERIFICATION.md`. La ampliación, vigencia y resolución de ambigüedades siguen antes del freeze.

## Gate 1B — Harness pre-GPU [B]
- normalizador de consulta;
- graph router v0;
- schema validator;
- citation guard;
- evaluator runner;
- experiment registry.

A y B ocurren en paralelo.

## Gate 2A — Retrieval baseline [A]
BM25 -> dense -> RRF -> reranker -> Graph OFF/AUTO.

BM25 y grafo OFF/AUTO/ON medidos. Dense/RRF/reranker implementados y probados con pesos reales en un índice pequeño; benchmark de todo el corpus pendiente de la 4090. Ver `MEMBER_A_RUNBOOK.md` para comandos exactos.

## Gate 2B — CUDA/4090 + decoder harness [B]
Diagnosticar máquina, instalar según hardware real, smoke test e inferencia mínima.

## Gate 3 — Integración A+B
Conectar retrieval real al harness de B y producir primeras 50 respuestas end-to-end.

## Gate 4 — Bakeoff
- retrievers/chunking/grafo;
- decoder Qwen vs ALIA vs Salamandra;
- una variable por experimento.

## Gate 5 — Fine-tuning condicional
- retrieval bajo: reranker FT/hard negatives;
- retrieval alto + generation baja: considerar QLoRA;
- si no agrega mejora medible, no entrenar.

## Gate 6 — Performance
Objetivo: margen amplio bajo el presupuesto total de 992 preguntas. Registrar p50/p95 y fallos.

## Gate 7 — Deliverables
UI, corpus/índice, reporte, informe, video, README, comando único.

## Gate 8 — Freeze
Congelar corpus, índice, grafo, modelos, prompts y configs exactos.

## Gate 9 — Sábado
Ingresar 992, ejecutar, validar, entregar y regenerar en vivo con el mismo freeze.
