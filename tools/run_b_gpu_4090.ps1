cd "C:\Users\ls.contreras\KingsCodeGPU\KingsCodeNvidia"

# ============================================================
# KINGSCODE B - DECODER REAL EN LA 4090
# - USA EL .VENV EXISTENTE (torch/transformers ya instalados)
# - NO MODIFICA EL REPO NI LA RAMA DE LUIS: worktree de main aparte
# - corpus\ y models\ se ENLAZAN (junction), no se copian
# - RUNNER FUERA DEL WORKING TREE, EN SEGUNDO PLANO, CON LOGS
# - SIN RAGAS, SIN TUNING, SIN HOLDOUT, SIN SELECCION DE DECODER
# Pasos del runner:
#   env -> corpus -> denso -> pesos -> smoke -> planes -> sample_50 -> evaluador -> presupuesto 992
# ============================================================

$Repo    = "C:\Users\ls.contreras\KingsCodeGPU\KingsCodeNvidia"
$Work    = "C:\Users\ls.contreras\KingsCodeGPU\KingsCodeRun"
$Py      = "$Repo\.venv\Scripts\python.exe"
$Script  = "C:\Users\ls.contreras\KingsCodeGPU\kingscode_b_gpu_run.py"
$Models  = "qwen3-8b"            # ej. "qwen3-8b,alia-legal-7b" (exploratorio, sin seleccion)
$LogRoot = "$Work\reports\lab_session"

# ------------------------------------------------------------
# 0. Evitar dos corridas GPU simultaneas
# ------------------------------------------------------------

$running = Get-CimInstance Win32_Process |
Where-Object {
    $_.Name -match "python" -and (
        $_.CommandLine -match "search_v2.py" -or
        $_.CommandLine -match "evaluate_retrieval_benchmark.py" -or
        $_.CommandLine -match "kingscode_b_gpu_run.py" -or
        $_.CommandLine -match "gpu_smoke.py" -or
        $_.CommandLine -match "member_b.py"
    )
}

if ($running) {
    Write-Host "YA HAY UNA CORRIDA GPU EN CURSO:"
    $running | Select-Object ProcessId, ExecutablePath, CommandLine | Format-List
    throw "No se lanzara una segunda copia."
}

# ------------------------------------------------------------
# 1. Worktree de main (no toca la rama ni los archivos de Luis)
# ------------------------------------------------------------

if (-not (Test-Path "$Repo\corpus\manifest.json")) { throw "No existe $Repo\corpus\manifest.json" }

git -C $Repo fetch origin main
if ($LASTEXITCODE -ne 0) { throw "git fetch fallo." }

if (-not (Test-Path "$Work\.git")) {
    git -C $Repo worktree add --detach $Work origin/main
    if ($LASTEXITCODE -ne 0) { throw "git worktree add fallo." }
} else {
    git -C $Work checkout -- reports/member_a_v02/verification.json 2>$null   # lo reescribe el verificador de A
    git -C $Work checkout --detach origin/main
    if ($LASTEXITCODE -ne 0) { throw "No pude poner el worktree en origin/main (hay cambios locales en $Work?)." }
}

if (-not (Test-Path "$Work\corpus")) { cmd /c "mklink /J `"$Work\corpus`" `"$Repo\corpus`"" | Out-Null }
if (-not (Test-Path "$Repo\models")) { New-Item -ItemType Directory -Force "$Repo\models" | Out-Null }
if (-not (Test-Path "$Work\models")) { cmd /c "mklink /J `"$Work\models`" `"$Repo\models`"" | Out-Null }

Write-Host "Worktree: $Work @ $((git -C $Work rev-parse HEAD).Trim())"
New-Item -ItemType Directory -Force -Path $LogRoot | Out-Null

# ------------------------------------------------------------
# 2. Runner fuera del working tree
# ------------------------------------------------------------

@'
"""KingsCode B GPU runner. Sequential subprocesses, each step logged; never edits answers."""
import hashlib
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

WORK = Path(sys.argv[1])
MODELS = [m.strip() for m in sys.argv[2].split(",") if m.strip()]
DRY = "--dry-run" in sys.argv
PY = sys.executable
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
OUT = WORK / "reports" / "lab_session" / STAMP
OUT.mkdir(parents=True, exist_ok=True)
(WORK / "reports" / "lab_session" / "LATEST.txt").write_text(str(OUT), encoding="utf-8")
summary = {"run": str(OUT), "models": MODELS, "python": PY, "steps": []}


def save():
    (OUT / "SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def step(name, args, *, fatal=True, log=None):
    print("=" * 72, flush=True)
    print(f"[{name}] {' '.join(args)}", flush=True)
    if DRY:
        summary["steps"].append({"step": name, "status": "dry_run"}); return 0
    start = time.perf_counter()
    log_path = OUT / (log or f"{name}.log")
    with log_path.open("w", encoding="utf-8") as fh:
        proc = subprocess.Popen([PY, *args], cwd=WORK, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace", env={**__import__("os").environ,
                                "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
        for line in proc.stdout:
            fh.write(line); print(line, end="", flush=True)
        rc = proc.wait()
    secs = time.perf_counter() - start
    summary["steps"].append({"step": name, "returncode": rc, "seconds": round(secs, 1), "log": str(log_path)})
    save()
    print(f"[{name}] rc={rc} {secs/60:.1f} min", flush=True)
    if rc != 0 and fatal:
        summary["status"] = f"stopped_at_{name}"; save()
        sys.exit(f"STOP en {name} (rc={rc}); ver {log_path}")
    return rc


def dense_status():
    idx = WORK / "corpus" / "index"
    h = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if not (idx / "dense.npy").exists() or not (idx / "dense.meta.json").exists():
        return {"status": "missing"}
    sys.path.insert(0, str(WORK))
    from kingscode.common import indexable, read_jsonl
    meta = json.loads((idx / "dense.meta.json").read_text(encoding="utf-8"))
    cfg = json.loads((WORK / "config/neural.json").read_text(encoding="utf-8"))
    lock = json.loads((WORK / "config/models.lock.json").read_text(encoding="utf-8"))
    ids = [p["passage_id"] for p in read_jsonl(WORK / "corpus/passages.jsonl") if indexable(p)]
    problems = [name for name, ok in (
        ("vectors_sha256", meta.get("vectors_sha256") == h(idx / "dense.npy")),
        ("corpus_sha256", meta.get("corpus_sha256") == h(WORK / "corpus/passages.jsonl")),
        ("passage_ids", meta.get("passage_ids") == ids),
        ("config", meta.get("config") == cfg),
        ("model_lock", meta.get("model_lock") == lock.get(cfg["embedding_model"]))) if not ok]
    return {"status": "valid" if not problems else "stale", "problems": problems,
            "matches_4090_freeze": h(idx / "dense.npy") == "0c156c5e95dce92d6abd6404a39242bd724228bfdf99f4e9e44ddf5dd16b8347"}


print("KINGSCODE B GPU RUN ->", OUT, flush=True)
step("env", ["-c", "import json,torch,transformers,jsonschema,huggingface_hub,accelerate;p=torch.cuda.get_device_properties(0);"
                   "print(json.dumps({'torch':torch.__version__,'cuda':torch.version.cuda,'gpu':p.name,"
                   "'vram_gb':round(p.total_memory/2**30,1),'bf16':torch.cuda.is_bf16_supported(),"
                   "'transformers':transformers.__version__}))"], log="env.json")
step("verify_corpus", ["tools/verify_member_a_v02.py"], log="verify_member_a_v02.json")
summary["dense"] = dense_status() if not DRY else "dry_run"; save()
print("DENSE:", summary["dense"], flush=True)

for m in MODELS:
    step(f"weights_{m}", ["tools/prepare_models.py", "--download", m])
smoke = step("decoder_smoke", ["tools/gpu_smoke.py", "--model", MODELS[0], "--precision", "bf16",
                               "--output-root", str(OUT / "decoder_smoke")], fatal=False)
step("freeze_plans", ["tools/member_b.py", "plan", "--input", "data/sample_50.jsonl", "--model", "qwen3-8b"], fatal=False)

results = []
if smoke == 0 or DRY:
    for m in MODELS:
        run_dir = WORK / "runs" / f"{STAMP}_{m}"
        step(f"sample_{m}", ["tools/member_b.py", "batch", "--input", "data/sample_50.jsonl", "--run-dir", str(run_dir),
                             "--fresh", "--model", m, "--exact-locator", "--retrieval-mode", "option"])
        step(f"evaluate_{m}", ["scripts/evaluate.py", "--submission", str(run_dir / "submissions.jsonl"),
                               "--split", "sample", "--out", str(OUT / f"evaluation_{m}.json")])
        if DRY:
            continue
        ev = json.loads((OUT / f"evaluation_{m}.json").read_text(encoding="utf-8"))
        br = json.loads((run_dir / "batch_report.json").read_text(encoding="utf-8"))
        spq = round(br["seconds"] / 50, 2)
        step(f"budget_{m}", ["tools/benchmark_budget.py", "--seconds-per-question", str(spq), "--questions", "992", "--hours", "6"], fatal=False)
        results.append({"model": m, "total_sin_ragas": ev["total_automatico"]["obtenidos"], "cerradas": ev["cerradas"]["puntos"],
                        "citas": ev["citas"]["puntos"], "abstencion": ev["abstencion"]["puntos"],
                        "errores_validacion": ev["validacion"]["errores"], "seconds_per_question": spq,
                        "fallbacks": len(br["fallback_ids"]), "diagnostics": br.get("diagnostics")})
else:
    print("El smoke del decoder fallo: no se corre sample_50 (revisar decoder_smoke.log).", flush=True)

summary["sample_results"] = results
summary["status"] = "passed" if results or DRY else "partial"
save()
print("=" * 72, flush=True)
for r in results:
    print(f"{r['model']}: {r['total_sin_ragas']} / 50 sin RAGAS | cerradas {r['cerradas']} | citas {r['citas']} | "
          f"abstencion {r['abstencion']} | {r['seconds_per_question']} s/pregunta | errores {r['errores_validacion']}", flush=True)
print("B GPU RUN FINISHED ->", OUT, flush=True)
'@ | Set-Content $Script -Encoding ASCII

# ------------------------------------------------------------
# 3. Verificar .venv + CUDA
# ------------------------------------------------------------

Write-Host "`n========== PYTHON / CUDA =========="

& $Py -c "import sys,torch; print('PYTHON=',sys.executable); print('VERSION=',sys.version); print('TORCH=',torch.__version__); print('CUDA=',torch.cuda.is_available()); print('GPU=',torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)"

if ($LASTEXITCODE -ne 0) {
    throw "Fallo la verificacion del .venv/CUDA."
}

# ------------------------------------------------------------
# 4. Evitar suspension
# ------------------------------------------------------------

powercfg /change standby-timeout-ac 0

# ------------------------------------------------------------
# 5. Lanzar EN SEGUNDO PLANO
# ------------------------------------------------------------

$stdout = "$LogRoot\B_GPU_RUN.stdout.log"
$stderr = "$LogRoot\B_GPU_RUN.stderr.log"

Remove-Item $stdout -Force -ErrorAction SilentlyContinue
Remove-Item $stderr -Force -ErrorAction SilentlyContinue

$p = Start-Process `
    -FilePath $Py `
    -ArgumentList @("-u", $Script, $Work, $Models) `
    -WorkingDirectory $Work `
    -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr `
    -PassThru

$p.Id | Set-Content "$LogRoot\B_GPU_RUN.pid"

Write-Host ""
Write-Host "============================================================"
Write-Host "B GPU RUN INICIADO"
Write-Host "PID: $($p.Id)"
Write-Host "STDOUT: $stdout"
Write-Host "STDERR: $stderr"
Write-Host "============================================================"

Start-Sleep -Seconds 5

Write-Host "`n========== PRIMERAS LINEAS =========="
Get-Content $stdout -Tail 30 -ErrorAction SilentlyContinue

Write-Host "`n========== GPU =========="
nvidia-smi

Write-Host "`nPara monitorearlo despues:"
Write-Host "Get-Content `"$stdout`" -Wait"

Write-Host "`nPara comprobar si sigue vivo:"
Write-Host "Get-Process -Id $($p.Id) -ErrorAction SilentlyContinue"

Write-Host "`nResumen al terminar:"
Write-Host "Get-Content (Join-Path (Get-Content `"$LogRoot\LATEST.txt`") SUMMARY.json)"
