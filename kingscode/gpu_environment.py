"""Read-only diagnostics and installation planning; no installation or GPU math."""
from __future__ import annotations

from datetime import datetime, timezone
import importlib
import platform
import re
import shutil
import subprocess
import sys


def diagnose(*, torch_module=None, runner=subprocess.run, which=shutil.which) -> dict:
    report = {"timestamp": datetime.now(timezone.utc).isoformat(), "platform": platform.platform(),
              "system": platform.system(), "python": sys.version, "gpus": [], "gpu_validated": False,
              "scope": "Inventory only; no matmul or model loading"}
    if which("nvidia-smi"):
        try:
            result = runner(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.free",
                             "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20, check=False)
            report["nvidia_smi_returncode"] = result.returncode
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    parts = [s.strip() for s in line.split(",")]
                    if len(parts) == 4:
                        report["gpus"].append({"name": parts[0], "driver_version": parts[1],
                                               "memory_total_mib": int(parts[2]), "memory_free_mib": int(parts[3])})
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            report["nvidia_smi_error_type"] = type(exc).__name__
    try:
        torch = torch_module if torch_module is not None else importlib.import_module("torch")
        report["torch"] = {"installed": True, "version": torch.__version__, "built_with_cuda": torch.version.cuda,
                           "cuda_available": bool(torch.cuda.is_available())}
        if report["torch"]["cuda_available"]:
            report["torch"]["bf16_supported"] = bool(torch.cuda.is_bf16_supported())
            report["torch"]["devices"] = [{"index": i, "name": torch.cuda.get_device_properties(i).name,
                                            "total_memory_bytes": torch.cuda.get_device_properties(i).total_memory}
                                           for i in range(torch.cuda.device_count())]
    except ImportError:
        report["torch"] = {"installed": False}
    except Exception as exc:
        report["torch"] = {"error_type": type(exc).__name__}
    return report


def environment_plan(report: dict, *, torch_version: str | None = None, cuda_tag: str | None = None) -> dict:
    if (torch_version is None) != (cuda_tag is None):
        raise ValueError("Supply both torch version and CUDA wheel tag selected from official documentation")
    has_gpu = bool(report.get("gpus") or report.get("torch", {}).get("devices"))
    if torch_version and (not has_gpu or not re.fullmatch(r"\d+\.\d+\.\d+", torch_version) or not re.fullmatch(r"cu\d{3,4}", cuda_tag)):
        raise ValueError("Need an observed GPU and explicit valid PyTorch/CUDA wheel selection")
    python = ".venv/Scripts/python.exe" if "Windows" in report.get("platform", "") else ".venv/bin/python"
    install = ([python, "-m", "pip", "install", f"torch=={torch_version}", "--index-url",
                f"https://download.pytorch.org/whl/{cuda_tag}"] if torch_version else None)
    return {"status": "plan_only" if has_gpu else "awaiting_target_gpu", "gpu_validated": False,
            "observed": report, "selected_wheel": {"torch": torch_version, "cuda_tag": cuda_tag},
            "selection_is_user_supplied_not_automatically_certified": bool(torch_version),
            "install_argv": install,
            "steps": [
                "Inspect GPU, VRAM, driver, OS, Python and installed torch/CUDA in observed.",
                "Select a supported wheel using https://pytorch.org/get-started/locally/ and check driver compatibility at https://docs.nvidia.com/deploy/cuda-compatibility/ . Do not equate local nvcc with the torch wheel runtime.",
                "If the installed stack already works, record its versions; otherwise pass the selected --torch-version and --cuda-tag to --plan, review install_argv and execute it manually.",
                f"{python} -m pip install -r requirements-gpu.txt",
                f"{python} tools/prepare_gpu_environment.py --diagnose --output reports/gpu_diagnostic.json",
                f"{python} tools/prepare_models.py --download-retrieval",
                f"{python} tools/prepare_models.py --download-decoders",
                f"{python} tools/prepare_models.py --verify",
                f"{python} tools/gpu_smoke.py --model qwen3-8b",
                "Only after a passing smoke: follow docs/GPU_DAY_RUNBOOK.md. BF16 fit is unknown until measured; no automatic quantization."],
            "fine_tuning_allowed": False}


def require_cuda(torch):
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA_NOT_AVAILABLE")
    if not torch.cuda.is_bf16_supported():
        raise RuntimeError("BF16_NOT_SUPPORTED")
