# Corpus v0.2 y locator exacto — plan revisado para Claude Code

Fecha: 2026-09-28 (lunes). Base: `origin/main` en `a3548a1`. Entrega: sábado 3 de octubre, 15:00.
Este documento revisa la propuesta de corpus v0.2 (P0–P8), la corrige con evidencia medida en el repo y la convierte en tareas ejecutables C0–C8. Cada tarea trae qué tocar, cómo saber que quedó bien y un prompt listo para pegar.

---

## 1. Veredicto sobre la propuesta

| Punto de la propuesta | Veredicto | Motivo (medido abajo) |
|---|---|---|
| No tocar corpus v0.1 antes de arreglar el locator | **Correcto** | Los 37 fallos de R6 en dev son de parser y ranking, no de documentos faltantes |
| P1 locator determinista con inyección directa | **Correcto, prioridad 1** | El R6 actual no puede inyectar: solo reordena lo que BM25 ya trajo |
| P2 resolver las 28 adquisiciones y ambiguos | **Correcto** | Incluye la Ley 472 de 1998, que falta y está en el `legal_basis` de la muestra |
| P3 cortes (CSJ, Consejo de Estado) | **Correcto pero acotado** | Solo decisiones identificadas por número y citadas por el corpus o por el banco. Nada masivo |
| P4 fuentes regulatorias por área | **Parcial** | Solo DUR 1625 (tributario) y Circular Única SIC si hay tiempo. Todo lo demás, backlog |
| P5 nodos externos del grafo por importancia | **Correcto, muy barato** | Es la mejor señal para saber qué adquirir sin intuición |
| P6 derecho internacional | **Casi fuera** | El enunciado (§4.2) dice: "El banco no cubre derecho ambiental ni derecho internacional". Solo decisiones CAN de propiedad industrial y competencia |
| Vigencia (156 documentos `unknown`) | **Correcto en el fondo, peligroso en la forma** | Solo se registra lo que la fuente oficial dice textualmente. Nunca bloquea respuestas |
| Jurisprudencia estructurada | **Parcial** | Solo encabezados de sección y el RESUELVE por regex. La ratio no se extrae con modelos |
| Benchmark v2 | **Correcto y urgente, con un cambio** | El v1 es 100 % explícito; las preguntas reales casi nunca lo son. Las preguntas semánticas las escribe el equipo a mano |
| "Dense deja de pesar igual que BM25" | **No todavía** | En `main` no hay corridas densas (están `GPU_BLOCKED`) y un benchmark 100 % explícito favorece a BM25 por diseño |

---

## 2. Evidencia medida (reproducible)

### 2.1 Por qué falla R6

Corrida `reports/benchmark/r6_bm25_diagnostic/20260928T185549565248Z-dev`: 83/120 éxitos; 20 `ranking_failure` y 17 `correct_document_wrong_passage`. Los 37 fallos caen en códigos y en la Constitución: CGP (18), Código Civil (8), Constitución (7), CST (2) y Código General Disciplinario (2). En todos el documento es correcto y el artículo no.

Hay tres defectos en `kingscode/diversify.py::parse_reference`, comprobados:

| Consulta | Salida actual | Correcto |
|---|---|---|
| `artículo 37 del Código General del Proceso` | `codes=['General del Proceso']` (texto libre, no id canónico) | `codigo_general_proceso`, art. 37 |
| `artículos 7 y 8 del Código Civil` | `articles=['7']` (pierde el 8) | arts. 7 y 8 |
| `artículo 11 de la Constitución Política` | sin norma ni código | `constitucion`, art. 11 |
| `Art. 60 del CST` | nada | `codigo_sustantivo_trabajo`, art. 60 |
| `artículo 90 del CGP` | solo el artículo | `codigo_general_proceso`, art. 90 |
| `... Código General del Proceso (Ley 1564 de 2012)` | `norms=[ley 1564 2012]`, que no casa con `canonical_body=('codigo_general_proceso',…)` | alias ley→código |

Además, `run_r6` (`kingscode/metadata_experiments.py`) solo reordena el pool de `retrieve(question, k*4)`. Si el artículo exacto no está en esos 32 candidatos (pasa con artículos de número bajo, porque "1", "2" son tokens frecuentes), el boost no tiene a quién subir.

`kingscode/reasoning/legal.py::references` (capa B) y `scripts/citations.py::extract` (oficial) ya resuelven correctamente las cinco primeras filas. Hay dos parsers que funcionan y el locator usa el tercero, que no funciona.

### 2.2 El benchmark interno no representa el banco

- Benchmark v1: 200/200 casos con etiqueta `EXPLICIT`, 6 con `GRAPH`. Todos siguen la plantilla "Ubique el texto oficial del artículo N de …".
- Muestra oficial: solo **4/50** preguntas nombran un artículo en el enunciado y **14/50** nombran alguna norma. Las otras 36 son semánticas ("¿Cuáles son los elementos esenciales de validez de un contrato?").

Consecuencias:
1. El locator va a subir mucho el benchmark y poco el puntaje real. Vale la pena porque es barato y porque las preguntas explícitas deben quedar perfectas, pero no es la palanca principal.
2. Ninguna decisión de pesos BM25 vs denso puede tomarse con v1: es un benchmark de identificadores y BM25 gana por construcción.

### 2.3 Qué falta del corpus según la muestra

Cuerpos del `legal_basis` de la muestra ausentes del corpus: Ley 472 de 1998 (2 ítems), Sentencias C-468 de 2024, SU-16 de 2020 y SU-277 de 2025. El enunciado (Paso 5) autoriza usar los `legal_basis` de la muestra para decidir qué adquirir. Lo que prohíbe es indexar las preguntas o las respuestas.

Todos los 163 `norm_name` del manifest reproducen su `canonical_body` con `citations.extract`. Esa propiedad debe mantenerse en v0.2: es la que permite que las citas queden respaldadas.

---

## 3. Reglas para Claude Code en esta fase

### 3.1 No dañar

1. **v0.1 es inmutable.** Construir v0.2 en `corpus_v02/` (fuera de git, igual que `corpus/`). Nunca sobrescribir `corpus/`, `corpus_manifest.json` ni sus hashes hasta que el equipo apruebe el freeze de v0.2 por escrito en `DECISION_LOG.md`.
2. **Una rama por tarea** (`feat/a-locator-v1`, `feat/a-acq-v02`…), PR a `main`, sin force-push.
3. **Contratos intactos.** `retrieve(question, k, graph_mode)` conserva su firma y el formato de pasaje (`docs/INTEGRATION_CONTRACTS.md`). Campos nuevos solo se añaden; nunca se renombran ni se quitan.
4. **Nada de B cambia en tareas de A,** salvo importar `kingscode/reasoning/legal.py` como parser.
5. **Archivos oficiales intactos:** verificar con `docs/OFFICIAL_SHA256.txt` al final de cada tarea.
6. **Suite verde:** `python -m unittest discover -s tests -v` antes y después; reportar el conteo.
7. **Los ids de gold del benchmark deben seguir resolviendo.** Si v0.2 cambia `canonical_fragment_id` de algo existente, es un bug.

### 3.2 No alucinar

1. **Ningún texto jurídico, fecha, número, estado de vigencia, ratificación o URL sale de la memoria del modelo.** Todo dato del corpus viene de bytes descargados de una fuente oficial, con URL final, fecha UTC, HTTP 200, TLS verificado y SHA-256.
2. **Identidad verificada:** un documento entra solo si el título descargado contiene el tipo, número y año esperados. Si no coincide, va al backlog con la clase `identifier_suspect`. Nunca se sustituye por la norma "más parecida".
3. **Fuente caída o bloqueada** → backlog `source_unavailable` con el error literal. No reintentar por mirrors no oficiales.
4. **Vigencia:** solo se escribe `repealed_by`, `modified_by` o `effective_to` cuando el texto de la fuente lo dice ("Derogado por el artículo X de la Ley Y", "Modificado por…"), guardando la frase exacta como evidencia. Todo lo demás queda `unknown`. SUIN y Función Pública advierten que su información no certifica vigencia: copiar esa advertencia en el manifest.
5. **Relaciones del grafo:** solo con evidencia textual explícita (ya es la política de A). `INTERPRETA`, `EXEQUIBLE` e `INEXEQUIBLE` solo desde la parte resolutiva, con la frase exacta como `evidence_text`.
6. **Ningún modelo cerrado genera preguntas, respuestas, resúmenes, ratios ni metadatos.** Claude Code escribe código y plantillas deterministas; las preguntas semánticas del benchmark v2 las escribe una persona del equipo.
7. **Métricas:** reportar solo números que salgan de un archivo en `reports/` generado en esa misma sesión, con su ruta. Si algo no se pudo correr, decir "no ejecutado" y el motivo. Nunca estimar un resultado.

---

## 4. Tareas

### C0 — Congelar v0.1 como línea base (30 min)

**Hacer:** `reports/freeze/corpus_v01_baseline.json` con los hashes de pasajes, grafo y BM25, el commit, las métricas R0 y R6-diagnóstico en dev y validación, y la evaluación oficial de la muestra con la versión actual de B.
**Aceptación:** el archivo existe, los hashes coinciden con `corpus_manifest.json` y la suite pasa.

```
Lee CLAUDE.md y docs/CORPUS_V02_PLAN.md (secciones 1-3). Tarea C0. Sin modificar código:
genera reports/freeze/corpus_v01_baseline.json con hashes del corpus v0.1, commit actual,
métricas R0 y R6 bm25-diagnostic en dev y validation (rutas de los reportes fuente) y la
evaluación oficial de la muestra con B actual. Si algo no se puede correr aquí (sin corpus/
local), escríbelo como "no_ejecutado" con el motivo. No inventes números.
```

### C1 — Locator exacto con inyección (prioridad máxima)

**Diseño:**

```
pregunta
  └─ parse (kingscode/reasoning/legal.py::references; respaldo: scripts/citations.py::extract)
       └─ referencias completas: (canonical_body, artículo) y decisiones (jurisprudencia, id, año)
            └─ LocatorIndex[(canonical_body, artículo)] → [passage_id…] en orden, incluidas "(continuación)"
                 y LocatorIndex[(jurisprudencia, id, año)] → [passage_id…] de la sentencia
                      └─ pool = locator_hits  ∪  retrieve(pregunta, candidate_k)
                           └─ orden final: locator_hits primero (máx. L_MAX), luego el ranking general
```

**Reglas:**
- El índice se construye desde `passages.jsonl` usando solo pasajes `retrieval_eligible`. Si hay grupos ambiguos (mismo número de artículo repetido), el locator no elige: no inyecta y lo registra.
- Alias por número y año: `(ley,1564,2012)`→`codigo_general_proceso`, `(decreto,2663,1950)`→`codigo_sustantivo_trabajo`, `(ley,84,1873)`/`(ley,57,1887)`→`codigo_civil`, etc. La fuente es el `canonical_body` del manifest, no una lista escrita a mano. Sin año, no hay alias (regla ya vigente en `legal.py`).
- Artículos compuestos (`2.2.1.2`, `134A`, `861-1`) y listas (`7 y 8`, `13, 15 y 42`) se normalizan igual que el campo `article` del pasaje; un test por cada forma.
- `L_MAX` configurable (por defecto 4 de 8) para que la evidencia semántica siga entrando. Si la pregunta nombra más artículos que `L_MAX`, se toman en el orden de la pregunta.
- Si la pregunta nombra una norma sin artículo, no se inyecta nada: solo se añade el nombre canónico a la consulta. No se trae "el artículo 1" por defecto.
- Implementar como variante nueva `R6L` en `metadata_experiments.py`, sin cambiar `R6` (para compararlas), y como opción `locator=True` en `Retriever.retrieve` desactivada por defecto hasta la selección.
- Arreglar `diversify.parse_reference` para que delegue en el parser de B o marcarlo como obsoleto con un test que documente los fallos anteriores.

**Aceptación:**
- Tests unitarios: las 6 consultas de §2.1 resuelven al par correcto; ambiguos → sin inyección; norma ausente del corpus → sin inyección y sin error.
- Benchmark v1: R6L-bm25 frente a R6-bm25 y R0 en dev y validación, con bootstrap pareado (`kingscode/benchmark_analysis.py`). Meta: Evidence Completeness@8 en dev ≥ 0,90. Holdout solo con `post_selection_confirmation`, y solo si el equipo lo aprueba.
- Muestra oficial: las 4 preguntas con artículo explícito tienen su artículo en el top‑8; el resto no empeora en `legal_basis_any@10`.
- Latencia p95 del locator < 5 ms por consulta.

```
Lee CLAUDE.md y docs/CORPUS_V02_PLAN.md completo. Tarea C1. Primero muéstrame el plan
(archivos, funciones, tests, cómo medir) y espera mi aprobación. Implementa el locator exacto
según la sección C1: parser de kingscode/reasoning/legal.py (respaldo scripts/citations.py),
LocatorIndex desde passages.jsonl solo con pasajes elegibles, alias ley/decreto→código tomados
del manifest, inyección de hasta L_MAX pasajes antes del ranking general, variante R6L sin
tocar R6. Tests para las 6 consultas de la tabla 2.1, listas, artículos compuestos y ambiguos.
Mide R0, R6 y R6L en dev y validation con bootstrap pareado. No corras holdout. No cambies
el default de retrieve() ni código de B. Reporta solo números de archivos generados en esta sesión.
```

### C2 — Benchmark v2 representativo (antes de elegir cualquier configuración)

**Composición objetivo:** unos 80 casos nuevos, con los mismos splits 60/20/20 por área.

| Tipo | Cómo se crea | Quién |
|---|---|---|
| `exact_reference` | ya existe (v1) | — |
| `graph_remission` / `modification` | plantillas deterministas desde aristas `REMITE_A` / `MODIFICA` con evidencia | Claude Code |
| `jurisprudence_by_id` | plantilla: "¿Qué decidió la Corte en la Sentencia X?", gold = sección RESUELVE | Claude Code |
| `semantic_rule`, `exception`, `conceptual`, `scenario` | pregunta en lenguaje natural sin número de artículo, redactada a partir del texto fuente; gold = pasajes que la responden | **persona del equipo** (40–50 casos, unos 2 minutos cada uno) |

**Reglas:** nada de la muestra oficial ni de las 992; ningún modelo cerrado redacta ni parafrasea; cada caso guarda autor, pasaje fuente y fecha; Claude Code prepara la herramienta de autoría (CLI o formulario) y valida el esquema, pero no escribe las preguntas semánticas.

**Aceptación:** `benchmarks/kingscode_ir_v2/` con manifest, esquema validado, sin solapamiento con v1, y R0/R6L medidos por tipo de pregunta.

```
Tarea C2 de docs/CORPUS_V02_PLAN.md. Plan primero. Construye benchmarks/kingscode_ir_v2 con:
(1) generadores deterministas para graph_remission, modification y jurisprudence_by_id desde
el grafo y los pasajes, con evidencia textual; (2) una herramienta de autoría para que una
persona escriba casos semánticos (pregunta, pasajes gold, autor, fecha) con validación de
esquema. No redactes preguntas semánticas tú mismo ni uses la muestra oficial. Mide R0 y R6L
por tipo en dev cuando existan al menos 20 casos humanos.
```

### C3 — Adquisición dirigida (P2 + P5 + gaps de la muestra)

**Cola priorizada, determinista y guardada en `reports/acquisition_queue_v02.json`:**
1. Faltantes del `legal_basis` de la muestra: Ley 472 de 1998, C-468/2024, SU-16/2020, SU-277/2025.
2. Los 28 de `reports/acquisition_backlog_v06.json`, primero `source_unavailable` y `not_found` con número y año completos.
3. Nodos externos `resolved=false` del grafo, ordenados por (número de aristas entrantes) × (peso del área en el banco, tabla §4.2 del enunciado) y bonificados si el área tiene poca cobertura. Solo leyes, decretos y sentencias con número y año completos. Tope: los 40 primeros.

**Fuentes, en este orden:** Función Pública → Secretaría del Senado → SUIN-Juriscol → relatorías oficiales. Se permite la URL pública del buscador oficial; no se permiten mirrors privados.

**Aceptación:** cada documento nuevo cumple §3.2.1–3.2.3; el parser `legal-blocks` lo procesa sin excepciones o va a backlog con el error; `norm_name` reproduce su `canonical_body` con `citations.extract` (test obligatorio); el reporte muestra adquiridos, fallidos por clase y cambio de cobertura de la muestra.

```
Tarea C3 de docs/CORPUS_V02_PLAN.md. Plan primero. Genera la cola priorizada de adquisición
según C3 (faltantes de legal_basis de la muestra, backlog v0.6, nodos externos del grafo
ponderados por área). Muéstramela antes de descargar. Luego adquiere en corpus_v02/ con
acquisition.py sin tocar corpus/. Verifica identidad (tipo/número/año en el título descargado),
TLS y hash. Lo que falle va al backlog con su clase y error literal. No sustituyas normas ni
uses mirrors no oficiales. Añade un test de que cada norm_name nuevo reproduce su
canonical_body con scripts/citations.py.
```

### C4 — Cortes, acotado

**Alcance:** solo sentencias identificadas por número (C-, T-, SU-, SL, SC, SP, STC… de la CSJ; radicados del Consejo de Estado) que (a) cita el propio corpus con número y año, o (b) aparecen en `seed_targets.json` o en el `legal_basis` de la muestra. Tope: 60 decisiones nuevas. Sin rastreo de buscadores ni descargas por lote.
**Estructura:** segmentar por encabezados reales (ANTECEDENTES, PROBLEMA JURÍDICO, CONSIDERACIONES, DECISIÓN/RESUELVE, SALVAMENTO) con el regex que ya existe en `corpus.py`, añadiendo metadatos (corte, sala, fecha, ponente) solo si están en la primera página. Aristas `EXEQUIBLE`/`INEXEQUIBLE` solo desde el RESUELVE con la frase literal.
**Aceptación:** encabezado del pasaje "Sentencia X de AAAA" reconocible por `citations.extract`; tests con 3 sentencias reales; cobertura de jurisprudencia por área antes/después.

### C5 — Metadatos de vigencia explícitos

**Hacer:** extraer de las notas de la fuente las frases "Derogado por…", "Modificado por…", "Adicionado por…", "Declarado INEXEQUIBLE…", "Rige a partir de…". Guardar `status_evidence` con la frase y el offset, y `source_of_status` con la URL. No inferir nada más.
**Importante para B:** `unknown` nunca bloquea respuestas ni dispara abstención (`policy.py` ya lo hace así desde T3; comprobar que siga igual).
**Aceptación:** conteo de documentos con al menos un estado explícito; 20 casos revisados a mano por el equipo con 0 falsos positivos.

### C6 — Construir v0.2 y comparar

**Hacer:** `tools/member_a.py build --corpus corpus_v02`; BM25 (y denso si hay GPU); métricas v0.1 vs v0.2 con la misma configuración en benchmark v1, v2 y la muestra oficial (`legal_basis_any@10`, techo de citas de `tools/analyze_citation_ceiling.py`).
**Criterio de adopción:** v0.2 no empeora Evidence Completeness@8 en v1 ni en v2 (IC 95 % del bootstrap) y mejora la cobertura de la muestra. Si no se cumple, se queda v0.1 y se documenta.

### C7 — Selección de retriever con pesos (solo con datos)

Solo cuando existan corridas densas reales en la 4090 **y** benchmark v2 con al menos 20 casos semánticos: RRF ponderado (peso BM25 vs denso) elegido en validación, reportado por tipo explícito vs semántico. Si el denso gana en semánticas, se queda aunque pierda en explícitas: el locator ya cubre las explícitas.

### C8 — Internacional (backlog)

Solo decisiones CAN relacionadas con propiedad industrial y competencia que el corpus ya cita (p. ej., reglamentos de la Decisión 486). OIT y tratados de derechos humanos: backlog documentado, no se adquieren esta semana, porque el banco excluye derecho internacional (§4.2 del enunciado).

---

## 5. Calendario

| Día | A (Luis) | B (Esteban) | Compartido |
|---|---|---|---|
| Lun 28 noche | C0 | revisar este plan | — |
| Mar 29 | C1 locator | integrar locator en `Pipeline` (flag) + decoder en GPU | charla SDLC |
| Mié 30 | C3 adquisición | workshop NVIDIA (todo el día) | autores de benchmark v2: 20 casos |
| Jue 1 | C4 cortes (acotado), C5 | bakeoff de decoders con retrieval congelado | 20 casos más de v2 |
| Vie 2 12:00 | C6 construir y comparar; **freeze candidato** | ensayo de 992 preguntas cronometrado | reporte de avance 17:00 |
| Vie 2 noche | publicar corpus + índice en la nube | congelar config final | verificación en ventana privada |
| Sáb 3 | nada cambia | ejecución ciega | verificación en vivo |

Si C3/C4 no terminan el viernes a las 12:00, se entrega v0.1 más locator. Llegar con un corpus a medio construir es peor que llegar con uno más pequeño y bien verificado.

---

## 6. Qué no hacer

- Descargar sentencias en masa o rastrear buscadores.
- Meter convenios o tratados "por si acaso".
- Cambiar el default de `retrieve()` sin una selección en validación registrada.
- Correr holdout más de una vez por configuración seleccionada.
- Tomar decisiones de pesos BM25/denso con el benchmark v1.
- Declarar una mejora sin intervalo de confianza o sin la ruta del reporte.
