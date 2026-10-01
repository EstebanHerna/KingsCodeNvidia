# Reporte de avance — Hackathon 2026

> **Borrador interno** (no es la plantilla oficial; esa está en `entregables/viernes/REPORTE_AVANCE.md` y no se modifica).
> Antes de enviar: actualizar la sección 1 con la mejor corrida del 1–2 de octubre, exportar a `REPORTE_AVANCE.pdf` (una página)
> y enviar a rf.manrique@uniandes.edu.co con asunto `[Hackathon 2026] Avance — KingsCode` antes del viernes a las 17:00.

**Equipo:** KingsCode
**Integrantes:** Esteban Alejandro Hernández · Luis Sebastián Contreras Díaz
**Fecha de la medición:** 2026-10-01 (RTX 4090, sala Turing)

---

## 1. Puntaje sobre las preguntas de muestra

Resultado de `python scripts/evaluate.py --submission <corrida>/submissions.jsonl --split sample` (sin RAGAS).

| Componente | Puntos obtenidos | Puntos posibles |
|---|---:|---:|
| Exactitud en cerradas | 10,67 (8/15) | 20 |
| Calidad de citación | 10,61 (recall 0,53; **0 citas sin respaldo**) | 20 |
| Abstención calibrada | 6,40 | 10 |
| **Total automático sin RAGAS** | **27,68** | **50** |

Observaciones sobre el resultado:

Configuración medida: Qwen3-8B (BF16, temperatura 0) + BM25 + router de grafo, k = 8, prompt `grounded-formats-v4`. Ninguna cita queda sin respaldo en la evidencia recuperada: una guarda determinista repara o suprime toda cita no respaldada. Dos corridas completas dieron un `submissions.jsonl` idéntico byte a byte, lo que respalda la verificación en vivo. El componente RAGAS (30 pts) aún no se ha medido.

## 2. Estado del corpus

| Métrica | Valor |
|---|---|
| Documentos incorporados | 167 (163 en corpus v0.1 + 4 en v0.2 provisional) |
| Fragmentos indexados | 26.132 (26.060 en v0.1 + 72 en v0.2); 26.630 segmentados en total |
| Áreas del banco con cobertura | 10/10: constitucional (40 docs), familia (29), laboral (25), civil (24), tributario (18), administrativo (17), penal (16), comercial (14), mercados (14), procesal (10) |
| Áreas del banco sin cobertura | Ninguna sin documentos; la profundidad es desigual (procesal y mercados son las más delgadas) |

Fuentes consultadas: Función Pública – Gestor Normativo (68 documentos), relatoría de la Corte Constitucional (93), Corte Suprema de Justicia (4), normograma del SENA (1, Código Civil), Comunidad Andina (1). Cada documento conserva URL, fecha de consulta y SHA-256 del original en `corpus_manifest.json`.

## 3. Arquitectura actual

| Componente | Elección |
|---|---|
| Encoder | Qwen/Qwen3-Embedding-0.6B (abierto, revisión fijada); recuperación híbrida preparada y en medición |
| Decoder | Qwen/Qwen3-8B, BF16, temperatura 0, greedy, sin "thinking"; atención SDPA |
| Estrategia de recuperación | BM25 sobre fragmentos por artículo, locator exacto de referencias normativas, expansión por grafo normativo activada por router, consultas por opción en cerradas fusionadas por RRF; reranker Qwen3-Reranker-0.6B en evaluación |
| Segmentación del corpus | Estructural jurídica: un fragmento por artículo (o unidad equivalente en sentencias), con norma, artículo y jerarquía en los metadatos |
| Mecanismo de abstención | Política sobre la evidencia (vacía, en conflicto o no vigente) + abstención declarada por el modelo; guarda de citas que repara o suprime antes de abstenerse |

## 4. Riesgos identificados

1. **RAGAS sin medir (30 pts).** Haremos una única medición con el juez oficial sobre la configuración final, antes del sábado.
2. **Tiempo de ejecución.** Hoy son 15,4 s/pregunta (≈ 4,2 h para 992, en una ventana de 6 h). Mitigación: checkpoints por pregunta con reanudación, alarma si una configuración pasa de 20 s/pregunta, y ninguna técnica nueva sin medir su costo.
3. **Corpus y reproducibilidad de fuentes.** Al volver a descargar las fuentes oficiales, 67 de 163 documentos cambiaron; por eso el índice se congela como snapshot (hashes por archivo) y se publica con licencia abierta. La cobertura de procedimiento y derecho de los mercados es la más delgada.
