# Integrante A — Knowledge Layer / Corpus / Graph / Retrieval — v0.5

## Objetivo
Crear la capa de conocimiento que permita recuperar evidencia jurídica oficial, trazable y estructurada con o sin expansión de grafo.

## A0 — inventario
Completado: 186 `seed_targets` priorizados. El ZIP oficial no contiene los textos completos.

## A1 — Corpus v0
Priorizar por peso del banco + aparición en sample_50 + cobertura de áreas. Empezar con Constitución, CGP, CST, Estatuto Tributario, Estatuto del Consumidor y demás fuentes de alta cobertura.

## A2 — adquisición reproducible
Por cada documento guardar:
- URL oficial;
- fecha de consulta;
- hash;
- tipo de documento;
- estado de descarga/parseo;
- fuente institucional.

No usar texto jurídico inventado o completado por modelos.

## A3 — parsing estructural
Generar simultáneamente:
- raw original;
- clean normalizado;
- passages estructurales;
- nodos de grafo;
- edges verificables.

Unidad primaria de leyes/códigos: artículo; preservar parágrafos, incisos y numerales. Sentencias: estructura jurídica disponible.

## A4 — grafo desde Corpus v0
Jerarquía `CONTIENE` siempre que pueda derivarse estructuralmente. Relaciones normativas adicionales solo con evidencia textual/metadata verificable.

## A5 — índices
En orden:
1. BM25;
2. dense embeddings;
3. RRF;
4. reranker;
5. graph expansion selectiva.

## A6 — benchmark
Medir:
- Recall@1/3/5/10;
- MRR;
- legal_basis@10 cuando sea evaluable;
- cobertura por área y tipo de pregunta;
- Graph OFF vs AUTO;
- latencia retrieval.

## Contrato con B
`retrieve(question, k, graph_mode="auto") -> list[passage]`

A es responsable de que cada evidence record sea trazable; B decide cómo consumirlo en generación.

## Estado ejecutado — 2026-09-27

- A0–A4: implementados. 191 objetivos configurados, 163 documentos oficiales adquiridos y parseados; 28 fallos conservados con su causa. Corpus v0.1, parser `legal-blocks-1.2`, fuentes raw/clean, offsets, jerarquía, grafo y manifest disponibles.
- A5: BM25 e interfaz pública operativos. Dense exacto, embeddings Qwen3, RRF y reranker Qwen3 implementados y probados con pesos reales sobre pasajes oficiales. El índice neuronal de todo el corpus y su comparación completa requieren ejecución en la máquina objetivo; no se presentan como terminados.
- A6: benchmark BM25 OFF/AUTO/ON sobre las 50 preguntas; cobertura, Recall@k, MRR, nDCG, desgloses por área/formato y auditoría de etiquetas. Los resultados están en `../CORPUS.md` y `../reports/retrieval_bm25.json`.
- QA: pruebas de contrato/métricas/parser, conservación de hashes oficiales, evidencia de cada edge y segunda reconstrucción independiente. Ver `VERIFICATION.md` y los reportes asociados al hash del corpus.

### Pendientes concretos

1. Integrar el `retrieve` real con B y su router/guards.
2. Ejecutar `python tools/check_cuda.py` en la 4090; continuar los comandos de `MEMBER_A_RUNBOOK.md` para dense → hybrid → hybrid+reranker.
3. Resolver fuentes fallidas, numeraciones ambiguas y revisión de vigencia antes del freeze; sin sustituir identidades por aproximación.
4. Medir cobertura de relaciones jurídicas adicionales antes de habilitar más tipos de edge/tags; conservar únicamente las relaciones sustentadas.
5. Revisar licencia y empaquetado/publicación del corpus con el equipo para la entrega final.

No se ha hecho fine-tuning ni se ha atribuido un score de respuestas al baseline de retrieval.
