# START HERE — KingsCode v0.5

## Para Claude Code
`CLAUDE.md` (importa `AGENTS.md` y fija el orden de lectura), luego `docs/B_EXTENSION_PLAN.md` y `docs/DECISION_LOG.md` para lo más reciente. Comandos: `/b-contexto`, `/b-medir`, `/b-tarea T1`.

## Para cualquier humano o agente
1. `AGENTS.md`
2. `docs/KINGSCODE_MASTER_KNOWLEDGE.md`
3. `docs/KINGSCODE_STATE.json`
4. `docs/TEAM_SPLIT.md`
5. `docs/ARCHITECTURE_V05.md`
6. `docs/INTEGRATION_CONTRACTS.md`
7. `config/strategy.json`
8. `docs/DECISION_LOG.md`

## Estado mergeado y trabajo actual
- **A:** v0.6 y el Benchmark interno v1 están implementados/auditados. El benchmark tiene 200 casos (120/40/40), R0 medido y `Evidence Completeness@8` como métrica primaria. No hay selección de retrieval ni freeze para B: R1-Qwen/R1-BGE/R2/R3–R8 reales siguen `GPU_BLOCKED`. Los diagnósticos CPU graph/R6/R7/R8 no son resultados R3-based.
- **B:** Gate 1B dummy es histórico. Están mergeados el fallback de citas a abstención por ítem, política mínima de abstención, retrieval con opciones de MC, UI, `run.sh` y `Dockerfile`; no hay ejecución end-to-end versionada con corpus/GPU, decoder real, bakeoff ni throughput T6 medido.

No asumir CUDA objetivo, pesos descargados, freeze, bakeoff, RAGAS o throughput reales.

## Próxima sesión en la 4090

Leer primero `docs/GPU_DAY_RUNBOOK.md`, `docs/BENCHMARK_METHODOLOGY.md`, `docs/MEMBER_A_RUNBOOK.md`, `docs/MEMBER_B_RUNBOOK.md` y `docs/KINGSCODE_STATE.json`. Primer comando: `git pull --ff-only origin main`. Después verificar commit/snapshot, ejecutar diagnósticos/validaciones versionadas y seguir el protocolo del benchmark 200: dense/complementarity → R2 → R3–R8 en validation → una confirmación holdout posterior → confirmación oficial-50 sin retuning → freeze para B. No confundir resultados históricos/dummy ni diagnósticos CPU con resultados GPU.
