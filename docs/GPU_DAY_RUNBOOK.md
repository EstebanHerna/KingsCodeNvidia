# Gate 2A + 2B — día de la RTX 4090

Estado de esta entrega: **infraestructura preparada, sin pruebas ejecutadas por instrucción expresa del usuario**. No se instaló CUDA/PyTorch GPU, no se descargaron decoders y no hay resultados de la 4090. Los 60 tests y el score dummy de Gate 1B son resultados históricos, no validación del código nuevo. Hay 28 tests nuevos preparados para CPU con mocks.

El router sigue siendo determinista; no tiene prompt ni LLM. Los prompts nuevos son para la respuesta final. Gate 1B conserva su backend y configuración; `smoke` sigue siendo dummy.

## 1. Sincronizar main y registrar el commit

Abrir PowerShell en la raíz del repositorio. Primer comando:

```powershell
git pull --ff-only origin main
```

No sobreescribir cambios locales. Verificar la rama, el commit recibido y la ascendencia del estado de partida:

```powershell
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor 254fa3a1ecd528137943007ef8946d9662d5bab7 HEAD
if ($LASTEXITCODE -ne 0) { throw 'El checkout no parte del estado aprobado.' }
if ((git rev-parse HEAD) -ne (git rev-parse origin/main)) { throw 'HEAD difiere de origin/main.' }
```

Comparar también el SHA con el commit final comunicado en la entrega. Guardarlo junto a los reportes; no confundir una revisión posterior de main con el código revisado aquí.

## 2. Entorno Python y snapshot del corpus

Usar Python 3.12 de 64 bits, compatible con el entorno de desarrollo y con la build que se seleccione. Evitar heredar paquetes globales de otra instalación.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
python -m pip install --upgrade pip
python -m pip install -r requirements-knowledge.txt
```

**El corpus y los modelos no están en Git.** Si la GPU está en otra máquina, copiar el directorio `corpus` del snapshot actual (raw, clean, passages, grafo, índice y manifest), sin reconstruir ni volver a descargar fuentes. Si aún no existe en destino:

```powershell
if (-not (Test-Path -LiteralPath '.\corpus\manifest.json')) {
    $CorpusSnapshot = Read-Host 'Ruta completa del directorio corpus del snapshot conservado'
    if (Test-Path -LiteralPath '.\corpus') { throw 'Revisar el corpus parcial existente antes de copiar.' }
    Copy-Item -LiteralPath $CorpusSnapshot -Destination '.\corpus' -Recurse
}
```

## 3. Preflight y dos verificaciones pendientes

Estos comandos se dejan preparados; **no se ejecutaron en esta entrega**. Ejecutarlos antes de cargar modelos:

```powershell
python tools/preflight.py
if ($LASTEXITCODE -ne 0) { throw 'Preflight falló.' }
python tools/verify_gate2_prep.py --stage first
if ($LASTEXITCODE -ne 0) { throw 'Primera verificación falló.' }
python tools/verify_gate2_prep.py --stage second
if ($LASTEXITCODE -ne 0) { throw 'Segunda verificación falló.' }
```

Cada verificación ejecuta la suite completa en un proceso nuevo y reproduce el dummy. Compara el JSONL y fingerprint con Gate 1B, los 19 hashes oficiales, los módulos originales A/B, los dos locks de retrieval y los hashes del snapshot. Los tests nuevos simulan Transformers/CUDA mediante objetos de prueba; no descargan pesos ni realizan operaciones CUDA reales.

## 4. Diagnosticar y seleccionar PyTorch

```powershell
python tools/prepare_gpu_environment.py --diagnose --output reports/gpu_diagnostic.json
python tools/prepare_gpu_environment.py --plan --report reports/gpu_diagnostic.json --output reports/gpu_plan.json
Get-Content reports/gpu_diagnostic.json
Get-Content reports/gpu_plan.json
```

Este diagnóstico no hace matmul ni instala paquetes. Leer GPU, VRAM, driver, SO, Python, PyTorch instalado y CUDA reportada por PyTorch. `gpu_validated=false` sigue siendo correcto: inventariar no valida inferencia.

Si hace falta instalar/reemplazar PyTorch, seleccionar la versión/build en el [selector oficial](https://pytorch.org/get-started/locally/) y contrastar el driver con la [compatibilidad de NVIDIA](https://docs.nvidia.com/deploy/cuda-compatibility/). No escoger por el `nvcc` local ni asumir que el driver admite cualquier wheel. No se fija ahora una build CUDA.

```powershell
$TorchVersion = Read-Host 'Versión exacta estable seleccionada en PyTorch, por ejemplo X.Y.Z'
$CudaTag = Read-Host 'Tag CUDA de la wheel seleccionada, con forma cuNNN'
python tools/prepare_gpu_environment.py --plan --report reports/gpu_diagnostic.json --torch-version $TorchVersion --cuda-tag $CudaTag --output reports/gpu_plan_selected.json
if ($LASTEXITCODE -ne 0) { throw 'Selección inválida o sin GPU observada.' }
Get-Content reports/gpu_plan_selected.json
# Ejecutar únicamente después de revisar la compatibilidad de esa selección:
python -m pip install "torch==$TorchVersion" --index-url "https://download.pytorch.org/whl/$CudaTag"
if ($LASTEXITCODE -ne 0) { throw 'Instalación de PyTorch falló.' }
python -m pip install -r requirements-gpu.txt
python tools/prepare_gpu_environment.py --diagnose --output reports/gpu_diagnostic_installed.json
```

El plan nunca instala automáticamente ni certifica la compatibilidad de una selección escrita por el operador. Si CUDA sigue sin estar disponible, detenerse y corregir el stack antes de cualquier modelo.

## 5. Preparar y verificar modelos

Revisiones/licencias en `MODEL_LOCKS_GATE2.md`. Solicitar con anticipación el acceso manual a Salamandra y, si se usará, Llama. La licencia declarada y el acceso de la cuenta son comprobaciones distintas. `HF_TOKEN` o `hf auth login` pertenecen a Hugging Face, nunca se guardan en Git. No aceptar términos automáticamente en nombre de otros.

```powershell
python tools/prepare_models.py --list
# Si el acceso gated ya fue aprobado, autenticar la cuenta autorizada:
hf auth login
python tools/prepare_models.py --download-retrieval
if ($LASTEXITCODE -ne 0) { throw 'Retrieval: falta acceso o falló la preparación.' }
python tools/prepare_models.py --download-decoders
if ($LASTEXITCODE -ne 0) { throw 'Decoder: revisar aprobación de Salamandra y conectividad.' }
python tools/prepare_models.py --verify
if ($LASTEXITCODE -ne 0) { throw 'No ejecutar con modelos sin verificar.' }
```

El caché es `models/`, ignorado por Git. Se compara la revisión exacta y cada archivo con SHA-256 LFS o Git blob del Hub; se guarda un manifest local con hashes. `--verify` es offline. Se descargan también templates `.jinja`, vocabularios y todos los shards. La inferencia mantiene `local_files_only=true` y `trust_remote_code=false`.

Llama está deshabilitado por defecto. Para preparar el control opcional, con su acceso aprobado:

```powershell
python tools/prepare_models.py --download llama31-8b
python tools/prepare_models.py --verify llama31-8b
```

## 6. Smoke real y BF16 primero

```powershell
python tools/gpu_smoke.py --model qwen3-8b
if ($LASTEXITCODE -ne 0) { throw 'GPU smoke falló; revisar su informe antes de continuar.' }
```

Comprueba CUDA, matmul BF16, embeddings, reranking, generación real y guardas oficiales/de citas. Carga los modelos por etapas y libera memoria entre ellos. Reporta tiempos y VRAM medida; no cambia flags del estado del proyecto. Si no hay CUDA, termina con `CUDA_NOT_AVAILABLE`. Una abstención o fallo de formato en la prueba mínima de decoder no cuenta como respuesta grounded aprobada.

BF16 no se declara viable por tener 24 GB: depende del contexto, caché KV y runtime. Contexto común inicial: 8192 tokens, **incluyendo** la reserva de salida; batch 1. Si no cabe, se rechaza la entrada, sin truncar evidencia silenciosamente.

Ante OOM, conservar el `experiment.json` BF16 con modelo/revisión, contexto, evidencia, configuración y memoria. Primero estudiar ese registro. INT8/4-bit son experimentos separados; no se prueban automáticamente:

```powershell
python -m pip install -r requirements-quantization.txt
$OomRecord = Read-Host 'Ruta del experiment.json de decoder-smoke BF16 con CUDA_OOM'
python tools/gpu_smoke.py --model qwen3-8b --precision int8 --oom-record $OomRecord
```

El registro requerido está en la subcarpeta `decoder` del GPU smoke. Para un fallback de `sample`, usar un OOM de `sample` con el mismo freeze/contexto/configuración; un OOM de smoke no lo sustituye. El hardware/runtime de bitsandbytes también debe verificarse; no hay descarga de pesos cuantizados alternativos ni sustitución de revisión.

## 7. Gate 2A — índice y matriz de retrieval

Configurar explícitamente A después de validar el stack. Esta acción futura cambia solo sus parámetros de ejecución; no reconstruye el corpus:

```powershell
python tools/prepare_gpu_environment.py --configure-retrieval
python tools/member_a.py dense
if ($LASTEXITCODE -ne 0) { throw 'No continuar sin índice denso válido.' }
python tools/retrieval_matrix.py list
python tools/retrieval_matrix.py run --candidate R0
python tools/retrieval_matrix.py run --candidate R1
python tools/retrieval_matrix.py run --candidate R2
python tools/retrieval_matrix.py run --candidate R3
python tools/retrieval_matrix.py run --candidate R4
python tools/retrieval_matrix.py run --candidate R5
```

| Experimento | Retrieval | Grafo |
|---|---|---|
| R0 | BM25 | OFF |
| R1 | Dense | OFF |
| R2 | BM25 + Dense + RRF | OFF |
| R3 | R2 + reranker | OFF |
| R4 | R3 + router determinista de B | AUTO |
| R5 | R3 + expansión forzada | ON, ablation |

Las seis corridas usan la misma normalización de B y snapshot. Los labels solo se leen al calcular métricas después de recuperar. Los reportes incluyen Recall@1/3/5/10, MRR@10, cobertura, latencia y modo/decisión de grafo. R1 vs R2 cambia fusión; R2 vs R3 cambia reranker; R3/R4/R5 aíslan el grafo. R0 vs R1 compara el tipo de recuperador. No hay decoder en estas métricas.

Elegir según los resultados reales, no por una preferencia preasignada. Cada comando guarda una carpeta nueva y no pisa el baseline. Un fallo se registra y devuelve código no cero; revisar antes de continuar.

## 8. Congelar evidencia y ejecutar decoders

```powershell
$RetrievalRun = Read-Host 'Carpeta de la corrida R0-R5 seleccionada tras revisar las métricas'
python tools/retrieval_matrix.py freeze --run $RetrievalRun --output artifacts/retrieval_freeze.json
if ($LASTEXITCODE -ne 0) { throw 'Freeze inválido o ya existente; no sobrescribir.' }
python tools/member_b.py decoder-smoke --model qwen3-8b
if ($LASTEXITCODE -ne 0) { throw 'Decoder smoke falló.' }
python tools/member_b.py sample --model qwen3-8b
python tools/member_b.py sample --model alia-legal-7b
python tools/member_b.py sample --model salamandra-7b
```

Alternativa a los tres comandos `sample`: `python tools/member_b.py bakeoff`. Usa procesos separados, BF16 y el mismo archivo de evidencia; no ejecutar ambas variantes salvo que se quiera una repetición explícita. Llama opcional: `python tools/member_b.py sample --model llama31-8b --allow-optional`.

El freeze toma los primeros ocho pasajes de los rankings medidos en diez y conserva sus IDs, orden, texto, scores y procedencia. Todos los decoders reciben las mismas 50 preguntas públicas y esos mismos pasajes. Esto evita mantener encoder/reranker/decoder simultáneamente en VRAM. Las latencias de decoder no incluyen retrieval: la latencia de recuperación queda en el experimento R elegido. No presentar esa cifra como latencia end-to-end en vivo.

Los prompts tienen la misma versión lógica, con el template nativo de cada tokenizer. Qwen usa `enable_thinking=false`; generación greedy, temperatura 0, semilla 0 y límites comunes por formato. El modelo solo produce campos de respuesta/abstención; el sistema adjunta evidencia literal y pasa por las guardas existentes. JSON, formato o citas inválidos abortan esa corrida; no se reparan manualmente.

## 9. Evaluación, métricas y juez separado

Cada `sample` ejecuta el evaluador oficial intacto sin RAGAS y guarda `experiment.json`, `trace.jsonl`, `questions.jsonl`, `submissions.jsonl` y `evaluation.json`. Registra score, JSON válido, citas/tasa sin respaldo, abstenciones, p50/p95, tokens de entrada/salida, VRAM pico, throughput, errores/OOM, versiones y hashes. En fallos anteriores a la publicación solo quedan trazas y registro de error.

El juez RAGAS queda preparado en `config/evaluation_gpu.json`. **Ejecutarlo solo cuando exista autorización y llave**, por separado de la inferencia competitiva. OpenRouter no se usa para retrieval, prompts, respuestas ni datos de apoyo:

```powershell
# Solo después de obtener autorización para usar el juez:
python -m pip install -r scripts/requirements-evaluador.txt
$Submission = Read-Host 'Ruta del submissions.jsonl ya generado y validado'
$JudgeKey = Read-Host 'Llave autorizada de OpenRouter' -AsSecureString
$KeyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($JudgeKey)
try {
    $env:OPENROUTER_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($KeyPointer)
    python scripts/evaluate.py --submission $Submission --split sample --ragas
} finally {
    Remove-Item Env:\OPENROUTER_API_KEY -ErrorAction SilentlyContinue
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($KeyPointer)
}
```

No versionar llaves, pesos ni cachés. Guardar el JSON del juez aparte del registro determinista original y conservar el hash de la submission. No editar las respuestas después de evaluar.

## 10. Decisiones que siguen pendientes

CUDA y bakeoff solo se pueden declarar completados después de mediciones reales y revisión de reportes. No hay afirmación actual sobre que BF16 quepa ni sobre cuál modelo gana. Determinismo se comprueba en el mismo entorno fijado; no se garantiza igualdad bit a bit entre hardware/librerías diferentes.

Fine-tuning sigue bloqueado: retrieval bajo → mejorar corpus/recuperación y evaluar si hace falta FT del reranker; retrieval alto y errores generativos persistentes → considerar QLoRA en otra tarea. Esta entrega no contiene entrenamiento ni lo ejecuta.
