# =====================================================================
# SCRIPT 1 - En la PC que YA TIENE corpus\ (la PC de la RTX 4090)
# Empaqueta corpus v0.1 + indice denso + LICENSE, verifica todo y lo
# publica como release de GitHub (repo publico => enlace de descarga
# directa, sin permisos, cumple el entregable 5).
#
# No modifica el repositorio de esa PC: solo LEE corpus\ y escribe en
# una carpeta aparte (%USERPROFILE%\kingscode_upload\<fecha>).
#
# Uso (PowerShell, cualquier carpeta):
#   powershell -ExecutionPolicy Bypass -File subir_corpus_snapshot.ps1
#   powershell -ExecutionPolicy Bypass -File subir_corpus_snapshot.ps1 -Repo "C:\ruta\KingsCodeNvidia"
#   ... -NoUpload   (solo empaqueta; luego se sube a mano a Drive)
# =====================================================================
param(
    [string]$Repo = "",
    [string]$GitHubRepo = "IngSeb0/KingsCodeNvidia",
    [string]$Tag = "corpus-v0.1-snapshot",
    [string]$License = "CC BY 4.0",
    [switch]$NoUpload,
    [switch]$NoOpen
)
$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
function Step($m) { Write-Host ""; Write-Host ">>> $m" -ForegroundColor Cyan }
function Check($w) { if ($LASTEXITCODE -ne 0) { throw "STOP: $w (exit $LASTEXITCODE)" } }

# Hashes del freeze de la 4090 (reports/gpu_freeze_4090/CRITICAL_ARTIFACT_HASHES.json)
$DenseSha = "0c156c5e95dce92d6abd6404a39242bd724228bfdf99f4e9e44ddf5dd16b8347"
$DenseMetaSha = "c63c929cb85311c345b9e7cefa3245748a9f16bd3a12ce396563bc07cddb23cb"

# ---------------------------------------------------------------------
Step "[0] Ubicar el repositorio que tiene corpus\"
$Candidates = @($Repo, "$HOME\KingsCodeGPU\KingsCodeNvidia", "$HOME\KingsCodeNvidia",
                "$HOME\Downloads\KingsCodeNvidia", "$HOME\Desktop\KingsCodeNvidia", (Get-Location).Path)
$Repo = $Candidates | Where-Object { $_ -and (Test-Path (Join-Path $_ "corpus\manifest.json")) } | Select-Object -First 1
if (-not $Repo) {
    $Tmp = $Candidates | Where-Object { $_ -and (Test-Path (Join-Path $_ "tmp\benchmark_corpus_v1\manifest.json")) } | Select-Object -First 1
    if ($Tmp) { throw "STOP: solo existe $Tmp\tmp\benchmark_corpus_v1. El empaquetador necesita corpus\ en la raiz del repo (con raw\ y clean\). Copia o restaura corpus\ ahi y vuelve a correr." }
    throw "STOP: no encontre ningun repo con corpus\manifest.json. Pasa la ruta: -Repo 'C:\ruta\KingsCodeNvidia'"
}
Set-Location $Repo
Write-Host "Repo: $Repo"
git rev-parse HEAD

# ---------------------------------------------------------------------
Step "[1] Python 3.11+ (solo libreria estandar; no instala nada)"
$PyExe = $null
foreach ($c in @(@{Exe = ".\.venv\Scripts\python.exe"; Args = @()}, @{Exe = "py"; Args = @("-3.12")},
                 @{Exe = "py"; Args = @("-3.11")}, @{Exe = "python"; Args = @()})) {
    try {
        $v = & $c.Exe @($c.Args) -c "import sys; print(sys.version_info >= (3, 11))"
        if ($v -eq "True") { $PyExe = $c.Exe; $PyArgs = $c.Args; break }
    } catch { }
}
if (-not $PyExe) { throw "STOP: se necesita Python 3.11 o superior (hashlib.file_digest)." }
function RunPy { & $PyExe @PyArgs @args }
Write-Host "Python: $PyExe $PyArgs"

# ---------------------------------------------------------------------
Step "[2] Herramienta de empaquetado (del repo del equipo, sin tocar tu rama)"
$Tool = Join-Path $Repo "tools\package_corpus_snapshot.py"
if (-not (Test-Path $Tool)) {
    git fetch origin; Check "git fetch origin"
    $Tool = Join-Path $env:TEMP "kc_package_corpus_snapshot.py"
    $ok = $false
    foreach ($ref in @("origin/main", "origin/docs/mapa-del-repo")) {
        cmd /c "git show ${ref}:tools/package_corpus_snapshot.py > `"$Tool`" 2>nul"
        if ($LASTEXITCODE -eq 0 -and (Get-Item $Tool).Length -gt 0) { $ok = $true; Write-Host "Herramienta tomada de $ref"; break }
    }
    if (-not $ok) { throw "STOP: no encontre tools/package_corpus_snapshot.py en origin/main ni en origin/docs/mapa-del-repo." }
}

# ---------------------------------------------------------------------
$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Out = "$HOME\kingscode_upload\$Stamp"
$Bundle = "$Out\kingscode_corpus_e_indice_v0.1"
New-Item -ItemType Directory -Force "$Bundle\indice_denso" | Out-Null

Step "[3] Empaquetar corpus v0.1 (verifica hashes antes y despues)"
RunPy $Tool pack --root $Repo --out "$Bundle\corpus_snapshot"; Check "empaquetado del corpus"
RunPy $Tool verify "$Bundle\corpus_snapshot\kingscode-corpus-v0.1.tar.gz" --files "$Bundle\corpus_snapshot\snapshot-files.sha256.json"; Check "verificacion del paquete"

# ---------------------------------------------------------------------
Step "[4] Indice denso (dense.npy + dense.meta.json)"
$DenseDir = @("$Repo\corpus\index", "$Repo\tmp\benchmark_corpus_v1\index") |
    Where-Object { (Test-Path "$_\dense.npy") -and (Test-Path "$_\dense.meta.json") } | Select-Object -First 1
$HaveDense = $false
if ($DenseDir) {
    $h1 = (Get-FileHash -Algorithm SHA256 "$DenseDir\dense.npy").Hash.ToLower()
    $h2 = (Get-FileHash -Algorithm SHA256 "$DenseDir\dense.meta.json").Hash.ToLower()
    if ($h1 -ne $DenseSha -or $h2 -ne $DenseMetaSha) {
        throw "STOP: el indice denso de $DenseDir no coincide con el freeze de la 4090 (dense $h1 / meta $h2)."
    }
    Copy-Item "$DenseDir\dense.npy", "$DenseDir\dense.meta.json" "$Bundle\indice_denso\"
    $HaveDense = $true
    Write-Host "Indice denso verificado desde $DenseDir"
} else {
    Write-Host "AVISO: no encontre dense.npy; el paquete queda solo con BM25 (el denso se puede reconstruir en GPU)." -ForegroundColor Yellow
}

# ---------------------------------------------------------------------
Step "[5] LICENSE (decision del equipo: $License)"
@"
KingsCode - corpus procesado e indices (corpus-v0.1)

Licencia de la compilacion, el procesamiento y los indices: $License
https://creativecommons.org/licenses/by/4.0/legalcode

Los textos juridicos provienen de fuentes oficiales colombianas; la URL,
fecha de consulta y hash de cada documento estan en corpus/manifest.json.
Equipo KingsCode - Hackathon 2026, Universidad de los Andes.
"@ | Out-File -Encoding ascii "$Bundle\LICENSE.txt"
Copy-Item "$Bundle\corpus_snapshot\LEEME.txt" "$Bundle\LEEME.txt"

# ---------------------------------------------------------------------
Step "[6] Archivo unico para el jurado (.zip) y sumas SHA-256"
$Zip = "$Out\kingscode_corpus_e_indice_v0.1.zip"
Compress-Archive -Path "$Bundle\*" -DestinationPath $Zip
$Assets = @($Zip, "$Bundle\corpus_snapshot\kingscode-corpus-v0.1.tar.gz",
            "$Bundle\corpus_snapshot\snapshot-files.sha256.json", "$Bundle\LEEME.txt", "$Bundle\LICENSE.txt")
if ($HaveDense) { $Assets += @("$Bundle\indice_denso\dense.npy", "$Bundle\indice_denso\dense.meta.json") }
$Sums = "$Out\SHA256SUMS.txt"
$Assets | ForEach-Object { "{0}  {1}" -f (Get-FileHash -Algorithm SHA256 $_).Hash.ToLower(), (Split-Path $_ -Leaf) } |
    Out-File -Encoding ascii $Sums
$Assets += $Sums
Get-Content $Sums

# ---------------------------------------------------------------------
Step "[7] Publicar"
$Gh = Get-Command gh -ErrorAction SilentlyContinue
if ($NoUpload -or -not $Gh) {
    if (-not $Gh) { Write-Host "No hay GitHub CLI (gh). Subelo a mano:" -ForegroundColor Yellow }
    Write-Host "  1. Sube $Zip a Google Drive/OneDrive."
    Write-Host "  2. Compartir -> 'Cualquier persona con el enlace' -> Lector."
    Write-Host "  3. Pega el enlace en README.md, seccion '## Corpus e indice'."
    if (-not $NoOpen) { explorer $Out }
    exit 0
}
cmd /c "gh auth status >nul 2>&1"
if ($LASTEXITCODE -ne 0) { gh auth login; Check "gh auth login" }
cmd /c "gh release view $Tag --repo $GitHubRepo >nul 2>&1"
if ($LASTEXITCODE -eq 0) { throw "STOP: ya existe el release $Tag. Revisalo en GitHub antes de reemplazar nada (o usa -Tag con otro nombre)." }
$Notes = "Snapshot historico corpus-v0.1 (163 documentos, 26.558 pasajes, grafo, BM25" + $(if ($HaveDense) { " e indice denso Qwen" } else { "" }) + "). No es un freeze competitivo. Verificar con tools/package_corpus_snapshot.py verify. Sumas en SHA256SUMS.txt."
gh release create $Tag @Assets --repo $GitHubRepo --title "Corpus e indice KingsCode v0.1" --notes $Notes; Check "gh release create"

$Url = "https://github.com/$GitHubRepo/releases/tag/$Tag"
Write-Host ""
Write-Host "LISTO. Release: $Url" -ForegroundColor Green
Write-Host "Enlace directo para el README (seccion '## Corpus e indice'):"
Write-Host "  https://github.com/$GitHubRepo/releases/download/$Tag/kingscode_corpus_e_indice_v0.1.zip"
Write-Host "Comprueba que descarga en una ventana privada del navegador."
