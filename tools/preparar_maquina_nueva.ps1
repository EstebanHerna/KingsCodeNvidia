# =====================================================================
# SCRIPT 2 - En una PC NUEVA (sin repo, sin corpus). Sin admin.
# Clona el repo, instala dependencias CPU, descarga el corpus v0.1 y el
# indice denso del release publico, verifica cada archivo, los coloca en
# corpus\ y valida contra los hashes de A. Deja listo tools\lab_gpu_session.ps1.
#
# Requisitos: Git y Python 3.11+ instalados (sin admin: instaladores "solo para mi").
# Uso (PowerShell):
#   powershell -ExecutionPolicy Bypass -File preparar_maquina_nueva.ps1
#   ... -Base "D:\trabajo"   (carpeta donde se clona; por defecto tu carpeta de usuario)
# =====================================================================
param(
    [string]$Base = "$HOME",
    [string]$GitHubRepo = "IngSeb0/KingsCodeNvidia",
    [string]$Tag = "corpus-v0.1-snapshot",
    [switch]$SkipSmoke
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
function Step($m) { Write-Host ""; Write-Host ">>> $m" -ForegroundColor Cyan }
function Check($w) { if ($LASTEXITCODE -ne 0) { throw "STOP: $w (exit $LASTEXITCODE)" } }
$DenseSha = "0c156c5e95dce92d6abd6404a39242bd724228bfdf99f4e9e44ddf5dd16b8347"
$DenseMetaSha = "c63c929cb85311c345b9e7cefa3245748a9f16bd3a12ce396563bc07cddb23cb"

# ---------------------------------------------------------------------
Step "[0] Requisitos"
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "STOP: instala Git (https://git-scm.com, opcion 'solo para mi')." }
$PyExe = $null
foreach ($c in @(@{Exe = "py"; Args = @("-3.12")}, @{Exe = "py"; Args = @("-3.11")}, @{Exe = "python"; Args = @()})) {
    try {
        $v = & $c.Exe @($c.Args) -c "import sys; print(sys.version_info >= (3, 11))"
        if ($v -eq "True") { $PyExe = $c.Exe; $PyArgs = $c.Args; break }
    } catch { }
}
if (-not $PyExe) { throw "STOP: instala Python 3.12 (python.org, 'Install for me only', marcar 'Add to PATH')." }
Write-Host "Git OK; Python: $PyExe $PyArgs"

# ---------------------------------------------------------------------
Step "[1] Clonar o actualizar el repo en $Base\KingsCodeNvidia"
New-Item -ItemType Directory -Force $Base | Out-Null
Set-Location $Base
if (-not (Test-Path "KingsCodeNvidia\.git")) {
    git clone "https://github.com/$GitHubRepo.git" KingsCodeNvidia; Check "git clone"
}
Set-Location "$Base\KingsCodeNvidia"
if (git status --porcelain) { git status --short; throw "STOP: el repo tiene cambios locales; guardalos o usa otra -Base." }
git checkout main; Check "git checkout main"
git pull --ff-only origin main; Check "git pull"
$Repo = (Get-Location).Path
Write-Host "Repo: $Repo @ $((git rev-parse HEAD).Trim())"
if (-not (Test-Path "tools\package_corpus_snapshot.py")) { throw "STOP: main aun no tiene tools\package_corpus_snapshot.py (falta mergear el PR #6)." }

# ---------------------------------------------------------------------
Step "[2] Entorno Python del proyecto (.venv, sin activar)"
if (-not (Test-Path ".venv\Scripts\python.exe")) { & $PyExe @PyArgs -m venv .venv; Check "crear .venv" }
$Py = ".\.venv\Scripts\python.exe"
& $Py -m pip install --upgrade pip; Check "pip"
& $Py -m pip install -r requirements-knowledge.txt; Check "requirements-knowledge"

# ---------------------------------------------------------------------
Step "[3] Descargar corpus e indice del release publico $Tag"
$Dl = "$Base\kingscode_descargas"
New-Item -ItemType Directory -Force $Dl | Out-Null
$Url = "https://github.com/$GitHubRepo/releases/download/$Tag"
foreach ($f in @("kingscode-corpus-v0.1.tar.gz", "snapshot-files.sha256.json", "dense.npy", "dense.meta.json", "SHA256SUMS.txt")) {
    if (-not (Test-Path "$Dl\$f")) {
        Write-Host "Descargando $f ..."
        try { Invoke-WebRequest -UseBasicParsing -Uri "$Url/$f" -OutFile "$Dl\$f" }
        catch {
            if ($f -like "dense*") { Write-Host "AVISO: el release no trae $f; quedara solo BM25." -ForegroundColor Yellow }
            else { throw "STOP: no pude descargar $f desde $Url (existe el release $Tag?)." }
        }
    }
}

# ---------------------------------------------------------------------
Step "[4] Verificar ANTES de extraer (archivo por archivo)"
& $Py tools\package_corpus_snapshot.py verify "$Dl\kingscode-corpus-v0.1.tar.gz" --files "$Dl\snapshot-files.sha256.json"; Check "verificacion del snapshot"
$HaveDense = (Test-Path "$Dl\dense.npy") -and (Test-Path "$Dl\dense.meta.json")
if ($HaveDense) {
    if ((Get-FileHash -Algorithm SHA256 "$Dl\dense.npy").Hash.ToLower() -ne $DenseSha -or
        (Get-FileHash -Algorithm SHA256 "$Dl\dense.meta.json").Hash.ToLower() -ne $DenseMetaSha) {
        throw "STOP: el indice denso descargado no coincide con el freeze de la 4090."
    }
    Write-Host "Indice denso verificado."
}

# ---------------------------------------------------------------------
Step "[5] Colocar el corpus en $Repo\corpus"
if (Test-Path "corpus\manifest.json") { throw "STOP: ya existe corpus\ en este repo; no se sobrescribe." }
tar -xzf "$Dl\kingscode-corpus-v0.1.tar.gz" -C .; Check "tar -xzf"
if ($HaveDense) { Copy-Item "$Dl\dense.npy", "$Dl\dense.meta.json" "corpus\index\" }

# ---------------------------------------------------------------------
Step "[6] Validar contra los hashes de A"
& $Py tools\verify_member_a_v02.py | Out-File -Encoding utf8 "$Dl\verify_member_a_v02.json"; Check "verify_member_a_v02"
Write-Host "Corpus v0.1 validado (ver $Dl\verify_member_a_v02.json)." -ForegroundColor Green

# ---------------------------------------------------------------------
if (-not $SkipSmoke) {
    Step "[7] Prueba real en CPU: 50 preguntas con BM25 del corpus real (decoder dummy; no es un puntaje)"
    $Run = "runs\smoke_bm25_$(Get-Date -Format yyyyMMdd_HHmmss)"
    & $Py tools\member_b.py batch --input data\sample_50.jsonl --run-dir $Run --fresh --exact-locator; Check "batch"
    & $Py scripts\evaluate.py --submission "$Run\submissions.jsonl" --split sample --out "$Run\evaluation.json"; Check "evaluate"
}

Write-Host ""
Write-Host "MAQUINA LISTA. Siguiente paso, si esta PC tiene GPU NVIDIA:" -ForegroundColor Green
Write-Host "  cd `"$Repo`""
Write-Host "  powershell -ExecutionPolicy Bypass -File tools\lab_gpu_session.ps1 -Repo `"$Repo`" -InstallTorch -DownloadModels -DecoderSmoke -FreezePlans -RunSample"
