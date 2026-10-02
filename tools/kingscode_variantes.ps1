# =====================================================================
# KingsCode - pruebas rapidas de variantes sobre sample_50 (una variable por corrida)
#
# Corre cada variante con tools\kingscode_pc_nueva_diagnostico.ps1 (-SkipSmoke -SkipVerify para
# ahorrar ~2 min por variante), sigue aunque una falle y al final imprime una tabla contra la base.
# La verificacion en vivo se hace solo en la configuracion final (sin -SkipVerify).
#
# Uso:
#   powershell -ExecutionPolicy Bypass -File tools\kingscode_variantes.ps1
#   ... -Variantes prompt_v4,citas            (solo esas)
#   ... -Variantes final -Final "-PromptVersion v4 -CitationFill -Rerank -ExactLocator"
#
# Variantes (orden: mayor valor esperado y menor costo primero):
#   prompt_v4       -PromptVersion v4          (~13 min; sin costo extra de tiempo)
#   citas           -CitationFill              (~13 min; sin costo extra de tiempo)
#   rerank_locator  -Rerank -ExactLocator      (~15 min; el locator solo actua con reranker)
#   rerank          -Rerank                    (~15 min; separa el efecto del locator)
#   hybrid          -RetrieverMode hybrid      (indice denso la primera vez, ~5-10 min con el build ordenado por largo)
#   alia            -Model alia-legal-7b       (descarga ~15 GB la primera vez)
# =====================================================================
param(
    [string[]]$Variantes = @("prompt_v4", "citas", "rerank_locator", "rerank", "hybrid", "alia"),
    [string]$Final = "",
    [string]$Work = "$HOME\KingsCodeGPU\KingsCodeNvidia",
    [switch]$Pull   # por defecto NO actualiza durante la tanda: todas las variantes usan el mismo commit
)
$ErrorActionPreference = "Continue"
# With powershell -File, "a,b,c" arrives as ONE string: split it here.
$Variantes = @($Variantes | ForEach-Object { $_ -split "," } | ForEach-Object { $_.Trim() } | Where-Object { $_ })
Set-Location $Work
if ($Pull) { git pull --ff-only origin main }
Write-Host "Commit congelado para toda la tanda: $((git rev-parse --short HEAD).Trim())" -ForegroundColor Cyan
$S = ".\tools\kingscode_pc_nueva_diagnostico.ps1"
$Catalogo = [ordered]@{
    "prompt_v4"      = @("-PromptVersion", "v4")
    "citas"          = @("-CitationFill")
    "menciones"      = @("-PromptVersion", "v4", "-CitationFill", "-CiteMentions", "3")
    "recomendada"    = @("-Recomendada")
    "rerank_locator" = @("-Rerank", "-ExactLocator")
    "rerank"         = @("-Rerank")
    "hybrid"         = @("-RetrieverMode", "hybrid")
    "alia"           = @("-Model", "alia-legal-7b")
}
$Inicio = Get-Date
foreach ($v in $Variantes) {
    if ($v -eq "final") {
        if (-not $Final) { Write-Host "final requiere -Final '<flags>'" -ForegroundColor Yellow; continue }
        $a = @($Final -split "\s+" | Where-Object { $_ })
        Write-Host "`n################ CONFIGURACION FINAL (con verificacion en vivo): $Final ################" -ForegroundColor Magenta
        powershell -ExecutionPolicy Bypass -File $S -SkipSmoke -NoPull @a
        continue
    }
    if (-not $Catalogo.Contains($v)) { Write-Host "Variante desconocida: $v" -ForegroundColor Yellow; continue }
    $a = @($Catalogo[$v]) + @("-SkipSmoke", "-SkipVerify", "-NoPull")
    $t0 = Get-Date
    Write-Host "`n################ VARIANTE: $v ($($Catalogo[$v] -join ' ')) ################" -ForegroundColor Magenta
    powershell -ExecutionPolicy Bypass -File $S @a
    Write-Host ("Variante {0}: {1:N1} min" -f $v, ((Get-Date) - $t0).TotalMinutes) -ForegroundColor Cyan
}

# ---------------------------------------------------------------------
$Base = 26.63   # qwen3-8b + bm25 + router, prompt v3 (2026-10-01, sha 3ec5651a...)
$Filas = Get-ChildItem ".\reports\decoder_diagnostic" -Directory | Sort-Object LastWriteTime | ForEach-Object {
    $f = "$($_.FullName)\RESUMEN.json"
    if (Test-Path $f) {
        $r = Get-Content $f -Raw | ConvertFrom-Json; $d = $r.diagnostics
        $tot = [double](($r.automatico_sin_ragas -split "/")[0].Trim())
        [pscustomobject]@{
            corrida = $_.Name; total = $tot; delta = [math]::Round($tot - $Base, 2)
            cerr = $r.cerradas; citas = $r.citas; abst = $r.abstencion; fb = $r.fallbacks_pipeline_error
            s_preg = $r.segundos_por_pregunta; ret_p95_ms = [math]::Round([double]$d.retrieval_ms_p95)
            vram_gb = $d.peak_reserved_vram_gb; verif = $r.verificacion_en_vivo.all_match
            apta = ($r.segundos_por_pregunta -le 20)
        }
    }
}
$Filas | Format-Table -AutoSize

# Per run: why each fallback happened (saved since PR #22) and how often the parser had to fix shape.
Write-Host "`nDetalle por corrida (fallbacks y correcciones del parser):" -ForegroundColor Cyan
Get-ChildItem ".\reports\decoder_diagnostic" -Directory | Sort-Object LastWriteTime | ForEach-Object {
    $run = $_
    if (-not (Test-Path "$($run.FullName)\RESUMEN.json")) { return }
    $r = Get-Content "$($run.FullName)\RESUMEN.json" -Raw | ConvertFrom-Json
    $why = Get-ChildItem "$($run.FullName)\batch\errors" -ErrorAction SilentlyContinue | ForEach-Object {
        $e = Get-Content $_.FullName -Raw | ConvertFrom-Json
        $reason = $e.attempts[0].detail.reason
        if (-not $reason) { $reason = $e.attempts[0].code }
        "{0}: {1}" -f $e.id, $reason
    }
    $co = $r.diagnostics.field_coercions
    $coText = $(if ($co) { ($co.PSObject.Properties | ForEach-Object { "$($_.Name)=$($_.Value.n)" }) -join ", " } else { "-" })
    $fw = $r.diagnostics.format_warnings
    $fwText = $(if ($fw) { ($fw.PSObject.Properties | ForEach-Object { "$($_.Name)=$($_.Value.n)" }) -join ", " } else { "-" })
    Write-Host ("  {0}`n    fallbacks: {1}`n    correcciones: {2}`n    avisos de extension: {3}" -f $run.Name, $(if ($why) { $why -join " | " } else { "ninguno" }), $coText, $fwText)
}
Write-Host ("Total: {0:N0} min. Base de referencia: {1}/50. 'apta' = <= 20 s/pregunta (presupuesto 22 s). Solo cuentan mejoras de ~2 puntos o mas." -f ((Get-Date) - $Inicio).TotalMinutes, $Base) -ForegroundColor Green
$Filas | Export-Csv -NoTypeInformation -Encoding UTF8 ".\reports\decoder_diagnostic\comparacion.csv"
Write-Host "Tabla guardada en reports\decoder_diagnostic\comparacion.csv"
