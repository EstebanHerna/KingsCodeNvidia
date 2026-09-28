# Gate 2-Prep — preparación entregada, validación pendiente

Base: `254fa3a1ecd528137943007ef8946d9662d5bab7`, rama `main`. Alcance: preparar la ejecución futura en la RTX 4090, conservando Gate 1A y Gate 1B.

**La instrucción final del usuario fue hacer los cambios seguros en main sin correr pruebas.** Por ello no se ejecutaron tests, smokes, CUDA, decoders, benchmarks ni RAGAS durante esta preparación. Las dos verificaciones están preparadas para el siguiente entorno. Los 60 tests/5 puntos del dummy son históricos; no se presentan como resultados de esta entrega. No se afirma que BF16 quepa ni que el nuevo backend esté validado en ejecución.

## Preparado

- Cuatro decoders fijados a revisiones reales del Hub oficial y licencias documentadas; los dos locks originales de retrieval se conservan. Salamandra/Llama requieren aprobación manual de acceso. No se descargaron pesos de decoders.
- Configuración común BF16, batch 1, contexto 8192, temperatura 0, seed 0, límites por formato, control opcional y fallbacks explícitos sin sustitución de modelo.
- Backend local lazy compatible con el protocolo existente; templates del snapshot, prompts `grounded-formats-v2`, JSON intermedio estricto, datos públicos y evidencia literal. Conserva las guardas de B.
- Diagnóstico y plan de instalación sin instalar ni adivinar CUDA; preparación de caché con verificación Git/LFS, hashes locales y ejecución offline.
- GPU smoke futuro, matriz R0–R5, freeze de evidencia y CLI `decoder-smoke`, `sample`, `bakeoff`. `smoke` conserva el flujo dummy anterior.
- Registry para score oficial, JSON/citas/abstención, tiempos, tokens, throughput, VRAM, errores/OOM, configuración y hashes. No se han poblado resultados reales de estos experimentos.
- 28 tests nuevos con mocks, sin ejecutarlos; comandos de verificación en dos procesos preparados. No se implementó fine-tuning.

## Archivos nuevos

Configuración: `config/decoder_bakeoff.json`, `config/experiment_matrix.json`, `config/evaluation_gpu.json`.

Modelos/entorno: `kingscode/model_assets.py`, `kingscode/gpu_environment.py`, `requirements-gpu.txt`, `requirements-quantization.txt`.

Generación y experimentos: `kingscode/generation/__init__.py`, `config.py`, `prompts.py`, `hf_decoder.py`, `experiments.py`, `retrieval_experiments.py`, `gpu_smoke.py`.

Herramientas: `tools/prepare_gpu_environment.py`, `tools/prepare_models.py`, `tools/gpu_smoke.py`, `tools/retrieval_matrix.py`, `tools/verify_gate2_prep.py`.

Pruebas preparadas: `tests/test_gpu_preparation.py`.

Documentación/evidencia: `docs/GPU_DAY_RUNBOOK.md`, `docs/MODEL_LOCKS_GATE2.md`, `reports/gate2_prep/model_sources.json` y este informe.

## Archivos actualizados

`config/models.lock.json`, `config/strategy.json`, `tools/member_b.py`, `tools/verify_member_b_second.py`, `AGENTS.md`, `START_HERE.md`, `README.md`, `docs/KINGSCODE_STATE.json`, `docs/KINGSCODE_MASTER_KNOWLEDGE.md`, `docs/DECISION_LOG.md`, `docs/ROADMAP.md`, `docs/MODEL_STRATEGY.md`, `docs/MEMBER_B_RUNBOOK.md`, `docs/INTEGRATION_CONTRACTS.md`, `docs/VERIFICATION.md`.

La auditoría antigua de B ahora acepta entradas adicionales de decoders en el lock, pero compara las dos entradas originales de A exactamente. Los módulos originales de A y B, los tests previos, `config/reasoning.json`, `config/neural.json` y el corpus no se modifican. No se modifican archivos oficiales ni outputs previos.

Comprobación de integridad de archivos, sin ejecutar el pipeline: los **19 hashes oficiales** coinciden; también coinciden los hashes conservados de pasajes, grafo y BM25. La revisión del diff confirma que los módulos originales A/B y tests previos no cambiaron. Esto es una comprobación estática de archivos, no una prueba funcional del código nuevo.

## Limitaciones y próximos pasos

- Validación funcional y regresiones: pendientes de ejecutar en la siguiente sesión, incluyendo ambos comandos `verify_gate2_prep.py`.
- Stack/driver/PyTorch, VRAM real, compatibilidad de templates y memoria del contexto: pendientes de la máquina objetivo.
- Descargar/verificar pesos requiere red y, para modelos gated, acceso aprobado. El caché y el corpus no están en Git; transferir el snapshot del corpus a la otra máquina.
- Los modelos nominales Qwen3-8B/Llama 8B tienen conteos oficiales algo superiores a 8.000.000.000 parámetros. Se documenta la necesidad de aclarar elegibilidad antes de entrega competitiva.
- Los decoders se comparan con retrieval congelado. Latencia de generación y retrieval se miden separadamente; no se inventa latencia end-to-end.
- La guarda autentica citas/procedencia, no implicación semántica general. Las reglas de abstención y formato siguen requiriendo calibración con resultados reales.

Primer comando exacto frente a la 4090, desde el checkout:

```powershell
git pull --ff-only origin main
```

Después seguir [el runbook GPU](../docs/GPU_DAY_RUNBOOK.md): verificar commit → venv/snapshot → preflight/verificaciones → diagnóstico → stack compatible → modelos → GPU smoke → R0–R5 → freeze → D1–D3. No marcar CUDA ni bakeoff completados antes de revisar los resultados reales.
