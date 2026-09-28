#!/usr/bin/env python3
"""Diagnóstico GPU/CUDA. No instala ni modifica nada.

Además de inventariar la máquina, clasifica si está en el perfil RTX 4090/24 GB
previsto por KingsCode. La recomendación sigue siendo provisional hasta correr
benchmarks reales.
"""
from __future__ import annotations
import json, platform, shutil, subprocess, sys


def run(cmd: list[str]) -> dict:
    try:
        p = subprocess.run(cmd, text=True, capture_output=True, timeout=20, check=False)
        return {"command": cmd, "returncode": p.returncode,
                "stdout": p.stdout.strip(), "stderr": p.stderr.strip()}
    except Exception as exc:
        return {"command": cmd, "error": str(exc)}


def parse_gpu_line(line: str):
    parts = [x.strip() for x in line.split(',')]
    if len(parts) < 4:
        return None
    try:
        return {"name": parts[0], "driver_version": parts[1],
                "memory_total_mib": int(parts[2]), "memory_free_mib": int(parts[3])}
    except Exception:
        return None


def main() -> int:
    report: dict = {
        "python": sys.version,
        "platform": platform.platform(),
        "nvidia_smi_found": bool(shutil.which("nvidia-smi")),
        "nvcc_found": bool(shutil.which("nvcc")),
    }
    gpu_rows=[]
    if report["nvidia_smi_found"]:
        smi = run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.free",
                   "--format=csv,noheader,nounits"])
        report["nvidia_smi"] = smi
        if smi.get("returncode") == 0:
            gpu_rows=[x for line in smi.get("stdout","").splitlines() if (x:=parse_gpu_line(line))]
            report["gpus"] = gpu_rows
    if report["nvcc_found"]:
        report["nvcc"] = run(["nvcc", "--version"])

    try:
        import torch  # type: ignore
        ti = {"version": torch.__version__, "built_with_cuda": torch.version.cuda,
              "cuda_available": bool(torch.cuda.is_available()),
              "device_count": int(torch.cuda.device_count())}
        if torch.cuda.is_available():
            devices=[]
            for i in range(torch.cuda.device_count()):
                prop=torch.cuda.get_device_properties(i)
                devices.append({"index":i,"name":prop.name,
                    "total_memory_gib":round(prop.total_memory/(1024**3),2),
                    "compute_capability":f"{prop.major}.{prop.minor}"})
            ti["devices"]=devices
            try:
                a=torch.randn((2048,2048),device='cuda',dtype=torch.float16)
                b=torch.randn((2048,2048),device='cuda',dtype=torch.float16)
                c=a@b
                torch.cuda.synchronize()
                ti["matmul_smoke_test"]={"ok":True,"shape":list(c.shape)}
            except Exception as exc:
                ti["matmul_smoke_test"]={"ok":False,"error":str(exc)}
        report["torch"]=ti
    except ImportError:
        report["torch"]={"installed":False}
    except Exception as exc:
        report["torch"]={"error":str(exc)}

    profile="unknown"
    if gpu_rows:
        g=gpu_rows[0]
        if "4090" in g["name"] and g["memory_total_mib"] >= 23000:
            profile="rtx4090_24gb"
        elif g["memory_total_mib"] >= 22000:
            profile="gpu_22gb_plus"
        elif g["memory_total_mib"] >= 15000:
            profile="gpu_16gb_class"
        else:
            profile="gpu_under_16gb"
    report["kingscode_profile"]=profile
    report["next_decision"]=(
        "benchmark BF16 first; compare lower-precision only if VRAM/throughput requires it"
        if profile in {"rtx4090_24gb","gpu_22gb_plus"}
        else "use quantized decoder path and keep retrieval models small"
    )
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
