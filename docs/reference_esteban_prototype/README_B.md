# KingsCode — Capa B (query, generación, guardas, evaluación, entrega)

## Estructura

```
oficial/            material oficial sin modificar (data/, scripts/, schema/)
configs/            una configuración JSON por experimento
src/b/
  config.py         Config: todos los parámetros de una corrida (se guarda con hash)
  contract.py       contrato A→B, retriever mock, verificación de encabezados
  query.py          B1 normalize_query (usa citations.py oficial)
  router.py         B2 route_graph, RRF entre consultas, lookup exacto primero
  prompts.py        plantillas por formato y sub_tarea + JSON schema guiado
  llm.py            backend OpenAI-compatible (vLLM / Ollama / llama.cpp) y mock
  answer.py         pregunta → fila del esquema oficial, con respaldos deterministas
  guard.py          B4 citation_guard: réplica exacta del chequeo de respaldo del evaluador
  validate.py       jsonschema oficial + evaluate.validate
  pipeline.py       comando único, caché reanudable, evaluación y bitácora CSV
src/retrieval_adapter.py   punto de unión con A (A lo implementa)
interfaz/app.py     interfaz Streamlit
tests/              pruebas de citas, guarda y normalizador
runs/               una carpeta por corrida + experimentos.csv
```

## Uso

```bash
pip install -r requirements.txt
cd src

# 1. harness sin GPU ni corpus (debe dar 0 errores de validación)
python -m b.pipeline --split sample --config ../configs/mock.json

# 2. con decoder real (levantar primero el servidor, ver abajo)
python -m b.pipeline --split sample --config ../configs/qwen3_vllm.json

# 3. solo cuando valga la pena (gasta crédito de OpenRouter)
python -m b.pipeline --split sample --config ../configs/qwen3_vllm.json --ragas

# 4. sábado
python -m b.pipeline --split none --input ../oficial/data/test_992.jsonl \
       --config ../configs/final.json --out ../submissions.jsonl
```

Cada corrida queda en `runs/<tag>_<hash>/` con `config.json`, `cache.jsonl`,
`log.jsonl`, `submissions.jsonl`, `validacion.txt` y `reporte.json`, y agrega una
fila a `runs/experimentos.csv`. Si se cae, se vuelve a lanzar y continúa.

## Servidor del decoder

vLLM (Linux/WSL2 con GPU NVIDIA, el más rápido por batching):

```bash
vllm serve Qwen/Qwen3-8B-AWQ --max-model-len 16384 --gpu-memory-utilization 0.9 --seed 20261003
```

Ollama (Windows/Mac, más lento, concurrency 1–2):

```bash
ollama pull qwen3:8b && ollama serve
```

## Reglas que el código hace cumplir

- Temperatura 0, `seed` fijo, thinking desactivado.
- Solo se leen los campos de entrada de las preguntas (`FIELDS_IN`); nunca `legal_basis` ni respuestas.
- Ninguna cita sale sin respaldo en los 10 primeros pasajes (guard.py). La guarda es automática y queda registrada en `log.jsonl`.
- Ninguna fila queda inválida: si el modelo falla, hay respaldo determinista y se registra en `fallbacks`.
- `pasajes_recuperados` entrega exactamente los 10 que el evaluador usa como respaldo.

## Interfaz

```bash
streamlit run interfaz/app.py -- --config configs/qwen3_vllm.json
```
