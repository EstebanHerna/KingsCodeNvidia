# =====================================================================
# KingsCode - TODO EN UNO para la PC que tiene corpus\ y GPU (la 4090)
#
# Un solo script, sin admin, PowerShell 5.1. Pasos (cada uno se salta si ya esta hecho):
#   [0] Ubica el repo que tiene corpus\ (el de Luis); NO lo modifica.
#   [1] Copia limpia de main en %USERPROFILE%\KingsCodeRun (o -Work).
#   [2] Copia corpus\ (v0.1, 26.558 pasajes) y enlaza models\ del repo fuente.
#       En una PC nueva sin corpus\, lo descarga del release publico, lo verifica y lo extrae.
#   [3] Entorno Python + dependencias CPU; valida el corpus contra los hashes de A.
#   [4] Valida el indice denso con las mismas reglas que DenseIndex de A.
#   [5] Publica corpus + indice + LICENSE como release del repo publico (entregable 5).
#   [6] Entorno GPU: PyTorch CUDA dentro del venv, BF16, VRAM.
#   [7] Descarga y verifica el decoder fijado por lock (ALIA ~7,77B por defecto; Qwen3-8B,
#       8.190.735.360 parametros, solo con -IncludePendingEligibility y marcado como no competitivo).
#   Pasos [8]-[11] SOLO si existe artifacts\retrieval_freeze.json de A (GPU_DAY_RUNBOOK sec. 8);
#   si no, se detienen con BLOCKED_ON_A_FREEZE. Misma evidencia congelada para cada decoder.
#   [8] Valida el freeze y fija su SHA-256 (se re-verifica antes y despues de cada decoder).
#   [9] decoder-smoke sobre el freeze.
#  [10] sample_50 sobre el freeze + evaluador oficial (sin RAGAS). Sin retrieval en vivo ni planner.
#  [11] Proyeccion de tiempo para 992 preguntas.
#  [12] Guarda todo en reports\lab_session\<fecha> y lo sube a una rama lab/<fecha>.
#
# NO hace: tuning, benchmark v1/Search V2, holdout, RAGAS (gasta la llave), seleccion de decoder.
# corpus v0.2 (corpora\corpus-v0.2, 72 pasajes) ya esta en git; no se sube aparte.
#
# Uso:
#   cd $HOME
#   powershell -ExecutionPolicy Bypass -File kingscode_gpu_todo.ps1
#   ... -Source "C:\ruta\KingsCodeNvidia"   (repo que tiene corpus\; si no, lo busca)
#   ... -Models "alia-legal-7b,salamandra-7b" (comparacion sin seleccion; Salamandra requiere acceso HF)
#   ... -IncludePendingEligibility          (agrega qwen3-8b con elegibilidad pendiente)
#   ... -SkipPublish -SkipDecoder -RebuildDense -NoPush
# =====================================================================
param(
    [string]$Source = "",
    [string]$Work = "$HOME\KingsCodeRun",
    [string]$GitHubRepo = "IngSeb0/KingsCodeNvidia",
    [string]$Models = "alia-legal-7b",
    [switch]$IncludePendingEligibility,
    [string]$Tag = "corpus-v0.1-snapshot",
    [string]$License = "CC BY 4.0",
    [switch]$SkipPublish,
    [switch]$SkipDecoder,
    [switch]$RebuildDense,
    [switch]$NoPush
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
function Step($m) { Write-Host ""; Write-Host ">>> $m" -ForegroundColor Cyan }
function Warn($m) { Write-Host "AVISO: $m" -ForegroundColor Yellow }
function Check($w) { if ($LASTEXITCODE -ne 0) { throw "STOP: $w (exit $LASTEXITCODE)" } }
function Quiet($cmd) { cmd /c "$cmd >nul 2>&1"; return ($LASTEXITCODE -eq 0) }
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Summary = [ordered]@{ started = (Get-Date).ToString("s"); steps = [ordered]@{} }
function Done($k, $v) { $Summary.steps[$k] = $v }

# ---------------------------------------------------------------------
Step "[0] Repo fuente con corpus\ (solo lectura)"
$Candidates = @($Source, "$HOME\KingsCodeGPU\KingsCodeNvidia", "$HOME\KingsCodeNvidia", "$HOME\Downloads\KingsCodeNvidia",
                "$HOME\Desktop\KingsCodeNvidia", (Get-Location).Path)
$Source = $Candidates | Where-Object { $_ -and (Test-Path (Join-Path $_ "corpus\manifest.json")) -and ($_ -ne $Work) } | Select-Object -First 1
if ($Source) { Write-Host "Fuente local: $Source" }
else { Warn "no hay corpus local: se descargara del release publico $Tag (PC nueva)."; $Source = $null }
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "STOP: falta Git." }

$PyExe = $null
foreach ($c in @(@{Exe = "py"; Args = @("-3.12")}, @{Exe = "py"; Args = @("-3.11")}, @{Exe = "python"; Args = @()})) {
    try { $v = & $c.Exe @($c.Args) -c "import sys; print(sys.version_info >= (3, 11))"; if ($v -eq "True") { $PyExe = $c.Exe; $PyArgs = $c.Args; break } } catch { }
}
if (-not $PyExe) { throw "STOP: se necesita Python 3.11+ (python.org, 'Install for me only')." }

# ---------------------------------------------------------------------
Step "[1] Copia limpia de main en $Work"
if (-not (Test-Path "$Work\.git")) { git clone "https://github.com/$GitHubRepo.git" $Work; Check "git clone" }
Set-Location $Work
if (git status --porcelain --untracked-files=no) { git status --short; throw "STOP: $Work tiene cambios locales; revisalos o usa otro -Work." }
git checkout main; Check "checkout main"
git pull --ff-only origin main; Check "pull main"
$Sha = (git rev-parse HEAD).Trim()
Write-Host "main @ $Sha"
$Out = "$Work\reports\lab_session\$Stamp"
New-Item -ItemType Directory -Force $Out | Out-Null
Done "git" @{ work = $Work; source = $(if ($Source) { $Source } else { "release $Tag" }); main_sha = $Sha }

# ---------------------------------------------------------------------
Step "[2] Corpus v0.1 y cache de modelos"
if (-not (Test-Path "$Work\corpus\manifest.json")) {
    if ($Source) {
        robocopy "$Source\corpus" "$Work\corpus" /E /NFL /NDL /NJH /NJS /NP | Out-Null
        if ($LASTEXITCODE -ge 8) { throw "STOP: robocopy fallo copiando corpus\ ($LASTEXITCODE)" }
        $global:LASTEXITCODE = 0
    } else {
        if (-not (Test-Path "$Work\tools\package_corpus_snapshot.py")) { throw "STOP: main aun no tiene tools\package_corpus_snapshot.py (falta mergear el PR #6)." }
        $Dl = "$HOME\kingscode_descargas"
        New-Item -ItemType Directory -Force $Dl | Out-Null
        $Url = "https://github.com/$GitHubRepo/releases/download/$Tag"
        foreach ($f in @("kingscode-corpus-v0.1.tar.gz", "snapshot-files.sha256.json", "dense.npy", "dense.meta.json")) {
            if (-not (Test-Path "$Dl\$f")) {
                Write-Host "Descargando $f ..."
                try { Invoke-WebRequest -UseBasicParsing -Uri "$Url/$f" -OutFile "$Dl\$f" }
                catch { if ($f -like "dense*") { Warn "el release no trae $f (quedara solo BM25)" } else { throw "STOP: no pude descargar $f; existe el release $Tag? Publicalo primero desde la PC que tiene corpus\." } }
            }
        }
        & $PyExe @PyArgs tools\package_corpus_snapshot.py verify "$Dl\kingscode-corpus-v0.1.tar.gz" --files "$Dl\snapshot-files.sha256.json"; Check "verificacion del snapshot antes de extraer"
        tar -xzf "$Dl\kingscode-corpus-v0.1.tar.gz" -C $Work; Check "tar -xzf"
        if ((Test-Path "$Dl\dense.npy") -and (Test-Path "$Dl\dense.meta.json")) { Copy-Item "$Dl\dense.npy", "$Dl\dense.meta.json" "$Work\corpus\index\" }
        $SkipPublish = $true  # lo descargado ya esta publicado
    }
}
if (-not (Test-Path "$Work\models")) {
    if ($Source) {
        if (-not (Test-Path "$Source\models")) { New-Item -ItemType Directory -Force "$Source\models" | Out-Null }
        cmd /c "mklink /J `"$Work\models`" `"$Source\models`"" | Out-Null; Check "enlace de models\"
    } else { New-Item -ItemType Directory -Force "$Work\models" | Out-Null }
}

# ---------------------------------------------------------------------
Step "[3] Entorno Python y validacion del corpus contra los hashes de A"
if (-not (Test-Path ".venv\Scripts\python.exe")) { & $PyExe @PyArgs -m venv .venv; Check "crear .venv" }
$Py = "$Work\.venv\Scripts\python.exe"
& $Py -m pip install --upgrade pip; Check "pip"
& $Py -m pip install -r requirements-knowledge.txt; Check "requirements-knowledge"
& $Py tools\verify_member_a_v02.py | Out-File -Encoding utf8 "$Out\verify_member_a_v02.json"; Check "verify_member_a_v02"
git checkout -- reports/member_a_v02/verification.json  # the verifier rewrites this tracked file
Done "corpus" "v0.1 validado (verify_member_a_v02 PASS)"

# ---------------------------------------------------------------------
Step "[4] Indice denso: mismas reglas que DenseIndex de A"
$DenseCheck = @'
import hashlib, json, sys
from pathlib import Path
root = Path(sys.argv[1]); idx = root / "corpus/index"
def h(p): return hashlib.sha256(p.read_bytes()).hexdigest()
if not (idx / "dense.npy").exists() or not (idx / "dense.meta.json").exists():
    print(json.dumps({"status": "missing"})); sys.exit(0)
meta = json.loads((idx / "dense.meta.json").read_text(encoding="utf-8"))
sys.path.insert(0, str(root))
from kingscode.common import indexable, read_jsonl
ids = [p["passage_id"] for p in read_jsonl(root / "corpus/passages.jsonl") if indexable(p)]
cfg = json.loads((root / "config/neural.json").read_text(encoding="utf-8"))
lock = json.loads((root / "config/models.lock.json").read_text(encoding="utf-8"))
problems = []
if meta.get("vectors_sha256") != h(idx / "dense.npy"): problems.append("vectors_sha256")
if meta.get("corpus_sha256") != h(root / "corpus/passages.jsonl"): problems.append("corpus_sha256")
if meta.get("passage_ids") != ids: problems.append("passage_ids")
if meta.get("config") != cfg: problems.append("config (config/neural.json cambio desde que se construyo)")
if meta.get("model_lock") != lock.get(cfg["embedding_model"]): problems.append("model_lock")
print(json.dumps({"status": "valid" if not problems else "stale", "problems": problems,
                  "dense_sha256": h(idx / "dense.npy"),
                  "matches_4090_freeze": h(idx / "dense.npy") == "0c156c5e95dce92d6abd6404a39242bd724228bfdf99f4e9e44ddf5dd16b8347"}))
'@
$DenseCheck | Out-File -Encoding ascii "$env:TEMP\kc_dense_check.py"
$Dense = (& $Py "$env:TEMP\kc_dense_check.py" $Work) | ConvertFrom-Json
Write-Host ("Indice denso: {0} {1}" -f $Dense.status, ($Dense.problems -join ", "))
Done "dense_before" $Dense

# ---------------------------------------------------------------------
Step "[6] Entorno GPU (antes de publicar, por si hay que reconstruir el denso)"
$GpuOk = $false
if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    nvidia-smi | Out-File -Encoding utf8 "$Out\nvidia_smi.txt"
    $DriverCuda = [double]((nvidia-smi | Select-String "CUDA Version:\s*([0-9.]+)").Matches[0].Groups[1].Value)
    try { & $Py -c "import torch,sys; sys.exit(0 if torch.cuda.is_available() else 1)"; $HasTorch = ($LASTEXITCODE -eq 0) } catch { $HasTorch = $false }
    if (-not $HasTorch) {
        $Index = if ($DriverCuda -ge 12.6) { "cu126" } elseif ($DriverCuda -ge 12.4) { "cu124" } elseif ($DriverCuda -ge 12.1) { "cu121" } else { "" }
        if (-not $Index) { throw "STOP: el driver solo admite CUDA $DriverCuda; se necesita >= 12.1." }
        & $Py -m pip install torch --index-url "https://download.pytorch.org/whl/$Index"; Check "PyTorch $Index"
    }
    & $Py -m pip install -r requirements-gpu.txt; Check "requirements-gpu"
    $Rt = (& $Py -c "import json,torch; p=torch.cuda.get_device_properties(0); print(json.dumps({'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':p.name,'vram_gb':round(p.total_memory/2**30,1),'bf16':torch.cuda.is_bf16_supported()}))") | ConvertFrom-Json
    $Rt | ConvertTo-Json | Out-File -Encoding utf8 "$Out\runtime.json"
    Write-Host ("GPU {0}, {1} GB, BF16={2}, torch {3} / CUDA {4}" -f $Rt.gpu, $Rt.vram_gb, $Rt.bf16, $Rt.torch, $Rt.cuda)
    $GpuOk = [bool]$Rt.bf16
    if ($Rt.vram_gb -lt 20) { Warn "menos de 20 GB de VRAM: un 8B en BF16 puede dar OOM (queda registrado)." }
    Done "gpu" $Rt
} else { Warn "sin nvidia-smi: se omiten los pasos de GPU."; Done "gpu" "no_gpu" }

if ($GpuOk -and ($Dense.status -ne "valid") -and $RebuildDense) {
    Step "[6b] Reconstruyendo indice denso Qwen sobre corpus v0.1"
    & $Py tools\prepare_models.py --download "Qwen/Qwen3-Embedding-0.6B"; Check "modelo de embeddings"
    & $Py tools\member_a.py dense --corpus corpus; Check "dense"
    $Dense = (& $Py "$env:TEMP\kc_dense_check.py" $Work) | ConvertFrom-Json
    Done "dense_rebuilt" $Dense
}

# ---------------------------------------------------------------------
if (-not $SkipPublish -and -not (Test-Path "$Work\tools\package_corpus_snapshot.py")) {
    Warn "main aun no tiene tools\package_corpus_snapshot.py (falta mergear el PR #6): se salta la publicacion."
    $SkipPublish = $true
}
if (-not $SkipPublish) {
    Step "[5] Publicar corpus v0.1 + indice + LICENSE (entregable 5)"
    $Gh = Get-Command gh -ErrorAction SilentlyContinue
    $Exists = $Gh -and (Quiet "gh release view $Tag --repo $GitHubRepo")
    if ($Exists) {
        Write-Host "El release $Tag ya existe; no se reemplaza."
        Done "publish" "ya_existia"
    } else {
        $Bundle = "$HOME\kingscode_upload\$Stamp\kingscode_corpus_e_indice_v0.1"
        New-Item -ItemType Directory -Force "$Bundle\indice_denso" | Out-Null
        & $Py tools\package_corpus_snapshot.py pack --root $Work --out "$Bundle\corpus_snapshot"; Check "empaquetado"
        & $Py tools\package_corpus_snapshot.py verify "$Bundle\corpus_snapshot\kingscode-corpus-v0.1.tar.gz" --files "$Bundle\corpus_snapshot\snapshot-files.sha256.json"; Check "verificacion del paquete"
        $WithDense = $Dense.status -eq "valid"
        if ($WithDense) { Copy-Item "$Work\corpus\index\dense.npy", "$Work\corpus\index\dense.meta.json" "$Bundle\indice_denso\" }
        else { Warn "el indice denso no es valido para la config actual ($($Dense.problems -join ', ')); se publica solo BM25. Usa -RebuildDense para reconstruirlo." }
        @"
KingsCode - corpus procesado e indices (corpus-v0.1)

Licencia de la compilacion, el procesamiento y los indices: $License
https://creativecommons.org/licenses/by/4.0/legalcode

Los textos juridicos provienen de fuentes oficiales colombianas; URL, fecha de
consulta y hash de cada documento estan en corpus/manifest.json.
Equipo KingsCode - Hackathon 2026, Universidad de los Andes.
"@ | Out-File -Encoding ascii "$Bundle\LICENSE.txt"
        Copy-Item "$Bundle\corpus_snapshot\LEEME.txt" "$Bundle\LEEME.txt"
        $Zip = "$HOME\kingscode_upload\$Stamp\kingscode_corpus_e_indice_v0.1.zip"
        Compress-Archive -Path "$Bundle\*" -DestinationPath $Zip
        $Assets = @($Zip, "$Bundle\corpus_snapshot\kingscode-corpus-v0.1.tar.gz", "$Bundle\corpus_snapshot\snapshot-files.sha256.json",
                    "$Bundle\LEEME.txt", "$Bundle\LICENSE.txt")
        if ($WithDense) { $Assets += @("$Bundle\indice_denso\dense.npy", "$Bundle\indice_denso\dense.meta.json") }
        $Sums = "$HOME\kingscode_upload\$Stamp\SHA256SUMS.txt"
        $Assets | ForEach-Object { "{0}  {1}" -f (Get-FileHash -Algorithm SHA256 $_).Hash.ToLower(), (Split-Path $_ -Leaf) } | Out-File -Encoding ascii $Sums
        $Assets += $Sums
        if ($Gh) {
            if (-not (Quiet "gh auth status")) { gh auth login; Check "gh auth login" }
            $Notes = "Snapshot historico corpus-v0.1 (163 documentos, 26.558 pasajes, grafo, BM25" + $(if ($WithDense) { " e indice denso Qwen" } else { "" }) + "). No es freeze competitivo. corpus-v0.2 esta en el repo (corpora/corpus-v0.2). Verificar con tools/package_corpus_snapshot.py verify."
            gh release create $Tag @Assets --repo $GitHubRepo --title "Corpus e indice KingsCode v0.1" --notes $Notes; Check "gh release create"
            Write-Host "Enlace para README (## Corpus e indice): https://github.com/$GitHubRepo/releases/download/$Tag/kingscode_corpus_e_indice_v0.1.zip" -ForegroundColor Green
            Done "publish" @{ release = "https://github.com/$GitHubRepo/releases/tag/$Tag"; dense = $WithDense }
        } else {
            Warn "no hay GitHub CLI: sube $Zip a Drive ('Cualquier persona con el enlace') y pega el enlace en el README."
            Done "publish" @{ manual_upload = $Zip; dense = $WithDense }
        }
    }
}

# ---------------------------------------------------------------------
$ModelList = @($Models.Split(",") | ForEach-Object { $_.Trim() } | Where-Object { $_ })
if ($IncludePendingEligibility -and $ModelList -notcontains "qwen3-8b") { $ModelList += "qwen3-8b" }
$Eligibility = [ordered]@{}
foreach ($m in $ModelList) { $Eligibility[$m] = $(if ($m -in @("qwen3-8b", "llama31-8b")) { "pending_organizer_confirmation_not_competitive" } else { "within_8B" }) }
Done "decoder_eligibility" $Eligibility
if ($GpuOk -and -not $SkipDecoder) {
    Step "[7] Pesos del decoder fijados por lock ($($ModelList -join ', '))"
    $FreeGb = [math]::Round((Get-PSDrive (Split-Path $Work -Qualifier).TrimEnd(":")).Free / 1GB, 1)
    Write-Host "Espacio libre: $FreeGb GB (cada decoder ~16 GB; solo archivos de pesos/tokenizer del lock)"
    foreach ($m in $ModelList) {
        & $Py tools\prepare_models.py --download $m; Check "descarga $m"
        & $Py tools\prepare_models.py --verify $m; Check "verificacion $m"
        if ($Eligibility[$m] -ne "within_8B") { Warn "$m tiene elegibilidad PENDIENTE (supera 8.000.000.000 parametros literales); no es candidato competitivo hasta la confirmacion." }
    }

    # GPU_DAY_RUNBOOK sec. 8: decoder-smoke/sample/bakeoff solo sobre el freeze de ocho evidencias de A,
    # la misma evidencia para cada decoder. Sin retrieval en vivo, sin planner.
    $Freeze = "$Work\artifacts\retrieval_freeze.json"
    if (-not (Test-Path $Freeze)) {
        Warn "BLOCKED_ON_A_FREEZE: no existe artifacts\retrieval_freeze.json. Pesos listos; el decoder se corre cuando A publique su seleccion y el freeze."
        Done "decoder" "BLOCKED_ON_A_FREEZE"
    } else {
        Step "[8] Freeze de A: validacion"
        & $Py -c "import sys; sys.path.insert(0, '.'); from pathlib import Path; from kingscode.generation.retrieval_experiments import load_freeze; load_freeze(Path(r'$Freeze'))"; Check "freeze de A"
        $FreezeSha = (Get-FileHash $Freeze -Algorithm SHA256).Hash.ToLower()
        $Results = @()
        foreach ($m in $ModelList) {
            if ((Get-FileHash $Freeze -Algorithm SHA256).Hash.ToLower() -ne $FreezeSha) { throw "STOP: el freeze cambio antes de $m" }
            Step "[9] decoder-smoke con $m (BF16, temperatura 0, evidencia congelada)"
            & $Py tools\member_b.py decoder-smoke --model $m --retrieval-freeze $Freeze --allow-optional --output-root "$Out\decoders" | Out-File -Encoding utf8 "$Out\decoder_smoke_$m.json"
            if ($LASTEXITCODE -ne 0) { Warn "decoder-smoke de $m fallo; ver $Out\decoder_smoke_$m.json (CUDA_OOM habilita int8/int4)."; $Results += [ordered]@{ model = $m; status = "smoke_failed" }; continue }
            Step "[10] sample_50 con $m sobre el mismo freeze + evaluador oficial (sin RAGAS)"
            & $Py tools\member_b.py sample --model $m --retrieval-freeze $Freeze --allow-optional --output-root "$Out\decoders" | Out-File -Encoding utf8 "$Out\sample_$m.json"
            # member_b.py imprime al final un JSON con indentacion; se toma desde la ultima llave en columna 0.
            $Raw = Get-Content "$Out\sample_$m.json" -Raw
            $At = $(if ($Raw.StartsWith("{")) { 0 } else { $Raw.LastIndexOf("`n{") + 1 })
            try { $Rec = $Raw.Substring($At) | ConvertFrom-Json } catch { $Rec = [pscustomobject]@{ status = "failed_unparsed_output" } }
            if ((Get-FileHash $Freeze -Algorithm SHA256).Hash.ToLower() -ne $FreezeSha) { throw "STOP: el freeze cambio durante $m" }
            $Auto = $Rec.official_evaluation.total_automatico
            $Spq = $(if ($Rec.metrics.completed_questions_per_second) { [math]::Round(1 / $Rec.metrics.completed_questions_per_second, 2) } else { $null })
            if ($Spq) {
                Step "[11] Presupuesto de tiempo para 992 con $m"
                & $Py tools\benchmark_budget.py --seconds-per-question $Spq --questions 992 --hours 6 | Out-File -Encoding utf8 "$Out\budget_$m.txt"
                Get-Content "$Out\budget_$m.txt"
            }
            $Results += [ordered]@{ model = $m; status = $Rec.status; eligibility = $Eligibility[$m]; automatico_sin_ragas = $Auto.obtenidos;
                                    posibles = $Auto.posibles; seconds_per_question = $Spq; abstenciones = $Rec.metrics.abstentions;
                                    citas_sin_respaldo = $Rec.metrics.unsupported_citation_count }
        }
        $Results | ConvertTo-Json | Out-File -Encoding utf8 "$Out\sample_results.json"
        $Results | ForEach-Object { Write-Host ("{0} [{1}]: {2} / {3} automatico sin RAGAS; {4} s/pregunta" -f $_.model, $_.eligibility, $_.automatico_sin_ragas, $_.posibles, $_.seconds_per_question) -ForegroundColor Green }
        Done "decoder" ([ordered]@{ freeze_sha256 = $FreezeSha; results = $Results; selection = "none: comparison only" })
    }
} elseif (-not $GpuOk) { Warn "sin GPU BF16: no se corre el decoder." }

# ---------------------------------------------------------------------
Step "[12] Guardar resultados"
$Summary.finished = (Get-Date).ToString("s")
$Summary | ConvertTo-Json -Depth 6 | Out-File -Encoding utf8 "$Out\summary.json"
if (-not $NoPush) {
    $Branch = "lab/$Stamp"
    git checkout -b $Branch; Check "rama $Branch"
    git add "reports/lab_session/$Stamp"; Check "git add"
    git -c user.name="KingsCode lab" -c user.email="lab@kingscode.local" commit -m "Lab GPU session $Stamp (main $Sha)"; Check "git commit"
    git push -u origin $Branch
    if ($LASTEXITCODE -ne 0) { Warn "no se pudo subir $Branch; los resultados quedan en $Out" } else { Write-Host "Resultados subidos a la rama $Branch" -ForegroundColor Green }
    git checkout main | Out-Null
}
Write-Host ""
Write-Host "LISTO. Resultados en $Out" -ForegroundColor Green
