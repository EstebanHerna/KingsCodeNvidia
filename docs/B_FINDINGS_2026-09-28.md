# Hallazgos de B — 28-sep-2026

> **Nota de vigencia (28-sep-2026, tarde):** este documento se escribió contra el commit `254fa3a` (Gate 1B, `DummyDecoder`). Desde entonces `a179af7` (Gate 2-Prep, Luis) agregó `kingscode/generation/hf_decoder.py` con un decoder real y ya se aplicó el fix del punto 1 (ver abajo y `docs/DECISION_LOG.md`, entrada "Corrección del abort-on-citation"). Los puntos 2, 4, 5, 6, 8 y 9 siguen vigentes tal cual. El punto 3 (política de abstención) está parcialmente cubierto por el fix de esta sesión, no por un rediseño de `policy.py`.

Revisión del repositorio en el commit `254fa3a` contra el enunciado oficial y el código de `scripts/evaluate.py` y `scripts/citations.py`. Todas las cifras son reproducibles con los comandos indicados.

## 1. Resultados actuales

| Medida | Valor | Fuente |
|---|---:|---|
| Puntaje automático sin RAGAS (dummy que se abstiene) | 5,00 / 50 | `reports/member_b/20260928T035443616407Z-9a776fef5883/evaluation.json` |
| Recall@10 de retrieval a nivel artículo (BM25, OFF) | 0,525 | `reports/retrieval_bm25.json` |
| Cuerpos de `legal_basis` presentes en los 8 pasajes recuperados (nivel cuerpo, como el evaluador) | 40/49 = 0,82 | `tools/analyze_citation_ceiling.py` |
| Ítems con al menos una norma correcta en la evidencia | 34/41 | ídem |
| Cuerpos de `legal_basis` que no existen en el corpus | Ley 472 de 1998 (2 ítems), C-468/2024, SU-16/2020, SU-277/2025 | ídem |
| Área más débil | Administrativo: 1/5 cuerpos en evidencia | ídem |
| Ítems que la política actual mandaría a abstención | 6/50, todos por `missing_explicit_reference` | `trace.jsonl` |

La métrica de A (artículo exacto) subestima lo que importa para citas: el evaluador compara cuerpos normativos y acepta como respaldo cualquier mención en el texto del pasaje.

## 2. Techo de citación sin decoder

Reproducir: `python tools/analyze_citation_ceiling.py`. Las filas no tienen texto real y las cerradas están fijas en "A", así que solo son informativos los componentes de citas y abstención.

| Estrategia para construir referencias | Citas /20 | Recall | Sin respaldo | Citas por ítem | Abstención /10 |
|---|---:|---:|---:|---:|---:|
| Ninguna | 0,00 | 0,00 | 0 | 0,0 | 1,16 |
| Norma del encabezado del pasaje 1 | 5,71 | 0,29 | 0 | 1,0 | 3,95 |
| Normas de los encabezados top‑3 | 10,20 | 0,51 | 0 | 2,2 | 5,58 |
| Normas de los encabezados top‑8 | 13,06 | 0,65 | 0 | 4,6 | 6,05 |
| Todas las normas mencionadas en la evidencia | 16,33 | 0,82 | 0 | 19,1 | 6,74 |

Lectura crítica:

- El salto de 0 a ~10–13 puntos no requiere modelo; requiere que el código escriba las normas de la evidencia en `referencia_legal` / `justificacion` y que nada sin respaldo se cuele. Con el decoder real (`kingscode/generation/prompts.py`) esto lo hace el propio modelo, guiado por el prompt; sigue siendo válido usarlo como piso/fallback si el modelo no cita nada.
- "Todas las normas de la evidencia" maximiza la métrica (el evaluador no penaliza citas respaldadas pero incorrectas), pero 19 normas por respuesta se ve como relleno ante el jurado y en el video. Es una decisión de equipo, no técnica.
- En `open_ended` los cuatro campos van al juez RAGAS; una lista larga de normas añade afirmaciones sin sustento en la respuesta esperada. Ahí conviene pocas normas.

## 3. Problemas en la capa B (por impacto, estado actualizado)

1. **~~La guarda aborta toda la corrida~~ — corregido el 28-sep-2026, tarde.** `Pipeline.run` ahora captura `CitationGuardError` y convierte esa fila en abstención sin abortar el resto de la corrida. `citation_guard` en sí sigue lanzando la excepción para cualquier llamador directo (`answer()`, tests) — eso es intencional, ver `docs/DECISION_LOG.md`.
2. **La guarda exige más que el evaluador — sigue vigente, sin aplicar.** Verifica artículo además de cuerpo (`legal.py`/`guards.py::citation_guard`), mientras el evaluador (`scripts/citations.py::bodies`) compara solo el cuerpo. Una cita "artículo 5 de la Ley 1010 de 2006" con un pasaje del artículo 1 de esa ley puntúa como respaldada en el evaluador y se rechaza aquí (ahora: se convierte en abstención en vez de abortar la corrida, pero sigue perdiendo el punto en vez de ganarlo). Documentado para revisión cruzada con Luis; no se aplicó unilateralmente porque toca ~16 tests de `GuardSchemaTests` que fijan ese comportamiento a propósito.
3. **La política se abstiene de más — sin cambios de diseño, mitigado parcialmente.** `policy.py:62–72` sigue igual. El fallback de citas ahora hace que una respuesta rechazada por cita se convierta en abstención en vez de tumbar la corrida, pero eso es un backstop, no una política de abstención mejor calibrada. Sigue siendo cierto que abstenerse en cerradas es casi siempre peor que adivinar.
4. **La entrada pública descarta `area`, `tema`, `sub_tarea` y `complejidad` — sin verificar.** `contracts.py:31–36` (ahora `Question`) sigue proyectando solo id/pregunta/formato/opciones. Falta confirmar con los organizadores si `test_992.jsonl` trae esos campos (pregunta abierta de la sesión del lunes) y, si sí, decidir si vale la pena ampliarlos para prompts por sub-tarea.
5. **La recuperación de cerradas ignora las opciones — sin cambios.** Solo se busca con `pregunta`.
6. **Throughput no dimensionado — parcialmente cubierto.** `kingscode/generation/experiments.py` (Gate 2-Prep) ya separa retrieval de decoder y congela evidencia entre modelos, pero no hay medición de concurrencia/caché reanudable sobre las 992 preguntas todavía.
7. **Cobertura de corpus — sin cambios, es tarea de A.** Falta la Ley 472 de 1998; 28 objetivos fallidos.
8. **Entregables — parcialmente cubierto en esta sesión.** `interfaz/app.py` (Streamlit, identidad Software Colombia) ya existe y está conectado al pipeline real, pendiente de probarse con corpus real. Siguen faltando `run.sh`/Dockerfile de un solo comando y la sección `## Corpus e índice` del README.

## 4. Lo que está bien y hay que conservar

- Proyección de campos públicos y aislamiento de etiquetas: cumple integridad académica.
- `evidence_record` copia literal del texto de A con su encabezado de norma: es lo que hace posible el respaldo.
- Registro por corrida con fingerprint y hashes: sirve para el informe y la verificación en vivo.
- Tests con pasajes oficiales reales.
- El decoder real (`HFDecoder`) preserva exactamente el mismo contrato/guardas que el dummy: no hubo que tocar `pipeline.py` para conectarlo, solo el fallback de citas de esta sesión.

## 5. Preguntas abiertas para los organizadores (lunes 17:00 o por correo)

- ¿`test_992.jsonl` incluye `area`, `tema`, `sub_tarea` y `complejidad`?
- ¿Se admite `respuesta_correcta: null` en cerradas con abstención? (La descripción del schema lo permite y el enum no; el sistema usa "A" como marcador formal, ver `abstention_row`.)
- ¿Gemma‑4‑E4B (4,5B efectivos, 8B con embeddings) cumple el límite?
- ¿En la verificación en vivo se compara el texto byte a byte o solo normas y pasajes?
- Confirmar elegibilidad nominal de Qwen3-8B (8.190.735.360 parámetros publicados) y Llama 3.1 8B (8.030.261.248) bajo el límite de 8.000 millones (ver `config/decoder_bakeoff.json`, campo `requirements`).
