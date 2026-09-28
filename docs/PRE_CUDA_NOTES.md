# Notas de inspección pre-CUDA

Actualización de A: ya existe corpus y baseline BM25. Diagnóstico local en `../reports/hardware.json`: PyTorch CPU, CUDA no disponible. Se ejecutó smoke real de los modelos de retrieval; la configuración de la 4090 y el benchmark completo siguen pendientes. Las notas siguientes conservan el contexto inicial; estado vigente en `KINGSCODE_STATE.json`.

## Starter pack observado
- 19 archivos oficiales.
- `sample_50.jsonl`: 50 ítems únicos.
  - 15 `multiple_choice`
  - 30 `semi_open`
  - 5 `open_ended`
  - 10 áreas jurídicas representadas.
- `seed_targets.json`: 186 documentos/fuentes iniciales, todos con nombre y URL únicos en el archivo observado.
- El ejemplo oficial contiene 5 respuestas y está deliberadamente incompleto.

## Comportamiento reproducido del evaluador oficial
Al correr el ejemplo sin `--ragas`:
- reporta 45 ítems faltantes, como anuncia su README;
- detecta 7 aciertos de citación y los 7 están respaldados;
- la corrección RAGAS queda pendiente;
- no requiere CUDA.

## Decisiones que NO se toman todavía
- versión de PyTorch;
- CUDA toolkit local;
- decoder definitivo;
- cuantización;
- encoder definitivo;
- librería de inferencia.

Estas decisiones dependen de la GPU/driver/VRAM reales y se toman después de
`tools/check_cuda.py`.

## Observación sobre seed_targets
Los valores de `donde_buscar` son puntos de búsqueda iniciales, no necesariamente
URLs directas al documento final. Debe guardarse la URL final y metadatos reales
durante la construcción del corpus, sin alterar el starter pack oficial.
