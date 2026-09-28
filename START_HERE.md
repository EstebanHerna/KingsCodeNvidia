# START HERE — KingsCode v0.5

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
