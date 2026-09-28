# KingsCode v0.5 — Agent-ready, Graph-Aware, 2 integrantes

Este paquete conserva el starter pack oficial y formaliza una organización paralela para dos integrantes y cualquier agente auxiliar.

## Cambios v0.5
- nuevo `AGENTS.md` como protocolo operativo universal;
- roles A/B actualizados para la arquitectura Graph-Aware;
- A ahora posee Knowledge Layer + Corpus + Graph + Retrieval;
- B ahora posee Query/Reasoning Layer + routing + Generation + Evaluation + Delivery;
- nuevo contrato estable A↔B;
- roadmap paralelo: A no espera CUDA y B no espera corpus completo;
- documentación stale de GraphRAG reemplazada por `ARCHITECTURE_V05.md`.

## Empezar
Leer `START_HERE.md`.

## Estado
- starter pack: verificado;
- arquitectura: v0.5;
- CUDA: todavía no configurado en la máquina objetivo;
- Corpus v0: 163 documentos oficiales; corpus, grafo y BM25 construidos;
- retrieval: interfaz estable, benchmark OFF/AUTO/ON y verificación independiente;
- Qwen embedding/reranker: implementación y smoke con pesos abiertos reales; benchmark completo pendiente de GPU;
- harness de B: por construir.

## Entrega del Integrante A
Consultar [CORPUS.md](CORPUS.md), [manifest](corpus_manifest.json) y [runbook](docs/MEMBER_A_RUNBOOK.md). Los resultados medidos, limitaciones y fuentes pendientes están documentados; el corpus aún no es el freeze competitivo.

```powershell
.venv/Scripts/python.exe tools/member_a.py query --question "¿Qué regula el Código General del Proceso?" --k 8
.venv/Scripts/python.exe tools/member_a.py reproduce
```
