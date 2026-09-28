# Roadmap KingsCode v0.5 — trabajo paralelo A/B

## Gate 0 — integridad [COMPLETADO]
Starter pack verificado y hashes oficiales conservados.

## Gate 1A — Corpus v0 [A, baseline completado]
- descargar fuentes oficiales prioritarias;
- raw + clean + passages;
- graph nodes/edges;
- manifest/provenance.

163 fuentes adquiridas; baseline y verificaciones en `../CORPUS.md` y `VERIFICATION.md`. La ampliación, vigencia y resolución de ambigüedades siguen antes del freeze.

## Gate 1B — Harness pre-GPU [B, completado con dummy]
- normalizador de consulta;
- graph router v0;
- schema validator;
- citation guard;
- evaluator runner;
- experiment registry.

A y B ocurren en paralelo.

Implementación y reproducción en `MEMBER_B_RUNBOOK.md`. El smoke usa A real y un dummy con abstención total; no cuenta como decoder/bakeoff ni ejecución competitiva.

## Gate 2-Prep — preparado, pendiente de ejecutar pruebas

Locks de los cuatro decoders, configuración BF16/bakeoff, backend lazy, prompts, diagnóstico/plan, preparación de modelos, GPU smoke y matriz de experimentos implementados. No se ejecutaron pruebas ni smokes por la instrucción final del usuario; no se valida GPU ni bakeoff. Ver `GPU_DAY_RUNBOOK.md` y `MODEL_LOCKS_GATE2.md`. Gate 1B mantiene su dummy sin cambios funcionales previstos; su reproducción se deja preparada para comprobarla en el siguiente entorno.

## Gate 2A — Retrieval baseline [A]
BM25 -> dense -> RRF -> reranker -> Graph OFF/AUTO.

BM25 y grafo OFF/AUTO/ON medidos. Dense/RRF/reranker implementados y probados con pesos reales en un índice pequeño; benchmark de todo el corpus pendiente de la 4090. Ver `MEMBER_A_RUNBOOK.md` para comandos exactos.

## Gate 2B — CUDA/4090 + decoder harness [B]
Diagnosticar máquina, instalar según hardware real, smoke test e inferencia mínima. Comandos preparados en `GPU_DAY_RUNBOOK.md`; ejecución real pendiente.

## Gate 3 — Integración A+B
Conectar retrieval real al harness de B y producir primeras 50 respuestas end-to-end.

Integración técnica de las 50 filas comprobada con dummy. Las respuestas jurídicas con decoder real siguen pendientes.

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
