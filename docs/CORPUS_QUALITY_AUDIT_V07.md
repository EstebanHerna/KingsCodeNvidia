# Corpus Quality Audit v0.7 — solo auditoría

Base a3548a1; protocolo preregistrado en 45e0c36 antes del muestreo. Rama `feat/member-a-corpus-quality-audit-v07`. No se corrigió el corpus ni se reconstruyeron índices.

## Muestra y alcance

200 pasajes únicos, 118 documentos: 50 legislación, 40 códigos/decretos, 50 jurisprudencia, 20 históricos, 20 ambiguos/excluidos, 20 asociados a fallos R0 DEV. Seed 0, balance por documento y por categoría de fallo; sin overlap real. Grafo: 20 por cada tipo existente (CONTIENE, CITA, REMITE_A, MODIFICA, DEROGA), 100 aristas. El censo adicional examinó 18,636 grupos de fragmentos canónicos. El protocolo, muestra y hashes antes/después están en `reports/corpus_quality_v07/`.

Se contrastaron cuerpos/offsets con clean y una extracción independiente del raw oficial. Esto respalda identidad, fidelidad local y trazabilidad; no certifica ausencia de omisiones de documento completo. La muestra está enriquecida por riesgo, no estima tasas poblacionales.

## Métricas separadas

| Métrica | Numerador / denominador | UNKNOWN | Alcance |
|---|---:|---:|---|
| source_identity_accuracy | 200 / 200 | 0 | 1.0 |
| text_fidelity_rate | 200 / 200 | 0 | 1.0 |
| parser_error_rate | 12 / 200 | 188 | Tasa no determinada |
| contamination_rate | 12 / 200 | 188 | Tasa no determinada |
| truncation_rate | 0 / 200 | 200 | Tasa no determinada |
| article_locator_accuracy | 128 / 150 | 21 | Tasa no determinada |
| hierarchy_accuracy | 0 / 200 | 199 | Tasa no determinada |
| structural_metadata_accuracy | 0 / 200 | 188 | Tasa no determinada |
| canonical_document_accuracy | 200 / 200 | 0 | 1.0 |
| canonical_fragment_accuracy | 128 / 200 | 71 | Tasa no determinada |
| canonical_collision_rate | 1 / 18636 | 0 | 5.4e-05 |
| provenance_complete_rate | 200 / 200 | 0 | 1.0 |
| verified_temporal_status_rate | 20 / 200 | 0 | 0.1 |
| incorrect_temporal_assertion_rate | 0 / 20 | 0 | 0 |
| unknown_with_no_evidence_rate | 180 / 200 | 0 | 0.9 |
| graph_grounding_precision | 89 / 100 | 3 | Tasa no determinada |
| relation_type_accuracy | 89 / 100 | 3 | Tasa no determinada |

En métricas con UNKNOWN no se publica un porcentaje definitivo. Parser/contaminación: 12 defectos confirmados de 200 (mínimo observado 6%), 188 sin certificación semántica. Locators: 128 respaldados, uno falso y 21 desconocidos entre 150 aplicables; 50 providencias excluidas. Jerarquía: 197 coincidencias literales de encabezados NO se cuentan como 197 relaciones padre-hijo correctas. Todas las omisiones/truncaciones siguen UNKNOWN. No hay quality score agregado.

Temporalidad: 20 bloques históricos respaldados, 180 UNKNOWN conservadores válidos. Cero afirmaciones temporales incorrectas entre las 20 afirmaciones examinadas; no equivale a certificar vigencia. Grafo: 89 respaldadas, 8 falsas y 3 UNKNOWN; precisión evaluada 89/97, con el denominador completo de 100 visible.

## Hallazgos confirmados

- **G01 HIGH:** seis MODIFICA y una DEROGA atribuyen la modificación/derogación a la sección/artículo contenedor, aunque el sujeto textual es otra disposición citada. Ejemplos: C-106/2018 y C-355/2006; Decreto780 art2.4.2.4; Ley80 art69. Ver endpoints, evidencia y contexto en los JSONL.
- **G02 HIGH:** una entrada de índice de SU-214/2016 se trata como cláusula de `RESUELVE 201`.
- **C01 HIGH:** tres ocurrencias distintas de “Fundamentos lógicos” de C-355/2006 comparten un fragment ID, afectando 172 pasajes. Los 990 grupos de segmentos físicos no son por sí solos colisiones.
- **P01 MEDIUM:** once pasajes de la muestra retienen encabezados del título/capítulo siguiente dentro del artículo precedente.
- **P02 HIGH:** Ley137/1994, pasaje `ley_137_de_1994:00015:8562271d262d`, contiene artículos40–46 con metadato artículo9. Esto puede engañar un locator correcto.
- **D01 MEDIUM:** siete grupos de texto idéntico (22 pasajes) son fórmulas comunes de providencias distintas; no prueban que los documentos sean mirrors. Dedup debe conservar identidad/provenance.

## Fallos R0 DEV y adquisición

`benchmark_crosswalk.json` cruza los fallos existentes con la muestra y presencia de gold spans. Un ranking failure no se transforma en corpus_missing. Cuando coincide un defecto del parser se registra; su efecto causal en la métrica no se presume. No se usaron validation/holdout ni se cambiaron anotaciones.

`target_review.json` conserva los 28 identificadores y sus clases v0.6 (14 source_unavailable, 11 not_found, 2 identifier_suspect, 1 ambiguous). Hay nueva evidencia oficial para 18: seis páginas/PDF de documento completo localizados, cinco landings, tres catálogos, una ficha, un edicto, una cita secundaria y un caso con emisor ambiguo. No son 18 adquisiciones aceptadas. Los suspect siguen suspect y los matches con año/tipo diferente se rechazaron. Cada registro enlaza su evidencia oficial y sus límites.

## Remediación y verificación

P0: sujeto de relaciones, separación TOC/secciones, colisión C355 y artículos partidos de Ley137. P1: límites de títulos y dedup con provenance. Todas son tareas de un corpus-v0.2 separado. No se toca snapshot v0.1 medido en GPU.

Se verificó otra vez la muestra/protocolo, todos los archivos del corpus contra los hashes previos y los 19 archivos oficiales. Revisión secuencial AUDITOR, LEGAL DATA CURATOR, CRITIC e INTEGRATOR por el mismo agente; no es una revisión externa independiente. Veredicto: auditoría aceptable con incertidumbre explícita; corpus no certificado. Revisión externa por Luis pendiente.
