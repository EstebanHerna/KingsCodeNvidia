# Verificación de KingsCode / Integrantes A y B

Las primeras secciones conservan la verificación previa del starter pack y de A. La última sección registra Gate 1B y su segunda verificación independiente.

## Pase 1 — preflight del proyecto
- Archivos mínimos presentes.
- `sample_50.jsonl`: 50 IDs únicos; 15 cerradas, 30 semiabiertas, 5 abiertas; 10 áreas.
- `seed_targets.json`: 186 documentos iniciales.
- 5/5 registros del ejemplo validan contra `submission.schema.json`.
- El evaluador oficial reproduce el comportamiento documentado del ejemplo parcial:
  45 ítems faltantes y 7 citas correctas respaldadas.

## Pase 2 — verificación independiente
- Los 19 archivos del starter pack se compararon byte a byte contra el ZIP original: sin diferencias.
- Se repitieron los conteos JSON/JSONL sin usar `tools/preflight.py`.
- Se volvió a validar el ejemplo con JSON Schema.
- Se volvió a ejecutar `evaluate.py` y reprodujo 5.24/50 puntos deterministas para el ejemplo parcial.
- Se verificó sintaxis de scripts oficiales y herramientas añadidas.

## CUDA
Se diagnosticó la máquina local: PyTorch `2.12.0+cpu`, CUDA no disponible, sin `nvidia-smi`. Evidencia en `reports/hardware.json`. La RTX 4090 objetivo todavía debe diagnosticarse por separado; no se instaló un stack GPU a ciegas.

## Implementación A — primer pase

- 16/16 pruebas unitarias y de integración, sin fallos ni saltos (`reports/member_a_tests.json` y `.txt`). Incluyen BM25 calculado a mano, RRF sin duplicación, índices obsoletos, no confundir cita mencionada con fuente recuperada, métricas por objetivos distintos, offsets sin pérdida, reformas citadas, numeración compuesta y exclusión completa de grupos ambiguos.
- 163 documentos; 26.558 pasajes validados contra el contrato; 26.060 indexables y 498 excluidos. Los offsets reproducen exactamente el texto y su prefijo declarado.
- 59.236 nodos y 75.380 edges; endpoints existentes y evidencia textual literal. Los nodos externos sin texto no producen pasajes.
- Integridad de los 19 archivos oficiales; hashes de fuentes, clean, pasajes, grafo e índice. Nueve combinaciones consulta/modo repetidas con igualdad exacta.
- Benchmark de las 50 preguntas con OFF/AUTO/ON: 41 evaluables, 36 con cobertura completa, Recall@10 de 0,525203 en OFF/AUTO y 0,537398 en ON. No es score de QA. La latencia reportada usa una instancia de Retriever precargada y excluye descarga/carga inicial.
- Prueba real de Qwen3 Embedding y Reranker abiertos sobre dos pasajes oficiales: vectores 2×1024 normalizados, consultas y reranking deterministas; índice denso guardado/cargado y rutas dense, hybrid/RRF y hybrid+reranker comprobadas (`reports/neural_smoke.json`). La reutilización de instancias en la prueba evita recargar pesos; no sustituye inferencias por scores simulados.

## Implementación A — segundo pase independiente

Después de corregir las ambigüedades detectadas en la revisión, se reconstruyó desde raw en `tmp/member_a_second_rebuild`, sin reutilizar los índices serializados de la primera ejecución:

- Coincidencia byte a byte de `passages.jsonl`, `graph/nodes.jsonl`, `graph/edges.jsonl` e `index/bm25.json`.
- 26.558 intervalos de texto y hashes de procedencia recalculados independientemente.
- Recall@10 y MRR@10 recalculados con aritmética independiente del módulo de evaluación: mismos valores en los tres modos.
- 150 rankings repetidos en otro proceso: mismos IDs y orden.
- 19 hashes oficiales verificados otra vez.

Evidencia: `reports/member_a_second_verification.json`. Hash de pasajes comprobado por ambos pases y por la prueba neuronal: `3b2b7a7beae2abe0abd14480be887a86ad933902c9735a21e02719a12daac3c0`.

## Límites y siguiente ejecución

En la entrega de A no se ejecutó el benchmark neuronal completo: no hay CUDA local y el smoke de dos pasajes no permite afirmar métricas para todo el corpus. En ese momento tampoco se generaron submissions ni score end-to-end; Gate 1B añade el smoke con dummy descrito abajo. Hay 28 objetivos de adquisición pendientes, ambigüedades de numeración conservadas para revisión y vigencia sin certificar. El corpus es baseline local, no freeze competitivo.

Comando local exacto: `.venv/Scripts/python.exe tools/member_a.py reproduce`. Segundo pase: `.venv/Scripts/python.exe tools/verify_member_a_second.py`. Próximo paso en la 4090: `python tools/check_cuda.py`; seguir luego `MEMBER_A_RUNBOOK.md` para dense/hybrid/reranker e integrar la interfaz con B.

## Gate 1B — primer pase y smoke

- Suite completa: 60 tests aprobados, sin fallos ni saltos; 44 nuevos de B y los 16 existentes de A. Primera ejecución final: 18,173 s.
- Normalizador, referencias exactas, alias con año, routing OFF/AUTO/ON y adaptador booleano probados; incluye integración con el Retriever real de A.
- Cita válida y citas rechazadas por artículo/año incorrecto, fuente secundaria mencionada, evidencia no emitida, texto/URL/metadata alterados. Las fixtures positivas son pasajes oficiales literales; las mutaciones negativas solo son probes unitarios, nunca corpus ni datos de entrenamiento.
- Schema válido en los tres formatos y fallos bloqueantes por output inválido; abstención ante evidencia vacía, débil, conflictiva o no vigente. Las etiquetas envenenadas no cambian entradas públicas, fingerprint ni salidas.
- Smoke completo sobre `sample_50`: 50 filas, 100 % JSON válido, 50 abstenciones deliberadas, cero citas. Routing: OFF 40, AUTO 6, ON 4. No se cargaron módulos neuronales.
- Evaluador oficial intacto, sin RAGAS: 0 errores, 5/50 puntos. Este valor no demuestra calidad jurídica ni calidad de citas; el backend dummy no responde sustantivamente.
- Registro final: `reports/member_b/20260928T035443616407Z-9a776fef5883/experiment.json`. Total 6,957 s; inicialización 3,845 s; latencia por pregunta p50 44,49 ms / p95 139,17 ms. Son mediciones locales, no un benchmark GPU.

## Gate 1B — segunda verificación independiente

Herramienta: `tools/verify_member_b_second.py`; informe: `reports/member_b_second_verification.json`. Finalizó el 2026-09-28 03:55:28 UTC (2026-09-27 en Bogotá).

- Se recalcularon los 19 hashes oficiales y se compararon 15 archivos de implementación/configuración/pruebas de A contra el commit original `382c5eb`: todos intactos.
- Se recalcularon hashes del corpus, grafo e índice BM25; mismo snapshot de A. Los módulos de B coinciden con los hashes registrados en la corrida.
- Validación independiente del schema oficial para 50 IDs/formats y autenticación de 400 registros de evidencia contra el corpus de A, sin reutilizar el helper de proyección de B.
- Suite completa repetida en otro proceso: 60/60 aprobados en 17,217 s; log en `reports/member_b_tests_second.txt`.
- Nueva ejecución del smoke en otro proceso: JSONL idéntico byte a byte, trazas idénticas excluyendo tiempos, mismo fingerprint y resultado oficial. Ningún módulo neuronal cargado en ambas ejecuciones.
- SHA-256 del JSONL: `09d9ac32ac981162105d91fc127dedd770023e6b5ca122d8cedfca5190f4767a`.
- Fingerprint: `9a776fef5883eb012f875170e6942ac2ed1aeb7621fabc322f3fb24201c849e9`.

Para repetir el gate: `.venv/Scripts/python.exe tools/member_b.py smoke`. Para auditarlo otra vez: `.venv/Scripts/python.exe tools/verify_member_b_second.py`. Detalles, contradicción del schema MC, archivos cambiados y pendientes en `docs/MEMBER_B_RUNBOOK.md` y `reports/MEMBER_B_DELIVERY.md`. CUDA objetivo, decoder real, bakeoff y RAGAS siguen pendientes; no se iniciaron en esta tarea.
