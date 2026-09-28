# Integrante B — Query / Reasoning / Generation / Evaluation / Delivery — v0.5

## Objetivo
Convertir evidencia recuperada por A en respuestas válidas, grounded, reproducibles y competitivas, y medir cada cambio con el evaluador oficial.

## B0 — harness independiente de GPU
Construir interfaces que funcionen primero con passages mock o fixtures reales:
- `normalize_query(question)`
- `route_graph(question, flat_passages) -> off|auto|on`
- `answer(question, passages, format)`
- `validate_submission(row)`
- `citation_guard(row, passages)`
- `run_eval(submission)`

## B1 — query normalizer
Normalizar sin destruir términos jurídicos exactos. Detectar y preservar:
- `Ley X de YYYY`;
- `Decreto X de YYYY`;
- `Artículo N`;
- sentencias y radicados;
- nombres de códigos;
- autoridades/corporaciones;
- expresiones de vigencia, derogación, modificación y remisión.

Expansión terminológica controlada, no multi-query libre por defecto.

## B2 — graph router v0
Determinista al comienzo. Activar grafo cuando existan señales como:
- remisiones;
- cambios normativos/temporalidad;
- modificación/derogación/reglamentación;
- necesidad explícita de jerarquía;
- insuficiencia del fast path.

Medir Graph OFF vs AUTO antes de sofisticarlo.

## B3 — decoder bakeoff
Con retrieval congelado, comparar:
1. Qwen3-8B;
2. ALIA-es-legal-administrative-7B-Instruct;
3. Salamandra-7B;
4. Llama 3.1 8B solo como control si hay tiempo.

Mismas preguntas, mismos passages, mismo prompt base, temperatura 0.

## B4 — salida y guardas
- JSON estricto según schema;
- no permitir citas fuera de `pasajes_recuperados`;
- abstener si evidencia insuficiente;
- no editar manualmente output del modelo.

## B5 — evaluación
Registrar por experimento:
- score oficial;
- RAGAS cuando corresponda;
- errores de schema;
- citas no respaldadas;
- abstenciones;
- latencia;
- VRAM;
- tokens de contexto;
- config exacta.

## B6 — entrega
Owner de:
- interfaz;
- comando único;
- README de ejecución;
- artefactos de reproducibilidad;
- empaquetado final;
- video/informe junto con A.

## Contrato con A
B consume el contrato de passage; no lee estructuras internas de BM25/FAISS/grafo directamente salvo para debugging acordado.

## Gate 1B implementado — 2026-09-27

Paquete independiente `kingscode/reasoning/`, configuración `config/reasoning.json` y CLI `tools/member_b.py`. Se preservó `from kingscode import retrieve, Retriever` y no se modificaron los internals de A.

- B0/B1: `Question` con proyección de campos públicos; `normalize_query` conserva referencias/negaciones, detecta entidades/señales y añade únicamente alias de un diccionario finito.
- B2: `route_graph(question, flat_passages)` devuelve OFF/AUTO/ON. Un adaptador booleano integra la decisión de B con el callback de A, después de una primera recuperación plana.
- B4: `answer`, backend `DummyDecoder`, abstención explícita, validación del schema oficial intacto y citation guard con trazabilidad exacta. Citas sin norma/año/artículo compatibles o evidencia alterada son errores bloqueantes.
- B5: `run_eval` invoca el evaluador oficial en un proceso separado, sin RAGAS. Registro por corrida con hashes, configuraciones, métricas, trazas, resultados y fingerprint estable.
- Pruebas de normalización, routing, schema, citas válidas/rechazadas, conflictos, etiquetas contaminadas e integración con el Retriever real. Segunda verificación: reejecución en otro proceso, comparación byte a byte y contraste de evidencia contra el corpus.

El dummy **siempre se abstiene**: el score del smoke solo comprueba la integración del evaluador, no capacidad jurídica. La contradicción entre la descripción y el enum de `respuesta_correcta` se resuelve con marcador A declarado no sustantivo y `abstencion=true`; ver `MEMBER_B_RUNBOOK.md`.

### Pendiente, sin marcar como completado

- Decoder real y B3/bakeoff, GPU/CUDA objetivo y benchmark neuronal completo.
- Calibración de abstención y verificación semántica de conclusiones; el guard actual verifica identidad/trazabilidad de citas.
- Ampliar formas de citación y probar routing/calidad por área con respuestas reales.
- RAGAS, UI, entrega competitiva, licencia/empaquetado y freeze final.

Siguiente comando exacto: `.venv/Scripts/python.exe tools/member_b.py smoke`.
Segunda verificación: `.venv/Scripts/python.exe tools/verify_member_b_second.py`.
Operación y contratos: `MEMBER_B_RUNBOOK.md`. Evidencia medida: `../reports/member_b_second_verification.json` y `../reports/member_b_tests_second.txt`.
