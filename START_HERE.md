# START HERE — KingsCode v0.5

## Para Claude Code
`CLAUDE.md` (importa `AGENTS.md` y fija el orden de lectura), luego `docs/B_EXTENSION_PLAN.md` y `docs/DECISION_LOG.md` para lo más reciente. Comandos: `/b-contexto`, `/b-medir`, `/b-tarea T1`.

## Mapa del repositorio
`docs/MAPA_DEL_REPO.md`: qué es cada carpeta, dónde está cada corpus (`corpus/` v0.1 fuera de git vs `corpora/corpus-v0.2/` agregado provisional) y qué falta para el sábado.

## Estado vigente (2026-09-29, prevalece sobre las secciones históricas de abajo)
Todo A+B está mergeado en `main`: resultados 4090, corpus v0.2/locator y auditoría v0.7 (A); planner con replay, ejecución robusta de 992 y reparación/construcción de citas (B). Sesión en PC con GPU sin admin: `tools/kingscode_gpu_todo.ps1`. Planes vigentes: `docs/CORPUS_V02_PLAN.md` (A) y `docs/B_PLAN_POST_GPU.md` (B). Última entrada: `docs/DECISION_LOG.md`.

## Para cualquier humano o agente
1. `AGENTS.md`
2. `docs/KINGSCODE_MASTER_KNOWLEDGE.md`
3. `docs/KINGSCODE_STATE.json`
4. `docs/TEAM_SPLIT.md`
5. `docs/ARCHITECTURE_V05.md`
6. `docs/INTEGRATION_CONTRACTS.md`
7. `config/strategy.json`
8. `docs/DECISION_LOG.md`

## Trabajo actual en paralelo
- **A:** Corpus v0 + grafo + retrieval baseline implementados. Ver `CORPUS.md`, `docs/MEMBER_A_RUNBOOK.md` y reportes de verificación; pendiente benchmark neuronal completo y ampliar/desambiguar fuentes.
- **B:** Gate 1B implementado: normalizador, router, dummy, abstención, guardas, evaluador y experimentos. Repetir con `.venv/Scripts/python.exe tools/member_b.py smoke`; ver `docs/MEMBER_B_RUNBOOK.md`. Decoder real/CUDA/bakeoff pendientes.

No asumir que CUDA ya está configurado.

## Próxima sesión en la 4090

Gate 2-Prep está preparado pero sin pruebas ejecutadas, por instrucción del usuario. Leer `docs/GPU_DAY_RUNBOOK.md` y `docs/MODEL_LOCKS_GATE2.md`. Primer comando en la GPU: `git pull --ff-only origin main`. Después verificar commit/snapshot y ejecutar las dos verificaciones pendientes. No confundir los 60 tests históricos de Gate 1B con validación del backend nuevo.

## Actualización que prevalece sobre los próximos pasos históricos de arriba

A ya tiene resultados RTX4090/Search V2 preservados en 60ebf7e. La fase vigente es locator productivo + benchmark v2 + corpus v0.2 en `feat/member-a-corpus-v02-locator`. Validation v1 cerrada; no reejecutar las variantes ni consumir holdout. Leer `reports/MEMBER_A_V02_PROGRESS.md` y `docs/A_TO_B_V02_CONTRACT.md`. B/decoder mantiene su estado independiente.
