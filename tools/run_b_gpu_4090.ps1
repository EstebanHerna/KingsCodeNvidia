# ============================================================
# KINGSCODE B - RUNNER DE DECODER (4090, .venv existente)
#
# Fases (docs/GPU_DAY_RUNBOOK.md, sec. 8):
#   -Phase prep     (PERMITIDA HOY) entorno, corpus, estado del denso y pesos
#                   de los decoders elegibles. No genera respuestas.
#   -Phase decoder  (BLOQUEADA hasta el freeze de A) decoder-smoke y sample_50
#                   de cada decoder sobre EL MISMO artifacts\retrieval_freeze.json
#                   (8 evidencias por pregunta), hash del freeze verificado antes
#                   y despues de cada decoder. Sin retrieval en vivo, sin planner.
#
# Decoders por defecto: qwen3-8b (opcion sugerida textualmente en el enunciado sec. 3.1)
#   y alia-legal-7b (~7,77B). Salamandra se agrega si hay HF_TOKEN.
#   -IncludePendingEligibility se conserva solo por compatibilidad; ya no cambia nada.
#
# No modifica el repo ni la rama de Luis (worktree de main aparte; corpus\ y
# models\ enlazados). No borra nada. Restaura la suspension al terminar.
# Sin RAGAS, sin tuning, sin holdout, sin seleccion de decoder.
#
# Uso:
#   powershell -ExecutionPolicy Bypass -File run_b_gpu_4090.ps1 -Phase prep
#   powershell -ExecutionPolicy Bypass -File run_b_gpu_4090.ps1 -Phase decoder
#   ... -Models alia-legal-7b         (un solo decoder)
# ============================================================
param(
    [ValidateSet("prep", "decoder")] [string]$Phase = "prep",
    [string]$Repo = "C:\Users\ls.contreras\KingsCodeGPU\KingsCodeNvidia",
    [string]$Work = "C:\Users\ls.contreras\KingsCodeGPU\KingsCodeRun",
    [string]$Freeze = "",
    [string]$Models = "qwen3-8b,alia-legal-7b",
    [switch]$IncludePendingEligibility
)

$Py      = "$Repo\.venv\Scripts\python.exe"
$Script  = Join-Path (Split-Path $Work) "kingscode_b_gpu_run.py"
$LogRoot = "$Work\reports\lab_session"
$Pending = ""
if ($env:HF_TOKEN) { $Models = "$Models,salamandra-7b" }   # Salamandra requiere acceso aprobado en HF

# ------------------------------------------------------------
# 0. Evitar dos corridas GPU simultaneas
# ------------------------------------------------------------
$running = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -match "python" -and ($_.CommandLine -match "search_v2.py|evaluate_retrieval_benchmark.py|kingscode_b_gpu_run.py|gpu_smoke.py|member_b.py|independent_ir_v2.py")
}
if ($running) {
    Write-Host "YA HAY UNA CORRIDA GPU EN CURSO:"
    $running | Select-Object ProcessId, CommandLine | Format-List
    throw "No se lanzara una segunda copia."
}

# ------------------------------------------------------------
# 1. Worktree de main (no toca la rama ni los archivos de Luis)
# ------------------------------------------------------------
if (-not (Test-Path "$Repo\corpus\manifest.json")) { throw "No existe $Repo\corpus\manifest.json" }
if (-not (Test-Path $Py)) { throw "No existe el .venv en $Py" }
git -C $Repo fetch origin main
if ($LASTEXITCODE -ne 0) { throw "git fetch fallo." }
if (-not (Test-Path "$Work\.git")) {
    git -C $Repo worktree add --detach $Work origin/main
    if ($LASTEXITCODE -ne 0) { throw "git worktree add fallo." }
} else {
    if (git -C $Work status --porcelain --untracked-files=no) { git -C $Work status --short; throw "El worktree $Work tiene cambios en archivos versionados; revisalos antes de continuar (no se descartan automaticamente)." }
    git -C $Work checkout --detach origin/main
    if ($LASTEXITCODE -ne 0) { throw "No pude poner el worktree en origin/main." }
}
if (-not (Test-Path "$Work\corpus")) { cmd /c "mklink /J `"$Work\corpus`" `"$Repo\corpus`"" | Out-Null }
if (-not (Test-Path "$Repo\models")) { New-Item -ItemType Directory -Force "$Repo\models" | Out-Null }
if (-not (Test-Path "$Work\models")) { cmd /c "mklink /J `"$Work\models`" `"$Repo\models`"" | Out-Null }
Write-Host "Worktree: $Work @ $((git -C $Work rev-parse HEAD).Trim())"
New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null

# ------------------------------------------------------------
# 2. Gate de la fase decoder: freeze de A
# ------------------------------------------------------------
if (-not $Freeze) { $Freeze = "$Work\artifacts\retrieval_freeze.json" }
if ($Phase -eq "decoder" -and -not (Test-Path $Freeze)) {
    throw "BLOCKED_ON_A_FREEZE: no existe $Freeze. Segun GPU_DAY_RUNBOOK sec. 8, decoder-smoke/sample/bakeoff esperan la seleccion confirmada de A y su freeze de ocho evidencias."
}

# ------------------------------------------------------------
# 3. Runner fuera del working tree
# ------------------------------------------------------------
@'
"""KingsCode B GPU runner. Sequential subprocesses, each step logged. Never edits answers, never deletes."""
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

WORK, PHASE, MODELS, PENDING, FREEZE, OLD_STANDBY = Path(sys.argv[1]), sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]
MODELS = [m for m in MODELS.split(",") if m]
PENDING = {m for m in PENDING.split(",") if m and m != "-"}
DRY = "--dry-run" in sys.argv
PY = sys.executable
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
OUT = WORK / "reports" / "lab_session" / f"{STAMP}_{PHASE}"
OUT.mkdir(parents=True, exist_ok=True)
(WORK / "reports" / "lab_session" / "LATEST.txt").write_text(str(OUT), encoding="utf-8")
summary = {"run": str(OUT), "phase": PHASE, "models": MODELS,
           "eligibility": {m: ("suggested_in_statement_3_1" if m in ("qwen3-8b", "llama31-8b") else "within_8B") for m in MODELS},
           "steps": []}


def save():
    (OUT / "SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def step(name, args, *, fatal=True):
    print("=" * 72, flush=True)
    print(f"[{name}] {' '.join(args)}", flush=True)
    if DRY:
        summary["steps"].append({"step": name, "status": "dry_run"}); save(); return 0, ""
    start = time.perf_counter()
    log_path = OUT / f"{name}.log"
    lines = []
    with log_path.open("w", encoding="utf-8") as fh:
        proc = subprocess.Popen([PY, *args], cwd=WORK, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                encoding="utf-8", errors="replace", env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
        for line in proc.stdout:
            fh.write(line); lines.append(line); print(line, end="", flush=True)
        rc = proc.wait()
    summary["steps"].append({"step": name, "returncode": rc, "seconds": round(time.perf_counter() - start, 1), "log": str(log_path)})
    save()
    if rc != 0 and fatal:
        summary["status"] = f"stopped_at_{name}"; save()
        raise SystemExit(f"STOP en {name} (rc={rc}); ver {log_path}")
    return rc, "".join(lines)


def last_json(text):
    """member_b.py prints one indent=2 JSON object last; its opening brace is the last '{' at column 0."""
    start = 0 if text.startswith("{") else text.rfind("\n{") + 1
    try:
        return json.loads(text[start:]) if start > 0 or text.startswith("{") else None
    except ValueError:
        return None


def dense_status():
    idx = WORK / "corpus" / "index"
    if not (idx / "dense.npy").exists() or not (idx / "dense.meta.json").exists():
        return {"status": "missing"}
    sys.path.insert(0, str(WORK))
    from kingscode.common import indexable, read_jsonl
    meta = json.loads((idx / "dense.meta.json").read_text(encoding="utf-8"))
    cfg = json.loads((WORK / "config/neural.json").read_text(encoding="utf-8"))
    lock = json.loads((WORK / "config/models.lock.json").read_text(encoding="utf-8"))
    ids = [p["passage_id"] for p in read_jsonl(WORK / "corpus/passages.jsonl") if indexable(p)]
    problems = [n for n, ok in (("vectors_sha256", meta.get("vectors_sha256") == sha(idx / "dense.npy")),
                                ("corpus_sha256", meta.get("corpus_sha256") == sha(WORK / "corpus/passages.jsonl")),
                                ("passage_ids", meta.get("passage_ids") == ids), ("config", meta.get("config") == cfg),
                                ("model_lock", meta.get("model_lock") == lock.get(cfg["embedding_model"]))) if not ok]
    return {"status": "valid" if not problems else "stale", "problems": problems,
            "matches_4090_freeze": sha(idx / "dense.npy") == "0c156c5e95dce92d6abd6404a39242bd724228bfdf99f4e9e44ddf5dd16b8347"}


try:
    print(f"KINGSCODE B GPU RUN [{PHASE}] -> {OUT}", flush=True)
    step("env", ["-c", "import json,torch,transformers,jsonschema,huggingface_hub,accelerate;p=torch.cuda.get_device_properties(0);"
                       "print(json.dumps({'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':p.name,"
                       "'vram_gb':round(p.total_memory/2**30,1),'bf16':torch.cuda.is_bf16_supported(),"
                       "'transformers':transformers.__version__}))"])
    step("verify_corpus", ["tools/verify_member_a_v02.py"])
    if PHASE == "prep":
        summary["dense"] = "dry_run" if DRY else dense_status(); save()
        print("DENSE:", summary["dense"], flush=True)
        for m in MODELS:
            step(f"weights_{m}", ["tools/prepare_models.py", "--download", m])
            step(f"verify_weights_{m}", ["tools/prepare_models.py", "--verify", m])
        summary["status"] = "prep_done_decoder_phase_blocked_until_A_freeze"
    else:
        step("validate_freeze", ["-c", "import sys; sys.path.insert(0, '.'); from pathlib import Path; "
                                       "from kingscode.generation.retrieval_experiments import load_freeze; "
                                       f"f = load_freeze(Path(r'{FREEZE}')); print('freeze ok', f['fingerprint'], len(f['records']))"])
        freeze_sha = "dry_run" if DRY else sha(FREEZE)
        summary["freeze"] = {"path": FREEZE, "sha256": freeze_sha}
        results = []
        for m in MODELS:
            if not DRY and sha(FREEZE) != freeze_sha:
                raise SystemExit(f"STOP: el freeze cambio antes de {m}")
            rc, _ = step(f"decoder_smoke_{m}", ["tools/member_b.py", "decoder-smoke", "--model", m, "--allow-optional"], fatal=False)
            if rc != 0:
                results.append({"model": m, "status": "smoke_failed"}); continue
            rc, text = step(f"sample_{m}", ["tools/member_b.py", "sample", "--model", m, "--retrieval-freeze", FREEZE, "--allow-optional"], fatal=False)
            if not DRY and sha(FREEZE) != freeze_sha:
                raise SystemExit(f"STOP: el freeze cambio durante {m}")
            record = last_json(text) or {}
            auto = (record.get("official_evaluation") or {}).get("total_automatico") or {}
            total = f"{auto.get('obtenidos')} / {auto.get('posibles')}" if auto else None
            results.append({"model": m, "status": record.get("status", "dry_run" if DRY else "failed"),
                            "eligibility": summary["eligibility"][m], "official_without_ragas": total,
                            "metrics": record.get("metrics"), "paths": record.get("paths"), "error": record.get("error")})
            save()
        summary["decoder_results"] = results
        summary["selection"] = "none: comparison only; eligibility and RAGAS finalists decided separately"
        summary["status"] = "decoder_phase_done"
    save()
    print("=" * 72, flush=True)
    for r in summary.get("decoder_results", []):
        print(f"{r['model']}: {r['status']} | {r.get('official_without_ragas')} automatico sin RAGAS | {r.get('eligibility')}", flush=True)
    print(f"B GPU RUN FINISHED [{summary['status']}] -> {OUT}", flush=True)
finally:
    if OLD_STANDBY.isdigit() and not DRY:
        subprocess.run(["powercfg", "/change", "standby-timeout-ac", OLD_STANDBY], check=False)
        print(f"Suspension AC restaurada a {OLD_STANDBY} min", flush=True)
'@ | Set-Content $Script -Encoding ASCII

# ------------------------------------------------------------
# 4. Verificar .venv + CUDA
# ------------------------------------------------------------
Write-Host "`n========== PYTHON / CUDA =========="
& $Py -c "import sys,torch; print('PYTHON=',sys.executable); print('TORCH=',torch.__version__); print('CUDA=',torch.cuda.is_available()); print('GPU=',torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)"
if ($LASTEXITCODE -ne 0) { throw "Fallo la verificacion del .venv/CUDA." }

# ------------------------------------------------------------
# 5. Suspension: guardar valor actual, desactivar, el runner lo restaura
# ------------------------------------------------------------
$OldStandby = "keep"
# Salida de powercfg (cualquier idioma): min, max, incremento, AC actual, DC actual -> AC es el penultimo 0x........
$vals = @(powercfg /query SCHEME_CURRENT SUB_SLEEP STANDBYIDLE | Select-String "0x([0-9a-fA-F]{8})\s*$" | ForEach-Object { $_.Matches[0].Groups[1].Value })
if ($vals.Count -ge 2) {
    $OldStandby = [string][int]([Convert]::ToInt64($vals[-2], 16) / 60)
    powercfg /change standby-timeout-ac 0
    Write-Host "Suspension AC desactivada (valor previo: $OldStandby min; se restaura al terminar)."
} else {
    Write-Host "No pude leer la suspension actual; no se modifica."
}

# ------------------------------------------------------------
# 6. Lanzar EN SEGUNDO PLANO
# ------------------------------------------------------------
$stdout = "$LogRoot\B_GPU_$Phase.stdout.log"
$stderr = "$LogRoot\B_GPU_$Phase.stderr.log"
$p = Start-Process -FilePath $Py `
    -ArgumentList @("-u", $Script, $Work, $Phase, $Models, $(if ($Pending) { $Pending } else { "-" }), $Freeze, $OldStandby) `
    -WorkingDirectory $Work -RedirectStandardOutput $stdout -RedirectStandardError $stderr -PassThru
$p.Id | Set-Content "$LogRoot\B_GPU_$Phase.pid"

Write-Host ""
Write-Host "============================================================"
Write-Host "B GPU RUN [$Phase] INICIADO  PID: $($p.Id)  MODELOS: $Models"
Write-Host "STDOUT: $stdout"
Write-Host "============================================================"
Start-Sleep -Seconds 5
Get-Content $stdout -Tail 20 -ErrorAction SilentlyContinue
Write-Host "`nMonitorear:  Get-Content `"$stdout`" -Wait"
Write-Host "Resumen:     Get-Content (Join-Path (Get-Content `"$LogRoot\LATEST.txt`") SUMMARY.json)"
if ($OldStandby -ne "keep") { Write-Host "Si detienes el proceso a mano, restaura la suspension:  powercfg /change standby-timeout-ac $OldStandby" }
