# Gate 1B — Harness pre-GPU

Implementación en `kingscode/reasoning/`. Consume la API pública de A sin cambiar sus módulos, corpus, índices ni grafo. El único backend habilitado por el comando `smoke` es `DummyDecoder`: siempre se abstiene y no carga modelos. Esto verifica integración, trazabilidad y evaluación; no mide calidad de razonamiento jurídico.

## Reproducir exactamente el flujo

Desde la raíz, con el entorno de A y su snapshot local disponibles:

```powershell
.venv/Scripts/python.exe tools/member_b.py smoke
```

El comando ejecuta las 50 preguntas, crea una carpeta nueva en `reports/member_b/` y devuelve sus rutas. Incluye normalización, primera recuperación OFF, routing, segunda recuperación cuando procede, política de abstención, dummy, citation guard, schema oficial y evaluador oficial sin `--ragas`. No requiere red, API keys, CUDA ni pesos de modelos.

Para comprobar todos los tests y repetir la auditoría independiente:

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe tools/verify_member_b_second.py
```

El segundo comando selecciona la corrida aprobada más reciente. `--run RUTA` permite indicar otra. Comprueba también que la implementación de A sigue idéntica al commit inicial `382c5eb`; por eso requiere el checkout Git con ese historial. Reconstruye la ejecución de B en otro proceso, sin reconstruir el corpus de A.

Si se parte de un clon nuevo, primero obtener el snapshot de A o seguir su runbook para adquirir/construir corpus. Volver a descargar las fuentes no garantiza los hashes del snapshot anterior. Dependencias de B: biblioteca estándar y `jsonschema`, ya incluido en `requirements-knowledge.txt`.

## Interfaces

```python
from kingscode import Retriever, retrieve  # Contrato de A conservado.
from kingscode.reasoning import (
    Question, normalize_query, route_graph, answer,
    citation_guard, validate_submission, run_eval,
    Pipeline, RetrieverGraphRouter,
)

adapter = RetrieverGraphRouter()
retriever = Retriever(mode="bm25", graph_router=adapter)
pipeline = Pipeline(retriever.retrieve, adapter=adapter)
question = Question(79, "Artículo 1 de la Ley 1010 de 2006", "semi_open")
row, trace = pipeline.run(question)

# Uso directo, sin orquestar retrieval:
passages = retrieve(question.text, 8, "off")
row = answer(question, passages, question.format)
validate_submission(row)  # Lanza error; no repara el output.
guard_report = citation_guard(row, passages)
```

`answer` acepta `Question` (ID real) o texto con `question_id=...`; el ID 0 por defecto solo sirve para consultas ad hoc, no para entregar el sample. Rechaza registros crudos del banco. El cargador proyecta exclusivamente `id`, `pregunta`, `formato` y `opciones`, y valida que las opciones solo contengan letras/texto. Las etiquetas no se pasan al normalizador, retrieval, router, política, prompt ni decoder. El evaluador oficial las lee únicamente en su proceso de calificación.

## Normalización y referencias

`normalize_query` devuelve `NormalizedQuery`: original, texto normalizado, texto de búsqueda, referencias con spans originales, autoridades, señales y expansiones. Solo aplica NFC/espacios al texto; conserva números, años, signos, negaciones y temporalidad. Añade hasta cuatro expansiones de un diccionario finito de alias, como CGP → Código General del Proceso. No genera preguntas adicionales. Abreviaturas ambiguas como C.P./C.C. no se expanden.

Reconoce referencias explícitas a normas con número/año, códigos, artículos simples/compuestos/con letra, listas de artículos, sentencias y radicados. No colapsa una ley a un código ignorando el año. Formas incompletas o no resueltas se conservan y bloquean su uso como cita respaldada. Los rangos textuales, referencias implícitas, subnumerales complejos y desambiguación jurídica general requieren ampliación/revisión futura.

## Router y adaptación a A

| Decisión | Condición inicial | Ejecución |
|---|---|---|
| OFF | Pregunta directa con evidencia compatible | Reutiliza la primera recuperación |
| AUTO | Evidencia plana débil, conflictiva o sin referencia explícita solicitada | El adaptador habilita expansión en A |
| ON | Relación normativa, jerarquía, temporalidad o retrieval vacío | Solicita expansión explícita |

El callback de A recibe solo texto y espera un booleano. `RetrieverGraphRouter` enlaza la decisión de B a la consulta exacta y devuelve `bool`, evitando que el string `"off"` active el grafo por ser truthy. Se usa una instancia por pipeline secuencial. Si el caller no proporciona adaptador, el coordinador resuelve AUTO a una llamada ON explícita y deja ambos valores en la traza. El grafo puede no aportar evidencia cuando no hay semillas; la política sigue absteniéndose. El número de activaciones no prueba mejora de retrieval ni del score.

## Política y guardas

- Abstención antes del backend ante consulta/retrieval vacíos, referencia explícita ausente/ambigua, evidencia léxica insuficiente, pasajes no elegibles, conflicto fuerte, vigencia no certificada o falta de evidencia de la relación solicitada.
- Conflictos mecánicos: mismo ID con textos distintos; misma norma/artículo/intervalo con textos distintos; textos del mismo artículo opuestos únicamente por negación modal. No pretende resolver todas las contradicciones jurídicas.
- El dummy también se abstiene cuando hay evidencia suficiente. Nunca copia una opción como respuesta sustantiva ni infiere una conclusión jurídica.
- Cada `pasajes_recuperados` conserva exactamente el texto de A y añade `passage_id`, `doc_id`, URL, identidad normativa, artículo, jerarquía, nodos y hashes disponibles. Omite offsets oficiales opcionales porque `text_prefix` de A no pertenece al intervalo clean.
- Citation guard verifica todas las cadenas emitidas, incluidos keywords y descarte de opciones. Exige fuente/artículo compatibles, referencia visible y evidencia incluida en la salida. Rechaza texto/URL/metadata alterados, pasajes duplicados, citas sin respaldo y respuestas no abstencionistas sin cita verificable. Una mera mención a otra ley dentro de un pasaje no lo convierte en evidencia del artículo de esa otra ley.
- La validación usa el schema oficial intacto, más comprobaciones de JSON estricto, evidencia no vacía para respuestas y máximo diez pasajes. Una salida inválida o una cita rechazada aborta la corrida y registra el fallo; no se publica un JSONL final parcial ni se edita manualmente.

### Contradicción oficial de opción múltiple

La descripción del schema dice que con abstención se admite `null`, pero el `enum` efectivo permite únicamente A/B/C/D, sin excepción. Se conserva el archivo oficial y se cumple su validación: abstención `true`, marcador formal `A`, descarte vacío y justificación que declara explícitamente que esa letra **no representa una elección**. No se consulta la opción esperada. El evaluador excluye estas filas de aciertos de cerradas por estar marcadas como abstención.

## Registro de experimentos

Cada carpeta contiene `questions.jsonl` (solo campos públicos), `submissions.jsonl`, `trace.jsonl`, `evaluation.json` y `experiment.json`. Este último fija:

- versión/hash de corpus y grafo, manifest y archivos oficiales;
- configuración de retrieval, routing, normalización, política, guardas, backend, prompt y generación;
- hashes de implementación de B y fingerprint del experimento;
- valid JSON rate, citas/errores de respaldo, abstenciones y motivos, modos de grafo, latencias, resultado oficial y rutas;
- estado aprobado/fallido, error cuando aplica y módulos neuronales cargados (ninguno en el smoke).

Las carpetas son nuevas por corrida. El fingerprint, JSONL final, decisiones y trazas sin tiempos son reproducibles; timestamps, rutas y latencias cambian. Cero citas emitidas implica tasa sin respaldo cero por convención, sin demostrar calidad de citas. La evidencia positiva/negativa de las guardas está en los tests.

## Límites y siguiente paso

No se ha ejecutado decoder real, calibración de confianza, RAGAS, interfaz de usuario, benchmark neuronal completo ni bakeoff. Gate 2-Prep añade código separado para esa fase, todavía sin probar por instrucción del usuario. La guarda comprueba identidad de cita y trazabilidad, no implicación semántica de toda una conclusión. Las reglas de routing/abstención son conservadoras y deben evaluarse por área al incorporar razonamiento real. Temperatura prevista: 0, `do_sample=false`, semilla 0.

Siguiente comando para repetir Gate 1B: `.venv/Scripts/python.exe tools/member_b.py smoke`. Revisar sus trazas y la segunda verificación antes de una tarea separada de integración del decoder/GPU; este gate no instala ni inicia esa fase.

## Comandos preparados para Gate 2

`decoder-smoke --model qwen3-8b`, `sample --model qwen3-8b` y `bakeoff` son ramas nuevas de `tools/member_b.py`. Admiten `--dry-run` para inspección futura sin modelos; no se ejecutaron durante la preparación. Usan `kingscode/generation/`, no sustituyen al dummy y vuelven a pasar por `answer`/citation guard/schema. `sample` requiere evidencia congelada y validada. Runbook completo: `GPU_DAY_RUNBOOK.md`.

La auditoría histórica `verify_member_b_second.py` ahora permite entradas adicionales de decoders en el lock, pero sigue exigiendo igualdad de las dos entradas originales de retrieval. Los informes anteriores que dicen 15 archivos intactos corresponden a Gate 1B; una ejecución futura distingue 14 archivos idénticos más dos entradas originales del lock.
