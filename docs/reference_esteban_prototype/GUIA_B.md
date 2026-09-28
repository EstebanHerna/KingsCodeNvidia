# Guía del rol B — KingsCode, Hackathon 2026

## 1. El reto en una frase

Les dan preguntas de derecho colombiano. Su sistema busca los artículos o sentencias pertinentes en un corpus que ustedes construyen (eso es A) y un modelo abierto de 8B o menos redacta la respuesta en un JSON con formato fijo, citando solo lo que encontró (eso es B). Un script oficial (`evaluate.py`) califica automáticamente 80 de los 100 puntos.

Flujo de una pregunta:

```
pregunta ─► B1 normalizar ─► A retrieve() ─► B2 ¿grafo? ─► pasajes (top 10)
                                                              │
                          submissions.jsonl ◄─ B4 guarda ◄─ B3 LLM (temp 0, JSON)
```

## 2. Cómo se califica (esto define todo lo que hace B)

| Componente | Pts | Qué mide | Qué campos lee |
|---|---:|---|---|
| Cerradas | 20 | % de letras correctas en selección múltiple | `respuesta_correcta` |
| RAGAS | 30 | un LLM juez compara su texto con la respuesta esperada (hechos correctos vs sobrantes/faltantes) + similitud semántica | semi_open: solo `respuesta`; open_ended: los 4 campos |
| Citas | 20 | recall de normas citadas vs `legal_basis`, penalizado ×2 por cada cita sin respaldo | MC: `justificacion`; semi: `respuesta` + `referencia_legal`; open: los 4 campos |
| Abstención | 10 | acertar = 1, abstenerse = 0,5, fallar = 0 | `abstencion` |
| Manual | 20 | interfaz, bitácora de corpus, video, reproducibilidad | — |

Referencia a batir: un modelo de frontera saca 0,905 en cerradas y 0,451 en RAGAS.

### Hallazgos al leer `evaluate.py` y `citations.py`

1. Las citas se comparan a nivel de cuerpo normativo, no de artículo. "Ley 1010 de 2006" vale lo mismo que "artículo 2 de la Ley 1010 de 2006". El artículo ayuda al jurado humano, no al puntaje.
2. Una cita está "respaldada" si la misma norma aparece en el texto de alguno de los 10 primeros `pasajes_recuperados`. Por eso cada pasaje debe empezar con el nombre de la norma (tarea de A, verificada por B con `contract.check_passage`).
3. Una cita incorrecta pero respaldada no resta. Una cita sin respaldo resta el doble. Consecuencia: la guarda de citas es la pieza de mayor retorno de B. Con la guarda, `tasa_sin_respaldo` = 0 siempre.
4. `referencia_legal` (semi_open) y `justificacion` (MC) cuentan para citas pero no van al juez RAGAS. Ahí el código escribe las normas de los pasajes usados sin ensuciar la respuesta que lee el juez.
5. Abstenerse casi nunca conviene. En la muestra, una cerrada vale 1,33 pts de accuracy y 0,23 de abstención: abstenerse solo gana si la probabilidad de acertar es menor a 7 %, y con 4 opciones el azar ya da 25 %. En texto libre, abstenerse da 0,12 pts; responder da en promedio 0,3–0,4 solo en RAGAS. Política: abstenerse únicamente si no hay evidencia; el umbral se calibra con la muestra y se reporta.
6. Alias peligrosos del extractor oficial: "C.P." se lee como Constitución (no Código Penal), "CC" como Código Civil, "ET" como Estatuto Tributario. El prompt prohíbe abreviaturas y la guarda elimina lo que se cuele.
7. RAGAS castiga afirmaciones sobrantes. Respuestas cortas, directas y con la norma principal rinden más que respuestas largas.
8. Solo con repetir las normas que menciona la propia pregunta, sin corpus ni modelo, el harness ya obtiene 5,7/20 en citas. Muchas preguntas traen su fundamento en el enunciado; por eso existe la búsqueda exacta (`lookup_first`).
9. El test del sábado trae `sub_tarea` (Definición básica, Reproducción literal, Conflicto normativo...). B la usa para elegir instrucciones específicas por tipo de pregunta.

## 3. Correcciones al plan v0.5

| Punto del plan | Problema | Corrección |
|---|---|---|
| Grafo como pieza central | Las citas se puntúan por cuerpo normativo; el grafo artículo→parágrafo casi no mueve el puntaje y consume días | Grafo OFF por defecto. Lo que sí rinde es la búsqueda exacta: si la pregunta dice "artículo 60 del CST", traer ese artículo directo. Grafo solo para remisiones/derogaciones y solo si la medición OFF vs AUTO lo justifica |
| ALIA-es-legal como candidato fuerte | Entrenado con derecho español (7,4 M de instrucciones sintéticas, España) sobre Salamandra-7B, contexto de 8k. Riesgo de citar normas españolas y de JSON inestable | Mantenerlo como control, no como favorito. Prioridad: Qwen3-8B. Revisar también Qwen3.5-4B y Gemma-4-E4B (8B contando embeddings: preguntar si cumple) |
| Bakeoff de 4 decoders | No hay tiempo para 4 | Dos (Qwen3-8B vs ALIA) con retrieval congelado; un tercero solo si sobra tiempo |
| Sin plan de tiempo para el sábado | 992 preguntas entre 9:00 y 15:00, compartiendo la mañana con la interfaz. Ollama secuencial a ~40 tok/s puede tardar 3+ horas | vLLM con concurrencia (minutos), caché reanudable, ensayo completo cronometrado el jueves |
| Faltaba qué pasa si el modelo devuelve JSON roto | Una fila inválida cuenta como fallo | Decodificación guiada por JSON schema + parser tolerante + respaldo determinista registrado |
| Pocos-ejemplos con la muestra | "Indexar material que contenga respuestas esperadas" descalifica; usar las 50 en el prompt es zona gris | No usarlas en prompts hasta que lo confirmen el lunes |
| Nada sobre el modelo cerrado | Usar Claude/GPT para generar datos, reescribir preguntas o corregir respuestas descalifica | Todo el pipeline corre con modelos abiertos; el código puede escribirse con ayuda, pero ninguna salida del sistema pasa por un modelo cerrado |

## 4. Lo que ya está construido (repo `kingscode_b`)

Todo lo de B0, B1, B2, B4, B5 y la base de B6 está implementado y probado:

- `normalize_query`: limpia sin reescribir, corrige errores de digitación frecuentes ("constitucipon", "Sentencia C 145"), extrae normas con el extractor oficial y añade expansiones controladas (acción popular → Ley 472 de 1998, etc.).
- `route_graph`: determinista; activa grafo con señales de vigencia/derogación/remisión/jerarquía, con 2+ normas en la pregunta o con score bajo.
- Recuperación desde B: consulta principal + una consulta por opción en cerradas, fusionadas con RRF; los pasajes de normas nombradas en la pregunta suben al frente.
- `answer`: prompt por formato y sub_tarea, JSON guiado, el modelo razona sobre cada opción antes de elegir letra, declara qué pasajes usó y el código arma las referencias desde esos pasajes.
- `citation_guard`: misma lógica exacta del evaluador; quita oraciones con citas sin respaldo.
- `validate_submission`: esquema oficial + validación del evaluador.
- `pipeline`: comando único, concurrencia, caché reanudable, reporte y fila en `runs/experimentos.csv`.
- Interfaz Streamlit con respuesta, evidencia y JSON.
- Verificado: 50/50 filas, 0 errores de validación, 0 citas sin respaldo, 5 pruebas unitarias pasando. Puntaje con mocks (sin corpus ni modelo, siempre "A"): 16,33/50. Esa es la línea base que todo lo real debe superar.

## 5. Qué tienes que hacer, en orden

### Domingo noche / lunes antes de las 9:00
1. Descomprimir `kingscode_b.zip` dentro del repo del equipo y correr:
   `pip install -r requirements.txt && cd src && python -m b.pipeline --split sample --config ../configs/mock.json`. Debe decir 0 errores.
2. Guardar la llave en `oficial/scripts/.env` (ya está en `.gitignore`). No correr `--ragas` todavía.
3. Pasarle a A el contrato: `src/b/contract.py` (docstring) y `src/retrieval_adapter.py`. Punto no negociable: cada pasaje empieza con el nombre completo de la norma, usando nombres que `citations.py` reconoce ("Código Civil", no "Ley 57 de 1887").

### Lunes (sesión de preguntas 17:00)
Llevar estas preguntas:
- ¿Gemma-4-E4B (4,5B efectivos, 8B con embeddings) cumple el límite de 8B?
- ¿Se pueden usar preguntas de la muestra como ejemplos en el prompt?
- ¿`test_992.jsonl` trae `sub_tarea`, `tema` y `area`, como la muestra?
- ¿La guarda automática que elimina citas sin respaldo cuenta como "edición manual"? (Es código, se declara en el informe.)
- ¿En la verificación en vivo re-ejecutan preguntas y comparan byte a byte? (vLLM con batching puede variar mínimamente aun con temperatura 0.)
- ¿Qué hardware hay en la sala Turing el sábado?

### Martes
4. Levantar el decoder. Con GPU NVIDIA y Linux/WSL2: `vllm serve Qwen/Qwen3-8B-AWQ ...`. Sin GPU: Colab T4 con vLLM y túnel, solo para desarrollo.
5. Correr `configs/qwen3_vllm.json` con el retriever mock para probar formato y latencia real. Revisar `runs/*/log.jsonl`: `fallbacks` debe ser casi 0.

### Miércoles (workshop NVIDIA, todo el día)
6. Mínimo: dejar corriendo una evaluación con el primer retriever real de A.

### Jueves
7. Bakeoff: Qwen3-8B vs ALIA, mismo retriever, misma muestra. Una sola corrida con `--ragas` por modelo finalista.
8. Ajustar `k` (5, 8, 10), `mc_option_queries` y `graph_mode` (off vs auto). Una variable a la vez; todo queda en `experimentos.csv`.
9. Ensayo del sábado: correr 992 preguntas sintéticas (la muestra repetida) y cronometrar. Objetivo: menos de 90 minutos.

### Viernes antes de las 17:00
10. Reporte de avance: puntaje de `experimentos.csv`, estado del corpus (lo da A), arquitectura, riesgos. Enviar con el asunto exacto.

### Sábado
11. 9:00: congelar índice y config (`configs/final.json`), lanzar las 992.
12. Mientras corre: pulir la interfaz y el README.
13. Validar `submissions.jsonl` (0 errores), subir repo, verificar el enlace del corpus en ventana privada antes de las 15:00.

## 6. Riesgos y mitigación

| Riesgo | Mitigación |
|---|---|
| No hay GPU propia el sábado | Confirmar hoy qué máquina corre; si es Ollama, bajar `k` y medir tiempo ya |
| A se atrasa | B avanza con el retriever mock y con fixtures; el contrato no cambia |
| JSON roto o thinking activado | JSON schema guiado, `enable_thinking=False`, respaldo determinista |
| Gastar los 20 USD de OpenRouter | `--ragas` solo en corridas candidatas; iterar con los 50 pts deterministas |
| Citas sin respaldo | Guarda automática, ya probada |
| Sin tiempo para la interfaz | Ya existe en Streamlit; el sábado solo se ajustan colores |
