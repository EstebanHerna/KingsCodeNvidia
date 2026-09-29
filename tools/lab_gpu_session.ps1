# =====================================================================
# KingsCode - sesión en PC con GPU (cuenta de estudiante, sin admin)
# Windows PowerShell. Todo queda en carpetas del usuario; nada pide admin.
#
# Uso típico (desde cualquier carpeta):
#   powershell -ExecutionPolicy Bypass -File tools\lab_gpu_session.ps1 `
#       -Repo "$HOME\KingsCodeNvidia" -CorpusSnapshot "D:\kingscode_corpus_v01" `
#       -InstallTorch -DownloadModels -DecoderSmoke -FreezePlans -RunSample
#
# Qué NO hace (a propósito):
#   - benchmark v1, Search V2, validation/holdout v1, tuning;
#   - C0-C3 del benchmark independiente KC-COL-IR (tools/independent_ir_v2.py)
#     mientras A no tenga >=10 retrieval gold aceptados (gate de su manifest);
#   - volver a descargar el corpus desde las fuentes (cambiaría los hashes
#     que verifica A): usa el snapshot conservado por Luis (-CorpusSnapshot);
#   - --ragas (gasta los 20 USD de OpenRouter; solo con autorización).
# =====================================================================
param(
    [string]$Repo = "$HOME\KingsCodeNvidia",
    [string]$RepoUrl = "https://github.com/IngSeb0/KingsCodeNvidia.git",
    [string]$CorpusSnapshot = "",   # carpeta 'corpus' o .tar.gz del snapshot v0.1 de Luis
    [switch]$SkipTests,             # la suite tarda ~5 min en CPU
    [switch]$InstallTorch,          # instala PyTorch CUDA dentro del .venv (sin admin)
    [switch]$DownloadModels,        # retrieval Qwen 0.6B + decoders Qwen3-8B y ALIA (~35 GB)
    [switch]$DecoderSmoke,          # primera generación real del decoder
    [switch]$FreezePlans,           # congela planes Qwen para sample_50 (no necesita corpus)
    [switch]$RunSample,             # corrida end-to-end de sample_50 con Qwen3-8B + evaluador oficial
    [switch]$BuildDense             # paso de A: embeddings Qwen del corpus v0.1 (si A lo pide)
)
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"

function Step($msg) { Write-Host ""; Write-Host ">>> $msg" -ForegroundColor Cyan }
function Check($what) { if ($LASTEXITCODE -ne 0) { throw "STOP: $what (exit $LASTEXITCODE)" } }

# ---------------------------------------------------------------------
Step "[0] Repositorio en main (todo A+B ya está mergeado ahí)"
if (-not (Test-Path "$Repo\.git")) {
    git clone $RepoUrl $Repo; Check "git clone"
}
Set-Location $Repo
git fetch origin; Check "git fetch"
if (git status --porcelain) { git status --short; throw "STOP: hay cambios locales; guárdalos o usa otra carpeta." }
git checkout main; Check "git checkout main"
git pull --ff-only origin main; Check "git pull --ff-only"
$Sha = (git rev-parse HEAD).Trim()
Write-Host "main @ $Sha"
$Out = "reports\lab_session\$Stamp"
New-Item -ItemType Directory -Force $Out | Out-Null
$Sha | Out-File "$Out\git_sha.txt" -Encoding utf8

# ---------------------------------------------------------------------
Step "[1] Python del proyecto (.venv, sin activar: evita la política de ejecución)"
$Py = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $Py)) {
    $made = $false
    try { py -3.12 -m venv .venv; $made = ($LASTEXITCODE -eq 0) } catch { }
    if (-not $made) { python -m venv .venv; Check "python -m venv" }
}
& $Py --version
& $Py -m pip install --upgrade pip; Check "pip upgrade"
& $Py -m pip install -r requirements-knowledge.txt; Check "requirements-knowledge"

# ---------------------------------------------------------------------
if (-not $SkipTests) {
    Step "[2] Suite completa en CPU (~5 min; sin corpus se saltan 10 tests)"
    & $Py -m unittest discover -s tests; Check "tests"
}
& $Py tools\benchmark_v2.py check | Out-File "$Out\benchmark_v2_check.json" -Encoding utf8; Check "benchmark_v2 check"

Step "[3] Gate del benchmark independiente KC-COL-IR (informativo, no corta la sesión)"
$Gate = & $Py -c @'
import json
m = json.load(open("benchmarks/kc_col_ir_v0.1/manifest.json", encoding="utf-8"))
c = m.get("counts", {})
print(json.dumps({"benchmark": m.get("benchmark"), "cuda_ready": m.get("cuda_ready"),
                  "accepted_retrieval_gold": c.get("accepted_retrieval_gold", 0),
                  "needs_human_review": c.get("needs_human_review", 0),
                  "gate_open": bool(m.get("cuda_ready")) and bool(m.get("baseline_gate", {}).get("unlocked"))}))
'@
$Gate | Out-File "$Out\independent_ir_gate.json" -Encoding utf8
Write-Host $Gate
$GateOpen = ($Gate | ConvertFrom-Json).gate_open
& $Py tools\independent_ir_v2.py check | Out-File "$Out\independent_ir_check.json" -Encoding utf8

# ---------------------------------------------------------------------
Step "[4] Corpus v0.1 (snapshot de Luis; nunca re-adquirir aquí)"
if (-not (Test-Path "corpus\manifest.json") -and $CorpusSnapshot) {
    if ($CorpusSnapshot -like "*.tar.gz" -or $CorpusSnapshot -like "*.tgz") {
        $Files = Join-Path (Split-Path $CorpusSnapshot) "snapshot-files.sha256.json"
        if (Test-Path $Files) {
            & $Py tools\package_corpus_snapshot.py verify $CorpusSnapshot --files $Files; Check "verificación del snapshot antes de extraer"
        } else {
            Write-Host "AVISO: falta snapshot-files.sha256.json junto al .tar.gz; se extrae y se verifica después con verify_member_a_v02." -ForegroundColor Yellow
        }
        tar -xzf $CorpusSnapshot -C .; Check "tar -xzf snapshot"
    } else {
        Copy-Item -Recurse -LiteralPath $CorpusSnapshot -Destination ".\corpus"
    }
}
$HaveCorpus = Test-Path "corpus\manifest.json"
if ($HaveCorpus) {
    & $Py tools\verify_member_a_v02.py | Out-File "$Out\verify_member_a_v02.json" -Encoding utf8; Check "verify_member_a_v02 (hashes del snapshot)"
    Write-Host "Corpus verificado contra los hashes de A."
} else {
    Write-Host "Sin corpus: se omiten neural smoke, dense y la corrida end-to-end. Pide a Luis el snapshot (B0)." -ForegroundColor Yellow
}

# ---------------------------------------------------------------------
Step "[5] GPU: driver y PyTorch"
nvidia-smi; Check "nvidia-smi (¿esta PC tiene GPU NVIDIA?)"
nvidia-smi | Out-File "$Out\nvidia_smi.txt" -Encoding utf8
$DriverCuda = [double]((nvidia-smi | Select-String "CUDA Version:\s*([0-9.]+)").Matches[0].Groups[1].Value)
Write-Host "CUDA máximo que admite el driver: $DriverCuda"
& $Py -c "import importlib.util,sys; sys.exit(0 if importlib.util.find_spec('torch') else 1)"
$HasTorch = ($LASTEXITCODE -eq 0)
if (-not $HasTorch -or $InstallTorch) {
    if (-not $InstallTorch) { throw "STOP: falta PyTorch. Vuelve a correr con -InstallTorch." }
    $Index = if ($DriverCuda -ge 12.6) { "cu126" } elseif ($DriverCuda -ge 12.4) { "cu124" } elseif ($DriverCuda -ge 12.1) { "cu121" } else { "" }
    if (-not $Index) { throw "STOP: driver con CUDA $DriverCuda; se necesita >=12.1 (pídelo al laboratorio)." }
    Write-Host "Instalando PyTorch $Index dentro de .venv (sin admin)..."
    & $Py -m pip install torch --index-url "https://download.pytorch.org/whl/$Index"; Check "pip install torch"
}
& $Py -m pip install -r requirements-gpu.txt; Check "requirements-gpu"
& $Py tools\check_cuda.py | Out-File "$Out\check_cuda.json" -Encoding utf8
$Runtime = & $Py -c @'
import json, torch
ok = torch.cuda.is_available()
out = {"torch": torch.__version__, "torch_cuda": torch.version.cuda, "cuda_available": ok}
if ok:
    p = torch.cuda.get_device_properties(0)
    out.update(gpu=p.name, vram_gb=round(p.total_memory / 2**30, 1), bf16=torch.cuda.is_bf16_supported())
print(json.dumps(out))
'@
$Runtime | Out-File "$Out\runtime.json" -Encoding utf8
Write-Host $Runtime
$Rt = $Runtime | ConvertFrom-Json
if (-not $Rt.cuda_available) { throw "STOP: torch no ve CUDA. Revisa $Out\check_cuda.json; no reinstales al azar." }
if (-not $Rt.bf16) { throw "STOP: la GPU no soporta BF16." }
if ($Rt.vram_gb -lt 20) {
    Write-Host "AVISO: $($Rt.vram_gb) GB de VRAM. Un 8B en BF16 necesita ~17 GB + contexto: probablemente dé OOM." -ForegroundColor Yellow
    Write-Host "La política exige registrar ese OOM BF16 antes de usar int8/int4 (tools\gpu_smoke.py --oom-record)." -ForegroundColor Yellow
}
Write-Host "GPU_READY" -ForegroundColor Green

# ---------------------------------------------------------------------
if ($DownloadModels) {
    Step "[6] Pesos fijados por lock (a .\models, fuera de git)"
    $FreeGb = [math]::Round((Get-PSDrive (Get-Location).Drive.Name).Free / 1GB, 1)
    Write-Host "Espacio libre: $FreeGb GB (retrieval ~3 GB, Qwen3-8B ~16 GB, ALIA ~15 GB)"
    if ($FreeGb -lt 40) { throw "STOP: poco disco para los modelos. Mueve -Repo a una unidad con más espacio." }
    & $Py tools\prepare_neural.py --download; Check "retrieval Qwen 0.6B"
    & $Py tools\prepare_models.py --download qwen3-8b; Check "Qwen3-8B"
    & $Py tools\prepare_models.py --download alia-legal-7b; Check "ALIA 7B"
    if ($env:HF_TOKEN) { & $Py tools\prepare_models.py --download salamandra-7b } else { Write-Host "Salamandra requiere HF_TOKEN con acceso aprobado; se omite." }
    & $Py tools\prepare_models.py --verify | Out-File "$Out\models_verify.json" -Encoding utf8
}

if ($HaveCorpus) {
    Step "[7] Neural smoke de retrieval (embeddings + reranker reales)"
    & $Py tools\neural_smoke.py; Check "neural_smoke"
    Copy-Item reports\neural_smoke.json "$Out\" -ErrorAction SilentlyContinue
}

if ($DecoderSmoke) {
    Step "[8] Primera generación real del decoder (Qwen3-8B, BF16, temperatura 0)"
    & $Py tools\gpu_smoke.py --model qwen3-8b --precision bf16 --output-root "$Out\decoder_smoke"
    if ($LASTEXITCODE -ne 0) { Write-Host "El smoke falló; revisa $Out\decoder_smoke (si es CUDA_OOM, ese registro habilita int8/int4)." -ForegroundColor Yellow }
}

if ($FreezePlans) {
    Step "[9] Planner Qwen: congelar planes de sample_50 (replay para BASE vs PLAN)"
    & $Py tools\member_b.py plan --input data\sample_50.jsonl --model qwen3-8b; Check "freeze plans"
}

if ($RunSample -and $HaveCorpus) {
    Step "[10] Corrida end-to-end sample_50: locator de A + Qwen3-8B + reparación de citas"
    $Run = "runs\lab_${Stamp}_qwen3"
    & $Py tools\member_b.py batch --input data\sample_50.jsonl --run-dir $Run --model qwen3-8b --exact-locator --retrieval-mode option; Check "batch sample_50"
    & $Py scripts\evaluate.py --submission "$Run\submissions.jsonl" --split sample --out "$Out\evaluation_sample_qwen3.json"; Check "evaluate.py"
    Copy-Item "$Run\submissions.jsonl","$Run\batch_report.json" "$Out\"
    Write-Host "Puntaje sin RAGAS en $Out\evaluation_sample_qwen3.json" -ForegroundColor Green
}

if ($BuildDense -and $HaveCorpus) {
    Step "[11] (A) Índice denso Qwen sobre corpus v0.1"
    & $Py tools\member_a.py dense --corpus corpus; Check "dense"
}

# ---------------------------------------------------------------------
Step "[12] Benchmark independiente KC-COL-IR (C0 BM25 / C1 dense / C2 hybrid / C3 hybrid+reranker)"
if (-not $GateOpen) {
    Write-Host "Gate cerrado: A necesita >=10 retrieval gold aceptados (hoy los candidatos esperan revisión humana). No correr C0-C3."
} elseif (-not $HaveCorpus) {
    Write-Host "Gate abierto pero falta el corpus: no se corre."
} else {
    foreach ($C in "C0", "C1", "C2", "C3") {
        & $Py tools\independent_ir_v2.py run --component $C; Check "independent_ir_v2 $C"
    }
    Write-Host "Una sola corrida por componente, sin tuning. Resultados en reports/ según el runner de A."
}

Step "Listo. Resultados en $Out"
Write-Host "Las PCs de laboratorio suelen borrarse al cerrar sesión. Para conservarlos:"
Write-Host "  git checkout -b lab/$Stamp; git add $Out; git commit -m 'Lab GPU session $Stamp'; git push -u origin lab/$Stamp"
