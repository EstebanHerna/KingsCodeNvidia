# =====================================================================
# KingsCode - PC NUEVA con GPU: de Windows limpio al diagnostico Qwen3-8B + BM25
#
# Un solo script, sin admin, Windows PowerShell 5.1. Cada paso se salta si ya esta hecho.
#   [0] Git y Python 3.12 (los instala con winget en el usuario si faltan); GPU NVIDIA.
#   [1] Clona o actualiza main en -Work.
#   [2] .venv + dependencias + PyTorch CUDA segun el driver.
#   [3] Corpus v0.1, en este orden: archivo local (-CorpusArchive), release publico o,
#       si no hay ninguno, descarga de las fuentes oficiales con el acquire + build de A
#       (config/sources.json). Compara documento por documento contra los hashes de v0.1
#       (corpus_manifest.json) y lo registra; un corpus descargado que no sea identico
#       sirve para diagnostico, no como freeze.
#  [3b] Corpus combinado v0.1 + v0.2 (corpora\corpus-v0.2, 4 documentos provisionales)
#       en corpus_v01_v02\ con tools\build_combined_corpus.py. -CorpusSet v01 lo omite.
#   [4] Pesos fijados por lock: Qwen3-8B (decoder) + embedding/reranker 0.6B (smoke).
#   [5] Smoke real en GPU (BF16, temperatura 0).
#   [6] Diagnostico: sample_50 con Qwen3-8B + BM25 (k=8, grafo off) + guardas,
#       y evaluador oficial automatico (sin RAGAS).
#   [7] RAGAS SOLO con -Ragas (gasta creditos de OpenRouter; la llave se pide oculta
#       y nunca se escribe a disco).
#
# Esto es un DIAGNOSTICO OPERATIVO (tiempos, JSON valido, advertencias, abstenciones),
# no la seleccion de decoder ni de retrieval: eso espera el freeze de A.
#
# Uso (desde cualquier carpeta):
#   powershell -ExecutionPolicy Bypass -File kingscode_pc_nueva_diagnostico.ps1
#   ... -CorpusArchive "D:\kingscode-corpus-v0.1.tar.gz"   (con snapshot-files.sha256.json al lado)
#   ... -Ragas                                             (solo con autorizacion de Esteban)
#   ... -Work "D:\KingsCode"  -RunName "qwen3_8b_bm25_prueba2"
# =====================================================================
param(
    [string]$Work = "$HOME\KingsCodeGPU\KingsCodeNvidia",
    [string]$GitHubRepo = "IngSeb0/KingsCodeNvidia",
    [string]$Tag = "corpus-v0.1-snapshot",
    [string]$CorpusArchive = "",
    [string]$Model = "qwen3-8b",
    [string]$RunName = "",
    [ValidateSet("v01+v02", "v01")] [string]$CorpusSet = "v01+v02",
    [switch]$Ragas,
    [switch]$SkipSmoke
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
function Step($m) { Write-Host ""; Write-Host ">>> $m" -ForegroundColor Cyan }
function Warn($m) { Write-Host "AVISO: $m" -ForegroundColor Yellow }
function Check($w) { if ($LASTEXITCODE -ne 0) { throw "STOP: $w (exit $LASTEXITCODE)" } }
function RefreshPath { $env:Path = [Environment]::GetEnvironmentVariable("Path", "User") + ";" + [Environment]::GetEnvironmentVariable("Path", "Machine") }
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
if (-not $RunName) { $RunName = "${Model}_bm25_$Stamp" }

# ---------------------------------------------------------------------
Step "[0] Herramientas: Git, Python 3.12, GPU"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw "STOP: falta Git y no hay winget. Instala Git desde https://git-scm.com/download/win y vuelve a correr." }
    winget install --id Git.Git -e --scope user --accept-source-agreements --accept-package-agreements
    RefreshPath
    if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "STOP: Git no quedo en el PATH. Cierra y abre PowerShell y vuelve a correr." }
}
function Find-Python {
    foreach ($c in @(@{Exe = "py"; Args = @("-3.12")}, @{Exe = "py"; Args = @("-3.11")}, @{Exe = "python"; Args = @()})) {
        try {
            $v = & $c.Exe @($c.Args) -c "import sys; print(sys.version_info >= (3, 11))" 2>$null
            if ($v -eq "True") { return $c }
        } catch { }
    }
    return $null
}
$PyCmd = Find-Python
if (-not $PyCmd) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) { throw "STOP: falta Python 3.12. Instalalo desde python.org ('Install for me only', marcar 'Add to PATH')." }
    winget install --id Python.Python.3.12 -e --scope user --accept-source-agreements --accept-package-agreements
    RefreshPath
    $PyCmd = Find-Python
    if (-not $PyCmd) { throw "STOP: Python no quedo en el PATH. Cierra y abre PowerShell y vuelve a correr." }
}
Write-Host ("Python base: {0} {1}" -f $PyCmd.Exe, ($PyCmd.Args -join " "))
if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) { throw "STOP: no hay nvidia-smi. Instala el driver NVIDIA (>= 12.1 CUDA) y vuelve a correr." }
$DriverCuda = [double]((nvidia-smi | Select-String "CUDA Version:\s*([0-9.]+)").Matches[0].Groups[1].Value)
Write-Host "Driver NVIDIA con CUDA $DriverCuda"

# ---------------------------------------------------------------------
Step "[1] Repo: main en $Work"
if (-not (Test-Path "$Work\.git")) {
    New-Item -ItemType Directory -Force (Split-Path $Work) | Out-Null
    git clone "https://github.com/$GitHubRepo.git" $Work; Check "git clone"
}
Set-Location $Work
if (git status --porcelain --untracked-files=no) { git status --short; throw "STOP: $Work tiene cambios locales en archivos versionados; revisalos (no se descartan solos)." }
git checkout main; Check "checkout main"
git pull --ff-only origin main; Check "pull main"
$Sha = (git rev-parse HEAD).Trim()
Write-Host "main @ $Sha"

# ---------------------------------------------------------------------
Step "[2] Entorno Python (.venv) y PyTorch CUDA"
if (-not (Test-Path ".venv\Scripts\python.exe")) { & $PyCmd.Exe @($PyCmd.Args) -m venv .venv; Check "crear .venv" }
$Py = "$Work\.venv\Scripts\python.exe"
& $Py -m pip install --upgrade pip --quiet; Check "pip"
& $Py -m pip install -r requirements-knowledge.txt --quiet; Check "requirements-knowledge"
$HasCuda = $false
try { & $Py -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)" 2>$null; $HasCuda = ($LASTEXITCODE -eq 0) } catch { }
if (-not $HasCuda) {
    $Index = if ($DriverCuda -ge 12.6) { "cu126" } elseif ($DriverCuda -ge 12.4) { "cu124" } elseif ($DriverCuda -ge 12.1) { "cu121" } else { "" }
    if (-not $Index) { throw "STOP: el driver solo admite CUDA $DriverCuda; actualiza el driver NVIDIA (>= 12.1)." }
    & $Py -m pip install torch --index-url "https://download.pytorch.org/whl/$Index"; Check "PyTorch $Index"
}
& $Py -m pip install -r requirements-gpu.txt --quiet; Check "requirements-gpu"
$Rt = (& $Py -c "import json,torch; p=torch.cuda.get_device_properties(0); print(json.dumps({'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':p.name,'vram_gb':round(p.total_memory/2**30,1),'bf16':torch.cuda.is_bf16_supported()}))") | ConvertFrom-Json
Write-Host ("GPU {0}, {1} GB, BF16={2}, torch {3} / CUDA {4}" -f $Rt.gpu, $Rt.vram_gb, $Rt.bf16, $Rt.torch, $Rt.cuda)
if (-not $Rt.bf16) { throw "STOP: la GPU no soporta BF16; el decoder esta fijado en BF16 (int8/int4 solo con registro de OOM)." }
if ($Rt.vram_gb -lt 20) { Warn "menos de 20 GB de VRAM: Qwen3-8B en BF16 usa ~19 GB y puede dar OOM (queda registrado)." }

# ---------------------------------------------------------------------
Step "[3] Corpus v0.1: archivo local > release > descarga oficial (acquire de A)"
$CorpusOrigin = "existente"
if (-not (Test-Path "corpus\manifest.json")) {
    $Archive = $null
    if ($CorpusArchive) {
        if (-not (Test-Path $CorpusArchive)) { throw "STOP: no existe $CorpusArchive (quita -CorpusArchive para descargar de las fuentes oficiales)." }
        $Archive = (Resolve-Path $CorpusArchive).Path
        $Files = Join-Path (Split-Path $Archive) "snapshot-files.sha256.json"
        if (-not (Test-Path $Files)) { throw "STOP: falta snapshot-files.sha256.json junto a $Archive (lo genera package_corpus_snapshot.py pack)." }
        $CorpusOrigin = "archivo $Archive"
    } else {
        $Dl = "$HOME\kingscode_descargas"
        New-Item -ItemType Directory -Force $Dl | Out-Null
        $Url = "https://github.com/$GitHubRepo/releases/download/$Tag"
        try {
            foreach ($f in @("kingscode-corpus-v0.1.tar.gz", "snapshot-files.sha256.json")) {
                if (-not (Test-Path "$Dl\$f")) { Write-Host "Descargando $f del release ..."; Invoke-WebRequest -UseBasicParsing -Uri "$Url/$f" -OutFile "$Dl\$f" }
            }
            $Archive, $Files = "$Dl\kingscode-corpus-v0.1.tar.gz", "$Dl\snapshot-files.sha256.json"
            $CorpusOrigin = "release $Tag"
        } catch {
            Remove-Item "$Dl\kingscode-corpus-v0.1.tar.gz", "$Dl\snapshot-files.sha256.json" -ErrorAction SilentlyContinue
            Warn "no hay release $Tag; se descarga de las fuentes oficiales con el acquire de A."
        }
    }
    if ($Archive) {
        & $Py tools\package_corpus_snapshot.py verify $Archive --files $Files; Check "verificacion del snapshot antes de extraer"
        tar -xzf $Archive -C $Work; Check "tar -xzf"
    } else {
        # Descarga oficial (config/sources.json, 163 objetivos) y reconstruccion determinista.
        & $Py tools\member_a.py acquire --corpus corpus --workers 3 | Out-File -Encoding utf8 "$HOME\kingscode_acquire_$Stamp.json"
        Check "acquire (descarga de fuentes oficiales)"
        & $Py tools\member_a.py build --corpus corpus | Out-Null; Check "build (pasajes, grafo, BM25)"
        git checkout -- corpus_manifest.json 2>$null   # build reescribe el manifest versionado de v0.1; se conserva la referencia
        $global:LASTEXITCODE = 0
        $CorpusOrigin = "descarga oficial (acquire + build)"
    }
}
$Cmp = (& $Py -c @"
import hashlib, json
from pathlib import Path
ref = {d['doc_id']: d['source_sha256'] for d in json.loads(Path('corpus_manifest.json').read_text(encoding='utf-8'))['documentos']}
got = {d['doc_id']: d['source_sha256'] for d in json.loads(Path('corpus/manifest.json').read_text(encoding='utf-8'))['documentos']}
same = sorted(k for k in ref if got.get(k) == ref[k])
print(json.dumps({'v01_docs': len(ref), 'identical_raw': len(same), 'changed': sorted(k for k in ref if k in got and got[k] != ref[k]), 'missing': sorted(set(ref) - set(got))}))
"@) | ConvertFrom-Json
Write-Host ("Corpus ({0}): {1}/{2} documentos con bytes identicos a v0.1; cambiados {3}; faltantes {4}" -f $CorpusOrigin, $Cmp.identical_raw, $Cmp.v01_docs, @($Cmp.changed).Count, @($Cmp.missing).Count)
& $Py tools\verify_member_a_v02.py | Out-Null
$CorpusExact = ($LASTEXITCODE -eq 0)
git checkout -- reports/member_a_v02/verification.json 2>$null  # el verificador reescribe este archivo versionado
$global:LASTEXITCODE = 0
if ($CorpusExact) { Write-Host "Corpus v0.1 verificado byte a byte contra los hashes de A." -ForegroundColor Green }
elseif ($CorpusOrigin -like "descarga oficial*") { Warn "el corpus descargado NO es identico a v0.1 (las fuentes cambiaron); sirve para diagnostico, no como freeze. Queda registrado." }
else { throw "STOP: el corpus no coincide con los hashes de A (verify_member_a_v02)." }

Step "[3b] Corpus combinado v0.1 + v0.2 (corpora\corpus-v0.2, provisional)"
if ($CorpusSet -eq "v01+v02") {
    if (-not (Test-Path "corpus_v01_v02\manifest.json")) { & $Py tools\build_combined_corpus.py | Out-Null; Check "build_combined_corpus" }
    $CorpusDir = "corpus_v01_v02"
} else { $CorpusDir = "corpus" }
Write-Host "Corpus para el diagnostico: $CorpusDir"

# ---------------------------------------------------------------------
Step "[4] Pesos fijados por lock (solo archivos del lock, verificados contra el Hub)"
$FreeGb = [math]::Round((Get-PSDrive (Split-Path $Work -Qualifier).TrimEnd(":")).Free / 1GB, 1)
Write-Host "Espacio libre: $FreeGb GB (Qwen3-8B ~16 GB + retrieval ~2,5 GB)"
if ($FreeGb -lt 25) { Warn "menos de 25 GB libres; la descarga puede fallar." }
& $Py tools\prepare_models.py --download $Model; Check "descarga $Model"
& $Py tools\prepare_models.py --verify $Model; Check "verificacion $Model"
if (-not $SkipSmoke) { & $Py tools\prepare_models.py --download-retrieval; Check "modelos de retrieval para el smoke" }
$env:HF_HUB_OFFLINE = "1"   # desde aqui todo es local: ninguna llamada a la red de Hugging Face

# ---------------------------------------------------------------------
$Out = "reports\decoder_diagnostic\$RunName"
if (Test-Path $Out) { throw "STOP: ya existe $Out; usa otro -RunName para conservar la corrida anterior." }
New-Item -ItemType Directory -Force $Out | Out-Null
if (-not $SkipSmoke) {
    Step "[5] Smoke real en GPU ($Model, BF16, temperatura 0)"
    & $Py tools\gpu_smoke.py --model $Model --output-root "$Out\smoke"
    if ($LASTEXITCODE -ne 0) { throw "STOP: el smoke fallo; revisa $Out\smoke (si es CUDA_OOM, ese registro habilita int8/int4)." }
}

# ---------------------------------------------------------------------
Step "[6] Diagnostico sample_50: $Model + BM25 k=8, grafo off, guardas (sin seleccion)"
$Run = "$Out\batch"
& $Py tools\member_b.py batch `
    --input data\sample_50.jsonl `
    --run-dir $Run `
    --fresh `
    --retries 0 `
    --retrieval-mode base `
    --retriever-mode bm25 `
    --graph-policy off `
    --k 8 `
    --corpus $CorpusDir `
    --model $Model `
    --precision bf16
Check "corrida integrada (conserva $Run)"
& $Py scripts\evaluate.py --submission "$Run\submissions.jsonl" --split sample --out "$Out\evaluation_official.json"
Check "evaluador oficial"

# ---------------------------------------------------------------------
if ($Ragas) {
    Step "[7] RAGAS (gasta creditos de OpenRouter)"
    & $Py -m pip install -r scripts\requirements-evaluador.txt --quiet; Check "dependencias del juez RAGAS"
    $JudgeKey = Read-Host "Pega la llave autorizada de OpenRouter" -AsSecureString
    $KeyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($JudgeKey)
    try {
        $env:OPENROUTER_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($KeyPointer)
        Remove-Item Env:\HF_HUB_OFFLINE -ErrorAction SilentlyContinue   # el juez descarga su modelo de similitud
        & $Py scripts\evaluate.py --submission "$Run\submissions.jsonl" --split sample --ragas --out "$Out\evaluation_ragas.json"
        Check "juez RAGAS"
    } finally {
        Remove-Item Env:\OPENROUTER_API_KEY -ErrorAction SilentlyContinue
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($KeyPointer)
    }
} else {
    Write-Host ""; Write-Host "[7] RAGAS omitido (usa -Ragas solo con autorizacion; gasta creditos)." -ForegroundColor Yellow
}

# ---------------------------------------------------------------------
Step "Resumen"
$Br = Get-Content "$Run\batch_report.json" -Raw | ConvertFrom-Json
$Ev = Get-Content "$Out\evaluation_official.json" -Raw | ConvertFrom-Json
$Spq = [math]::Round($Br.seconds / 50, 1)
$Summary = [ordered]@{
    main_sha = $Sha; model = $Model; gpu = $Rt.gpu; vram_gb = $Rt.vram_gb; torch = $Rt.torch
    retrieval = "bm25 k=8 graph off (diagnostico, no freeze)"
    corpus = $CorpusDir; corpus_origin = $CorpusOrigin; corpus_v01_byte_identical = $CorpusExact; corpus_v01_comparison = $Cmp
    automatico_sin_ragas = "$($Ev.total_automatico.obtenidos) / $($Ev.total_automatico.posibles)"
    cerradas = $Ev.cerradas.puntos; citas = $Ev.citas.puntos; abstencion = $Ev.abstencion.puntos
    errores_validacion = $Ev.validacion.errores
    fallbacks_pipeline_error = @($Br.fallback_ids).Count
    segundos_por_pregunta = $Spq; proyeccion_992_horas = [math]::Round($Spq * 992 / 3600, 2)
    diagnostics = $Br.diagnostics
    ragas = $(if ($Ragas) { "$Out\evaluation_ragas.json" } else { "no ejecutado" })
}
$Summary | ConvertTo-Json -Depth 8 | Out-File -Encoding utf8 "$Out\RESUMEN.json"
Write-Host ("{0}: {1} automatico sin RAGAS | cerradas {2}, citas {3}, abstencion {4} | {5} s/pregunta -> 992 en {6} h | fallbacks {7}" -f `
    $Model, $Summary.automatico_sin_ragas, $Summary.cerradas, $Summary.citas, $Summary.abstencion, $Spq, $Summary.proyeccion_992_horas, $Summary.fallbacks_pipeline_error) -ForegroundColor Green
if ($Summary.proyeccion_992_horas -gt 5) { Warn "la proyeccion para 992 supera 5 h: la ventana del sabado es de 6 h." }
Write-Host "Envia a Esteban: $Work\$Out\RESUMEN.json, $Out\evaluation_official.json y $Run\batch_report.json"
